package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ChatInfo(
    val type: Int = 1,
    val title: String,
    val content: String? = null,

    // Images
    @SerialName("picProfile") val picFunction: String? = null,      // Light mode avatar
    @SerialName("picProfileDark") val picFunctionDark: String? = null, // Dark mode avatar
    @SerialName("appIconPkg") val appIconPkg: String? = null,       // Custom App Icon (Package Name)

    // Colors
    val colorTitle: String? = null,
    val colorTitleDark: String? = null,
    val colorContent: String? = null,
    val colorContentDark: String? = null,

    // Logic
    val actions: List<HyperActionRef>? = null,
    val timerInfo: TimerInfo? = null
)