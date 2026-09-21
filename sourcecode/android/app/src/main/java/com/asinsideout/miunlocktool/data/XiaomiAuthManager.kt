package com.asinsideout.miunlocktool.data

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.util.Base64
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.Cookie
import okhttp3.CookieJar
import okhttp3.HttpUrl
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.net.URLEncoder
import java.security.MessageDigest
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.TimeUnit

data class AuthSessionInfo(
    val loginUrl: String,
    val lpUrl: String,
    val qrUrl: String,
    val timeoutSeconds: Int
)

sealed class AuthPollResult {
    data class Success(val token: String) : AuthPollResult()
    data class Status(val message: String) : AuthPollResult()
    data class Error(val message: String) : AuthPollResult()
    object Expired : AuthPollResult()
}

class InMemoryCookieJar : CookieJar {
    private val cookieStore = ConcurrentHashMap<String, MutableList<Cookie>>()

    override fun saveFromResponse(url: HttpUrl, cookies: List<Cookie>) {
        val existing = cookieStore.getOrPut(url.host) { mutableListOf() }
        synchronized(existing) {
            cookies.forEach { newCookie ->
                existing.removeAll { it.name == newCookie.name }
                existing.add(newCookie)
            }
        }
    }

    override fun loadForRequest(url: HttpUrl): List<Cookie> {
        val list = mutableListOf<Cookie>()
        cookieStore.forEach { (_, cookies) ->
            synchronized(cookies) {
                list.addAll(cookies)
            }
        }
        return list
    }

    fun getCookieValue(name: String): String? {
        cookieStore.values.forEach { list ->
            synchronized(list) {
                list.find { it.name == name }?.let { return it.value }
            }
        }
        return null
    }

    fun clear() {
        cookieStore.clear()
    }
}

class XiaomiAuthManager {

