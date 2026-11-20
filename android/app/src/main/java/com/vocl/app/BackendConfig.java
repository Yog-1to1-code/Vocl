package com.vocl.app;

public final class BackendConfig {

    // Toggle USE_TLS to true and update HOST for Cloud Run production
    private static final boolean USE_TLS = false;
    private static final String HOST = "10.0.2.2:8080";

    public static final String BASE_HTTP_URL = (USE_TLS ? "https://" : "http://") + HOST;
    public static final String BASE_WS_URL  = (USE_TLS ? "wss://" : "ws://")   + HOST;

    private BackendConfig() {}
}
