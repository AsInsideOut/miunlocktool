package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ProgressTextInfo(
    @SerialName("progressInfo")
    val progressInfo: CircularProgressInfo,
    val textInfo: TextInfo? = null
)