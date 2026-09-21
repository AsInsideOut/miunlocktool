package com.asinsideout.miunlocktool.data

import android.content.Context
import android.content.SharedPreferences
import androidx.appcompat.app.AppCompatDelegate

class PreferencesManager(context: Context) {

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    companion object {
        private const val PREFS_NAME = "hyperapply_preferences"
        private const val KEY_TOKEN = "key_token"
        private const val KEY_THEME = "key_theme"
        private const val KEY_LANG = "key_lang"
        private const val KEY_NTP_SERVER = "key_ntp_server"
        private const val KEY_BURST_COUNT = "key_burst_count"
        private const val KEY_BURST_INTERVAL = "key_burst_interval"
        private const val KEY_MODE = "key_execution_mode"

        const val THEME_LIGHT = AppCompatDelegate.MODE_NIGHT_NO
        const val THEME_DARK = AppCompatDelegate.MODE_NIGHT_YES
        const val THEME_SYSTEM = AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM

        const val LANG_SYSTEM = "system"
        const val LANG_EN = "en"
        const val LANG_RU = "ru"

        const val DEFAULT_NTP = "time.google.com"
        const val DEFAULT_BURST_COUNT = 20
        const val DEFAULT_BURST_INTERVAL_MS = 100L
    }

    var token: String
        get() = prefs.getString(KEY_TOKEN, "") ?: ""
        set(value) = prefs.edit().putString(KEY_TOKEN, value.trim()).apply()

    var themeMode: Int
        get() = prefs.getInt(KEY_THEME, THEME_SYSTEM)
        set(value) = prefs.edit().putInt(KEY_THEME, value).apply()

    var language: String
        get() = prefs.getString(KEY_LANG, LANG_EN) ?: LANG_EN
        set(value) = prefs.edit().putString(KEY_LANG, value).apply()

    var ntpServer: String
        get() = prefs.getString(KEY_NTP_SERVER, DEFAULT_NTP) ?: DEFAULT_NTP
        set(value) = prefs.edit().putString(KEY_NTP_SERVER, value).apply()

    var burstCount: Int
        get() = prefs.getInt(KEY_BURST_COUNT, DEFAULT_BURST_COUNT)
        set(value) = prefs.edit().putInt(KEY_BURST_COUNT, value).apply()

    var burstIntervalMs: Long
        get() = prefs.getLong(KEY_BURST_INTERVAL, DEFAULT_BURST_INTERVAL_MS)
        set(value) = prefs.edit().putLong(KEY_BURST_INTERVAL, value).apply()

    var executionMode: Int
        get() = prefs.getInt(KEY_MODE, ExecutionMode.AUTO.id)
        set(value) = prefs.edit().putInt(KEY_MODE, value).apply()
}

