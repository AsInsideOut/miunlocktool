package com.asinsideout.miunlocktool.fastboot

import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.hardware.usb.UsbConstants
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbDeviceConnection
import android.hardware.usb.UsbEndpoint
import android.hardware.usb.UsbInterface
import android.hardware.usb.UsbManager
import android.os.Build
import java.nio.charset.StandardCharsets

class FastbootUsbTransport(private val usbManager: UsbManager) {

    companion object {
        const val ACTION_USB_PERMISSION = "com.asinsideout.miunlocktool.USB_PERMISSION"

        // Standard Fastboot USB Class/Subclass/Protocol (AOSP)
        const val FASTBOOT_CLASS = 0xFF        // 255 (Vendor Specific)
        const val FASTBOOT_SUBCLASS = 0x42     // 66
        const val FASTBOOT_PROTOCOL = 0x03     // 3

        // Well-known Fastboot Vendor IDs
        const val VID_XIAOMI = 0x2717
        const val VID_GOOGLE = 0x18D1
        const val VID_QUALCOMM = 0x05C6

        const val DEFAULT_TIMEOUT_MS = 5000
        const val DATA_TIMEOUT_MS = 30000
        const val MAX_COMMAND_LENGTH = 64
        const val BUFFER_SIZE = 4096
    }

    private var connection: UsbDeviceConnection? = null
    private var fastbootInterface: UsbInterface? = null
    private var inEndpoint: UsbEndpoint? = null
    private var outEndpoint: UsbEndpoint? = null
    private var connectedDevice: UsbDevice? = null

    val isConnected: Boolean
        get() = connection != null && inEndpoint != null && outEndpoint != null

    val currentDevice: UsbDevice?
        get() = connectedDevice

    /**
     * Scans for all USB devices attached to the host and determines which ones are likely in Fastboot mode.
     */
    fun findFastbootDevices(): List<FastbootDeviceInfo> {
        val list = mutableListOf<FastbootDeviceInfo>()
        val deviceList = usbManager.deviceList ?: return list

        for (device in deviceList.values) {
            val isFastboot = isFastbootDevice(device)
            val name = "${device.manufacturerName ?: "Unknown"} ${device.productName ?: "Device"}"
            list.add(
                FastbootDeviceInfo(
                    device = device,
                    name = name.trim(),
                    vendorId = device.vendorId,
                    productId = device.productId,
                    hasFastbootInterface = isFastboot
                )
            )
        }
        return list
    }

    /**
     * Checks if a UsbDevice matches Fastboot interface or known Fastboot hardware signatures.
     */
    fun isFastbootDevice(device: UsbDevice): Boolean {
        for (i in 0 until device.interfaceCount) {
            val intf = device.getInterface(i)
            // Exact AOSP Fastboot standard (Class 0xFF, Subclass 0x42, Protocol 0x03)
            if (intf.interfaceClass == FASTBOOT_CLASS &&
                intf.interfaceSubclass == FASTBOOT_SUBCLASS &&
                intf.interfaceProtocol == FASTBOOT_PROTOCOL
            ) {
                return true
            }
            // Relaxed Fastboot check (Class 0xFF, Subclass 0x42)
            if (intf.interfaceClass == FASTBOOT_CLASS && intf.interfaceSubclass == FASTBOOT_SUBCLASS) {
                return true
            }
        }

        // Secondary check: Known vendor with Bulk IN & Bulk OUT vendor interface
        if (device.vendorId == VID_XIAOMI || device.vendorId == VID_GOOGLE || device.vendorId == VID_QUALCOMM) {
            for (i in 0 until device.interfaceCount) {
                val intf = device.getInterface(i)
                if (intf.interfaceClass == FASTBOOT_CLASS) {
                    var hasIn = false
                    var hasOut = false
                    for (e in 0 until intf.endpointCount) {
                        val ep = intf.getEndpoint(e)
                        if (ep.type == UsbConstants.USB_ENDPOINT_XFER_BULK) {
                            if (ep.direction == UsbConstants.USB_DIR_IN) hasIn = true
                            if (ep.direction == UsbConstants.USB_DIR_OUT) hasOut = true
                        }
                    }
                    if (hasIn && hasOut) return true
                }
            }
        }
        return false
    }

