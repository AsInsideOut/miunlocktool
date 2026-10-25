package com.asinsideout.miunlocktool.ui.apply

import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.content.res.ColorStateList
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.lifecycle.lifecycleScope
import com.google.android.material.bottomsheet.BottomSheetDialogFragment
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.data.AuthPollResult
import com.asinsideout.miunlocktool.data.AuthSessionInfo
import com.asinsideout.miunlocktool.data.PreferencesManager
import com.asinsideout.miunlocktool.data.ThemeColorManager
import com.asinsideout.miunlocktool.data.XiaomiAuthManager
import com.asinsideout.miunlocktool.databinding.BottomSheetXiaomiAuthBinding
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

class XiaomiAuthBottomSheet : BottomSheetDialogFragment() {

    private var _binding: BottomSheetXiaomiAuthBinding? = null
    private val binding get() = _binding!!

    private val authManager = XiaomiAuthManager()
    private var currentSession: AuthSessionInfo? = null
    private var pollingJob: Job? = null
    private var isAuthCompleted = false

    var onTokenExtracted: ((String) -> Unit)? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = BottomSheetXiaomiAuthBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        applyTranslations()
        applyAccentColor()
        setupListeners()
        startSession()
    }

    private fun applyTranslations() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        binding.tvAuthTitle.text = tm.tr("login_title")
        binding.tvAuthSubtitle.text = tm.tr("login_subtitle")
        binding.tvAuthScanTip.text = tm.tr("login_qr_scan_tip")
        binding.btnOpenBrowser.text = tm.tr("login_open_browser_btn")
        binding.btnRefreshQr.text = tm.tr("login_refresh_qr")
        binding.btnClose.text = tm.tr("close_btn")
        binding.tvAuthStatus.text = tm.tr("login_loading_qr")
    }

    private fun applyAccentColor() {
        val accentColor = PreferencesManager(requireContext()).accentColor
        binding.ivAuthShield.imageTintList = ColorStateList.valueOf(accentColor)
        ThemeColorManager.applyPrimaryButtonStyle(binding.btnOpenBrowser, accentColor)
        ThemeColorManager.applyTonalButtonStyle(binding.btnRefreshQr, accentColor)
        ThemeColorManager.applyOutlinedButtonStyle(binding.btnClose, accentColor)
        binding.progressAuth.setIndicatorColor(accentColor)
        binding.pbQrLoading.indeterminateTintList = ColorStateList.valueOf(accentColor)
    }

    private fun setupListeners() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        binding.btnClose.setOnClickListener {
            dismiss()
        }

        binding.btnRefreshQr.setOnClickListener {
            binding.tvAuthStatus.text = tm.tr("login_refreshing_qr")
            binding.pbQrLoading.visibility = View.VISIBLE
            binding.ivQrCode.setImageBitmap(null)
            startSession()
        }

        binding.btnOpenBrowser.setOnClickListener {
            val loginUrl = currentSession?.loginUrl
            if (!loginUrl.isNullOrEmpty()) {
                try {
                    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(loginUrl))
                    startActivity(intent)
                    binding.tvAuthStatus.text = tm.tr("login_browser_opened")
                } catch (e: Exception) {
                    binding.tvAuthStatus.text = tm.tr("login_error", e.localizedMessage ?: "Unknown")
                }
            }
        }
    }

    private fun startSession() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        pollingJob?.cancel()
        binding.progressAuth.visibility = View.VISIBLE

        viewLifecycleOwner.lifecycleScope.launch {
            val result = authManager.initiateAuth()
            if (result.isSuccess) {
                val session = result.getOrNull()!!
                currentSession = session
                loadQrCode(session.qrUrl)
                startPolling(session.lpUrl)
            } else {
                val errorMsg = result.exceptionOrNull()?.localizedMessage ?: "Network error"
                binding.tvAuthStatus.text = tm.tr("login_qr_fetch_error", errorMsg)
                binding.pbQrLoading.visibility = View.GONE
                binding.progressAuth.visibility = View.GONE
            }
        }
    }

    private suspend fun loadQrCode(qrUrl: String) {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        if (qrUrl.isEmpty()) {
            binding.pbQrLoading.visibility = View.GONE
            return
        }

        val bitmap: Bitmap? = authManager.fetchQrBitmap(qrUrl)
        if (_binding != null) {
            binding.pbQrLoading.visibility = View.GONE
            if (bitmap != null) {
                binding.ivQrCode.setImageBitmap(bitmap)
                binding.tvAuthStatus.text = tm.tr("login_waiting")
            } else {
                binding.tvAuthStatus.text = tm.tr("login_qr_fetch_error", "Image download failed")
            }
        }
    }

    private fun startPolling(lpUrl: String) {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        pollingJob?.cancel()
        pollingJob = viewLifecycleOwner.lifecycleScope.launch {
            var retryCount = 0
            while (isActive && !isAuthCompleted && retryCount < 100) {
                val pollResult = authManager.pollOnce(lpUrl)
                if (!isActive) break

                when (pollResult) {
                    is AuthPollResult.Success -> {
                        handleSuccess(pollResult.token)
                        return@launch
                    }
                    is AuthPollResult.Status -> {
                        retryCount++
                    }
                    is AuthPollResult.Error -> {
                        retryCount++
                        delay(2000)
                    }
                    is AuthPollResult.Expired -> {
                        binding.tvAuthStatus.text = tm.tr("login_qr_expired")
                        return@launch
                    }
                }
            }
        }
    }

    private fun handleSuccess(token: String) {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        if (isAuthCompleted) return
        isAuthCompleted = true
        pollingJob?.cancel()

        if (_binding != null) {
            binding.tvAuthStatus.text = tm.tr("login_success")
            binding.progressAuth.visibility = View.GONE
        }

        onTokenExtracted?.invoke(token)

        viewLifecycleOwner.lifecycleScope.launch {
            delay(800)
            dismiss()
        }
    }

    override fun onDestroyView() {
        pollingJob?.cancel()
        super.onDestroyView()
        _binding = null
    }

    companion object {
        const val TAG = "XiaomiAuthBottomSheet"

        fun newInstance(): XiaomiAuthBottomSheet {
            return XiaomiAuthBottomSheet()
        }
    }
}

