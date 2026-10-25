package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class HyperActionRef(
    val type: Int,
    val action: String? = null,
    val progressInfo: ProgressInfo? = null,
    val actionTitle: String? = null,
    @SerialName("actionIntent")
    val actionIntent: String? = null,
    @SerialName("actionIntentType")
    val actionIntentType: Int? = null, // e.g., 1 for Activity, 2 for Broadcast, 3 for Service
    @SerialName("actionBgColor")
    val actionBgColor: String? = null
)
