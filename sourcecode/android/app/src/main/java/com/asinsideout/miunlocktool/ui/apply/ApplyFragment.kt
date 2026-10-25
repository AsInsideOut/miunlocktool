package com.asinsideout.miunlocktool.ui.apply

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.res.ColorStateList
import android.content.res.Configuration
import android.graphics.Color
import android.net.Uri
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import android.content.BroadcastReceiver
import android.content.IntentFilter
import android.hardware.usb.UsbDevice
import android.hardware.usb.UsbManager
import android.os.Build
import com.asinsideout.miunlocktool.fastboot.FastbootConnectionState
import com.asinsideout.miunlocktool.fastboot.FastbootUsbTransport
import com.asinsideout.miunlocktool.data.TranslationManager
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.data.AccountStatus
import com.asinsideout.miunlocktool.data.ApplyResult
import com.asinsideout.miunlocktool.data.ExecutionMode
import com.asinsideout.miunlocktool.data.LogColorType
import com.asinsideout.miunlocktool.data.PreferencesManager
import com.asinsideout.miunlocktool.data.ThemeColorManager
import com.asinsideout.miunlocktool.data.XiaomiApiService
import com.asinsideout.miunlocktool.databinding.FragmentApplyBinding
import com.asinsideout.miunlocktool.service.ApplyScheduler
import com.asinsideout.miunlocktool.ui.MainViewModel
import com.asinsideout.miunlocktool.ui.components.LogAdapter
import kotlinx.coroutines.launch
import java.util.Locale

class ApplyFragment : Fragment() {

    private var _binding: FragmentApplyBinding? = null
    private val binding get() = _binding!!

    private val viewModel: MainViewModel by activityViewModels()

    private val prefs: PreferencesManager get() = viewModel.prefs
    private val apiService: XiaomiApiService get() = viewModel.apiService
    private val scheduler: ApplyScheduler get() = viewModel.scheduler
    private lateinit var logAdapter: LogAdapter
    private var lastStatusResult: com.asinsideout.miunlocktool.data.CheckStatusResult? = null

