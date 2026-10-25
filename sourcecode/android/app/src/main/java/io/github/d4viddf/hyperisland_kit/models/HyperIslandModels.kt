package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class HyperIslandPayload(
    @SerialName("param_v2")
    val paramV2: ParamV2,

    // Top-level overrides (sometimes required by legacy HOS versions)
    val title: String? = null,
    val content: String? = null,
    val colorTitle: String? = null,
    val scene: String? = null,
    @SerialName("isShowNotification")
    val isShowNotification: Boolean = true
)