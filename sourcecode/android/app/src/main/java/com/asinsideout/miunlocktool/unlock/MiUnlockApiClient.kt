package com.asinsideout.miunlocktool.unlock

import android.util.Base64
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.HttpUrl
import okhttp3.HttpUrl.Companion.toHttpUrlOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.nio.charset.StandardCharsets
import java.security.SecureRandom
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.TimeUnit

data class DeviceClearResult(
    val code: Int,
    val cleanOrNot: Int,
    val notice: String
)

data class AhaUnlockResult(
    val code: Int,
    val isSuccess: Boolean,
    val encryptData: String? = null,
    val description: String? = null,
    val rawJson: JSONObject? = null
)

class MiUnlockApiClient(
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
) {

    companion object {
        const val USER_AGENT = "XiaomiPCSuite"
        const val REGION_URL = "https://account.xiaomi.com/pass/user/login/region"

        val DOMAINS = mapOf(
            "Singapore" to "https://unlock.update.intl.miui.com",
            "China" to "https://unlock.update.miui.com",
            "India" to "https://in-unlock.update.intl.miui.com",
            "Russia" to "https://ru-unlock.update.intl.miui.com",
            "Europe" to "https://eu-unlock.update.intl.miui.com"
        )

        private val EUROPE_REGIONS = setOf(
            "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "EL",
            "HU", "IS", "IE", "IT", "LV", "LI", "LT", "LU", "MT", "NL", "NO", "PL",
            "PT", "RO", "SK", "SI", "ES", "SE", "UK", "GB"
        )
    }

    private val random = SecureRandom()

    fun getDomainForZone(zone: String): String {
        return DOMAINS[zone] ?: DOMAINS["Singapore"]!!
    }

    fun mapRegionToZone(region: String?): String {
        val reg = region?.trim()?.uppercase() ?: return "Singapore"
        return when {
            reg == "CN" -> "China"
            reg == "IN" -> "India"
            reg == "RU" -> "Russia"
            EUROPE_REGIONS.contains(reg) -> "Europe"
            else -> "Singapore"
        }
    }

    private fun generateRandomString(length: Int = 16): String {
        val chars = "abcdefghijklmnopqrstuvwxyz"
        val sb = StringBuilder(length)
        for (i in 0 until length) {
            sb.append(chars[random.nextInt(chars.length)])
        }
        return sb.toString()
    }

    private suspend fun sendSignedPost(
        domain: String,
        path: String,
        rawParams: MutableMap<String, String>,
        ssecurity: String,
        cookies: Map<String, String>
    ): Result<JSONObject> = withContext(Dispatchers.IO) {
        try {
            val urlString = "$domain$path"
            val httpUrlBuilder = urlString.toHttpUrlOrNull()?.newBuilder()
                ?: return@withContext Result.failure(IllegalArgumentException("Invalid URL: $urlString"))

            // Base64-encode 'data' if present, exactly as in MiUnlockTool utils.py
            if (rawParams.containsKey("data")) {
                val dataVal = rawParams["data"] ?: ""
                val b64Data = Base64.encodeToString(dataVal.toByteArray(StandardCharsets.UTF_8), Base64.NO_WRAP)
                rawParams["data"] = b64Data
            }

            val postParams = MiUnlockCrypto.prepareEncryptedParams(path, rawParams, ssecurity)

            // Add query parameters
            for ((k, v) in postParams) {
                httpUrlBuilder.addQueryParameter(k, v)
            }

            val cookieHeader = cookies.entries.joinToString("; ") { "${it.key}=${it.value}" }

            val reqBuilder = Request.Builder()
                .url(httpUrlBuilder.build())
                .post(ByteArray(0).toRequestBody(null, 0, 0)) // empty POST body with query params
                .header("User-Agent", USER_AGENT)

            if (cookieHeader.isNotEmpty()) {
                reqBuilder.header("Cookie", cookieHeader)
            }

            val response = client.newCall(reqBuilder.build()).execute()
            if (!response.isSuccessful) {
                return@withContext Result.failure(IllegalStateException("HTTP ${response.code}: ${response.message}"))
            }

            val body = response.body?.string() ?: return@withContext Result.failure(IllegalStateException("Empty response from server"))
            MiUnlockCrypto.decryptApiResponse(body, ssecurity)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getNonce(
        domain: String,
        ssecurity: String,
        cookies: Map<String, String>
    ): Result<String> = withContext(Dispatchers.IO) {
        val r = generateRandomString(16)
        val params = mutableMapOf("r" to r)
        val res = sendSignedPost(domain, "/api/v2/nonce", params, ssecurity, cookies)
        if (res.isFailure) {
            return@withContext Result.failure(res.exceptionOrNull() ?: Exception("Failed to get nonce"))
        }

        val json = res.getOrThrow()
        val code = json.optInt("code", -1)
        if (code != 0) {
            val desc = json.optString("descEN", json.optString("description", "Code $code"))
            return@withContext Result.failure(IllegalStateException("Nonce retrieval error: $desc (code $code)"))
        }

        val nonce = json.optString("nonce")
        if (nonce.isEmpty()) {
            return@withContext Result.failure(IllegalStateException("Server returned empty nonce"))
        }

        Result.success(nonce)
    }

    suspend fun checkDeviceClear(
        domain: String,
        product: String,
        nonce: String,
        ssecurity: String,
        cookies: Map<String, String>
    ): Result<DeviceClearResult> = withContext(Dispatchers.IO) {
        val dataJson = JSONObject().apply {
            put("product", product)
        }
        val params = mutableMapOf(
            "appId" to "1",
            "data" to dataJson.toString(),
            "nonce" to nonce
        )

        val res = sendSignedPost(domain, "/api/v2/unlock/device/clear", params, ssecurity, cookies)
        if (res.isFailure) {
            return@withContext Result.failure(res.exceptionOrNull() ?: Exception("Device clear check failed"))
        }

        val json = res.getOrThrow()
        val code = json.optInt("code", -1)
        val cleanOrNot = json.optInt("cleanOrNot", 0)
        val notice = json.optString("notice", "")

        Result.success(DeviceClearResult(code = code, cleanOrNot = cleanOrNot, notice = notice))
    }

    suspend fun applyAhaUnlock(
        domain: String,
        product: String,
        deviceToken: String,
        nonce: String,
        ssecurity: String,
        deviceId: String,
        userId: String,
        cookies: Map<String, String>
    ): Result<AhaUnlockResult> = withContext(Dispatchers.IO) {
        val pcId = MiUnlockCrypto.md5Hex(deviceId)

        val deviceInfo = JSONObject().apply {
            put("boardVersion", "")
            put("deviceName", "")
            put("product", product)
            put("socId", "")
        }

        val dataJson = JSONObject().apply {
            put("clientId", "2")
            put("clientVersion", "7.6.727.43")
            put("deviceInfo", deviceInfo)
            put("deviceToken", deviceToken)
            put("language", "en")
            put("operate", "unlock")
            put("pcId", pcId)
            put("region", "")
            put("uid", userId)
        }

        val params = mutableMapOf(
            "appId" to "1",
            "data" to dataJson.toString(),
            "nonce" to nonce
        )

        val res = sendSignedPost(domain, "/api/v3/ahaUnlock", params, ssecurity, cookies)
        if (res.isFailure) {
            return@withContext Result.failure(res.exceptionOrNull() ?: Exception("AhaUnlock request failed"))
        }

        val json = res.getOrThrow()
        val code = json.optInt("code", -1)
        val desc = json.optString("descEN", json.optString("description", "Code $code"))

        if (code == 0) {
            val encryptData = json.optString("encryptData")
            if (encryptData.isNotEmpty()) {
                Result.success(
                    AhaUnlockResult(
                        code = 0,
                        isSuccess = true,
                        encryptData = encryptData,
                        description = "Success",
                        rawJson = json
                    )
                )
            } else {
                Result.failure(IllegalStateException("Server returned code 0 but encryptData is missing"))
            }
        } else {
            Result.success(
                AhaUnlockResult(
                    code = code,
                    isSuccess = false,
                    description = desc,
                    rawJson = json
                )
            )
        }
    }
}
