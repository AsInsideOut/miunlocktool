package com.asinsideout.miunlocktool.service

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.os.Build
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.data.PreferencesManager
import com.asinsideout.miunlocktool.ui.MainActivity
import io.github.d4viddf.hyperisland_kit.HyperIslandNotification
import io.github.d4viddf.hyperisland_kit.HyperPicture
import io.github.d4viddf.hyperisland_kit.models.ImageTextInfoLeft
import io.github.d4viddf.hyperisland_kit.models.PicInfo
import io.github.d4viddf.hyperisland_kit.models.TextInfo
import io.github.d4viddf.hyperisland_kit.models.TimerInfo

class LiveNotificationManager(
    private val context: Context,
    private val prefs: PreferencesManager
) {

    companion object {
        private const val TAG = "LiveNotificationManager"
        const val CHANNEL_ID = "miunlock_spotlight_channel_v2"
        const val NOTIFICATION_ID = 2026

        // Picture keys
        private const val PIC_KEY_CLOCK = "icon_clock"
        private const val PIC_KEY_BOLT = "icon_bolt"
        private const val PIC_KEY_CHECK = "icon_check"
    }

    private val notificationManager = NotificationManagerCompat.from(context)

    // Track first post to only enable float (island expansion) on the initial show
    private var isFirstPost = true

    init {
        createNotificationChannel()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            try {
                // Delete legacy low importance channel if present
                val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
                try {
                    nm.deleteNotificationChannel("miunlock_live_status_channel")
                } catch (_: Throwable) {}

                val channel = NotificationChannel(
                    CHANNEL_ID,
                    context.getString(R.string.notif_channel_name),
                    NotificationManager.IMPORTANCE_HIGH // Required for HyperOS Notification Spotlight!
                ).apply {
                    description = context.getString(R.string.notif_channel_desc)
                    setShowBadge(true)
                    setSound(null, null)
                    enableVibration(false)
                    lockscreenVisibility = Notification.VISIBILITY_PUBLIC
                }
                nm.createNotificationChannel(channel)
            } catch (t: Throwable) {
                Log.e(TAG, "Error creating notification channel", t)
            }
        }
    }

    private fun getPendingIntent(): PendingIntent {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_SINGLE_TOP or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        return PendingIntent.getActivity(
            context,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }

    private fun getStopPendingIntent(): PendingIntent {
        val intent = Intent(context, ApplyForegroundService::class.java).apply {
            action = ApplyForegroundService.ACTION_STOP_FROM_NOTIFICATION
        }
        return PendingIntent.getService(
            context,
            102,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }

    private fun isRussian(): Boolean {
        return prefs.language == "ru"
    }

    private fun createCircleBitmap(drawableId: Int, bgColor: Int): Bitmap {
        val size = 128
        val bitmap = Bitmap.createBitmap(size, size, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        val paint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = bgColor
            style = Paint.Style.FILL
        }
        canvas.drawCircle(size / 2f, size / 2f, size / 2f, paint)
        val drawable = ContextCompat.getDrawable(context, drawableId)?.mutate()
        if (drawable != null) {
            val iconSize = (size * 0.55f).toInt()
            val margin = (size - iconSize) / 2
            drawable.setBounds(margin, margin, margin + iconSize, margin + iconSize)
            drawable.setTint(Color.WHITE)
            drawable.draw(canvas)
        }
        return bitmap
    }

    /**
     * Helper that follows the exact same pattern as the HyperIsland demo's notify() method.
     * 1. Build NotificationCompat with addExtras(buildResourceBundle())
     * 2. After .build(), attach JSON via notification.extras.putString("miui.focus.param", ...)
     */
    private fun buildHyperNotification(
        compatBuilder: NotificationCompat.Builder,
        hyperBuilder: HyperIslandNotification
    ): Notification {
        try {
            // Step 1: Add resource bundle (actions + pics) to the compat builder BEFORE build()
            compatBuilder.addExtras(hyperBuilder.buildResourceBundle())

            // Step 2: Build the notification
            val notification = compatBuilder.build()

            // Step 3: Add JSON param AFTER build() — exactly like the demo
            notification.extras.putString("miui.focus.param", hyperBuilder.buildJsonParam())

            return notification
        } catch (t: Throwable) {
            Log.e(TAG, "Error building HyperIsland notification, falling back to standard", t)
            return compatBuilder.build()
        }
    }

    fun buildCountdownNotification(countdown: String): Notification {
        val cleanTimer = countdown.substringBefore(".")
        val subtitle = if (isRussian()) "До отправки" else "Time to submit"
        val circleColor = Color.parseColor("#007AFF") // HyperOS / iOS style timer blue

        val compatBuilder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notif_clock)
            .setLargeIcon(createCircleBitmap(R.drawable.ic_notif_clock, circleColor))
            .setContentTitle(cleanTimer) // Spotlight uses Title as the big clock digits
            .setContentText(subtitle)
            .setContentIntent(getPendingIntent())
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setCategory(NotificationCompat.CATEGORY_STOPWATCH) // Spotlight trigger in HyperOS!
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .addAction(
                R.drawable.ic_notif_stop,
                if (isRussian()) "Остановить" else "Stop",
                getStopPendingIntent()
            )

        // Build HyperIsland payload for countdown
        val islandTitle = "Xiaomi Unlock Tool"

        val hyperBuilder = HyperIslandNotification.Builder(context, "miunlock_tool", islandTitle)
            .addPicture(HyperPicture(PIC_KEY_CLOCK, context, R.drawable.ic_notif_clock))
            // ChatInfo with text content for the notification banner
            .setChatInfo(
                title = islandTitle,
                content = cleanTimer,
                pictureKey = PIC_KEY_CLOCK
            )
            // Small Island: clock icon
            .setSmallIsland(PIC_KEY_CLOCK)
            // Big Island: icon on left with countdown text
            .setBigIslandInfo(
                left = ImageTextInfoLeft(
                    type = 1,
                    picInfo = PicInfo(type = 1, pic = PIC_KEY_CLOCK),
                    textInfo = TextInfo(title = islandTitle, content = cleanTimer)
                )
            )
            // Island config
            .setIslandConfig(priority = 1, dismissible = false)
            .setIslandFirstFloat(false)
            .setEnableFloat(isFirstPost) // Only float (expand) on very first post
            .setShowNotification(true)

        return buildHyperNotification(compatBuilder, hyperBuilder)
    }

    fun updateCountdown(countdown: String) {
        try {
            notificationManager.notify(NOTIFICATION_ID, buildCountdownNotification(countdown))
            if (isFirstPost) isFirstPost = false
        } catch (t: Throwable) {
            Log.e(TAG, "updateCountdown error", t)
        }
    }

    fun buildSendingNotification(): Notification {
        val title = if (isRussian()) "Отправка..." else "Sending..."
        val subtitle = if (isRussian()) "Отправка заявок" else "Submitting requests"
        val circleColor = Color.parseColor("#FF9500") // Orange for sending burst

        val compatBuilder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notif_bolt)
            .setLargeIcon(createCircleBitmap(R.drawable.ic_notif_bolt, circleColor))
            .setContentTitle(title)
            .setContentText(subtitle)
            .setContentIntent(getPendingIntent())
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setCategory(NotificationCompat.CATEGORY_STOPWATCH)
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .addAction(
                R.drawable.ic_notif_stop,
                if (isRussian()) "Остановить" else "Stop",
                getStopPendingIntent()
            )

        val islandTitle = "Xiaomi Unlock Tool"

        val hyperBuilder = HyperIslandNotification.Builder(context, "miunlock_tool", islandTitle)
            .addPicture(HyperPicture(PIC_KEY_BOLT, context, R.drawable.ic_notif_bolt))
            .setChatInfo(
                title = islandTitle,
                content = if (isRussian()) "Отправка..." else "Sending...",
                pictureKey = PIC_KEY_BOLT
            )
            .setSmallIsland(PIC_KEY_BOLT)
            .setBigIslandInfo(
                left = ImageTextInfoLeft(
                    type = 1,
                    picInfo = PicInfo(type = 1, pic = PIC_KEY_BOLT),
                    textInfo = TextInfo(title = islandTitle, content = subtitle)
                )
            )
            .setIslandConfig(priority = 1, dismissible = false)
            .setIslandFirstFloat(false)
            .setEnableFloat(false) // Never auto-expand for sending (transition from countdown)
            .setShowNotification(true)

        return buildHyperNotification(compatBuilder, hyperBuilder)
    }

    fun updateSending() {
        try {
            notificationManager.notify(NOTIFICATION_ID, buildSendingNotification())
        } catch (t: Throwable) {
            Log.e(TAG, "updateSending error", t)
        }
    }

    fun buildSuccessNotification(): Notification {
        val title = if (isRussian()) "Успех!" else "Success!"
        val subtitle = if (isRussian()) {
            "Все заявки получили код 0 (Успех)"
        } else {
            "All requests received code 0 (Success)"
        }
        val circleColor = Color.parseColor("#34C759") // Green for success

        val compatBuilder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notif_check)
            .setLargeIcon(createCircleBitmap(R.drawable.ic_notif_check, circleColor))
            .setContentTitle(title)
            .setContentText(subtitle)
            .setContentIntent(getPendingIntent())
            .setOngoing(false)
            .setAutoCancel(true)
            .setCategory(NotificationCompat.CATEGORY_STATUS)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)

        val islandTitle = "Xiaomi Unlock Tool"

        val hyperBuilder = HyperIslandNotification.Builder(context, "miunlock_tool", islandTitle)
            .addPicture(HyperPicture(PIC_KEY_CHECK, context, R.drawable.ic_notif_check))
            .setChatInfo(
                title = islandTitle,
                content = title,
                pictureKey = PIC_KEY_CHECK
            )
            .setSmallIsland(PIC_KEY_CHECK)
            .setBigIslandInfo(
                left = ImageTextInfoLeft(
                    type = 1,
                    picInfo = PicInfo(type = 1, pic = PIC_KEY_CHECK),
                    textInfo = TextInfo(title = islandTitle, content = title)
                )
            )
            .setIslandConfig(priority = 1, dismissible = true)
            .setIslandFirstFloat(false)
            .setEnableFloat(false) // Don't auto-expand for success
            .setShowNotification(true)

        return buildHyperNotification(compatBuilder, hyperBuilder)
    }

    fun updateSuccess() {
        try {
            notificationManager.notify(NOTIFICATION_ID, buildSuccessNotification())
        } catch (t: Throwable) {
            Log.e(TAG, "updateSuccess error", t)
        }
    }

    fun cancel() {
        try {
            notificationManager.cancel(NOTIFICATION_ID)
            isFirstPost = true // Reset for next session
        } catch (t: Throwable) {
            Log.e(TAG, "cancel error", t)
        }
    }
}
