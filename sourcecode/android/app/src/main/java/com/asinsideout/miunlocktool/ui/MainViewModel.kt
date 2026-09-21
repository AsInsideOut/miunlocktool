package com.asinsideout.miunlocktool.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.asinsideout.miunlocktool.data.ExecutionMode
import com.asinsideout.miunlocktool.data.LogColorType
import com.asinsideout.miunlocktool.data.LogEntry
import com.asinsideout.miunlocktool.data.PingTester
import com.asinsideout.miunlocktool.data.PreferencesManager
import com.asinsideout.miunlocktool.data.SntpClient
import com.asinsideout.miunlocktool.data.XiaomiApiService
import com.asinsideout.miunlocktool.service.ApplyScheduler
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

sealed class UpdateResult {
    object Idle : UpdateResult()
    object Checking : UpdateResult()
    data class UpdateAvailable(val remoteVersion: String, val currentVersion: String, val url: String) : UpdateResult()
    data class UpToDate(val version: String) : UpdateResult()
    data class Error(val message: String) : UpdateResult()
}

class MainViewModel(application: Application) : AndroidViewModel(application) {

    val prefs = PreferencesManager(application)
    val apiService = XiaomiApiService()
    val sntpClient = SntpClient()
    val pingTester = PingTester()

    val scheduler = ApplyScheduler(prefs, apiService, sntpClient, pingTester, viewModelScope)

    private val _logs = MutableStateFlow<List<LogEntry>>(emptyList())
    val logs: StateFlow<List<LogEntry>> = _logs.asStateFlow()

    private val _updateState = MutableStateFlow<UpdateResult>(UpdateResult.Idle)
    val updateState: StateFlow<UpdateResult> = _updateState.asStateFlow()

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(8, TimeUnit.SECONDS)
        .build()

    val currentVersion = "8.0"
    val updateUrl = "https://miunlock.su"
    private val versionCheckUrl = "https://miunlock.su/version.txt"

    init {
        viewModelScope.launch {
            scheduler.logFlow.collect { entry ->
                val current = _logs.value.toMutableList()
                current.add(entry)
                if (current.size > 500) {
                    current.removeAt(0)
                }
                _logs.value = current
            }
        }
    }

    fun clearLogs() {
        _logs.value = emptyList()
    }

    fun addLog(message: String, color: LogColorType = LogColorType.DEFAULT) {
        scheduler.log(message, color)
    }

    fun startScheduler(mode: ExecutionMode) {
        scheduler.start(mode)
    }

    fun stopScheduler() {
        scheduler.stop()
    }

    fun syncNtp() {
        scheduler.syncNtp()
    }

    fun measurePing() {
        scheduler.measurePing()
    }

    fun resetUpdateState() {
        _updateState.value = UpdateResult.Idle
    }

    fun checkForUpdates() {
        viewModelScope.launch {
            _updateState.value = UpdateResult.Checking
            val result = withContext(Dispatchers.IO) {
                try {
                    val request = Request.Builder()
                        .url(versionCheckUrl)
                        .header("User-Agent", "okhttp/4.12.0")
                        .get()
                        .build()

                    httpClient.newCall(request).execute().use { response ->
                        if (!response.isSuccessful) {
                            return@withContext UpdateResult.Error("HTTP error: ${response.code}")
                        }
                        val rawBody = response.body?.string()?.trim() ?: ""
                        if (rawBody.isEmpty()) {
                            return@withContext UpdateResult.Error("Empty response from server")
                        }

                        // Extract version from raw body (e.g. "8.1" or "7.3")
                        val cleanVersion = rawBody.lines().firstOrNull()?.trim() ?: rawBody
                        if (isNewerVersion(cleanVersion, currentVersion)) {
                            UpdateResult.UpdateAvailable(cleanVersion, currentVersion, updateUrl)
                        } else {
                            UpdateResult.UpToDate(currentVersion)
                        }
                    }
                } catch (e: Exception) {
                    UpdateResult.Error(e.localizedMessage ?: e.message ?: "Unknown error")
                }
            }
            _updateState.value = result
        }
    }

    private fun isNewerVersion(remote: String, current: String): Boolean {
        try {
            val remoteClean = remote.replace(Regex("[^0-9.]"), "")
            val currentClean = current.replace(Regex("[^0-9.]"), "")

            val remoteParts = remoteClean.split(".").mapNotNull { it.toIntOrNull() }
            val currentParts = currentClean.split(".").mapNotNull { it.toIntOrNull() }

            val maxLen = maxOf(remoteParts.size, currentParts.size)
            for (i in 0 until maxLen) {
                val r = remoteParts.getOrElse(i) { 0 }
                val c = currentParts.getOrElse(i) { 0 }
                if (r > c) return true
                if (r < c) return false
            }
            return false
        } catch (e: Exception) {
            return false
        }
    }
}

