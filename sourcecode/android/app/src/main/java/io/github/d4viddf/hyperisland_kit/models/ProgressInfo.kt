package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

// This is for LINEAR progress (ParamV2) or BUTTON progress (HyperActionRef)
@Serializable
data class ProgressInfo(
    val progress: Int,
    @SerialName("colorProgress")
    val colorProgress: String? = null,
    @SerialName("colorProgressEnd")
    val colorProgressEnd: String? = null,
    @SerialName("picForward")
    val picForward: String? = null,
    @SerialName("picMiddle")
    val picMiddle: String? = null,
    @SerialName("picMiddleUnselected")
    val picMiddleUnselected: String? = null,
    @SerialName("picEnd")
    val picEnd: String? = null,
    @SerialName("picEndUnselected")
    val picEndUnselected: String? = null
)