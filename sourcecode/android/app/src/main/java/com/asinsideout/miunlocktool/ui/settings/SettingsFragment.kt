package com.asinsideout.miunlocktool.ui.settings

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.res.ColorStateList
import android.content.res.Configuration
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Bundle
import android.text.Editable
import android.text.TextWatcher
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.FrameLayout
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.content.FileProvider
import androidx.core.os.LocaleListCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.google.android.material.progressindicator.LinearProgressIndicator
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.data.PreferencesManager
import com.asinsideout.miunlocktool.data.ThemeColorManager
import com.asinsideout.miunlocktool.databinding.FragmentSettingsBinding
import com.asinsideout.miunlocktool.ui.DownloadState
import com.asinsideout.miunlocktool.ui.MainActivity
import com.asinsideout.miunlocktool.ui.MainViewModel
import com.asinsideout.miunlocktool.ui.UpdateResult
import kotlinx.coroutines.launch
import java.io.File
import java.util.Locale

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
        setupAccentColorPicker()
        setupLanguageSelector()
        setupNtpSelector()
        setupTimingProfileSelector()
        setupBurstSliders()
        setupUpdateChecker()
        setupAboutAndLinks()
        applyTranslations()

    }

    override fun onResume() {
        super.onResume()
        applyTranslations()
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


    private fun setupAccentColorPicker() {
        // Initial preview swatch
        updateColorPreview(prefs.accentColor)
        binding.etCustomColor.setText(prefs.accentColorHex)

        // Populate preset circles
        populateColorPresets()

        // Realtime swatch preview when typing HEX
        binding.etCustomColor.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                val parsed = ThemeColorManager.parseColorHex(s?.toString())
                if (parsed != null) {
                    updateColorPreview(parsed)
                    binding.tilCustomColor.error = null
                }
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        // Apply custom color button
        binding.btnApplyColor.setOnClickListener {
            val input = binding.etCustomColor.text?.toString()?.trim() ?: ""
            val parsed = ThemeColorManager.parseColorHex(input)
            if (parsed != null) {
                binding.tilCustomColor.error = null
                val cleanHex = if (input.startsWith("#")) input.uppercase(Locale.ROOT) else "#${input.uppercase(Locale.ROOT)}"
                viewModel.setAccentColor(parsed, cleanHex)
                populateColorPresets()
                Toast.makeText(requireContext(), R.string.settings_color_applied, Toast.LENGTH_SHORT).show()
            } else {
                binding.tilCustomColor.error = getString(R.string.settings_invalid_hex)
            }
        }

        // Observe changes
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.accentColor.collect { color ->
                val isDark = when (resources.configuration.uiMode and Configuration.UI_MODE_NIGHT_MASK) {
                    Configuration.UI_MODE_NIGHT_YES -> true
                    else -> false
                }
                updateColorPreview(color)
                populateColorPresets()

                val radioCsl = ThemeColorManager.createRadioColorStateList(color, isDark)
                // Theme radio buttons
                binding.rbThemeLight.buttonTintList = radioCsl
                binding.rbThemeDark.buttonTintList = radioCsl
                binding.rbThemeSystem.buttonTintList = radioCsl


                // Language radio buttons
                binding.rbLangEn.buttonTintList = radioCsl
                binding.rbLangRu.buttonTintList = radioCsl
                binding.rbLangUk.buttonTintList = radioCsl
                binding.rbLangEs.buttonTintList = radioCsl
                binding.rbLangPt.buttonTintList = radioCsl
                binding.rbLangId.buttonTintList = radioCsl
                binding.rbLangZh.buttonTintList = radioCsl

                // NTP radio buttons
                binding.rbNtpGoogle.buttonTintList = radioCsl
                binding.rbNtpAndroid.buttonTintList = radioCsl
                binding.rbNtpCloudflare.buttonTintList = radioCsl

                // Timing profile radio buttons
                binding.rbProfileEurope.buttonTintList = radioCsl
                binding.rbProfileAsia.buttonTintList = radioCsl
                binding.rbProfileUsaAfrica.buttonTintList = radioCsl
                binding.rbProfileCustom.buttonTintList = radioCsl

                // Sliders
                val accentCsl = ColorStateList.valueOf(color)
                binding.sliderBurstCount.thumbTintList = accentCsl
                binding.sliderBurstCount.trackActiveTintList = accentCsl
                binding.sliderBurstInterval.thumbTintList = accentCsl
                binding.sliderBurstInterval.trackActiveTintList = accentCsl

                // Buttons
                ThemeColorManager.applyPrimaryButtonStyle(binding.btnCheckUpdate, color)
                ThemeColorManager.applyPrimaryButtonStyle(binding.btnApplyColor, color)
                binding.btnCopyWallet.iconTint = accentCsl
                binding.btnCopyWallet.setTextColor(color)

                // Section Headers
                binding.tvSectionAppearance.setTextColor(color)
                binding.tvSectionLanguage.setTextColor(color)
                binding.tvSectionNetwork.setTextColor(color)
                binding.tvSectionTimingProfile.setTextColor(color)
                binding.tvSectionTiming.setTextColor(color)
                binding.tvSectionUpdates.setTextColor(color)
                binding.tvSectionAbout.setTextColor(color)

                // Links & Menu items
                binding.tvLinkTg.setTextColor(color)
                binding.tvLink4pda.setTextColor(color)
                binding.tvLinkGithub.setTextColor(color)
                binding.tvLinkWeb.setTextColor(color)
                binding.tvLinkDonateDa.setTextColor(color)

                // Input outline tint
                binding.tilCustomColor.boxStrokeColor = color
                binding.tilCustomColor.hintTextColor = accentCsl
                binding.tilCustomTimings.boxStrokeColor = color
                binding.tilCustomTimings.hintTextColor = accentCsl
            }
        }
    }

    private fun updateColorPreview(color: Int) {
        val density = resources.displayMetrics.density
        val drawable = GradientDrawable().apply {
            shape = GradientDrawable.OVAL
            setColor(color)
            setStroke((2 * density).toInt(), Color.parseColor("#4DFFFFFF"))
        }
        binding.viewColorPreview.background = drawable
    }

    private fun populateColorPresets() {
        val density = resources.displayMetrics.density
        binding.layoutColorPresets.removeAllViews()

        val currentColor = prefs.accentColor

        for (preset in ThemeColorManager.PRESETS) {
            val frame = FrameLayout(requireContext()).apply {
                val size = (42 * density).toInt()
                layoutParams = LinearLayout.LayoutParams(size, size).apply {
                    marginEnd = (10 * density).toInt()
                }
            }

            val circle = View(requireContext()).apply {
                val circleSize = (38 * density).toInt()
                layoutParams = FrameLayout.LayoutParams(circleSize, circleSize, Gravity.CENTER)
                val bg = GradientDrawable().apply {
                    shape = GradientDrawable.OVAL
                    setColor(preset.color)
                    val strokeColor = if (preset.color == currentColor) Color.WHITE else Color.parseColor("#4DFFFFFF")
                    val strokeWidth = if (preset.color == currentColor) (2.5f * density).toInt() else (1.5f * density).toInt()
                    setStroke(strokeWidth, strokeColor)
                }
                background = bg
            }
            frame.addView(circle)

            if (preset.color == currentColor) {
                val checkIcon = ImageView(requireContext()).apply {
                    val iconSize = (20 * density).toInt()
                    layoutParams = FrameLayout.LayoutParams(iconSize, iconSize, Gravity.CENTER)
                    setImageResource(R.drawable.ic_check)
                    imageTintList = ColorStateList.valueOf(ThemeColorManager.getContrastOnColor(preset.color))
                }
                frame.addView(checkIcon)
            }

            frame.setOnClickListener {
                viewModel.setAccentColor(preset.color, preset.hex)
                binding.etCustomColor.setText(preset.hex)
                binding.tilCustomColor.error = null
                Toast.makeText(requireContext(), R.string.settings_color_applied, Toast.LENGTH_SHORT).show()
            }

            binding.layoutColorPresets.addView(frame)
        }
    }

    private fun setupLanguageSelector() {
        when (prefs.language) {
            PreferencesManager.LANG_RU -> binding.rbLangRu.isChecked = true
            PreferencesManager.LANG_UK -> binding.rbLangUk.isChecked = true
            PreferencesManager.LANG_UK -> binding.rbLangUk.isChecked = true
            PreferencesManager.LANG_ES -> binding.rbLangEs.isChecked = true
            PreferencesManager.LANG_PT -> binding.rbLangPt.isChecked = true
            PreferencesManager.LANG_ID -> binding.rbLangId.isChecked = true
            PreferencesManager.LANG_ZH -> binding.rbLangZh.isChecked = true
            else -> binding.rbLangEn.isChecked = true
        }

        binding.rbLangEn.setOnClickListener { selectLanguage(PreferencesManager.LANG_EN) }
        binding.rbLangRu.setOnClickListener { selectLanguage(PreferencesManager.LANG_RU) }
        binding.rbLangUk.setOnClickListener { selectLanguage(PreferencesManager.LANG_UK) }
        binding.rbLangEs.setOnClickListener { selectLanguage(PreferencesManager.LANG_ES) }
        binding.rbLangPt.setOnClickListener { selectLanguage(PreferencesManager.LANG_PT) }
        binding.rbLangId.setOnClickListener { selectLanguage(PreferencesManager.LANG_ID) }
        binding.rbLangZh.setOnClickListener { selectLanguage(PreferencesManager.LANG_ZH) }
    }

    private fun updateLocaleConfiguration(targetLang: String) {
        try {
            val locale = Locale.forLanguageTag(targetLang)
            Locale.setDefault(locale)
            val res = resources
            val config = res.configuration
            config.setLocale(locale)
            @Suppress("DEPRECATION")
            res.updateConfiguration(config, res.displayMetrics)
        } catch (_: Exception) {}
    }

    private fun selectLanguage(targetLang: String) {
        if (prefs.language == targetLang) return

        if (targetLang == PreferencesManager.LANG_EN || targetLang == PreferencesManager.LANG_RU || targetLang == PreferencesManager.LANG_UK) {
            lifecycleScope.launch {
                com.asinsideout.miunlocktool.data.TranslationManager.setLanguage(requireContext(), targetLang)
                prefs.language = targetLang
                updateLocaleConfiguration(targetLang)
                (activity as? MainActivity)?.applyAllTranslations()
                applyTranslations()
            }
            return
        }

        // External language: download if needed
        val langName = com.asinsideout.miunlocktool.data.TranslationManager.getLanguageDisplayName(targetLang)
        val progressDialog = MaterialAlertDialogBuilder(requireContext())
            .setTitle(com.asinsideout.miunlocktool.data.TranslationManager.tr("settings_section_language"))
            .setMessage(com.asinsideout.miunlocktool.data.TranslationManager.tr("downloading_language_pack", langName))
            .setCancelable(false)
            .create()
        progressDialog.show()

        lifecycleScope.launch {
            val result = com.asinsideout.miunlocktool.data.TranslationManager.setLanguage(requireContext(), targetLang)
            progressDialog.dismiss()
            if (result.isSuccess) {
                prefs.language = targetLang
                updateLocaleConfiguration(targetLang)
                (activity as? MainActivity)?.applyAllTranslations()
                applyTranslations()
                Toast.makeText(
                    requireContext(),
                    com.asinsideout.miunlocktool.data.TranslationManager.tr("language_pack_downloaded"),
                    Toast.LENGTH_SHORT
                ).show()
            } else {
                Toast.makeText(
                    requireContext(),
                    com.asinsideout.miunlocktool.data.TranslationManager.tr("language_pack_error"),
                    Toast.LENGTH_LONG
                ).show()
                // Revert selection
                when (prefs.language) {
                    PreferencesManager.LANG_RU -> binding.rbLangRu.isChecked = true
                    PreferencesManager.LANG_ES -> binding.rbLangEs.isChecked = true
                    PreferencesManager.LANG_PT -> binding.rbLangPt.isChecked = true
                    PreferencesManager.LANG_ID -> binding.rbLangId.isChecked = true
                    PreferencesManager.LANG_ZH -> binding.rbLangZh.isChecked = true
                    else -> binding.rbLangEn.isChecked = true
                }
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

    private fun setupTimingProfileSelector() {
        when (prefs.timingProfile) {
            PreferencesManager.PROFILE_ASIA -> binding.rbProfileAsia.isChecked = true
            PreferencesManager.PROFILE_USA_AFRICA -> binding.rbProfileUsaAfrica.isChecked = true
            PreferencesManager.PROFILE_CUSTOM -> {
                binding.rbProfileCustom.isChecked = true
                binding.tilCustomTimings.visibility = View.VISIBLE
            }
            else -> binding.rbProfileEurope.isChecked = true
        }

        binding.etCustomTimings.setText(prefs.customTimings)
        binding.etCustomTimings.addTextChangedListener(object : TextWatcher {
            override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
            override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
                prefs.customTimings = s?.toString()?.trim() ?: ""
            }
            override fun afterTextChanged(s: Editable?) {}
        })

        binding.rgTimingProfile.setOnCheckedChangeListener { _, checkedId ->
            val profile = when (checkedId) {
                R.id.rb_profile_asia -> PreferencesManager.PROFILE_ASIA
                R.id.rb_profile_usa_africa -> PreferencesManager.PROFILE_USA_AFRICA
                R.id.rb_profile_custom -> PreferencesManager.PROFILE_CUSTOM
                else -> PreferencesManager.PROFILE_EUROPE
            }
            prefs.timingProfile = profile
            binding.tilCustomTimings.visibility = if (profile == PreferencesManager.PROFILE_CUSTOM) View.VISIBLE else View.GONE
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
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        _binding?.tvBurstCountLabel?.text = "${tm.tr("settings_burst_count")}: $count"
    }

    private fun updateBurstIntervalLabel(interval: Long) {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        _binding?.tvBurstIntervalLabel?.text = "${tm.tr("settings_burst_interval")}: ${interval} ms"
    }

    fun applyTranslations() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        _binding?.let { b ->
            b.tvSettingsTitle.text = tm.tr("settings_title")
            b.tvSectionAppearance.text = tm.tr("settings_section_appearance")
            b.tvThemeTitle.text = tm.tr("settings_theme")
            b.tvAccentColorTitle.text = tm.tr("settings_accent_color")

            b.rbThemeLight.text = tm.tr("settings_theme_light")
            b.rbThemeDark.text = tm.tr("settings_theme_dark")
            b.rbThemeSystem.text = tm.tr("settings_theme_system")


            b.tilCustomColor.hint = tm.tr("settings_color_hex_hint")
            b.btnApplyColor.text = tm.tr("settings_apply_color")

            b.tvSectionLanguage.text = tm.tr("settings_section_language")
            b.rbLangEn.text = tm.tr("settings_lang_en")
            b.rbLangRu.text = tm.tr("settings_lang_ru")
            b.rbLangUk.text = tm.tr("settings_lang_uk")
            b.rbLangEs.text = tm.tr("settings_lang_es")
            b.rbLangPt.text = tm.tr("settings_lang_pt")
            b.rbLangId.text = tm.tr("settings_lang_id")
            b.rbLangZh.text = tm.tr("settings_lang_zh")

            b.tvSectionNetwork.text = tm.tr("settings_section_network")
            b.rbNtpGoogle.text = tm.tr("settings_ntp_google")
            b.rbNtpAndroid.text = tm.tr("settings_ntp_android")
            b.rbNtpCloudflare.text = tm.tr("settings_ntp_cloudflare")

            b.tvSectionTimingProfile.text = tm.tr("settings_section_timing_profile")
            b.rbProfileEurope.text = tm.tr("settings_profile_europe")
            b.rbProfileAsia.text = tm.tr("settings_profile_asia")
            b.rbProfileUsaAfrica.text = tm.tr("settings_profile_usa_africa")
            b.rbProfileCustom.text = tm.tr("settings_profile_custom")
            b.tilCustomTimings.hint = tm.tr("settings_custom_timings_hint")

            b.tvSectionTiming.text = tm.tr("settings_section_timing")
            updateBurstCountLabel(prefs.burstCount)
            updateBurstIntervalLabel(prefs.burstIntervalMs)

            b.tvSectionUpdates.text = tm.tr("settings_section_updates")
            b.btnCheckUpdate.text = tm.tr("btn_check_update")

            b.tvSectionAbout.text = tm.tr("settings_section_about")
            b.tvAboutText.text = tm.tr("settings_about_text")
            b.tvAuthorsDevsTitle.text = tm.tr("authors_devs_title")
            b.tvAuthorsDevsBody.text = tm.tr("authors_devs_body")
            b.tvAuthorsSocialTitle.text = tm.tr("authors_social_title")
            b.tvLinkTg.text = tm.tr("authors_link_tg")
            b.tvLink4pda.text = tm.tr("authors_link_4pda")
            b.tvLinkGithub.text = tm.tr("authors_link_github")
            b.tvLinkWeb.text = tm.tr("authors_link_web")
            b.tvAuthorsDonateTitle.text = tm.tr("authors_donate_title")
            b.tvLinkDonateDa.text = tm.tr("authors_donate_da")
            b.tvAuthorsDonateCrypto.text = tm.tr("authors_donate_crypto")
            b.tvWalletAddress.text = tm.tr("authors_wallet_address")
            b.btnCopyWallet.text = tm.tr("copy_address_btn")
        }
    }

    private fun setupAboutAndLinks() {
        binding.tvLinkTg.setOnClickListener {
            openUrl("https://t.me/miunlocktoolrevamp")
        }
        binding.tvLink4pda.setOnClickListener {
            openUrl("https://4pda.to/forum/index.php?showtopic=721838&view=findpost&p=145201115")
        }
        binding.tvLinkGithub.setOnClickListener {
            openUrl("https://github.com/AsInsideOut/miunlocktool")
        }
        binding.tvLinkWeb.setOnClickListener {
            val isRu = prefs.language == PreferencesManager.LANG_RU ||
                    (prefs.language == PreferencesManager.LANG_SYSTEM && java.util.Locale.getDefault().language.lowercase().startsWith("ru"))
            val siteUrl = if (isRu) "https://miunlocktool.ru/" else "https://miunlock.su/"
            openUrl(siteUrl)
        }
        binding.tvLinkDonateDa.setOnClickListener {
            openUrl("https://dalink.to/asinsideout")
        }
        binding.btnCopyWallet.setOnClickListener {
            val tm = com.asinsideout.miunlocktool.data.TranslationManager
            val wallet = tm.tr("authors_wallet_address")
            val clipboard = requireContext().getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
            val clip = ClipData.newPlainText("USDT TON Wallet", wallet)
            clipboard.setPrimaryClip(clip)
            Toast.makeText(requireContext(), tm.tr("authors_wallet_copied"), Toast.LENGTH_SHORT).show()
        }
    }

    private fun openUrl(url: String) {
        try {
            val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
            startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(requireContext(), "Could not open link: ${e.message}", Toast.LENGTH_SHORT).show()
        }
    }

    private var downloadDialog: AlertDialog? = null
    private var downloadProgressBar: LinearProgressIndicator? = null
    private var downloadStatusText: TextView? = null

    private fun showDownloadDialog() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        val context = requireContext()
        val layout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            val pad = (20 * resources.displayMetrics.density).toInt()
            setPadding(pad, pad, pad, pad)
        }

        downloadStatusText = TextView(context).apply {
            text = tm.tr("update_downloading", 0)
            setTextAppearance(com.google.android.material.R.style.TextAppearance_Material3_BodyMedium)
        }
        layout.addView(downloadStatusText)

        downloadProgressBar = LinearProgressIndicator(context).apply {
            isIndeterminate = false
            max = 100
            progress = 0
            val lp = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            ).apply {
                topMargin = (12 * resources.displayMetrics.density).toInt()
            }
            layoutParams = lp
            val accent = prefs.accentColor
            setIndicatorColor(accent)
        }
        layout.addView(downloadProgressBar)

        downloadDialog = MaterialAlertDialogBuilder(context)
            .setTitle(tm.tr("update_available_title"))
            .setView(layout)
            .setCancelable(false)
            .setNegativeButton(tm.tr("update_cancel_btn")) { dialog, _ ->
                viewModel.resetDownloadState()
                dialog.dismiss()
                downloadDialog = null
            }
            .create()
        downloadDialog?.show()
    }

    private fun installApk(context: Context, apkFile: File) {
        try {
            val uri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                apkFile
            )
            val intent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(uri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            }
            context.startActivity(intent)
        } catch (e: Exception) {
            Toast.makeText(context, "Cannot open APK: ${e.message}", Toast.LENGTH_LONG).show()
        }
    }

    private fun setupUpdateChecker() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        binding.btnCheckUpdate.setOnClickListener {
            viewModel.checkForUpdates()
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.updateState.collect { state ->
                val b = _binding ?: return@collect
                when (state) {
                    is UpdateResult.Idle -> {
                        b.btnCheckUpdate.isEnabled = true
                        b.btnCheckUpdate.text = tm.tr("btn_check_update")
                    }
                    is UpdateResult.Checking -> {
                        b.btnCheckUpdate.isEnabled = false
                        b.btnCheckUpdate.text = tm.tr("update_checking")
                    }
                    is UpdateResult.UpdateAvailable -> {
                        b.btnCheckUpdate.isEnabled = true
                        b.btnCheckUpdate.text = tm.tr("btn_check_update")

                        MaterialAlertDialogBuilder(requireContext())
                            .setTitle(tm.tr("update_available_title"))
                            .setMessage(tm.tr("update_available_msg", state.remoteVersion, state.currentVersion))
                            .setPositiveButton(tm.tr("update_download_btn")) { _, _ ->
                                showDownloadDialog()
                                viewModel.downloadUpdate(requireContext())
                            }
                            .setNegativeButton(tm.tr("update_cancel_btn"), null)
                            .show()

                        viewModel.resetUpdateState()
                    }
                    is UpdateResult.UpToDate -> {
                        b.btnCheckUpdate.isEnabled = true
                        b.btnCheckUpdate.text = tm.tr("btn_check_update")

                        MaterialAlertDialogBuilder(requireContext())
                            .setTitle(tm.tr("update_latest_title"))
                            .setMessage(tm.tr("update_latest_msg", state.version))
                            .setPositiveButton(tm.tr("dialog_ok"), null)
                            .show()

                        viewModel.resetUpdateState()
                    }
                    is UpdateResult.Error -> {
                        b.btnCheckUpdate.isEnabled = true
                        b.btnCheckUpdate.text = tm.tr("btn_check_update")

                        MaterialAlertDialogBuilder(requireContext())
                            .setTitle(tm.tr("update_error_title"))
                            .setMessage(tm.tr("update_error_msg", state.message))
                            .setPositiveButton(tm.tr("dialog_ok"), null)
                            .show()

                        viewModel.resetUpdateState()
                    }
                }
            }
        }

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.downloadState.collect { state ->
                when (state) {
                    is DownloadState.Idle -> {
                        downloadDialog?.dismiss()
                        downloadDialog = null
                    }
                    is DownloadState.Progress -> {
                        if (downloadDialog == null || !downloadDialog!!.isShowing) {
                            showDownloadDialog()
                        }
                        if (state.totalBytes > 0) {
                            downloadProgressBar?.isIndeterminate = false
                            downloadProgressBar?.progress = state.percent
                            downloadStatusText?.text = tm.tr("update_downloading", state.percent)
                        } else {
                            downloadProgressBar?.isIndeterminate = true
                            downloadStatusText?.text = tm.tr("update_checking")
                        }
                    }
                    is DownloadState.Success -> {
                        downloadDialog?.dismiss()
                        downloadDialog = null
                        Toast.makeText(requireContext(), tm.tr("update_installing"), Toast.LENGTH_SHORT).show()
                        installApk(requireContext(), state.apkFile)
                        viewModel.resetDownloadState()
                    }
                    is DownloadState.Error -> {
                        downloadDialog?.dismiss()
                        downloadDialog = null
                        MaterialAlertDialogBuilder(requireContext())
                            .setTitle(tm.tr("update_error_title"))
                            .setMessage(tm.tr("update_download_error", state.message))
                            .setPositiveButton(tm.tr("dialog_ok"), null)
                            .show()
                        viewModel.resetDownloadState()
                    }
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        downloadDialog?.dismiss()
        downloadDialog = null
        _binding = null
    }
}
