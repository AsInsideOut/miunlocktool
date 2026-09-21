import sys
import os
import json
import webbrowser
import threading
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
    return "8.0"


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

        welcome_text = self.translation.tr('welcome_text')

        text_widget = ctk.CTkTextbox(
            text_frame,
            wrap="word",
            font=MaterialTypography.BODY_MEDIUM,
            fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
            text_color=MaterialColors.get_color('on_surface', dark_mode),
            border_width=0,
            height=200
        )
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", welcome_text)
        text_widget.configure(state="disabled")

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
        for alpha in [0.12, 0.28, 0.45, 0.65, 0.82, 1.0]:
            self.after(int(alpha * 90), lambda level=alpha: self.attributes("-alpha", level))

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
        # Чекбокс называется «Отключить анимации», поэтому его True означает,
        # что фактические анимации выключены.
        self.animations_enabled_var = ctk.BooleanVar(
            value=not bool(self.app.settings.get('animations_enabled', True))
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
        for alpha in [0.15, 0.35, 0.6, 0.8, 1.0]:
            self.after(int(alpha * 120), lambda level=alpha: self.attributes('-alpha', level))
        self.attributes('-alpha', 1.0)

    def _animate_out(self):
        self.grab_release()
        if not self.app.settings.get('animations_enabled', True):
            self._final_close()
            return
        for alpha in [0.9, 0.7, 0.45, 0.2, 0.0]:
            self.after(int((1.0 - alpha) * 90), lambda level=alpha: self.attributes('-alpha', level))
        self.after(350, self._final_close)

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
            self.app.settings['animations_enabled'] = not bool(self.animations_enabled_var.get())

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
        self.about_btn.pack(fill="x", padx=12, pady=(20, 8))

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
                def move_old(step):
                    if old_widget.winfo_exists():
                        try:
                            old_widget.place_configure(y=-step * 10)
                        except Exception:
                            pass

                for step in range(8):
                    self.after(step * 18, lambda s=step: move_old(s))

                def destroy_old():
                    if old_widget.winfo_exists():
                        old_widget.destroy()

                self.after(120, destroy_old)
            else:
                old_widget.destroy()

        new_widget = new_widget_factory()
        new_widget.place(in_=stage, x=0, y=26, relwidth=1, relheight=1)

        if animations_enabled:
            def move_new(step):
                if new_widget.winfo_exists():
                    try:
                        new_widget.place_configure(y=max(0, 26 - step * 5))
                    except Exception:
                        pass

            for step in range(8):
                self.after(step * 18, lambda s=step: move_new(s))
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

            about_text = ctk.CTkTextbox(
                frame,
                wrap="word",
                font=MaterialTypography.BODY_MEDIUM,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                text_color=MaterialColors.get_color('on_surface', dark_mode),
                border_width=0,
                cursor="arrow",
                height=520
            )
            about_text.pack(fill="both", expand=True, padx=20, pady=20)
            about_text.insert("1.0", self.translation.tr('about_content'))
            about_text.configure(state="disabled")
            return frame

        self._animate_section_switch(build, width_mode='wide')

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

            general_text = ctk.CTkTextbox(
                frame,
                wrap="word",
                font=MaterialTypography.BODY_MEDIUM,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                text_color=MaterialColors.get_color('on_surface', dark_mode),
                border_width=0,
                cursor="arrow",
                height=520
            )
            general_text.pack(fill="both", expand=True, padx=20, pady=20)
            general_text.insert("1.0", self.translation.tr('general_content'))
            general_text.configure(state="disabled")
            return frame

        self._animate_section_switch(build, width_mode='wide')

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

            if self.translation.language == 'ru':
                cookies_text = """Получение токена

Инструкция для всех браузеров:

1. Скачайте расширение Cookie Editor

2. Авторизуйтесь в аккаунт, предварительно
выйдя из него, на сайте Mi Community
http://c.mi.com/global

3. В окне Cookie Editor извлеките
New_bbs_ServiceToken и скопируйте его

Особенности работы:

1. Все время в скрипте является Пекинским
2. Регион в Mi Community стоит Global"""
            elif self.translation.language == 'id':
                cookies_text = """Mendapatkan token

Instruksi untuk semua browser:

1. Unduh ekstensi Cookie Editor

2. Masuk ke akun Anda (setelah keluar)
   di situs web Mi Community
   http://c.mi.com/global

3. Di jendela Cookie Editor, ekstrak
   New_bbs_ServiceToken dan salin

Catatan penting:

1. Semua waktu dalam skrip adalah waktu Beijing
2. Region akun Mi Community diatur ke Global"""
            elif self.translation.language == 'es':
                cookies_text = """Obteniendo token

Instrucciones para todos los navegadores:

1. Descargue la extensión Cookie Editor

2. Inicie sesión en su cuenta (después de cerrar sesión)
   en el sitio web de Mi Community
   http://c.mi.com/global

3. En la ventana de Cookie Editor, extraiga
   New_bbs_ServiceToken y cópielo

Notas importantes:

1. Todas las horas en el script son hora de Pekín
2. La región en Mi Community está configurada como Global"""
            elif self.translation.language == 'zh':
                cookies_text = """获取令牌

所有浏览器的说明：

1. 下载Cookie Editor扩展

2. 登录您的账户（先退出）
   在小米社区网站
   http://c.mi.com/global

3. 在Cookie Editor窗口中提取
   New_bbs_ServiceToken并复制

重要说明：

1. 脚本中的所有时间均为北京时间
2. Mi Community区域设置为全球"""
            else:
                cookies_text = """Getting token

1. Download the Cookie Editor extension

2. Log in to your account (after logging out)
   on the Mi Community website
   http://c.mi.com/global

3. In the Cookie Editor window, extract
   New_bbs_ServiceToken and copy it

Important notes:

1. All times in the script are Beijing time
2. Region in Mi Community is set to Global"""

            cookies_textbox = ctk.CTkTextbox(
                frame,
                wrap="word",
                font=MaterialTypography.BODY_MEDIUM,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                text_color=MaterialColors.get_color('on_surface', dark_mode),
                border_width=0,
                cursor="arrow",
                height=520
            )
            cookies_textbox.pack(fill="both", expand=True, padx=20, pady=20)
            cookies_textbox.insert("1.0", cookies_text)
            cookies_textbox.configure(state="disabled")
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

            trouble_text = ctk.CTkTextbox(
                frame,
                wrap="word",
                font=MaterialTypography.BODY_MEDIUM,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                text_color=MaterialColors.get_color('on_surface', dark_mode),
                border_width=0,
                cursor="arrow",
                height=520
            )
            trouble_text.pack(fill="both", expand=True, padx=20, pady=20)
            trouble_text.insert("1.0", self.translation.tr('trouble_content'))
            trouble_text.configure(state="disabled")
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

            authors_text = ctk.CTkTextbox(
                frame,
                wrap="word",
                font=MaterialTypography.BODY_MEDIUM,
                fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
                text_color=MaterialColors.get_color('on_surface', dark_mode),
                border_width=0,
                cursor="arrow",
                height=520
            )
            authors_text.pack(fill="both", expand=True, padx=20, pady=20)
            authors_text.insert("1.0", self.translation.tr('authors_content'))
            authors_text.configure(state="disabled")
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

        animations_checkbox = MD3Switch(
            animations_frame,
            text=self.translation.tr('animations_checkbox'),
            variable=self.animations_enabled_var
        )
        animations_checkbox.pack(anchor="w", pady=8)

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