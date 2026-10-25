package com.asinsideout.miunlocktool.unlock

import android.util.Base64
import org.json.JSONObject
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import javax.crypto.Cipher
import javax.crypto.Mac
import javax.crypto.spec.IvParameterSpec
import javax.crypto.spec.SecretKeySpec

object MiUnlockCrypto {

    val FIXED_IV = "0102030405060708".toByteArray(StandardCharsets.UTF_8)
    val SIGN_KEY = "2tBeoEyJTunmWUGq7bQH2Abn0k2NhhurOaqBfyxCuLVgn4AVj7swcawe53uDUno".toByteArray(StandardCharsets.UTF_8)

    fun aesCbcEncrypt(data: ByteArray, key: ByteArray, iv: ByteArray = FIXED_IV): ByteArray {
        val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
        val secretKey = SecretKeySpec(key, "AES")
        val ivSpec = IvParameterSpec(iv)
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, ivSpec)
        return cipher.doFinal(data)
    }

    fun aesCbcDecrypt(cipherText: ByteArray, key: ByteArray, iv: ByteArray = FIXED_IV): ByteArray {
        val cipher = Cipher.getInstance("AES/CBC/PKCS5Padding")
        val secretKey = SecretKeySpec(key, "AES")
        val ivSpec = IvParameterSpec(iv)
        cipher.init(Cipher.DECRYPT_MODE, secretKey, ivSpec)
        return cipher.doFinal(cipherText)
    }

    fun hmacSha1(key: ByteArray, message: ByteArray): ByteArray {
        val mac = Mac.getInstance("HmacSHA1")
        val secretKey = SecretKeySpec(key, "HmacSHA1")
        mac.init(secretKey)
        return mac.doFinal(message)
    }

    fun sha1(data: ByteArray): ByteArray {
        val md = MessageDigest.getInstance("SHA-1")
        return md.digest(data)
    }

    fun md5Hex(input: String): String {
        val md = MessageDigest.getInstance("MD5")
        val digest = md.digest(input.toByteArray(StandardCharsets.UTF_8))
        return bytesToHex(digest)
    }

    fun bytesToHex(bytes: ByteArray): String {
        val sb = StringBuilder(bytes.size * 2)
        for (b in bytes) {
            sb.append(String.format("%02x", b))
        }
        return sb.toString()
    }

    fun hexToBytes(hex: String): ByteArray {
        val clean = hex.trim()
        val len = clean.length
        val data = ByteArray(len / 2)
        var i = 0
        while (i < len) {
            data[i / 2] = ((Character.digit(clean[i], 16) shl 4) +
                    Character.digit(clean[i + 1], 16)).toByte()
            i += 2
        }
        return data
    }

    /**
     * Encrypts and signs request parameters exactly matching MiUnlockTool's utils._send.
     */
    fun prepareEncryptedParams(
        path: String,
        paramsRaw: MutableMap<String, String>,
        ssecurity: String
    ): Map<String, String> {
        val ssecurityKey = Base64.decode(ssecurity, Base64.DEFAULT)
        paramsRaw["sid"] = "miui_unlocktool_client"

        val paramOrder = paramsRaw.keys.sorted()
        val signParams = paramOrder.joinToString("&") { k -> "$k=${paramsRaw[k]}" }
        val signStr = "POST\n$path\n$signParams"

        val signHashHex = bytesToHex(hmacSha1(SIGN_KEY, signStr.toByteArray(StandardCharsets.UTF_8)))
        val currentSign = Base64.encodeToString(
            aesCbcEncrypt(signHashHex.toByteArray(StandardCharsets.UTF_8), ssecurityKey, FIXED_IV),
            Base64.NO_WRAP
        )

        val encodedParams = mutableListOf<String>()
        val postParams = mutableMapOf<String, String>()

        for (k in paramOrder) {
            val v = paramsRaw[k] ?: ""
            val encryptedBytes = aesCbcEncrypt(v.toByteArray(StandardCharsets.UTF_8), ssecurityKey, FIXED_IV)
            val encryptedBase64 = Base64.encodeToString(encryptedBytes, Base64.NO_WRAP)
            encodedParams.add("$k=$encryptedBase64")
            postParams[k] = encryptedBase64
        }

        encodedParams.add("sign=$currentSign")
        encodedParams.add(ssecurity)

        val sha1Input = "POST&$path&${encodedParams.joinToString("&")}"
        val signature = Base64.encodeToString(
            sha1(sha1Input.toByteArray(StandardCharsets.UTF_8)),
            Base64.NO_WRAP
        )

        postParams["sign"] = currentSign
        postParams["signature"] = signature

        return postParams
    }

    /**
     * Decrypts Xiaomi API response body according to utils._send specification.
     */
    fun decryptApiResponse(responseBody: String, ssecurity: String): Result<JSONObject> {
        return try {
            val trimmed = responseBody.trim()
            if (trimmed.isEmpty()) {
                return Result.failure(IllegalStateException("Empty response body"))
            }

            val ssecurityKey = Base64.decode(ssecurity, Base64.DEFAULT)
            val encryptedBytes = Base64.decode(trimmed, Base64.DEFAULT)
            val decryptedBytes = aesCbcDecrypt(encryptedBytes, ssecurityKey, FIXED_IV)

            // Inner payload is base64-encoded JSON string
            val innerBase64Str = String(decryptedBytes, StandardCharsets.UTF_8)
            val innerJsonBytes = Base64.decode(innerBase64Str, Base64.DEFAULT)
            val jsonStr = String(innerJsonBytes, StandardCharsets.UTF_8)

            val json = JSONObject(jsonStr)
            Result.success(json)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
