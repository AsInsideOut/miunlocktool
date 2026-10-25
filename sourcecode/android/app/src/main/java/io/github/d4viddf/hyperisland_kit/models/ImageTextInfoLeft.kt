package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class ImageTextInfoLeft(
    val type: Int = 1,
    val picInfo: PicInfo? = null,
    val textInfo: TextInfo? = null,
    val progressInfo: CircularProgressInfo? = null
)