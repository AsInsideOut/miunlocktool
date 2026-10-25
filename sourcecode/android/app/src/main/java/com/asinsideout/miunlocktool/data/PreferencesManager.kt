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
        const val LANG_UK = "uk"
        const val LANG_ES = "es"
        const val LANG_PT = "pt"
        const val LANG_ID = "id"
        const val LANG_ZH = "zh"

        private const val KEY_ACCENT_COLOR = "key_accent_color"
        private const val KEY_ACCENT_COLOR_HEX = "key_accent_color_hex"

        const val DEFAULT_ACCENT_HEX = "#6750A4"
        val DEFAULT_ACCENT_COLOR = android.graphics.Color.parseColor(DEFAULT_ACCENT_HEX)

        const val DEFAULT_NTP = "time.google.com"
        const val DEFAULT_BURST_COUNT = 20
        const val DEFAULT_BURST_INTERVAL_MS = 100L

        private const val KEY_TIMING_PROFILE = "key_timing_profile"
        private const val KEY_CUSTOM_TIMINGS = "key_custom_timings"

        const val PROFILE_EUROPE = "europe"
        const val PROFILE_ASIA = "asia"
        const val PROFILE_USA_AFRICA = "usa_africa"
        const val PROFILE_CUSTOM = "custom"

        val EUROPE_TIMINGS = listOf(58.700, 58.800, 59.100, 59.300, 59.500, 59.800)
        val ASIA_TIMINGS = listOf(58.800, 59.100, 59.300, 59.500, 59.700)
        val USA_AFRICA_TIMINGS = listOf(58.500, 58.800, 59.100, 59.300, 59.500, 59.700)

        fun parseTimings(input: String): List<Double> {
            val list = mutableListOf<Double>()
            val parts = input.split(',', ';', ' ', '\n', '\t')
            for (p in parts) {
                val clean = p.trim().replace(':', '.')
                val num = clean.toDoubleOrNull()
                if (num != null && num in 0.0..60.0) {
                    list.add(Math.round(num * 1000.0) / 1000.0)
                }
            }
            return if (list.isNotEmpty()) list.sorted() else EUROPE_TIMINGS
        }
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

    var accentColorHex: String
        get() = prefs.getString(KEY_ACCENT_COLOR_HEX, DEFAULT_ACCENT_HEX) ?: DEFAULT_ACCENT_HEX
        set(value) = prefs.edit().putString(KEY_ACCENT_COLOR_HEX, value).apply()

    var accentColor: Int
        get() = prefs.getInt(KEY_ACCENT_COLOR, DEFAULT_ACCENT_COLOR)
        set(value) = prefs.edit().putInt(KEY_ACCENT_COLOR, value).apply()


    var timingProfile: String
        get() = prefs.getString(KEY_TIMING_PROFILE, PROFILE_EUROPE) ?: PROFILE_EUROPE
        set(value) = prefs.edit().putString(KEY_TIMING_PROFILE, value).apply()

    var customTimings: String
        get() = prefs.getString(KEY_CUSTOM_TIMINGS, "58.700, 58.800, 59.100, 59.300, 59.500, 59.800") ?: "58.700, 58.800, 59.100, 59.300, 59.500, 59.800"
        set(value) = prefs.edit().putString(KEY_CUSTOM_TIMINGS, value).apply()

    fun getActiveTimings(): List<Double> {
        return when (timingProfile) {
            PROFILE_ASIA -> ASIA_TIMINGS
            PROFILE_USA_AFRICA -> USA_AFRICA_TIMINGS
            PROFILE_CUSTOM -> parseTimings(customTimings)
            else -> EUROPE_TIMINGS
        }
    }
}

