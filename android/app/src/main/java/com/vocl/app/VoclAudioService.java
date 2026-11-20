package com.vocl.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.os.PowerManager;
import android.util.Log;

import androidx.annotation.Nullable;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import okhttp3.WebSocket;
import okhttp3.WebSocketListener;
import okio.ByteString;

public class VoclAudioService extends Service {

    private static final String TAG = "VoclAudioService";
    public static final String EXTRA_PROBLEM_ID = "problem_id";
    public static final String ACTION_STOP_SESSION = "com.vocl.app.STOP_SESSION";

    public static final String BROADCAST_STATE   = "com.vocl.app.STATE_CHANGE";
    public static final String BROADCAST_AUTOPSY = "com.vocl.app.SESSION_COMPLETE";
    public static final String EXTRA_STATUS  = "status";
    public static final String EXTRA_AUTOPSY = "autopsy";

    private static final String CHANNEL_ID = "vocl_live_session";

    // Shared snapshot so MainActivity can re-sync UI after screen unlock
    private static volatile boolean sessionActive;
    private static volatile String currentStatus;
    private static volatile String lastAutopsyJson;

    private PowerManager.WakeLock wakeLock;
    private AudioStreamEngine audioEngine;
    private OkHttpClient httpClient;
    private WebSocket webSocket;
    private Thread captureThread;
    private ExecutorService shutdownExecutor;
    private volatile boolean isRunning;
    private final AtomicBoolean isEnding = new AtomicBoolean(false);
    private final AtomicBoolean isCleanedUp = new AtomicBoolean(false);

    private CountDownLatch autopsyLatch;

    public static boolean isSessionActive() {
        return sessionActive;
    }

    @Nullable
    public static String getCurrentStatus() {
        return currentStatus;
    }

    @Nullable
    public static String getLastAutopsyJson() {
        return lastAutopsyJson;
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
        httpClient = new OkHttpClient.Builder()
                .readTimeout(0, TimeUnit.MILLISECONDS)
                .build();
        audioEngine = new AudioStreamEngine();
        shutdownExecutor = Executors.newSingleThreadExecutor();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) return START_NOT_STICKY;

        if (ACTION_STOP_SESSION.equals(intent.getAction())) {
            endSessionAsync();
            return START_NOT_STICKY;
        }

        String problemId = intent.getStringExtra(EXTRA_PROBLEM_ID);
        if (problemId == null || problemId.isEmpty()) {
            stopSelf();
            return START_NOT_STICKY;
        }

        Notification notification = buildNotification();
        startForeground(1, notification);

        acquireWakeLock();
        startAudioSession(problemId);

