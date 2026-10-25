import os
import re
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

UPDATE_CHECK_URL_GLOBAL = "https://miunlock.su/version.txt"
UPDATE_CHECK_URL_RU = "https://miunlocktool.ru/version.txt"
UPDATE_DOWNLOAD_URL_GLOBAL = "https://miunlock.su/download/stable/pc/Latest_Release.zip"
UPDATE_DOWNLOAD_URL_RU = "https://miunlocktool.ru/download/stable/pc/Latest_Release.zip"

UPDATE_CHECK_URL = UPDATE_CHECK_URL_GLOBAL
UPDATE_DOWNLOAD_URL = UPDATE_DOWNLOAD_URL_GLOBAL


def get_update_check_url(lang=None):
    if lang == 'ru':
        return UPDATE_CHECK_URL_RU
    return UPDATE_CHECK_URL_GLOBAL


def get_update_download_url(lang=None):
    if lang == 'ru':
        return UPDATE_DOWNLOAD_URL_RU
    return UPDATE_DOWNLOAD_URL_GLOBAL


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
    return "8.2"


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
    def check_for_updates(lang=None):
        try:
            import requests
            current = UpdateChecker.get_current_version()
            current_num = UpdateChecker.extract_version_number(current)
            if not current_num:
                return None, "Не удалось определить текущую версию"

            if lang is None:
                try:
                    import __main__
                    if hasattr(__main__, 'app') and hasattr(__main__.app, 'translation'):
                        lang = __main__.app.translation.language
                except Exception:
                    pass

            check_url = get_update_check_url(lang)
            response = requests.get(check_url, timeout=5)
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

