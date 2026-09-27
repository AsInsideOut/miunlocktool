import sys
import os
import json
import webbrowser
import threading
import subprocess
import re
from tkinter import messagebox
import customtkinter as ctk

try:
    from theme import (
        MaterialColors, MD3Card, MD3Label, MD3Button,
        MD3Entry, MD3Switch, MaterialTypography
    )
except ImportError:
    try:
        from .theme import (
            MaterialColors, MD3Card, MD3Label, MD3Button,
            MD3Entry, MD3Switch, MaterialTypography
        )
    except ImportError:
        from res.theme import (
            MaterialColors, MD3Card, MD3Label, MD3Button,
            MD3Entry, MD3Switch, MaterialTypography
        )

try:
    from settings_ui import (
        build_about_section, build_general_section,
        build_cookies_section, build_trouble_section,
        FOURPDA_TOPIC_URL, TELEGRAM_URL, GITHUB_URL, SITE_URL
    )
except ImportError:
    try:
        from .settings_ui import (
            build_about_section, build_general_section,
            build_cookies_section, build_trouble_section,
            FOURPDA_TOPIC_URL, TELEGRAM_URL, GITHUB_URL, SITE_URL
        )
    except ImportError:
        from res.settings_ui import (
            build_about_section, build_general_section,
            build_cookies_section, build_trouble_section,
            FOURPDA_TOPIC_URL, TELEGRAM_URL, GITHUB_URL, SITE_URL
        )

UPDATE_CHECK_URL = "https://miunlock.su/version.txt"
UPDATE_DOWNLOAD_URL = "https://miunlock.su/download/stable/pc/Latest_Release.zip"


def get_display_region(app):
    try:
        if app is not None and getattr(app, 'settings', None):
            region = app.settings.get('region')
            if region:
                return str(region)
    except Exception:
        pass

    try:
        import __main__
        if hasattr(__main__, 'detect_user_region'):
            return str(__main__.detect_user_region())
    except Exception:
        pass

    return 'Europe'


def get_current_version():
    try:
        import __main__
        if hasattr(__main__, 'CURRENT_VERSION'):
            return __main__.CURRENT_VERSION
    except:
        pass
    return "8.1"


class UpdateChecker:
    @staticmethod
    def get_current_version():
        return get_current_version()

    @staticmethod
    def extract_version_number(version_str):
        if not version_str:
            return None

        text = str(version_str).strip()
        match = re.search(r'(\d+\.\d+\.\d+)', text)
        if not match:
            match = re.search(r'(\d+\.\d+)', text)
        return match.group(1) if match else None

    @staticmethod
    def compare_versions(v1, v2):
        try:
            v1_parts = list(map(int, str(v1).split('.')))
            v2_parts = list(map(int, str(v2).split('.')))
            for i in range(max(len(v1_parts), len(v2_parts))):
                a = v1_parts[i] if i < len(v1_parts) else 0
                b = v2_parts[i] if i < len(v2_parts) else 0
                if a > b:
                    return 1
                elif a < b:
                    return -1
            return 0
        except:
            return 0

    @staticmethod
    def check_for_updates():
        try:
            import requests
            current = UpdateChecker.get_current_version()
            current_num = UpdateChecker.extract_version_number(current)
            if not current_num:
                return None, "Не удалось определить текущую версию"

            response = requests.get(UPDATE_CHECK_URL, timeout=5)
            if response.status_code == 200:
                latest = response.text.strip()
                latest_num = UpdateChecker.extract_version_number(latest)
                if latest_num and UpdateChecker.compare_versions(latest_num, current_num) > 0:
                    return latest_num, latest
                else:
                    return None, "up_to_date"
            else:
                return None, "update_check_error"
        except Exception as e:
            return None, f"update_error: {str(e)}"


