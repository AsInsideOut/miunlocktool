package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class TextInfo(
    val title: String,
    val content: String? = null,
    @SerialName("showHighlightColor")
    val showHighlightColor: Boolean = false,
    val narrowFont: Boolean? = null
)