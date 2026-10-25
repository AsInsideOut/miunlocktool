package com.asinsideout.miunlocktool.fastboot

import java.util.Locale

class FastbootManager(val transport: FastbootUsbTransport) {

    /**
     * Retrieves the device codename (e.g. "redwood", "sweet", "marble") via 'getvar:product'.
     */
    fun getProduct(): Result<String> {
        if (!transport.isConnected) {
            return Result.failure(IllegalStateException("Fastboot device is not connected"))
        }

        val res = transport.execute("getvar:product")
        if (res.isFailure) {
            return Result.failure(res.exceptionOrNull() ?: Exception("Unknown error executing getvar:product"))
        }

        val cmdRes = res.getOrThrow()
        if (!cmdRes.isSuccess) {
            return Result.failure(IllegalStateException("getvar:product failed: ${cmdRes.payload} (status: ${cmdRes.status})"))
        }

        // Product can be returned directly in OKAY payload: e.g. "OKAYredwood" -> payload = "redwood"
        if (cmdRes.payload.isNotEmpty()) {
            val prod = cmdRes.payload.removePrefix("product:").trim()
            if (prod.isNotEmpty()) return Result.success(prod)
        }

        // Or product can be delivered via INFO lines: e.g. "INFOproduct: redwood"
        for (line in cmdRes.infoLines) {
            val clean = line.removePrefix("product:").trim()
            if (clean.isNotEmpty()) {
                return Result.success(clean)
            }
        }

        return Result.failure(IllegalStateException("Empty product returned from fastboot. Raw: ${cmdRes.raw}"))
    }

    /**
     * Retrieves the device unlock token.
     * Tries 'oem get_token' first, then falls back to 'getvar:token' if needed.
     */
    fun getToken(): Result<String> {
        if (!transport.isConnected) {
            return Result.failure(IllegalStateException("Fastboot device is not connected"))
        }

        // 1. Try 'oem get_token'
        val oemRes = transport.execute("oem get_token")
        if (oemRes.isSuccess) {
            val cmd = oemRes.getOrThrow()
            val parsedToken = parseTokenFromResponse(cmd)
            if (parsedToken.isNotEmpty()) {
                return Result.success(parsedToken)
            }
        }

        // 2. Fallback to 'getvar:token'
        val getvarRes = transport.execute("getvar:token")
        if (getvarRes.isSuccess) {
            val cmd = getvarRes.getOrThrow()
            val parsedToken = parseTokenFromResponse(cmd)
            if (parsedToken.isNotEmpty()) {
                return Result.success(parsedToken)
            }
        }

        val oemErr = oemRes.exceptionOrNull()?.message ?: oemRes.getOrNull()?.payload ?: "none"
        val getvarErr = getvarRes.exceptionOrNull()?.message ?: getvarRes.getOrNull()?.payload ?: "none"
        return Result.failure(IllegalStateException("Failed to retrieve token via 'oem get_token' ($oemErr) or 'getvar:token' ($getvarErr)"))
    }

    /**
     * Parses token strings from Fastboot response lines.
     * Xiaomi bootloaders often split the token across multiple 'INFOtoken: <part>' lines.
     */
    private fun parseTokenFromResponse(res: FastbootCmdResult): String {
        val parts = mutableListOf<String>()

        // Check info lines first (standard for Xiaomi OEM get_token)
        for (line in res.infoLines) {
            if (line.contains("token:", ignoreCase = true)) {
                val tokenPart = line.substringAfter("token:").trim()
                if (tokenPart.isNotEmpty()) {
                    parts.add(tokenPart)
                }
            } else if (line.isNotBlank() && !line.startsWith("OKAY") && !line.startsWith("FAIL")) {
                parts.add(line.trim())
            }
        }

        if (parts.isNotEmpty()) {
            return parts.joinToString("")
        }

        // If no info lines, check the payload
        if (res.payload.isNotEmpty()) {
            val tokenFromPayload = res.payload.substringAfter("token:").trim()
            if (tokenFromPayload.isNotEmpty()) {
                return tokenFromPayload
            }
        }

        return ""
    }

    /**
     * Stages the binary token payload into device memory before unlocking.
     * Sends 'stage:<hex_length>', waits for 'DATA<hex_length>', transfers the data, and checks final 'OKAY'.
     */
    fun stage(data: ByteArray): Result<Unit> {
        if (!transport.isConnected) {
            return Result.failure(IllegalStateException("Fastboot device is not connected"))
        }

        val hexLen = String.format(Locale.US, "%08x", data.size)
        val stageCmd = "stage:$hexLen"

        val res = transport.execute(stageCmd)
        if (res.isFailure) {
            return Result.failure(res.exceptionOrNull() ?: Exception("Stage command failed"))
        }

        val cmdRes = res.getOrThrow()
        if (cmdRes.status != "DATA") {
            return Result.failure(IllegalStateException("Expected DATA response from device during stage, got: ${cmdRes.status} (${cmdRes.payload})"))
        }

        // Send binary data
        val sendDataRes = transport.sendData(data)
        if (sendDataRes.isFailure) {
            return Result.failure(sendDataRes.exceptionOrNull() ?: Exception("Failed to transfer stage data"))
        }

        // Read final confirmation (should be OKAY)
        val confirmRes = transport.readResponse()
        if (confirmRes.isFailure) {
            return Result.failure(confirmRes.exceptionOrNull() ?: Exception("Failed reading post-stage confirmation"))
        }

        val confirm = confirmRes.getOrThrow()
        if (!confirm.isSuccess) {
            return Result.failure(IllegalStateException("Stage rejected by bootloader: ${confirm.payload} (status: ${confirm.status})"))
        }

        return Result.success(Unit)
    }

    /**
     * Executes 'oem unlock' on the bootloader.
     */
    fun oemUnlock(): Result<String> {
        if (!transport.isConnected) {
            return Result.failure(IllegalStateException("Fastboot device is not connected"))
        }

        val res = transport.execute("oem unlock")
        if (res.isFailure) {
            return Result.failure(res.exceptionOrNull() ?: Exception("Failed to send oem unlock"))
        }

        val cmdRes = res.getOrThrow()
        return if (cmdRes.isSuccess) {
            Result.success(cmdRes.payload.ifEmpty { "OKAY" })
        } else {
            Result.failure(IllegalStateException("Unlock failed: ${cmdRes.payload} (${cmdRes.status})"))
        }
    }

    /**
     * Reboots the device.
     */
    fun reboot(mode: String = ""): Result<Unit> {
        if (!transport.isConnected) {
            return Result.failure(IllegalStateException("Fastboot device is not connected"))
        }

        val cmd = if (mode.isEmpty()) "reboot" else "reboot-$mode"
        val res = transport.execute(cmd)
        return if (res.isSuccess && res.getOrThrow().isSuccess) {
            Result.success(Unit)
        } else {
            Result.failure(res.exceptionOrNull() ?: Exception("Reboot command failed"))
        }
    }
}
