package com.asinsideout.miunlocktool.fastboot

import android.hardware.usb.UsbDevice

data class FastbootDeviceInfo(
    val device: UsbDevice,
    val name: String,
    val vendorId: Int,
    val productId: Int,
    val hasFastbootInterface: Boolean
)

data class FastbootCmdResult(
    val isSuccess: Boolean,
    val status: String, // "OKAY", "FAIL", "DATA", "ERROR"
    val payload: String = "",
    val infoLines: List<String> = emptyList(),
    val raw: String = "",
    val expectedDataLength: Long = 0L
)

enum class FastbootConnectionState {
    NO_DEVICE,
    DEVICE_ATTACHED,
    PERMISSION_REQUIRED,
    CONNECTING,
    CONNECTED,
    DISCONNECTED,
    ERROR
}
