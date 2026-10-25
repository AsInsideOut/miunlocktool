package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

/**
 * Model for the "textButton" component (Component 18/Custom Specification).
 * Matches the structure: [{"actionTitle":..., "actionBgColor":...}]
 */
@Serializable
data class TextButtonInfo(
    val type: Int = 0, // Usually 0 for standard text buttons
    val actionTitle: String,
    val actionIcon: String? = null, // Key for the icon (e.g. "miui.focus.pic_...")
    val actionIconDark: String? = null,

    // Colors
    val actionBgColor: String? = null,
    val actionBgColorDark: String? = null,
    val actionTitleColor: String? = null,
    val actionTitleColorDark: String? = null,

    // Intent Config
    val actionIntentType: Int = 0,
    val actionIntent: String? = null
)