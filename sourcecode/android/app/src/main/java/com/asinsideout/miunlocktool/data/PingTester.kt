package com.asinsideout.miunlocktool.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.InetSocketAddress
import java.net.Socket
import java.util.concurrent.TimeUnit

data class PingResult(
    val httpPingMs: Long,
    val tcpPingMs: Long,
    val averageMs: Long
)

class PingTester {

    private val client = OkHttpClient.Builder()
        .connectTimeout(1500, TimeUnit.MILLISECONDS)
        .readTimeout(1500, TimeUnit.MILLISECONDS)
        .build()

    private val httpHosts = listOf(
        "https://sgp-api.buy.mi.com",
        "https://api.buy.mi.com",
        "https://account.xiaomi.com"
    )

    private val tcpHosts = listOf(
        Pair("sgp-api.buy.mi.com", 443),
        Pair("api.buy.mi.com", 443),
        Pair("account.xiaomi.com", 443)
    )

    fun httpPing(url: String, timeoutMs: Int = 1500): Long? {
        return try {
            val request = Request.Builder()
                .url(url)
                .header("User-Agent", "Mozilla/5.0 (Linux; Android 14) XiaomiUnlockTool")
                .head()
                .build()
            val start = System.currentTimeMillis()
            client.newCall(request).execute().use { response ->
                val duration = System.currentTimeMillis() - start
                if (response.code < 500) duration else null
            }
        } catch (e: Exception) {
            null
        }
    }

    fun tcpPing(host: String, port: Int = 443, timeoutMs: Int = 1500): Long? {
        return try {
            val start = System.currentTimeMillis()
            Socket().use { socket ->
                socket.connect(InetSocketAddress(host, port), timeoutMs)
            }
            System.currentTimeMillis() - start
        } catch (e: Exception) {
            null
        }
    }

    suspend fun measurePings(durationSeconds: Int = 15): PingResult = withContext(Dispatchers.IO) {
        val httpPings = mutableListOf<Long>()
        val tcpPings = mutableListOf<Long>()
        val endTime = System.currentTimeMillis() + (durationSeconds * 1000L)

        while (System.currentTimeMillis() < endTime) {
            for (url in httpHosts) {
                httpPing(url)?.let { httpPings.add(it) }
            }
            for ((host, port) in tcpHosts) {
                tcpPing(host, port)?.let { tcpPings.add(it) }
            }
            delay(500)
        }

        val avgHttp = if (httpPings.isNotEmpty()) httpPings.average().toLong() else 165L
        val avgTcp = if (tcpPings.isNotEmpty()) tcpPings.average().toLong() else 165L
        val combined = ((avgHttp + avgTcp) / 2L)
        PingResult(httpPingMs = avgHttp, tcpPingMs = avgTcp, averageMs = combined)
    }

    suspend fun measureQuickPing(): PingResult = withContext(Dispatchers.IO) {
        val httpPings = mutableListOf<Long>()
        val tcpPings = mutableListOf<Long>()

        for (url in httpHosts) {
            httpPing(url)?.let { httpPings.add(it) }
        }
        for ((host, port) in tcpHosts) {
            tcpPing(host, port)?.let { tcpPings.add(it) }
        }

        val avgHttp = if (httpPings.isNotEmpty()) httpPings.average().toLong() else 165L
        val avgTcp = if (tcpPings.isNotEmpty()) tcpPings.average().toLong() else 165L
        val combined = if (httpPings.isNotEmpty() || tcpPings.isNotEmpty()) {
            ((avgHttp + avgTcp) / 2L)
        } else {
            -1L
        }
        PingResult(httpPingMs = avgHttp, tcpPingMs = avgTcp, averageMs = combined)
    }

    suspend fun measureAveragePingMs(count: Int = 1): Long {
        return measureQuickPing().averageMs
    }
}
