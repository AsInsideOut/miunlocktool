package com.asinsideout.miunlocktool.service

import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import android.util.Log
import androidx.core.content.ContextCompat
import com.asinsideout.miunlocktool.data.PreferencesManager

class ApplyForegroundService : Service() {

    companion object {
        private const val TAG = "ApplyForegroundService"
        const val ACTION_START = "com.asinsideout.miunlocktool.action.START"
        const val ACTION_STOP = "com.asinsideout.miunlocktool.action.STOP"
        const val ACTION_STOP_FROM_NOTIFICATION = "com.asinsideout.miunlocktool.action.STOP_FROM_NOTIFICATION"

        fun start(context: Context) {
            try {
                val intent = Intent(context, ApplyForegroundService::class.java).apply {
                    action = ACTION_START
                }
                ContextCompat.startForegroundService(context, intent)
            } catch (t: Throwable) {
                Log.e(TAG, "Failed to start foreground service", t)
            }
        }

        fun stop(context: Context) {
            try {
                val intent = Intent(context, ApplyForegroundService::class.java).apply {
                    action = ACTION_STOP
                }
                context.startService(intent)
            } catch (t: Throwable) {
                Log.e(TAG, "Failed to stop service", t)
            }
        }
    }

    private var wakeLock: PowerManager.WakeLock? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        try {
            when (intent?.action) {
                ACTION_STOP_FROM_NOTIFICATION -> {
                    Log.d(TAG, "Stopped by notification button")
                    try {
                        ApplyScheduler.activeInstance?.stop()
                    } catch (_: Throwable) {}
                    releaseWakeLock()
                    try {
                        stopForeground(STOP_FOREGROUND_REMOVE)
                    } catch (_: Throwable) {}
                    stopSelf()
                }
                ACTION_STOP -> {
                    Log.d(TAG, "Service stop requested by scheduler")
                    releaseWakeLock()
                    try {
                        stopForeground(STOP_FOREGROUND_REMOVE)
                    } catch (_: Throwable) {}
                    stopSelf()
                }
                ACTION_START -> {
                    acquireWakeLock()
                    val prefs = PreferencesManager(this)
                    val notifManager = LiveNotificationManager(this, prefs)
                    val notification = notifManager.buildCountdownNotification("--:--:--")

                    var started = false
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                        try {
                            startForeground(
                                LiveNotificationManager.NOTIFICATION_ID,
                                notification,
                                ServiceInfo.FOREGROUND_SERVICE_TYPE_SPECIAL_USE
                            )
                            started = true
                        } catch (t: Throwable) {
                            Log.w(TAG, "startForeground with SPECIAL_USE failed: ${t.message}")
                        }
                    }

                    if (!started && Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        try {
                            startForeground(LiveNotificationManager.NOTIFICATION_ID, notification, 0)
                            started = true
                        } catch (t: Throwable) {
                            Log.w(TAG, "startForeground with type 0 failed: ${t.message}")
                        }
                    }

                    if (!started) {
                        try {
                            startForeground(LiveNotificationManager.NOTIFICATION_ID, notification)
                        } catch (t: Throwable) {
                            Log.e(TAG, "startForeground fallback failed: ${t.message}")
                        }
                    }
                }
            }
        } catch (t: Throwable) {
            Log.e(TAG, "Error in onStartCommand", t)
        }
        return START_NOT_STICKY
    }

    private fun acquireWakeLock() {
        try {
            if (wakeLock == null) {
                val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
                wakeLock = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "MiUnlock:CountdownWakeLock").apply {
                    acquire(6 * 60 * 60 * 1000L)
                }
            }
        } catch (t: Throwable) {
            Log.w(TAG, "Could not acquire WakeLock", t)
        }
    }

    private fun releaseWakeLock() {
        try {
            if (wakeLock?.isHeld == true) {
                wakeLock?.release()
            }
        } catch (_: Throwable) {}
        wakeLock = null
    }

    override fun onDestroy() {
        releaseWakeLock()
        super.onDestroy()
    }
}
