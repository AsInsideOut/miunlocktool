package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class PicInfo(
    val type: Int = 1, // 1=Image, 2=Anim
    val pic: String,

    // Animation Props
    val loop: Boolean = false,
    val autoplay: Boolean = false,
    val number: Int = 0,

    // Effects
    val contentDescription: String? = null,
    val effectColor: String? = null,
    val effectSrc: String? = null
)