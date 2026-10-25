package io.github.d4viddf.hyperisland_kit.models

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class StepInfo(
    val currentStep: Int,
    val totalStep: Int,
    @SerialName("activeColor")
    val activeColor: String? = null
)