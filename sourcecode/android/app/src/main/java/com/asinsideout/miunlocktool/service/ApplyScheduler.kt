package com.asinsideout.miunlocktool.service

import com.asinsideout.miunlocktool.data.ApplyResult
import com.asinsideout.miunlocktool.data.ExecutionMode
import com.asinsideout.miunlocktool.data.LogColorType
import com.asinsideout.miunlocktool.data.LogEntry
import com.asinsideout.miunlocktool.data.PingTester
import com.asinsideout.miunlocktool.data.PreferencesManager
import com.asinsideout.miunlocktool.data.SntpClient
import com.asinsideout.miunlocktool.data.XiaomiApiService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

class ApplyScheduler(
    private val prefs: PreferencesManager,
    private val apiService: XiaomiApiService,
    private val sntpClient: SntpClient,
    private val pingTester: PingTester,
    private val scope: CoroutineScope
) {

    private val _clockBeijing = MutableStateFlow("--:--:--.---")
    val clockBeijing: StateFlow<String> = _clockBeijing.asStateFlow()

    private val _countdown = MutableStateFlow("--:--:--")
    val countdown: StateFlow<String> = _countdown.asStateFlow()

    private val _pingMs = MutableStateFlow(-1L)
    val pingMs: StateFlow<Long> = _pingMs.asStateFlow()

    private val _isRunning = MutableStateFlow(false)
    val isRunning: StateFlow<Boolean> = _isRunning.asStateFlow()

    private val _logFlow = MutableSharedFlow<LogEntry>(replay = 100)
    val logFlow: SharedFlow<LogEntry> = _logFlow.asSharedFlow()

    private val _applyResultFlow = MutableSharedFlow<ApplyResult>()
    val applyResultFlow: SharedFlow<ApplyResult> = _applyResultFlow.asSharedFlow()

    private var clockJob: Job? = null
    private var schedulerJob: Job? = null

    private val timeFormat = SimpleDateFormat("HH:mm:ss.SSS", Locale.US).apply {
        timeZone = SntpClient.BEIJING_TIMEZONE
    }
    private val logTimeFormat = SimpleDateFormat("HH:mm:ss", Locale.US).apply {
        timeZone = SntpClient.BEIJING_TIMEZONE
    }

    init {
        startClockTicker()
    }

    fun log(text: String, color: LogColorType = LogColorType.DEFAULT) {
        val now = logTimeFormat.format(sntpClient.getSynchronizedTimeMs())
        scope.launch {
            _logFlow.emit(LogEntry(now, text, color))
        }
    }

    fun syncNtp() {
        scope.launch {
            log("Connecting to NTP server: ${prefs.ntpServer}...", LogColorType.CYAN)
            val success = sntpClient.requestTime(prefs.ntpServer)
            if (success) {
                val cal = sntpClient.getBeijingCalendar()
                log("NTP Synchronized! Beijing Time: ${timeFormat.format(cal.time)} (Offset: ${sntpClient.clockOffsetMs} ms)", LogColorType.GREEN)
            } else {
                log("NTP synchronization failed. Using system clock.", LogColorType.YELLOW)
            }
        }
    }

    fun measurePing(autoTriggered: Boolean = false) {
        scope.launch {
            if (autoTriggered) {
                log("Beijing 23:59:50 reached: Measuring API ping automatically...", LogColorType.CYAN)
            } else {
                log("Measuring latency to Xiaomi API...", LogColorType.CYAN)
            }
            val ping = pingTester.measureAveragePingMs()
            _pingMs.value = ping
            if (ping > 0) {
                log("Average ping: $ping ms", LogColorType.GREEN)
                val sendSeconds = calculateSendTime(ping)
                log("Calculated trigger time: 23:59:${String.format(Locale.US, "%.3f", sendSeconds)}", LogColorType.CYAN)
            } else {
                log("Ping measurement timed out", LogColorType.RED)
            }
        }
    }

    private fun calculateSendTime(pingMs: Long): Double {
        val pingSec = pingMs / 1000.0
        var sendTime = 60.0 - pingSec
        if (sendTime < 56.0) sendTime = 56.0
        if (sendTime > 59.95) sendTime = 59.95
        return sendTime
    }

    private fun startClockTicker() {
        clockJob?.cancel()
        clockJob = scope.launch(Dispatchers.Default) {
            var lastAutoPingDay = -1
            while (isActive) {
                val beijingNowMs = sntpClient.getSynchronizedTimeMs()
                val cal = Calendar.getInstance(SntpClient.BEIJING_TIMEZONE)
                cal.timeInMillis = beijingNowMs
                _clockBeijing.value = timeFormat.format(cal.time)

                val hour = cal.get(Calendar.HOUR_OF_DAY)
                val min = cal.get(Calendar.MINUTE)
                val sec = cal.get(Calendar.SECOND)
                val day = cal.get(Calendar.DAY_OF_YEAR)

                // Measure ping automatically at 23:59:50 Beijing time
                if (hour == 23 && min == 59 && sec == 50 && day != lastAutoPingDay) {
                    lastAutoPingDay = day
                    measurePing(autoTriggered = true)
                }

                // Calculate countdown until midnight Beijing time (00:00:00)
                val target = Calendar.getInstance(SntpClient.BEIJING_TIMEZONE)
                target.timeInMillis = beijingNowMs
                target.set(Calendar.HOUR_OF_DAY, 24)
                target.set(Calendar.MINUTE, 0)
                target.set(Calendar.SECOND, 0)
                target.set(Calendar.MILLISECOND, 0)

                val diffMs = target.timeInMillis - beijingNowMs
                if (diffMs > 0) {
                    val hours = (diffMs / (1000 * 60 * 60)) % 24
                    val minutes = (diffMs / (1000 * 60)) % 60
                    val seconds = (diffMs / 1000) % 60
                    val millis = diffMs % 1000
                    _countdown.value = String.format(Locale.US, "%02d:%02d:%02d.%03d", hours, minutes, seconds, millis)
                } else {
                    _countdown.value = "00:00:00.000"
                }

                delay(50)
            }
        }
    }

    fun start(mode: ExecutionMode) {
        val token = prefs.token
        if (token.isEmpty()) {
            log("Error: Token is empty. Enter new_bbs_serviceToken first.", LogColorType.RED)
            return
        }

        stop()
        _isRunning.value = true

        schedulerJob = scope.launch(Dispatchers.Default) {
            when (mode) {
                ExecutionMode.AUTO -> runAutoMode(token)
                ExecutionMode.MANUAL -> runManualMode(token)
            }
        }
    }

    fun stop() {
        schedulerJob?.cancel()
        schedulerJob = null
        _isRunning.value = false
        log("Process stopped.", LogColorType.YELLOW)
    }

    private suspend fun runAutoMode(token: String) {
        log("Auto Mode started. Waiting for Beijing midnight...", LogColorType.PURPLE)

        // Ensure NTP is synced
        if (!sntpClient.isSynchronized) {
            log("Syncing time with NTP...", LogColorType.CYAN)
            sntpClient.requestTime(prefs.ntpServer)
        }

        var autoPingDoneThisCycle = false
        while (_isRunning.value) {
            val cal = sntpClient.getBeijingCalendar()
            val hour = cal.get(Calendar.HOUR_OF_DAY)
            val min = cal.get(Calendar.MINUTE)
            val sec = cal.get(Calendar.SECOND)
            val millis = cal.get(Calendar.MILLISECOND)

            // Re-sync NTP at 23:58:00
            if (hour == 23 && min == 58 && sec == 0) {
                log("Re-synchronizing NTP at 23:58...", LogColorType.CYAN)
                sntpClient.requestTime(prefs.ntpServer)
                delay(1000)
            }

            // Measure ping automatically at 23:59:50 Beijing time
            if (hour == 23 && min == 59 && sec == 50 && !autoPingDoneThisCycle) {
                autoPingDoneThisCycle = true
                measurePing(autoTriggered = true)
            }

            // Calculate trigger time based on measured ping
            val targetSeconds = if (_pingMs.value > 0) {
                calculateSendTime(_pingMs.value)
            } else {
                58.800
            }
            val currentSeconds = sec.toDouble() + (millis.toDouble() / 1000.0)

            // Start burst sequence at calculated trigger time
            if (hour == 23 && min == 59 && currentSeconds >= targetSeconds) {
                log("Burst trigger reached (23:59:${String.format(Locale.US, "%.3f", targetSeconds)})! Starting burst sequence...", LogColorType.PURPLE)
                val burstCount = prefs.burstCount
                val interval = prefs.burstIntervalMs

                for (i in 1..burstCount) {
                    if (!_isRunning.value) break
                    val devId = apiService.generateDeviceId()
                    log("[Burst #$i/$burstCount] Sending with deviceId: ${devId.take(8)}...", LogColorType.CYAN)
                    val result = apiService.applyUnlock(token, devId)
                    val stopLoop = handleApplyResult(result, i)
                    if (stopLoop) break
                    delay(interval)
                }
                _isRunning.value = false
                return
            }

            delay(50)
        }
    }

    private suspend fun runManualMode(token: String) {
        log("Manual Mode: Sending single request now...", LogColorType.PURPLE)
        val result = apiService.applyUnlock(token)
        handleApplyResult(result, 1)
        _isRunning.value = false
    }

    private suspend fun handleApplyResult(result: ApplyResult, seq: Int): Boolean {
        _applyResultFlow.emit(result)

        if (result.isSuccess) {
            log("SUCCESS! Application approved (Code: ${result.code})! You can now bind your device!", LogColorType.GREEN)
            return true
        } else if (result.code == 0 && result.applyResult == 3) {
            log("LIMIT REACHED: Daily quota exceeded for today. (Deadline: ${result.deadline ?: "Tomorrow"})", LogColorType.YELLOW)
            return false
        } else if (result.code == 100004 || result.code == 10004) {
            log("ERROR: Token expired. Please refresh your new_bbs_serviceToken.", LogColorType.RED)
            return true
        } else {
            log("[#$seq] Response code: ${result.code}, message: ${result.message}", LogColorType.YELLOW)
            return false
        }
    }
}

