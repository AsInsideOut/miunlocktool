package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class FixedWidthDigitInfo(
    val content: String? = null,
    val digit: Int,
    val showHighlightColor: Boolean = false,
    val turnAnim: Boolean = true
)