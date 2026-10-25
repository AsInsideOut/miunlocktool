package io.github.d4viddf.hyperisland_kit

import android.annotation.SuppressLint
import android.app.Notification
import android.app.PendingIntent
import android.content.Context
import android.graphics.Bitmap
import android.graphics.drawable.Icon
import android.os.Build
import android.os.Bundle
import android.widget.RemoteViews
import androidx.core.net.toUri
import io.github.d4viddf.hyperisland_kit.models.*
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.json.Json

private const val ACTION_PREFIX = "miui.focus.action_"
private const val PIC_PREFIX = "miui.focus.pic_"

// ==========================================
//  DATA WRAPPERS
// ==========================================

/**
 * Represents a clickable action button within the notification or island.
 * Can be configured as a standard icon button, a text-only button, or a progress button.
 *
 * @param key Unique identifier for this action (used to reference it in templates).
 * @param title The text label for the action.
 * @param icon The icon for the action (null for text-only buttons).
 * @param pendingIntent The intent to fire when clicked.
 * @param actionIntentType The type of intent: 1 = Activity, 2 = Broadcast, 3 = Service.
 * @param actionBgColor Background color in Hex (e.g., "#FF0000").
 * @param actionBgColorDark Background color for Dark Mode.
 * @param titleColor Text color in Hex.
 * @param titleColorDark Text color for Dark Mode.
 * @param isProgressButton If true, this button acts as a circular progress indicator.
 * @param progress The progress value (0-100) if [isProgressButton] is true.
 * @param progressColor Color of the progress arc.
 * @param colorReach Color of the reached progress (alternative to progressColor).
 * @param isCCW If true, progress draws Counter-Clockwise.
 */
data class HyperAction(
    val key: String,
    val title: CharSequence?,
    val icon: Icon?,
    val pendingIntent: PendingIntent,
    val actionIntentType: Int,

    // Customization Fields
    val actionBgColor: String? = null,
    val actionBgColorDark: String? = null,
    val titleColor: String? = null,
    val titleColorDark: String? = null,

    // Progress Button Fields
    val isProgressButton: Boolean = false,
    val progress: Int = 0,
    val progressColor: String? = null,
    val colorReach: String? = null,
    val isCCW: Boolean = false
) {
    // Constructor 1 (Standard Resource Icon)
    constructor(
        key: String, title: CharSequence?, context: Context, drawableRes: Int, pendingIntent: PendingIntent, actionIntentType: Int,
        isProgressButton: Boolean = false, progress: Int = 0, progressColor: String? = null, actionBgColor: String? = null, isCCW: Boolean = false, colorReach: String? = null
    ) : this(key, title, Icon.createWithResource(context, drawableRes), pendingIntent, actionIntentType, actionBgColor = actionBgColor, isProgressButton = isProgressButton, progress = progress, progressColor = progressColor, isCCW = isCCW, colorReach = colorReach)

    // Constructor 2 (Bitmap Icon)
    constructor(
        key: String, title: CharSequence?, bitmap: Bitmap, pendingIntent: PendingIntent, actionIntentType: Int,
        isProgressButton: Boolean = false, progress: Int = 0, progressColor: String? = null, actionBgColor: String? = null, isCCW: Boolean = false, colorReach: String? = null
    ) : this(key, title, Icon.createWithBitmap(bitmap), pendingIntent, actionIntentType, actionBgColor = actionBgColor, isProgressButton = isProgressButton, progress = progress, progressColor = progressColor, isCCW = isCCW, colorReach = colorReach)

    // Constructor 3 (Text Only / TextButton)
    constructor(
        key: String, title: CharSequence, pendingIntent: PendingIntent, actionIntentType: Int,
        bgColor: String? = null, bgColorDark: String? = null, titleColor: String? = null, titleColorDark: String? = null
    ) : this(key, title, null, pendingIntent, actionIntentType, actionBgColor = bgColor, actionBgColorDark = bgColorDark, titleColor = titleColor, titleColorDark = titleColorDark, isProgressButton = false)
}

/**
 * Wrapper for images used in the notification (Icons, Cover Art, Avatars).
 * @param key Unique identifier to reference this picture in templates.
 * @param icon The Android Icon object.
 */
data class HyperPicture(
    val key: String,
    val icon: Icon
) {
    constructor(key: String, context: Context, drawableRes: Int) : this(key, Icon.createWithResource(context, drawableRes))
    constructor(key: String, bitmap: Bitmap) : this(key, Icon.createWithBitmap(bitmap))
}

private fun createTransparentIcon(context: Context): Icon {
    return Icon.createWithResource(context, android.R.drawable.screen_background_light_transparent)
}

// ==========================================
//  BUILDER CLASS
// ==========================================

/**
 * Main Builder for creating HyperOS/Xiaomi Dynamic Island Notifications (Focus Notifications).
 * * Supports two modes:
 * 1. **Standard Template Mode**: Use setters like [setBaseInfo], [setChatInfo] to use system-defined layouts.
 * 2. **Custom View (DIY) Mode**: Use [setCustomRemoteView] to provide your own [RemoteViews] for total control.
 *
 * @param context Application context.
 * @param businessName Unique string ID for your notification logic (e.g., "music_player", "taxi_ride").
 * @param ticker Text shown in the status bar "pill" or small island.
 */
