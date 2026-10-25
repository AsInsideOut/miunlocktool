package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class SameWidthDigitInfo(
    val content: String? = null,
    val digit: String? = null,
    val timerInfo: TimerInfo? = null,
    @SerialName("showHighlightColor") val showHighlightColor: Boolean = true,
    val turnAnim: Boolean = false
)