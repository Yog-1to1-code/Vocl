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
import java.util.concurrent.TimeUnit;

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

    private PowerManager.WakeLock wakeLock;
    private AudioStreamEngine audioEngine;
    private OkHttpClient httpClient;
    private WebSocket webSocket;
    private Thread captureThread;
    private volatile boolean isRunning;

    private CountDownLatch autopsyLatch;
    private String autopsyJson;

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
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent == null) return START_NOT_STICKY;

        if (ACTION_STOP_SESSION.equals(intent.getAction())) {
            endSession();
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
        isRunning = true;
        autopsyLatch = new CountDownLatch(1);
        autopsyJson = null;

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
                cleanupSession();
            }

            @Override
            public void onClosed(WebSocket ws, int code, String reason) {
                Log.i(TAG, "WebSocket closed: " + reason);
                cleanupSession();
            }
        });
    }

    private void startCaptureLoop(WebSocket ws) {
        captureThread = new Thread(() -> {
            while (isRunning) {
                byte[] chunk = audioEngine.readCaptureChunk();
                if (chunk != null && isRunning) {
                    ws.send(ByteString.of(chunk));
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
                    autopsyJson = text;
                    broadcastAutopsy(text);
                    if (autopsyLatch != null) autopsyLatch.countDown();
                    break;
                default:
                    Log.d(TAG, "Unknown message type: " + type);
            }
        } catch (JSONException e) {
            Log.w(TAG, "Malformed server message", e);
        }
    }

    private void endSession() {
        if (!isRunning) return;
        isRunning = false;

        if (webSocket != null) {
            try {
                webSocket.send("{\"type\":\"end_session\"}");
            } catch (Exception e) {
                Log.w(TAG, "Failed to send end_session", e);
            }

            // Wait up to 5s for autopsy response
            if (autopsyLatch != null) {
                try {
                    autopsyLatch.await(5, TimeUnit.SECONDS);
                } catch (InterruptedException ignored) {}
            }

            webSocket.close(1000, "session ended");
        }

        cleanupSession();
    }

    private void cleanupSession() {
        isRunning = false;
        audioEngine.release();
        releaseWakeLock();
        stopForeground(STOP_FOREGROUND_REMOVE);
        stopSelf();
    }

    private void broadcastState(String status) {
        Intent intent = new Intent(BROADCAST_STATE);
        intent.setPackage(getPackageName());
        intent.putExtra(EXTRA_STATUS, status);
        sendBroadcast(intent);
    }

    private void broadcastAutopsy(String json) {
        Intent intent = new Intent(BROADCAST_AUTOPSY);
        intent.setPackage(getPackageName());
        intent.putExtra(EXTRA_AUTOPSY, json);
        sendBroadcast(intent);
    }

    private void acquireWakeLock() {
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
        endSession();
        super.onDestroy();
    }
}
