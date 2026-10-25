package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SmallIslandArea(
    @SerialName("combinePicInfo") val combinePicInfo: CombinePicInfo? = null,
    val picInfo: PicInfo? = null
)