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
        private val JSON_MEDIA_TYPE = "application/json; charset=utf-8".toMediaType()
        private val STATIC_POST_BODY = "{\"is_retry\":true}".toRequestBody(JSON_MEDIA_TYPE)
    }

    data class ParsedApiResponse(
        val raw: String,
        val jsonObject: JSONObject?,
        val isStringResponse: Boolean,
        val stringValue: String?,
        val code: Int?,
        val message: String?,
        val applyResult: Int?,
        val deadline: String?,
        val isPass: Int?,
        val buttonState: Int?
    )

    fun parseApiResponse(rawBody: String): ParsedApiResponse {
        val clean = rawBody.trim().trim('\uFEFF')
        if (clean.isEmpty()) {
            return ParsedApiResponse(
                raw = clean,
                jsonObject = null,
                isStringResponse = false,
                stringValue = null,
                code = null,
                message = "Empty response",
                applyResult = null,
                deadline = null,
                isPass = null,
                buttonState = null
            )
        }

        var targetJson: JSONObject? = null
        var extractedString: String? = null
        var isString = false

        // 1. Direct JSONObject check
        if (clean.startsWith("{") && clean.endsWith("}")) {
            try {
                targetJson = JSONObject(clean)
            } catch (_: Exception) {
                // Not standard JSON, proceed with tokener
            }
        }

        // 2. Tokenize with JSONTokener if not parsed
        if (targetJson == null) {
            try {
                val tokener = org.json.JSONTokener(clean)
                val root = tokener.nextValue()
                if (root is JSONObject) {
                    targetJson = root
                } else if (root is String) {
                    isString = true
                    val trimmed = root.trim()
                    extractedString = trimmed
                    var candidate = trimmed
                    // Strip enclosing quotes if string was double-encoded
                    for (i in 0..2) {
                        if (candidate.startsWith("\"") && candidate.endsWith("\"") && candidate.length >= 2) {
                            candidate = candidate.substring(1, candidate.length - 1).trim()
                        } else {
                            break
                        }
                    }
                    if (candidate.startsWith("{") && candidate.endsWith("}")) {
                        try {
                            targetJson = JSONObject(candidate)
                        } catch (_: Exception) {
                            // Keep candidate as string
                        }
                    }
                } else if (root is Number) {
                    val num = root.toInt()
                    return ParsedApiResponse(
                        raw = clean,
                        jsonObject = null,
                        isStringResponse = true,
                        stringValue = num.toString(),
                        code = num,
                        message = null,
                        applyResult = null,
                        deadline = null,
                        isPass = null,
                        buttonState = null
                    )
                }
            } catch (_: Exception) {
                isString = true
                extractedString = clean
            }
        }

        // 3. If JSONObject was found, extract fields
        if (targetJson != null) {
            val code = if (targetJson.has("code")) targetJson.optInt("code", -1) else null
            val message = targetJson.optString("message", targetJson.optString("msg", ""))
            val dataObj = targetJson.optJSONObject("data")
            val applyResult = if (dataObj != null && dataObj.has("apply_result")) {
                dataObj.optInt("apply_result")
            } else if (targetJson.has("apply_result")) {
                targetJson.optInt("apply_result")
            } else null

            val deadline = dataObj?.optString("deadline_format", "")?.takeIf { it.isNotEmpty() }
                ?: targetJson.optString("deadline_format", "").takeIf { it.isNotEmpty() }
            val isPass = dataObj?.optInt("is_pass", -1)?.takeIf { it != -1 }
                ?: targetJson.optInt("is_pass", -1).takeIf { it != -1 }
            val buttonState = dataObj?.optInt("button_state", -1)?.takeIf { it != -1 }
                ?: targetJson.optInt("button_state", -1).takeIf { it != -1 }

            return ParsedApiResponse(
                raw = clean,
                jsonObject = targetJson,
                isStringResponse = isString,
                stringValue = extractedString,
                code = code,
                message = message,
                applyResult = applyResult,
                deadline = deadline,
                isPass = isPass,
                buttonState = buttonState
            )
        }

        // 4. Handle String response (plain text, JSON string, or keyword)
        val str = extractedString ?: clean

        val intCode = str.toIntOrNull()
        if (intCode != null) {
            return ParsedApiResponse(
                raw = clean,
                jsonObject = null,
                isStringResponse = true,
                stringValue = str,
                code = intCode,
                message = str,
                applyResult = if (intCode == 0) 1 else null,
                deadline = null,
                isPass = null,
                buttonState = null
            )
        }

        // Regex fallbacks for partially formatted / embedded responses
        val codeRegex = Regex("""["']?code["']?\s*[:=]\s*(\d+)""")
        val matchCode = codeRegex.find(str)?.groupValues?.get(1)?.toIntOrNull()

        val applyResultRegex = Regex("""["']?apply_result["']?\s*[:=]\s*(\d+)""")
        val matchApplyResult = applyResultRegex.find(str)?.groupValues?.get(1)?.toIntOrNull()

        val isPassRegex = Regex("""["']?is_pass["']?\s*[:=]\s*(\d+)""")
        val matchIsPass = isPassRegex.find(str)?.groupValues?.get(1)?.toIntOrNull()

        val buttonStateRegex = Regex("""["']?button_state["']?\s*[:=]\s*(\d+)""")
        val matchButtonState = buttonStateRegex.find(str)?.groupValues?.get(1)?.toIntOrNull()

        val deadlineRegex = Regex("""["']?deadline_format["']?\s*[:=]\s*["']([^"']+)["']""")
        val matchDeadline = deadlineRegex.find(str)?.groupValues?.get(1)

        val lower = str.lowercase(java.util.Locale.ROOT)
        val inferredCode = when {
            matchCode != null -> matchCode
            lower.contains("success") || lower.contains("ok") || lower.contains("approved") -> 0
            lower.contains("100003") -> 100003
            lower.contains("100004") || (lower.contains("token") && lower.contains("expired")) -> 100004
            else -> null
        }

        return ParsedApiResponse(
            raw = clean,
            jsonObject = null,
            isStringResponse = true,
            stringValue = str,
            code = inferredCode,
            message = str,
            applyResult = matchApplyResult ?: (if (inferredCode == 0) 1 else null),
            deadline = matchDeadline,
            isPass = matchIsPass,
            buttonState = matchButtonState
        )
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

                val parsed = parseApiResponse(body)
                val code = parsed.code

                if (code == 100004 || code == 10004) {
                    return@withContext CheckStatusResult(
                        AccountStatus.EXPIRED,
                        "Token expired or invalid"
                    )
                }

                val isPass = parsed.isPass
                val buttonState = parsed.buttonState
                val deadline = parsed.deadline ?: ""

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
                    else -> {
                        if (code == 0 && (parsed.stringValue?.contains("approved", ignoreCase = true) == true ||
                                parsed.stringValue?.contains("success", ignoreCase = true) == true)) {
                            CheckStatusResult(
                                AccountStatus.APPROVED,
                                "Account already approved until $deadline",
                                deadline
                            )
                        } else {
                            CheckStatusResult(
                                AccountStatus.UNKNOWN,
                                parsed.stringValue?.take(100) ?: "Unknown response code=${code ?: -1}"
                            )
                        }
                    }
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
        try {
            val request = Request.Builder()
                .url("$BASE_URL$APPLY_PATH")
                .header("User-Agent", USER_AGENT)
                .header("Cookie", cookie)
                .header("Connection", "keep-alive")
                .post(STATIC_POST_BODY)
                .build()

            client.newCall(request).execute().use { response ->
                val body = response.body?.string() ?: ""
                if (!response.isSuccessful) {
                    return@withContext ApplyResult(
                        code = response.code,
                        applyResult = null,
                        message = "HTTP error ${response.code}",
                        isSuccess = false,
                        isSent = false,
                        isStatusUnavailable = false,
                        rawResponse = body
                    )
                }

                // HTTP request was received and processed by the server successfully
                if (body.isEmpty()) {
                    return@withContext ApplyResult(
                        code = 0,
                        applyResult = null,
                        message = "Empty response body",
                        isSuccess = false,
                        isSent = true,
                        isStatusUnavailable = true,
                        rawResponse = ""
                    )
                }

                val parsed = parseApiResponse(body)
                val code = parsed.code
                val applyResult = parsed.applyResult
                val deadline = parsed.deadline
                val msg = parsed.message ?: ""

                if (code == null) {
                    // Response could not be parsed to a definitive code, but application was sent!
                    return@withContext ApplyResult(
                        code = -1,
                        applyResult = null,
                        message = msg.ifEmpty { "Status response format unrecognized" },
                        isSuccess = false,
                        isSent = true,
                        isStatusUnavailable = true,
                        rawResponse = body
                    )
                }

                val isSuccess = (code == 0 && applyResult == 1) || code == 100003

                ApplyResult(
                    code = code,
                    applyResult = applyResult,
                    message = msg,
                    isSuccess = isSuccess,
                    deadline = deadline,
                    isSent = true,
                    isStatusUnavailable = false,
                    rawResponse = body
                )
            }
        } catch (e: Exception) {
            // Exception in sending the HTTP request (network down, socket timeout, etc.)
            ApplyResult(
                code = -1,
                applyResult = null,
                message = "Request error: ${e.message}",
                isSuccess = false,
                isSent = false,
                isStatusUnavailable = false,
                rawResponse = null
            )
        }
    }
}

