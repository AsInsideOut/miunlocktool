package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class BaseInfo(
    val type: Int = 1, // 1 for Template 1, 2 for Template 2
    val title: String, // Main Title 1
    val subTitle: String? = null, // Main Title 2
    val extraTitle: String? = null, // Supplement Text
    val specialTitle: String? = null, // Special Label
    val content: String, // Sub Text 1 (Description)
    val subContent: String? = null, // Sub Text 2
    @SerialName("picFunction")
    val picFunction: String? = null, // Function Icon Key

    // Config
    val showDivider: Boolean? = null,
    val showContentDivider: Boolean? = null,

    // Colors
    val colorTitle: String? = null,
    val colorTitleDark: String? = null,
    val colorSubTitle: String? = null,
    val colorSubTitleDark: String? = null,
    val colorExtraTitle: String? = null,
    val colorExtraTitleDark: String? = null,
    val colorSpecialTitle: String? = null,
    val colorSpecialTitleDark: String? = null,
    val colorSpecialBg: String? = null,
    val colorContent: String? = null,
    val colorContentDark: String? = null,
    val colorSubContent: String? = null,
    val colorSubContentDark: String? = null,

    val actions: List<HyperActionRef>? = null
)