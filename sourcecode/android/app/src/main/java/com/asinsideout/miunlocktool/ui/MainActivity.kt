package com.asinsideout.miunlocktool.ui

import android.content.res.Configuration
import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.graphics.Color
import androidx.fragment.app.Fragment
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.lifecycleScope
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.databinding.ActivityMainBinding
import com.asinsideout.miunlocktool.ui.apply.ApplyFragment
import com.asinsideout.miunlocktool.ui.components.glass.LiquidGlassBottomNavigation
import com.asinsideout.miunlocktool.ui.guide.GuideFragment
import com.asinsideout.miunlocktool.ui.settings.SettingsFragment
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private val viewModel: MainViewModel by viewModels()

    private lateinit var applyFragment: ApplyFragment
    private lateinit var guideFragment: GuideFragment
    private lateinit var settingsFragment: SettingsFragment
    private lateinit var activeFragment: Fragment

    private var currentTag = TAG_APPLY
    private val selectedTabIndexState = mutableIntStateOf(0)
    private val languageChangeTrigger = mutableIntStateOf(0)

    companion object {
        private const val TAG_APPLY = "tag_apply"
        private const val TAG_GUIDE = "tag_guide"
        private const val TAG_SETTINGS = "tag_settings"
        private const val KEY_ACTIVE_TAG = "key_active_tag"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setSupportActionBar(binding.topAppBar)

        if (savedInstanceState == null) {
            applyFragment = ApplyFragment()
            guideFragment = GuideFragment()
            settingsFragment = SettingsFragment()
            currentTag = TAG_APPLY
            activeFragment = applyFragment

            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, settingsFragment, TAG_SETTINGS).hide(settingsFragment)
                .add(R.id.fragment_container, guideFragment, TAG_GUIDE).hide(guideFragment)
                .add(R.id.fragment_container, applyFragment, TAG_APPLY)
                .commit()
        } else {
            applyFragment = supportFragmentManager.findFragmentByTag(TAG_APPLY) as? ApplyFragment ?: ApplyFragment()
            guideFragment = supportFragmentManager.findFragmentByTag(TAG_GUIDE) as? GuideFragment ?: GuideFragment()
            settingsFragment = supportFragmentManager.findFragmentByTag(TAG_SETTINGS) as? SettingsFragment ?: SettingsFragment()

            currentTag = savedInstanceState.getString(KEY_ACTIVE_TAG, TAG_APPLY) ?: TAG_APPLY
            activeFragment = when (currentTag) {
                TAG_SETTINGS -> settingsFragment
                TAG_GUIDE -> guideFragment
                else -> applyFragment
            }

            supportFragmentManager.beginTransaction().apply {
                if (activeFragment == applyFragment) show(applyFragment) else hide(applyFragment)
                if (activeFragment == guideFragment) show(guideFragment) else hide(guideFragment)
                if (activeFragment == settingsFragment) show(settingsFragment) else hide(settingsFragment)
            }.commit()
        }

        selectedTabIndexState.intValue = getTabIndex(currentTag)

        setupNavigation()
        observeStylingChanges()
        applyStylingAndTheme()
        applyAllTranslations()
        checkNotificationPermission()
    }

    private fun checkNotificationPermission() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) != android.content.pm.PackageManager.PERMISSION_GRANTED) {
                requestPermissions(arrayOf(android.Manifest.permission.POST_NOTIFICATIONS), 101)
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString(KEY_ACTIVE_TAG, currentTag)
    }

    override fun onResume() {
        super.onResume()
        applyStylingAndTheme()
        applyAllTranslations()
    }

    fun applyAllTranslations() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        binding.topAppBar.title = tm.tr("app_name")
        languageChangeTrigger.intValue++

        if (::applyFragment.isInitialized && applyFragment.isAdded && applyFragment.view != null) applyFragment.applyTranslations()
        if (::guideFragment.isInitialized && guideFragment.isAdded && guideFragment.view != null) guideFragment.applyTranslations()
        if (::settingsFragment.isInitialized && settingsFragment.isAdded && settingsFragment.view != null) settingsFragment.applyTranslations()
    }

    private fun observeStylingChanges() {
        lifecycleScope.launch {
            viewModel.accentColor.collect {
                applyStylingAndTheme()
            }
        }
    }

    fun applyStylingAndTheme() {
        // Theme updates are reactive via ViewModel StateFlow and Jetpack Compose
    }

    private fun setupNavigation() {
        androidx.core.view.ViewCompat.setOnApplyWindowInsetsListener(binding.appBarLayout) { view, windowInsets ->
            val insets = windowInsets.getInsets(androidx.core.view.WindowInsetsCompat.Type.systemBars())
            view.setPadding(view.paddingLeft, insets.top, view.paddingRight, view.paddingBottom)
            windowInsets
        }
        binding.appBarLayout.requestApplyInsets()

        binding.composeBottomNavigation.setContent {
            @Suppress("UNUSED_VARIABLE")
            val lang = languageChangeTrigger.intValue
            val accentColorInt by viewModel.accentColor.collectAsStateWithLifecycle()
            val accentColor = remember(accentColorInt) { Color(accentColorInt) }
            val selectedIndex = selectedTabIndexState.intValue

            val onTabSelectedLambda: (Int) -> Unit = { index ->
                if (index != selectedTabIndexState.intValue) {
                    selectedTabIndexState.intValue = index
                    when (index) {
                        0 -> switchFragment(applyFragment, TAG_APPLY)
                        1 -> switchFragment(guideFragment, TAG_GUIDE)
                        2 -> switchFragment(settingsFragment, TAG_SETTINGS)
                    }
                }
            }

            LiquidGlassBottomNavigation(
                selectedTabIndex = selectedIndex,
                onTabSelected = onTabSelectedLambda,
                accentColor = accentColor
            )
        }
    }

    private fun getTabIndex(tag: String): Int {
        return when (tag) {
            TAG_APPLY -> 0
            TAG_GUIDE -> 1
            TAG_SETTINGS -> 2
            else -> 0
        }
    }

    private fun switchFragment(target: Fragment, targetTag: String) {
        if (target == activeFragment || targetTag == currentTag) return

        val currentIndex = getTabIndex(currentTag)
        val targetIndex = getTabIndex(targetTag)
        selectedTabIndexState.intValue = targetIndex
        val movingLeft = targetIndex < currentIndex

        val outgoingFragment = activeFragment
        val outgoingView = outgoingFragment.view
        val incomingView = target.view

        val containerWidth = binding.fragmentContainer.width.toFloat().takeIf { it > 0 }
            ?: resources.displayMetrics.widthPixels.toFloat()

        activeFragment = target
        currentTag = targetTag

        if (outgoingView == null || incomingView == null) {
            supportFragmentManager.beginTransaction()
                .hide(outgoingFragment)
                .show(target)
                .commitNowAllowingStateLoss()
            return
        }

        // Show incoming fragment and animate views
        supportFragmentManager.beginTransaction()
            .show(target)
            .commitNowAllowingStateLoss()

        val enterStart = if (movingLeft) -containerWidth else containerWidth
        val exitEnd = if (movingLeft) containerWidth else -containerWidth

        incomingView.translationX = enterStart
        incomingView.alpha = 1f
        outgoingView.translationX = 0f
        outgoingView.alpha = 1f

        val duration = 280L
        val interpolator = androidx.interpolator.view.animation.FastOutSlowInInterpolator()

        outgoingView.animate().cancel()
        incomingView.animate().cancel()

        outgoingView.animate()
            .translationX(exitEnd)
            .setDuration(duration)
            .setInterpolator(interpolator)
            .withEndAction {
                outgoingView.translationX = 0f
                if (activeFragment != outgoingFragment) {
                    supportFragmentManager.beginTransaction()
                        .hide(outgoingFragment)
                        .commitNowAllowingStateLoss()
                }
            }
            .start()

        incomingView.animate()
            .translationX(0f)
            .setDuration(duration)
            .setInterpolator(interpolator)
            .withEndAction {
                incomingView.translationX = 0f
            }
            .start()
    }
}
