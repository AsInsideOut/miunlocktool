package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class CircularProgressInfo(
    val progress: Int,
    @SerialName("colorReach")
    val colorReach: String? = null,
    @SerialName("colorUnReach")
    val colorUnReach: String? = null,
    @SerialName("isCCW")
    val isCCW: Boolean = false
)