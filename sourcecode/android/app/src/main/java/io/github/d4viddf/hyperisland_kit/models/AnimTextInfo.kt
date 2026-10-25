package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class AnimIconInfo(
    val type: Int = 0,
    val src: String,
    val srcDark: String? = null,
    val loop: Boolean = true,
    val autoplay: Boolean = true
)

@Serializable
data class AnimTextInfo(
    val animIconInfo: AnimIconInfo,
    val title: String,
    val content: String? = null,
    val timerInfo: TimerInfo? = null,

    // Colors
    val colorTitle: String? = null,
    val colorTitleDark: String? = null,
    val colorContent: String? = null,
    val colorContentDark: String? = null
)

@Serializable
data class IconTextInfo(
    val animIconInfo: AnimIconInfo,
    val title: String,
    val content: String? = null,
    val subContent: String? = null,

    // Colors
    val colorTitle: String? = null,
    val colorTitleDark: String? = null,
    val colorContent: String? = null,
    val colorContentDark: String? = null
)