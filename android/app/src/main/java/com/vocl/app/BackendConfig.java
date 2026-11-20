package com.vocl.app;

public final class BackendConfig {

    // Populated per Gradle flavor (prod -> https/wss vocl.onrender.com, local -> http/ws 127.0.0.1:8080)
    public static final String BASE_HTTP_URL =
            (BuildConfig.USE_TLS ? "https://" : "http://") + BuildConfig.BACKEND_HOST;
    public static final String BASE_WS_URL =
            (BuildConfig.USE_TLS ? "wss://" : "ws://") + BuildConfig.BACKEND_HOST;

    private BackendConfig() {}
}
