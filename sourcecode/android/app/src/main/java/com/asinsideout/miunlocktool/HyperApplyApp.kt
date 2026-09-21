package com.asinsideout.miunlocktool

import android.app.Application
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import com.asinsideout.miunlocktool.data.PreferencesManager

class HyperApplyApp : Application() {

    override fun onCreate() {
        super.onCreate()
        val prefs = PreferencesManager(this)

        // Apply saved theme mode
        AppCompatDelegate.setDefaultNightMode(prefs.themeMode)

        // Apply saved language (defaults to English "en")
        val appLocale = LocaleListCompat.forLanguageTags(prefs.language)
        AppCompatDelegate.setApplicationLocales(appLocale)
    }
}

