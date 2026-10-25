package com.asinsideout.miunlocktool.ui

import android.app.Application
import android.content.Context
import android.os.Environment
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
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.TimeUnit
import java.util.Locale
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import com.asinsideout.miunlocktool.fastboot.FastbootConnectionState
import com.asinsideout.miunlocktool.fastboot.FastbootManager
import com.asinsideout.miunlocktool.fastboot.FastbootUsbTransport
import com.asinsideout.miunlocktool.unlock.MiUnlockWorkflow

sealed class UpdateResult {
    object Idle : UpdateResult()
    object Checking : UpdateResult()
    data class UpdateAvailable(val remoteVersion: String, val currentVersion: String, val url: String) : UpdateResult()
    data class UpToDate(val version: String) : UpdateResult()
    data class Error(val message: String) : UpdateResult()
}

sealed class DownloadState {
    object Idle : DownloadState()
    data class Progress(val percent: Int, val bytesDownloaded: Long, val totalBytes: Long) : DownloadState()
    data class Success(val apkFile: File) : DownloadState()
    data class Error(val message: String) : DownloadState()
}

class MainViewModel(application: Application) : AndroidViewModel(application) {

    val prefs = PreferencesManager(application)
    val apiService = XiaomiApiService()
    val sntpClient = SntpClient()
    val pingTester = PingTester()
    val notificationManager = com.asinsideout.miunlocktool.service.LiveNotificationManager(application, prefs)

    val scheduler = ApplyScheduler(
        prefs,
        apiService,
        sntpClient,
        pingTester,
        viewModelScope,
        notificationManager,
        application
    )

    private val _logs = MutableStateFlow<List<LogEntry>>(emptyList())
    val logs: StateFlow<List<LogEntry>> = _logs.asStateFlow()

    private val _updateState = MutableStateFlow<UpdateResult>(UpdateResult.Idle)
    val updateState: StateFlow<UpdateResult> = _updateState.asStateFlow()

    private val _downloadState = MutableStateFlow<DownloadState>(DownloadState.Idle)
    val downloadState: StateFlow<DownloadState> = _downloadState.asStateFlow()

    private val _accentColor = MutableStateFlow(prefs.accentColor)
    val accentColor: StateFlow<Int> = _accentColor.asStateFlow()

    fun setAccentColor(color: Int, hex: String) {
        prefs.accentColor = color
        prefs.accentColorHex = hex
        _accentColor.value = color
    }


    // Fastboot USB Layer
    private val usbManager = application.getSystemService(Context.USB_SERVICE) as UsbManager
    val fastbootTransport = FastbootUsbTransport(usbManager)
    val fastbootManager = FastbootManager(fastbootTransport)
    val miUnlockWorkflow = MiUnlockWorkflow(fastbootManager)

    private val _fastbootDeviceState = MutableStateFlow(FastbootConnectionState.NO_DEVICE)
    val fastbootDeviceState: StateFlow<FastbootConnectionState> = _fastbootDeviceState.asStateFlow()

    private val _fastbootDeviceInfoText = MutableStateFlow("USB device not found")
    val fastbootDeviceInfoText: StateFlow<String> = _fastbootDeviceInfoText.asStateFlow()

    private val _fastbootProduct = MutableStateFlow<String?>(null)
    val fastbootProduct: StateFlow<String?> = _fastbootProduct.asStateFlow()

    private val _fastbootToken = MutableStateFlow<String?>(null)
    val fastbootToken: StateFlow<String?> = _fastbootToken.asStateFlow()

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    val currentVersion = "8.2"

    fun isRussianLanguage(): Boolean {
        val lang = prefs.language
        return lang == PreferencesManager.LANG_RU ||
                (lang == PreferencesManager.LANG_SYSTEM && Locale.getDefault().language.lowercase().startsWith("ru"))
    }

    val updateUrl: String
        get() = if (isRussianLanguage()) "https://miunlocktool.ru" else "https://miunlock.su"

    val versionCheckUrl: String
        get() = if (isRussianLanguage()) "https://miunlocktool.ru/version.txt" else "https://miunlock.su/version.txt"

