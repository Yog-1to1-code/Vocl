package com.vocl.app;

import android.Manifest;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.webkit.JavascriptInterface;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import android.util.Base64;
import android.util.Log;

import org.json.JSONObject;

import java.util.concurrent.TimeUnit;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "MainActivity";
    private static final int PERMISSION_REQUEST_CODE = 100;
    private WebView webView;
    private String deliveredAutopsyJson;
    private final OkHttpClient apiClient = new OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build();

    private final BroadcastReceiver stateReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String status = intent.getStringExtra(VoclAudioService.EXTRA_STATUS);
            if (status != null) {
                pushStateToWebView(status);
            }
        }
    };

    private final BroadcastReceiver autopsyReceiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            String json = intent.getStringExtra(VoclAudioService.EXTRA_AUTOPSY);
            if (json != null) {
                deliveredAutopsyJson = json;
                pushAutopsyToWebView(json);
            }
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        webView = new WebView(this);
        setContentView(webView);

        configureWebView();
        requestPermissions();

        String startPage = AuthTokenStore.get(this) != null
                ? "file:///android_asset/drills.html"
                : "file:///android_asset/login.html";
        webView.loadUrl(startPage);
    }

    private void configureWebView() {
        webView.setBackgroundColor(0xFF000000);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setAllowFileAccess(true);
        // Allow file:///android_asset/ screens to fetch() our HTTPS backend on all OEM WebViews
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);

        webView.addJavascriptInterface(new VoclBridge(), "VoclNative");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {
                if (url.startsWith("file:///android_asset/")) {
                    view.loadUrl(url);
                    return true;
                }
                return false;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                syncServiceStateToWebView();
            }
        });
    }

    private void requestPermissions() {
        String[] permissions;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions = new String[]{
                    Manifest.permission.RECORD_AUDIO,
                    Manifest.permission.POST_NOTIFICATIONS
            };
        } else {
            permissions = new String[]{Manifest.permission.RECORD_AUDIO};
        }

        boolean allGranted = true;
        for (String perm : permissions) {
            if (ContextCompat.checkSelfPermission(this, perm) != PackageManager.PERMISSION_GRANTED) {
                allGranted = false;
                break;
            }
        }

        if (!allGranted) {
            ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQUEST_CODE);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CODE) {
            for (int result : grantResults) {
                if (result != PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "Microphone permission is required for interviews",
                            Toast.LENGTH_LONG).show();
                    break;
                }
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        IntentFilter stateFilter = new IntentFilter(VoclAudioService.BROADCAST_STATE);
        IntentFilter autopsyFilter = new IntentFilter(VoclAudioService.BROADCAST_AUTOPSY);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(stateReceiver, stateFilter, Context.RECEIVER_NOT_EXPORTED);
            registerReceiver(autopsyReceiver, autopsyFilter, Context.RECEIVER_NOT_EXPORTED);
        } else {
            registerReceiver(stateReceiver, stateFilter);
            registerReceiver(autopsyReceiver, autopsyFilter);
        }
        syncServiceStateToWebView();
    }

    @Override
    protected void onPause() {
        super.onPause();
        unregisterReceiver(stateReceiver);
        unregisterReceiver(autopsyReceiver);
    }

    private void syncServiceStateToWebView() {
        if (VoclAudioService.isSessionActive()) {
            String status = VoclAudioService.getCurrentStatus();
            if (status != null) {
                pushStateToWebView(status);
            }
        }
        String latestAutopsy = VoclAudioService.getLastAutopsyJson();
        if (latestAutopsy != null && !latestAutopsy.equals(deliveredAutopsyJson)) {
            deliveredAutopsyJson = latestAutopsy;
            pushAutopsyToWebView(latestAutopsy);
        }
    }

    private void pushStateToWebView(String status) {
        String quotedStatus = JSONObject.quote(status);
        runOnUiThread(() -> webView.evaluateJavascript(
                "window.onVoclStateChange && window.onVoclStateChange(" + quotedStatus + ")", null));
    }

    private void pushAutopsyToWebView(String json) {
        // JSONObject.quote safely escapes quotes, backslashes, CR/LF, and control chars
        String quotedJson = JSONObject.quote(json);
        runOnUiThread(() -> webView.evaluateJavascript(
                "window.onVoclSessionComplete && window.onVoclSessionComplete(JSON.parse(" + quotedJson + "))", null));
    }

    @Override
    public void onBackPressed() {
        String currentUrl = webView.getUrl();
        if (currentUrl != null && currentUrl.contains("live.html") && VoclAudioService.isSessionActive()) {
            webView.evaluateJavascript("window.endInterview && window.endInterview()", null);
            return;
        }
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    // Exposed to JavaScript as window.VoclNative
    public class VoclBridge {

        @JavascriptInterface
        public void startSession(String problemId) {
            if (ContextCompat.checkSelfPermission(MainActivity.this,
                    Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                runOnUiThread(() -> Toast.makeText(MainActivity.this,
                        "Microphone permission required", Toast.LENGTH_SHORT).show());
                return;
            }

            deliveredAutopsyJson = null;
            Intent intent = new Intent(MainActivity.this, VoclAudioService.class);
            intent.putExtra(VoclAudioService.EXTRA_PROBLEM_ID, problemId);
            ContextCompat.startForegroundService(MainActivity.this, intent);
        }

        @JavascriptInterface
        public void stopSession() {
            Intent intent = new Intent(MainActivity.this, VoclAudioService.class);
            intent.setAction(VoclAudioService.ACTION_STOP_SESSION);
            startService(intent);
        }

        @JavascriptInterface
        public String getBackendBaseUrl() {
            return BackendConfig.BASE_HTTP_URL;
        }

        @JavascriptInterface
        public String getBackendUrl() {
            return BackendConfig.BASE_HTTP_URL;
        }

        @JavascriptInterface
        public void setMuted(boolean muted) {
            VoclAudioService.setMicMuted(muted);
        }

        @JavascriptInterface
        public void saveAuthToken(String token) {
            AuthTokenStore.save(MainActivity.this, token);
        }

        @JavascriptInterface
        public String getAuthToken() {
            String token = AuthTokenStore.get(MainActivity.this);
            return token != null ? token : "";
        }

        @JavascriptInterface
        public void clearAuthToken() {
            AuthTokenStore.clear(MainActivity.this);
        }

        @JavascriptInterface
        public boolean isLocalFlavor() {
            return "local".equals(BuildConfig.FLAVOR);
        }

        // Native OkHttp proxy bypasses WebView file:// CORS/origin quirks and attaches JWT
        @JavascriptInterface
        public String apiRequest(String method, String path) {
            return apiRequestWithBody(method, path, null);
        }

        @JavascriptInterface
        public String apiRequestWithBody(String method, String path, String jsonBody) {
            String url = BackendConfig.BASE_HTTP_URL + path;
            Request.Builder builder = new Request.Builder().url(url);
            String token = AuthTokenStore.get(MainActivity.this);
            if (token != null) {
                builder.header("Authorization", "Bearer " + token);
            }
            if ("DELETE".equalsIgnoreCase(method)) {
                builder.delete();
            } else if ("POST".equalsIgnoreCase(method)) {
                RequestBody body = RequestBody.create(
                        jsonBody != null ? jsonBody : "{}",
                        MediaType.parse("application/json; charset=utf-8"));
                builder.post(body);
            } else {
                builder.get();
            }
            try (Response resp = apiClient.newCall(builder.build()).execute()) {
                if (resp.isSuccessful() && resp.body() != null) {
                    return resp.body().string();
                }
                Log.w(TAG, "apiRequest " + method + " " + url + " -> HTTP " + resp.code());
            } catch (Exception e) {
                Log.e(TAG, "apiRequest " + method + " " + url + " failed: " + e.getMessage(), e);
            }
            return null;
        }

        // Fetch authenticated session audio bytes as a base64 data URI for WebView <audio> playback
        @JavascriptInterface
        public String fetchAudioBase64(String path) {
            String url = BackendConfig.BASE_HTTP_URL + path;
            Request.Builder builder = new Request.Builder().url(url).get();
            String token = AuthTokenStore.get(MainActivity.this);
            if (token != null) {
                builder.header("Authorization", "Bearer " + token);
            }
            try (Response resp = apiClient.newCall(builder.build()).execute()) {
                if (resp.isSuccessful() && resp.body() != null) {
                    byte[] raw = resp.body().bytes();
                    String contentType = resp.header("Content-Type", "audio/ogg");
                    int semi = contentType.indexOf(';');
                    if (semi > 0) contentType = contentType.substring(0, semi).trim();
                    return "data:" + contentType + ";base64," + Base64.encodeToString(raw, Base64.NO_WRAP);
                }
                Log.w(TAG, "fetchAudioBase64 " + url + " -> HTTP " + resp.code());
            } catch (Exception e) {
                Log.e(TAG, "fetchAudioBase64 " + url + " failed: " + e.getMessage(), e);
            }
            return null;
        }

        // Native OkHttp proxy for Supabase Auth REST calls (bypasses WebView file:// CORS)
        @JavascriptInterface
        public String supabaseAuthPost(String fullUrl, String apiKey, String jsonBody) {
            RequestBody body = RequestBody.create(
                    jsonBody != null ? jsonBody : "{}",
                    MediaType.parse("application/json; charset=utf-8"));
            Request req = new Request.Builder()
                    .url(fullUrl)
                    .header("apikey", apiKey != null ? apiKey : "")
                    .header("Content-Type", "application/json")
                    .post(body)
                    .build();
            try (Response resp = apiClient.newCall(req).execute()) {
                String respBody = resp.body() != null ? resp.body().string() : "{}";
                JSONObject wrapped = new JSONObject();
                wrapped.put("ok", resp.isSuccessful());
                wrapped.put("status", resp.code());
                wrapped.put("body", respBody);
                return wrapped.toString();
            } catch (Exception e) {
                Log.e(TAG, "supabaseAuthPost failed: " + e.getMessage(), e);
                return null;
            }
        }
    }
}
