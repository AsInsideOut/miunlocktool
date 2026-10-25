package com.asinsideout.miunlocktool.ui.components.glass

import android.view.HapticFeedbackConstants
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.EaseOut
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.spring
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.text.BasicText
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.snapshotFlow
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.paint
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.clearAndSetSemantics
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.util.fastCoerceIn
import androidx.compose.ui.util.fastRoundToInt
import androidx.compose.ui.util.lerp
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.data.TranslationManager
import com.kyant.backdrop.Backdrop
import com.kyant.backdrop.backdrops.emptyBackdrop
import com.kyant.backdrop.backdrops.layerBackdrop
import com.kyant.backdrop.backdrops.rememberCombinedBackdrop
import com.kyant.backdrop.backdrops.rememberLayerBackdrop
import com.kyant.backdrop.drawBackdrop
import com.kyant.backdrop.effects.blur
import com.kyant.backdrop.effects.lens
import com.kyant.backdrop.effects.vibrancy
import com.kyant.backdrop.highlight.Highlight
import com.kyant.backdrop.shadow.InnerShadow
import com.kyant.backdrop.shadow.Shadow
import kotlinx.coroutines.flow.collectLatest
import kotlinx.coroutines.flow.drop
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.sign

private val LocalLiquidBottomTabScale = staticCompositionLocalOf { { 1f } }

data class LiquidTabItem(
    val id: Int,
    val iconRes: Int,
    val titleKey: String
)

val LIQUID_TABS = listOf(
    LiquidTabItem(0, R.drawable.ic_apply, "nav_apply"),
    LiquidTabItem(1, R.drawable.ic_guide, "nav_guide"),
    LiquidTabItem(2, R.drawable.ic_settings, "nav_settings")
)