    private val usbReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            val action = intent?.action ?: return
            when (action) {
                FastbootUsbTransport.ACTION_USB_PERMISSION -> {
                    val device = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        intent.getParcelableExtra(UsbManager.EXTRA_DEVICE, UsbDevice::class.java)
                    } else {
                        @Suppress("DEPRECATION")
                        intent.getParcelableExtra(UsbManager.EXTRA_DEVICE)
                    }
                    val granted = intent.getBooleanExtra(UsbManager.EXTRA_PERMISSION_GRANTED, false)
                    viewModel.onUsbPermissionResult(granted, device)
                }
                UsbManager.ACTION_USB_DEVICE_ATTACHED -> {
                    context?.let { viewModel.checkAndConnectFastboot(it) }
                }
                UsbManager.ACTION_USB_DEVICE_DETACHED -> {
                    viewModel.disconnectFastboot()
                }
            }
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentApplyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupLogRecyclerView()
        setupTokenInput()
        setupFastbootOtgCard()
        setupTimingAndPing()
        setupActionButtons()
        observeSchedulerState()
        applyTranslations()
    }



    override fun onStart() {
        super.onStart()
        val filter = IntentFilter().apply {
            addAction(FastbootUsbTransport.ACTION_USB_PERMISSION)
            addAction(UsbManager.ACTION_USB_DEVICE_ATTACHED)
            addAction(UsbManager.ACTION_USB_DEVICE_DETACHED)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            requireContext().registerReceiver(usbReceiver, filter, Context.RECEIVER_EXPORTED)
        } else {
            requireContext().registerReceiver(usbReceiver, filter)
        }
    }

    override fun onStop() {
        super.onStop()
        try {
            requireContext().unregisterReceiver(usbReceiver)
        } catch (_: Exception) {}
    }

    override fun onResume() {
        super.onResume()
        applyTranslations()
    }

    private fun renderStatus(result: com.asinsideout.miunlocktool.data.CheckStatusResult?) {
        val b = _binding ?: return
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        if (result == null) {
            b.tvStatusSummary.text = tm.tr("status_not_checked")
            b.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_info_container))
            b.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_info_container))
            return
        }

        when (result.status) {
            AccountStatus.READY -> {
                b.tvStatusSummary.text = tm.tr("status_ready")
                b.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_success_container))
                b.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_success_container))
            }
            AccountStatus.APPROVED -> {
                b.tvStatusSummary.text = tm.tr("status_approved", result.deadline ?: "")
                b.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_info_container))
                b.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_info_container))
            }
            AccountStatus.BLOCKED -> {
                b.tvStatusSummary.text = tm.tr("status_blocked", result.deadline ?: "")
                b.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_warning_container))
                b.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_warning_container))
            }
            AccountStatus.TOO_NEW -> {
                b.tvStatusSummary.text = tm.tr("status_too_new")
                b.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_warning_container))
                b.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_warning_container))
            }
            AccountStatus.EXPIRED -> {
                b.tvStatusSummary.text = tm.tr("status_expired")
                b.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.md_theme_light_errorContainer))
                b.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.md_theme_light_onErrorContainer))
            }
            AccountStatus.ERROR, AccountStatus.UNKNOWN -> {
                b.tvStatusSummary.text = tm.tr("status_error", result.message)
                b.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_warning_container))
                b.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_warning_container))
            }
            else -> {}
        }
    }

    fun applyTranslations() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        _binding?.let { b ->
            b.tvTokenTitle.text = tm.tr("section_token")
            b.btnLogin.text = tm.tr("login_btn")
            b.tilToken.hint = tm.tr("token_hint")
            b.btnPaste.text = tm.tr("token_paste")
            b.btnClearToken.text = tm.tr("token_clear")
            b.btnCheckStatus.text = tm.tr("token_check_status")

            renderStatus(lastStatusResult)

            b.tvClockTitle.text = tm.tr("beijing_time_title")
            b.btnSyncNtp.text = tm.tr("btn_sync_ntp")
            b.tvCountdownLabel.text = tm.tr("beijing_countdown_title")

            b.tvLogTitle.text = tm.tr("log_title")
            b.btnCopyLog.text = tm.tr("log_copy")
            b.btnClearLog.text = tm.tr("log_clear")

            if (scheduler.isRunning.value) {
                b.btnAction.text = tm.tr("btn_stop_auto")
            } else {
                b.btnAction.text = tm.tr("btn_start_auto")
            }

            if (scheduler.pingMs.value <= 0) {
                b.tvPingValue.text = tm.tr("ping_unmeasured")
            }

            b.tvFastbootTitle.text = tm.tr("fastboot_title")
            b.btnFastbootConnect.text = tm.tr("fastboot_btn_connect")
            b.btnFastbootDisconnect.text = tm.tr("fastboot_btn_disconnect")
            b.btnFastbootGetProduct.text = tm.tr("fastboot_btn_get_product")
            b.btnFastbootGetToken.text = tm.tr("fastboot_btn_get_token")

            updateTimingProfileDisplay()
        }
    }

    private fun updateTimingProfileDisplay() {
        val b = _binding ?: return
        val profileName = when (prefs.timingProfile) {
            PreferencesManager.PROFILE_ASIA -> "Asia"
            PreferencesManager.PROFILE_USA_AFRICA -> "USA / Africa"
            PreferencesManager.PROFILE_CUSTOM -> "Custom"
            else -> "Europe"
        }
        val timings = prefs.getActiveTimings()
        val timingsStr = timings.take(4).joinToString(", ") { String.format(Locale.US, "%.3f", it) } +
                (if (timings.size > 4) "..." else "")
        b.tvSendOffset.text = "$profileName ($timingsStr)"
    }

    private fun setupFastbootOtgCard() {
        val b = _binding ?: return

        b.btnFastbootConnect.setOnClickListener {
            viewModel.checkAndConnectFastboot(requireContext())
        }

        b.btnFastbootDisconnect.setOnClickListener {
            viewModel.disconnectFastboot()
        }

        b.btnFastbootGetProduct.setOnClickListener {
            viewModel.fetchFastbootProduct()
        }

        b.btnFastbootGetToken.setOnClickListener {
            viewModel.fetchFastbootToken()
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.fastbootDeviceState.collect { state ->
                val tm = TranslationManager
                when (state) {
                    FastbootConnectionState.NO_DEVICE -> {
                        b.tvFastbootStatusBadge.text = tm.tr("fastboot_status_disconnected")
                        b.tvFastbootStatusBadge.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_info_container))
                        b.tvFastbootStatusBadge.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_info_container))
                        b.btnFastbootConnect.isEnabled = true
                        b.btnFastbootDisconnect.isEnabled = false
                        b.btnFastbootGetProduct.isEnabled = false
                        b.btnFastbootGetToken.isEnabled = false
                    }
                    FastbootConnectionState.DEVICE_ATTACHED, FastbootConnectionState.PERMISSION_REQUIRED -> {
                        b.tvFastbootStatusBadge.text = tm.tr("fastboot_status_permission_required")
                        b.tvFastbootStatusBadge.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_warning_container))
                        b.tvFastbootStatusBadge.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_warning_container))
                        b.btnFastbootConnect.isEnabled = true
                        b.btnFastbootDisconnect.isEnabled = false
                        b.btnFastbootGetProduct.isEnabled = false
                        b.btnFastbootGetToken.isEnabled = false
                    }
                    FastbootConnectionState.CONNECTING -> {
                        b.tvFastbootStatusBadge.text = "Connecting..."
                        b.tvFastbootStatusBadge.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_info_container))
                        b.tvFastbootStatusBadge.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_info_container))
                        b.btnFastbootConnect.isEnabled = false
                        b.btnFastbootDisconnect.isEnabled = true
                        b.btnFastbootGetProduct.isEnabled = false
                        b.btnFastbootGetToken.isEnabled = false
                    }
                    FastbootConnectionState.CONNECTED -> {
                        b.tvFastbootStatusBadge.text = tm.tr("fastboot_status_connected", "OK")
                        b.tvFastbootStatusBadge.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_success_container))
                        b.tvFastbootStatusBadge.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_success_container))
                        b.btnFastbootConnect.isEnabled = false
                        b.btnFastbootDisconnect.isEnabled = true
                        b.btnFastbootGetProduct.isEnabled = true
                        b.btnFastbootGetToken.isEnabled = true
                    }
                    FastbootConnectionState.DISCONNECTED -> {
                        b.tvFastbootStatusBadge.text = tm.tr("fastboot_status_disconnected")
                        b.tvFastbootStatusBadge.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_info_container))
                        b.tvFastbootStatusBadge.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_info_container))
                        b.btnFastbootConnect.isEnabled = true
                        b.btnFastbootDisconnect.isEnabled = false
                        b.btnFastbootGetProduct.isEnabled = false
                        b.btnFastbootGetToken.isEnabled = false
                    }
                    FastbootConnectionState.ERROR -> {
                        b.tvFastbootStatusBadge.text = "Error"
                        b.tvFastbootStatusBadge.setBackgroundColor(ContextCompat.getColor(requireContext(), R.color.md_theme_light_errorContainer))
                        b.tvFastbootStatusBadge.setTextColor(ContextCompat.getColor(requireContext(), R.color.md_theme_light_onErrorContainer))
                        b.btnFastbootConnect.isEnabled = true
                        b.btnFastbootDisconnect.isEnabled = false
                        b.btnFastbootGetProduct.isEnabled = false
                        b.btnFastbootGetToken.isEnabled = false
                    }
                }
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.fastbootDeviceInfoText.collect { text ->
                b.tvFastbootDeviceInfo.text = text
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.fastbootProduct.collect { prod ->
                b.tvFastbootProduct.text = if (prod != null) {
                    TranslationManager.tr("fastboot_product_label", prod)
                } else {
                    "Product: --"
                }
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.fastbootToken.collect { token ->
                b.tvFastbootToken.text = if (token != null) {
                    TranslationManager.tr("fastboot_token_label", token)
                } else {
                    "Token: --"
                }
            }
        }
    }

    private fun setupLogRecyclerView() {
        logAdapter = LogAdapter()
        binding.rvLogs.apply {
            layoutManager = LinearLayoutManager(requireContext()).apply {
                stackFromEnd = true
            }
            adapter = logAdapter
        }

        binding.btnClearLog.setOnClickListener {
            viewModel.clearLogs()
        }

        binding.btnCopyLog.setOnClickListener {
            val text = logAdapter.getAllLogsText()
            if (text.isNotEmpty()) {
                val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                val clip = ClipData.newPlainText("HyperApply Logs", text)
                clipboard.setPrimaryClip(clip)
                Toast.makeText(requireContext(), R.string.log_copied, Toast.LENGTH_SHORT).show()
            }
        }
    }

    private var lastEasterEgg: String? = null

    private fun checkEasterEgg(text: String): Boolean {
        val clean = text.trim().lowercase(Locale.ROOT)
        if (clean in EASTER_EGG_KEYWORDS) {
            lastEasterEgg = clean
            openEasterEggUrl()
            return true
        }
        return false
    }

    private fun openEasterEggUrl() {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(EASTER_EGG_URL))
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(requireContext(), "Could not open browser", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupTokenInput() {
        binding.etToken.setText(prefs.token)
        lastEasterEgg = prefs.token.trim().lowercase(Locale.ROOT)

        binding.etToken.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                prefs.token = s?.toString()?.trim() ?: ""
            }
            override fun afterTextChanged(s: Editable?) {
                val clean = s?.toString()?.trim()?.lowercase(Locale.ROOT) ?: ""
                if (clean in EASTER_EGG_KEYWORDS) {
                    if (clean != lastEasterEgg) {
                        checkEasterEgg(clean)
                    }
                } else {
                    lastEasterEgg = null
                }
            }
        })

        binding.btnLogin.setOnClickListener {
            openLoginBottomSheet()
        }

        binding.btnPaste.setOnClickListener {
            val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val item = clipboard.primaryClip?.getItemAt(0)
            val pasteData = item?.text?.toString()?.trim() ?: ""
            if (pasteData.isNotEmpty()) {
                binding.etToken.setText(pasteData)
                prefs.token = pasteData
                checkEasterEgg(pasteData)
            }
        }

        binding.btnClearToken.setOnClickListener {
            binding.etToken.setText("")
            prefs.token = ""
            lastEasterEgg = null
        }

        binding.btnCheckStatus.setOnClickListener {
            checkAccountStatus()
        }
    }

    private fun openLoginBottomSheet() {
        val sheet = XiaomiAuthBottomSheet.newInstance()
        sheet.onTokenExtracted = { token ->
            binding.etToken.setText(token)
            prefs.token = token
            val masked = if (token.length > 14) "${token.take(8)}...${token.takeLast(6)}" else "***"
            viewModel.addLog(
                getString(R.string.login_success) + " ($masked)",
                LogColorType.GREEN
            )
            Toast.makeText(requireContext(), R.string.login_success, Toast.LENGTH_SHORT).show()
            checkAccountStatus()
        }
        sheet.show(parentFragmentManager, XiaomiAuthBottomSheet.TAG)
    }

    private fun checkAccountStatus() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        val token = prefs.token
        if (checkEasterEgg(token)) {
            return
        }
        if (token.isEmpty()) {
            Toast.makeText(requireContext(), tm.tr("toast_token_required"), Toast.LENGTH_SHORT).show()
            return
        }

        binding.tvStatusSummary.text = tm.tr("status_checking")
        binding.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_info_container))
        binding.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_info_container))

        lifecycleScope.launch {
            val result = apiService.checkAccountStatus(token)
            lastStatusResult = result
            renderStatus(result)
        }
    }

    private fun setupTimingAndPing() {
        binding.btnSyncNtp.setOnClickListener {
            viewModel.syncNtp()
        }

        // Trigger initial NTP sync and automatic ping check
        viewModel.syncNtp()
        viewModel.measurePing()
    }

    private fun setupActionButtons() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        binding.btnAction.setOnClickListener {
            try {
                if (scheduler.isRunning.value) {
                    viewModel.stopScheduler()
                    Toast.makeText(requireContext(), tm.tr("toast_stopped"), Toast.LENGTH_SHORT).show()
                } else {
                    val token = prefs.token
                    if (checkEasterEgg(token)) {
                        return@setOnClickListener
                    }
                    if (token.isEmpty()) {
                        Toast.makeText(requireContext(), tm.tr("toast_token_required"), Toast.LENGTH_SHORT).show()
                        return@setOnClickListener
                    }
                    prefs.executionMode = ExecutionMode.AUTO.id
                    viewModel.startScheduler(ExecutionMode.AUTO)
                    Toast.makeText(requireContext(), tm.tr("toast_started"), Toast.LENGTH_SHORT).show()
                }
            } catch (t: Throwable) {
                Toast.makeText(requireContext(), "Error: ${t.localizedMessage ?: t.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun updateActionButtonText() {
        val b = _binding ?: return
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        val isRunning = scheduler.isRunning.value
        if (isRunning) {
            b.btnAction.text = tm.tr("btn_stop_auto")
            b.btnAction.setIconResource(R.drawable.ic_delete)
            b.btnAction.backgroundTintList = ColorStateList.valueOf(Color.parseColor("#B00020"))
            b.btnAction.setTextColor(Color.WHITE)
            b.btnAction.iconTint = ColorStateList.valueOf(Color.WHITE)
        } else {
            b.btnAction.text = tm.tr("btn_start_auto")
            b.btnAction.setIconResource(R.drawable.ic_bolt)
            val color = prefs.accentColor
            b.btnAction.backgroundTintList = ColorStateList.valueOf(color)
            val textColor = ThemeColorManager.getContrastOnColor(color)
            b.btnAction.setTextColor(textColor)
            b.btnAction.iconTint = ColorStateList.valueOf(textColor)
        }
    }

    private fun observeSchedulerState() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        viewLifecycleOwner.lifecycleScope.launch {
            scheduler.clockBeijing.collect { timeStr ->
                _binding?.tvBeijingClock?.text = timeStr
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            scheduler.countdown.collect { countdownStr ->
                _binding?.tvCountdown?.text = countdownStr
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            scheduler.pingDetailed.collect { res ->
                val b = _binding ?: return@collect
                if (res != null && res.averageMs > 0) {
                    b.tvPingValue.text = "HTTP: ${res.httpPingMs} ms | TCP: ${res.tcpPingMs} ms"
                    val pingSec = res.averageMs / 1000.0
                    val sendSec = 60.0 - pingSec
                    b.tvSendOffset.text = tm.tr(
                        "send_offset_calc",
                        String.format(Locale.US, "23:59:%.3f (Avg %d ms)", sendSec, res.averageMs)
                    )
                } else {
                    val singlePing = scheduler.pingMs.value
                    if (singlePing > 0) {
                        b.tvPingValue.text = "${singlePing} ms"
                        val pingSec = singlePing / 1000.0
                        val sendSec = 60.0 - pingSec
                        b.tvSendOffset.text = tm.tr(
                            "send_offset_calc",
                            String.format(Locale.US, "23:59:%.3f", sendSec)
                        )
                    } else {
                        b.tvPingValue.text = tm.tr("ping_unmeasured")
                    }
                }
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            scheduler.isRunning.collect {
                updateActionButtonText()
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.logs.collect { list ->
                val b = _binding ?: return@collect
                logAdapter.setLogs(list)
                if (list.isNotEmpty()) {
                    b.rvLogs.scrollToPosition(list.size - 1)
                }
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            scheduler.applyResultFlow.collect { result ->
                showResultDialog(result)
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.accentColor.collect { color ->
                val b = _binding ?: return@collect

                // 1. Primary Action Buttons
                if (!scheduler.isRunning.value) {
                    ThemeColorManager.applyPrimaryButtonStyle(b.btnAction, color)
                }
                ThemeColorManager.applyPrimaryButtonStyle(b.btnCheckStatus, color)
                ThemeColorManager.applyPrimaryButtonStyle(b.btnLogin, color)

                // 2. Tonal Buttons (Paste, Sync NTP)
                ThemeColorManager.applyTonalButtonStyle(b.btnPaste, color)
                ThemeColorManager.applyTonalButtonStyle(b.btnSyncNtp, color)

                // 3. Outlined Buttons (Clear)
                ThemeColorManager.applyOutlinedButtonStyle(b.btnClearToken, color)

                // 4. Icons & Large Beijing Clock Text
                b.ivClockIcon.imageTintList = ColorStateList.valueOf(color)
                b.ivPingIcon.imageTintList = ColorStateList.valueOf(color)
                b.tvBeijingClock.setTextColor(color)

                // 5. Token Input Box Focus Tint
                b.tilToken.boxStrokeColor = color
                b.tilToken.hintTextColor = ColorStateList.valueOf(color)

                // 6. Fastboot Buttons & Icons
                ThemeColorManager.applyTonalButtonStyle(b.btnFastbootConnect, color)
                ThemeColorManager.applyOutlinedButtonStyle(b.btnFastbootDisconnect, color)
                ThemeColorManager.applyTonalButtonStyle(b.btnFastbootGetProduct, color)
                ThemeColorManager.applyTonalButtonStyle(b.btnFastbootGetToken, color)
                b.ivFastbootIcon.imageTintList = ColorStateList.valueOf(color)
            }
        }
    }

    private fun showResultDialog(result: ApplyResult) {
        if (!isAdded) return
        val tm = com.asinsideout.miunlocktool.data.TranslationManager

        if (result.isSuccess) {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle(tm.tr("dialog_success_title"))
                .setMessage(tm.tr("dialog_success_msg"))
                .setIcon(R.drawable.ic_check)
                .setPositiveButton(tm.tr("dialog_ok"), null)
                .show()
        } else if (result.isStatusUnavailable) {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle(tm.tr("dialog_status_unavailable_title"))
                .setMessage(tm.tr("dialog_status_unavailable_msg"))
                .setIcon(R.drawable.ic_apply)
                .setPositiveButton(tm.tr("dialog_ok"), null)
                .show()
        } else if (result.code == 0 && result.applyResult == 3) {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle(tm.tr("dialog_quota_title"))
                .setMessage(tm.tr("dialog_quota_msg"))
                .setIcon(R.drawable.ic_check)
                .setPositiveButton(tm.tr("dialog_ok"), null)
                .show()
        } else if (result.code == 100004 || result.code == 10004) {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle(tm.tr("dialog_error_title"))
                .setMessage(tm.tr("status_expired"))
                .setPositiveButton(tm.tr("dialog_ok"), null)
                .show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Do NOT stop scheduler on tab switch
        _binding = null
    }

    companion object {
        private const val EASTER_EGG_URL = "https://miunlock.su/edro/unitedrussia.mp4"
        private val EASTER_EGG_KEYWORDS = setOf(
            "united russia",
            "edro",
            "единая россия",
            "едро"
        )
    }
}

