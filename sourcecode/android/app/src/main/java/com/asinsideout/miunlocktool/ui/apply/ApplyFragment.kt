package com.asinsideout.miunlocktool.ui.apply

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
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
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.data.AccountStatus
import com.asinsideout.miunlocktool.data.ApplyResult
import com.asinsideout.miunlocktool.data.ExecutionMode
import com.asinsideout.miunlocktool.data.LogColorType
import com.asinsideout.miunlocktool.data.PreferencesManager
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
        setupTimingAndPing()
        setupModeSelector()
        setupActionButtons()
        observeSchedulerState()
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

    private fun setupTokenInput() {
        binding.etToken.setText(prefs.token)

        binding.etToken.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                prefs.token = s?.toString()?.trim() ?: ""
            }
            override fun afterTextChanged(s: Editable?) {}
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
            }
        }

        binding.btnClearToken.setOnClickListener {
            binding.etToken.setText("")
            prefs.token = ""
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
        val token = prefs.token
        if (token.isEmpty()) {
            Toast.makeText(requireContext(), R.string.toast_token_required, Toast.LENGTH_SHORT).show()
            return
        }

        binding.tvStatusSummary.text = getString(R.string.status_checking)
        binding.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_info_container))
        binding.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_info_container))

        lifecycleScope.launch {
            val result = apiService.checkAccountStatus(token)
            when (result.status) {
                AccountStatus.READY -> {
                    binding.tvStatusSummary.text = getString(R.string.status_ready)
                    binding.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_success_container))
                    binding.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_success_container))
                }
                AccountStatus.APPROVED -> {
                    binding.tvStatusSummary.text = getString(R.string.status_approved, result.deadline ?: "")
                    binding.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_info_container))
                    binding.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_info_container))
                }
                AccountStatus.BLOCKED -> {
                    binding.tvStatusSummary.text = getString(R.string.status_blocked, result.deadline ?: "")
                    binding.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_warning_container))
                    binding.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_warning_container))
                }
                AccountStatus.TOO_NEW -> {
                    binding.tvStatusSummary.text = getString(R.string.status_too_new)
                    binding.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_warning_container))
                    binding.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_warning_container))
                }
                AccountStatus.EXPIRED -> {
                    binding.tvStatusSummary.text = getString(R.string.status_expired)
                    binding.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.md_theme_light_errorContainer))
                    binding.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.md_theme_light_onErrorContainer))
                }
                AccountStatus.ERROR, AccountStatus.UNKNOWN -> {
                    binding.tvStatusSummary.text = getString(R.string.status_error, result.message)
                    binding.cardStatusBadge.setCardBackgroundColor(ContextCompat.getColor(requireContext(), R.color.status_warning_container))
                    binding.tvStatusSummary.setTextColor(ContextCompat.getColor(requireContext(), R.color.status_on_warning_container))
                }
                else -> {}
            }
        }
    }

    private fun setupTimingAndPing() {
        binding.btnSyncNtp.setOnClickListener {
            viewModel.syncNtp()
        }

        binding.btnMeasurePing.setOnClickListener {
            viewModel.measurePing()
        }

        // Trigger initial NTP sync
        viewModel.syncNtp()
    }

    private fun setupModeSelector() {
        if (prefs.executionMode == ExecutionMode.MANUAL.id) {
            binding.rbManual.isChecked = true
        } else {
            binding.rbAuto.isChecked = true
        }

        binding.rgModes.setOnCheckedChangeListener { _, checkedId ->
            val mode = if (checkedId == R.id.rb_manual) {
                ExecutionMode.MANUAL
            } else {
                ExecutionMode.AUTO
            }
            prefs.executionMode = mode.id
            updateActionButtonText()
        }
    }

    private fun setupActionButtons() {
        binding.btnAction.setOnClickListener {
            if (scheduler.isRunning.value) {
                viewModel.stopScheduler()
                Toast.makeText(requireContext(), R.string.toast_stopped, Toast.LENGTH_SHORT).show()
            } else {
                val token = prefs.token
                if (token.isEmpty()) {
                    Toast.makeText(requireContext(), R.string.toast_token_required, Toast.LENGTH_SHORT).show()
                    return@setOnClickListener
                }
                val mode = if (prefs.executionMode == ExecutionMode.MANUAL.id) {
                    ExecutionMode.MANUAL
                } else {
                    ExecutionMode.AUTO
                }
                viewModel.startScheduler(mode)
                if (mode == ExecutionMode.MANUAL) {
                    Toast.makeText(requireContext(), R.string.toast_burst_started, Toast.LENGTH_SHORT).show()
                } else {
                    Toast.makeText(requireContext(), R.string.toast_started, Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun updateActionButtonText() {
        val isRunning = scheduler.isRunning.value
        if (isRunning) {
            binding.btnAction.setText(R.string.btn_stop_auto)
            binding.btnAction.setIconResource(R.drawable.ic_delete)
        } else {
            val isManual = prefs.executionMode == ExecutionMode.MANUAL.id
            if (isManual) {
                binding.btnAction.setText(R.string.btn_send_now)
                binding.btnAction.setIconResource(R.drawable.ic_bolt)
            } else {
                binding.btnAction.setText(R.string.btn_start_auto)
                binding.btnAction.setIconResource(R.drawable.ic_bolt)
            }
        }
    }

    private fun observeSchedulerState() {
        lifecycleScope.launch {
            scheduler.clockBeijing.collect { timeStr ->
                binding.tvBeijingClock.text = timeStr
            }
        }

        lifecycleScope.launch {
            scheduler.countdown.collect { countdownStr ->
                binding.tvCountdown.text = countdownStr
            }
        }

        lifecycleScope.launch {
            scheduler.pingMs.collect { ping ->
                if (ping > 0) {
                    binding.tvPingValue.text = "${ping} ms"
                    val pingSec = ping / 1000.0
                    val sendSec = 60.0 - pingSec
                    binding.tvSendOffset.text = getString(R.string.send_offset_calc, String.format(Locale.US, "23:59:%.3f", sendSec))
                } else {
                    binding.tvPingValue.setText(R.string.ping_unmeasured)
                }
            }
        }

        lifecycleScope.launch {
            scheduler.isRunning.collect { running ->
                updateActionButtonText()
                binding.rgModes.isEnabled = !running
                binding.rbAuto.isEnabled = !running
                binding.rbManual.isEnabled = !running
            }
        }

        lifecycleScope.launch {
            viewModel.logs.collect { list ->
                logAdapter.setLogs(list)
                if (list.isNotEmpty()) {
                    binding.rvLogs.scrollToPosition(list.size - 1)
                }
            }
        }

        lifecycleScope.launch {
            scheduler.applyResultFlow.collect { result ->
                showResultDialog(result)
            }
        }
    }

    private fun showResultDialog(result: ApplyResult) {
        if (!isAdded) return

        if (result.isSuccess) {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle(R.string.dialog_success_title)
                .setMessage(R.string.dialog_success_msg)
                .setIcon(R.drawable.ic_check)
                .setPositiveButton(R.string.dialog_ok, null)
                .show()
        } else if (result.code == 0 && result.applyResult == 3) {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle(R.string.dialog_quota_title)
                .setMessage(getString(R.string.dialog_quota_msg, result.deadline ?: "Tomorrow"))
                .setPositiveButton(R.string.dialog_ok, null)
                .show()
        } else if (result.code == 100004 || result.code == 10004) {
            MaterialAlertDialogBuilder(requireContext())
                .setTitle(R.string.dialog_error_title)
                .setMessage(R.string.status_expired)
                .setPositiveButton(R.string.dialog_ok, null)
                .show()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        // Do NOT stop scheduler on tab switch
        _binding = null
    }
}