    companion object {
        const val LONGPOLLING_URL = "https://account.xiaomi.com/longPolling/loginUrl"
        const val SERVICELOGIN_URL = "https://account.xiaomi.com/pass/serviceLogin"
        const val SID = "18n_bbs_global"
        const val CALLBACK_URL = "https://sgp-api.buy.mi.com/bbs/api/global/user/login-back"
        const val USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    private val cookieJar = InMemoryCookieJar()

    private val client = OkHttpClient.Builder()
        .cookieJar(cookieJar)
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(45, TimeUnit.SECONDS)
        .followRedirects(true)
        .followSslRedirects(true)
        .build()

    suspend fun initiateAuth(): Result<AuthSessionInfo> = withContext(Dispatchers.IO) {
        try {
            cookieJar.clear()
            val url = "$LONGPOLLING_URL?sid=$SID&_json=false&callback=${URLEncoder.encode(CALLBACK_URL, "UTF-8")}"
            val request = Request.Builder()
                .url(url)
                .header("User-Agent", USER_AGENT)
                .header("Accept", "application/json;charset=UTF-8")
                .build()

            val response = client.newCall(request).execute()
            var body = response.body?.string() ?: return@withContext Result.failure(Exception("Empty response"))
            if (body.startsWith("&&&START&&&")) {
                body = body.removePrefix("&&&START&&&")
            }

            val json = JSONObject(body)
            val loginUrl = json.optString("loginUrl")
            val lpUrl = json.optString("lp")
            val qrUrl = json.optString("qr")
            val timeout = json.optInt("timeout", 300)

            if (loginUrl.isEmpty() || lpUrl.isEmpty()) {
                return@withContext Result.failure(Exception("Missing login or polling URL"))
            }

            Result.success(AuthSessionInfo(loginUrl, lpUrl, qrUrl, timeout))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun fetchQrBitmap(qrUrl: String): Bitmap? = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url(qrUrl)
                .header("User-Agent", USER_AGENT)
                .build()
            val response = client.newCall(request).execute()
            val bytes = response.body?.bytes() ?: return@withContext null
            BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
        } catch (e: Exception) {
            null
        }
    }

    suspend fun pollOnce(lpUrl: String): AuthPollResult = withContext(Dispatchers.IO) {
        try {
            val request = Request.Builder()
                .url(lpUrl)
                .header("User-Agent", USER_AGENT)
                .build()

            val response = client.newCall(request).execute()
            if (!response.isSuccessful) {
                return@withContext AuthPollResult.Status("HTTP ${response.code}")
            }

            var body = response.body?.string() ?: return@withContext AuthPollResult.Status("Empty poll response")
            if (body.startsWith("&&&START&&&")) {
                body = body.removePrefix("&&&START&&&")
            }

            val json = JSONObject(body)
            val code = json.optInt("code", -1)

            when (code) {
                0 -> {
                    // Success! Complete handshake
                    val token = finalizeAuth(json)
                    if (token != null) {
                        AuthPollResult.Success(token)
                    } else {
                        AuthPollResult.Error("Failed to extract new_bbs_serviceToken")
                    }
                }
                70016, 87001 -> {
                    val desc = json.optString("description", "Waiting for confirmation")
                    AuthPollResult.Status(desc)
                }
                else -> {
                    val desc = json.optString("description", "Code $code")
                    AuthPollResult.Status(desc)
                }
            }
        } catch (e: java.net.SocketTimeoutException) {
            AuthPollResult.Status("Polling...")
        } catch (e: Exception) {
            AuthPollResult.Error(e.localizedMessage ?: "Network error during polling")
        }
    }

    private fun finalizeAuth(authData: JSONObject): String? {
        try {
            val nonce = authData.optString("nonce")
            val ssecurity = authData.optString("ssecurity")
            val location = authData.optString("location")

            if (location.isNotEmpty() && nonce.isNotEmpty() && ssecurity.isNotEmpty()) {
                val toHash = "nonce=$nonce&$ssecurity".toByteArray(Charsets.UTF_8)
                val sha1 = MessageDigest.getInstance("SHA-1").digest(toHash)
                val base64 = Base64.encodeToString(sha1, Base64.NO_WRAP)
                val clientSign = URLEncoder.encode(base64, "UTF-8")
                val finalUrl = "$location&clientSign=$clientSign"

                val req = Request.Builder()
                    .url(finalUrl)
                    .header("User-Agent", USER_AGENT)
                    .build()
                client.newCall(req).execute()
            } else {
                val serviceLoginUrl = "$SERVICELOGIN_URL?sid=$SID&_json=true"
                val req = Request.Builder()
                    .url(serviceLoginUrl)
                    .header("User-Agent", USER_AGENT)
                    .build()
                val resp = client.newCall(req).execute()
                var text = resp.body?.string() ?: ""
                if (text.startsWith("&&&START&&&")) {
                    text = text.removePrefix("&&&START&&&")
                }
                val resJson = JSONObject(text)
                val fNonce = resJson.optString("nonce")
                val fSsecurity = resJson.optString("ssecurity")
                val fLocation = resJson.optString("location")

                if (fNonce.isNotEmpty() && fSsecurity.isNotEmpty() && fLocation.isNotEmpty()) {
                    val toHash = "nonce=$fNonce&$fSsecurity".toByteArray(Charsets.UTF_8)
                    val sha1 = MessageDigest.getInstance("SHA-1").digest(toHash)
                    val base64 = Base64.encodeToString(sha1, Base64.NO_WRAP)
                    val clientSign = URLEncoder.encode(base64, "UTF-8")
                    val finalUrl = "$fLocation&clientSign=$clientSign"

                    val finalReq = Request.Builder()
                        .url(finalUrl)
                        .header("User-Agent", USER_AGENT)
                        .build()
                    client.newCall(finalReq).execute()
                }
            }

            return cookieJar.getCookieValue("new_bbs_serviceToken")
                ?: cookieJar.getCookieValue("serviceToken")
        } catch (e: Exception) {
            return null
        }
    }
}

