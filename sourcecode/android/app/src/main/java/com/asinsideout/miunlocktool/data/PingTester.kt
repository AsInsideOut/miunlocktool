package com.asinsideout.miunlocktool.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

class PingTester {

    private val client = OkHttpClient.Builder()
        .connectTimeout(3, TimeUnit.SECONDS)
        .readTimeout(5, TimeUnit.SECONDS)
        .build()

    private val pingHosts = listOf(
        "https://sgp-api.buy.mi.com",
        "https://api.buy.mi.com",
        "https://account.xiaomi.com"
    )

    suspend fun measureAveragePingMs(count: Int = 3): Long = withContext(Dispatchers.IO) {
        val latencies = mutableListOf<Long>()

        for (i in 0 until count) {
            for (host in pingHosts) {
                try {
                    val request = Request.Builder()
                        .url(host)
                        .header("User-Agent", "Mozilla/5.0 (Linux; Android 14)")
                        .head()
                        .build()

                    val start = System.currentTimeMillis()
                    client.newCall(request).execute().use { response ->
                        val duration = System.currentTimeMillis() - start
                        if (response.code < 500) {
                            latencies.add(duration)
                        }
                    }
                } catch (e: Exception) {
                    // Ignore transient errors
                }
            }
        }

        if (latencies.isNotEmpty()) {
            latencies.average().toLong()
        } else {
            -1L
        }
    }
}

