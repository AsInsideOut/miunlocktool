package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class HintInfo(
    val type: Int = 1, // 1 = Button Comp 3 (Action), 2 = Button Comp 2 (Timer/Text)

    // Type 1 Fields
    val title: String? = null,
    val content: String? = null, // Aux text
    @SerialName("actionInfo") val actionInfo: HyperActionRef? = null,

    // Type 2 Fields
    val subTitle: String? = null,
    val subContent: String? = null, // Front text 2
    val timerInfo: TimerInfo? = null
)