class HyperIslandNotification private constructor(
    private val context: Context,
    private val businessName: String,
    private val ticker: String
) {
    private var targetPage: String? = null
    private var scene: String? = null

    // Templates
    private var baseInfo: BaseInfo? = null
    private var chatInfo: ChatInfo? = null
    private var highlightInfo: HighlightInfo? = null
    private var highlightInfoV3: HighlightInfoV3? = null
    private var coverInfo: CoverInfo? = null
    private var animTextInfo: AnimTextInfo? = null
    private var iconTextInfo: IconTextInfo? = null

    // Components
    private var paramIsland: ParamIsland? = null
    private var progressBar: ProgressInfo? = null
    private var multiProgressInfo: MultiProgressInfo? = null
    private var bgInfo: BgInfo? = null
    private var hintInfo: HintInfo? = null
    private var stepInfo: StepInfo? = null
    private var textButton: List<TextButtonInfo>? = null
    private var bannerPicInfo: PicInfo? = null

    // Island Configs
    private var islandPriority: Int = 2
    private var islandTimeout: Int? = null
    private var dismissIsland: Boolean = false
    private var maxSize: Boolean = false
    private var needCloseAnimation: Boolean = true
    private var expandedTime: Int? = null
    private var highlightColor: String? = null
    private var shareData: ShareData? = null

    // General Configs
    private var timeout: Long? = null
    private var enableFloat: Boolean = true
    private var isShowNotification: Boolean = true
    private var logEnabled: Boolean = true

    private var islandFirstFloat: Boolean = true
    private var padding: Boolean? = null
    private var showSmallIcon: Boolean? = null
    private var hideDeco: Boolean? = null
    private var cancel: Boolean? = null
    private var reopen: Boolean? = null
    private var updatable: Boolean = true

    // Custom View (DIY) Specifics
    private var picTicker: Icon? = null
    private var picTickerDark: Icon? = null
    private var outEffectSrc: String? = null

    // AOD specific
    private var aodTitle: String? = null
    private var aodPic: Icon? = null

    // RemoteViews container
    private var rv: RemoteViews? = null
    private var rvAod: RemoteViews? = null
    private var rvNight: RemoteViews? = null
    private var rvTiny: RemoteViews? = null
    private var rvTinyNight: RemoteViews? = null
    private var rvDecoLand: RemoteViews? = null
    private var rvDecoLandNight: RemoteViews? = null
    private var rvDecoPort: RemoteViews? = null
    private var rvDecoPortNight: RemoteViews? = null
    private var rvIslandExpand: RemoteViews? = null

    // Action Lists
    private val actions = mutableListOf<HyperAction>()
    private val hiddenActions = mutableListOf<HyperAction>()
    private val pictures = mutableListOf<HyperPicture>()

    @OptIn(ExperimentalSerializationApi::class)
    private val jsonSerializer = Json {
        encodeDefaults = true
        explicitNulls = false
        ignoreUnknownKeys = true
    }

    private fun HyperAction.getType(): Int {
        return when {
            this.isProgressButton -> 1
            this.icon == null && this.title != null -> 2
            else -> 0
        }
    }

    // --- General Methods ---

    /** Enables logging of the JSON payload for debugging. */
    fun setLogEnabled(enabled: Boolean) = apply { this.logEnabled = enabled }

    /** Sets how long the notification stays visible (in milliseconds). */
    fun setTimeout(durationMs: Long) = apply { this.timeout = durationMs }

    /** If true, the notification will float (heads-up) when first posted. */
    fun setEnableFloat(enable: Boolean) = apply { this.enableFloat = enable }

    /** If false, the notification will NOT appear in the notification shade (Island only). */
    fun setShowNotification(show: Boolean) = apply { this.isShowNotification = show }

    /** Sets the target activity (Package + Class Name) to open in a small freeform window on tap. */
    fun setSmallWindowTarget(activityName: String) = apply { this.targetPage = activityName }

    /** Sets a scene ID for specific system animations (e.g., "recorder", "timer"). */
    fun setScene(sceneName: String) = apply { this.scene = sceneName }


    // ==========================================
    //  CUSTOM VIEW (DIY) SETTERS
    // ==========================================

    /**
     * [Custom Mode] Sets the main [RemoteViews] for the notification banner.
     * **Important:** Calling this switches the builder to 'Custom Mode'.
     * You must use [buildCustomExtras] instead of [buildResourceBundle]/[buildJsonParam].
     */
    fun setCustomRemoteView(rv: RemoteViews) = apply { this.rv = rv }

    /** [Custom Mode] Sets the RemoteViews for the Always-On Display (AOD). */
    fun setCustomAodRemoteView(rv: RemoteViews) = apply { this.rvAod = rv }

    /** [Custom Mode] Sets the RemoteViews for Dark Mode (Night). */
    fun setCustomNightRemoteView(rv: RemoteViews) = apply { this.rvNight = rv }

    /** [Custom Mode] Sets the RemoteViews for the Small Island (the pill/capsule state). */
    fun setCustomTinyRemoteView(rv: RemoteViews) = apply { this.rvTiny = rv }

    /** [Custom Mode] Sets the RemoteViews for the Small Island in Dark Mode. */
    fun setCustomTinyNightRemoteView(rv: RemoteViews) = apply { this.rvTinyNight = rv }

    /** [Custom Mode] Landscape decoration view. */
    fun setCustomDecoLandRemoteView(rv: RemoteViews) = apply { this.rvDecoLand = rv }

    /** [Custom Mode] Landscape decoration view (Dark Mode). */
    fun setCustomDecoLandNightRemoteView(rv: RemoteViews) = apply { this.rvDecoLandNight = rv }

    /** [Custom Mode] Portrait decoration view. */
    fun setCustomDecoPortRemoteView(rv: RemoteViews) = apply { this.rvDecoPort = rv }

    /** [Custom Mode] Portrait decoration view (Dark Mode). */
    fun setCustomDecoPortNightRemoteView(rv: RemoteViews) = apply { this.rvDecoPortNight = rv }

    /** [Custom Mode] Sets the RemoteViews for the Expanded Island (when long-pressed). */
    fun setCustomIslandExpandRemoteView(rv: RemoteViews) = apply { this.rvIslandExpand = rv }

    /** [Custom Mode] Required. Sets the icon displayed in the status bar/ticker. */
    fun setTickerIcon(icon: Icon) = apply { this.picTicker = icon }

    /** [Custom Mode] Optional. Sets the ticker icon for Dark Mode. */
    fun setTickerIconDark(icon: Icon) = apply { this.picTickerDark = icon }

    /** [Custom Mode] Configures AOD text title (use if not providing a custom AOD RemoteView). */
    fun setAodConfig(title: String?, pic: Icon? = null) = apply {
        this.aodTitle = title
        this.aodPic = pic
    }


    /** Adds an action that will appear in the notification's bottom action bar. */
    fun addAction(action: HyperAction) = apply { this.actions.add(action) }

    /**
     * Adds an action that is registered in the bundle but NOT shown in the bottom action bar.
     * Essential for actions used inside Island areas, Hints, or TextButtons.
     */
    fun addHiddenAction(action: HyperAction) = apply { this.hiddenActions.add(action) }

    /** Adds a picture resource to be referenced by its key in other methods. */
    fun addPicture(picture: HyperPicture) = apply { this.pictures.add(picture) }

    /**
     * Configures general Dynamic Island behavior.
     * @param priority Higher priority islands displace lower ones (Default 2).
     * @param timeout Auto-close timeout in ms.
     * @param dismissible If true, user can swipe away the island.
     * @param highlightColor Color for edge lighting effects.
     * @param maxSize If true, the island will use all the available space.
     * @param expandedTimeMs Time in ms to show the expanded island before closing.
     * @param needCloseAnimation If true, the island will have a close animation.
     */
    fun setIslandConfig(
        priority: Int = 2,
        timeout: Int? = null,
        dismissible: Boolean = false,
        maxSize: Boolean = false,
        highlightColor: String? = null,
        expandedTimeMs: Int? = null,
        needCloseAnimation: Boolean = true
    ) = apply {
        this.islandPriority = priority
        this.islandTimeout = timeout
        this.dismissIsland = dismissible
        this.maxSize = maxSize
        this.highlightColor = highlightColor
        this.expandedTime = expandedTimeMs
        this.needCloseAnimation = needCloseAnimation
    }

    /** Sets data for sharing content from the island. */
    fun setShareData(title: String, content: String, picKey: String, shareContent: String, sharePicKey: String? = null) = apply {
        this.shareData = ShareData(title = title, content = content, pic = PIC_PREFIX + picKey, shareContent = shareContent, sharePic = sharePicKey?.let { PIC_PREFIX + it })
    }

    // ==========================================
    //  TEMPLATE SETTERS
    // ==========================================

    /**
     * Sets the "Chat" template. Ideal for messaging or calls.
     * @param title Sender name.
     * @param content Message body.
     * @param pictureKey Sender avatar key.
     * @param actionKeys List of [HyperAction.key] to show.
     * @param titleColor Text color in Hex.
     * @param titleColorDark Text color for Dark Mode.
     * @param contentColor Text color in Hex.
     * @param contentColorDark Text color for Dark Mode.
     */
    fun setChatInfo(
        title: String,
        content: String? = null,
        pictureKey: String? = null,
        pictureKeyDark: String? = null,
        appPkg: String? = null,
        timer: TimerInfo? = null,
        actionKeys: List<String>? = null,
        titleColor: String? = null,
        titleColorDark: String? = null,
        contentColor: String? = null,
        contentColorDark: String? = null
    ) = apply {
        clearOtherTemplates()
        this.chatInfo = ChatInfo(
            title = title,
            content = if (timer != null) null else content,
            picFunction = pictureKey?.let { PIC_PREFIX + it },
            picFunctionDark = pictureKeyDark?.let { PIC_PREFIX + it },
            appIconPkg = appPkg,
            timerInfo = timer,
            colorTitle = titleColor,
            colorTitleDark = titleColorDark,
            colorContent = contentColor,
            colorContentDark = contentColorDark,
            actions = resolveActionKeys(actionKeys)
        )
    }

    /**
     * Sets the "Base" template. General purpose notification.
     * @param type 1 = Standard layout, 2 = Banner style (icon on right).
     * @param title Main headline.
     * @param content Main body text.
     * @param subTitle Secondary text (often top right).
     * @param subContent Secondary body text (often colored).
     */
    fun setBaseInfo(
        title: String,
        content: String,
        subTitle: String? = null,
        extraTitle: String? = null,
        specialTitle: String? = null,
        subContent: String? = null,
        pictureKey: String? = null,
        type: Int = 1,
        showDivider: Boolean? = null,
        showContentDivider: Boolean? = null,
        colorTitle: String? = null, colorSubTitle: String? = null, colorExtraTitle: String? = null, colorSpecialTitle: String? = null, colorSpecialBg: String? = null, colorContent: String? = null, colorSubContent: String? = null,
        colorTitleDark: String? = null, colorSubTitleDark: String? = null, colorExtraTitleDark: String? = null, colorSpecialTitleDark: String? = null, colorContentDark: String? = null, colorSubContentDark: String? = null,
        actionKeys: List<String>? = null
    ) = apply {
        clearOtherTemplates()
        this.baseInfo = BaseInfo(
            type, title, subTitle, extraTitle, specialTitle, content, subContent, pictureKey?.let { PIC_PREFIX + it },
            showDivider, showContentDivider,
            colorTitle, colorSubTitle, colorExtraTitle, colorSpecialTitle, colorSpecialBg, colorContent, colorSubContent,
            colorTitleDark, colorSubTitleDark, colorExtraTitleDark, colorSpecialTitleDark, colorContentDark, colorSubContentDark,
            resolveActionKeys(actionKeys)
        )
    }

    /** Sets the "Highlight" template (Timer/Recording style).
     * @param title Main headline.
     * @param content Main body text.
     * @param subContent Secondary body text.
     * @param picKey Icon key.
     * @param timer Timer info.
     */
    fun setHighlightInfo(title: String, content: String? = null, subContent: String? = null, picKey: String? = null, timer: TimerInfo? = null) = apply {
        clearOtherTemplates()
        this.highlightInfo = HighlightInfo(
            title = title,
            content = content,
            subContent = subContent,
            picFunction = picKey?.let { PIC_PREFIX + it },
            timerInfo = timer
        )
    }

    /** Sets Highlight V3 template. Suitable for Promos/Sales.
     * @param primaryText Main headline.
     * @param secondaryText Secondary body text.
     * @param primaryColor Primary color in Hex.
     */
    fun setHighlightInfoV3(primaryText: String, secondaryText: String? = null, label: String? = null, action: HyperAction? = null, primaryColor: String? = null) = apply {
        clearOtherTemplates()
        this.highlightInfoV3 = HighlightInfoV3(
            primaryText = primaryText,
            secondaryText = secondaryText,
            highLightText = label,
            actionInfo = action?.toActionRef(true),
            primaryColor = primaryColor
        )
    }

    /** Sets Cover template (Large vertical image on left).
     * @param picKey Icon key.
     * @param title Main headline.
     * @param content Main body text.
     * @param subContent Secondary body text.
     */
    fun setCoverInfo(picKey: String, title: String, content: String? = null, subContent: String? = null) = apply {
        clearOtherTemplates()
        this.coverInfo = CoverInfo(
            picCover = PIC_PREFIX + picKey,
            title = title,
            content = content,
            subContent = subContent
        )
    }

    /** Sets Animated Text template.
     * @param picKey Icon key.
     * @param title Main headline.
     * @param content Main body text.
     */
    fun setAnimTextInfo(picKey: String, title: String, content: String? = null, isAnimation: Boolean = false) = apply {
        clearOtherTemplates()
        this.animTextInfo = AnimTextInfo(
            animIconInfo = AnimIconInfo(src = resolvePicSource(picKey), type = if (isAnimation) 3 else 0),
            title = title,
            content = content
        )
    }

    /** Sets Icon Text template (Icon left, multiple text lines).
     * @param picKey Icon key.
     * @param title Main headline.
     * @param content Main body text.
     * @param subContent Secondary body text.
     */
    fun setIconTextInfo(picKey: String, title: String, content: String? = null, subContent: String? = null) = apply {
        clearOtherTemplates()
        this.iconTextInfo = IconTextInfo(
            animIconInfo = AnimIconInfo(src = resolvePicSource(picKey)),
            title = title,
            content = content,
            subContent = subContent
        )
    }


    // ==========================================
    //  COMPONENT SETTERS
    // ==========================================

    /** Replaces standard bottom actions with text-based buttons. */
    fun setTextButtons(vararg actions: HyperAction) = apply {
        this.textButton = actions.map { it.toTextButtonInfo() }
    }

    /** Adds a Hint bar (top bar) with a title and an optional action link. */
    fun setHintInfo(title: String, actionKey: String? = null) = apply {
        val actionRef = actionKey?.let { key ->
            (actions + hiddenActions).firstOrNull { it.key == key }?.toActionRef(true)
        }
        this.hintInfo = HintInfo(type = 1, title = title, actionInfo = actionRef)
    }

    /** Adds a Hint bar with title, content, and a specific action button. */
    fun setHintAction(title: String, content: String? = null, action: HyperAction) = apply {
        this.hintInfo = HintInfo(type = 1, title = title, content = content, actionInfo = action.toActionRef(true))
    }

    /** Adds a Hint bar configured as a Timer. */
    fun setHintTimer(frontText1: String, frontText2: String? = null, mainText1: String? = null, mainText2: String? = null, timer: TimerInfo? = null, action: HyperAction) = apply {
        this.hintInfo = HintInfo(type = 2, content = frontText1, subContent = frontText2, title = mainText1, subTitle = mainText2, timerInfo = timer, actionInfo = action.toActionRef(true))
    }

    /** Sets the background of the notification (Color or Image).
     * @param picKey Icon key.
     * @param color Background color in Hex.
     * @param type 1 = Color, 2 = Image.
     */
    fun setBackground(picKey: String? = null, color: String? = null, type: Int = 1) = apply {
        this.bgInfo = BgInfo(type, picKey?.let { PIC_PREFIX + it }, color)
    }

    /** Adds a Multi-Step progress bar component.
     * @param title Title of the progress bar.
     * @param progress Current progress.
     * @param color Color of the progress bar.
     * @param points Number of points in the progress bar 0-4.
     * */
    fun setMultiProgress(title: String, progress: Int, color: String? = null, points: Int = 0) = apply {
        this.multiProgressInfo = MultiProgressInfo(title, progress.coerceIn(0, 4), points.coerceIn(0, 4), color)
    }

    /** Adds a Step progress component. */
    fun setStepProgress(currentStep: Int, totalStep: Int, activeColor: String? = null) = apply {
        this.stepInfo = StepInfo(currentStep, totalStep, activeColor)
    }

    /**
     * Adds a graphical progress bar (e.g. for Taxi or Delivery).
     * @param picForwardKey Icon moving along the bar.
     * @param picEndKey Icon at the end (reached).
     * @param picEndUnselectedKey Icon at the end (not reached).
     * @param picMiddleKey Icon in the middle.
     * @param picMiddleUnselectedKey Icon in the middle (not reached).
     * @param progress Progress value (0-100).
     * @param color Color of the bar.
     * @param colorEnd Color of the bar at the end.
     */
    fun setProgressBar(progress: Int, color: String? = null, colorEnd: String? = null, picForwardKey: String? = null, picMiddleKey: String? = null, picMiddleUnselectedKey: String? = null, picEndKey: String? = null, picEndUnselectedKey: String? = null) = apply {
        this.progressBar = ProgressInfo(progress, color, colorEnd, picForwardKey?.let { PIC_PREFIX + it }, picMiddleKey?.let { PIC_PREFIX + it }, picMiddleUnselectedKey?.let { PIC_PREFIX + it }, picEndKey?.let { PIC_PREFIX + it }, picEndUnselectedKey?.let { PIC_PREFIX + it })
    }

    /** Sets the independent icon on the right side (Banner style). */
    fun setBannerIcon(type:Int=1,picKey: String) = apply {
        this.bannerPicInfo = PicInfo(type = type, pic = PIC_PREFIX + picKey)
    }

    /** Alias for [setBannerIcon] for compatibility. */
    fun setPicInfo(type: Int = 1, picKey: String) = apply {
        this.bannerPicInfo = PicInfo(type = type, pic = PIC_PREFIX + picKey)
    }

    // ==========================================
    //  ISLAND SETTERS
    // ==========================================

    /** Sets a simple icon for the Small Island (Capsule state). */
    fun setSmallIsland(picKey: String) = apply {
        ensureParamIsland()
        this.paramIsland = this.paramIsland?.copy(islandProperty = 1, smallIslandArea = SmallIslandArea(picInfo = PicInfo(type = 1, pic = PIC_PREFIX + picKey)))
    }

    /** Configures Small Island with a circular progress indicator. */
    fun setSmallIslandCircularProgress(pictureKey: String, progress: Int, color: String? = null, colorUnReach: String? = null, isCCW: Boolean = false) = apply {
        ensureParamIsland()
        val combine = CombinePicInfo(PicInfo(1, PIC_PREFIX + pictureKey), CircularProgressInfo(progress, color, colorUnReach, isCCW))
        this.paramIsland = this.paramIsland?.copy(islandProperty = 1, smallIslandArea = SmallIslandArea(combinePicInfo = combine))
    }

    /**
     * Configures the Expanded (Big) Island.
     * @param left Left area content (Image + Text).
     * @param right Right area content (Image + Text).
     * @param centerText TextInfo on the right side.
     * @param pic PicInfo on the right side.
     * @param progressText ProgressTextInfo on the right side.
     */
    fun setBigIslandInfo(
        left: ImageTextInfoLeft? = null,
        right: ImageTextInfoRight? = null,
        centerText: TextInfo? = null,
        pic: PicInfo? = null,
        progressText: ProgressTextInfo? = null,
    ) = apply {
        ensureParamIsland()
        val fixedLeft = left?.copy(picInfo = prefixPicInfo(left.picInfo))
        val fixedRight = right?.copy(picInfo = prefixPicInfo(right.picInfo))
        val fixedPic = prefixPicInfo(pic)

        this.paramIsland = this.paramIsland?.copy(
            islandProperty = 1,
            bigIslandArea = BigIslandArea(
                imageTextInfoLeft = fixedLeft,
                imageTextInfoRight = fixedRight,
                textInfo = centerText,
                picInfo = fixedPic,
                progressTextInfo = progressText,
            )
        )
    }

    /** Sets Big Island content with a fixed-width digit display (e.g., Score/Speed).
     * @param digit Number of digits to show.
     * @param content Content to display.
     * @param showHighlight If true, the digit will be highlighted.
     */
    fun setBigIslandFixedWidthDigit(digit: Int, content: String? = null, showHighlight: Boolean = false) = apply {
        ensureParamIsland()
        this.paramIsland = this.paramIsland?.copy(bigIslandArea = BigIslandArea(fixedWidthDigitInfo = FixedWidthDigitInfo(digit = digit, content = content, showHighlightColor = showHighlight)))
    }

    /** Sets Big Island content as a Countdown Timer.
     * @param countdownTime Time in ms (currenttimemillis() + countdownTime).
     * @param pictureKey Icon key.
     */
    fun setBigIslandCountdown(countdownTime: Long, pictureKey: String) = apply {
        ensureParamIsland()
        val timer = TimerInfo(-1, countdownTime, System.currentTimeMillis(), System.currentTimeMillis())
        val left = ImageTextInfoLeft(1, PicInfo(1, PIC_PREFIX + pictureKey), null, null)
        this.paramIsland = this.paramIsland?.copy(islandProperty = 1, bigIslandArea = BigIslandArea(imageTextInfoLeft = left, sameWidthDigitInfo = SameWidthDigitInfo(timerInfo = timer)))
    }

    /** Sets Big Island content as a Count-Up Timer.
     * @param startTime Start time in ms.
     * @param pictureKey Icon key.
     */
    fun setBigIslandCountUp(startTime: Long, pictureKey: String) = apply {
        ensureParamIsland()
        val timer = TimerInfo(1, startTime, startTime, startTime)
        val left = ImageTextInfoLeft(1, PicInfo(1, PIC_PREFIX + pictureKey), null, null)
        this.paramIsland = this.paramIsland?.copy(islandProperty = 1, bigIslandArea = BigIslandArea(imageTextInfoLeft = left, sameWidthDigitInfo = SameWidthDigitInfo(timerInfo = timer)))
    }

    /** Sets Big Island content with a large Progress Circle.
     * @param pictureKey Icon key.
     * @param title Title of the progress bar.
     * @param progress Current progress.
     * @param color Color of the progress bar.
     * @param isCCW If true, the progress bar will be drawn in a counter-clockwise direction.
     */
    fun setBigIslandProgressCircle(
        pictureKey: String,
        title: String,
        progress: Int,
        color: String? = null,
        isCCW: Boolean = false,
    ) = apply {
        if (this.paramIsland == null) this.paramIsland = ParamIsland()

        val leftInfo = ImageTextInfoLeft(type = 1, picInfo = PicInfo(type = 1, pic = "miui.focus.pic_" + pictureKey), textInfo = TextInfo(title = title, content = null))
        val progressComponent = ProgressTextInfo(progressInfo = CircularProgressInfo(progress = progress, colorReach = color, isCCW = isCCW), textInfo = null)

        this.paramIsland = this.paramIsland?.copy(
            islandProperty = 1,
            bigIslandArea = BigIslandArea(
                imageTextInfoLeft = leftInfo,
                progressTextInfo = progressComponent
            )
        )
    }

    /** Sets Big Island content to a looping animation.
     * @param animSrc Animation source.
     * @param isLoop If true, the animation will loop.
     * @param effectColor Color of the effect.
     */
    fun setBigIslandAnim(animSrc: String, isLoop: Boolean = true, effectColor: String? = null) = apply {
        ensureParamIsland()
        this.paramIsland = this.paramIsland?.copy(
            bigIslandArea = BigIslandArea(
                picInfo = PicInfo(type = 2, pic = resolvePicSource(animSrc), loop = isLoop, effectColor = effectColor)
            )
        )
    }

    /** If true, the Dynamic Island will expand automatically upon first display (Float first). */
    fun setIslandFirstFloat(enable: Boolean) = apply { this.islandFirstFloat = enable }

    /** Controls the padding around the content. */
    fun setPadding(enable: Boolean) = apply { this.padding = enable }

    /** Shows the small app icon in the header (usually for BaseInfo). */
    fun setShowSmallIcon(show: Boolean) = apply { this.showSmallIcon = show }

    /** Hides the decoration (like the arrow or extra icons) in certain templates. */
    fun setHideDeco(hide: Boolean) = apply { this.hideDeco = hide }

    /** If true, allows the notification to be cancelled/dismissed programmatically or by user. */
    fun setCancel(cancel: Boolean) = apply { this.cancel = cancel }

    /** Logic for reopening the island or app (specific to certain system apps). */
    fun setReopen(reopen: Boolean) = apply { this.reopen = reopen }

    // ==========================================
    //  BUILD & HELPERS
    // ==========================================

    private fun resolveActionKeys(keys: List<String>?): List<HyperActionRef>? {
        // Resolve from both visible and hidden actions
        return keys?.mapNotNull { key ->
            (actions + hiddenActions).firstOrNull { it.key == key }?.toActionRef(false)
        }?.ifEmpty { null }
    }

    private fun resolvePicSource(src: String): String {
        return if (pictures.any { PIC_PREFIX + it.key == src || it.key == src }) {
            if (src.startsWith(PIC_PREFIX)) src else PIC_PREFIX + src
        } else {
            src
        }
    }

    private fun ensureParamIsland() { if (this.paramIsland == null) this.paramIsland = ParamIsland() }
    private fun prefixPicInfo(picInfo: PicInfo?): PicInfo? { return picInfo?.copy(pic = PIC_PREFIX + picInfo.pic) }

    private fun clearOtherTemplates() {
        this.baseInfo = null
        this.chatInfo = null
        this.highlightInfo = null
        this.highlightInfoV3 = null
        this.coverInfo = null
        this.animTextInfo = null
        this.iconTextInfo = null
    }

    // ==========================================
    //  BUILD METHODS
    // ==========================================

    /**
     * **METHOD A: STANDARD TEMPLATE (ParamV2)**
     * * Use this method when you are using standard templates like [setBaseInfo], [setChatInfo].
     * @return Bundle containing actions and pictures. JSON must be generated via [buildJsonParam].
     */
    fun buildResourceBundle(): Bundle {
        val bundle = Bundle()
        val actionsBundle = Bundle()

        val allActions = actions + hiddenActions

        allActions.forEach {
            val actionIcon = it.icon ?: createTransparentIcon(context)
            actionsBundle.putParcelable(ACTION_PREFIX + it.key, Notification.Action.Builder(actionIcon, it.title, it.pendingIntent).build())
        }
        bundle.putBundle("miui.focus.actions", actionsBundle)

        val picsBundle = Bundle()
        pictures.forEach { picsBundle.putParcelable(PIC_PREFIX + it.key, it.icon) }
        bundle.putBundle("miui.focus.pics", picsBundle)
        return bundle
    }

    /**
     * Generates the JSON String for Standard Templates.
     * Pass this string to `notification.extras.putString("miui.focus.param", ...)`
     */
    fun buildJsonParam(): String {
        val finalIsland = (this.paramIsland ?: ParamIsland()).copy(
            islandPriority = this.islandPriority, islandTimeout = this.islandTimeout, dismissIsland = this.dismissIsland,
            maxSize = this.maxSize, needCloseAnimation = this.needCloseAnimation, expandedTime = this.expandedTime,
            highlightColor = this.highlightColor, shareData = this.shareData
        )

        val paramV2 = ParamV2(
            business = businessName, ticker = ticker, smallWindowInfo = targetPage?.let { SmallWindowInfo(it) }, scene = scene,
            timeout = timeout, enableFloat = enableFloat, isShowNotification = isShowNotification,
            islandFirstFloat = this.islandFirstFloat, padding = this.padding, showSmallIcon = this.showSmallIcon,
            hideDeco = this.hideDeco, cancel = this.cancel, reopen = this.reopen,
            chatInfo = chatInfo, baseInfo = baseInfo, highlightInfo = highlightInfo, highlightInfoV3 = highlightInfoV3,
            coverInfo = coverInfo, animTextInfo = animTextInfo, iconTextInfo = iconTextInfo,
            paramIsland = finalIsland,
            actions = actions.map { it.toActionRef(true) }.ifEmpty { null },
            textButton = textButton, progressInfo = progressBar, multiProgressInfo = multiProgressInfo, bgInfo = bgInfo,
            hintInfo = hintInfo, stepInfo = stepInfo, bannerPicInfo = this.bannerPicInfo
        )
        val payload = HyperIslandPayload(paramV2, scene = scene)
        return jsonSerializer.encodeToString(HyperIslandPayload.serializer(), payload)
    }

    /**
     * **METHOD B: CUSTOM VIEW (DIY)**
     * * Use this method when you have set a RemoteView using [setCustomRemoteView].
     * * @return A SINGLE Bundle containing everything (JSON for 'custom', Pictures, and RemoteViews).
     * Add this result directly to your NotificationCompat.Builder using `.addExtras()`.
     */
    fun buildCustomExtras(): Bundle {
        val extras = Bundle()
        val picsBundle = Bundle()

        // 1. Ticker Images
        if (picTicker != null) {
            picsBundle.putParcelable("miui.focus.pic_ticker", picTicker)
        }
        if (picTickerDark != null) {
            picsBundle.putParcelable("miui.focus.pic_ticker_dark", picTickerDark)
        }

        // 2. AOD Images
        if (aodTitle != null && rvAod == null && aodPic != null) {
            picsBundle.putParcelable("miui.focus.pic_aod", aodPic)
        }

        // 3. Additional Pictures (from addPicture)
        pictures.forEach { picsBundle.putParcelable(PIC_PREFIX + it.key, it.icon) }

        // 4. Construct JSON (ParamCustom)
        val finalIsland = (this.paramIsland ?: ParamIsland()).copy(
            islandPriority = this.islandPriority, islandTimeout = this.islandTimeout, dismissIsland = this.dismissIsland,
            maxSize = this.maxSize, needCloseAnimation = this.needCloseAnimation, expandedTime = this.expandedTime,
            highlightColor = this.highlightColor
        )

        val paramCustom = ParamCustom(
            ticker = ticker,
            tickerPic = if (picTicker != null) "miui.focus.pic_ticker" else null,
            tickerPicDark = if (picTickerDark != null) "miui.focus.pic_ticker_dark" else null,
            enableFloat = enableFloat,
            updatable = updatable,
            isShowNotification = isShowNotification,
            islandFirstFloat = islandFirstFloat,
            timeout = timeout,
            reopen = reopen,
            outEffectSrc = outEffectSrc,
            aodTitle = if (rvAod == null) aodTitle else null,
            aodPic = if (aodTitle != null && rvAod == null && aodPic != null) "miui.focus.pic_aod" else null,
            paramIsland = finalIsland
        )

        // 5. Pack everything
        extras.putString("miui.focus.param.custom", jsonSerializer.encodeToString(ParamCustom.serializer(), paramCustom))
        extras.putParcelable("miui.focus.pics", picsBundle)
        extras.putString("miui.focus.ticker", ticker)

        // 6. Pack RemoteViews
        rv?.let { extras.putParcelable("miui.focus.rv", it) }
        rvAod?.let { extras.putParcelable("miui.focus.rvAod", it) }
        rvNight?.let { extras.putParcelable("miui.focus.rvNight", it) }
        rvTiny?.let { extras.putParcelable("miui.focus.rv.tiny", it) }
        rvTinyNight?.let { extras.putParcelable("miui.focus.rv.tinyNight", it) }
        rvDecoLand?.let { extras.putParcelable("miui.focus.rv.deco.land", it) }
        rvDecoLandNight?.let { extras.putParcelable("miui.focus.rv.deco.landNight", it) }
        rvDecoPort?.let { extras.putParcelable("miui.focus.rv.deco.port", it) }
        rvDecoPortNight?.let { extras.putParcelable("miui.focus.rv.deco.portNight", it) }
        rvIslandExpand?.let { extras.putParcelable("miui.focus.rv.island.expand", it) }

        return extras
    }

    private fun HyperAction.toActionRef(isFullDefinition: Boolean): HyperActionRef {
        val pKey = ACTION_PREFIX + this.key
        return HyperActionRef(
            type = this.getType(),
            action = if (isFullDefinition) pKey else null,
            actionIntent = if (!isFullDefinition) pKey else null,
            actionIntentType = this.actionIntentType,
            progressInfo = if (this.isProgressButton) ProgressInfo(this.progress, this.colorReach ?: this.progressColor) else null,
            actionTitle = this.title?.toString(),
            actionBgColor = this.actionBgColor
        )
    }

    private fun HyperAction.toTextButtonInfo(): TextButtonInfo {
        val iconKey = if (this.icon != null) PIC_PREFIX + this.key else null
        return TextButtonInfo(
            type = 0,
            actionTitle = this.title?.toString() ?: "",
            actionIcon = iconKey, actionIconDark = iconKey,
            actionBgColor = this.actionBgColor, actionBgColorDark = this.actionBgColorDark ?: this.actionBgColor,
            actionTitleColor = this.titleColor, actionTitleColorDark = this.titleColorDark ?: this.titleColor,
            actionIntentType = this.actionIntentType, actionIntent = ACTION_PREFIX + this.key
        )
    }

    companion object {
        fun Builder(context: Context, businessName: String, ticker: String): HyperIslandNotification = HyperIslandNotification(context, businessName, ticker)
        fun isSupported(context: Context): Boolean = isXiaomiDevice() && hasFocusPermission(context) && isSupportIsland()
        private fun isXiaomiDevice() = Build.MANUFACTURER.equals("Xiaomi", ignoreCase = true)
        private fun hasFocusPermission(context: Context): Boolean {
            return try {
                val bundle = context.contentResolver.call("content://miui.statusbar.notification.public".toUri(), "canShowFocus", null, Bundle().apply { putString("package", context.packageName) })
                bundle?.getBoolean("canShowFocus", false) ?: false
            } catch (e: Exception) { false }
        }
        @SuppressLint("PrivateApi")
        private fun isSupportIsland(): Boolean {
            return try {
                val method = Class.forName("android.os.SystemProperties").getDeclaredMethod("getBoolean", String::class.java, Boolean::class.java)
                method.invoke(null, "persist.sys.feature.island", false) as Boolean
            } catch (e: Exception) { false }
        }
    }
}