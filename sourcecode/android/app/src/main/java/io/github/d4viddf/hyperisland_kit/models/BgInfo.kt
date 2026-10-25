package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class BgInfo(
    val type: Int = 1, // 1: Fullscreen, 2: Right side
    val picBg: String? = null,
    val colorBg: String? = null
)