package com.vocl.app;

public final class BackendConfig {

    // Emulator loopback — swap to Cloud Run wss:// for production
    private static final String HOST = "10.0.2.2:8080";

    public static final String BASE_HTTP_URL = "http://" + HOST;
    public static final String BASE_WS_URL  = "ws://"   + HOST;

    private BackendConfig() {}
}