        return START_NOT_STICKY;
    }

    private void startAudioSession(String problemId) {
        // Tear down any lingering socket or audio capture before starting fresh
        isRunning = false;
        if (webSocket != null) {
            try { webSocket.cancel(); } catch (Exception ignored) {}
            webSocket = null;
        }
        if (captureThread != null) {
            captureThread.interrupt();
            captureThread = null;
        }

        isEnding.set(false);
        isCleanedUp.set(false);
        isRunning = true;
        sessionActive = true;
        currentStatus = "connecting";
        lastAutopsyJson = null;
        autopsyLatch = new CountDownLatch(1);

        audioEngine.initCapture();
        audioEngine.initPlayback();
        audioEngine.startPlayback();

        String wsUrl = BackendConfig.BASE_WS_URL + "/ws/interview/" + problemId;
        Request request = new Request.Builder().url(wsUrl).build();

        webSocket = httpClient.newWebSocket(request, new WebSocketListener() {
            @Override
            public void onOpen(WebSocket ws, Response response) {
                Log.i(TAG, "WebSocket connected");
                audioEngine.startCapture();
                startCaptureLoop(ws);
                broadcastState("listening");
            }

            @Override
            public void onMessage(WebSocket ws, String text) {
                handleTextMessage(text);
            }

            @Override
            public void onMessage(WebSocket ws, ByteString bytes) {
                audioEngine.writePlaybackData(bytes.toByteArray());
            }

            @Override
            public void onFailure(WebSocket ws, Throwable t, @Nullable Response response) {
                Log.e(TAG, "WebSocket failure", t);
                if (autopsyLatch != null) autopsyLatch.countDown();
                broadcastState("error");
                cleanupSession();
            }

            @Override
            public void onClosed(WebSocket ws, int code, String reason) {
                Log.i(TAG, "WebSocket closed: " + reason);
                if (autopsyLatch != null) autopsyLatch.countDown();
                cleanupSession();
            }
        });
    }

    private void startCaptureLoop(WebSocket ws) {
        captureThread = new Thread(() -> {
            while (isRunning && !Thread.currentThread().isInterrupted()) {
                byte[] chunk = audioEngine.readCaptureChunk();
                if (chunk != null && isRunning) {
                    ws.send(ByteString.of(chunk));
                } else if (isRunning) {
                    try {
                        Thread.sleep(20); // Prevent busy-wait if AudioRecord is unavailable
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
        }, "vocl-capture");
        captureThread.start();
    }

    private void handleTextMessage(String text) {
        try {
            JSONObject msg = new JSONObject(text);
            String type = msg.optString("type", "");

            switch (type) {
                case "clear_audio_buffer":
                    audioEngine.flushPlayback();
                    break;
                case "state":
                    broadcastState(msg.optString("status", "listening"));
                    break;
                case "autopsy":
                    broadcastAutopsy(text);
                    if (autopsyLatch != null) autopsyLatch.countDown();
                    break;
                case "error":
                    broadcastState("error");
                    if (autopsyLatch != null) autopsyLatch.countDown();
                    break;
                default:
                    Log.d(TAG, "Ignoring frame type: " + type);
            }
        } catch (JSONException e) {
            Log.w(TAG, "Malformed server message", e);
        }
    }

    private void endSessionAsync() {
        if (!isEnding.compareAndSet(false, true)) return;
        isRunning = false;
        if (captureThread != null) {
            captureThread.interrupt();
        }

        // Run autopsy wait off main thread so UI never freezes
        if (shutdownExecutor == null || shutdownExecutor.isShutdown()) {
            cleanupSession();
            return;
        }
        shutdownExecutor.execute(() -> {
            WebSocket activeSocket = webSocket;
            if (activeSocket != null) {
                try {
                    activeSocket.send("{\"type\":\"end_session\"}");
                } catch (Exception e) {
                    Log.w(TAG, "Failed to send end_session", e);
                }

                CountDownLatch latch = autopsyLatch;
                if (latch != null) {
                    try {
                        latch.await(5, TimeUnit.SECONDS);
                    } catch (InterruptedException ignored) {
                        Thread.currentThread().interrupt();
                    }
                }

                try {
                    activeSocket.close(1000, "session ended");
                } catch (Exception ignored) {}
            }
            cleanupSession();
        });
    }

    private void cleanupSession() {
        if (!isCleanedUp.compareAndSet(false, true)) return;
        isRunning = false;
        sessionActive = false;
        if (captureThread != null) {
            captureThread.interrupt();
            captureThread = null;
        }
        audioEngine.release();
        releaseWakeLock();
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
    }

    private void broadcastState(String status) {
        currentStatus = status;
        Intent intent = new Intent(BROADCAST_STATE);
        intent.setPackage(getPackageName());
        intent.putExtra(EXTRA_STATUS, status);
        sendBroadcast(intent);
    }

    private void broadcastAutopsy(String json) {
        lastAutopsyJson = json;
        sessionActive = false;
        Intent intent = new Intent(BROADCAST_AUTOPSY);
        intent.setPackage(getPackageName());
        intent.putExtra(EXTRA_AUTOPSY, json);
        sendBroadcast(intent);
    }

    private void acquireWakeLock() {
        releaseWakeLock();
        PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
        wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "vocl:live_session");
        wakeLock.acquire(15 * 60 * 1000L); // 15 min safety cap
    }

    private void releaseWakeLock() {
        if (wakeLock != null && wakeLock.isHeld()) {
            wakeLock.release();
            wakeLock = null;
        }
    }

    private void createNotificationChannel() {
        NotificationChannel channel = new NotificationChannel(
                CHANNEL_ID, "Live Interview", NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("Active audio interview session");
        getSystemService(NotificationManager.class).createNotificationChannel(channel);
    }

    private Notification buildNotification() {
        return new Notification.Builder(this, CHANNEL_ID)
                .setContentTitle("Vocl")
                .setContentText("Live Interview Active")
                .setSmallIcon(android.R.drawable.ic_btn_speak_now)
                .setOngoing(true)
                .build();
    }

    @Override
    public void onDestroy() {
        isRunning = false;
        sessionActive = false;
        if (webSocket != null) {
            webSocket.close(1000, "service destroyed");
        }
        audioEngine.release();
        releaseWakeLock();
        if (shutdownExecutor != null) {
            shutdownExecutor.shutdownNow();
        }
        super.onDestroy();
    }
}