    fun hasPermission(device: UsbDevice): Boolean {
        return usbManager.hasPermission(device)
    }

    fun requestPermission(context: Context, device: UsbDevice) {
        val flags = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        } else {
            PendingIntent.FLAG_UPDATE_CURRENT
        }
        val intent = Intent(ACTION_USB_PERMISSION).apply {
            setPackage(context.packageName)
        }
        val permissionIntent = PendingIntent.getBroadcast(context, 0, intent, flags)
        usbManager.requestPermission(device, permissionIntent)
    }

    @Synchronized
    fun connect(device: UsbDevice): Result<Unit> {
        disconnect()

        if (!usbManager.hasPermission(device)) {
            return Result.failure(SecurityException("USB permission not granted for device: ${device.deviceName}"))
        }

        var selectedInterface: UsbInterface? = null
        var inEp: UsbEndpoint? = null
        var outEp: UsbEndpoint? = null

        // Find matching fastboot interface and bulk endpoints
        for (i in 0 until device.interfaceCount) {
            val intf = device.getInterface(i)
            var currentIn: UsbEndpoint? = null
            var currentOut: UsbEndpoint? = null

            for (e in 0 until intf.endpointCount) {
                val ep = intf.getEndpoint(e)
                if (ep.type == UsbConstants.USB_ENDPOINT_XFER_BULK) {
                    if (ep.direction == UsbConstants.USB_DIR_IN) {
                        currentIn = ep
                    } else if (ep.direction == UsbConstants.USB_DIR_OUT) {
                        currentOut = ep
                    }
                }
            }

            if (currentIn != null && currentOut != null) {
                // Prefer exact Fastboot class
                if (intf.interfaceClass == FASTBOOT_CLASS && intf.interfaceSubclass == FASTBOOT_SUBCLASS) {
                    selectedInterface = intf
                    inEp = currentIn
                    outEp = currentOut
                    break
                } else if (selectedInterface == null) {
                    selectedInterface = intf
                    inEp = currentIn
                    outEp = currentOut
                }
            }
        }

        if (selectedInterface == null || inEp == null || outEp == null) {
            return Result.failure(IllegalStateException("No valid Fastboot bulk endpoints found on device"))
        }

        val conn = usbManager.openDevice(device)
            ?: return Result.failure(IllegalStateException("Unable to open UsbDeviceConnection"))

        if (!conn.claimInterface(selectedInterface, true)) {
            conn.close()
            return Result.failure(IllegalStateException("Failed to claim USB Fastboot interface"))
        }

        this.connection = conn
        this.fastbootInterface = selectedInterface
        this.inEndpoint = inEp
        this.outEndpoint = outEp
        this.connectedDevice = device

        return Result.success(Unit)
    }

    @Synchronized
    fun disconnect() {
        try {
            fastbootInterface?.let {
                connection?.releaseInterface(it)
            }
        } catch (_: Exception) {}

        try {
            connection?.close()
        } catch (_: Exception) {}

        connection = null
        fastbootInterface = null
        inEndpoint = null
        outEndpoint = null
        connectedDevice = null
    }

    @Synchronized
    fun sendCommand(command: String, timeoutMs: Int = DEFAULT_TIMEOUT_MS): Result<Unit> {
        val conn = connection ?: return Result.failure(IllegalStateException("Not connected"))
        val out = outEndpoint ?: return Result.failure(IllegalStateException("Out endpoint missing"))

        val bytes = command.toByteArray(StandardCharsets.US_ASCII)
        if (bytes.size > MAX_COMMAND_LENGTH) {
            return Result.failure(IllegalArgumentException("Command length exceeds $MAX_COMMAND_LENGTH bytes: $command"))
        }

        val transferred = conn.bulkTransfer(out, bytes, bytes.size, timeoutMs)
        return if (transferred == bytes.size) {
            Result.success(Unit)
        } else {
            Result.failure(IllegalStateException("Failed to send command: transferred $transferred of ${bytes.size} bytes"))
        }
    }

    @Synchronized
    fun readResponse(timeoutMs: Int = DEFAULT_TIMEOUT_MS): Result<FastbootCmdResult> {
        val conn = connection ?: return Result.failure(IllegalStateException("Not connected"))
        val inEp = inEndpoint ?: return Result.failure(IllegalStateException("In endpoint missing"))

        val buffer = ByteArray(BUFFER_SIZE)
        val infoLines = mutableListOf<String>()

        while (true) {
            val len = conn.bulkTransfer(inEp, buffer, buffer.size, timeoutMs)
            if (len < 0) {
                return Result.failure(IllegalStateException("Bulk read timeout or transfer error ($len)"))
            }
            if (len < 4) {
                return Result.failure(IllegalStateException("Malformed response from bootloader (less than 4 bytes: $len)"))
            }

            val prefix = String(buffer, 0, 4, StandardCharsets.US_ASCII)
            val payload = if (len > 4) {
                String(buffer, 4, len - 4, StandardCharsets.UTF_8).trim()
            } else {
                ""
            }

            when (prefix) {
                "INFO" -> {
                    // Accumulate info line and continue reading until OKAY or FAIL
                    infoLines.add(payload)
                }
                "OKAY" -> {
                    return Result.success(
                        FastbootCmdResult(
                            isSuccess = true,
                            status = "OKAY",
                            payload = payload,
                            infoLines = infoLines,
                            raw = String(buffer, 0, len, StandardCharsets.UTF_8)
                        )
                    )
                }
                "FAIL" -> {
                    return Result.success(
                        FastbootCmdResult(
                            isSuccess = false,
                            status = "FAIL",
                            payload = payload,
                            infoLines = infoLines,
                            raw = String(buffer, 0, len, StandardCharsets.UTF_8)
                        )
                    )
                }
                "DATA" -> {
                    val expectedLength = payload.toLongOrNull(16) ?: 0L
                    return Result.success(
                        FastbootCmdResult(
                            isSuccess = true,
                            status = "DATA",
                            payload = payload,
                            infoLines = infoLines,
                            raw = String(buffer, 0, len, StandardCharsets.UTF_8),
                            expectedDataLength = expectedLength
                        )
                    )
                }
                else -> {
                    return Result.success(
                        FastbootCmdResult(
                            isSuccess = false,
                            status = "ERROR",
                            payload = "Unexpected prefix: $prefix payload: $payload",
                            infoLines = infoLines,
                            raw = String(buffer, 0, len, StandardCharsets.ISO_8859_1)
                        )
                    )
                }
            }
        }
    }

    @Synchronized
    fun sendData(data: ByteArray, timeoutMs: Int = DATA_TIMEOUT_MS): Result<Unit> {
        val conn = connection ?: return Result.failure(IllegalStateException("Not connected"))
        val out = outEndpoint ?: return Result.failure(IllegalStateException("Out endpoint missing"))

        var offset = 0
        val chunkSize = 16384 // 16KB chunks

        while (offset < data.size) {
            val count = minOf(chunkSize, data.size - offset)
            val chunk = ByteArray(count)
            System.arraycopy(data, offset, chunk, 0, count)

            val transferred = conn.bulkTransfer(out, chunk, count, timeoutMs)
            if (transferred != count) {
                return Result.failure(IllegalStateException("Data transfer aborted at offset $offset: sent $transferred of $count bytes"))
            }
            offset += count
        }

        return Result.success(Unit)
    }

    fun execute(command: String, timeoutMs: Int = DEFAULT_TIMEOUT_MS): Result<FastbootCmdResult> {
        val sendRes = sendCommand(command, timeoutMs)
        if (sendRes.isFailure) {
            return Result.failure(sendRes.exceptionOrNull() ?: Exception("Failed to send command"))
        }
        return readResponse(timeoutMs)
    }
}
