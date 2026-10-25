package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.Serializable

@Serializable
data class HighlightInfo(
    val title: String, // Emphasized Text
    val content: String? = null, // Aux Text 1
    val subContent: String? = null, // Aux Text 2
    val picFunction: String? = null, // Function Icon
    val picFunctionDark: String? = null,
    val type: Int? = null, // 1: Hide Aux Text 1
    val timerInfo: TimerInfo? = null,

    // Colors
    val colorTitle: String? = null,
    val colorTitleDark: String? = null,
    val colorContent: String? = null,
    val colorContentDark: String? = null,
    val colorSubContent: String? = null,
    val colorSubContentDark: String? = null
)