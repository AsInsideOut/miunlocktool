# -*- coding: utf-8 -*-
"""
Dialog for configuring submission timings with 15 editable timing slots.
Allows choosing and custom-editing millisecond offsets around 23:59:59 (UTC+8).
Compact Material 3 design with high-contrast dark palette.
"""

import customtkinter as ctk

try:
    from theme import MaterialColors, MD3Card, MD3Label, MD3Button
except ImportError:
    try:
        from .theme import MaterialColors, MD3Card, MD3Label, MD3Button
    except ImportError:
        from res.theme import MaterialColors, MD3Card, MD3Label, MD3Button

# 3 Региональных профиля для скрипта (без стикеров)
TIMING_PROFILES = {
    'europe': {
        'id': 'europe',
        'name_ru': 'Европейский',
        'name_en': 'Europe',
        'timings': [58.700, 58.800, 59.100, 59.300, 59.500, 59.800],
        'region': 'Europe',
        'icon': ''
    },
    'asia': {
        'id': 'asia',
        'name_ru': 'Азиатский',
        'name_en': 'Asia',
        'timings': [58.800, 59.100, 59.300, 59.500, 59.700],
        'region': 'Asia',
        'icon': ''
    },
    'usa_africa': {
        'id': 'usa_africa',
        'name_ru': 'США / Африка',
        'name_en': 'USA / Africa',
        'timings': [58.500, 58.800, 59.100, 59.300, 59.500, 59.700],
        'region': 'America',
        'icon': ''
    }
}

# 15 таймингов по умолчанию (миллисекундная точность .3f)
DEFAULT_15_TIMINGS = [
    58.500, 58.700, 58.800, 59.000, 59.100,
    59.200, 59.300, 59.400, 59.500, 59.600,
    59.700, 59.800, 59.850, 59.900, 59.950
]

DEFAULT_AUTO_TIMINGS = [58.700, 58.800, 59.100, 59.300, 59.500, 59.800]
ALL_AVAILABLE_TIMINGS = DEFAULT_15_TIMINGS
MIN_SELECTED_TIMINGS = 1

# Темная цветовая палитра
CARD_BG = "#222228"
CARD_BG_ELEVATED = "#2C2B34"
CARD_BORDER = "#3E3D48"
TEXT_HEADER = "#FFFFFF"
TEXT_BODY = "#E2E8F0"
COLOR_PRIMARY = "#D0BCFF"
COLOR_ERROR = "#F87171"


def parse_timing_value(val_str, fallback=59.100):
    """Парсит значение тайминга из строки, поддерживая точки, двоеточия и запятые (например, 59:100 или 59.100)."""
    if not val_str:
        return fallback
    clean = str(val_str).strip().replace(':', '.').replace(',', '.')
    try:
        f = float(clean)
        if 0.0 <= f <= 60.0:
            return round(f, 3)
    except (ValueError, TypeError):
        pass
    return fallback


class TimingSettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.translation = app.translation

        ctk.set_appearance_mode("Dark")
        self.title(self.translation.tr('timings_dialog_title'))

        # Размеры окна увеличены для лучшей читаемости
        win_w = 640
        win_h = 580
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        if screen_h <= 650:
            win_h = min(580, max(500, screen_h - 40))
            win_w = min(640, max(540, screen_w - 30))

        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2 - 20)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()
        self.focus_set()

        # Загрузка сохраненных 15 таймингов или дефолтных
        saved_15 = None
        if hasattr(self.app, 'settings') and 'custom_15_timings' in self.app.settings:
            saved_15 = self.app.settings['custom_15_timings']
        elif hasattr(self.app, 'config') and 'custom_15_timings' in self.app.config:
            saved_15 = self.app.config['custom_15_timings']

        if not saved_15 or len(saved_15) != 15:
            self.timings_15 = list(DEFAULT_15_TIMINGS)
        else:
            self.timings_15 = [float(x) for x in saved_15]

        # Текущие выбранные тайминги
        current_saved = getattr(self.app, 'selected_timings', None)
        if not current_saved:
            current_saved = list(TIMING_PROFILES['europe']['timings'])
        self.selected_timings = [float(x) for x in current_saved]

        # Инициализация переменных для каждого из 15 слотов
        self.slot_vars = []
        self.slot_entry_vars = []
        for i in range(15):
            t_val = self.timings_15[i]
            is_checked = any(abs(t_val - s) < 0.008 for s in self.selected_timings)
            self.slot_vars.append(ctk.BooleanVar(value=is_checked))
            self.slot_entry_vars.append(ctk.StringVar(value=f"{t_val:.3f}"))

        self._build_ui()

    def _build_ui(self):
        dark_mode = True
        color_primary = MaterialColors.get_color('primary', dark_mode)

        container = ctk.CTkFrame(
            self,
            fg_color="#18181D",
            corner_radius=14,
            border_width=1,
            border_color="#303038"
        )
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # 1. Заголовок окна
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", padx=4, pady=(6, 12))

        title_label = ctk.CTkLabel(
            header_frame,
            text=self.translation.tr('timings_dialog_title'),
            font=("Arial", 18, "bold"),
            text_color=TEXT_HEADER
        )
        title_label.pack(side="left")

        current_region = getattr(self.app, 'settings', {}).get('region', 'Europe') if hasattr(self.app, 'settings') else 'Europe'
        reg_badge = ctk.CTkFrame(header_frame, fg_color=CARD_BG_ELEVATED, corner_radius=8)
        reg_badge.pack(side="right")

        reg_label = ctk.CTkLabel(
            reg_badge,
            text=f"Регион: {current_region}",
            font=("Arial", 12, "bold"),
            text_color=color_primary
        )
        reg_label.pack(padx=10, pady=4)

        # 2. Карточка со слотами 15 таймингов (3 колонки по 5 строк) - без выбора профилей
        slots_card = ctk.CTkFrame(
            container,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER
        )
        slots_card.pack(fill="both", expand=True, pady=(0, 10))

        slots_inner = ctk.CTkFrame(slots_card, fg_color="transparent")
        slots_inner.pack(fill="both", expand=True, padx=14, pady=12)

        slots_header_row = ctk.CTkFrame(slots_inner, fg_color="transparent")
        slots_header_row.pack(fill="x", pady=(0, 10))

        slots_desc = ctk.CTkLabel(
            slots_header_row,
            text=self.translation.tr('timings_slots_title'),
            font=("Arial", 14, "bold"),
            text_color=TEXT_BODY
        )
        slots_desc.pack(side="left")

        slots_hint = ctk.CTkLabel(
            slots_header_row,
            text="(формат: 59.100 или 59:100)",
            font=("Arial", 12),
            text_color="#94A3B8"
        )
        slots_hint.pack(side="left", padx=(8, 0))

        # Сетка 3 колонки x 5 строк с крупными удобными элементами
        grid_frame = ctk.CTkFrame(slots_inner, fg_color="transparent")
        grid_frame.pack(fill="both", expand=True)
        grid_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.slot_entries = []
        for i in range(15):
            col = i // 5
            row = i % 5

            cell = ctk.CTkFrame(grid_frame, fg_color="transparent")
            cell.grid(row=row, column=col, sticky="w", padx=8, pady=4)

            cb = ctk.CTkCheckBox(
                cell,
                text="",
                variable=self.slot_vars[i],
                command=lambda idx=i: self._on_slot_toggle(idx),
                width=22,
                height=22,
                corner_radius=5,
                fg_color=color_primary,
                checkmark_color="#18181C"
            )
            cb.pack(side="left", padx=(0, 6))

            idx_lbl = ctk.CTkLabel(
                cell,
                text=f"#{i + 1:02d}",
                font=("Consolas", 12, "bold"),
                text_color="#94A3B8",
                width=28,
                anchor="e"
            )
            idx_lbl.pack(side="left", padx=(0, 6))

            entry = ctk.CTkEntry(
                cell,
                textvariable=self.slot_entry_vars[i],
                width=96,
                height=32,
                corner_radius=8,
                font=("Consolas", 13, "bold"),
                fg_color="#18181C",
                border_color="#475569",
                border_width=1,
                justify="center"
            )
            entry.pack(side="left", padx=(0, 4))
            self.slot_entries.append(entry)

            sec_lbl = ctk.CTkLabel(
                cell,
                text="с",
                font=("Arial", 12, "bold"),
                text_color="#94A3B8"
            )
            sec_lbl.pack(side="left")

        # 3. Строка счетчика и предупреждения
        info_row = ctk.CTkFrame(slots_inner, fg_color="transparent")
        info_row.pack(fill="x", pady=(10, 0))

        self.count_label = ctk.CTkLabel(
            info_row,
            text="",
            font=("Arial", 13, "bold"),
            text_color=color_primary
        )
        self.count_label.pack(side="left")

        self.warning_min_label = ctk.CTkLabel(
            info_row,
            text="",
            font=("Arial", 13, "bold"),
            text_color=COLOR_ERROR
        )
        self.warning_min_label.pack(side="right")

        self._update_counter_label()

        # 4. Карточка-предупреждение о бане
        risk_card = ctk.CTkFrame(
            container,
            fg_color=CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color="#F59E0B"
        )
        risk_card.pack(fill="x", pady=(0, 12))

        risk_inner = ctk.CTkFrame(risk_card, fg_color="transparent")
        risk_inner.pack(fill="x", padx=12, pady=8)

        risk_label = ctk.CTkLabel(
            risk_inner,
            text=self.translation.tr('timings_risk_warning'),
            font=("Arial", 12),
            text_color=TEXT_BODY,
            justify="left",
            wraplength=580
        )
        risk_label.pack(anchor="w")

        # 5. Кнопки действий
        actions_frame = ctk.CTkFrame(container, fg_color="transparent")
        actions_frame.pack(fill="x", side="bottom", pady=(0, 4))

        reset_btn = MD3Button(
            actions_frame,
            text=self.translation.tr('timings_reset_btn'),
            button_type='outlined',
            size='medium',
            height=36,
            command=self._reset_to_defaults
        )
        reset_btn.pack(side="left")

        save_btn = MD3Button(
            actions_frame,
            text=self.translation.tr('timings_save_btn'),
            button_type='filled',
            size='medium',
            height=36,
            command=self._save_and_close
        )
        save_btn.pack(side="right")

    def _on_slot_toggle(self, idx):
        selected_count = sum(1 for v in self.slot_vars if v.get())
        if selected_count < MIN_SELECTED_TIMINGS:
            self.slot_vars[idx].set(True)
            self.warning_min_label.configure(text=self.translation.tr('timings_min_warning'))
            self.after(2500, lambda: self.warning_min_label.configure(text=""))
        else:
            self.warning_min_label.configure(text="")
        self._update_counter_label()

    def _update_counter_label(self):
        selected_count = sum(1 for v in self.slot_vars if v.get())
        text = self.translation.tr('timings_count_label').format(selected_count, 15)
        self.count_label.configure(text=text)

    def _reset_to_defaults(self):
        """Сброс к дефолтным 15 слотам."""
        for i in range(15):
            def_val = DEFAULT_15_TIMINGS[i]
            self.slot_entry_vars[i].set(f"{def_val:.3f}")
            is_def = any(abs(def_val - t) < 0.008 for t in DEFAULT_AUTO_TIMINGS)
            self.slot_vars[i].set(is_def)
        self.warning_min_label.configure(text="")
        self._update_counter_label()

    def _save_and_close(self):
        selected = []
        all_15 = []

        for i in range(15):
            val_str = self.slot_entry_vars[i].get()
            val = parse_timing_value(val_str, DEFAULT_15_TIMINGS[i])
            all_15.append(val)
            if self.slot_vars[i].get():
                selected.append(val)

        if not selected:
            selected = list(DEFAULT_AUTO_TIMINGS)

        selected = sorted(list(set(selected)))

        self.app.selected_timings = selected

        if hasattr(self.app, 'settings'):
            self.app.settings['manual_timings'] = selected
            self.app.settings['auto_timings'] = selected
            self.app.settings['custom_15_timings'] = all_15

        if hasattr(self.app, 'config'):
            self.app.config['manual_timings'] = selected
            self.app.config['auto_timings'] = selected
            self.app.config['custom_15_timings'] = all_15

        if hasattr(self.app, 'save_settings'):
            self.app.save_settings()

        if hasattr(self.app, 'manual_time_var'):
            self.app.manual_time_var.set(", ".join(f"{t:.3f}" for t in selected))

        timings_str = ", ".join(f"{t:.3f}s" for t in selected)
        self.app.log_message(f"[{self.translation.tr('timings_btn')}] {timings_str} ({len(selected)} req)", color="blue")

        self.destroy()
