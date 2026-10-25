package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

/**
 * Configuration payload for "DIY" (Custom RemoteView) Focus Notifications.
 * This is used when 'miui.focus.param.custom' is required instead of 'miui.focus.param'.
 */
@Serializable
data class ParamCustom(
    // --- Core Content ---
    val ticker: String,
    @SerialName("tickerPic") val tickerPic: String? = null,
    @SerialName("tickerPicDark") val tickerPicDark: String? = null,

    // --- Configuration ---
    val enableFloat: Boolean = true,
    val updatable: Boolean = true,
    val isShowNotification: Boolean = true,
    @SerialName("islandFirstFloat") val islandFirstFloat: Boolean = true,
    val timeout: Long? = 5000,
    val reopen: Boolean? = true,

    // --- Visual Effects ---
    @SerialName("outEffectSrc") val outEffectSrc: String? = null,

    // --- AOD (Always On Display) ---
    @SerialName("aodTitle") val aodTitle: String? = null,
    @SerialName("aodPic") val aodPic: String? = null,

    // --- Island Interaction ---
    @SerialName("param_island") val paramIsland: ParamIsland? = null
)