package com.asinsideout.miunlocktool

import android.app.Application
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import com.asinsideout.miunlocktool.data.PreferencesManager

class HyperApplyApp : Application() {

    override fun onCreate() {
        super.onCreate()
        val prefs = PreferencesManager(this)

        // Initialize TranslationManager with saved language
        com.asinsideout.miunlocktool.data.TranslationManager.init(this, prefs.language)

        // Apply saved theme mode
        AppCompatDelegate.setDefaultNightMode(prefs.themeMode)

        // Apply saved language (defaults to English "en")
        val appLocale = LocaleListCompat.forLanguageTags(prefs.language)
        AppCompatDelegate.setApplicationLocales(appLocale)
    }
}

