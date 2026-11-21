package com.vocl.app;

import android.content.Context;
import android.content.SharedPreferences;

import androidx.annotation.Nullable;

public final class AuthTokenStore {

    private static final String PREFS_NAME = "vocl_auth_prefs";
    private static final String KEY_JWT = "jwt_access_token";

    private AuthTokenStore() {}

    public static void save(Context context, String token) {
        SharedPreferences prefs = context.getApplicationContext()
                .getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        prefs.edit().putString(KEY_JWT, token).apply();
    }

    @Nullable
    public static String get(Context context) {
        SharedPreferences prefs = context.getApplicationContext()
                .getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        String token = prefs.getString(KEY_JWT, null);
        return (token != null && !token.isEmpty()) ? token : null;
    }

    public static void clear(Context context) {
        SharedPreferences prefs = context.getApplicationContext()
                .getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
        prefs.edit().remove(KEY_JWT).apply();
    }
}
