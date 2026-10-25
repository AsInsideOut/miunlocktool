package com.asinsideout.miunlocktool.unlock

import com.asinsideout.miunlocktool.fastboot.FastbootManager

sealed class UnlockStageResult {
    data class DeviceInfoRead(val product: String, val token: String) : UnlockStageResult()
    data class ClearCheck(val cleanOrNot: Int, val notice: String) : UnlockStageResult()
    data class TokenObtained(val encryptDataHex: String) : UnlockStageResult()
    data class UnlockCompleted(val message: String) : UnlockStageResult()
    data class Failed(val stage: String, val error: String, val code: Int? = null) : UnlockStageResult()
}

class MiUnlockWorkflow(
    val fastbootManager: FastbootManager,
    val apiClient: MiUnlockApiClient = MiUnlockApiClient()
) {

    /**
     * Reads device product and token from the connected Fastboot device.
     */
    fun readDeviceInfo(): Result<Pair<String, String>> {
        val prodRes = fastbootManager.getProduct()
        if (prodRes.isFailure) {
            return Result.failure(prodRes.exceptionOrNull() ?: Exception("Failed to read product name"))
        }

        val tokenRes = fastbootManager.getToken()
        if (tokenRes.isFailure) {
            return Result.failure(tokenRes.exceptionOrNull() ?: Exception("Failed to read token"))
        }

        return Result.success(Pair(prodRes.getOrThrow(), tokenRes.getOrThrow()))
    }

    /**
     * Retrieves server nonce, checks clear warning, and requests encryptData token from Xiaomi.
     */
    suspend fun obtainServerUnlockToken(
        zone: String,
        product: String,
        deviceToken: String,
        ssecurity: String,
        deviceId: String,
        userId: String,
        cookies: Map<String, String>,
        onClearWarning: ((cleanOrNot: Int, notice: String) -> Unit)? = null
    ): Result<String> {
        val domain = apiClient.getDomainForZone(zone)

        // 1. Get Nonce
        val nonceRes = apiClient.getNonce(domain, ssecurity, cookies)
        if (nonceRes.isFailure) {
            return Result.failure(nonceRes.exceptionOrNull() ?: Exception("Failed to get server nonce"))
        }
        val nonce = nonceRes.getOrThrow()

        // 2. Check Device Clear
        val clearRes = apiClient.checkDeviceClear(domain, product, nonce, ssecurity, cookies)
        if (clearRes.isSuccess) {
            val clear = clearRes.getOrThrow()
            onClearWarning?.invoke(clear.cleanOrNot, clear.notice)
        }

        // 3. Request ahaUnlock token
        val unlockRes = apiClient.applyAhaUnlock(
            domain = domain,
            product = product,
            deviceToken = deviceToken,
            nonce = nonce,
            ssecurity = ssecurity,
            deviceId = deviceId,
            userId = userId,
            cookies = cookies
        )

        if (unlockRes.isFailure) {
            return Result.failure(unlockRes.exceptionOrNull() ?: Exception("Unlock request error"))
        }

        val result = unlockRes.getOrThrow()
        if (!result.isSuccess || result.encryptData.isNullOrEmpty()) {
            return Result.failure(IllegalStateException(result.description ?: "Server refused unlock (code ${result.code})"))
        }

        return Result.success(result.encryptData)
    }

    /**
     * Performs the actual Fastboot stage & OEM unlock.
     * WARNING: This operation performs bootloader unlocking on the device!
     */
    fun performFastbootUnlock(encryptDataHex: String): Result<String> {
        val rawData = MiUnlockCrypto.hexToBytes(encryptDataHex)

        val stageRes = fastbootManager.stage(rawData)
        if (stageRes.isFailure) {
            return Result.failure(stageRes.exceptionOrNull() ?: Exception("Failed staging token to device"))
        }

        val unlockRes = fastbootManager.oemUnlock()
        if (unlockRes.isFailure) {
            return Result.failure(unlockRes.exceptionOrNull() ?: Exception("oem unlock command failed"))
        }

        return Result.success(unlockRes.getOrThrow())
    }
}
