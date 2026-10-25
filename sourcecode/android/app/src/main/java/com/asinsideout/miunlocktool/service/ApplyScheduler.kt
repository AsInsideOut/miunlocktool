package com.asinsideout.miunlocktool.service

import android.content.Context
import com.asinsideout.miunlocktool.data.AccountStatus
import com.asinsideout.miunlocktool.data.ApplyResult
import com.asinsideout.miunlocktool.data.ExecutionMode
import com.asinsideout.miunlocktool.data.LogColorType
import com.asinsideout.miunlocktool.data.LogEntry
import com.asinsideout.miunlocktool.data.PingResult
import com.asinsideout.miunlocktool.data.PingTester
import com.asinsideout.miunlocktool.data.PreferencesManager
import com.asinsideout.miunlocktool.data.SntpClient
import com.asinsideout.miunlocktool.data.XiaomiApiService
import com.asinsideout.miunlocktool.data.TranslationManager
import android.util.Log
import kotlinx.coroutines.CoroutineExceptionHandler
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
    private val scope: CoroutineScope,
    private val notificationManager: LiveNotificationManager? = null,
    private val context: Context? = null
) {

    companion object {
        var activeInstance: ApplyScheduler? = null
    }

    private val _clockBeijing = MutableStateFlow("--:--:--.---")
    val clockBeijing: StateFlow<String> = _clockBeijing.asStateFlow()

    private val _countdown = MutableStateFlow("--:--:--")
    val countdown: StateFlow<String> = _countdown.asStateFlow()

    private val _pingMs = MutableStateFlow(-1L)
    val pingMs: StateFlow<Long> = _pingMs.asStateFlow()

    private val _pingDetailed = MutableStateFlow<PingResult?>(null)
    val pingDetailed: StateFlow<PingResult?> = _pingDetailed.asStateFlow()

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
        // Automatic initial ping measurement in background
        measurePing(autoTriggered = true)
    }

    fun log(text: String, color: LogColorType = LogColorType.DEFAULT) {
        val now = logTimeFormat.format(sntpClient.getSynchronizedTimeMs())
        scope.launch {
            _logFlow.emit(LogEntry(now, text, color))
        }
    }

    fun syncNtp(autoTriggered: Boolean = false) {
        scope.launch {
            if (autoTriggered) {
                log(TranslationManager.tr("log_ntp_auto_reached"), LogColorType.CYAN)
            } else {
                log(TranslationManager.tr("log_connecting_ntp", prefs.ntpServer), LogColorType.CYAN)
            }
            val success = sntpClient.requestTime(prefs.ntpServer)
            if (success) {
                val cal = sntpClient.getBeijingCalendar()
                log(TranslationManager.tr("log_ntp_success", timeFormat.format(cal.time), sntpClient.clockOffsetMs), LogColorType.GREEN)
            } else {
                log(TranslationManager.tr("log_ntp_failed"), LogColorType.YELLOW)
            }
        }
    }

    fun measurePing(autoTriggered: Boolean = false) {
        scope.launch {
            if (!autoTriggered) {
                log(TranslationManager.tr("log_latency_measuring"), LogColorType.CYAN)
            }
            val res = pingTester.measureQuickPing()
            _pingDetailed.value = res
            _pingMs.value = res.averageMs
            if (res.averageMs > 0 && !autoTriggered) {
                log(TranslationManager.tr("log_latency_result", res.httpPingMs, res.tcpPingMs, res.averageMs), LogColorType.GREEN)
                val sendSeconds = calculateSendTime(res.averageMs)
                log(TranslationManager.tr("log_trigger_time", String.format(Locale.US, "%.3f", sendSeconds)), LogColorType.CYAN)
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
            var lastAutoNtpDay = -1
            var lastPeriodicPingTime = 0L

            while (isActive) {
                val beijingNowMs = sntpClient.getSynchronizedTimeMs()
                val cal = Calendar.getInstance(SntpClient.BEIJING_TIMEZONE)
                cal.timeInMillis = beijingNowMs
                _clockBeijing.value = timeFormat.format(cal.time)

                val hour = cal.get(Calendar.HOUR_OF_DAY)
                val min = cal.get(Calendar.MINUTE)
                val sec = cal.get(Calendar.SECOND)
                val day = cal.get(Calendar.DAY_OF_YEAR)

                // Automatic NTP synchronization at 23:59:00 Beijing time
                if (hour == 23 && min == 59 && sec >= 0 && sec < 5 && day != lastAutoNtpDay) {
                    lastAutoNtpDay = day
                    syncNtp(autoTriggered = true)
                }

                // Automatic ping (PC style): 23:59:40
                if (hour == 23 && min == 59 && sec >= 40 && sec < 45 && day != lastAutoPingDay && !_isRunning.value) {
                    lastAutoPingDay = day
                    measurePing(autoTriggered = true)
                }

                // Periodic background ping check every 60s when not close to midnight
                val nowReal = System.currentTimeMillis()
                if (nowReal - lastPeriodicPingTime > 60_000L && !(hour == 23 && min == 59)) {
                    lastPeriodicPingTime = nowReal
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
            log(TranslationManager.tr("log_error_token_empty"), LogColorType.RED)
            return
        }

        // Cancel previous job if running without stopping service
        schedulerJob?.cancel()
        schedulerJob = null
        _isRunning.value = true
        activeInstance = this

        try {
            context?.let { ApplyForegroundService.start(it) }
        } catch (t: Throwable) {
            Log.e("ApplyScheduler", "Failed to start foreground service", t)
        }
        try {
            notificationManager?.updateCountdown(_countdown.value)
        } catch (t: Throwable) {
            Log.e("ApplyScheduler", "Failed to update notification", t)
        }

        val handler = CoroutineExceptionHandler { _, throwable ->
            Log.e("ApplyScheduler", "Coroutine unhandled exception", throwable)
            log("Error: ${throwable.localizedMessage ?: throwable.message}", LogColorType.RED)
            stop()
        }

        schedulerJob = scope.launch(Dispatchers.Default + handler) {
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
        activeInstance = null
        try {
            context?.let { ApplyForegroundService.stop(it) }
        } catch (t: Throwable) {
            Log.e("ApplyScheduler", "Failed to stop foreground service", t)
        }
        try {
            notificationManager?.cancel()
        } catch (t: Throwable) {
            Log.e("ApplyScheduler", "Failed to cancel notification", t)
        }
        log(TranslationManager.tr("log_process_stopped"), LogColorType.YELLOW)
    }

    private suspend fun runAutoMode(token: String) {
        log(TranslationManager.tr("log_auto_mode_started"), LogColorType.PURPLE)

        // Ensure NTP is synced initially
        if (!sntpClient.isSynchronized) {
            log(TranslationManager.tr("log_syncing_time"), LogColorType.CYAN)
            sntpClient.requestTime(prefs.ntpServer)
        }

        var autoNtpDoneThisCycle = false
        var autoPingDoneThisCycle = false
        var lastNotifSec = -1

        while (_isRunning.value) {
            val cal = sntpClient.getBeijingCalendar()
            val hour = cal.get(Calendar.HOUR_OF_DAY)
            val min = cal.get(Calendar.MINUTE)
            val sec = cal.get(Calendar.SECOND)
            val millis = cal.get(Calendar.MILLISECOND)

            // Update live notification countdown once every second
            if (sec != lastNotifSec) {
                lastNotifSec = sec
                notificationManager?.updateCountdown(_countdown.value)
            }

            // 1. Automatic NTP synchronization at 23:59:00 Beijing time
            if (hour == 23 && min == 59 && sec >= 0 && sec < 5 && !autoNtpDoneThisCycle) {
                autoNtpDoneThisCycle = true
                syncNtp(autoTriggered = true)
            }

            // 2. Automatic Ping measurement like PC version: 15s measurement starting at 23:59:40
            if (hour == 23 && min == 59 && sec >= 40 && !autoPingDoneThisCycle) {
                autoPingDoneThisCycle = true
                log(TranslationManager.tr("log_ping_wait_pc"), LogColorType.CYAN)
                val pingResult = pingTester.measurePings(durationSeconds = 15)
                _pingDetailed.value = pingResult
                _pingMs.value = pingResult.averageMs
                log(
                    TranslationManager.tr("log_ping_result_pc", pingResult.httpPingMs, pingResult.tcpPingMs, pingResult.averageMs),
                    LogColorType.GREEN
                )
                val sendSec = calculateSendTime(pingResult.averageMs)
                log(TranslationManager.tr("log_trigger_time", String.format(Locale.US, "%.3f", sendSec)), LogColorType.CYAN)
            }

            // Calculate trigger time based on measured ping
            val targetSeconds = if (_pingMs.value > 0) {
                calculateSendTime(_pingMs.value)
            } else {
                58.800
            }
            val currentSeconds = sec.toDouble() + (millis.toDouble() / 1000.0)

            val timings = prefs.getActiveTimings()
            val firstTiming = timings.firstOrNull() ?: 58.700
            val scheduleSeconds = maxOf(50.0, firstTiming - 3.0)

            // Start timing profile sequence at calculated trigger time
            if (hour == 23 && min == 59 && currentSeconds >= scheduleSeconds) {
                notificationManager?.updateSending()
                val profileName = when (prefs.timingProfile) {
                    PreferencesManager.PROFILE_ASIA -> "Asia"
                    PreferencesManager.PROFILE_USA_AFRICA -> "USA / Africa"
                    PreferencesManager.PROFILE_CUSTOM -> "Custom"
                    else -> "Europe"
                }
                val timingsStr = timings.joinToString(", ") { String.format(Locale.US, "%.3fs", it) }
                log(TranslationManager.tr("log_scheduling_requests", profileName, timings.size, timingsStr), LogColorType.PURPLE)

                // Dispatch requests for each timing in the profile with unique device_ids
                for ((index, tVal) in timings.withIndex()) {
                    scope.launch(Dispatchers.IO) {
                        val targetCal = Calendar.getInstance(SntpClient.BEIJING_TIMEZONE).apply {
                            timeInMillis = sntpClient.getSynchronizedTimeMs()
                            set(Calendar.HOUR_OF_DAY, 23)
                            set(Calendar.MINUTE, 59)
                            val secPart = tVal.toInt()
                            val msPart = Math.round((tVal - secPart) * 1000).toInt()
                            set(Calendar.SECOND, secPart)
                            set(Calendar.MILLISECOND, msPart)
                        }
                        val delayMs = maxOf(0L, targetCal.timeInMillis - sntpClient.getSynchronizedTimeMs())
                        if (delayMs > 0) {
                            delay(delayMs)
                        }
                        if (!_isRunning.value) return@launch

                        val devId = apiService.generateDeviceId()
                        val seq = index + 1
                        log(TranslationManager.tr("log_sending_target", seq, timings.size, String.format(Locale.US, "%.3f", tVal), devId.take(8)), LogColorType.CYAN)

                        // Stage 1: Отправка заявки
                        log(TranslationManager.tr("log_apply_sending_seq", seq), LogColorType.PURPLE)
                        val result = apiService.applyUnlock(token, devId)
                        if (!result.isSent) {
                            log(TranslationManager.tr("log_apply_send_failed_seq", seq, result.message), LogColorType.RED)
                            handleApplyResult(result, seq)
                            return@launch
                        }
                        log(TranslationManager.tr("log_apply_sent_success_seq", seq), LogColorType.GREEN)

                        // Stage 2: Получение статуса
                        log(TranslationManager.tr("log_getting_status_seq", seq), LogColorType.CYAN)
                        val finalResult = resolveStatus(result, token, seq)
                        val stop = handleApplyResult(finalResult, seq)
                        if (stop) {
                            _isRunning.value = false
                        }
                    }
                }

                // Wait until requests are executed across midnight
                delay(8000L)
                _isRunning.value = false
                return
            }

            delay(50)
        }
    }

    private suspend fun runManualMode(token: String) {
        notificationManager?.updateSending()
        val devId = apiService.generateDeviceId()
        log(TranslationManager.tr("log_manual_sending", devId.take(8)), LogColorType.PURPLE)

        // Stage 1: Отправка заявки
        log(TranslationManager.tr("log_apply_sending"), LogColorType.PURPLE)
        val result = apiService.applyUnlock(token, devId)
        if (!result.isSent) {
            log(TranslationManager.tr("log_apply_send_failed", result.message), LogColorType.RED)
            handleApplyResult(result, 1)
            _isRunning.value = false
            return
        }
        log(TranslationManager.tr("log_apply_sent_success"), LogColorType.GREEN)

        // Stage 2: Получение статуса
        log(TranslationManager.tr("log_getting_status"), LogColorType.CYAN)
        val finalResult = resolveStatus(result, token, 1)
        handleApplyResult(finalResult, 1)
        _isRunning.value = false
    }

    private suspend fun resolveStatus(result: ApplyResult, token: String, seq: Int): ApplyResult {
        // If apply response already confirmed success
        if (result.isSuccess) {
            try {
                val statusCheck = apiService.checkAccountStatus(token)
                if (statusCheck.status == AccountStatus.APPROVED) {
                    log(TranslationManager.tr("log_status_account_approved", statusCheck.deadline ?: ""), LogColorType.GREEN)
                    return result.copy(deadline = statusCheck.deadline ?: result.deadline)
                }
            } catch (_: Exception) {}
            return result
        }

        // If apply response indicates token expired
        if (result.code == 100004 || result.code == 10004) {
            return result
        }

        // If apply response indicates quota code 0 applyResult 3
        if (result.code == 0 && result.applyResult == 3) {
            return result
        }

        // If status was unavailable or unparseable, query separate status endpoint
        if (result.isStatusUnavailable || result.code == -1) {
            try {
                val statusCheck = apiService.checkAccountStatus(token)
                when (statusCheck.status) {
                    AccountStatus.APPROVED -> {
                        log(TranslationManager.tr("log_status_account_approved", statusCheck.deadline ?: ""), LogColorType.GREEN)
                        return result.copy(
                            isSuccess = true,
                            code = 0,
                            applyResult = 1,
                            isStatusUnavailable = false,
                            deadline = statusCheck.deadline
                        )
                    }
                    AccountStatus.EXPIRED -> {
                        return result.copy(code = 100004, isStatusUnavailable = false)
                    }
                    AccountStatus.READY -> {
                        return result.copy(isStatusUnavailable = true, message = statusCheck.message)
                    }
                    AccountStatus.BLOCKED -> {
                        return result.copy(code = 100001, isStatusUnavailable = false, message = statusCheck.message, deadline = statusCheck.deadline)
                    }
                    AccountStatus.TOO_NEW -> {
                        return result.copy(code = 100002, isStatusUnavailable = false, message = statusCheck.message)
                    }
                    else -> {
                        log(TranslationManager.tr("log_status_unavailable"), LogColorType.YELLOW)
                        return result.copy(isStatusUnavailable = true)
                    }
                }
            } catch (e: Exception) {
                log(TranslationManager.tr("log_status_unavailable"), LogColorType.YELLOW)
                return result.copy(isStatusUnavailable = true)
            }
        }

        return result
    }

    private suspend fun handleApplyResult(result: ApplyResult, seq: Int): Boolean {
        _applyResultFlow.emit(result)

        if (result.isSuccess) {
            notificationManager?.updateSuccess()
            context?.let { ApplyForegroundService.stop(it) }
            if (result.code == 100003) {
                log(TranslationManager.tr("log_success_100003"), LogColorType.GREEN)
            } else {
                log(TranslationManager.tr("log_success_approved", result.code, result.applyResult?.toString() ?: "1"), LogColorType.GREEN)
            }
            return true
        } else if (result.isStatusUnavailable) {
            log(TranslationManager.tr("log_status_unavailable_summary"), LogColorType.YELLOW)
            return false
        } else if (result.code == 0 && result.applyResult == 3) {
            notificationManager?.updateSuccess()
            context?.let { ApplyForegroundService.stop(it) }
            log(TranslationManager.tr("log_success_code0"), LogColorType.GREEN)
            return false
        } else if (result.code == 100004 || result.code == 10004) {
            notificationManager?.cancel()
            context?.let { ApplyForegroundService.stop(it) }
            log(TranslationManager.tr("log_error_token_expired"), LogColorType.RED)
            return true
        } else if (!result.isSent) {
            return false
        } else {
            log(TranslationManager.tr("log_response_code", seq, result.code, result.message), LogColorType.YELLOW)
            return false
        }
    }
}
