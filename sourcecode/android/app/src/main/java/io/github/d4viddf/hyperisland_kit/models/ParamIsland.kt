package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class ParamIsland(
    @SerialName("islandProperty") val islandProperty: Int = 1,
    @SerialName("islandPriority") val islandPriority: Int = 2,
    @SerialName("islandTimeout") val islandTimeout: Int? = null,
    @SerialName("islandOrder") val islandOrder: Boolean = false,

    // Config Flags
    val dismissIsland: Boolean = false,
    val maxSize: Boolean = false,
    val needCloseAnimation: Boolean = true,
    val expandedTime: Int? = null,
    val highlightColor: String? = null,

    // Areas
    @SerialName("bigIslandArea") val bigIslandArea: BigIslandArea? = null,
    @SerialName("smallIslandArea") val smallIslandArea: SmallIslandArea? = null,
    val shareData: ShareData? = null
)

@Serializable
data class ShareData(
    val title: String,
    val content: String,
    val pic: String,
    val shareContent: String,
    val sharePic: String? = null
)