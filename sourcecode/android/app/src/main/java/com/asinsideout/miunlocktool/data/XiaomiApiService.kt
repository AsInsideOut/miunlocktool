package com.asinsideout.miunlocktool.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.security.MessageDigest
import java.util.Random
import java.util.concurrent.TimeUnit

class XiaomiApiService {

    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    companion object {
        private const val BASE_URL = "https://sgp-api.buy.mi.com"
        private const val STATUS_PATH = "/bbs/api/global/user/bl-switch/state"
        private const val APPLY_PATH = "/bbs/api/global/apply/bl-auth"
        private const val USER_AGENT = "okhttp/4.12.0"
        private const val VERSION_CODE = "500411"
        private const val VERSION_NAME = "5.4.11"
    }

    fun generateDeviceId(): String {
        val random = Random()
        val raw = "${random.nextDouble()}-${System.currentTimeMillis()}-${random.nextInt(1000000)}"
        val md = MessageDigest.getInstance("SHA-1")
        val digest = md.digest(raw.toByteArray(Charsets.UTF_8))
        return digest.joinToString("") { "%02X".format(it) }
    }

    suspend fun checkAccountStatus(token: String): CheckStatusResult = withContext(Dispatchers.IO) {
        val cleanToken = token.trim()
        if (cleanToken.isEmpty()) {
            return@withContext CheckStatusResult(AccountStatus.ERROR, "Token is empty")
        }

        val deviceId = generateDeviceId()
        val cookie = "new_bbs_serviceToken=$cleanToken;versionCode=$VERSION_CODE;versionName=$VERSION_NAME;deviceId=$deviceId;"

        try {
            val request = Request.Builder()
                .url("$BASE_URL$STATUS_PATH")
                .header("User-Agent", USER_AGENT)
                .header("Cookie", cookie)
                .header("Connection", "keep-alive")
                .get()
                .build()

            client.newCall(request).execute().use { response ->
                val body = response.body?.string() ?: ""
                if (!response.isSuccessful || body.isEmpty()) {
                    return@withContext CheckStatusResult(
                        AccountStatus.ERROR,
                        "Server returned HTTP ${response.code}"
                    )
                }

                val json = JSONObject(body)
                val code = json.optInt("code", -1)

                if (code == 100004 || code == 10004) {
                    return@withContext CheckStatusResult(
                        AccountStatus.EXPIRED,
                        "Token expired or invalid"
                    )
                }

                val data = json.optJSONObject("data") ?: JSONObject()
                val isPass = data.optInt("is_pass", -1)
                val buttonState = data.optInt("button_state", -1)
                val deadline = data.optString("deadline_format", "")

                when (isPass) {
                    4 -> {
                        when (buttonState) {
                            1 -> CheckStatusResult(
                                AccountStatus.READY,
                                "Account is ready to apply",
                                deadline
                            )
                            2 -> CheckStatusResult(
                                AccountStatus.BLOCKED,
                                "Account blocked until $deadline",
                                deadline
                            )
                            3 -> CheckStatusResult(
                                AccountStatus.TOO_NEW,
                                "Account too new (under 30 days)",
                                deadline
                            )
                            else -> CheckStatusResult(
                                AccountStatus.UNKNOWN,
                                "Unknown state (is_pass=4, button_state=$buttonState)"
                            )
                        }
                    }
                    1 -> CheckStatusResult(
                        AccountStatus.APPROVED,
                        "Account already approved until $deadline",
                        deadline
                    )
                    else -> CheckStatusResult(
                        AccountStatus.UNKNOWN,
                        "Unknown code=$code, is_pass=$isPass"
                    )
                }
            }
        } catch (e: Exception) {
            CheckStatusResult(AccountStatus.ERROR, "Error: ${e.message}")
        }
    }

    suspend fun applyUnlock(token: String, customDeviceId: String? = null): ApplyResult = withContext(Dispatchers.IO) {
        val cleanToken = token.trim()
        val deviceId = customDeviceId ?: generateDeviceId()
        val cookie = "new_bbs_serviceToken=$cleanToken;versionCode=$VERSION_CODE;versionName=$VERSION_NAME;deviceId=$deviceId;"
        val jsonMediaType = "application/json; charset=utf-8".toMediaType()
        val bodyContent = "{\"is_retry\":true}"
        val requestBody = bodyContent.toRequestBody(jsonMediaType)

        try {
            val request = Request.Builder()
                .url("$BASE_URL$APPLY_PATH")
                .header("User-Agent", USER_AGENT)
                .header("Cookie", cookie)
                .header("Connection", "keep-alive")
                .post(requestBody)
                .build()

            client.newCall(request).execute().use { response ->
                val body = response.body?.string() ?: ""
                if (!response.isSuccessful || body.isEmpty()) {
                    return@withContext ApplyResult(
                        code = response.code,
                        applyResult = null,
                        message = "HTTP error ${response.code}",
                        isSuccess = false
                    )
                }

                val json = JSONObject(body)
                val code = json.optInt("code", -1)
                val msg = json.optString("message", "")
                val data = json.optJSONObject("data")

                val applyResult = data?.optInt("apply_result")
                val deadline = data?.optString("deadline_format")

                val isSuccess = (code == 0 && applyResult == 1) || code == 100003

                ApplyResult(
                    code = code,
                    applyResult = applyResult,
                    message = msg,
                    isSuccess = isSuccess,
                    deadline = deadline
                )
            }
        } catch (e: Exception) {
            ApplyResult(
                code = -1,
                applyResult = null,
                message = "Request exception: ${e.message}",
                isSuccess = false
            )
        }
    }
}

