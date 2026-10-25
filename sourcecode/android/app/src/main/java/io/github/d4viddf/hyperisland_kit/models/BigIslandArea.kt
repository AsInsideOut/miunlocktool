package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class BigIslandArea(
    @SerialName("imageTextInfoLeft") val imageTextInfoLeft: ImageTextInfoLeft? = null,
    @SerialName("imageTextInfoRight") val imageTextInfoRight: ImageTextInfoRight? = null,
    @SerialName("sameWidthDigitInfo") val sameWidthDigitInfo: SameWidthDigitInfo? = null,
    @SerialName("fixedWidthDigitInfo") val fixedWidthDigitInfo: FixedWidthDigitInfo? = null,
    @SerialName("progressTextInfo") val progressTextInfo: ProgressTextInfo? = null,
    val textInfo: TextInfo? = null,
    val picInfo: PicInfo? = null,
)