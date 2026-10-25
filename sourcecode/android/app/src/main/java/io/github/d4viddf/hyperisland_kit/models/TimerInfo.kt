package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class TimerInfo(
    @SerialName("timerType")
    val timerType: Int,
    @SerialName("timerWhen")
    val timerWhen: Long,
    @SerialName("timerTotal")
    val timerTotal: Long,
    @SerialName("timerSystemCurrent")
    val timerSystemCurrent: Long
)