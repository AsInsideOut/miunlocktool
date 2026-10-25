package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ParamV2(
    val protocol: Int = 3,
    val business: String,
    val updatable: Boolean = true,
    val ticker: String,

    // --- Basic Config ---
    @SerialName("timeout") val timeout: Long? = null,
    @SerialName("enableFloat") val enableFloat: Boolean = true,
    @SerialName("isShowNotification") val isShowNotification: Boolean = true,
    @SerialName("islandFirstFloat") val islandFirstFloat: Boolean = false,
    @SerialName("padding") val padding: Boolean? = null,
    @SerialName("showSmallIcon") val showSmallIcon: Boolean? = null,
    @SerialName("hideDeco") val hideDeco: Boolean? = null,
    @SerialName("cancel") val cancel: Boolean? = null,
    @SerialName("reopen") val reopen: Boolean? = null,

    // --- Identifiers ---
    @SerialName("notifyId") val notifyId: String? = null,
    @SerialName("orderId") val orderId: String? = null,

    // --- Visual Assets ---
    val scene: String? = null,
    @SerialName("tickerPic") val tickerPic: String? = null,
    @SerialName("tickerPicDark") val tickerPicDark: String? = null,
    @SerialName("outEffectColor") val outEffectColor: String? = null,
    @SerialName("outEffectSrc") val outEffectSrc: String? = null,

    // --- Always On Display (AOD) ---
    @SerialName("aodTitle") val aodTitle: String? = null,
    @SerialName("aodPic") val aodPic: String? = null,

    // --- Right Side Icon (Banner) ---
    @SerialName("picInfo") val bannerPicInfo: PicInfo? = null,

    // --- Window Info ---
    @SerialName("smallWindowInfo") val smallWindowInfo: SmallWindowInfo? = null,

    // --- Island Configuration ---
    @SerialName("param_island") val paramIsland: ParamIsland? = null,

    // --- Data Templates (The Core Content) ---
    val baseInfo: BaseInfo? = null,
    val chatInfo: ChatInfo? = null,
    val highlightInfo: HighlightInfo? = null,
    val highlightInfoV3: HighlightInfoV3? = null,
    val coverInfo: CoverInfo? = null,
    val animTextInfo: AnimTextInfo? = null,
    val iconTextInfo: IconTextInfo? = null,
    val hintInfo: HintInfo? = null,
    val stepInfo: StepInfo? = null,

    // --- Components ---
    val bgInfo: BgInfo? = null,
    val actions: List<HyperActionRef>? = null,
    @SerialName("textButton") val textButton: List<TextButtonInfo>? = null,
    val progressInfo: ProgressInfo? = null,
    val multiProgressInfo: MultiProgressInfo? = null,
)