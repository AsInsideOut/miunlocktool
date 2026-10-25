package com.asinsideout.miunlocktool.ui.guide

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.activityViewModels
import androidx.lifecycle.lifecycleScope
import com.asinsideout.miunlocktool.databinding.FragmentGuideBinding
import com.asinsideout.miunlocktool.ui.MainViewModel
import kotlinx.coroutines.launch

class GuideFragment : Fragment() {

    private var _binding: FragmentGuideBinding? = null
    private val binding get() = _binding!!
    private val viewModel: MainViewModel by activityViewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentGuideBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        applyTranslations()

        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.accentColor.collect { color ->
                binding.tvStep1Title.setTextColor(color)
                binding.tvStep2Title.setTextColor(color)
                binding.tvStep3Title.setTextColor(color)
                binding.tvStep4Title.setTextColor(color)
            }
        }
    }



    override fun onResume() {
        super.onResume()
        applyTranslations()
    }

    fun applyTranslations() {
        val tm = com.asinsideout.miunlocktool.data.TranslationManager
        _binding?.let { b ->
            b.tvGuideTitle.text = tm.tr("guide_title")
            b.tvStep1Title.text = tm.tr("guide_step1_title")
            b.tvStep1Body.text = tm.tr("guide_step1_body")
            b.tvStep2Title.text = tm.tr("guide_step2_title")
            b.tvStep2Body.text = tm.tr("guide_step2_body")
            b.tvStep3Title.text = tm.tr("guide_step3_title")
            b.tvStep3Body.text = tm.tr("guide_step3_body")
            b.tvStep4Title.text = tm.tr("guide_step4_title")
            b.tvStep4Body.text = tm.tr("guide_step4_body")
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

