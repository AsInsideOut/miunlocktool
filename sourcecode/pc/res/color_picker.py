# -*- coding: utf-8 -*-
"""
Custom Color Picker Dialog in Material 3 dark style.
Allows selecting an accent theme color via presets, RGB sliders, or HEX input.
Features 'Принять' (Apply) and 'Закрыть' (Cancel) buttons.
"""

import re
import customtkinter as ctk

try:
    from theme import MaterialColors, MD3Button, MD3Label
except ImportError:
    try:
        from .theme import MaterialColors, MD3Button, MD3Label
    except ImportError:
        from res.theme import MaterialColors, MD3Button, MD3Label

PRESET_COLORS = [
    '#D0BCFF',  # Material Lavender (Default)
    '#A855F7',  # Violet / Purple
    '#818CF8',  # Indigo
    '#3B82F6',  # Electric Blue
    '#0EA5E9',  # Sky Blue
    '#06B6D4',  # Cyan
    '#14B8A6',  # Teal
    '#10B981',  # Emerald
    '#22C55E',  # Mint Green
    '#EAB308',  # Amber
    '#F97316',  # Warm Orange
    '#EF4444',  # Coral Red
    '#EC4899',  # Neon Pink
    '#F43F5E',  # Rose
]


class CustomColorPickerDialog(ctk.CTkToplevel):
    def __init__(self, parent, initial_color="#D0BCFF", on_accept=None, translation=None):
        super().__init__(parent)
        self.parent = parent
        self.initial_color = self._normalize_hex(initial_color) or "#D0BCFF"
        self.current_color = self.initial_color
        self.on_accept_cb = on_accept
        self.translation = translation

        ctk.set_appearance_mode("Dark")
        win_title = self.translation.tr('color_picker_title') if self.translation else "Выбор цвета темы"
        self.title(win_title)

        win_w = 420
        win_h = 510
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()
        self.focus_set()

        r, g, b = self._hex_to_rgb(self.current_color)
        self.r_val = ctk.IntVar(value=r)
        self.g_val = ctk.IntVar(value=g)
        self.b_val = ctk.IntVar(value=b)
        self.hex_var = ctk.StringVar(value=self.current_color)

        self.updating_from_code = False
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def _normalize_hex(self, color_str):
        if not color_str:
            return None
        c = str(color_str).strip()
        if re.fullmatch(r'#?[0-9a-fA-F]{6}', c):
            return '#' + c.lstrip('#').upper()
        return None

    def _hex_to_rgb(self, hex_str):
        h = hex_str.lstrip('#')
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, r, g, b):
        return f"#{int(r):02X}{int(g):02X}{int(b):02X}"

    def _build_ui(self):
        main_frame = ctk.CTkFrame(
            self,
            fg_color="#18181D",
            corner_radius=14,
            border_width=1,
            border_color="#303038"
        )
        main_frame.pack(fill="both", expand=True, padx=12, pady=12)

        # 1. Заголовок и карточка предпросмотра
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=14, pady=(12, 8))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text=self.translation.tr('color_picker_title') if self.translation else "Выбор цвета темы",
            font=("Arial", 16, "bold"),
            text_color="#FFFFFF"
        )
        title_lbl.pack(anchor="w")

        # Плашка сравнения цветов: Старый -> Новый
        preview_container = ctk.CTkFrame(
            main_frame,
            fg_color="#22222A",
            corner_radius=10,
            border_width=1,
            border_color="#3A3A46"
        )
        preview_container.pack(fill="x", padx=14, pady=(4, 10))

        preview_row = ctk.CTkFrame(preview_container, fg_color="transparent")
        preview_row.pack(fill="x", padx=12, pady=10)

        # Старый цвет
        old_col = ctk.CTkFrame(preview_row, fg_color="transparent")
        old_col.pack(side="left", padx=(0, 16))

        ctk.CTkLabel(
            old_col,
            text=self.translation.tr('color_picker_current') if self.translation else "Текущий:",
            font=("Arial", 11),
            text_color="#94A3B8"
        ).pack(anchor="w")

        self.old_swatch = ctk.CTkFrame(
            old_col,
            width=70,
            height=34,
            corner_radius=6,
            fg_color=self.initial_color,
            border_width=1,
            border_color="#555566"
        )
        self.old_swatch.pack(pady=(2, 0))
        self.old_swatch.pack_propagate(False)

        # Стрелка
        ctk.CTkLabel(
            preview_row,
            text="➜",
            font=("Arial", 14, "bold"),
            text_color="#64748B"
        ).pack(side="left", padx=(0, 16))

        # Новый выбранный цвет
        new_col = ctk.CTkFrame(preview_row, fg_color="transparent")
        new_col.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            new_col,
            text=self.translation.tr('color_picker_selected') if self.translation else "Выбранный цвет:",
            font=("Arial", 11),
            text_color="#94A3B8"
        ).pack(anchor="w")

        self.new_swatch = ctk.CTkFrame(
            new_col,
            height=34,
            corner_radius=6,
            fg_color=self.current_color,
            border_width=1,
            border_color="#FFFFFF"
        )
        self.new_swatch.pack(fill="x", pady=(2, 0))

        self.hex_label_on_swatch = ctk.CTkLabel(
            self.new_swatch,
            text=self.current_color,
            font=("Consolas", 13, "bold"),
            text_color="#000000" if self._is_bright(self.current_color) else "#FFFFFF"
        )
        self.hex_label_on_swatch.pack(expand=True)

        # 2. Готовые пресеты (2 ряда по 7 чипов)
        presets_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#22222A",
            corner_radius=10,
            border_width=1,
            border_color="#3A3A46"
        )
        presets_frame.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkLabel(
            presets_frame,
            text=self.translation.tr('color_picker_palette') if self.translation else "Палитра готовых цветов:",
            font=("Arial", 12, "bold"),
            text_color="#E2E8F0"
        ).pack(anchor="w", padx=12, pady=(8, 4))

        swatches_grid = ctk.CTkFrame(presets_frame, fg_color="transparent")
        swatches_grid.pack(fill="x", padx=10, pady=(0, 10))
        for col_idx in range(7):
            swatches_grid.grid_columnconfigure(col_idx, weight=1)

        self.preset_buttons = []
        for idx, color_hex in enumerate(PRESET_COLORS):
            row = idx // 7
            col = idx % 7
            btn = ctk.CTkButton(
                swatches_grid,
                text="",
                width=38,
                height=26,
                corner_radius=6,
                fg_color=color_hex,
                hover_color=color_hex,
                border_width=2 if color_hex.upper() == self.current_color.upper() else 0,
                border_color="#FFFFFF",
                command=lambda c=color_hex: self._select_preset(c)
            )
            btn.grid(row=row, column=col, padx=3, pady=3)
            self.preset_buttons.append((color_hex, btn))

        # 3. Ползунки RGB и ввод HEX
        controls_frame = ctk.CTkFrame(
            main_frame,
            fg_color="#22222A",
            corner_radius=10,
            border_width=1,
            border_color="#3A3A46"
        )
        controls_frame.pack(fill="x", padx=14, pady=(0, 12))

        # R Slider
        lbl_r = self.translation.tr('color_picker_red') if self.translation else "Красный (R)"
        self._create_slider_row(controls_frame, lbl_r, self.r_val, "#EF4444")
        # G Slider
        lbl_g = self.translation.tr('color_picker_green') if self.translation else "Зеленый (G)"
        self._create_slider_row(controls_frame, lbl_g, self.g_val, "#22C55E")
        # B Slider
        lbl_b = self.translation.tr('color_picker_blue') if self.translation else "Синий (B)"
        self._create_slider_row(controls_frame, lbl_b, self.b_val, "#3B82F6")

        # Поле прямого ввода HEX
        hex_row = ctk.CTkFrame(controls_frame, fg_color="transparent")
        hex_row.pack(fill="x", padx=12, pady=(4, 10))

        ctk.CTkLabel(
            hex_row,
            text="HEX:",
            font=("Arial", 12, "bold"),
            text_color="#94A3B8"
        ).pack(side="left", padx=(0, 8))

        self.hex_entry = ctk.CTkEntry(
            hex_row,
            textvariable=self.hex_var,
            width=110,
            height=28,
            corner_radius=6,
            font=("Consolas", 12, "bold"),
            fg_color="#18181D",
            border_color="#475569",
            justify="center"
        )
        self.hex_entry.pack(side="left")
        self.hex_entry.bind("<KeyRelease>", self._on_hex_entry_change)

        # 4. Две нижние кнопки: Закрыть и Принять
        actions_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=14, pady=(4, 8), side="bottom")

        cancel_text = self.translation.tr('color_picker_cancel') if self.translation else "Закрыть"
        self.cancel_btn = ctk.CTkButton(
            actions_frame,
            text=cancel_text,
            width=110,
            height=36,
            corner_radius=10,
            font=("Arial", 13, "bold"),
            fg_color="#2A2A34",
            hover_color="#3A3A46",
            text_color="#E2E8F0",
            border_width=1,
            border_color="#4B4B5A",
            command=self.on_cancel
        )
        self.cancel_btn.pack(side="left")

        accept_text = self.translation.tr('color_picker_accept') if self.translation else "Принять"
        self.accept_btn = ctk.CTkButton(
            actions_frame,
            text=accept_text,
            width=140,
            height=36,
            corner_radius=10,
            font=("Arial", 13, "bold"),
            fg_color=self.current_color,
            hover_color=self.current_color,
            text_color="#000000" if self._is_bright(self.current_color) else "#FFFFFF",
            command=self.on_accept_click
        )
        self.accept_btn.pack(side="right")

    def _create_slider_row(self, parent, label_text, var, accent_color):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=12, pady=(6, 2))

        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            font=("Arial", 11),
            text_color="#CBD5E1",
            width=85,
            anchor="w"
        )
        lbl.pack(side="left")

        slider = ctk.CTkSlider(
            row,
            from_=0,
            to=255,
            number_of_steps=255,
            variable=var,
            progress_color=accent_color,
            button_color=accent_color,
            button_hover_color=accent_color,
            command=lambda val: self._on_slider_change()
        )
        slider.pack(side="left", fill="x", expand=True, padx=(4, 8))

        val_lbl = ctk.CTkLabel(
            row,
            textvariable=var,
            font=("Consolas", 11, "bold"),
            text_color="#CBD5E1",
            width=32,
            anchor="e"
        )
        val_lbl.pack(side="right")

    def _is_bright(self, hex_str):
        try:
            r, g, b = self._hex_to_rgb(hex_str)
            return (0.299 * r + 0.587 * g + 0.114 * b) > 155
        except Exception:
            return True

    def _select_preset(self, color_hex):
        norm = self._normalize_hex(color_hex)
        if not norm:
            return
        r, g, b = self._hex_to_rgb(norm)
        self.updating_from_code = True
        self.r_val.set(r)
        self.g_val.set(g)
        self.b_val.set(b)
        self.hex_var.set(norm)
        self.updating_from_code = False
        self._update_color_preview(norm)

    def _on_slider_change(self):
        if self.updating_from_code:
            return
        r = self.r_val.get()
        g = self.g_val.get()
        b = self.b_val.get()
        new_hex = self._rgb_to_hex(r, g, b)
        self.updating_from_code = True
        self.hex_var.set(new_hex)
        self.updating_from_code = False
        self._update_color_preview(new_hex)

    def _on_hex_entry_change(self, event=None):
        if self.updating_from_code:
            return
        raw = self.hex_var.get().strip()
        norm = self._normalize_hex(raw)
        if norm:
            r, g, b = self._hex_to_rgb(norm)
            self.updating_from_code = True
            self.r_val.set(r)
            self.g_val.set(g)
            self.b_val.set(b)
            self.updating_from_code = False
            self._update_color_preview(norm)

    def _update_color_preview(self, hex_color):
        self.current_color = hex_color
        is_bright = self._is_bright(hex_color)
        text_color = "#000000" if is_bright else "#FFFFFF"

        self.new_swatch.configure(fg_color=hex_color)
        self.hex_label_on_swatch.configure(text=hex_color, text_color=text_color)
        self.accept_btn.configure(fg_color=hex_color, hover_color=hex_color, text_color=text_color)

        for col_hex, btn in self.preset_buttons:
            if col_hex.upper() == hex_color.upper():
                btn.configure(border_width=2)
            else:
                btn.configure(border_width=0)

    def on_accept_click(self):
        """Применяет выбранный цвет и закрывает окно."""
        if self.on_accept_cb and callable(self.on_accept_cb):
            try:
                self.on_accept_cb(self.current_color)
            except Exception as e:
                print(f"Error applying color: {e}")
        self.destroy()

    def on_cancel(self):
        """Закрывает окно без сохранения/применения цвета."""
        self.destroy()
