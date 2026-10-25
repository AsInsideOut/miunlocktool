package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class CoverInfo(
    val picCover: String, // Cover Image Key
    val title: String,
    val content: String? = null,
    val subContent: String? = null,

    // Colors
    val colorTitle: String? = null,
    val colorTitleDark: String? = null,
    val colorContent: String? = null,
    val colorContentDark: String? = null,
    val colorSubContent: String? = null,
    val colorSubContentDark: String? = null
)