import subprocess
import sys
import os
import hashlib
import random
import time
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox, colorchooser
import webbrowser
import re
import threading
import json
import colorsys
import requests as requests_lib

base_path = os.path.dirname(os.path.abspath(__file__))
miunlock_path = os.path.join(base_path, 'miunlock')
if miunlock_path not in sys.path:
    sys.path.insert(0, base_path)

res_path = os.path.join(base_path, 'res')
if res_path not in sys.path:
    sys.path.insert(0, res_path)
    sys.path.insert(0, base_path)

try:
    import customtkinter as ctk
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])
        import customtkinter as ctk
    except Exception as e:
        messagebox.showerror(
            "Installation Error",
            f"Failed to install customtkinter:\n{e}\n\n"
            "Try to install manually:\n"
            "pip install customtkinter"
        )
        sys.exit(1)

try:
    import ntplib
    import pytz
    import urllib3
    import statistics
    import requests
except ImportError:
    pass

try:
    from res.theme import *
    from res.api_handler import RequestHandler
    from res.settings import WelcomeWindow, InstructionsWindow, UpdateChecker
    from res.lang import Translation
    from res.xiaomi_auth import XiaomiAuthDialog
except ImportError:
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    res_path = os.path.join(base_path, 'res')
    if res_path not in sys.path:
        sys.path.insert(0, base_path)
        sys.path.insert(0, res_path)

    from theme import *
    from api_handler import RequestHandler
    from settings import WelcomeWindow, InstructionsWindow, UpdateChecker
    from lang import Translation
    from xiaomi_auth import XiaomiAuthDialog

# Всегда используем темную тему
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CURRENT_VERSION = "8.0"
VERSION_CODE = 700300

CONFIG_DIR = os.path.join(os.environ['APPDATA'], 'MiUnlockTool') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), '.config', 'MiUnlockTool')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

ntp_servers = [
    "time1.google.com", "time2.google.com", "time3.google.com", "time4.google.com", "time.android.com",
    "time.aws.com", "time.google.com", "time.cloudflare.com",
    "ntp.time.in.ua", "stratum1.net", "ntp5.stratum2.ru"
]

MI_SERVERS = ['sgp-api.buy.mi.com']

os.system('cls' if os.name == 'nt' else 'clear')


class MaterialColors:
    _colors = {
        'dark': {
            'primary': '#D0BCFF',
            'on_primary': '#381E72',
            'primary_container': '#4F378B',
            'on_primary_container': '#EADDFF',
            'secondary': '#CCC2DC',
            'on_secondary': '#332D41',
            'secondary_container': '#4A4458',
            'on_secondary_container': '#E8DEF8',
            'surface': '#1C1B1F',
            'on_surface': '#E6E1E5',
            'surface_variant': '#49454F',
            'on_surface_variant': '#CAC4D0',
            'background': '#1C1B1F',
            'on_background': '#E6E1E5',
            'error': '#F2B8B5',
            'on_error': '#601410',
            'error_container': '#8C1D18',
            'on_error_container': '#F9DEDC',
            'outline': '#938F99',
            'outline_variant': '#49454F',
            'surface_container_lowest': '#111112',
            'surface_container_low': '#212126',
            'surface_container': '#28282D',
            'surface_container_high': '#323239',
            'surface_container_highest': '#3D3D46'
        }
    }

    @classmethod
    def get_color(cls, name, dark_mode=True):
        return cls._colors['dark'].get(name, cls._colors['dark']['surface'])


class MD3Card(ctk.CTkFrame):
    def __init__(self, master, elevation=1, **kwargs):
        super().__init__(master, **kwargs)
        self.elevation = elevation
        self.configure(
            fg_color=MaterialColors.get_color('surface_container'),
            corner_radius=16,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )


class MD3Label(ctk.CTkLabel):
    def __init__(self, master, text="", typography='body_medium', text_color=None, **kwargs):
        font_styles = {
            'headline_medium': ("Arial", 24, "bold"),
            'title_large': ("Arial", 18, "bold"),
            'title_medium': ("Arial", 16, "bold"),
            'body_medium': ("Arial", 12),
            'body_small': ("Arial", 11),
            'label_large': ("Arial", 13)
        }
        font = font_styles.get(typography, ("Arial", 12))
        if text_color is None:
            text_color = MaterialColors.get_color('on_surface')
        super().__init__(master, text=text, font=font, text_color=text_color, **kwargs)


class MD3Button(ctk.CTkButton):
    def __init__(self, master, text="", button_type='filled', size='medium', command=None, **kwargs):
        heights = {'small': 34, 'medium': 40, 'large': 48}
        height = heights.get(size, 40)

        if button_type == 'filled':
            fg_color = MaterialColors.get_color('primary')
            hover_color = MaterialColors.get_color('primary_container')
            text_color = MaterialColors.get_color('on_primary')
            border_width = 0
        elif button_type == 'outlined':
            fg_color = 'transparent'
            hover_color = MaterialColors.get_color('surface_container_high')
            text_color = MaterialColors.get_color('primary')
            border_width = 1
            border_color = MaterialColors.get_color('outline')
        else:
            fg_color = 'transparent'
            hover_color = MaterialColors.get_color('surface_container_high')
            text_color = MaterialColors.get_color('primary')
            border_width = 0

        super().__init__(
            master, text=text, height=height, command=command,
            fg_color=fg_color, hover_color=hover_color, text_color=text_color,
            border_width=border_width, corner_radius=14, **kwargs
        )
        if button_type == 'outlined' and border_width > 0:
            self.configure(border_color=border_color)


