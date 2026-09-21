package com.asinsideout.miunlocktool.ui.settings

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.data.PreferencesManager
import com.asinsideout.miunlocktool.databinding.FragmentSettingsBinding
import com.asinsideout.miunlocktool.ui.MainViewModel
import com.asinsideout.miunlocktool.ui.UpdateResult
import kotlinx.coroutines.launch

class SettingsFragment : Fragment() {

    private var _binding: FragmentSettingsBinding? = null
    private val binding get() = _binding!!

    private val viewModel: MainViewModel by activityViewModels()
    private val prefs: PreferencesManager get() = viewModel.prefs

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSettingsBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupThemeSelector()
        setupLanguageSelector()
        setupNtpSelector()
        setupBurstSliders()
        setupUpdateChecker()
    }

    private fun setupThemeSelector() {
        when (prefs.themeMode) {
            PreferencesManager.THEME_LIGHT -> binding.rbThemeLight.isChecked = true
            PreferencesManager.THEME_DARK -> binding.rbThemeDark.isChecked = true
            else -> binding.rbThemeSystem.isChecked = true
        }

        binding.rgTheme.setOnCheckedChangeListener { _, checkedId ->
            val mode = when (checkedId) {
                R.id.rb_theme_light -> PreferencesManager.THEME_LIGHT
                R.id.rb_theme_dark -> PreferencesManager.THEME_DARK
                else -> PreferencesManager.THEME_SYSTEM
            }
            if (prefs.themeMode != mode) {
                prefs.themeMode = mode
                AppCompatDelegate.setDefaultNightMode(mode)
            }
        }
    }

    private fun setupLanguageSelector() {
        if (prefs.language == PreferencesManager.LANG_RU) {
            binding.rbLangRu.isChecked = true
        } else {
            binding.rbLangEn.isChecked = true
        }

        binding.rbLangEn.setOnClickListener {
            if (prefs.language != PreferencesManager.LANG_EN) {
                prefs.language = PreferencesManager.LANG_EN
                val appLocale = LocaleListCompat.forLanguageTags(PreferencesManager.LANG_EN)
                AppCompatDelegate.setApplicationLocales(appLocale)
            }
        }

        binding.rbLangRu.setOnClickListener {
            if (prefs.language != PreferencesManager.LANG_RU) {
                prefs.language = PreferencesManager.LANG_RU
                val appLocale = LocaleListCompat.forLanguageTags(PreferencesManager.LANG_RU)
                AppCompatDelegate.setApplicationLocales(appLocale)
            }
        }
    }

    private fun setupNtpSelector() {
        when (prefs.ntpServer) {
            "time.android.com" -> binding.rbNtpAndroid.isChecked = true
            "time.cloudflare.com" -> binding.rbNtpCloudflare.isChecked = true
            else -> binding.rbNtpGoogle.isChecked = true
        }

        binding.rgNtp.setOnCheckedChangeListener { _, checkedId ->
            val server = when (checkedId) {
                R.id.rb_ntp_android -> "time.android.com"
                R.id.rb_ntp_cloudflare -> "time.cloudflare.com"
                else -> "time.google.com"
            }
            prefs.ntpServer = server
        }
    }

    private fun setupBurstSliders() {
        // Burst Count
        binding.sliderBurstCount.value = prefs.burstCount.toFloat().coerceIn(5f, 50f)
        updateBurstCountLabel(prefs.burstCount)
        binding.sliderBurstCount.addOnChangeListener { _, value, fromUser ->
            if (fromUser) {
                val count = value.toInt()
                prefs.burstCount = count
                updateBurstCountLabel(count)
            }
        }

        // Burst Interval
        binding.sliderBurstInterval.value = prefs.burstIntervalMs.toFloat().coerceIn(25f, 500f)
        updateBurstIntervalLabel(prefs.burstIntervalMs)
        binding.sliderBurstInterval.addOnChangeListener { _, value, fromUser ->
            if (fromUser) {
                val interval = value.toLong()
                prefs.burstIntervalMs = interval
                updateBurstIntervalLabel(interval)
            }
        }
    }

    private fun updateBurstCountLabel(count: Int) {
        binding.tvBurstCountLabel.text = "${getString(R.string.settings_burst_count)}: $count"
    }

    private fun updateBurstIntervalLabel(interval: Long) {
        binding.tvBurstIntervalLabel.text = "${getString(R.string.settings_burst_interval)}: ${interval} ms"
    }

    private fun setupUpdateChecker() {
        binding.btnCheckUpdate.setOnClickListener {
            viewModel.checkForUpdates()
        }

        lifecycleScope.launch {
            viewModel.updateState.collect { state ->
                when (state) {
                    is UpdateResult.Idle -> {
                        binding.btnCheckUpdate.isEnabled = true
                        binding.btnCheckUpdate.setText(R.string.btn_check_update)
                    }
                    is UpdateResult.Checking -> {
                        binding.btnCheckUpdate.isEnabled = false
                        binding.btnCheckUpdate.setText(R.string.update_checking)
                    }
                    is UpdateResult.UpdateAvailable -> {
                        binding.btnCheckUpdate.isEnabled = true
                        binding.btnCheckUpdate.setText(R.string.btn_check_update)

                        MaterialAlertDialogBuilder(requireContext())
                            .setTitle(R.string.update_available_title)
                            .setMessage(getString(R.string.update_available_msg, state.remoteVersion, state.currentVersion))
                            .setPositiveButton(R.string.update_download_btn) { _, _ ->
                                val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse(state.url))
                                startActivity(browserIntent)
                            }
                            .setNegativeButton(R.string.update_cancel_btn, null)
                            .show()

                        viewModel.resetUpdateState()
                    }
                    is UpdateResult.UpToDate -> {
                        binding.btnCheckUpdate.isEnabled = true
                        binding.btnCheckUpdate.setText(R.string.btn_check_update)

                        MaterialAlertDialogBuilder(requireContext())
                            .setTitle(R.string.update_latest_title)
                            .setMessage(getString(R.string.update_latest_msg, state.version))
                            .setPositiveButton(R.string.dialog_ok, null)
                            .show()

                        viewModel.resetUpdateState()
                    }
                    is UpdateResult.Error -> {
                        binding.btnCheckUpdate.isEnabled = true
                        binding.btnCheckUpdate.setText(R.string.btn_check_update)

                        MaterialAlertDialogBuilder(requireContext())
                            .setTitle(R.string.update_error_title)
                            .setMessage(getString(R.string.update_error_msg, state.message))
                            .setPositiveButton(R.string.dialog_ok, null)
                            .show()

                        viewModel.resetUpdateState()
                    }
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

