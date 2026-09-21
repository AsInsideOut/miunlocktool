package com.asinsideout.miunlocktool.ui

import android.os.Bundle
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.asinsideout.miunlocktool.R
import com.asinsideout.miunlocktool.databinding.ActivityMainBinding
import com.asinsideout.miunlocktool.ui.apply.ApplyFragment
import com.asinsideout.miunlocktool.ui.guide.GuideFragment
import com.asinsideout.miunlocktool.ui.settings.SettingsFragment

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    val viewModel: MainViewModel by viewModels()

    private lateinit var applyFragment: ApplyFragment
    private lateinit var guideFragment: GuideFragment
    private lateinit var settingsFragment: SettingsFragment
    private lateinit var activeFragment: Fragment

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        if (savedInstanceState == null) {
            applyFragment = ApplyFragment()
            guideFragment = GuideFragment()
            settingsFragment = SettingsFragment()
            activeFragment = applyFragment

            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, settingsFragment, "settings").hide(settingsFragment)
                .add(R.id.fragment_container, guideFragment, "guide").hide(guideFragment)
                .add(R.id.fragment_container, applyFragment, "apply")
                .commit()
        } else {
            applyFragment = supportFragmentManager.findFragmentByTag("apply") as? ApplyFragment ?: ApplyFragment()
            guideFragment = supportFragmentManager.findFragmentByTag("guide") as? GuideFragment ?: GuideFragment()
            settingsFragment = supportFragmentManager.findFragmentByTag("settings") as? SettingsFragment ?: SettingsFragment()
            activeFragment = applyFragment
        }

        setupNavigation()
    }

    private fun setupNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.menu_apply -> {
                    switchFragment(applyFragment)
                    true
                }
                R.id.menu_guide -> {
                    switchFragment(guideFragment)
                    true
                }
                R.id.menu_settings -> {
                    switchFragment(settingsFragment)
                    true
                }
                else -> false
            }
        }
    }

    private fun switchFragment(target: Fragment) {
        if (target != activeFragment) {
            supportFragmentManager.beginTransaction()
                .hide(activeFragment)
                .show(target)
                .commit()
            activeFragment = target
        }
    }
}