class MD3SegmentedButton(ctk.CTkFrame):
    def __init__(self, master, values, variable, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.values = values
        self.variable = variable
        self.command = command
        self.buttons = []
        self.button_frame = None
        self.create_buttons()

    def create_buttons(self):
        if self.button_frame:
            self.button_frame.destroy()

        self.configure(fg_color=MaterialColors.get_color('surface_container'), corner_radius=24)

        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(fill="both", expand=True, padx=2, pady=2)

        self.buttons = []
        for i, value in enumerate(self.values):
            btn = ctk.CTkButton(
                self.button_frame,
                text=value,
                height=36,
                corner_radius=20,
                fg_color=MaterialColors.get_color('surface_container_low'),
                hover_color=MaterialColors.get_color('surface_container'),
                text_color=MaterialColors.get_color('on_surface')
            )
            btn.configure(command=lambda v=value: self.select(v))
            btn.pack(side="left", fill="both", expand=True, padx=2, pady=2)
            self.buttons.append(btn)

        current = self.variable.get()
        if current in self.values:
            self.select(current)

    def update_values(self, new_values):
        self.values = new_values
        self.create_buttons()

    def select(self, value):
        for btn, val in zip(self.buttons, self.values):
            if val == value:
                btn.configure(
                    fg_color=MaterialColors.get_color('primary'),
                    text_color=MaterialColors.get_color('on_primary')
                )
            else:
                btn.configure(
                    fg_color=MaterialColors.get_color('surface_container_low'),
                    text_color=MaterialColors.get_color('on_surface')
                )
        self.variable.set(value)
        if self.command:
            self.command(value)

    def update_colors(self):
        self.configure(fg_color=MaterialColors.get_color('surface_container'))
        for btn, val in zip(self.buttons, self.values):
            if self.variable.get() == val:
                btn.configure(
                    fg_color=MaterialColors.get_color('primary'),
                    text_color=MaterialColors.get_color('on_primary')
                )
            else:
                btn.configure(
                    fg_color=MaterialColors.get_color('surface_container_low'),
                    text_color=MaterialColors.get_color('on_surface')
                )


class MD3Entry(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            corner_radius=8,
            border_width=1,
            fg_color=MaterialColors.get_color('surface_container_lowest'),
            border_color=MaterialColors.get_color('outline'),
            text_color=MaterialColors.get_color('on_surface'),
            **kwargs
        )


def get_system_language():
    try:
        import locale
        lang = locale.getlocale()[0]
        if lang:
            lang_lower = lang.lower()
            if lang_lower.startswith("ru"):
                return "ru"
            elif lang_lower.startswith("id") or lang_lower.startswith("in") or "indonesian" in lang_lower:
                return "id"
            elif lang_lower.startswith("es") or "spanish" in lang_lower:
                return "es"
            elif lang_lower.startswith("pt") or "portuguese" in lang_lower:
                return "pt"
            elif lang_lower.startswith("zh") or "chinese" in lang_lower:
                return "zh"
    except Exception:
        pass

    env_lang = (os.environ.get("LANG", "") + os.environ.get("LANGUAGE", "")).lower()
    if "ru" in env_lang:
        return "ru"
    elif "id" in env_lang or "in" in env_lang or "indonesian" in env_lang:
        return "id"
    elif "es" in env_lang or "spanish" in env_lang:
        return "es"
    elif "pt" in env_lang or "portuguese" in env_lang:
        return "pt"
    elif "zh" in env_lang or "chinese" in env_lang:
        return "zh"

    return "en"


def get_user_timezone_offset_minutes():
    try:
        local_now = datetime.now().astimezone()
        offset = local_now.utcoffset()
        if offset is None:
            return 0
        return int(offset.total_seconds() // 60)
    except Exception:
        return 0


def get_user_region_by_utc_offset(offset_minutes):
    america_offsets = {-660, -600, -570, -540, -480, -420, -360, -300, -270, -240, -180, -120, -60}
    europe_offsets = {-60, 0, 60, 120, 180}
    asia_offsets = {180, 210, 240, 270, 300, 330, 345, 360, 390, 420, 480, 540, 600, 660, 720}

    if offset_minutes in america_offsets:
        return 'America'
    if offset_minutes in europe_offsets:
        return 'Europe'
    if offset_minutes in asia_offsets:
        return 'Asia'

    if offset_minutes < 0:
        return 'America'
    if offset_minutes > 0:
        return 'Asia'
    return 'Europe'


def detect_user_region():
    offset_minutes = get_user_timezone_offset_minutes()
    return get_user_region_by_utc_offset(offset_minutes)


def ensure_config_dir():
    try:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR, exist_ok=True)
        return True
    except Exception as e:
        print(f"Ошибка создания папки конфигурации: {e}")
        return False


def load_config():
    system_language = get_system_language()
    default_config = {
        'cookie': '',
        'language': system_language,
        'theme': 'Dark',
        'skip_cookie_check': False,
        'color_theme': 'Material 3',
        'custom_primary_color': '#D0BCFF',
        'log_to_txt': True,
        'first_run': True,
        'login_user': '',
        'login_pwd': '',
        'login_wb_id': '',
        'region': detect_user_region(),
        'animations_enabled': True
    }

    if not os.path.exists(CONFIG_FILE):
        return default_config

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if not isinstance(config, dict):
                print("Config file is corrupted, using default")
                return default_config
            merged = {**default_config, **config}
            merged['theme'] = 'Dark'

            if 'log_to_txt' not in merged or merged['log_to_txt'] is None:
                merged['log_to_txt'] = True

            if 'language' in config:
                merged['language'] = config['language']
            return merged
    except (json.JSONDecodeError, PermissionError, FileNotFoundError) as e:
        print(f"Error loading config: {e}, using default")
        return default_config
    except Exception as e:
        print(f"Unexpected error loading config: {e}, using default")
        return default_config


def save_config(config):
    try:
        if not ensure_config_dir():
            return False
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        return False


def _on_key_release(event):
    ctrl = (event.state & 0x4) != 0
    if event.keycode == 88 and ctrl and event.keysym.lower() != "x":
        event.widget.event_generate("<<Cut>>")
    if event.keycode == 86 and ctrl and event.keysym.lower() != "v":
        event.widget.event_generate("<<Paste>>")
    if event.keycode == 67 and ctrl and event.keysym.lower() != "c":
        event.widget.event_generate("<<Copy>>")


class XiaomiUnlockTool:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.translation = Translation(self.config.get('language', 'ru'))

        self.instructions_windows = []

        self.root.title(self.translation.tr('title'))

        # Responsive sizing: fits 700p/720p screens while supporting fullscreen expansion
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        default_w = 980
        default_h = 620
        if screen_h <= 720:
            default_h = min(620, max(540, screen_h - 70))
            default_w = min(980, max(800, screen_w - 40))
        pos_x = max(0, (screen_w - default_w) // 2)
        pos_y = max(0, (screen_h - default_h) // 2 - 20)
        self.root.geometry(f"{default_w}x{default_h}+{pos_x}+{pos_y}")
        self.root.minsize(800, 520)
        self.root.resizable(True, True)

        # Fullscreen bindings (F11 toggles, Escape exits)
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen, "+")
        self.root.bind("<Escape>", self.exit_fullscreen, "+")

        saved_theme_color = self.config.get('custom_primary_color', '#D0BCFF')
        if isinstance(saved_theme_color, str) and re.fullmatch(r'#[0-9A-Fa-f]{6}', saved_theme_color):
            self._load_custom_theme_palette(saved_theme_color)
        self.root.configure(fg_color=MaterialColors.get_color('background'))

        self.root.bind_all("<KeyRelease>", _on_key_release, "+")

        detected_region = detect_user_region()
        self.settings = {
            'full_log': False,
            'skip_cookie_check': self.config.get('skip_cookie_check', False),
            'theme': 'Dark',
            'color_theme': 'Material 3',
            'log_to_txt': self.config.get('log_to_txt', True),
            'language': self.config.get('language', 'ru'),
            'region': self.config.get('region', detected_region),
            'animations_enabled': self.config.get('animations_enabled', True)
        }
        self.skip_cookie_check_var = ctk.BooleanVar(value=self.settings.get('skip_cookie_check', False))
        self.log_to_txt_var = ctk.BooleanVar(value=self.settings.get('log_to_txt', True))
        self.animations_enabled_var = ctk.BooleanVar(
            value=not bool(self.settings.get('animations_enabled', True))
        )
        self.settings_language_var = ctk.StringVar(value=self.settings.get('language', 'ru'))
        self.config['theme'] = 'Dark'
        self.config['region'] = self.settings['region']

        self.cookie_value = ctk.StringVar(value=self.config.get('cookie', ''))
        self.language_var = ctk.StringVar(value=self.settings.get('language', self.translation.language))
        self.device_id = ctk.StringVar()
        self.status_var = ctk.StringVar(value=self.translation.tr('status_ready'))
        self.application_status_key = 'application_status_not_sent'
        self.application_status_var = ctk.StringVar(
            value=self.translation.tr('application_status').format(
                self.translation.tr(self.application_status_key)
            )
        )
        self.ping_var = ctk.StringVar(value=self.translation.tr('ping'))
        self.time_var = ctk.StringVar(value=self.translation.tr('time'))
        self.mode_var = ctk.StringVar(value=self.translation.tr('auto_mode_2'))
        self.manual_time_var = ctk.StringVar(value="59.1")
        self.auto_mode_index = 2

        self.cookie_value.trace_add('write', self.auto_save_cookie)

        self.manual_time_frame = None
        self.mode_segmented = None

        # Переменные для системы вкладок
        self.current_tab = "unlock"  # unlock, settings, mi_unlock
        self.tab_containers = {}
        self.tab_buttons = {}

        self.create_material_ui()

        self.request_handler = RequestHandler(self)

        self.start_beijing_time = None
        self.start_timestamp = None
        self.ping_measurement_done = threading.Event()
        self.measured_ping_http = None
        self.measured_ping_tcp = None

        self.show_welcome_if_needed()

    def auto_save_cookie(self, *args):
        try:
            self.config['cookie'] = self.cookie_value.get()
            save_config(self.config)
        except Exception as e:
            print(f"Ошибка автосохранения cookie: {e}")

    def open_telegram(self):
        try:
            webbrowser.open("https://t.me/miunlocktoolrevamp", new=2)
        except Exception as e:
            print(f"Telegram link open error: {e}")

    def open_github(self):
        try:
            webbrowser.open("https://github.com/AsInsideOut/miunlocktool", new=2)
        except Exception as e:
            print(f"GitHub link open error: {e}")

    def open_site(self):
        try:
            webbrowser.open("https://miunlock.su/", new=2)
        except Exception as e:
            print(f"Site link open error: {e}")

    def open_4pda(self):
        try:
            webbrowser.open("https://4pda.to/", new=2)
        except Exception as e:
            print(f"4PDA link open error: {e}")

    def open_mi_unlock_drivers(self):
        try:
            webbrowser.open(
                "https://drive.google.com/drive/folders/1awcuYgP6krpUICxi7GIcxVsvk74R7w_W?usp=sharing",
                new=2
            )
        except Exception as e:
            print(f"Mi Unlock drivers link open error: {e}")

    def set_application_status(self, status, status_key=None):
        if status_key:
            self.application_status_key = status_key
        self.root.after(
            0,
            lambda: self.application_status_var.set(
                self.translation.tr('application_status').format(status)
            )
        )

    def change_language(self, new_lang=None):
        if new_lang is None:
            new_lang = self.language_var.get()
        if new_lang == self.translation.language:
            return

        self.translation.language = new_lang
        self.settings['language'] = new_lang
        self.language_var.set(new_lang)
        self.save_settings()
        self.update_ui_text()

    def show_welcome_if_needed(self):
        first_run = self.config.get('first_run', True)
        if not first_run:
            return

        win = WelcomeWindow(self.root, self.translation, self)
        self.root.wait_window(win)

        if first_run:
            self.config['first_run'] = False
            self.config['cookie'] = self.cookie_value.get()
            save_config(self.config)

    def save_settings(self):
        try:
            if hasattr(self, 'skip_cookie_check_var'):
                self.settings['skip_cookie_check'] = bool(self.skip_cookie_check_var.get())
            if hasattr(self, 'log_to_txt_var'):
                self.settings['log_to_txt'] = bool(self.log_to_txt_var.get())
            if hasattr(self, 'animations_enabled_var'):
                self.settings['animations_enabled'] = not bool(self.animations_enabled_var.get())
            if hasattr(self, 'language_var'):
                self.settings['language'] = self.language_var.get()
            self.settings['theme'] = 'Dark'
            self.config['skip_cookie_check'] = self.settings['skip_cookie_check']
            self.config['theme'] = 'Dark'
            self.config['language'] = self.settings.get('language', self.translation.language)
            self.config['log_to_txt'] = self.settings['log_to_txt']
            self.config['animations_enabled'] = self.settings['animations_enabled']
            self.config['region'] = self.settings.get('region', detect_user_region())
            self.config['cookie'] = self.cookie_value.get()
            self.config['login_user'] = self.settings.get('login_user', '')
            self.config['login_pwd'] = self.settings.get('login_pwd', '')
            self.config['login_wb_id'] = self.settings.get('login_wb_id', '')

            save_config(self.config)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False

    def apply_theme(self, theme: str):
        self.settings['theme'] = 'Dark'
        ctk.set_appearance_mode('Dark')
        self.update_md3_colors()

    def update_colors(self):
        pass

    def create_material_ui(self):
        dark_mode = True

        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color=MaterialColors.get_color('background')
        )
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # === TOP BAR (без кнопок Mi Unlock и Инструкции) ===
        self.top_bar = MD3Card(self.main_container, elevation=1)
        self.top_bar.pack(fill="x", pady=(0, 8), padx=0)

        top_bar_inner = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        top_bar_inner.pack(fill="x", padx=18, pady=10)

        # Левая часть - заголовок и соцсети
        title_frame = ctk.CTkFrame(top_bar_inner, fg_color="transparent")
        title_frame.pack(side="left", fill="y")

        self.title_label = MD3Label(
            title_frame,
            text=self.translation.tr('main_title'),
            typography='headline_medium'
        )
        self.title_label.pack(anchor="w")

        self.social_stack = ctk.CTkFrame(title_frame, fg_color="transparent")
        self.social_stack.pack(anchor="w", pady=(5, 0))

        self.telegram_btn = ctk.CTkButton(
            self.social_stack,
            text=self.translation.tr('social_telegram'),
            width=104,
            height=30,
            corner_radius=10,
            fg_color="#5B8DEF",
            hover_color="#4A7AE6",
            text_color="#F8FBFF",
            border_width=0,
            command=self.open_telegram
        )
        self.telegram_btn.pack(side="left", padx=(0, 6))

        self.fourpda_btn = ctk.CTkButton(
            self.social_stack,
            text="4PDA",
            width=88,
            height=30,
            corner_radius=10,
            fg_color="#607D9B",
            hover_color="#506B85",
            text_color="#F5F8FC",
            border_width=0,
            command=self.open_4pda
        )
        self.fourpda_btn.pack(side="left", padx=(0, 6))

        self.github_btn = ctk.CTkButton(
            self.social_stack,
            text=self.translation.tr('social_github'),
            width=96,
            height=30,
            corner_radius=10,
            fg_color="#1B1F24",
            hover_color="#2A3138",
            text_color="#F3F4F6",
            border_width=0,
            command=self.open_github
        )
        self.github_btn.pack(side="left", padx=(0, 6))

        self.site_btn = ctk.CTkButton(
            self.social_stack,
            text=self._get_site_button_text(),
            width=118,
            height=30,
            corner_radius=10,
            fg_color=MaterialColors.get_color('surface_container_high'),
            hover_color=MaterialColors.get_color('surface_container_highest'),
            text_color=MaterialColors.get_color('on_surface'),
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant'),
            command=self.open_site
        )
        self.site_btn.pack(side="left")

        # Правая часть - язык, логин
        self.language_optionmenu_wrap = ctk.CTkFrame(
            top_bar_inner,
            fg_color="transparent",
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline')
        )
        self.language_optionmenu_wrap.pack(side="right", padx=(10, 0))

        self.language_optionmenu = ctk.CTkOptionMenu(
            self.language_optionmenu_wrap,
            values=['ru', 'en', 'id', 'es', 'zh', 'pt'],
            variable=self.language_var,
            width=96,
            height=30,
            corner_radius=10,
            font=("Arial", 12),
            fg_color=MaterialColors.get_color('surface_container_high'),
            button_color=MaterialColors.get_color('surface'),
            button_hover_color=MaterialColors.get_color('surface_container_highest'),
            dropdown_fg_color=MaterialColors.get_color('surface_container'),
            dropdown_hover_color=MaterialColors.get_color('surface_container_highest'),
            text_color=MaterialColors.get_color('on_surface'),
            command=self.change_language
        )
        self.language_optionmenu.pack(fill="both", expand=True)

        # === TAB NAVIGATION BAR ===
        self.tab_bar = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_bar.pack(fill="x", pady=(0, 8), padx=16)

        tab_buttons_frame = ctk.CTkFrame(self.tab_bar, fg_color="transparent")
        tab_buttons_frame.pack(anchor="center")

        self.tab_buttons['settings'] = MD3Button(
            tab_buttons_frame,
            text=self.translation.tr('tab_settings'),
            button_type='outlined',
            size='medium',
            command=lambda: self.switch_tab("settings")
        )
        self.tab_buttons['settings'].pack(side="left", padx=(0, 10))

        self.tab_buttons['unlock'] = MD3Button(
            tab_buttons_frame,
            text=self.translation.tr('tab_unlock'),
            button_type='filled',
            size='medium',
            command=lambda: self.switch_tab("unlock")
        )
        self.tab_buttons['unlock'].pack(side="left", padx=(0, 10))

        self.tab_buttons['mi_unlock'] = MD3Button(
            tab_buttons_frame,
            text=self.translation.tr('tab_mi_unlock'),
            button_type='outlined',
            size='medium',
            command=lambda: self.switch_tab("mi_unlock")
        )
        self.tab_buttons['mi_unlock'].pack(side="left", padx=(0, 0))

        # === CONTENT AREA ===
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=16)

        # Создаем контейнеры для каждой вкладки
        self.tab_containers['unlock'] = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.tab_containers['settings'] = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.tab_containers['mi_unlock'] = ctk.CTkFrame(self.content_area, fg_color="transparent")

        # Создаем UI для вкладки "Подача заявок"
        self._create_unlock_tab()

        # Создаем встроенную вкладку "Настройки и инструкции"
        self._create_settings_tab()

        # Создаем UI для вкладки "Mi Unlock"
        self._create_mi_unlock_tab()

        # Устанавливаем Авторежим #2 по умолчанию
        self.auto_mode_index = 2
        self.mode_var.set(self.translation.tr('auto_mode_2'))
        self.toggle_mode(self.mode_var.get())

        # Показываем первую вкладку по умолчанию
        self.switch_tab("unlock")

    def _create_unlock_tab(self):
        """Создает вкладку с параметрами подачи заявок"""
        dark_mode = True
        container = self.tab_containers['unlock']
        container.pack(fill="both", expand=True)

        left_column = ctk.CTkFrame(container, fg_color="transparent", width=460)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_column = ctk.CTkFrame(container, fg_color="transparent", width=460)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.params_card = MD3Card(left_column, elevation=2)
        self.params_card.pack(fill="both", expand=True)
        self.params_card.configure(corner_radius=18)

        card_header = ctk.CTkFrame(self.params_card, fg_color="transparent", height=46)
        card_header.pack(fill="x", padx=18, pady=(12, 0))
        card_header.pack_propagate(False)

        self.params_label_bg = ctk.CTkFrame(
            card_header,
            fg_color='#202020',
            corner_radius=12,
            border_width=0,
            height=36
        )
        self.params_label_bg.pack(side="left")

        # Исправлено: используем перевод для заголовка вкладки
        self.params_label = MD3Label(
            self.params_label_bg,
            text=self.translation.tr('tab_unlock'),
            typography='title_large',
        )
        self.params_label.pack(side="left", padx=12, pady=2)

        card_content = ctk.CTkScrollableFrame(self.params_card, fg_color="transparent")
        card_content.pack(fill="both", expand=True, padx=12, pady=(8, 10))

        mode_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(0, 10))

        self.mode_label = MD3Label(
            mode_frame,
            text=self.translation.tr('mode_label'),
            typography='label_large'
        )
        self.mode_label.pack(anchor="w", pady=(0, 4))

        self.mode_segmented = MD3SegmentedButton(
            mode_frame,
            values=[self.translation.tr('auto_mode_2'), self.translation.tr('manual_mode')],
            variable=self.mode_var,
            command=self.toggle_mode
        )
        self.mode_segmented.pack(fill="x")

        self.manual_time_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        self.manual_time_frame.pack(fill="x", pady=(0, 10))

        self.manual_time_label = MD3Label(
            self.manual_time_frame,
            text=self.translation.tr('manual_time_label'),
            typography='label_large'
        )
        self.manual_time_label.pack(anchor="w", pady=(0, 4))

        manual_time_input = ctk.CTkFrame(self.manual_time_frame, fg_color="transparent")
        manual_time_input.pack(fill="x")

        self.manual_time_entry = MD3Entry(
            manual_time_input,
            textvariable=self.manual_time_var,
            placeholder_text="59.1",
            width=120
        )
        self.manual_time_entry.pack(side="left")

        self.manual_time_hint = MD3Label(
            manual_time_input,
            text=self.translation.tr('manual_time_hint'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant')
        )
        self.manual_time_hint.pack(side="left", padx=(12, 0))

        cookie_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        cookie_frame.pack(fill="x", pady=(0, 12))

        cookie_header = ctk.CTkFrame(cookie_frame, fg_color="transparent")
        cookie_header.pack(fill="x", pady=(0, 4))

        self.cookie_text_label = MD3Label(
            cookie_header,
            text=self.translation.tr('cookie_label'),
            typography='label_large'
        )
        self.cookie_text_label.pack(side="left", anchor="w")

        self.login_btn = MD3Button(
            cookie_header,
            text=self.translation.tr('login_btn'),
            button_type='outlined',
            size='small',
            command=self.open_login_dialog
        )
        self.login_btn.pack(side="right")

        # Исправлено: placeholder теперь всегда "new_bbs_ServiceToken"
        self.cookie_entry = MD3Entry(
            cookie_frame,
            textvariable=self.cookie_value,
            placeholder_text="new_bbs_ServiceToken",
            height=36
        )
        self.cookie_entry.pack(fill="x")
        self.cookie_entry.bind("<Return>", lambda event: self.start_process())

        self.check_eligibility_btn = MD3Button(
            cookie_frame,
            text=self.translation.tr('check_eligibility_btn'),
            button_type='outlined',
            size='small',
            command=self.check_eligibility
        )
        self.check_eligibility_btn.pack(fill="x", pady=(8, 0))

        self.info_card = MD3Card(card_content, elevation=1)
        self.info_card.pack(fill="x", pady=(0, 12))
        self.info_card.configure(corner_radius=16)

        info_content = ctk.CTkFrame(self.info_card, fg_color="transparent")
        info_content.pack(fill="x", padx=12, pady=10)

        self.info_label = MD3Label(
            info_content,
            text=self.translation.tr('info'),
            typography='title_medium'
        )
        self.info_label.pack(anchor="w", pady=(0, 6))

        status_item = ctk.CTkFrame(info_content, fg_color="transparent")
        status_item.pack(fill="x", pady=(0, 4))

        status_icon = ctk.CTkLabel(
            status_item,
            text="⏳",
            font=("Arial", 16),
            width=24
        )
        status_icon.pack(side="left")

        self.status_text = MD3Label(
            status_item,
            textvariable=self.status_var,
            typography='body_medium'
        )
        self.status_text.pack(side="left", padx=(12, 0))

        time_item = ctk.CTkFrame(info_content, fg_color="transparent")
        time_item.pack(fill="x", pady=(0, 4))

        time_icon = ctk.CTkLabel(
            time_item,
            text="🕐",
            font=("Arial", 16),
            width=24
        )
        time_icon.pack(side="left")

        self.time_text = MD3Label(
            time_item,
            textvariable=self.time_var,
            typography='body_medium'
        )
        self.time_text.pack(side="left", padx=(12, 0))

        application_status_item = ctk.CTkFrame(info_content, fg_color="transparent")
        application_status_item.pack(fill="x")

        application_status_icon = ctk.CTkLabel(
            application_status_item,
            text="•",
            font=("Arial", 18),
            width=24,
            anchor="center"
        )
        application_status_icon.pack(side="left")

        self.application_status_text = MD3Label(
            application_status_item,
            textvariable=self.application_status_var,
            typography='body_medium'
        )
        self.application_status_text.pack(side="left", padx=(12, 0))

        button_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        button_frame.pack(fill="x", pady=(0, 6))

        self.start_button = MD3Button(
            button_frame,
            text=self.translation.tr('submit_application'),
            button_type='filled',
            size='large',
            command=self.start_process
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.exit_bg = ctk.CTkFrame(
            button_frame,
            fg_color='#202020',
            corner_radius=12,
            border_width=0,
            height=44
        )
        self.exit_bg.pack(side="right")

        self.exit_button = MD3Button(
            self.exit_bg,
            text=self.translation.tr('exit'),
            button_type='text',
            size='small',
            command=self.exit_application
        )
        self.exit_button.pack(fill="both", expand=True, padx=10, pady=4)

        desc_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        desc_frame.pack(fill="x", pady=(10, 0))

        self.desc_label = MD3Label(
            desc_frame,
            text=self.translation.tr('desc'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant'),
            wraplength=420,
            justify="left"
        )
        self.desc_label.pack(fill="x")

        def on_left_col_configure(event):
            try:
                new_wrap = max(260, event.width - 60)
                if hasattr(self, 'desc_label') and self.desc_label.winfo_exists():
                    self.desc_label.configure(wraplength=new_wrap)
            except Exception:
                pass
        left_column.bind("<Configure>", on_left_col_configure, add="+")

        self.log_card = MD3Card(right_column, elevation=2)
        self.log_card.pack(fill="both", expand=True)
        self.log_card.configure(corner_radius=18)

        log_header = ctk.CTkFrame(self.log_card, fg_color="transparent", height=46)
        log_header.pack(fill="x", padx=18, pady=(12, 0))
        log_header.pack_propagate(False)

        self.log_label_bg = ctk.CTkFrame(
            log_header,
            fg_color='#202020',
            corner_radius=6,
            border_width=0,
            height=34,
            width=160
        )
        self.log_label_bg.pack(side="left")

        self.log_label = MD3Label(
            self.log_label_bg,
            text=self.translation.tr('execution_log'),
            typography='title_large',
            text_color='#FFFFFF'
        )
        self.log_label.pack(side="left", padx=12, pady=2)

        log_controls = ctk.CTkFrame(log_header, fg_color="transparent")
        log_controls.pack(side="right")

        self.clear_log_bg = ctk.CTkFrame(
            log_controls,
            fg_color='#202020',
            corner_radius=12,
            border_width=0,
            height=36,
            width=118
        )
        self.clear_log_bg.pack(side="left")

        self.clear_log_btn = MD3Button(
            self.clear_log_bg,
            text=self.translation.tr('clear_log_btn'),
            button_type='text',
            size='small',
            command=self.clear_log
        )
        self.clear_log_btn.pack(fill="both", expand=True, padx=12, pady=4)

        log_content = ctk.CTkFrame(self.log_card, fg_color="transparent")
        log_content.pack(fill="both", expand=True, padx=18, pady=(8, 12))

        log_text_container = ctk.CTkFrame(
            log_content,
            fg_color=MaterialColors.get_color('surface_container_lowest'),
            corner_radius=8,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        log_text_container.pack(fill="both", expand=True)

        self.log_text = ctk.CTkTextbox(
            log_text_container,
            wrap="word",
            font=("Consolas", 12),
            fg_color=MaterialColors.get_color('surface_container_lowest'),
            text_color=MaterialColors.get_color('on_surface'),
            border_width=0
        )
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            log_text_container,
            command=self.log_text.yview
        )
        scrollbar.pack(side="right", fill="y")

        self.log_text.configure(yscrollcommand=scrollbar.set)
        self.log_text.configure(state='disabled')

    def _create_settings_tab(self):
        """Создает встроенную вкладку настроек и инструкций внутри основного интерфейса."""
        container = self.tab_containers['settings']
        container.pack(fill="both", expand=True)

        sidebar = ctk.CTkFrame(
            container,
            fg_color=MaterialColors.get_color('surface_container'),
            width=220,
            corner_radius=16,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        sidebar.pack(side="left", fill="both", padx=(0, 12), pady=8)
        sidebar.pack_propagate(False)

        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(side="right", fill="both", expand=True)

        self.settings_sidebar_buttons = {}
        self.settings_content_area = ctk.CTkFrame(content, fg_color="transparent")
        self.settings_content_area.pack(fill="both", expand=True)

        sections = [
            ('about', self.translation.tr('about_title')),
            ('general', self.translation.tr('general_title')),
            ('cookies', self.translation.tr('cookies_title')),
            ('trouble', self.translation.tr('trouble_title')),
            ('authors', self.translation.tr('authors_title')),
            ('settings', self.translation.tr('settings')),
        ]

        for section_key, title in sections:
            btn = MD3Button(
                sidebar,
                text=title,
                button_type='outlined',
                size='medium',
                command=lambda key=section_key: self._show_settings_section(key)
            )
            btn.pack(fill="x", padx=12, pady=(10 if section_key == 'about' else 6), anchor="w")
            self.settings_sidebar_buttons[section_key] = btn

        self.settings_active_section = 'about'
        self._show_settings_section('about')

    def _show_settings_section(self, section_name):
        self.settings_active_section = section_name

        for key, btn in self.settings_sidebar_buttons.items():
            if key == section_name:
                btn.configure(
                    fg_color=MaterialColors.get_color('primary'),
                    hover_color=MaterialColors.get_color('primary_container'),
                    text_color=MaterialColors.get_color('on_primary'),
                    border_width=0
                )
            else:
                btn.configure(
                    fg_color='transparent',
                    hover_color=MaterialColors.get_color('surface_container_high'),
                    text_color=MaterialColors.get_color('primary'),
                    border_width=1,
                    border_color=MaterialColors.get_color('outline')
                )

        for widget in self.settings_content_area.winfo_children():
            widget.destroy()

        if section_name in ('about', 'general', 'trouble', 'authors'):
            key = f"{section_name}_content"
            content_text = self.translation.tr(key)
            panel = MD3Card(self.settings_content_area, fg_color=MaterialColors.get_color('surface_container_low'), corner_radius=16, border_width=1, border_color=MaterialColors.get_color('outline_variant'))
            panel.pack(fill="both", expand=True, padx=8, pady=8)

            textbox = ctk.CTkTextbox(
                panel,
                wrap="word",
                font=("Arial", 14),
                fg_color=MaterialColors.get_color('surface_container_low'),
                text_color=MaterialColors.get_color('on_surface'),
                border_width=0,
                height=120
            )
            textbox.pack(fill="both", expand=True, padx=18, pady=18)
            textbox.insert("1.0", content_text)
            textbox.configure(state="disabled")
            self._animate_settings_panel(panel)
            return

        if section_name == 'cookies':
            panel = MD3Card(self.settings_content_area, fg_color=MaterialColors.get_color('surface_container_low'), corner_radius=16, border_width=1, border_color=MaterialColors.get_color('outline_variant'))
            panel.pack(fill="both", expand=True, padx=8, pady=8)

            if self.translation.language == 'ru':
                content_text = "Получение токена\n\nИнструкция для всех браузеров:\n\n1. Скачайте расширение Cookie Editor\n\n2. Авторизуйтесь в аккаунт, предварительно выйдя из него, на сайте Mi Community\nhttp://c.mi.com/global\n\n3. В окне Cookie Editor извлеките New_bbs_ServiceToken и скопируйте его\n\nОсобенности работы:\n\n1. Все время в скрипте является Пекинским\n2. Регион в Mi Community стоит Global"
            elif self.translation.language == 'id':
                content_text = "Mendapatkan token\n\nInstruksi untuk semua browser:\n\n1. Unduh ekstensi Cookie Editor\n\n2. Masuk ke akun Anda (setelah keluar) di situs web Mi Community\nhttp://c.mi.com/global\n\n3. Di jendela Cookie Editor, ekstrak New_bbs_ServiceToken dan salin\n\nCatatan penting:\n\n1. Semua waktu dalam skrip adalah waktu Beijing\n2. Region akun Mi Community diatur ke Global"
            elif self.translation.language == 'es':
                content_text = "Obteniendo token\n\nInstrucciones para todos los navegadores:\n\n1. Descargue la extensión Cookie Editor\n\n2. Inicie sesión en su cuenta (después de cerrar sesión) en el sitio web de Mi Community\nhttp://c.mi.com/global\n\n3. En la ventana de Cookie Editor, extraiga New_bbs_ServiceToken y cópielo\n\nNotas importantes:\n\n1. Todas las horas en el script son hora de Pekín\n2. La región en Mi Community está configurada como Global"
            elif self.translation.language == 'zh':
                content_text = "获取令牌\n\n所有浏览器的说明：\n\n1. 下载Cookie Editor扩展\n\n2. 登录您的账户（先退出）在小米社区网站\nhttp://c.mi.com/global\n\n3. 在Cookie Editor窗口中提取 New_bbs_ServiceToken 并复制\n\n重要说明：\n\n1. 脚本中的所有时间均为北京时间\n2. Mi Community区域设置为全球"
            elif self.translation.language == 'pt':
                content_text = "Obtendo token\n\nInstruções para todos os navegadores:\n\n1. Baixe a extensão Cookie Editor\n\n2. Faça login na sua conta (após sair) no site da Mi Community\nhttp://c.mi.com/global\n\n3. Na janela do Cookie Editor, extraia New_bbs_ServiceToken e copie-o\n\nNotas importantes:\n\n1. Todos os horários no script são no horário de Pequim\n2. A região na Mi Community está configurada como Global"
            else:
                content_text = "Getting token\n\n1. Download the Cookie Editor extension\n\n2. Log in to your account (after logging out) on the Mi Community website\nhttp://c.mi.com/global\n\n3. In the Cookie Editor window, extract New_bbs_ServiceToken and copy it\n\nImportant notes:\n\n1. All times in the script are Beijing time\n2. Region in Mi Community is set to Global"

            textbox = ctk.CTkTextbox(
                panel,
                wrap="word",
                font=("Arial", 14),
                fg_color=MaterialColors.get_color('surface_container_low'),
                text_color=MaterialColors.get_color('on_surface'),
                border_width=0,
                height=120
            )
            textbox.pack(fill="both", expand=True, padx=18, pady=18)
            textbox.insert("1.0", content_text)
            textbox.configure(state="disabled")
            self._animate_settings_panel(panel)
            return

        if section_name == 'settings':
            panel = MD3Card(self.settings_content_area, fg_color=MaterialColors.get_color('surface_container_low'), corner_radius=16, border_width=1, border_color=MaterialColors.get_color('outline_variant'))
            panel.pack(fill="both", expand=True, padx=8, pady=8)

            scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=8, pady=8)

            language_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            language_frame.pack(fill="x", pady=16)
            MD3Label(language_frame, text=self.translation.tr('language_label'), typography='label_large').pack(anchor="w")
            ctk.CTkOptionMenu(
                language_frame,
                values=['ru', 'en', 'id', 'es', 'zh', 'pt'],
                variable=self.language_var,
                width=200,
                height=40,
                corner_radius=12,
                font=("Arial", 13),
                fg_color=MaterialColors.get_color('surface_container_high'),
                button_color=MaterialColors.get_color('primary'),
                button_hover_color=MaterialColors.get_color('primary_container'),
                text_color=MaterialColors.get_color('on_surface'),
                dropdown_fg_color=MaterialColors.get_color('surface_container'),
                dropdown_hover_color=MaterialColors.get_color('surface_container_highest'),
                dropdown_text_color=MaterialColors.get_color('on_surface'),
                command=self.change_language
            ).pack(anchor="w", pady=(4, 0))

            separator_color = ctk.CTkFrame(scroll, fg_color=MaterialColors.get_color('outline_variant'), height=1)
            separator_color.pack(fill="x", padx=0, pady=(10, 10))

            color_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            color_frame.pack(fill="x", pady=10)

            MD3Label(
                color_frame,
                text=self.translation.tr('theme_color_label'),
                typography='label_large'
            ).pack(anchor="w")

            color_controls = ctk.CTkFrame(color_frame, fg_color="transparent")
            color_controls.pack(fill="x", pady=(6, 0))

            self.theme_color_entry = ctk.CTkEntry(
                color_controls,
                width=180,
                height=40,
                corner_radius=10,
                font=("Arial", 13),
                placeholder_text="#D0BCFF",
                fg_color=MaterialColors.get_color('surface_container_high'),
                border_color=MaterialColors.get_color('outline'),
                text_color=MaterialColors.get_color('on_surface')
            )
            self.theme_color_entry.pack(side="left", padx=(0, 8))
            self.theme_color_entry.insert(0, self.settings.get('custom_primary_color', '#D0BCFF'))

            self.theme_color_preview = ctk.CTkFrame(
                color_controls,
                width=40,
                height=40,
                corner_radius=10,
                fg_color=self.settings.get('custom_primary_color', '#D0BCFF')
            )
            self.theme_color_preview.pack(side="left", padx=(0, 8))
            self.theme_color_preview.pack_propagate(False)

            MD3Button(
                color_controls,
                text=self.translation.tr('theme_color_picker'),
                button_type='outlined',
                size='small',
                command=self.choose_theme_color
            ).pack(side="left", padx=(0, 8))

            MD3Button(
                color_controls,
                text=self.translation.tr('theme_color_apply'),
                button_type='filled',
                size='small',
                command=self.apply_custom_theme_color
            ).pack(side="left")

            MD3Label(
                color_frame,
                text=self.translation.tr('theme_color_hint'),
                typography='body_small'
            ).pack(anchor="w", pady=(6, 0))

            separator0 = ctk.CTkFrame(scroll, fg_color=MaterialColors.get_color('outline_variant'), height=1)
            separator0.pack(fill="x", padx=0, pady=(10, 10))

            check_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            check_frame.pack(fill="x", pady=10)

            checkbox_style = {
                'height': 32,
                'corner_radius': 8,
                'border_width': 2,
                'border_color': MaterialColors.get_color('outline'),
                'fg_color': MaterialColors.get_color('primary'),
                'hover_color': MaterialColors.get_color('primary_container'),
                'text_color': MaterialColors.get_color('on_surface'),
                'font': ("Arial", 13)
            }

            ctk.CTkCheckBox(
                check_frame,
                text=self.translation.tr('cookie_checkbox'),
                variable=self.skip_cookie_check_var,
                command=self.save_settings,
                **checkbox_style
            ).pack(anchor="w", pady=8)
            ctk.CTkCheckBox(
                check_frame,
                text=self.translation.tr('log_to_txt_checkbox'),
                variable=self.log_to_txt_var,
                command=self.save_settings,
                **checkbox_style
            ).pack(anchor="w", pady=8)
            ctk.CTkCheckBox(
                check_frame,
                text=self.translation.tr('animations_checkbox'),
                variable=self.animations_enabled_var,
                command=self.toggle_animations,
                state="normal",
                **{
                    **checkbox_style,
                    'fg_color': MaterialColors.get_color('surface_container_high'),
                    'hover_color': MaterialColors.get_color('surface_container_high'),
                    'border_color': MaterialColors.get_color('outline_variant'),
                    'text_color': MaterialColors.get_color('on_surface_variant')
                }
            ).pack(anchor="w", pady=8)

            separator2 = ctk.CTkFrame(scroll, fg_color=MaterialColors.get_color('outline_variant'), height=1)
            separator2.pack(fill="x", padx=0, pady=(10, 10))

            version_frame = ctk.CTkFrame(scroll, fg_color="transparent")
            version_frame.pack(fill="x", pady=10)
            MD3Label(version_frame, text=self.translation.tr('current_version').format(CURRENT_VERSION), typography='label_large').pack(anchor="w")
            self.update_button = MD3Button(
                version_frame,
                text=self.translation.tr('check_updates'),
                button_type='outlined',
                size='small',
                command=self.check_updates
            )
            self.update_button.pack(anchor="w", pady=(8, 0))
            self._animate_settings_panel(panel)
            return

    def choose_theme_color(self):
        """Открывает системный выбор цвета и подставляет HEX."""
        try:
            initial = self.settings.get('custom_primary_color', '#D0BCFF')
            result = colorchooser.askcolor(
                color=initial,
                title=self.translation.tr('theme_color_picker')
            )
            if result and result[1]:
                self.theme_color_entry.delete(0, "end")
                self.theme_color_entry.insert(0, result[1].upper())
                self.theme_color_preview.configure(fg_color=result[1])
        except Exception as e:
            print(f"Ошибка выбора цвета: {e}")

    def apply_custom_theme_color(self):
        """Применяет цвет темы из HEX или RGB (R,G,B)."""
        raw = self.theme_color_entry.get().strip()
        if not raw:
            return

        color = None
        if re.fullmatch(r'#?[0-9a-fA-F]{6}', raw):
            color = '#' + raw.lstrip('#').upper()
        else:
            rgb_match = re.fullmatch(
                r'\s*(\d{1,3})\s*[,;]\s*(\d{1,3})\s*[,;]\s*(\d{1,3})\s*',
                raw
            )
            if rgb_match:
                rgb = tuple(int(x) for x in rgb_match.groups())
                if all(0 <= x <= 255 for x in rgb):
                    color = '#{:02X}{:02X}{:02X}'.format(*rgb)

        if not color:
            messagebox.showerror(
                self.translation.tr('theme_color_error_title'),
                self.translation.tr('theme_color_error')
            )
            return

        self._set_custom_theme_color(color)
        self.theme_color_entry.delete(0, "end")
        self.theme_color_entry.insert(0, color)
        if hasattr(self, 'theme_color_preview'):
            self.theme_color_preview.configure(fg_color=color)

    def _load_custom_theme_palette(self, color):
        """Загружает сохраненную палитру до создания виджетов."""
        color = color.upper()
        rgb = tuple(int(color[i:i+2], 16) / 255 for i in (1, 3, 5))
        h, s, v = colorsys.rgb_to_hsv(*rgb)

        def hsv_hex(hh, ss, vv):
            rr, gg, bb = colorsys.hsv_to_rgb(hh % 1.0, max(0.0, min(1.0, ss)), max(0.0, min(1.0, vv)))
            return '#{:02X}{:02X}{:02X}'.format(round(rr * 255), round(gg * 255), round(bb * 255))

        colors = MaterialColors._colors['dark']
        colors['primary'] = color
        colors['on_primary'] = '#000000' if (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) > 0.62 else '#FFFFFF'
        colors['primary_container'] = hsv_hex(h, s * 0.90, max(0.25, v * 0.55))
        colors['on_primary_container'] = color
        colors['secondary'] = hsv_hex((h + 0.04) % 1.0, s * 0.45, min(1.0, v * 0.90))
        colors['secondary_container'] = hsv_hex(h, s * 0.45, max(0.22, v * 0.38))

    def _set_custom_theme_color(self, color):
        """Перестраивает основные Material 3 accent-цвета вокруг выбранного цвета."""
        color = color.upper()
        rgb = tuple(int(color[i:i+2], 16) / 255 for i in (1, 3, 5))
        h, s, v = colorsys.rgb_to_hsv(*rgb)

        def hsv_hex(hh, ss, vv):
            rr, gg, bb = colorsys.hsv_to_rgb(hh % 1.0, max(0.0, min(1.0, ss)), max(0.0, min(1.0, vv)))
            return '#{:02X}{:02X}{:02X}'.format(round(rr * 255), round(gg * 255), round(bb * 255))

        # Для темной темы: основной цвет — выбранный, container темнее,
        # а on-primary автоматически выбирается по контрасту.
        primary = color
        primary_container = hsv_hex(h, s * 0.90, max(0.25, v * 0.55))
        on_primary = '#000000' if (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) > 0.62 else '#FFFFFF'
        secondary = hsv_hex((h + 0.04) % 1.0, s * 0.45, min(1.0, v * 0.90))
        secondary_container = hsv_hex(h, s * 0.45, max(0.22, v * 0.38))

        colors = MaterialColors._colors['dark']
        colors['primary'] = primary
        colors['on_primary'] = on_primary
        colors['primary_container'] = primary_container
        colors['on_primary_container'] = primary
        colors['secondary'] = secondary
        colors['secondary_container'] = secondary_container

        self.settings['custom_primary_color'] = color
        self.config['custom_primary_color'] = color
        save_config(self.config)

        self.update_md3_colors()
        try:
            self._show_settings_section(self.settings_active_section)
        except Exception:
            pass

    def reset_custom_theme_color(self):
        self._set_custom_theme_color('#D0BCFF')
        if hasattr(self, 'theme_color_entry'):
            self.theme_color_entry.delete(0, "end")
            self.theme_color_entry.insert(0, '#D0BCFF')
        if hasattr(self, 'theme_color_preview'):
            self.theme_color_preview.configure(fg_color='#D0BCFF')

    def toggle_animations(self):
        # Галочка означает «Отключить анимации», поэтому значение инвертировано.
        try:
            self.settings['animations_enabled'] = not bool(self.animations_enabled_var.get())
            self.config['animations_enabled'] = self.settings['animations_enabled']
            save_config(self.config)
        except Exception as e:
            print(f"Ошибка сохранения состояния анимаций: {e}")

    def check_updates(self):
        if not hasattr(self, 'update_button'):
            return

        self.update_button.configure(
            state="disabled",
            text=self.translation.tr('update_checking')
        )

        def worker():
            try:
                latest_version, message = UpdateChecker.check_for_updates()
            except Exception as e:
                latest_version, message = None, f"update_error: {e}"

            def finish():
                try:
                    self.update_button.configure(
                        state="normal",
                        text=self.translation.tr('check_updates')
                    )

                    if latest_version:
                        answer = messagebox.askyesno(
                            self.translation.tr('update_available'),
                            self.translation.tr('update_message').format(latest_version),
                            parent=self.root
                        )
                        if answer:
                            autoupdate_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "autoupdate.py")
                            if os.path.exists(autoupdate_script):
                                subprocess.Popen([sys.executable, autoupdate_script, "--force"])
                                self.root.destroy()
                                return
                            webbrowser.open("https://miunlock.su/download/stable/pc/Latest_Release.zip", new=2)
                        return

                    if message == "up_to_date":
                        title = self.translation.tr('update_not_available')
                        text = (
                            self.translation.tr('current_version').format(CURRENT_VERSION)
                            + " "
                            + self.translation.tr('update_not_available')
                        )
                    elif isinstance(message, str) and message.startswith("update_error:"):
                        title = self.translation.tr('update_not_available')
                        text = self.translation.tr('update_error')
                    else:
                        title = self.translation.tr('update_not_available')
                        text = str(message)

                    messagebox.showinfo(title, text, parent=self.root)
                except Exception as e:
                    print(f"Ошибка отображения результата проверки обновлений: {e}")

            self.root.after(0, finish)

        threading.Thread(target=worker, daemon=True).start()

    def open_instructions(self):
        self.switch_tab("settings")

    def on_instructions_close(self, window=None):
        return

    def _create_mi_unlock_tab(self):
        """Создает вкладку с полноценным Mi Unlock функционалом с интерфейсом как у Подачи заявок"""
        trans = self.translation
        dark_mode = True
        container = self.tab_containers['mi_unlock']
        container.pack(fill="both", expand=True)

        # Двухколонный layout как в unlock tab
        left_column = ctk.CTkFrame(container, fg_color="transparent", width=460)
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        right_column = ctk.CTkFrame(container, fg_color="transparent", width=460)
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # ===== ЛЕВАЯ КОЛОННА =====
        mi_card = MD3Card(left_column, elevation=2)
        mi_card.pack(fill="both", expand=True)
        mi_card.configure(corner_radius=18)

        # Header левой карточки
        card_header = ctk.CTkFrame(mi_card, fg_color="transparent", height=46)
        card_header.pack(fill="x", padx=18, pady=(12, 0))
        card_header.pack_propagate(False)

        mi_label_bg = ctk.CTkFrame(
            card_header,
            fg_color='#202020',
            corner_radius=12,
            border_width=0,
            height=36
        )
        mi_label_bg.pack(side="left")

        self.mi_label = MD3Label(
            mi_label_bg,
            text=trans.tr('mi_unlock_label'),
            typography='title_large',
        )
        self.mi_label.pack(side="left", padx=12, pady=2)

        # Content левой карточки
        card_content = ctk.CTkScrollableFrame(mi_card, fg_color="transparent")
        card_content.pack(fill="both", expand=True, padx=12, pady=(8, 10))

        # Информация о статусе
        info_card = MD3Card(card_content, elevation=1)
        info_card.pack(fill="x", pady=(0, 12))
        info_card.configure(corner_radius=16)

        info_content = ctk.CTkFrame(info_card, fg_color="transparent")
        info_content.pack(fill="x", padx=12, pady=10)

        self.mi_info_label = MD3Label(
            info_content,
            text=trans.tr('info'),
            typography='title_medium'
        )
        self.mi_info_label.pack(anchor="w", pady=(0, 12))

        # Состояние процесса
        process_state = {'process': None, 'closed': False, 'status_label': None}

        status_item = ctk.CTkFrame(info_content, fg_color="transparent")
        status_item.pack(fill="x", pady=(0, 8))

        status_icon = ctk.CTkLabel(
            status_item,
            text="⚙️",
            font=("Arial", 16),
            width=24
        )
        status_icon.pack(side="left")

        self.mi_status_label_var = ctk.StringVar(value=trans.tr('mi_unlock_checking_python'))
        status_label_var = self.mi_status_label_var
        status_label = MD3Label(
            status_item,
            textvariable=status_label_var,
            typography='body_medium'
        )
        status_label.pack(side="left", padx=(12, 0), anchor="w")
        process_state['status_label'] = status_label

        python_item = ctk.CTkFrame(info_content, fg_color="transparent")
        python_item.pack(fill="x", pady=(0, 8))

        python_icon = ctk.CTkLabel(
            python_item,
            text="🐍",
            font=("Arial", 16),
            width=24
        )
        python_icon.pack(side="left")

        self.mi_python_label_var = ctk.StringVar(value=trans.tr('mi_unlock_python_not_found'))
        python_label_var = self.mi_python_label_var
        python_label = MD3Label(
            python_item,
            textvariable=python_label_var,
            typography='body_medium'
        )
        python_label.pack(side="left", padx=(12, 0), anchor="w")

        package_item = ctk.CTkFrame(info_content, fg_color="transparent")
        package_item.pack(fill="x")

        package_icon = ctk.CTkLabel(
            package_item,
            text="📦",
            font=("Arial", 16),
            width=24
        )
        package_icon.pack(side="left")

        self.mi_package_label_var = ctk.StringVar(value=trans.tr('mi_unlock_package_not_installed'))
        package_label_var = self.mi_package_label_var
        package_label = MD3Label(
            package_item,
            textvariable=package_label_var,
            typography='body_medium'
        )
        package_label.pack(side="left", padx=(12, 0), anchor="w")

        # Кнопки действия
        button_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        button_frame.pack(fill="x")

        def start_mi_unlock():
            start_mi_btn.configure(state="disabled")
            self.mi_close_btn.configure(state="disabled")
            threading.Thread(target=install_and_run_miunlock, daemon=True).start()

        def close_mi_unlock():
            """Закрывает вкладку Mi Unlock и завершает процесс"""
            # Завершаем процесс если он запущен
            if process_state['process'] and process_state['process'].poll() is None:
                try:
                    process_state['process'].terminate()
                    process_state['process'].wait(timeout=2)
                except:
                    try:
                        process_state['process'].kill()
                    except:
                        pass
            process_state['closed'] = True

            self.exit_application()

        self.start_mi_btn = MD3Button(
            button_frame,
            text=trans.tr('mi_unlock_start_button'),
            button_type='filled',
            size='large',
            command=start_mi_unlock
        )
        self.start_mi_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))
        start_mi_btn = self.start_mi_btn

        exit_bg = ctk.CTkFrame(
            button_frame,
            fg_color='#202020',
            corner_radius=12,
            border_width=0,
            height=44
        )
        exit_bg.pack(side="right")

        self.mi_close_btn = MD3Button(
            exit_bg,
            text=trans.tr('exit'),
            button_type='text',
            size='small',
            command=close_mi_unlock
        )
        self.mi_close_btn.pack(fill="both", expand=True, padx=10, pady=4)

        self.mi_drivers_btn = MD3Button(
            card_content,
            text=trans.tr('mi_unlock_drivers_button'),
            button_type='outlined',
            size='medium',
            command=self.open_mi_unlock_drivers
        )
        self.mi_drivers_btn.pack(fill="x", pady=(8, 0))

        # ===== ПРАВАЯ КОЛОННА (ЛОГИРОВАНИЕ) =====
        log_card = MD3Card(right_column, elevation=2)
        log_card.pack(fill="both", expand=True)
        log_card.configure(corner_radius=18)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent", height=46)
        log_header.pack(fill="x", padx=18, pady=(12, 0))
        log_header.pack_propagate(False)

        log_label_bg = ctk.CTkFrame(
            log_header,
            fg_color='#202020',
            corner_radius=6,
            border_width=0,
            height=34,
            width=160
        )
        log_label_bg.pack(side="left")

        self.mi_log_label = MD3Label(
            log_label_bg,
            text=trans.tr('mi_unlock_log_title'),
            typography='title_large',
            text_color='#FFFFFF'
        )
        self.mi_log_label.pack(side="left", padx=12, pady=2)

        log_controls = ctk.CTkFrame(log_header, fg_color="transparent")
        log_controls.pack(side="right")

        clear_log_bg = ctk.CTkFrame(
            log_controls,
            fg_color='#202020',
            corner_radius=12,
            border_width=0,
            height=36,
            width=118
        )
        clear_log_bg.pack(side="left")

        def clear_log_content():
            output_text.configure(state="normal")
            output_text.delete("1.0", "end")
            output_text.configure(state="disabled")

        self.mi_clear_log_btn = MD3Button(
            clear_log_bg,
            text=trans.tr('clear_log_btn'),
            button_type='text',
            size='small',
            command=clear_log_content
        )
        self.mi_clear_log_btn.pack(fill="both", expand=True, padx=12, pady=4)

        log_content = ctk.CTkFrame(log_card, fg_color="transparent")
        log_content.pack(fill="both", expand=True, padx=18, pady=(8, 12))

        log_text_container = ctk.CTkFrame(
            log_content,
            fg_color=MaterialColors.get_color('surface_container_lowest'),
            corner_radius=8,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        log_text_container.pack(fill="both", expand=True)

        output_text = ctk.CTkTextbox(
            log_text_container,
            wrap="word",
            font=("Consolas", 12),
            fg_color=MaterialColors.get_color('surface_container_lowest'),
            text_color=MaterialColors.get_color('on_surface'),
            border_width=0
        )
        output_text.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(
            log_text_container,
            command=output_text.yview
        )
        scrollbar.pack(side="right", fill="y")

        output_text.configure(yscrollcommand=scrollbar.set)
        output_text.configure(state='disabled')

        # ===== ВВОД =====
        input_card = ctk.CTkFrame(card_content, fg_color="transparent")
        input_card.pack(fill="x", padx=0, pady=(0, 16), before=info_card)

        self.mi_input_label = MD3Label(
            input_card,
            text=trans.tr('input_label'),
            typography='label_large'
        )
        self.mi_input_label.pack(anchor="w", pady=(0, 8))

        input_entry = MD3Entry(
            input_card,
            placeholder_text=trans.tr('mi_unlock_input_placeholder'),
            height=36
        )
        self.mi_input_entry = input_entry
        input_entry.pack(fill="x")

        def send_input(event=None):
            text = input_entry.get()
            if text and process_state['process'] and process_state['process'].poll() is None:
                try:
                    process_state['process'].stdin.write(text + "\n")
                    process_state['process'].stdin.flush()
                    log_message(trans.tr('mi_unlock_input_prefix').format(text), "cyan")
                    input_entry.delete(0, "end")
                except Exception as e:
                    log_message(trans.tr('mi_unlock_input_error').format(e), "red")

        def handle_input_enter(event=None):
            if process_state['process'] is None:
                start_mi_unlock()
                return "break"
            send_input(event)
            return "break"

        input_entry.bind("<Return>", handle_input_enter)

        mi_desc_frame = ctk.CTkFrame(left_column, fg_color="transparent")
        mi_desc_frame.pack(fill="x", pady=(10, 0))

        self.mi_desc_label = MD3Label(
            mi_desc_frame,
            text=trans.tr('mi_unlock_desc'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant'),
            wraplength=450,
            justify="left"
        )
        self.mi_desc_label.pack()

        # ===== ФУНКЦИИ =====
        def log_message(message, color="white"):
            if process_state['closed']:
                return
            try:
                output_text.configure(state="normal")
                timestamp = datetime.now().strftime("%H:%M:%S")
                if isinstance(message, str) and message.startswith('mi_unlock_'):
                    try:
                        message = trans.tr(message)
                    except:
                        pass
                formatted = f"[{timestamp}] {message}\n"
                output_text.insert("end", formatted)
                output_text.see("end")
                output_text.configure(state="disabled")
                container.update_idletasks()
            except Exception:
                pass

        def update_status(message, color="white"):
            if process_state['closed']:
                return
            try:
                if isinstance(message, str) and message.startswith('mi_unlock_'):
                    try:
                        message = trans.tr(message)
                    except:
                        pass
                if process_state['status_label'] and process_state['status_label'].winfo_exists():
                    process_state['status_label'].configure(text=message, text_color=color)
                log_message(message, color)
            except Exception:
                pass

        def safe_update_status(msg, color="white"):
            if not process_state['closed']:
                try:
                    container.after(0, lambda: update_status(msg, color))
                except:
                    pass

        def safe_log_message(msg, color="white"):
            if not process_state['closed']:
                try:
                    container.after(0, lambda: log_message(msg, color))
                except:
                    pass

        def update_labels(python_version=None, miunlock_installed=False):
            if python_version:
                python_label_var.set(trans.tr('mi_unlock_python_found_label').format(python_version))
            miunlock_status = trans.tr('mi_unlock_package_installed') if miunlock_installed else trans.tr(
                'mi_unlock_package_not_installed')
            package_label_var.set(miunlock_status)

        def find_python():
            test_commands = [sys.executable, 'python', 'python3', 'py'] if os.name == 'nt' else [sys.executable, 'python3', 'python']
            flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

            for cmd in test_commands:
                try:
                    result = subprocess.run(
                        [cmd, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=5,
                        creationflags=flags
                    )
                    if result.returncode == 0:
                        version = (result.stdout or result.stderr).strip()
                        return cmd, version
                except:
                    continue
            return None, None

        def install_and_run_miunlock():
            try:
                safe_update_status('mi_unlock_checking_python', "orange")
                python_cmd, version = find_python()

                if not python_cmd:
                    safe_log_message(trans.tr('mi_unlock_python_not_found'), "red")
                    safe_log_message(trans.tr('mi_unlock_python_error_msg'), "red")
                    safe_update_status("Python not found!", "red")
                    return

                safe_log_message(trans.tr('mi_unlock_python_found').format(version), "green")
                safe_update_status(f"Python found: {version}", "green")
                container.after(0, lambda: update_labels(python_version=version))

                flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

                safe_update_status('mi_unlock_installing', "orange")
                safe_log_message("Attempting: pip install miunlock", "blue")

                install_cmds = [
                    [python_cmd, '-m', 'pip', 'install', 'miunlock'],
                    ['pip', 'install', 'miunlock'],
                    [python_cmd, '-m', 'pip', 'install', 'miunlock', '--user']
                ]

                installed = False
                for cmd in install_cmds:
                    try:
                        safe_log_message(f"Trying: {' '.join(cmd)}", "blue")
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=120,
                            creationflags=flags
                        )
                        if result.returncode == 0:
                            safe_log_message("✓ Installation successful!", "green")
                            installed = True
                            break
                        else:
                            safe_log_message(f"✗ Failed: {result.stderr[:200]}", "orange")
                    except Exception as e:
                        safe_log_message(f"✗ Error: {str(e)[:200]}", "orange")
                        continue

                if not installed:
                    safe_update_status('mi_unlock_install_error', "red")
                    safe_log_message("All installation attempts failed", "red")
                    return

                container.after(0, lambda: update_labels(miunlock_installed=True))

                safe_update_status('mi_unlock_upgrading', "orange")
                safe_log_message("Attempting upgrade...", "blue")

                upgrade_cmds = [
                    [python_cmd, '-m', 'pip', 'install', '--upgrade', 'miunlock'],
                    ['pip', 'install', '--upgrade', 'miunlock']
                ]

                for cmd in upgrade_cmds:
                    try:
                        safe_log_message(f"Upgrading: {' '.join(cmd)}", "blue")
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=60,
                            creationflags=flags
                        )
                        if result.returncode == 0:
                            safe_log_message("✓ Upgrade successful!", "green")
                            break
                        else:
                            safe_log_message(f"✗ Upgrade failed: {result.stderr[:200]}", "orange")
                    except Exception as e:
                        safe_log_message(f"✗ Upgrade error: {str(e)[:200]}", "orange")
                        continue

                safe_update_status('mi_unlock_starting', "green")
                safe_log_message(trans.tr('mi_unlock_launching'), "blue")

                run_cmds = [
                    [python_cmd, '-m', 'miunlock'],
                    ['miunlock']
                ]

                for cmd in run_cmds:
                    try:
                        safe_log_message(f"Running: {' '.join(cmd)}", "blue")
                        process_state['process'] = subprocess.Popen(
                            cmd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                            bufsize=1,
                            universal_newlines=True,
                            creationflags=flags
                        )
                        break
                    except Exception as e:
                        safe_log_message(f"✗ Failed to run: {str(e)[:200]}", "orange")
                        continue
                else:
                    safe_update_status("Failed to start miunlock!", "red")
                    safe_log_message("All run attempts failed", "red")
                    return

                def read_output():
                    try:
                        for line in iter(process_state['process'].stdout.readline, ''):
                            if process_state['closed']:
                                break
                            if line:
                                line_stripped = line.strip()
                                if line_stripped:
                                    if not process_state['closed']:
                                        try:
                                            container.after(0, lambda l=line_stripped: log_message(l, "white"))
                                        except:
                                            pass
                    except Exception as e:
                        if "closed" not in str(e).lower() and not process_state['closed']:
                            try:
                                container.after(0,
                                                lambda: log_message(trans.tr('mi_unlock_read_error').format(e), "red"))
                            except:
                                pass

                read_thread = threading.Thread(target=read_output, daemon=True)
                read_thread.start()

                process_state['process'].wait()

                if not process_state['closed']:
                    if process_state['process'].returncode == 0:
                        try:
                            container.after(0, lambda: update_status('mi_unlock_completed', "green"))
                            container.after(0, lambda: log_message(trans.tr('mi_unlock_finished'), "green"))
                        except:
                            pass
                    else:
                        try:
                            container.after(0, lambda: log_message(
                                trans.tr('mi_unlock_process_exit').format(process_state['process'].returncode),
                                "orange"))
                        except:
                            pass

            except Exception as e:
                if not process_state['closed']:
                    try:
                        container.after(0, lambda: update_status(trans.tr('mi_unlock_error').format(str(e)), "red"))
                        container.after(0, lambda: log_message(trans.tr('mi_unlock_critical_error').format(e), "red"))
                    except:
                        pass

    def _animate_settings_panel(self, panel, step=0):
        # animations_enabled — фактическое состояние анимаций.
        if not self.settings.get('animations_enabled', True):
            panel.pack(fill="both", expand=True, padx=8, pady=8)
            return

        if step == 0:
            panel.pack_forget()
            panel.place(relx=0, rely=0.04, relwidth=1, relheight=0.96, anchor="nw")

        if step < 6:
            progress = (step + 1) / 6
            panel.place_configure(rely=0.04 * (1 - progress), relheight=0.96 + (0.04 * progress))
            panel.after(16, lambda: self._animate_settings_panel(panel, step + 1))
        else:
            panel.place_forget()
            panel.pack(fill="both", expand=True, padx=8, pady=8)

    def switch_tab(self, tab_name, step=0):
        """Переключает между вкладками"""
        if step == 0:
            self.current_tab = tab_name
            for container in self.tab_containers.values():
                container.place_forget()
                container.pack_forget()

            if tab_name in self.tab_containers:
                container = self.tab_containers[tab_name]
                if self.settings.get('animations_enabled', True):
                    container.place(relx=0.025, rely=0, relwidth=1, relheight=1, anchor="nw")
                    container.after(16, lambda: self.switch_tab(tab_name, 1))
                else:
                    container.pack(fill="both", expand=True)
        elif step < 6:
            if self.current_tab != tab_name:
                return
            if tab_name in self.tab_containers:
                container = self.tab_containers[tab_name]
                progress = (step + 1) / 6
                container.place_configure(relx=0.025 * (1 - progress))
                container.after(16, lambda: self.switch_tab(tab_name, step + 1))
        else:
            if self.current_tab != tab_name:
                return
            if tab_name in self.tab_containers:
                container = self.tab_containers[tab_name]
                container.place_forget()
                container.pack(fill="both", expand=True)

        if self.current_tab != tab_name:
            return

        # Обновляем стили кнопок
        dark_mode = True
        for btn_name, btn in self.tab_buttons.items():
            if btn_name == "settings":
                if btn_name == tab_name:
                    btn.configure(
                        fg_color=MaterialColors.get_color('primary'),
                        hover_color=MaterialColors.get_color('primary_container'),
                        text_color=MaterialColors.get_color('on_primary'),
                        border_width=0
                    )
                else:
                    btn.configure(
                        fg_color='transparent',
                        hover_color=MaterialColors.get_color('surface_container_high'),
                        text_color=MaterialColors.get_color('primary'),
                        border_width=1,
                        border_color=MaterialColors.get_color('outline')
                    )
            elif btn_name == tab_name:
                # Активная кнопка - filled
                btn.configure(
                    fg_color=MaterialColors.get_color('primary'),
                    hover_color=MaterialColors.get_color('primary_container'),
                    text_color=MaterialColors.get_color('on_primary'),
                    border_width=0
                )
            else:
                # Неактивная кнопка - outlined
                btn.configure(
                    fg_color='transparent',
                    hover_color=MaterialColors.get_color('surface_container_high'),
                    text_color=MaterialColors.get_color('primary'),
                    border_width=1,
                    border_color=MaterialColors.get_color('outline')
                )

    def open_login_dialog(self):
        try:
            dialog = XiaomiAuthDialog(self.root, self.translation, self.config)
            self.root.wait_window(dialog)
            if getattr(dialog, 'success', False) and getattr(dialog, 'token', None):
                token = dialog.token
                self.cookie_value.set(token)
                self.auto_save_cookie()
                masked_token = token[:8] + "..." + token[-6:] if len(token) > 14 else "***"
                self.log_message(f"{self.translation.tr('login_success')} (Token: {masked_token})", color='green')
        except Exception as e:
            self.log_message(f"Error opening login dialog: {e}", color='red')

    def check_eligibility(self):
        token = self.cookie_value.get().strip()
        if not token:
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('cookie_error'))
            return

        if getattr(self, '_eligibility_thread', None) and self._eligibility_thread.is_alive():
            return

        self.log_message(self.translation.tr('checking_eligibility'), color="blue")
        if hasattr(self, 'check_eligibility_btn') and self.check_eligibility_btn is not None:
            self.check_eligibility_btn.configure(state="disabled")

        def worker():
            try:
                device_id = self.request_handler.generate_device_id()
                self.request_handler.check_unlock_status(token, device_id, force=True, show_success_dialog=True)
            except Exception as e:
                self.log_message(f"Error checking eligibility: {e}", color="red")
            finally:
                if hasattr(self, 'check_eligibility_btn') and self.check_eligibility_btn is not None:
                    self.root.after(0, lambda: self.check_eligibility_btn.configure(state="normal"))

        self._eligibility_thread = threading.Thread(target=worker, daemon=True)
        self._eligibility_thread.start()

    def clear_log(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")

    def toggle_mode(self, selected_mode):
        if selected_mode == self.translation.tr('manual_mode'):
            self.auto_mode_index = 0
        else:
            # По умолчанию Авторежим #2
            self.auto_mode_index = 2

        if hasattr(self, 'manual_time_frame') and self.manual_time_frame is not None:
            if selected_mode == self.translation.tr('manual_mode'):
                self.manual_time_frame.pack(fill="x", pady=(0, 16))
                self.ping_var.set(self.translation.tr('ping_not_measured_manual'))
                self.desc_label.configure(text=self.translation.tr('desc_manual'))
            else:
                self.manual_time_frame.pack_forget()
                self.ping_var.set(self.translation.tr('ping'))
                self.desc_label.configure(text=self.translation.tr('desc'))

    def is_auto_mode_1(self):
        return False  # Авторежим #1 заблокирован

    def is_auto_mode_2(self):
        return self.auto_mode_index == 2

    def _get_site_button_text(self):
        # Название кнопки берём из общего словаря переводов.
        # Это позволяет ей корректно меняться вместе с остальным интерфейсом.
        return self.translation.tr('social_site_script')

    def update_ui_text(self):
        self.root.title(self.translation.tr('title'))

        if hasattr(self, 'update_button'):
            self.update_button.configure(text=self.translation.tr('check_updates'))
        if hasattr(self, 'site_btn'):
            self.site_btn.configure(text=self._get_site_button_text())
        self.title_label.configure(text=self.translation.tr('main_title'))

        # Обновляем текст кнопок вкладок
        if hasattr(self, 'tab_buttons') and self.tab_buttons:
            self.tab_buttons['unlock'].configure(text=self.translation.tr('tab_unlock'))
            self.tab_buttons['settings'].configure(text=self.translation.tr('tab_settings'))
            self.tab_buttons['mi_unlock'].configure(text=self.translation.tr('tab_mi_unlock'))

        if hasattr(self, 'settings_sidebar_buttons'):
            section_titles = {
                'about': 'about_title',
                'general': 'general_title',
                'cookies': 'cookies_title',
                'trouble': 'trouble_title',
                'authors': 'authors_title',
                'settings': 'settings'
            }
            for section_key, button in self.settings_sidebar_buttons.items():
                button.configure(text=self.translation.tr(section_titles[section_key]))
            self._show_settings_section(self.settings_active_section)

        self.desc_label.configure(text=self.translation.tr('desc'))
        if hasattr(self, 'mi_desc_label'):
            self.mi_desc_label.configure(text=self.translation.tr('mi_unlock_desc'))

        # Исправлено: перевод заголовка вкладки "Подача Заявок"
        self.params_label.configure(text=self.translation.tr('tab_unlock'))
        self.mode_label.configure(text=self.translation.tr('mode_label'))
        # Обновляем сегментированную кнопку - только 2 режима
        if self.mode_segmented:
            new_values = [self.translation.tr('auto_mode_2'), self.translation.tr('manual_mode')]
            self.mode_segmented.update_values(new_values)

        if self.auto_mode_index == 0:
            self.mode_var.set(self.translation.tr('manual_mode'))
        else:
            self.auto_mode_index = 2
            self.mode_var.set(self.translation.tr('auto_mode_2'))

        if self.mode_segmented:
            self.mode_segmented.select(self.mode_var.get())

        self.manual_time_label.configure(text=self.translation.tr('manual_time_label'))
        self.manual_time_hint.configure(text=self.translation.tr('manual_time_hint'))
        self.cookie_text_label.configure(text=self.translation.tr('cookie_label'))
        if hasattr(self, 'login_btn') and self.login_btn is not None:
            self.login_btn.configure(text=self.translation.tr('login_btn'))
        if hasattr(self, 'check_eligibility_btn') and self.check_eligibility_btn is not None:
            self.check_eligibility_btn.configure(text=self.translation.tr('check_eligibility_btn'))
        self.info_label.configure(text=self.translation.tr('info'))
        self.status_var.set(self.translation.tr('status_ready'))

        if self.auto_mode_index == 0:
            self.ping_var.set(self.translation.tr('ping_not_measured_manual'))
        else:
            self.ping_var.set(self.translation.tr('ping'))

        self.time_var.set(self.translation.tr('time'))
        if hasattr(self, 'mi_label'):
            self.mi_label.configure(text=self.translation.tr('mi_unlock_label'))
        if hasattr(self, 'mi_info_label'):
            self.mi_info_label.configure(text=self.translation.tr('info'))
        if hasattr(self, 'mi_input_label'):
            self.mi_input_label.configure(text=self.translation.tr('input_label'))
        if hasattr(self, 'mi_input_entry'):
            self.mi_input_entry.configure(placeholder_text=self.translation.tr('mi_unlock_input_placeholder'))
        if hasattr(self, 'mi_log_label'):
            self.mi_log_label.configure(text=self.translation.tr('mi_unlock_log_title'))
        if hasattr(self, 'mi_clear_log_btn'):
            self.mi_clear_log_btn.configure(text=self.translation.tr('clear_log_btn'))
        if hasattr(self, 'start_mi_btn'):
            self.start_mi_btn.configure(text=self.translation.tr('mi_unlock_start_button'))
        if hasattr(self, 'mi_drivers_btn'):
            self.mi_drivers_btn.configure(text=self.translation.tr('mi_unlock_drivers_button'))
        if hasattr(self, 'mi_close_btn'):
            self.mi_close_btn.configure(text=self.translation.tr('exit'))

        # Обновляем статусы Mi Unlock, если сейчас отображается один из стандартных переводимых статусов.
        mi_status_keys = (
            ('mi_status_label_var', 'mi_unlock_checking_python'),
            ('mi_python_label_var', 'mi_unlock_python_not_found'),
            ('mi_package_label_var', 'mi_unlock_package_not_installed'),
        )
        for attr_name, key in mi_status_keys:
            var = getattr(self, attr_name, None)
            if var is not None:
                current = var.get()
                known_values = {
                    lang_data.get(key)
                    for lang_data in self.translation.translations.values()
                    if lang_data.get(key)
                }
                if current in known_values:
                    var.set(self.translation.tr(key))

        self.application_status_var.set(
            self.translation.tr('application_status').format(
                self.translation.tr(getattr(self, 'application_status_key', 'application_status_not_sent'))
            )
        )

        self.log_label.configure(text=self.translation.tr('execution_log'))
        self.clear_log_btn.configure(text=self.translation.tr('clear_log_btn'))
        self.start_button.configure(text=self.translation.tr('submit_application'))
        self.exit_button.configure(text=self.translation.tr('exit'))

        # Исправлено: плейсхолдер всегда "new_bbs_ServiceToken"
        self.cookie_entry.configure(placeholder_text="new_bbs_ServiceToken")
        self.manual_time_entry.configure(placeholder_text="59.1")

        if hasattr(self, 'theme_color_entry'):
            self.theme_color_entry.configure(placeholder_text=self.translation.tr('theme_color_placeholder'))
        self.toggle_mode(self.mode_var.get())

    def update_theme_globally(self):
        self.apply_theme('Dark')

    def update_md3_colors(self):
        dark_mode = True

        self.top_bar.configure(fg_color=MaterialColors.get_color('surface_container'))
        self.title_label.configure(text_color=MaterialColors.get_color('on_surface'))
        if hasattr(self, 'subtitle_label') and self.subtitle_label is not None:
            try:
                self.subtitle_label.configure(text_color=MaterialColors.get_color('on_surface_variant'))
            except Exception:
                pass

        if hasattr(self, 'params_card'):
            self.params_card.configure(fg_color=MaterialColors.get_color('surface_container'))
        if hasattr(self, 'info_card'):
            self.info_card.configure(fg_color=MaterialColors.get_color('surface_container'))
        if hasattr(self, 'log_card'):
            self.log_card.configure(fg_color=MaterialColors.get_color('surface_container'))

        text_color = MaterialColors.get_color('on_surface')
        for _name in ('params_label', 'mode_label', 'manual_time_label', 'cookie_text_label', 'info_label', 'log_label'):
            _widget = getattr(self, _name, None)
            if _widget is not None:
                _widget.configure(text_color=text_color)

        self.log_label_bg.configure(fg_color='#1F1F1F')
        self.clear_log_bg.configure(fg_color='#1F1F1F')
        self.exit_bg.configure(fg_color='#1F1F1F')
        if hasattr(self, 'params_label_bg'):
            self.params_label_bg.configure(fg_color='#1F1F1F')

        bg_color = MaterialColors.get_color('surface_container_lowest')
        border_color = MaterialColors.get_color('outline')

        for _name in ('cookie_entry', 'manual_time_entry', 'log_text', 'status_text', 'time_text'):
            _widget = getattr(self, _name, None)
            if _widget is not None:
                kwargs = {'fg_color': bg_color, 'text_color': text_color}
                if _name in ('cookie_entry', 'manual_time_entry'):
                    kwargs['border_color'] = border_color
                if _name == 'log_text':
                    kwargs['border_color'] = MaterialColors.get_color('outline_variant')
                _widget.configure(**kwargs)

        self.start_button.configure(
            fg_color=MaterialColors.get_color('primary'),
            hover_color=MaterialColors.get_color('primary_container'),
            text_color=MaterialColors.get_color('on_primary'),
            border_width=0
        )

        # Кнопки встроенного Mi Unlock должны использовать выбранный accent-цвет.
        for _name in ('start_mi_btn',):
            _widget = getattr(self, _name, None)
            if _widget is not None:
                _widget.configure(
                    fg_color=MaterialColors.get_color('primary'),
                    hover_color=MaterialColors.get_color('primary_container'),
                    text_color=MaterialColors.get_color('on_primary'),
                    border_width=0
                )

        _widget = getattr(self, 'mi_drivers_btn', None)
        if _widget is not None:
            _widget.configure(
                fg_color='transparent',
                hover_color=MaterialColors.get_color('primary_container'),
                text_color=MaterialColors.get_color('primary'),
                border_color=MaterialColors.get_color('primary'),
                border_width=1
            )

        _widget = getattr(self, 'mi_clear_log_btn', None)
        if _widget is not None:
            _widget.configure(
                fg_color='transparent',
                hover_color=MaterialColors.get_color('surface_container'),
                text_color=MaterialColors.get_color('primary'),
                border_width=0
            )

        _widget = getattr(self, 'mi_close_btn', None)
        if _widget is not None:
            _widget.configure(
                fg_color='transparent',
                hover_color=MaterialColors.get_color('surface_container'),
                text_color=MaterialColors.get_color('on_surface'),
                border_width=0
            )

        for _btn_name in ('login_btn', 'check_eligibility_btn'):
            _widget = getattr(self, _btn_name, None)
            if _widget is not None:
                _widget.configure(
                    fg_color='transparent',
                    hover_color=MaterialColors.get_color('surface_container'),
                    text_color=MaterialColors.get_color('primary'),
                    border_color=MaterialColors.get_color('outline'),
                    border_width=1
                )

        self.exit_button.configure(
            fg_color='transparent',
            hover_color=MaterialColors.get_color('surface_container'),
            text_color='#FFFFFF',
            border_width=0
        )

        self.clear_log_btn.configure(
            fg_color='transparent',
            hover_color='#565656',
            text_color='#FFFFFF',
            border_width=0
        )

        self.clear_log_bg.configure(
            fg_color='#202020',
            corner_radius=12,
            border_width=0
        )

        if self.mode_segmented:
            self.mode_segmented.update_colors()

        self.main_container.configure(fg_color=MaterialColors.get_color('background'))
        self.content_area.configure(fg_color=MaterialColors.get_color('background'))

        self.desc_label.configure(text_color=MaterialColors.get_color('on_surface_variant'))

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not getattr(self, 'is_fullscreen', False)
        self.root.attributes("-fullscreen", self.is_fullscreen)
        return "break"

    def exit_fullscreen(self, event=None):
        if getattr(self, 'is_fullscreen', False):
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            return "break"

    def exit_application(self):
        self.config['cookie'] = self.cookie_value.get()
        save_config(self.config)
        self.root.destroy()
        sys.exit(0)

    def log_message(self, message, color=None):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        self.log_text.configure(state="normal")
        self.log_text.insert("end", formatted_message + "\n")

        if color:
            last_line_index = int(self.log_text.index("end-1c").split(".")[0])
            tag_name = f"color_{color}_{last_line_index}"
            self.log_text.tag_add(tag_name, f"end-2l", "end-1c")

            color_map = {
                'green': '#0D904F',
                'red': '#B3261E',
                'blue': '#006C84',
                'orange': '#FF6F00',
                'cyan': '#00BCD4',
            }
            self.log_text.tag_config(tag_name, foreground=color_map.get(color, '#000000'))

        self.log_text.see("end")
        self.log_text.configure(state="disabled")

        try:
            if self.settings.get('log_to_txt', True):
                if not hasattr(self, 'current_log_file') or self.current_log_file is None:
                    if getattr(sys, 'frozen', False):
                        base_dir = os.path.dirname(sys.executable)
                    else:
                        base_dir = os.path.dirname(os.path.abspath(__file__))

                    now = datetime.now()
                    date_str = now.strftime("%d%m%Y_%H_%M_%S")
                    filename = f"log_miunlock_{date_str}.txt"
                    self.current_log_file = os.path.join(base_dir, filename)
                    self._write_log_header()

                with open(self.current_log_file, 'a', encoding='utf-8') as f:
                    f.write(formatted_message + "\n")
        except Exception as e:
            print(f"Ошибка записи лога: {e}")

    def _write_log_header(self):
        try:
            with open(self.current_log_file, 'w', encoding='utf-8') as f:
                f.write("=== XIAOMI UNLOCK TOOL LOG ===\n")
                f.write(f"Version: {CURRENT_VERSION}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 30 + "\n")
                f.write("SETTINGS:\n")
                f.write(f"Mode: {self.mode_var.get()}\n")
                if self.mode_var.get() == self.translation.tr('auto_mode'):
                    f.write(f"Spam Mode: {self.settings.get('spam_mode', True)}\n")
                if self.mode_var.get() == self.translation.tr('manual_mode'):
                    f.write(f"Manual Time Target: {self.manual_time_var.get()}\n")
                f.write(f"Skip Cookie Check: {self.settings.get('skip_cookie_check')}\n")
                f.write(f"Language: {self.translation.language}\n")
                f.write(f"Server List: {MI_SERVERS}\n")
                f.write("=" * 30 + "\n\n")
        except Exception:
            pass

    def wait_until_target_time(self, start_beijing_time, start_timestamp, script_time):
        target_midnight = start_beijing_time.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        base_minute = target_midnight - timedelta(minutes=1)
        send_at = base_minute + timedelta(seconds=script_time)
        if send_at <= start_beijing_time:
            base_minute += timedelta(days=1)
            send_at += timedelta(days=1)

        self.log_message(self.translation.tr('target_time').format(
            send_at.strftime('%Y-%m-%d %H:%M:%S.%f'),
            script_time
        ))

        def check_time():
            current_time = self.request_handler.get_synchronized_beijing_time(self.start_beijing_time,
                                                                              self.start_timestamp)
            self.time_var.set(
                f"{self.translation.tr('time_synchronized')}: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")

            if current_time >= send_at:
                self.log_message(self.translation.tr('time_reached').format(
                    current_time.strftime('%Y-%m-%d %H:%M:%S.%f')))
                self.send_request_with_token()
            else:
                self.root.after(10, check_time)

        check_time()

    def send_request_with_token(self):
        main_token = self.cookie_value.get().strip()
        if not main_token:
            self.log_message(self.translation.tr('cookie_error'), "red")
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('cookie_error'))
            return

        device_id = self.request_handler.generate_device_id()
        self.request_handler.single_request(main_token, device_id)

    def start_process(self):
        main_token = self.cookie_value.get().strip()
        if not main_token:
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('cookie_error'))
            return

        self.current_log_file = None

        self.log_message("\n" + "=" * 50)
        self.log_message(self.translation.tr('unlock_process'))
        self.status_var.set(self.translation.tr('unlock_process'))
        self.set_application_status(
            self.translation.tr('application_status_sending'),
            'application_status_sending'
        )

        skip_cookie_check = bool(self.settings.get('skip_cookie_check', False))
        if not skip_cookie_check:
            if not self.request_handler.check_unlock_status(main_token, self.request_handler.generate_device_id()):
                self.log_message(
                    self.translation.tr('token_status_check_failed'),
                    "red"
                )
                messagebox.showerror(
                    self.translation.tr('error_title'),
                    self.translation.tr('token_status_check_failed')
                )
                return
            self.log_message(self.translation.tr('log_token_check_success'), "green")
        else:
            self.log_message(self.translation.tr('log_token_check_skipped'), "orange")

        self.start_beijing_time = self.request_handler.get_initial_beijing_time()
        if self.start_beijing_time is None:
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('time_error'))
            return

        self.start_timestamp = time.time()

        if self.auto_mode_index == 0:
            self.start_manual_mode()
        else:
            self.log_message(self.translation.tr('log_mode2_selected'), color="blue")
            self.start_auto_mode_2()

    def start_auto_mode_2(self):
        self.log_message(self.translation.tr('log_mode2_ntp_saved'), "blue")
        self.status_var.set(self.translation.tr('status_mode2_waiting'))

        if self.start_beijing_time is None:
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('time_error'))
            return
        if self.start_timestamp is None:
            self.start_timestamp = time.time()

        target_send = self.start_beijing_time.replace(hour=23, minute=59, second=59, microsecond=0)
        if target_send <= self.start_beijing_time:
            target_send += timedelta(days=1)

        def check_time():
            now = self.request_handler.get_synchronized_beijing_time(self.start_beijing_time, self.start_timestamp)
            self.time_var.set(f"{self.translation.tr('time_synchronized')}: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
            if now >= target_send:
                self.log_message(self.translation.tr('log_mode2_beijing_reached'), "blue")
                self.schedule_auto_mode_2_http_spam(target_send)
            else:
                self.root.after(10, check_time)

        check_time()

    def schedule_auto_mode_2_http_spam(self, base_send_time=None):
        token = self.cookie_value.get().strip()
        if not token:
            self.log_message(self.translation.tr('cookie_error'), "red")
            return

        self.status_var.set(self.translation.tr('status_mode2_sending'))
        target_offsets_ms = [58.6, 58.8, 59.1, 59.3, 59.5, 59.8]
        if base_send_time is None:
            base_send_time = self.start_beijing_time.replace(hour=23, minute=59, second=59, microsecond=0)
            if base_send_time <= self.start_beijing_time:
                base_send_time += timedelta(days=1)

        now_sync = self.request_handler.get_synchronized_beijing_time(self.start_beijing_time, self.start_timestamp)

        for i, offset_ms in enumerate(target_offsets_ms):
            send_at = base_send_time + timedelta(milliseconds=offset_ms)
            send_dt = send_at - now_sync
            delay = max(0.0, send_dt.total_seconds())
            device_id = self.request_handler.generate_device_id()
            self.log_message(
                f"[{self.translation.tr('mode2_prefix')}] HTTP #{i + 1} target 23:59:59 (+{offset_ms:.1f}ms) device_id={device_id}",
                "blue"
            )
            self.log_message(
                f"[{self.translation.tr('mode2_prefix')}] HTTP #{i + 1} {self.translation.tr('mode2_timing')} = {delay:.6f}s rel to current sync",
                "blue"
            )
            threading.Timer(
                delay,
                self.request_handler.send_auto_mode_2_http_request,
                args=(i + 1, device_id, token)
            ).start()

        self.log_message(f"[{self.translation.tr('mode2_prefix')}] {self.translation.tr('log_mode2_plan_sent')}", "green")

    def wait_for_presync_time(self):
        # Этот метод больше не используется, но оставляем для совместимости
        pass

    def measure_pings_and_send(self):
        # Этот метод больше не используется, но оставляем для совместимости
        pass

    def schedule_multi_request(self, ping_http_ms, ping_tcp_ms):
        # Этот метод больше не используется, но оставляем для совместимости
        pass

    def start_manual_mode(self):
        # Ручной режим доступен через сегментированную кнопку
        try:
            script_time = float(self.manual_time_var.get())
            if script_time < 0 or script_time > 60:
                self.log_message(self.translation.tr('manual_time_error'))
                messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('manual_time_error'))
                return
            self.log_message(self.translation.tr('manual_mode_start').format(script_time))
        except ValueError as e:
            self.log_message(f"Error: {e}")
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('manual_time_error'))
            return

        self.wait_until_target_time(self.start_beijing_time, self.start_timestamp, script_time)

    def open_miflash_unlock(self):
        try:
            trans = self.translation
            dark_mode = True

            unlock_window = ctk.CTkToplevel()
            unlock_window.title(trans.tr('mi_unlock_title'))
            win_w = 860
            win_h = 580
            screen_w = unlock_window.winfo_screenwidth()
            screen_h = unlock_window.winfo_screenheight()
            if screen_h <= 720:
                win_h = min(580, max(480, screen_h - 70))
                win_w = min(860, max(680, screen_w - 40))
            pos_x = max(0, (screen_w - win_w) // 2)
            pos_y = max(0, (screen_h - win_h) // 2 - 20)
            unlock_window.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
            unlock_window.minsize(680, 480)
            unlock_window.resizable(True, True)
            unlock_window.configure(fg_color=MaterialColors.get_color('background'))

            if os.name == 'nt':
                unlock_window.attributes('-toolwindow', True)

            main_frame = ctk.CTkFrame(unlock_window, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            title_card = MD3Card(main_frame, elevation=2)
            title_card.pack(fill="x", pady=(0, 20))

            title_inner = ctk.CTkFrame(title_card, fg_color="transparent")
            title_inner.pack(fill="x", padx=24, pady=16)

            title_label = MD3Label(
                title_inner,
                text=trans.tr('mi_unlock_title'),
                typography='headline_medium'
            )
            title_label.pack(side="left")

            close_btn = MD3Button(
                title_inner,
                text=trans.tr('mi_unlock_close'),
                button_type='outlined',
                size='small',
                command=lambda: on_close()
            )
            close_btn.pack(side="right")

            status_card = MD3Card(main_frame, elevation=1)
            status_card.pack(fill="x", pady=(0, 15))

            status_inner = ctk.CTkFrame(status_card, fg_color="transparent")
            status_inner.pack(fill="x", padx=16, pady=12)

            status_icon = ctk.CTkLabel(
                status_inner,
                text="⚙️",
                font=("Arial", 18),
                width=30
            )
            status_icon.pack(side="left")

            status_label = MD3Label(
                status_inner,
                text=trans.tr('mi_unlock_checking_python'),
                typography='body_medium'
            )
            status_label.pack(side="left", padx=(12, 0))

            log_card = MD3Card(main_frame, elevation=2)
            log_card.pack(fill="both", expand=True, pady=(0, 15))

            log_header = ctk.CTkFrame(log_card, fg_color="transparent", height=40)
            log_header.pack(fill="x", padx=16, pady=(16, 8))
            log_header.pack_propagate(False)

            log_title = MD3Label(
                log_header,
                text=trans.tr('execution_log'),
                typography='title_medium'
            )
            log_title.pack(side="left")

            clear_log_btn = MD3Button(
                log_header,
                text=trans.tr('clear_log_btn'),
                button_type='text',
                size='small',
                command=lambda: clear_output()
            )
            clear_log_btn.pack(side="right")

            output_container = ctk.CTkFrame(
                log_card,
                fg_color=MaterialColors.get_color('surface_container_lowest'),
                corner_radius=8,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant')
            )
            output_container.pack(fill="both", expand=True, padx=16, pady=(0, 16))

            output_text = ctk.CTkTextbox(
                output_container,
                wrap="word",
                font=("Consolas", 11),
                fg_color=MaterialColors.get_color('surface_container_lowest'),
                text_color=MaterialColors.get_color('on_surface'),
                border_width=0
            )
            output_text.pack(side="left", fill="both", expand=True)

            scrollbar = ctk.CTkScrollbar(
                output_container,
                command=output_text.yview
            )
            scrollbar.pack(side="right", fill="y")
            output_text.configure(yscrollcommand=scrollbar.set)
            output_text.configure(state='disabled')

            input_card = MD3Card(main_frame, elevation=1)
            input_card.pack(fill="x")

            input_inner = ctk.CTkFrame(input_card, fg_color="transparent")
            input_inner.pack(fill="x", padx=16, pady=12)

            input_label = MD3Label(
                input_inner,
                text=trans.tr('mi_unlock_input_label'),
                typography='body_small'
            )
            input_label.pack(anchor="w", pady=(0, 5))

            input_row = ctk.CTkFrame(input_inner, fg_color="transparent")
            input_row.pack(fill="x")

            input_entry = MD3Entry(
                input_row,
                placeholder_text=trans.tr('mi_unlock_input_placeholder'),
                height=38
            )
            input_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

            def send_input():
                text = input_entry.get()
                if text and process and process.poll() is None:
                    try:
                        process.stdin.write(text + "\n")
                        process.stdin.flush()
                        log_message(trans.tr('mi_unlock_input_prefix').format(text), "cyan")
                        input_entry.delete(0, "end")
                    except Exception as e:
                        log_message(trans.tr('mi_unlock_input_error').format(e), "red")

            send_btn = MD3Button(
                input_row,
                text=trans.tr('mi_unlock_send_btn'),
                button_type='filled',
                size='small',
                command=send_input
            )
            send_btn.pack(side="right")
            input_entry.bind("<Return>", lambda event: send_input())

            window_closed = False
            process = None

            def on_close():
                nonlocal window_closed, process
                window_closed = True
                if process and process.poll() is None:
                    try:
                        process.terminate()
                        process.wait(timeout=2)
                    except:
                        try:
                            process.kill()
                        except:
                            pass
                unlock_window.destroy()

            def clear_output():
                output_text.configure(state="normal")
                output_text.delete("1.0", "end")
                output_text.configure(state="disabled")

            def log_message(message, color="white"):
                if window_closed:
                    return
                try:
                    output_text.configure(state="normal")
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    if isinstance(message, str) and message.startswith('mi_unlock_'):
                        try:
                            message = trans.tr(message)
                        except:
                            pass
                    formatted = f"[{timestamp}] {message}\n"
                    output_text.insert("end", formatted)
                    output_text.see("end")
                    output_text.configure(state="disabled")
                    unlock_window.update_idletasks()
                except Exception:
                    pass

            def update_status(message, color="white"):
                if window_closed:
                    return
                try:
                    if isinstance(message, str) and message.startswith('mi_unlock_'):
                        try:
                            message = trans.tr(message)
                        except:
                            pass
                    if status_label and status_label.winfo_exists():
                        status_label.configure(text=message, text_color=color)
                    log_message(message, color)
                except Exception:
                    pass

            def safe_update_status(msg, color="white"):
                if not window_closed:
                    unlock_window.after(0, lambda: update_status(msg, color))

            def safe_log_message(msg, color="white"):
                if not window_closed:
                    unlock_window.after(0, lambda: log_message(msg, color))

            def find_python():
                test_commands = [sys.executable, 'python', 'python3', 'py'] if os.name == 'nt' else [sys.executable, 'python3', 'python']
                flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

                for cmd in test_commands:
                    try:
                        result = subprocess.run(
                            [cmd, '--version'],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            creationflags=flags
                        )
                        if result.returncode == 0:
                            version = (result.stdout or result.stderr).strip()
                            return cmd, version
                    except:
                        continue
                return None, None

            def install_and_run_miunlock():
                nonlocal process

                try:
                    safe_update_status('mi_unlock_checking_python', "orange")
                    python_cmd, version = find_python()

                    if not python_cmd:
                        safe_log_message(trans.tr('mi_unlock_python_not_found'), "red")
                        safe_log_message(trans.tr('mi_unlock_python_error_msg'), "red")
                        safe_update_status("Python not found!", "red")
                        return

                    safe_log_message(trans.tr('mi_unlock_python_found').format(version), "green")
                    safe_update_status(f"Python found: {version}", "green")

                    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0

                    safe_update_status('mi_unlock_installing', "orange")
                    safe_log_message("Attempting: pip install miunlock", "blue")

                    install_cmds = [
                        [python_cmd, '-m', 'pip', 'install', 'miunlock'],
                        ['pip', 'install', 'miunlock'],
                        [python_cmd, '-m', 'pip', 'install', 'miunlock', '--user']
                    ]

                    installed = False
                    for cmd in install_cmds:
                        try:
                            safe_log_message(f"Trying: {' '.join(cmd)}", "blue")
                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=120,
                                creationflags=flags
                            )
                            if result.returncode == 0:
                                safe_log_message("✓ Installation successful!", "green")
                                installed = True
                                break
                            else:
                                safe_log_message(f"✗ Failed: {result.stderr[:200]}", "orange")
                        except Exception as e:
                            safe_log_message(f"✗ Error: {str(e)[:200]}", "orange")
                            continue

                    if not installed:
                        safe_update_status('mi_unlock_install_error', "red")
                        safe_log_message("All installation attempts failed", "red")
                        return

                    safe_update_status('mi_unlock_upgrading', "orange")
                    safe_log_message("Attempting upgrade...", "blue")

                    upgrade_cmds = [
                        [python_cmd, '-m', 'pip', 'install', '--upgrade', 'miunlock'],
                        ['pip', 'install', '--upgrade', 'miunlock']
                    ]

                    for cmd in upgrade_cmds:
                        try:
                            safe_log_message(f"Upgrading: {' '.join(cmd)}", "blue")
                            result = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True,
                                timeout=60,
                                creationflags=flags
                            )
                            if result.returncode == 0:
                                safe_log_message("✓ Upgrade successful!", "green")
                                break
                            else:
                                safe_log_message(f"✗ Upgrade failed: {result.stderr[:200]}", "orange")
                        except Exception as e:
                            safe_log_message(f"✗ Upgrade error: {str(e)[:200]}", "orange")
                            continue

                    safe_update_status('mi_unlock_starting', "green")
                    safe_log_message(trans.tr('mi_unlock_launching'), "blue")

                    run_cmds = [
                        [python_cmd, '-m', 'miunlock'],
                        ['miunlock']
                    ]

                    for cmd in run_cmds:
                        try:
                            safe_log_message(f"Running: {' '.join(cmd)}", "blue")
                            process = subprocess.Popen(
                                cmd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                text=True,
                                bufsize=1,
                                universal_newlines=True,
                                creationflags=flags
                            )
                            break
                        except Exception as e:
                            safe_log_message(f"✗ Failed to run: {str(e)[:200]}", "orange")
                            continue
                    else:
                        safe_update_status("Failed to start miunlock!", "red")
                        safe_log_message("All run attempts failed", "red")
                        return

                    def read_output():
                        try:
                            for line in iter(process.stdout.readline, ''):
                                if window_closed:
                                    break
                                if line:
                                    line_stripped = line.strip()
                                    if line_stripped:
                                        if not window_closed:
                                            unlock_window.after(0, lambda l=line_stripped: log_message(l, "white"))
                        except Exception as e:
                            if "closed" not in str(e).lower() and not window_closed:
                                unlock_window.after(0, lambda: log_message(trans.tr('mi_unlock_read_error').format(e),
                                                                           "red"))

                    read_thread = threading.Thread(target=read_output, daemon=True)
                    read_thread.start()

                    process.wait()

                    if not window_closed:
                        if process.returncode == 0:
                            unlock_window.after(0, lambda: update_status('mi_unlock_completed', "green"))
                            unlock_window.after(0, lambda: log_message(trans.tr('mi_unlock_finished'), "green"))
                        else:
                            unlock_window.after(0, lambda: log_message(
                                trans.tr('mi_unlock_process_exit').format(process.returncode), "orange"))

                except Exception as e:
                    if not window_closed:
                        unlock_window.after(0, lambda: update_status(trans.tr('mi_unlock_error').format(str(e)), "red"))
                        unlock_window.after(0,
                                            lambda: log_message(trans.tr('mi_unlock_critical_error').format(e), "red"))

            threading.Thread(target=install_and_run_miunlock, daemon=True).start()
            unlock_window.protocol("WM_DELETE_WINDOW", on_close)

        except Exception as e:
            trans = self.translation
            messagebox.showerror(trans.tr('error_title'), trans.tr('mi_unlock_critical_error').format(e))


def main():
    global root
    root = ctk.CTk()
    app = XiaomiUnlockTool(root)
    root.app = app
    root.mainloop()


if __name__ == "__main__":
    main()