    val apkDownloadUrl: String
        get() = if (isRussianLanguage()) "https://miunlocktool.ru/download/stable/android/miunlock.apk" else "https://miunlock.su/download/stable/android/miunlock.apk"

    val apkDownloadFallbackUrl: String
        get() = if (isRussianLanguage()) "https://miunlocktool.ru/miunlock.apk" else "https://miunlock.su/miunlock.apk"

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
        try {
            scheduler.start(mode)
        } catch (t: Throwable) {
            addLog("Error starting scheduler: ${t.localizedMessage ?: t.message}", LogColorType.RED)
        }
    }

    fun stopScheduler() {
        try {
            scheduler.stop()
        } catch (t: Throwable) {
            addLog("Error stopping scheduler: ${t.localizedMessage ?: t.message}", LogColorType.RED)
        }
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

    fun resetDownloadState() {
        _downloadState.value = DownloadState.Idle
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
                            UpdateResult.UpdateAvailable(cleanVersion, currentVersion, apkDownloadUrl)
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

    fun downloadUpdate(context: Context) {
        viewModelScope.launch {
            _downloadState.value = DownloadState.Progress(0, 0, -1)
            val result = withContext(Dispatchers.IO) {
                val candidateUrls = listOf(apkDownloadUrl, apkDownloadFallbackUrl)
                var lastError: String = "Download failed"

                for (url in candidateUrls) {
                    try {
                        val request = Request.Builder()
                            .url(url)
                            .header("User-Agent", "Mozilla/5.0 (Linux; Android 14) XiaomiUnlockTool-Updater")
                            .get()
                            .build()

                        httpClient.newCall(request).execute().use { response ->
                            if (!response.isSuccessful) {
                                lastError = "HTTP error: ${response.code}"
                                return@use
                            }
                            val body = response.body ?: run {
                                lastError = "Empty response body"
                                return@use
                            }
                            val contentLength = body.contentLength()
                            val targetDir = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS) ?: context.cacheDir
                            if (!targetDir.exists()) {
                                targetDir.mkdirs()
                            }
                            val apkFile = File(targetDir, "miunlock.apk")
                            if (apkFile.exists()) {
                                apkFile.delete()
                            }

                            body.byteStream().use { input ->
                                FileOutputStream(apkFile).use { output ->
                                    val buffer = ByteArray(8192)
                                    var bytesRead: Int
                                    var totalRead = 0L
                                    var lastPercent = -1

                                    while (input.read(buffer).also { bytesRead = it } != -1) {
                                        output.write(buffer, 0, bytesRead)
                                        totalRead += bytesRead
                                        if (contentLength > 0) {
                                            val percent = ((totalRead * 100) / contentLength).toInt().coerceIn(0, 100)
                                            if (percent != lastPercent) {
                                                lastPercent = percent
                                                _downloadState.value = DownloadState.Progress(percent, totalRead, contentLength)
                                            }
                                        }
                                    }
                                    output.flush()
                                }
                            }

                            return@withContext DownloadState.Success(apkFile)
                        }
                    } catch (e: Exception) {
                        lastError = e.localizedMessage ?: e.message ?: "Download failed"
                    }
                }

                DownloadState.Error(lastError)
            }
            _downloadState.value = result
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

    // Fastboot Actions
    fun checkAndConnectFastboot(context: Context) {
        val devices = fastbootTransport.findFastbootDevices()
        if (devices.isEmpty()) {
            _fastbootDeviceState.value = FastbootConnectionState.NO_DEVICE
            _fastbootDeviceInfoText.value = "USB device not found"
            addLog("[USB] No USB devices detected. Connect a Xiaomi device in Fastboot mode via USB OTG adapter.", LogColorType.YELLOW)
            return
        }

        val target = devices.firstOrNull { it.hasFastbootInterface } ?: devices.first()
        val dev = target.device
        val devDesc = "${target.name} (VID: 0x%04X, PID: 0x%04X)".format(target.vendorId, target.productId)

        _fastbootDeviceInfoText.value = devDesc
        addLog("[USB] Device detected: $devDesc", LogColorType.CYAN)

        if (!fastbootTransport.hasPermission(dev)) {
            _fastbootDeviceState.value = FastbootConnectionState.PERMISSION_REQUIRED
            addLog("[USB] Permission requested for ${target.name}", LogColorType.DEFAULT)
            fastbootTransport.requestPermission(context, dev)
        } else {
            addLog("[USB] Permission already granted", LogColorType.GREEN)
            connectFastbootDevice(dev)
        }
    }

    fun onUsbPermissionResult(granted: Boolean, device: UsbDevice?) {
        if (granted && device != null) {
            addLog("[USB] Permission granted", LogColorType.GREEN)
            connectFastbootDevice(device)
        } else {
            _fastbootDeviceState.value = FastbootConnectionState.ERROR
            _fastbootDeviceInfoText.value = "USB permission denied"
            addLog("[USB] USB permission denied", LogColorType.RED)
        }
    }

    fun connectFastbootDevice(device: UsbDevice) {
        _fastbootDeviceState.value = FastbootConnectionState.CONNECTING
        addLog("[FASTBOOT] Connecting to ${device.deviceName}...", LogColorType.DEFAULT)

        val res = fastbootTransport.connect(device)
        if (res.isSuccess) {
            _fastbootDeviceState.value = FastbootConnectionState.CONNECTED
            addLog("[FASTBOOT] Interface found and claimed. Fastboot connected!", LogColorType.GREEN)
        } else {
            _fastbootDeviceState.value = FastbootConnectionState.ERROR
            val msg = res.exceptionOrNull()?.message ?: "Connection failed"
            _fastbootDeviceInfoText.value = msg
            addLog("[FASTBOOT] Connection error: $msg", LogColorType.RED)
        }
    }

    fun disconnectFastboot() {
        fastbootTransport.disconnect()
        _fastbootDeviceState.value = FastbootConnectionState.DISCONNECTED
        _fastbootDeviceInfoText.value = "Disconnected"
        _fastbootProduct.value = null
        _fastbootToken.value = null
        addLog("[FASTBOOT] Disconnected", LogColorType.YELLOW)
    }

    fun fetchFastbootProduct() {
        if (!fastbootTransport.isConnected) {
            addLog("[FASTBOOT] Device is not connected. Tap 'Connect' first.", LogColorType.YELLOW)
            return
        }
        viewModelScope.launch(Dispatchers.IO) {
            addLog("[FASTBOOT] Sending: getvar:product", LogColorType.DEFAULT)
            val res = fastbootManager.getProduct()
            if (res.isSuccess) {
                val prod = res.getOrThrow()
                _fastbootProduct.value = prod
                addLog("[FASTBOOT] Response: OKAY", LogColorType.DEFAULT)
                addLog("[FASTBOOT] Product: $prod", LogColorType.GREEN)
            } else {
                val err = res.exceptionOrNull()?.message ?: "Unknown error"
                addLog("[FASTBOOT] Error reading product: $err", LogColorType.RED)
            }
        }
    }

    fun fetchFastbootToken() {
        if (!fastbootTransport.isConnected) {
            addLog("[FASTBOOT] Device is not connected. Tap 'Connect' first.", LogColorType.YELLOW)
            return
        }
        viewModelScope.launch(Dispatchers.IO) {
            addLog("[FASTBOOT] Requesting token (oem get_token / getvar:token)...", LogColorType.DEFAULT)
            val res = fastbootManager.getToken()
            if (res.isSuccess) {
                val token = res.getOrThrow()
                _fastbootToken.value = token
                addLog("[FASTBOOT] Token received: ${token.take(24)}... (length: ${token.length})", LogColorType.GREEN)
                addLog("[FASTBOOT] Full Token: $token", LogColorType.CYAN)
            } else {
                val err = res.exceptionOrNull()?.message ?: "Unknown error"
                addLog("[FASTBOOT] Failed to retrieve token: $err", LogColorType.RED)
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        fastbootTransport.disconnect()
    }
}
