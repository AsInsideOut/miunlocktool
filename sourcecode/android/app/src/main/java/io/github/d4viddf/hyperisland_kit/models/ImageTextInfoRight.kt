package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class ImageTextInfoRight(
    val type: Int = 2,
    val picInfo: PicInfo? = null,
    val textInfo: TextInfo? = null
)