class WelcomeWindow(ctk.CTkToplevel):
    def __init__(self, parent, translation, app=None):
        super().__init__(parent)
        self.translation = translation
        self.app = app

        self.update_idletasks()
        self.title(self.translation.tr('welcome_title'))
        self.geometry("700x550")
        self.resizable(False, False)

        self.attributes("-alpha", 0.0)
        self.grab_set()
        self.focus_set()
        self.attributes("-topmost", True)

        # Принудительно устанавливаем темную тему для окна
        ctk.set_appearance_mode("Dark")
        dark_mode = True

        main_container = ctk.CTkFrame(
            self,
            fg_color=MaterialColors.get_color('surface_container', dark_mode),
            corner_radius=12
        )
        main_container.pack(fill="both", expand=True, padx=0, pady=0)

        header_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=30, pady=(30, 10))
        header_frame.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            header_frame,
            text="🔓",
            font=("Arial", 48),
            text_color=MaterialColors.get_color('primary', dark_mode)
        )
        icon_label.pack(side="left", padx=(0, 20))

        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="y", expand=True)

        title_label = MD3Label(
            title_frame,
            text="Xiaomi Unlock Tool",
            typography='headline_large'
        )
        title_label.pack(anchor="w")

        version_label = MD3Label(
            title_frame,
            text=f"Version {UpdateChecker.get_current_version()}",
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant', dark_mode)
        )
        version_label.pack(anchor="w", pady=(5, 0))

        text_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        text_frame.pack(fill="both", expand=True, padx=30, pady=20)

        welcome_card = MD3Card(
            text_frame,
            fg_color=MaterialColors.get_color('surface_container_high', dark_mode),
            corner_radius=12,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant', dark_mode)
        )
        welcome_card.pack(fill="both", expand=True)

        welcome_scroll = ctk.CTkScrollableFrame(welcome_card, fg_color="transparent")
        welcome_scroll.pack(fill="both", expand=True, padx=12, pady=12)

        welcome_label = ctk.CTkLabel(
            welcome_scroll,
            text=self.translation.tr('welcome_text'),
            font=("Arial", 13),
            text_color=MaterialColors.get_color('on_surface', dark_mode),
            justify="left",
            wraplength=480
        )
        welcome_label.pack(anchor="w", padx=8, pady=8)

        button_frame = ctk.CTkFrame(main_container, fg_color="transparent", height=60)
        button_frame.pack(fill="x", padx=30, pady=(0, 30))
        button_frame.pack_propagate(False)

        continue_button = MD3Button(
            button_frame,
            text=self.translation.tr('welcome_btn'),
            button_type='filled',
            size='large',
            command=self._on_ok
        )
        continue_button.pack(fill="x")

        self.protocol("WM_DELETE_WINDOW", self._on_ok)

        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.winfo_width()) // 2
        y = (screen_height - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        self.after(20, self._animate_in)

    def _animate_in(self):
        if self.app and not self.app.settings.get('animations_enabled', True):
            self.attributes("-alpha", 1.0)
            return
        steps = 10
        def fade(step):
            if not self.winfo_exists():
                return
            t = (step + 1) / steps
            eased = 1 - (1 - t) ** 2.5
            try:
                self.attributes("-alpha", min(1.0, max(0.05, eased)))
            except Exception:
                pass
            if step < steps - 1:
                self.after(16, lambda: fade(step + 1))
            else:
                self.attributes("-alpha", 1.0)
        try:
            self.attributes("-alpha", 0.05)
            fade(0)
        except Exception:
            self.attributes("-alpha", 1.0)

    def _on_ok(self):
        self.grab_release()
        self.attributes("-alpha", 0.0)
        self.destroy()


class InstructionsWindow(ctk.CTkToplevel):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.parent = parent
        self.app = app
        self.translation = app.translation

        # Принудительно устанавливаем темную тему для окна
        ctk.set_appearance_mode("Dark")

        self.title(self.translation.tr('instructions_title'))
        win_w = 900
        win_h = 620
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        if screen_h <= 720:
            win_h = min(620, max(520, screen_h - 70))
            win_w = min(900, max(750, screen_w - 40))
        pos_x = max(0, (screen_w - win_w) // 2)
        pos_y = max(0, (screen_h - win_h) // 2 - 20)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(750, 500)
        self.resizable(True, True)
        self.attributes("-alpha", 1.0)
        self.update_idletasks()
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._request_close)

        self.skip_cookie_check_var = ctk.BooleanVar(
            value=self.app.settings.get('skip_cookie_check', False)
        )
        self.default_ping_var = ctk.StringVar(
            value=str(self.app.settings.get('default_ping', 165))
        )
        self.theme_var = ctk.StringVar(value='Dark')
        self.language_var = ctk.StringVar(
            value=self.app.translation.language
        )
        self.log_to_txt_var = ctk.BooleanVar(
            value=self.app.settings.get('log_to_txt', False)
        )
        self.animations_enabled_var = ctk.BooleanVar(
            value=False
        )

        self.skip_cookie_check_var.trace_add('write', self.auto_save_settings)
        self.default_ping_var.trace_add('write', self.auto_save_settings)
        self.language_var.trace_add('write', self.on_language_changed)
        self.log_to_txt_var.trace_add('write', self.auto_save_settings)
        self.animations_enabled_var.trace_add('write', self.auto_save_settings)

        self.cookies_expanded = False
        self._is_updating = False
        self.current_content_provider = None
        self.active_section = None
        self.scrollable_frame = None

        self._create_layout()
        self._create_sidebar_buttons()

        self.attributes("-alpha", 1.0)
        self.after(30, self._animate_in)
        self.show_about_content()

    def _request_close(self):
        if getattr(self, '_is_closing', False):
            return
        self._is_closing = True
        self._animate_out()

    def _final_close(self):
        if self.app and hasattr(self.app, 'on_instructions_close'):
            try:
                self.app.on_instructions_close(self)
            except Exception:
                pass
        if self.winfo_exists():
            self.grab_release()
            self.destroy()

    def _animate_in(self):
        if not self.app.settings.get('animations_enabled', True):
            self.attributes('-alpha', 1.0)
            return
        steps = 10
        def fade(step):
            if not self.winfo_exists():
                return
            t = (step + 1) / steps
            eased = 1 - (1 - t) ** 2.5
            try:
                self.attributes('-alpha', min(1.0, max(0.05, eased)))
            except Exception:
                pass
            if step < steps - 1:
                self.after(16, lambda: fade(step + 1))
            else:
                self.attributes('-alpha', 1.0)
        try:
            self.attributes('-alpha', 0.05)
            fade(0)
        except Exception:
            self.attributes('-alpha', 1.0)

    def _animate_out(self):
        self.grab_release()
        if not self.app.settings.get('animations_enabled', True):
            self._final_close()
            return
        steps = 8
        def fade_out(step):
            if not self.winfo_exists():
                return
            t = (step + 1) / steps
            eased = max(0.0, 1.0 - (t ** 2))
            try:
                self.attributes('-alpha', eased)
            except Exception:
                pass
            if step < steps - 1:
                self.after(16, lambda: fade_out(step + 1))
            else:
                self._final_close()
        fade_out(0)

    def _recreate_ui(self):
        provider = self.current_content_provider
        cookies_state = self.cookies_expanded
        for w in self.winfo_children():
            w.destroy()
        self._create_layout()
        self._create_sidebar_buttons()
        if cookies_state:
            self.toggle_cookies_section()
        if provider:
            provider()

    def on_language_changed(self, *args):
        if self._is_updating:
            return

        new_lang = self.language_var.get()
        if new_lang == self.app.translation.language:
            return

        self._is_updating = True
        try:
            self.app.translation.language = new_lang
            self.app.settings['language'] = new_lang
            self.app.save_settings()
            self.app.update_ui_text()
            self._recreate_ui()
        finally:
            self._is_updating = False

    def auto_save_settings(self, *args):
        if self._is_updating:
            return

        self._is_updating = True
        try:
            try:
                ping_value = int(self.default_ping_var.get())
                if ping_value <= 0:
                    self._is_updating = False
                    return
                self.app.settings['default_ping'] = ping_value
            except ValueError:
                self._is_updating = False
                return

            self.app.settings['skip_cookie_check'] = self.skip_cookie_check_var.get()
            self.app.settings['log_to_txt'] = self.log_to_txt_var.get()
            self.app.settings['theme'] = 'Dark'
            self.app.settings['language'] = self.language_var.get()
            self.app.settings['animations_enabled'] = False

            self.app.save_settings()

            self.app.log_message(self.translation.tr('settings_saved'))
            self.app.log_message(
                self.translation.tr('cookie_check').format(
                    "Disabled" if self.skip_cookie_check_var.get() else "Enabled"
                )
            )
            self.app.log_message(
                self.translation.tr('default_ping').format(self.app.settings['default_ping'])
            )

        except Exception as e:
            print(f"Ошибка автосохранения настроек: {e}")
        finally:
            self._is_updating = False

    def get_current_theme(self):
        return 'Dark'

    def _create_layout(self):
        dark_mode = True

        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=MaterialColors.get_color('background', dark_mode)
        )
        self.main_frame.pack(fill="both", expand=True, padx=0, pady=0)

        self.sidebar_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=MaterialColors.get_color('surface_container', dark_mode),
            width=230
        )
        self.sidebar_frame.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar_frame.pack_propagate(False)

        self.content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=MaterialColors.get_color('background', dark_mode)
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)

        self.header_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color=MaterialColors.get_color('primary', dark_mode)
        )
        self.header_frame.pack(fill="x", pady=(0, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=self.translation.tr('instructions_title'),
            font=("Arial", 20, "bold"),
            text_color=MaterialColors.get_color('on_primary', dark_mode),
            fg_color=MaterialColors.get_color('primary', dark_mode)
        )
        self.title_label.pack(pady=12)

        self.content_area = ctk.CTkFrame(
            self.content_frame,
            fg_color=MaterialColors.get_color('background', dark_mode)
        )
        self.content_area.pack(fill="both", expand=True, padx=20, pady=20)

    def _create_sidebar_buttons(self):
        dark_mode = True
        button_font = ("Arial", 16, "bold")
        button_height = 48
        sidebar_bg = MaterialColors.get_color('surface_container', dark_mode)
        text_color = MaterialColors.get_color('on_surface', dark_mode)

        menu_title = ctk.CTkLabel(
            self.sidebar_frame,
            text=self.translation.tr('sections_menu'),
            font=("Arial", 16, "bold"),
            text_color="#FFFFFF"
        )
        menu_title.pack(anchor="w", padx=16, pady=(16, 6))

        self.about_btn = MD3Button(
            self.sidebar_frame,
            text=self.translation.tr('about_title'),
            button_type='outlined',
            size='medium',
            font=button_font,
            height=button_height,
            fg_color=sidebar_bg,
            hover_color=MaterialColors.get_color('surface_container_high', dark_mode),
            text_color=text_color,
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline', dark_mode),
            anchor="w",
            command=lambda: self._show_section(self.show_about_content, 'about')
        )
        self.about_btn.pack(fill="x", padx=12, pady=(6, 8))

        self.general_btn = MD3Button(
            self.sidebar_frame,
            text=self.translation.tr('general_title'),
            button_type='outlined',
            size='medium',
            font=button_font,
            height=button_height,
            fg_color=sidebar_bg,
            hover_color=MaterialColors.get_color('surface_container_high', dark_mode),
            text_color=text_color,
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline', dark_mode),
            anchor="w",
            command=lambda: self._show_section(self.show_general_content, 'general')
        )
        self.general_btn.pack(fill="x", padx=12, pady=8)

        self.cookies_btn = MD3Button(
            self.sidebar_frame,
            text=self.translation.tr('cookies_title'),
            button_type='outlined',
            size='medium',
            font=button_font,
            height=button_height,
            fg_color=sidebar_bg,
            hover_color=MaterialColors.get_color('surface_container_high', dark_mode),
            text_color=text_color,
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline', dark_mode),
            anchor="w",
            command=lambda: self._show_section(self.show_cookies_content, 'cookies')
        )
        self.cookies_btn.pack(fill="x", padx=12, pady=8)

        self.trouble_btn = MD3Button(
            self.sidebar_frame,
            text=self.translation.tr('trouble_title'),
            button_type='outlined',
            size='medium',
            font=button_font,
            height=button_height,
            fg_color=sidebar_bg,
            hover_color=MaterialColors.get_color('surface_container_high', dark_mode),
            text_color=text_color,
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline', dark_mode),
            anchor="w",
            command=lambda: self._show_section(self.show_trouble_content, 'trouble')
        )
        self.trouble_btn.pack(fill="x", padx=12, pady=8)

        self.authors_btn = MD3Button(
            self.sidebar_frame,
            text=self.translation.tr('authors_title'),
            button_type='outlined',
            size='medium',
            font=button_font,
            height=button_height,
            fg_color=sidebar_bg,
            hover_color=MaterialColors.get_color('surface_container_high', dark_mode),
            text_color=text_color,
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline', dark_mode),
            anchor="w",
            command=lambda: self._show_section(self.show_authors_content, 'authors')
        )
        self.authors_btn.pack(fill="x", padx=12, pady=8)

        self.settings_btn = MD3Button(
            self.sidebar_frame,
            text=self.translation.tr('settings'),
            button_type='outlined',
            size='medium',
            font=button_font,
            height=button_height,
            fg_color=sidebar_bg,
            hover_color=MaterialColors.get_color('surface_container_high', dark_mode),
            text_color=text_color,
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline', dark_mode),
            anchor="w",
            command=lambda: self._show_section(self.show_settings_content, 'settings')
        )
        self.settings_btn.pack(fill="x", padx=12, pady=(8, 12))

    def _show_section(self, provider, section_name):
        if self.active_section == section_name:
            return
        self.active_section = section_name
        provider()

    def _recreate_ui(self):
        provider = self.current_content_provider
        cookies_state = self.cookies_expanded
        active_section = self.active_section
        for w in self.winfo_children():
            w.destroy()
        self._create_layout()
        self._create_sidebar_buttons()
        if cookies_state:
            self.toggle_cookies_section()
        if provider and active_section:
            self.active_section = active_section
            if active_section == 'about':
                self.show_about_content()
            elif active_section == 'general':
                self.show_general_content()
            elif active_section == 'cookies':
                self.show_cookies_content()
            elif active_section == 'trouble':
                self.show_trouble_content()
            elif active_section == 'authors':
                self.show_authors_content()
            elif active_section == 'settings':
                self.show_settings_content()
        elif provider:
            provider()

    def protocol_close(self):
        self._animate_out()

    def clear_content_area(self):
        for w in list(self.content_area.winfo_children()):
            w.destroy()

    def _animate_section_switch(self, new_widget_factory, width_mode='medium'):
        stage = self.content_area
        old_widgets = list(stage.winfo_children())
        animations_enabled = self.app.settings.get('animations_enabled', True) if self.app else True

        if old_widgets:
            old_widget = old_widgets[-1]

            if animations_enabled:
                steps = 8
                def move_old(step):
                    if old_widget.winfo_exists():
                        t = (step + 1) / steps
                        eased = t ** 2
                        try:
                            old_widget.place_configure(y=int(-18 * eased))
                        except Exception:
                            pass
                        if step < steps - 1:
                            self.after(16, lambda: move_old(step + 1))
                        else:
                            try:
                                old_widget.destroy()
                            except Exception:
                                pass
                move_old(0)
            else:
                old_widget.destroy()

        new_widget = new_widget_factory()
        new_widget.place(in_=stage, x=0, y=20, relwidth=1, relheight=1)

        if animations_enabled:
            steps = 10
            def move_new(step):
                if new_widget.winfo_exists():
                    t = (step + 1) / steps
                    eased = 1 - (1 - t) ** 3
                    try:
                        new_widget.place_configure(y=int(20 * (1 - eased)))
                    except Exception:
                        pass
                    if step < steps - 1:
                        self.after(16, lambda: move_new(step + 1))
                    else:
                        new_widget.place_configure(y=0)
            move_new(0)
        else:
            new_widget.place_configure(y=0)

        if width_mode == 'full':
            new_widget.configure(width=760)
        elif width_mode == 'wide':
            new_widget.configure(width=680)
        else:
            new_widget.configure(width=620)

    def show_about_content(self):
        self.current_content_provider = self.show_about_content
        dark_mode = True

        def build():
            frame = MD3Card(
                self.content_area,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                corner_radius=12,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant', dark_mode)
            )
            frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=12, pady=12)
            site_text = "Сайт" if self.translation.language == 'ru' else ("Website" if self.translation.language in ('en', 'pt') else ("Situs Web" if self.translation.language == 'id' else ("Sitio Web" if self.translation.language == 'es' else "网站")))
            build_about_section(
                scroll, self.translation.language,
                lambda: webbrowser.open(TELEGRAM_URL, new=2),
                lambda: webbrowser.open(FOURPDA_TOPIC_URL, new=2),
                lambda: webbrowser.open(GITHUB_URL, new=2),
                lambda: webbrowser.open(SITE_URL, new=2),
                site_text, get_current_version()
            )
            return frame

        self._animate_section_switch(build, width_mode='full')

    def show_general_content(self):
        self.current_content_provider = self.show_general_content
        dark_mode = True

        def build():
            frame = MD3Card(
                self.content_area,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                corner_radius=12,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant', dark_mode)
            )
            frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=12, pady=12)
            build_general_section(scroll, self.translation.language)
            return frame

        self._animate_section_switch(build, width_mode='full')

    def show_cookies_content(self):
        self.current_content_provider = self.show_cookies_content
        dark_mode = True

        def build():
            frame = MD3Card(
                self.content_area,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                corner_radius=12,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant', dark_mode)
            )
            frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=12, pady=12)
            build_cookies_section(scroll, self.translation.language)
            return frame

        self._animate_section_switch(build, width_mode='full')

    def show_trouble_content(self):
        self.current_content_provider = self.show_trouble_content
        dark_mode = True

        def build():
            frame = MD3Card(
                self.content_area,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                corner_radius=12,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant', dark_mode)
            )
            frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)
            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=12, pady=12)
            build_trouble_section(
                scroll, self.translation.language,
                lambda: webbrowser.open(TELEGRAM_URL, new=2)
            )
            return frame

        self._animate_section_switch(build, width_mode='full')

    def show_authors_content(self):
        self.current_content_provider = self.show_authors_content
        dark_mode = True

        def build():
            frame = MD3Card(
                self.content_area,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                corner_radius=12,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant', dark_mode)
            )
            frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

            scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=12, pady=12)

            # 1. Крупная надпись: Разработчики Скрипта
            dev_title = ctk.CTkLabel(
                scroll,
                text=self.translation.tr('authors_developers_title'),
                font=("Arial", 22, "bold"),
                text_color=MaterialColors.get_color('on_surface', dark_mode)
            )
            dev_title.pack(anchor="w", padx=10, pady=(8, 4))

            devs_names = ctk.CTkLabel(
                scroll,
                text="pktloss, New G3n",
                font=("Arial", 16, "bold"),
                text_color=MaterialColors.get_color('primary', dark_mode)
            )
            devs_names.pack(anchor="w", padx=10, pady=(0, 16))

            # 2. Крупная надпись: Разработчик PC и CLI версии скрипта
            pc_cli_title = ctk.CTkLabel(
                scroll,
                text=self.translation.tr('authors_pc_cli_dev'),
                font=("Arial", 18, "bold"),
                text_color=MaterialColors.get_color('on_surface', dark_mode)
            )
            pc_cli_title.pack(anchor="w", padx=10, pady=(4, 4))

            pc_cli_name = ctk.CTkLabel(
                scroll,
                text="New G3n",
                font=("Arial", 15, "bold"),
                text_color=MaterialColors.get_color('primary', dark_mode)
            )
            pc_cli_name.pack(anchor="w", padx=10, pady=(0, 16))

            # 3. Надпись: Разработчик Сайта скрипта и Android версии
            web_android_title = ctk.CTkLabel(
                scroll,
                text=self.translation.tr('authors_web_android_dev'),
                font=("Arial", 18, "bold"),
                text_color=MaterialColors.get_color('on_surface', dark_mode)
            )
            web_android_title.pack(anchor="w", padx=10, pady=(4, 4))

            web_android_name = ctk.CTkLabel(
                scroll,
                text="pktloss",
                font=("Arial", 15, "bold"),
                text_color=MaterialColors.get_color('primary', dark_mode)
            )
            web_android_name.pack(anchor="w", padx=10, pady=(0, 16))

            # 4. Надпись не таким большим шрифтом: Скрипт написан на основе скрипта
            base_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            base_frame.pack(anchor="w", padx=10, pady=(4, 16))

            base_title = ctk.CTkLabel(
                base_frame,
                text=self.translation.tr('authors_base_script'),
                font=("Arial", 13),
                text_color=MaterialColors.get_color('on_surface_variant', dark_mode)
            )
            base_title.pack(side="left", padx=(0, 6))

            base_name = ctk.CTkLabel(
                base_frame,
                text="Vierta",
                font=("Arial", 13, "bold"),
                text_color=MaterialColors.get_color('primary', dark_mode)
            )
            base_name.pack(side="left")

            # Разделитель
            sep1 = ctk.CTkFrame(scroll, fg_color=MaterialColors.get_color('outline_variant', dark_mode), height=1)
            sep1.pack(fill="x", padx=10, pady=(4, 16))

            # 5. Текст: Ссылки на Соц Сети
            social_title = ctk.CTkLabel(
                scroll,
                text=self.translation.tr('authors_social_links'),
                font=("Arial", 16, "bold"),
                text_color=MaterialColors.get_color('on_surface', dark_mode)
            )
            social_title.pack(anchor="w", padx=10, pady=(0, 10))

            social_row = ctk.CTkFrame(scroll, fg_color="transparent")
            social_row.pack(anchor="w", padx=10, pady=(0, 16))

            tg_btn = ctk.CTkButton(
                social_row,
                text=self.translation.tr('social_telegram'),
                width=104,
                height=32,
                corner_radius=10,
                font=("Arial", 12, "bold"),
                fg_color="#5B8DEF",
                hover_color="#4A7AE6",
                text_color="#F8FBFF",
                border_width=0,
                command=lambda: webbrowser.open("https://t.me/miunlocktoolrevamp", new=2)
            )
            tg_btn.pack(side="left", padx=(0, 8))

            fourpda_btn = ctk.CTkButton(
                social_row,
                text="4PDA",
                width=88,
                height=32,
                corner_radius=10,
                font=("Arial", 12, "bold"),
                fg_color="#607D9B",
                hover_color="#506B85",
                text_color="#F5F8FC",
                border_width=0,
                command=lambda: webbrowser.open("https://4pda.to/forum/index.php?showtopic=721838&view=findpost&p=145201115", new=2)
            )
            fourpda_btn.pack(side="left", padx=(0, 8))

            gh_btn = ctk.CTkButton(
                social_row,
                text=self.translation.tr('social_github'),
                width=96,
                height=32,
                corner_radius=10,
                font=("Arial", 12, "bold"),
                fg_color="#1B1F24",
                hover_color="#2A3138",
                text_color="#F3F4F6",
                border_width=0,
                command=lambda: webbrowser.open("https://github.com/AsInsideOut/miunlocktool", new=2)
            )
            gh_btn.pack(side="left", padx=(0, 8))

            site_text = "Сайт" if self.translation.language == 'ru' else ("Website" if self.translation.language in ('en', 'pt') else ("Situs Web" if self.translation.language == 'id' else ("Sitio Web" if self.translation.language == 'es' else "网站")))
            st_btn = ctk.CTkButton(
                social_row,
                text=site_text,
                width=118,
                height=32,
                corner_radius=10,
                font=("Arial", 12, "bold"),
                fg_color=MaterialColors.get_color('surface_container_high', dark_mode),
                hover_color=MaterialColors.get_color('surface_container_highest', dark_mode),
                text_color=MaterialColors.get_color('on_surface', dark_mode),
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant', dark_mode),
                command=lambda: webbrowser.open("https://miunlock.su/", new=2)
            )
            st_btn.pack(side="left")

            # Разделитель
            sep2 = ctk.CTkFrame(scroll, fg_color=MaterialColors.get_color('outline_variant', dark_mode), height=1)
            sep2.pack(fill="x", padx=10, pady=(4, 16))

            # 6. Надпись: Пожертвовать на разработку
            donate_title = ctk.CTkLabel(
                scroll,
                text=self.translation.tr('authors_donate_title'),
                font=("Arial", 16, "bold"),
                text_color=MaterialColors.get_color('on_surface', dark_mode)
            )
            donate_title.pack(anchor="w", padx=10, pady=(0, 10))

            donate_btn = ctk.CTkButton(
                scroll,
                text="DonationAlerts",
                width=160,
                height=34,
                corner_radius=10,
                font=("Arial", 13, "bold"),
                fg_color="#FF6700",
                hover_color="#E65100",
                text_color="#FFFFFF",
                border_width=0,
                command=lambda: webbrowser.open("https://dalink.to/asinsideout", new=2)
            )
            donate_btn.pack(anchor="w", padx=10, pady=(0, 12))

            # 7. Криптокошелек (с возможностью копирования)
            crypto_frame = ctk.CTkFrame(
                scroll,
                fg_color=MaterialColors.get_color('surface_container_high', dark_mode),
                corner_radius=12,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant', dark_mode)
            )
            crypto_frame.pack(fill="x", padx=10, pady=(0, 16))

            crypto_header = ctk.CTkFrame(crypto_frame, fg_color="transparent")
            crypto_header.pack(fill="x", padx=14, pady=(10, 6))

            crypto_net = ctk.CTkLabel(
                crypto_header,
                text=self.translation.tr('authors_crypto_network'),
                font=("Arial", 12, "bold"),
                text_color=MaterialColors.get_color('primary', dark_mode)
            )
            crypto_net.pack(side="left")

            wallet_val = "UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG"

            def copy_wallet():
                try:
                    self.clipboard_clear()
                    self.clipboard_append(wallet_val)
                    self.update()
                    copy_btn.configure(text=self.translation.tr('address_copied'), fg_color="#10B981")
                    self.after(2000, lambda: copy_btn.configure(text=self.translation.tr('copy_address_btn'), fg_color=MaterialColors.get_color('surface_container_highest', dark_mode)))
                except Exception:
                    pass

            copy_btn = ctk.CTkButton(
                crypto_header,
                text=self.translation.tr('copy_address_btn'),
                width=100,
                height=26,
                corner_radius=8,
                font=("Arial", 11, "bold"),
                fg_color=MaterialColors.get_color('surface_container_highest', dark_mode),
                hover_color=MaterialColors.get_color('primary', dark_mode),
                text_color=MaterialColors.get_color('on_surface', dark_mode),
                command=copy_wallet
            )
            copy_btn.pack(side="right")

            crypto_entry = ctk.CTkEntry(
                crypto_frame,
                font=("Consolas", 12),
                height=32,
                corner_radius=8,
                fg_color=MaterialColors.get_color('surface_container_lowest', dark_mode),
                text_color=MaterialColors.get_color('on_surface', dark_mode),
                border_color=MaterialColors.get_color('outline', dark_mode),
                border_width=1
            )
            crypto_entry.insert(0, wallet_val)
            crypto_entry.configure(state="readonly")
            crypto_entry.pack(fill="x", padx=14, pady=(0, 10))

            return frame

        self._animate_section_switch(build, width_mode='full')

    def show_settings_content(self):
        self.current_content_provider = self.show_settings_content
        dark_mode = True

        def build():
            # Создаем карточку с прокруткой
            self.settings_frame = MD3Card(
                self.content_area,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                corner_radius=12,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant', dark_mode)
            )
            self.settings_frame.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

            # Создаем скроллируемый фрейм внутри карточки
            self.scrollable_frame = ctk.CTkScrollableFrame(
                self.settings_frame,
                fg_color="transparent",
                corner_radius=0,
                border_width=0
            )
            self.scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)

            return self.settings_frame

        self._animate_section_switch(build, width_mode='full')
        self.settings_frame.update_idletasks()

        scrollable = self.scrollable_frame

        # Тема (только темная)
        theme_frame = ctk.CTkFrame(
            scrollable,
            fg_color="transparent"
        )
        theme_frame.pack(fill="x", pady=10, padx=18)

        theme_label_widget = MD3Label(
            theme_frame,
            text=self.translation.tr('theme_label'),
            typography='label_large'
        )
        theme_label_widget.pack(anchor="w", pady=(8, 4))

        theme_locked_label = MD3Label(
            theme_frame,
            text=self.translation.tr('theme_dark_only'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant', dark_mode)
        )
        theme_locked_label.pack(anchor="w", pady=(0, 6))

        separator0 = ctk.CTkFrame(
            scrollable,
            fg_color=MaterialColors.get_color('outline_variant', dark_mode),
            height=1
        )
        separator0.pack(fill="x", padx=18, pady=(10, 10))

        # Язык
        language_frame = ctk.CTkFrame(
            scrollable,
            fg_color="transparent"
        )
        language_frame.pack(fill="x", pady=10, padx=18)

        language_label_widget = MD3Label(
            language_frame,
            text=self.translation.tr('language_label'),
            typography='label_large'
        )
        language_label_widget.pack(anchor="w", pady=(8, 4))

        language_optionmenu = ctk.CTkOptionMenu(
            language_frame,
            values=['ru', 'en', 'id', 'es', 'zh', 'pt'],
            variable=self.language_var,
            width=200,
            height=34,
            font=("Arial", 14),
            fg_color=MaterialColors.get_color('surface_container', dark_mode),
            button_color=MaterialColors.get_color('primary', dark_mode),
            button_hover_color=MaterialColors.get_color('primary_container', dark_mode),
            text_color=MaterialColors.get_color('on_surface', dark_mode)
        )
        language_optionmenu.pack(anchor="w", pady=(0, 8))

        separator1 = ctk.CTkFrame(
            scrollable,
            fg_color=MaterialColors.get_color('outline_variant', dark_mode),
            height=1
        )
        separator1.pack(fill="x", padx=18, pady=(10, 10))

        # Чекбоксы
        skip_check_frame = ctk.CTkFrame(
            scrollable,
            fg_color="transparent"
        )
        skip_check_frame.pack(fill="x", pady=10, padx=18)

        cookie_checkbox = MD3Switch(
            skip_check_frame,
            text=self.translation.tr('cookie_checkbox'),
            variable=self.skip_cookie_check_var
        )
        cookie_checkbox.pack(anchor="w", pady=8)

        log_to_txt_frame = ctk.CTkFrame(
            scrollable,
            fg_color="transparent"
        )
        log_to_txt_frame.pack(fill="x", pady=10, padx=18)

        log_to_txt_checkbox = MD3Switch(
            log_to_txt_frame,
            text=self.translation.tr('log_to_txt_checkbox'),
            variable=self.log_to_txt_var
        )
        log_to_txt_checkbox.pack(anchor="w", pady=8)

        animations_frame = ctk.CTkFrame(
            scrollable,
            fg_color="transparent"
        )
        animations_frame.pack(fill="x", pady=10, padx=18)

        animations_row = ctk.CTkFrame(animations_frame, fg_color="transparent")
        animations_row.pack(anchor="w", fill="x", pady=8)

        animations_checkbox = MD3Switch(
            animations_row,
            text=self.translation.tr('animations_checkbox'),
            variable=self.animations_enabled_var,
            state="disabled"
        )
        animations_checkbox.pack(side="left")

        animations_note = ctk.CTkLabel(
            animations_row,
            text=f"({self.translation.tr('animations_coming_soon')})",
            font=("Arial", 12),
            text_color=MaterialColors.get_color('on_surface_variant', dark_mode)
        )
        animations_note.pack(side="left", padx=(10, 0))

        separator2 = ctk.CTkFrame(
            scrollable,
            fg_color=MaterialColors.get_color('outline_variant', dark_mode),
            height=1
        )
        separator2.pack(fill="x", padx=18, pady=(10, 10))

        # Пинг
        ping_frame = ctk.CTkFrame(
            scrollable,
            fg_color="transparent"
        )
        ping_frame.pack(fill="x", pady=10, padx=18)

        ping_top_frame = ctk.CTkFrame(
            ping_frame,
            fg_color="transparent"
        )
        ping_top_frame.pack(fill="x", pady=(0, 4))

        ping_label_widget = MD3Label(
            ping_top_frame,
            text=self.translation.tr('ping_label'),
            typography='label_large'
        )
        ping_label_widget.pack(side="left", pady=(0, 0))

        ping_entry = MD3Entry(
            ping_frame,
            textvariable=self.default_ping_var,
            width=150,
            height=36
        )
        ping_entry.pack(anchor="w", pady=(0, 4))

        ping_note_label = MD3Label(
            ping_frame,
            text=self.translation.tr('ping_note'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant', dark_mode),
            wraplength=400,
            justify="left"
        )
        ping_note_label.pack(anchor="w", pady=(0, 8))

        separator3 = ctk.CTkFrame(
            scrollable,
            fg_color=MaterialColors.get_color('outline_variant', dark_mode),
            height=1
        )
        separator3.pack(fill="x", padx=18, pady=(10, 10))

        # Обновления
        update_frame = ctk.CTkFrame(
            scrollable,
            fg_color="transparent"
        )
        update_frame.pack(fill="x", pady=10, padx=18)

        version_row = ctk.CTkFrame(
            update_frame,
            fg_color="transparent"
        )
        version_row.pack(fill="x", pady=(8, 4))

        current_ver_label = MD3Label(
            version_row,
            text=self.translation.tr('current_version').format(UpdateChecker.get_current_version()),
            typography='label_large'
        )
        current_ver_label.pack(side="left", anchor="w")

        self.update_button = MD3Button(
            version_row,
            text=self.translation.tr('check_updates'),
            command=self.check_updates,
            button_type='outlined',
            size='small'
        )
        self.update_button.pack(side="right", anchor="e")

        region_text = self.translation.tr('your_region').format(
            get_display_region(self.app)
        )
        self.region_label = MD3Label(
            update_frame,
            text=region_text,
            typography='label_large'
        )
        self.region_label.pack(anchor="w", pady=(0, 8))

        # Добавляем небольшой отступ внизу для удобства скролла
        bottom_spacer = ctk.CTkFrame(
            scrollable,
            fg_color="transparent",
            height=30
        )
        bottom_spacer.pack(fill="x")

    def check_updates(self):
        self.update_button.configure(
            state="disabled",
            text=self.translation.tr('update_checking')
        )

        def worker():
            latest_version, message = UpdateChecker.check_for_updates()

            def finish():
                self.update_button.configure(
                    state="normal",
                    text=self.translation.tr('check_updates')
                )
                if latest_version:
                    self.show_update_dialog(latest_version, message)
                else:
                    if message == "up_to_date":
                        msg = self.translation.tr('current_version').format(UpdateChecker.get_current_version()) + " " + self.translation.tr('update_not_available')
                    elif message == "update_check_error":
                        msg = self.translation.tr('update_error')
                    else:
                        msg = message
                    messagebox.showinfo(
                        self.translation.tr('update_not_available'),
                        msg
                    )

            self.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def show_update_dialog(self, latest_version, message):
        update_url = UPDATE_DOWNLOAD_URL

        dialog = ctk.CTkToplevel(self)
        dialog.title(self.translation.tr('update_available'))
        dialog.geometry("420x210")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.transient(self)

        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - dialog.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        msg_lbl = ctk.CTkLabel(
            frame,
            text=self.translation.tr('update_message').format(latest_version),
            font=("Arial", 14),
            wraplength=360,
            justify="left"
        )
        msg_lbl.pack(pady=(10, 16))

        btns = ctk.CTkFrame(frame, fg_color="transparent")
        btns.pack(fill="x", pady=(8, 0))

        def open_update():
            dialog.destroy()
            try:
                autoupdate_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autoupdate.py")
                if os.path.exists(autoupdate_script):
                    subprocess.Popen([sys.executable, autoupdate_script, "--force"])
                    if hasattr(self, 'app') and hasattr(self.app, 'root'):
                        self.app.root.destroy()
                    elif hasattr(self, 'root'):
                        self.root.destroy()
                    return
            except Exception:
                pass
            webbrowser.open(update_url)

        def close_dialog():
            dialog.destroy()

        update_btn = MD3Button(
            btns,
            text=self.translation.tr('update_btn_update'),
            command=open_update,
            button_type='filled',
            size='small'
        )
        update_btn.pack(side="right", padx=(10, 0))

        ok_btn = MD3Button(
            btns,
            text=self.translation.tr('update_btn_ok'),
            command=close_dialog,
            button_type='outlined',
            size='small'
        )
        ok_btn.pack(side="right")

    def destroy(self):
        super().destroy()