package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class CombinePicInfo(
    val picInfo: PicInfo,
    @SerialName("progressInfo")
    val progressInfo: CircularProgressInfo
)