@Composable
fun LiquidGlassBottomNavigation(
    selectedTabIndex: Int,
    onTabSelected: (Int) -> Unit,
    accentColor: Color,
    modifier: Modifier = Modifier,
    backdrop: Backdrop = emptyBackdrop()
) {
    val isDark = isSystemInDarkTheme()
    val tabsCount = LIQUID_TABS.size

    val view = LocalView.current

    val containerColor = if (isDark) {
        Color(0xFF18181C).copy(alpha = 0.58f)
    } else {
        Color(0xFFFAFAFA).copy(alpha = 0.65f)
    }

    val tabsBackdrop = rememberLayerBackdrop()

    Box(
        modifier = modifier
            .fillMaxWidth()
            .navigationBarsPadding()
            .padding(horizontal = 20.dp, vertical = 10.dp),
        contentAlignment = Alignment.Center
    ) {
        BoxWithConstraints(
            modifier = Modifier
                .widthIn(max = 440.dp)
                .fillMaxWidth(),
            contentAlignment = Alignment.CenterStart
        ) {
            val density = LocalDensity.current
            val tabWidth = with(density) {
                (constraints.maxWidth.toFloat() - 8f.dp.toPx()) / tabsCount
            }

            val offsetAnimation = remember { Animatable(0f) }
            val panelOffset by remember(density) {
                derivedStateOf {
                    val fraction = (offsetAnimation.value / constraints.maxWidth).fastCoerceIn(-1f, 1f)
                    with(density) {
                        4f.dp.toPx() * fraction.sign * EaseOut.transform(abs(fraction))
                    }
                }
            }

            val isLtr = LocalLayoutDirection.current == LayoutDirection.Ltr
            val animationScope = rememberCoroutineScope()
            var currentIndex by remember(selectedTabIndex) {
                mutableIntStateOf(selectedTabIndex)
            }

            val dampedDragAnimation = remember(animationScope) {
                DampedDragAnimation(
                    animationScope = animationScope,
                    initialValue = selectedTabIndex.toFloat(),
                    valueRange = 0f..(tabsCount - 1).toFloat(),
                    visibilityThreshold = 0.001f,
                    initialScale = 1f,
                    pressedScale = 78f / 56f,
                    onDragStarted = {},
                    onDragStopped = {
                        val targetIndex = targetValue.fastRoundToInt().coerceIn(0, tabsCount - 1)
                        currentIndex = targetIndex
                        animateToValue(targetIndex.toFloat())
                        onTabSelected(targetIndex)
                        animationScope.launch {
                            offsetAnimation.animateTo(
                                0f,
                                spring(1f, 300f, 0.5f)
                            )
                        }
                    },
                    onDrag = { _, dragAmount ->
                        updateValue(
                            (targetValue + dragAmount.x / tabWidth * if (isLtr) 1f else -1f)
                                .fastCoerceIn(0f, (tabsCount - 1).toFloat())
                        )
                        animationScope.launch {
                            offsetAnimation.snapTo(offsetAnimation.value + dragAmount.x)
                        }
                    }
                )
            }

            LaunchedEffect(selectedTabIndex) {
                if (currentIndex != selectedTabIndex) {
                    currentIndex = selectedTabIndex
                    dampedDragAnimation.animateToValue(selectedTabIndex.toFloat())
                }
            }

            val interactiveHighlight = remember(animationScope) {
                InteractiveHighlight(
                    animationScope = animationScope,
                    position = { size, _ ->
                        Offset(
                            if (isLtr) (dampedDragAnimation.value + 0.5f) * tabWidth + panelOffset
                            else size.width - (dampedDragAnimation.value + 0.5f) * tabWidth + panelOffset,
                            size.height / 2f
                        )
                    }
                )
            }

            // Glass dock body
            Row(
                Modifier
                    .graphicsLayer {
                        translationX = panelOffset
                    }
                    .drawBackdrop(
                        backdrop = backdrop,
                        shape = { Capsule() },
                        effects = {
                            vibrancy()
                            blur(18f.dp.toPx())
                            lens(26f.dp.toPx(), 26f.dp.toPx(), depthEffect = true, chromaticAberration = true)
                        },
                        highlight = {
                            Highlight(
                                width = 1f.dp,
                                blurRadius = 1.dp,
                                alpha = if (isDark) 0.40f else 0.75f
                            )
                        },
                        shadow = {
                            Shadow(
                                radius = 24.dp,
                                color = Color.Black.copy(alpha = if (isDark) 0.38f else 0.16f)
                            )
                        },
                        innerShadow = {
                            InnerShadow(
                                radius = 8.dp,
                                color = if (isDark) Color.White.copy(alpha = 0.08f) else Color.White.copy(alpha = 0.45f)
                            )
                        },
                        layerBlock = {
                            val progress = dampedDragAnimation.pressProgress
                            val scale = lerp(1f, 1f + 12f.dp.toPx() / size.width, progress)
                            scaleX = scale
                            scaleY = scale
                        },
                        onDrawSurface = { drawRect(containerColor) }
                    )
                    .then(interactiveHighlight.modifier)
                    .height(64.dp)
                    .fillMaxWidth()
                    .padding(4.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                LIQUID_TABS.forEachIndexed { index, tab ->
                    LiquidTabItemView(
                        tab = tab,
                        isSelected = currentIndex == index,
                        accentColor = accentColor,
                        isDark = isDark,
                        onClick = {
                            view.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP)
                            if (currentIndex != index) {
                                currentIndex = index
                                animationScope.launch {
                                    dampedDragAnimation.animateToValue(index.toFloat())
                                }
                                onTabSelected(index)
                            }
                        }
                    )
                }
            }

            // Hidden mirror layer for lens composite
            CompositionLocalProvider(
                LocalLiquidBottomTabScale provides {
                    lerp(1f, 1.15f, dampedDragAnimation.pressProgress)
                }
            ) {
                Row(
                    Modifier
                        .clearAndSetSemantics {}
                        .alpha(0f)
                        .layerBackdrop(tabsBackdrop)
                        .graphicsLayer {
                            translationX = panelOffset
                        }
                        .drawBackdrop(
                            backdrop = backdrop,
                            shape = { Capsule() },
                            effects = {
                                val progress = dampedDragAnimation.pressProgress
                                vibrancy()
                                blur(8f.dp.toPx())
                                lens(
                                    24f.dp.toPx() * progress,
                                    24f.dp.toPx() * progress,
                                    chromaticAberration = true
                                )
                            },
                            highlight = {
                                val progress = dampedDragAnimation.pressProgress
                                Highlight.Default.copy(alpha = progress)
                            },
                            onDrawSurface = { drawRect(containerColor) }
                        )
                        .then(interactiveHighlight.modifier)
                        .height(56.dp)
                        .fillMaxWidth()
                        .padding(horizontal = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    LIQUID_TABS.forEachIndexed { index, tab ->
                        LiquidTabItemView(
                            tab = tab,
                            isSelected = currentIndex == index,
                            accentColor = accentColor,
                            isDark = isDark,
                            onClick = null
                        )
                    }
                }
            }

            // Sliding active liquid bubble pill with refraction & chromatic dispersion
            Box(
                Modifier
                    .padding(horizontal = 4.dp)
                    .graphicsLayer {
                        translationX =
                            if (isLtr) dampedDragAnimation.value * tabWidth + panelOffset
                            else size.width - (dampedDragAnimation.value + 1f) * tabWidth + panelOffset
                    }
                    .then(interactiveHighlight.gestureModifier)
                    .then(dampedDragAnimation.modifier)
                    .drawBackdrop(
                        backdrop = rememberCombinedBackdrop(backdrop, tabsBackdrop),
                        shape = { Capsule() },
                        effects = {
                            val progress = dampedDragAnimation.pressProgress
                            lens(
                                12f.dp.toPx() * (0.6f + 0.4f * progress),
                                16f.dp.toPx() * (0.6f + 0.4f * progress),
                                depthEffect = true,
                                chromaticAberration = true
                            )
                        },
                        highlight = {
                            val progress = dampedDragAnimation.pressProgress
                            Highlight.Default.copy(
                                width = 1.dp,
                                alpha = 0.5f + 0.5f * progress
                            )
                        },
                        shadow = {
                            val progress = dampedDragAnimation.pressProgress
                            Shadow(
                                radius = 14.dp,
                                color = accentColor.copy(alpha = 0.35f + 0.25f * progress)
                            )
                        },
                        innerShadow = {
                            val progress = dampedDragAnimation.pressProgress
                            InnerShadow(
                                radius = 8.dp * (0.5f + 0.5f * progress),
                                color = Color.White.copy(alpha = 0.25f + 0.35f * progress),
                                alpha = 0.6f + 0.4f * progress
                            )
                        },
                        layerBlock = {
                            scaleX = dampedDragAnimation.scaleX
                            scaleY = dampedDragAnimation.scaleY
                            val velocity = dampedDragAnimation.velocity / 10f
                            scaleX /= 1f - (velocity * 0.75f).fastCoerceIn(-0.2f, 0.2f)
                            scaleY *= 1f - (velocity * 0.25f).fastCoerceIn(-0.2f, 0.2f)
                        },
                        onDrawSurface = {
                            val progress = dampedDragAnimation.pressProgress
                            // Luminous accent color liquid core
                            drawRect(
                                accentColor.copy(alpha = if (isDark) 0.32f else 0.22f)
                            )
                            drawRect(
                                if (isDark) Color.White.copy(alpha = 0.12f * (1f - progress))
                                else Color.Black.copy(alpha = 0.05f * (1f - progress))
                            )
                            drawRect(
                                accentColor.copy(alpha = 0.25f * progress)
                            )
                        }
                    )
                    .height(56.dp)
                    .fillMaxWidth(1f / tabsCount)
            )
        }
    }
}

@Composable
private fun androidx.compose.foundation.layout.RowScope.LiquidTabItemView(
    tab: LiquidTabItem,
    isSelected: Boolean,
    accentColor: Color,
    isDark: Boolean,
    onClick: (() -> Unit)? = null
) {
    val scale = LocalLiquidBottomTabScale.current

    val title = TranslationManager.tr(tab.titleKey)

    val targetContentColor = if (isSelected) {
        if (isDark) Color.White else accentColor
    } else {
        if (isDark) Color(0xFFB0B0B8) else Color(0xFF6B6B76)
    }
    val contentColor by animateColorAsState(
        targetValue = targetContentColor,
        animationSpec = spring(stiffness = 400f),
        label = "tabContentColor"
    )

    val scaleFactor by animateFloatAsState(
        targetValue = if (isSelected) 1.05f else 1.0f,
        animationSpec = spring(dampingRatio = 0.7f, stiffness = 400f),
        label = "tabScale"
    )

    val iconPainter = painterResource(id = tab.iconRes)

    Column(
        modifier = Modifier
            .weight(1f)
            .fillMaxHeight()
            .clip(Capsule())
            .then(
                if (onClick != null) {
                    Modifier.clickable(
                        interactionSource = remember { MutableInteractionSource() },
                        indication = null,
                        role = Role.Tab,
                        onClick = onClick
                    )
                } else Modifier
            )
            .graphicsLayer {
                val sc = scale() * scaleFactor
                scaleX = sc
                scaleY = sc
            },
        verticalArrangement = Arrangement.spacedBy(3.dp, Alignment.CenterVertically),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            Modifier
                .size(22.dp)
                .paint(
                    iconPainter,
                    colorFilter = ColorFilter.tint(contentColor)
                )
        )
        BasicText(
            text = title,
            style = TextStyle(
                color = contentColor,
                fontSize = 11.sp,
                fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
            )
        )
    }
}
