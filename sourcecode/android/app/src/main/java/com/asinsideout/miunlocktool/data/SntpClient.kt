package com.asinsideout.miunlocktool.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.util.Calendar
import java.util.TimeZone

class SntpClient {

    var clockOffsetMs: Long = 0L
        private set

    var isSynchronized: Boolean = false
        private set

    companion object {
        private const val NTP_PORT = 123
        private const val NTP_PACKET_SIZE = 48
        private const val NTP_MODE_CLIENT = 3
        private const val NTP_VERSION = 3
        private const val OFFSET_1900_TO_1970 = 2208988800L
        private const val TIMEOUT_MS = 5000

        val BEIJING_TIMEZONE: TimeZone = TimeZone.getTimeZone("Asia/Shanghai")
    }

    suspend fun requestTime(host: String): Boolean = withContext(Dispatchers.IO) {
        var socket: DatagramSocket? = null
        try {
            val address = InetAddress.getByName(host)
            val buffer = ByteArray(NTP_PACKET_SIZE)
            buffer[0] = ((NTP_MODE_CLIENT or (NTP_VERSION shl 3))).toByte()

            val requestTime = System.currentTimeMillis()
            writeTimeStamp(buffer, 40, requestTime)

            socket = DatagramSocket()
            socket.soTimeout = TIMEOUT_MS

            val requestPacket = DatagramPacket(buffer, buffer.size, address, NTP_PORT)
            socket.send(requestPacket)

            val responsePacket = DatagramPacket(buffer, buffer.size)
            socket.receive(responsePacket)
            val responseTime = System.currentTimeMillis()

            val t0 = readTimeStamp(buffer, 24)
            val t1 = readTimeStamp(buffer, 32)
            val t2 = readTimeStamp(buffer, 40)
            val t3 = responseTime

            val offset = ((t1 - t0) + (t2 - t3)) / 2
            clockOffsetMs = offset
            isSynchronized = true
            true
        } catch (e: Exception) {
            false
        } finally {
            socket?.close()
        }
    }

    fun getSynchronizedTimeMs(): Long {
        return System.currentTimeMillis() + clockOffsetMs
    }

    fun getBeijingCalendar(): Calendar {
        val cal = Calendar.getInstance(BEIJING_TIMEZONE)
        cal.timeInMillis = getSynchronizedTimeMs()
        return cal
    }

    private fun writeTimeStamp(buffer: ByteArray, offset: Int, time: Long) {
        var seconds = time / 1000L
        val milliseconds = time - seconds * 1000L
        seconds += OFFSET_1900_TO_1970

        buffer[offset] = (seconds shr 24).toByte()
        buffer[offset + 1] = (seconds shr 16).toByte()
        buffer[offset + 2] = (seconds shr 8).toByte()
        buffer[offset + 3] = (seconds).toByte()

        val fraction = (milliseconds * 0x100000000L) / 1000L
        buffer[offset + 4] = (fraction shr 24).toByte()
        buffer[offset + 5] = (fraction shr 16).toByte()
        buffer[offset + 6] = (fraction shr 8).toByte()
        buffer[offset + 7] = (fraction).toByte()
    }

    private fun readTimeStamp(buffer: ByteArray, offset: Int): Long {
        val s0 = buffer[offset].toLong() and 0xFF
        val s1 = buffer[offset + 1].toLong() and 0xFF
        val s2 = buffer[offset + 2].toLong() and 0xFF
        val s3 = buffer[offset + 3].toLong() and 0xFF
        val seconds = (s0 shl 24) or (s1 shl 16) or (s2 shl 8) or s3

        val f0 = buffer[offset + 4].toLong() and 0xFF
        val f1 = buffer[offset + 5].toLong() and 0xFF
        val f2 = buffer[offset + 6].toLong() and 0xFF
        val f3 = buffer[offset + 7].toLong() and 0xFF
        val fraction = (f0 shl 24) or (f1 shl 16) or (f2 shl 8) or f3

        val ms = ((seconds - OFFSET_1900_TO_1970) * 1000L) + ((fraction * 1000L) / 0x100000000L)
        return ms
    }
}

