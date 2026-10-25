package com.asinsideout.miunlocktool.data

import android.content.res.ColorStateList
import android.graphics.Color
import androidx.core.graphics.ColorUtils
import com.google.android.material.bottomnavigation.BottomNavigationView

data class ColorPreset(
    val nameResId: Int,
    val hex: String,
    val color: Int
)

object ThemeColorManager {

    val PRESETS = listOf(
        ColorPreset(com.asinsideout.miunlocktool.R.string.settings_color_purple, "#6750A4", Color.parseColor("#6750A4")),
        ColorPreset(com.asinsideout.miunlocktool.R.string.settings_color_blue, "#007AFF", Color.parseColor("#007AFF")),
        ColorPreset(com.asinsideout.miunlocktool.R.string.settings_color_orange, "#FF6900", Color.parseColor("#FF6900")),
        ColorPreset(com.asinsideout.miunlocktool.R.string.settings_color_green, "#2E7D32", Color.parseColor("#2E7D32")),
        ColorPreset(com.asinsideout.miunlocktool.R.string.settings_color_red, "#D32F2F", Color.parseColor("#D32F2F")),
        ColorPreset(com.asinsideout.miunlocktool.R.string.settings_color_cyan, "#00BCD4", Color.parseColor("#00BCD4"))
    )

    fun parseColorHex(input: String?): Int? {
        if (input.isNullOrBlank()) return null
        val clean = input.trim().removePrefix("#")

        return try {
            when (clean.length) {
                3 -> {
                    // Shorthand #RGB -> #RRGGBB (e.g. 09F -> 0099FF)
                    val r = clean[0]
                    val g = clean[1]
                    val b = clean[2]
                    Color.parseColor("#FF$r$r$g$g$b$b")
                }
                6 -> {
                    Color.parseColor("#FF$clean")
                }
                8 -> {
                    Color.parseColor("#$clean")
                }
                else -> null
            }
        } catch (e: Exception) {
            null
        }
    }

    fun adjustAlpha(color: Int, factor: Float): Int {
        val alpha = (Color.alpha(color) * factor).coerceIn(0f, 255f).toInt()
        val red = Color.red(color)
        val green = Color.green(color)
        val blue = Color.blue(color)
        return Color.argb(alpha, red, green, blue)
    }

    fun getContrastOnColor(color: Int): Int {
        val luminance = ColorUtils.calculateLuminance(color)
        return if (luminance > 0.45) Color.parseColor("#1C1B1F") else Color.WHITE
    }

    fun createNavColorStateList(accentColor: Int, isDark: Boolean): ColorStateList {
        val unselectedColor = if (isDark) {
            Color.parseColor("#8CE6E1E5")
        } else {
            Color.parseColor("#8C49454F")
        }

        return ColorStateList(
            arrayOf(
                intArrayOf(android.R.attr.state_checked),
                intArrayOf()
            ),
            intArrayOf(
                accentColor,
                unselectedColor
            )
        )
    }

    fun applyToBottomNav(
        navView: BottomNavigationView,
        accentColor: Int,
        isDark: Boolean,
        density: Float
    ) {
        val colorStateList = createNavColorStateList(accentColor, isDark)
        navView.itemIconTintList = colorStateList
        navView.itemTextColor = colorStateList

        val defaultColor = if (isDark) Color.parseColor("#28282D") else Color.parseColor("#FFFFFF")
        val pb = navView.paddingBottom
        navView.setBackgroundColor(defaultColor)
        navView.setPadding(0, 0, 0, pb)
        navView.clipToOutline = false
        navView.elevation = 4f * density

        navView.isItemActiveIndicatorEnabled = true
        navView.itemActiveIndicatorColor = ColorStateList.valueOf(adjustAlpha(accentColor, 0.22f))
    }

    fun createRadioColorStateList(accentColor: Int, isDark: Boolean): ColorStateList {
        val unselected = if (isDark) Color.parseColor("#8CE6E1E5") else Color.parseColor("#8C49454F")
        return ColorStateList(
            arrayOf(
                intArrayOf(android.R.attr.state_checked),
                intArrayOf(-android.R.attr.state_checked)
            ),
            intArrayOf(
                accentColor,
                unselected
            )
        )
    }

    fun applyPrimaryButtonStyle(button: com.google.android.material.button.MaterialButton, accentColor: Int) {
        button.backgroundTintList = ColorStateList.valueOf(accentColor)
        val contrast = getContrastOnColor(accentColor)
        button.setTextColor(contrast)
        button.iconTint = ColorStateList.valueOf(contrast)
    }

    fun applyTonalButtonStyle(button: com.google.android.material.button.MaterialButton, accentColor: Int) {
        button.backgroundTintList = ColorStateList.valueOf(adjustAlpha(accentColor, 0.22f))
        button.setTextColor(accentColor)
        button.iconTint = ColorStateList.valueOf(accentColor)
    }

    fun applyOutlinedButtonStyle(button: com.google.android.material.button.MaterialButton, accentColor: Int) {
        button.strokeColor = ColorStateList.valueOf(adjustAlpha(accentColor, 0.60f))
        button.setTextColor(accentColor)
        button.iconTint = ColorStateList.valueOf(accentColor)
    }
}
