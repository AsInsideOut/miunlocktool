package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class HighlightInfoV3(
    val primaryText: String, // High light text (e.g. Price)
    val secondaryText: String? = null, // Supplement text
    val highLightText: String? = null, // Text Label
    val showSecondaryLine: Boolean? = null, // Strikethrough on secondary text?

    // Action (Round button)
    val actionInfo: HyperActionRef? = null,

    // Colors
    val primaryColor: String? = null,
    val primaryColorDark: String? = null,
    val secondaryColor: String? = null,
    val secondaryColorDark: String? = null,
    val highLightTextColor: String? = null,
    val highLightTextColorDark: String? = null,
    val highLightBgColor: String? = null,
    val highLightBgColorDark: String? = null
)