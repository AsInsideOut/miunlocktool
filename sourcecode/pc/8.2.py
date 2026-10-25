import subprocess
import sys
import os
import time
from datetime import datetime, timedelta, timezone
import tkinter as tk
from tkinter import messagebox, colorchooser
import webbrowser
import re
import threading
import queue
import collections
import heapq
import json
import colorsys
import concurrent.futures

base_path = os.path.dirname(os.path.abspath(__file__))
if base_path not in sys.path:
    sys.path.insert(0, base_path)

res_path = os.path.join(base_path, 'res')
if res_path not in sys.path:
    sys.path.insert(0, res_path)

miunlock_path = os.path.join(base_path, 'miunlock')
if miunlock_path not in sys.path:
    sys.path.insert(0, miunlock_path)

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
    from res.theme import *
    from res.api_handler import RequestHandler
    from res.settings import WelcomeWindow, UpdateChecker, get_update_check_url, get_update_download_url
    from res.lang import Translation
    from res.xiaomi_auth import XiaomiAuthPanel
    from res.settings_ui import (
        build_about_section, build_general_section,
        build_cookies_section, build_trouble_section
    )
    from res.timing_dialog import (
        TimingSettingsDialog, DEFAULT_AUTO_TIMINGS, ALL_AVAILABLE_TIMINGS,
        TIMING_PROFILES, parse_timing_value
    )
    from res.color_picker import CustomColorPickerDialog
    from res.hyperos_bypass import HyperOSBypassPanel
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
    from settings import WelcomeWindow, UpdateChecker, get_update_check_url, get_update_download_url
    from lang import Translation
    from xiaomi_auth import XiaomiAuthPanel
    from settings_ui import (
        build_about_section, build_general_section,
        build_cookies_section, build_trouble_section
    )
    from timing_dialog import (
        TimingSettingsDialog, DEFAULT_AUTO_TIMINGS, ALL_AVAILABLE_TIMINGS,
        TIMING_PROFILES, parse_timing_value
    )
    from color_picker import CustomColorPickerDialog
    from hyperos_bypass import HyperOSBypassPanel

# Всегда используем темную тему
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CURRENT_VERSION = "8.2"

CONFIG_DIR = os.path.join(os.environ['APPDATA'], 'MiUnlockTool') if os.name == 'nt' else os.path.join(os.path.expanduser('~'), '.config', 'MiUnlockTool')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

MI_SERVERS = ['sgp-api.buy.mi.com']


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
        height = kwargs.pop('height', heights.get(size, 40))
        corner_radius = kwargs.pop('corner_radius', 14)

        if button_type == 'filled':
            fg_color = kwargs.pop('fg_color', MaterialColors.get_color('primary'))
            hover_color = kwargs.pop('hover_color', MaterialColors.get_color('primary_container'))
            text_color = kwargs.pop('text_color', MaterialColors.get_color('on_primary'))
            border_width = kwargs.pop('border_width', 0)
        elif button_type == 'outlined':
            fg_color = kwargs.pop('fg_color', 'transparent')
            hover_color = kwargs.pop('hover_color', MaterialColors.get_color('surface_container_high'))
            text_color = kwargs.pop('text_color', MaterialColors.get_color('primary'))
            border_width = kwargs.pop('border_width', 1)
            border_color = kwargs.pop('border_color', MaterialColors.get_color('outline'))
        else:
            fg_color = kwargs.pop('fg_color', 'transparent')
            hover_color = kwargs.pop('hover_color', MaterialColors.get_color('surface_container_high'))
            text_color = kwargs.pop('text_color', MaterialColors.get_color('primary'))
            border_width = kwargs.pop('border_width', 0)

        super().__init__(
            master, text=text, height=height, command=command,
            fg_color=fg_color, hover_color=hover_color, text_color=text_color,
            border_width=border_width, corner_radius=corner_radius, **kwargs
        )
        if button_type == 'outlined' and border_width > 0 and 'border_color' in locals():
            self.configure(border_color=border_color)



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
            elif lang_lower.startswith("ua") or lang_lower.startswith("uk") or "ukrainian" in lang_lower:
                return "ua"
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
    elif "ua" in env_lang or "uk" in env_lang or "ukrainian" in env_lang:
        return "ua"
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
        'animations_enabled': True,
        'beijing_clock_collapsed': False
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
            merged['animations_enabled'] = bool(config.get('animations_enabled', True))

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


class FooterToolTip:
    """Всплывающая подсказка Material 3 для плашки-подвала."""
    def __init__(self, widget, text_getter):
        self.widget = widget
        self.text_getter = text_getter
        self.tip_window = None
        self.after_id = None
        widget.bind('<Enter>', self.schedule, add='+')
        widget.bind('<Leave>', self.hide, add='+')
        widget.bind('<ButtonPress>', self.hide, add='+')

    def schedule(self, event=None):
        self.unschedule()
        try:
            self.after_id = self.widget.after(450, self.show)
        except Exception:
            pass

    def unschedule(self):
        if self.after_id:
            try:
                self.widget.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def show(self, event=None):
        if self.tip_window or not self.widget.winfo_exists():
            return
        try:
            x = self.widget.winfo_rootx() + 10
            y = self.widget.winfo_rooty() - 85
            self.tip_window = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            tw.attributes("-topmost", True)

            text = self.text_getter() if callable(self.text_getter) else self.text_getter
            container = tk.Frame(
                tw,
                bg=MaterialColors.get_color('surface_container_highest'),
                padx=10,
                pady=7,
                highlightbackground=MaterialColors.get_color('outline_variant'),
                highlightthickness=1
            )
            container.pack()
            lbl = tk.Label(
                container,
                text=text,
                justify='left',
                bg=MaterialColors.get_color('surface_container_highest'),
                fg=MaterialColors.get_color('on_surface'),
                font=('Arial', 9)
            )
            lbl.pack()
        except Exception:
            self.hide()

    def hide(self, event=None):
        self.unschedule()
        if self.tip_window:
            try:
                self.tip_window.destroy()
            except Exception:
                pass
            self.tip_window = None


class FooterTitleLabel(ctk.CTkLabel):
    """Специальный лейбл заголовка подвала, адаптирующийся под смену режима и языка."""
    def __init__(self, master, outer, is_mi=False, **kwargs):
        super().__init__(master, **kwargs)
        self.outer = outer
        self.is_mi = is_mi

    def configure(self, **kwargs):
        if 'text' in kwargs:
            raw = kwargs.pop('text')
            if self.is_mi:
                new_text = self.outer.translation.tr('tab_mi_unlock')
            else:
                mode_val = getattr(self.outer, 'mode_var', None)
                manual_text = self.outer.translation.tr('manual_mode')
                desc_manual_line = self.outer.translation.tr('desc_manual').splitlines()[0] if self.outer.translation.tr('desc_manual') else ''
                is_manual = (
                    ('desc_manual' in str(raw)) or 
                    (desc_manual_line and desc_manual_line in str(raw)) or 
                    (mode_val and mode_val.get() == manual_text)
                )
                if is_manual:
                    new_text = f"{self.outer.translation.tr('main_title')} • {manual_text}"
                else:
                    new_text = self.outer.translation.tr('main_title')
            kwargs['text'] = new_text
        super().configure(**kwargs)



class ThreadCoordinator:
    """
    Hardware-adaptive thread coordinator.
    Allocates and bounds execution streams:
    - High-core CPUs (cores > 2): 4 managed threads total (Main + Send + BgWorker + TimeEngine), strictly <= 5 active.
    - Low-core / weak CPUs (cores <= 2): 2 managed threads total:
        * Thread 1: Dedicated Send stream (isolated network dispatching)
        * Thread 2: Main GUI thread (handles UI, cooperative time tracking, and cooperative jobs)
    """
    def __init__(self, app):
        self.app = app
        self.root = getattr(app, 'root', None)
        self.cpu_count = os.cpu_count() or 2
        self.is_weak_cpu = self.cpu_count <= 2
        self._running = True

        # --- STREAM 2: Main GUI Dispatch Queue (Thread-Safe UI Bridge) ---
        self._ui_queue = queue.Queue()
        if self.root is not None:
            self._schedule_ui_drain()

        # --- STREAM 1: Send Dispatcher (Dedicated Network / Send Thread) ---
        self._send_cond = threading.Condition()
        self._send_scheduled = []  # min-heap of (target_perf, seq, func, args, kwargs)
        self._send_immediate = collections.deque()
        self._send_seq = 0
        self._send_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=32,
            thread_name_prefix="SendWorker"
        )
        self.send_thread = threading.Thread(
            target=self._send_dispatcher_loop,
            name="SendDispatcherThread",
            daemon=True
        )
        self.send_thread.start()

        # --- STREAM 3 & 4 (High-core mode) vs STREAM 2 Cooperative (Weak-core mode) ---
        if not self.is_weak_cpu:
            # STREAM 3: Background Worker Thread (updates, async disk logs, eligibility)
            self._bg_queue = queue.Queue()
            self._log_queue = queue.Queue()
            self.bg_worker_thread = threading.Thread(
                target=self._bg_worker_loop,
                name="BgWorkerThread",
                daemon=True
            )
            self.bg_worker_thread.start()

            # STREAM 4: Time Calculation & Sync Engine
            self._time_lock = threading.Lock()
            self._time_sync_active = False
            self._start_beijing_time = None
            self._start_perf = 0.0
            self._last_ui_clock_update = 0.0
            self._ping_target = None
            self._ping_callback = None
            self._multi_target = None
            self._multi_callback = None
            self._single_target = None
            self._single_callback = None
            self.time_engine_thread = threading.Thread(
                target=self._time_engine_loop,
                name="TimeEngineThread",
                daemon=True
            )
            self.time_engine_thread.start()
        else:
            self._bg_queue = None
            self._log_queue = None
            self.bg_worker_thread = None
            self.time_engine_thread = None
            self._time_sync_active = False
            self._start_beijing_time = None
            self._start_perf = 0.0
            self._ping_target = None
            self._ping_callback = None
            self._multi_target = None
            self._multi_callback = None
            self._single_target = None
            self._single_callback = None

    def _schedule_ui_drain(self):
        if not self._running:
            return
        if self.root is not None:
            try:
                if hasattr(self.root, 'winfo_exists') and not self.root.winfo_exists():
                    return
                self._drain_after_id = self.root.after(15, self._drain_ui_queue)
            except Exception:
                pass

    def _drain_ui_queue(self):
        if not self._running:
            return
        try:
            processed = 0
            while not self._ui_queue.empty() and processed < 64:
                try:
                    func, args, kwargs = self._ui_queue.get_nowait()
                    func(*args, **kwargs)
                    processed += 1
                except (queue.Empty, Exception):
                    break
        finally:
            self._schedule_ui_drain()

    def post_to_ui(self, func, *args, **kwargs):
        """Safely executes func on Main GUI Thread (Thread 2) with microsecond non-blocking dispatch."""
        if self.root is None or threading.current_thread() is threading.main_thread():
            try:
                func(*args, **kwargs)
            except Exception as e:
                print(f"[UI] Direct execution error: {e}")
        else:
            self._ui_queue.put((func, args, kwargs))

    def submit_send(self, func, *args, **kwargs):
        """Submits an immediate network/send task to Dedicated Send Thread (Thread 1)."""
        with self._send_cond:
            self._send_immediate.append((func, args, kwargs))
            self._send_cond.notify()

    def schedule_send_in(self, delay_seconds, func, *args, **kwargs):
        """Schedules a send task after delay_seconds on Thread 1 with microsecond precision."""
        target_perf = time.perf_counter() + max(0.0, float(delay_seconds))
        with self._send_cond:
            self._send_seq += 1
            heapq.heappush(self._send_scheduled, (target_perf, self._send_seq, func, args, kwargs))
            self._send_cond.notify()

    def _execute_send_task(self, func, args, kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            print(f"[SendWorker] Error executing task: {e}")

    def _dispatch_send(self, func, args, kwargs):
        """Asynchronously dispatches network request task immediately without waiting for server response."""
        if not self._running:
            return
        dispatched = False
        if hasattr(self, '_send_executor') and self._send_executor is not None:
            try:
                self._send_executor.submit(self._execute_send_task, func, args, kwargs)
                dispatched = True
            except Exception:
                dispatched = False
        if not dispatched:
            try:
                th = threading.Thread(
                    target=self._execute_send_task,
                    args=(func, args, kwargs),
                    daemon=True
                )
                th.start()
            except Exception as e:
                print(f"[SendDispatcher] Failed to dispatch task: {e}")

    def _send_dispatcher_loop(self):
        while self._running:
            func = None
            args = ()
            kwargs = {}
            with self._send_cond:
                while self._running and not self._send_immediate and not self._send_scheduled:
                    self._send_cond.wait(timeout=0.2)

                if not self._running:
                    break

                # 1. Immediate tasks take top priority
                if self._send_immediate:
                    func, args, kwargs = self._send_immediate.popleft()
                # 2. Check scheduled tasks
                elif self._send_scheduled:
                    target_perf = self._send_scheduled[0][0]
                    now = time.perf_counter()
                    remaining = target_perf - now
                    if remaining <= 0:
                        _, _, func, args, kwargs = heapq.heappop(self._send_scheduled)
                    elif remaining > 0.003:
                        # Sleep until 2ms before target
                        self._send_cond.wait(timeout=remaining - 0.002)
                        continue
                    else:
                        # High-precision spin-wait for microsecond accuracy
                        while time.perf_counter() < target_perf:
                            pass
                        _, _, func, args, kwargs = heapq.heappop(self._send_scheduled)

            if func is not None:
                self._dispatch_send(func, args, kwargs)

    def submit_bg_task(self, func, *args, **kwargs):
        """Submits a background task to Worker Stream (Thread 3) or cooperative executor."""
        if not self.is_weak_cpu and self._bg_queue is not None:
            self._bg_queue.put((func, args, kwargs))
        else:
            # On weak CPUs: Thread 2 handles all non-send computations
            if self.root is not None:
                try:
                    self.root.after(10, lambda: func(*args, **kwargs))
                except Exception:
                    func(*args, **kwargs)
            else:
                func(*args, **kwargs)

    def queue_log_write(self, formatted_message):
        """Dispatches log writing to disk asynchronously without blocking send or UI."""
        if not self.app.settings.get('log_to_txt', True):
            return

        if not self.is_weak_cpu and self._log_queue is not None:
            self._log_queue.put(formatted_message)
        else:
            self._write_log_direct(formatted_message)

    def _write_log_direct(self, formatted_message):
        try:
            target_file = getattr(self.app, 'current_log_file', None)
            if not target_file and hasattr(self.app, '_ensure_log_file'):
                self.app._ensure_log_file()
                target_file = getattr(self.app, 'current_log_file', None)
            if target_file:
                with open(target_file, 'a', encoding='utf-8') as f:
                    f.write(formatted_message)
        except Exception as e:
            print(f"[Logger] Write error: {e}")

    def _bg_worker_loop(self):
        while self._running:
            # 1. Drain batched log messages
            if self._log_queue is not None:
                batch = []
                while not self._log_queue.empty():
                    try:
                        batch.append(self._log_queue.get_nowait())
                    except queue.Empty:
                        break
                if batch:
                    self._write_log_direct("".join(batch))

            # 2. Process background tasks
            if self._bg_queue is not None:
                try:
                    task = self._bg_queue.get(timeout=0.1)
                    if task is None or not self._running:
                        break
                    func, args, kwargs = task
                    try:
                        func(*args, **kwargs)
                    except Exception as e:
                        print(f"[BgWorker] Task error: {e}")
                        self._bg_queue.task_done()
                except queue.Empty:
                    pass

    def arm_time_sync(self, start_beijing_time, start_timestamp):
        """Arms precision Beijing time tracking."""
        self._start_beijing_time = start_beijing_time
        self._start_perf = time.perf_counter()
        self._time_sync_active = True
        self._last_ui_clock_update = 0.0

    def get_synced_beijing_time(self):
        """Calculates current Beijing time based on perf_counter elapsed."""
        if not self._time_sync_active or not self._start_beijing_time:
            return None
        elapsed = time.perf_counter() - self._start_perf
        return self._start_beijing_time + timedelta(seconds=elapsed)

    def watch_ping_target(self, target_ping_start, on_reached):
        """Watches for target schedule time (compatibility redirect)."""
        self.watch_multi_target(target_ping_start, on_reached)

    def watch_multi_target(self, schedule_time, on_reached):
        """Watches for manual multi-request schedule time."""
        self._multi_target = schedule_time
        self._multi_callback = on_reached
        if self.is_weak_cpu and self.root is not None:
            self._cooperative_multi_check()

    def _cooperative_multi_check(self):
        if not self._time_sync_active or not self._multi_target:
            return
        now = self.get_synced_beijing_time()
        if now and now >= self._multi_target:
            cb = self._multi_callback
            self._multi_target = None
            self._multi_callback = None
            if cb:
                cb()
        else:
            if self.root is not None:
                self.root.after(50, self._cooperative_multi_check)

    def watch_single_target(self, send_at, on_reached):
        """Watches for single request target time."""
        self._single_target = send_at
        self._single_callback = on_reached
        if self.is_weak_cpu and self.root is not None:
            self._cooperative_single_check()

    def _cooperative_single_check(self):
        if not self._time_sync_active or not self._single_target:
            return
        now = self.get_synced_beijing_time()
        if now and now >= self._single_target:
            cb = self._single_callback
            self._single_target = None
            self._single_callback = None
            if cb:
                cb()
        else:
            if self.root is not None:
                self.root.after(20, self._cooperative_single_check)

    def _time_engine_loop(self):
        """STREAM 4: Time Calculation & Sync Engine loop."""
        while self._running:
            try:
                if self._time_sync_active and self._start_beijing_time:
                    now = self.get_synced_beijing_time()
                    now_perf = time.perf_counter()

                    # 1. Check Multi Target
                    if self._multi_target and now and now >= self._multi_target:
                        cb = self._multi_callback
                        self._multi_target = None
                        self._multi_callback = None
                        if cb:
                            self.post_to_ui(cb)

                    # 3. Check Single Target
                    if self._single_target and now and now >= self._single_target:
                        cb = self._single_callback
                        self._single_target = None
                        self._single_callback = None
                        if cb:
                            self.submit_send(cb)

                    # 4. Periodic UI Clock string update (every 100ms)
                    if now and now_perf - self._last_ui_clock_update >= 0.10:
                        self._last_ui_clock_update = now_perf
                        time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                        if hasattr(self.app, '_update_clock_text'):
                            self.post_to_ui(self.app._update_clock_text, time_str)

                time.sleep(0.01)
            except Exception as e:
                time.sleep(0.05)

    def cancel_active_targets(self):
        """Cancels any pending single or multi targets and scheduled sends."""
        self._single_target = None
        self._single_callback = None
        self._multi_target = None
        self._multi_callback = None
        with self._send_cond:
            self._send_scheduled.clear()
            self._send_immediate.clear()

    def stop(self):
        """Stops all background threads gracefully."""
        self._running = False
        if getattr(self, '_drain_after_id', None) and self.root:
            try:
                self.root.after_cancel(self._drain_after_id)
            except Exception:
                pass
            self._drain_after_id = None

        with self._send_cond:
            self._send_cond.notify_all()

        if hasattr(self, '_send_executor') and self._send_executor is not None:
            try:
                self._send_executor.shutdown(wait=False)
            except Exception:
                pass

        if getattr(self, '_bg_queue', None) is not None:
            try:
                self._bg_queue.put(None)
            except Exception:
                pass

        for th in (getattr(self, 'send_thread', None), getattr(self, 'bg_worker_thread', None), getattr(self, 'time_engine_thread', None)):
            if th and th.is_alive() and th is not threading.current_thread():
                th.join(timeout=0.3)


class LanguageDownloadPopup(ctk.CTkToplevel):
    """Мини-попап, отображаемый во время реального скачивания языкового пакета."""
    def __init__(self, parent, lang_code, lang_display_name, translation=None):
        super().__init__(parent)
        self.parent = parent
        self.lang_code = lang_code
        self.translation = translation

        ctk.set_appearance_mode("Dark")
        is_ru = getattr(translation, 'language', 'ru') == 'ru'
        win_title = translation.tr('lang_download_title') if translation else ("Скачивание языка" if is_ru else "Downloading Language")
        self.title(win_title)

        win_w = 380
        win_h = 135
        try:
            parent.update_idletasks()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pos_x = max(0, px + (pw - win_w) // 2)
            pos_y = max(0, py + (ph - win_h) // 2)
        except Exception:
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            pos_x = max(0, (screen_w - win_w) // 2)
            pos_y = max(0, (screen_h - win_h) // 2)

        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.resizable(False, False)
        self.transient(parent)
        self.attributes('-topmost', True)

        self.protocol("WM_DELETE_WINDOW", self.close)

        card = ctk.CTkFrame(
            self,
            fg_color=MaterialColors.get_color('surface_container_high'),
            corner_radius=14,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        card.pack(fill="both", expand=True, padx=8, pady=8)

        content_row = ctk.CTkFrame(card, fg_color="transparent")
        content_row.pack(fill="x", padx=16, pady=(14, 6))

        icon_label = ctk.CTkLabel(
            content_row,
            text="📥",
            font=("Segoe UI Emoji", 24),
            width=32
        )
        icon_label.pack(side="left", padx=(0, 10))

        text_col = ctk.CTkFrame(content_row, fg_color="transparent")
        text_col.pack(side="left", fill="x", expand=True)

        header_text = translation.tr('lang_download_msg') if translation else ("Скачивание языкового пакета..." if is_ru else "Downloading language pack...")
        self.title_label = ctk.CTkLabel(
            text_col,
            text=header_text,
            font=("Arial", 13, "bold"),
            text_color=MaterialColors.get_color('on_surface'),
            anchor="w"
        )
        self.title_label.pack(fill="x")

        sub_domain = "miunlocktool.ru" if self.translation.language == "ru" else "miunlock.su"
        sub_text = f"{lang_display_name} • {sub_domain}"
        self.sub_label = ctk.CTkLabel(
            text_col,
            text=sub_text,
            font=("Arial", 11),
            text_color=MaterialColors.get_color('on_surface_variant'),
            anchor="w"
        )
        self.sub_label.pack(fill="x", pady=(2, 0))

        self.progress_bar = ctk.CTkProgressBar(
            card,
            height=6,
            corner_radius=3,
            mode="indeterminate",
            progress_color=MaterialColors.get_color('primary')
        )
        self.progress_bar.pack(fill="x", padx=16, pady=(10, 10))
        self.progress_bar.start()

    def close(self):
        try:
            self.progress_bar.stop()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass


class XiaomiUnlockTool:
    def __init__(self, root):
        self.root = root
        self.config = load_config()
        self.translation = Translation(self.config.get('language', 'ru'))

        self.root.title(self.translation.tr('title'))

        # Responsive sizing: fits 700p/720p screens while supporting fullscreen expansion
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        default_w = 1100
        default_h = 620
        if screen_h <= 720:
            default_h = min(620, max(540, screen_h - 70))
        if screen_w < 1140:
            default_w = max(800, screen_w - 40)
        pos_x = max(0, (screen_w - default_w) // 2)
        pos_y = max(0, (screen_h - default_h) // 2 - 20)
        self.root.geometry(f"{default_w}x{default_h}+{pos_x}+{pos_y}")
        self.root.minsize(min(1100, screen_w), 520)
        self.root.resizable(True, True)

        # Fullscreen bindings (F11 toggles, Escape exits)
        self.is_fullscreen = False
        self.root.bind("<F11>", self.toggle_fullscreen, "+")
        self.root.bind("<Escape>", self.exit_fullscreen, "+")

        saved_theme_color = self.config.get('custom_primary_color', '#D0BCFF')
        if isinstance(saved_theme_color, str) and re.fullmatch(r'#[0-9A-Fa-f]{6}', saved_theme_color):
            self._load_custom_theme_palette(saved_theme_color)
        else:
            saved_theme_color = MaterialColors.get_color('primary')
        self.root.configure(fg_color=MaterialColors.get_color('background'))

        self.root.bind_all("<KeyRelease>", _on_key_release, "+")

        detected_region = detect_user_region()
        saved_region = self.config.get('region', detected_region)

        def _get_prof_by_reg(reg):
            if reg == 'Asia':
                return 'asia'
            elif reg in ('America', 'USA', 'Africa'):
                return 'usa_africa'
            return 'europe'

        default_prof = _get_prof_by_reg(saved_region)
        initial_profile = self.config.get('timing_profile', default_prof)
        if initial_profile not in TIMING_PROFILES:
            initial_profile = default_prof

        self.current_timing_profile = initial_profile
        profile_timings = TIMING_PROFILES[initial_profile]['timings']

        self.settings = {
            'full_log': False,
            'skip_cookie_check': self.config.get('skip_cookie_check', False),
            'theme': 'Dark',
            'color_theme': 'Material 3',
            'log_to_txt': self.config.get('log_to_txt', True),
            'language': self.config.get('language', 'ru'),
            'region': saved_region,
            'animations_enabled': bool(self.config.get('animations_enabled', True)),
            'timing_profile': initial_profile,
            'auto_timings': self.config.get('auto_timings', list(profile_timings)),
            'custom_primary_color': saved_theme_color
        }
        self.selected_timings = list(self.settings.get('auto_timings', profile_timings))
        self.skip_cookie_check_var = ctk.BooleanVar(value=self.settings.get('skip_cookie_check', False))
        self.log_to_txt_var = ctk.BooleanVar(value=self.settings.get('log_to_txt', True))
        self.animations_enabled_var = ctk.BooleanVar(value=bool(self.settings.get('animations_enabled', True)))
        self.beijing_clock_collapsed = bool(self.config.get('beijing_clock_collapsed', False))
        self.beijing_clock_container = None
        self.beijing_collapsed_btn = None
        self.beijing_collapse_btn = None
        self.config['theme'] = 'Dark'
        self.config['region'] = self.settings['region']
        self.config['animations_enabled'] = self.settings['animations_enabled']
        self.config['timing_profile'] = self.current_timing_profile
        self.animations_checkbox = None

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
        self.manual_time_var = ctk.StringVar(value=", ".join(f"{t:.3f}" for t in self.selected_timings))
        self.auto_mode_index = 2

        self.cookie_value.trace_add('write', self.auto_save_cookie)

        self.manual_time_frame = None
        self.mode_segmented = None
        self.profiles_menu_container = None
        self.profiles_menu_visible = False
        self.profile_buttons = {}

        # Переменные для системы вкладок
        self.current_tab = "unlock"  # unlock, settings, mi_unlock
        self.tab_containers = {}
        self.tab_buttons = {}

        self.create_material_ui()

        self.request_handler = RequestHandler(self)
        self.thread_coordinator = ThreadCoordinator(self)
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
        except Exception:
            pass

        self.start_beijing_time = None
        self.start_timestamp = None

        self.current_log_file = None
        try:
            if self.settings.get('log_to_txt', True):
                self._ensure_log_file()
        except Exception:
            pass

        self.show_welcome_if_needed()
        self._tick_beijing_clock()

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
            site_url = "https://miunlocktool.ru/" if getattr(self, "translation", None) and self.translation.language == "ru" else "https://miunlock.su/"
            webbrowser.open(site_url, new=2)
        except Exception as e:
            print(f"Site link open error: {e}")

    def open_4pda(self):
        try:
            webbrowser.open("https://4pda.to/forum/index.php?showtopic=721838&view=findpost&p=145201115", new=2)
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

        if self.translation.is_download_needed(new_lang):
            self._download_and_apply_language(new_lang)
        else:
            self._apply_language(new_lang)

    def _apply_language(self, new_lang):
        success = self.translation.set_language(new_lang)
        if not success:
            self.language_var.set(self.translation.language)
            return

        self.settings['language'] = self.translation.language
        self.language_var.set(self.translation.language)
        self.save_settings()
        if hasattr(self, '_clear_settings_cache'):
            self._clear_settings_cache()
        self.update_ui_text()

    def _download_and_apply_language(self, new_lang):
        lang_name = Translation.get_display_name(new_lang)
        popup = LanguageDownloadPopup(self.root, new_lang, lang_name, self.translation)
        finished = [False]

        def on_finish(success):
            if finished[0]:
                return
            finished[0] = True
            popup.close()
            if not success:
                try:
                    from tkinter import messagebox
                    err_msg = self.translation.tr('lang_download_failed', lang_name)
                    messagebox.showerror(
                        self.translation.tr('error_title'),
                        err_msg
                    )
                except Exception:
                    pass
                self.language_var.set(self.translation.language)
                return

            self.settings['language'] = self.translation.language
            self.language_var.set(self.translation.language)
            self.save_settings()
            if hasattr(self, '_clear_settings_cache'):
                self._clear_settings_cache()
            self.update_ui_text()

        # Watchdog: close popup after 12 seconds if network completely stalled
        self.root.after(12000, lambda: on_finish(False) if not finished[0] else None)

        def worker():
            success = False
            try:
                start_t = time.time()
                success = self.translation.set_language(new_lang)
                elapsed = time.time() - start_t
                if elapsed < 0.3:
                    time.sleep(0.3 - elapsed)
            except Exception as e:
                print(f"[LanguageDownload] Error downloading language '{new_lang}': {e}")
                success = False
            finally:
                self.root.after(0, lambda: on_finish(success))

        threading.Thread(target=worker, daemon=True).start()

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
                self.settings['animations_enabled'] = bool(self.animations_enabled_var.get())
            if hasattr(self, 'language_var'):
                self.settings['language'] = self.language_var.get()
            self.settings['theme'] = 'Dark'
            self.config['skip_cookie_check'] = self.settings['skip_cookie_check']
            self.config['theme'] = 'Dark'
            self.config['language'] = self.settings.get('language', self.translation.language)
            self.config['log_to_txt'] = self.settings['log_to_txt']
            self.config['animations_enabled'] = self.settings.get('animations_enabled', True)
            self.config['region'] = self.settings.get('region', detect_user_region())
            self.config['cookie'] = self.cookie_value.get()
            self.config['login_user'] = self.settings.get('login_user', '')
            self.config['login_pwd'] = self.settings.get('login_pwd', '')
            self.config['login_wb_id'] = self.settings.get('login_wb_id', '')
            if hasattr(self, 'selected_timings'):
                self.settings['auto_timings'] = self.selected_timings
                self.config['auto_timings'] = self.selected_timings

            save_config(self.config)
            return True
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
            return False

    def create_material_ui(self):
        dark_mode = True

        self.main_container = ctk.CTkFrame(
            self.root,
            fg_color=MaterialColors.get_color('background')
        )
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # === TOP BAR (с кнопками вкладок) ===
        self.top_bar = MD3Card(self.main_container, elevation=1)
        self.top_bar.pack(fill="x", pady=(0, 8), padx=0)

        top_bar_inner = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        top_bar_inner.pack(fill="x", padx=18, pady=10)

        # Левая часть - заголовок
        title_frame = ctk.CTkFrame(top_bar_inner, fg_color="transparent")
        title_frame.pack(side="left")

        self.title_label = MD3Label(
            title_frame,
            text=self.translation.tr('main_title'),
            typography='headline_medium'
        )
        self.title_label.pack(side="left")

        # Правая часть - язык, регион
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
            values=['ru', 'en', 'ua', 'id', 'es', 'zh', 'pt'],
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

        user_reg = self.settings.get('region', detect_user_region())
        self.header_region_label = MD3Label(
            top_bar_inner,
            text=self.translation.tr('header_region').format(user_reg),
            typography='label_large',
            text_color='#FFFFFF'
        )
        self.header_region_label.pack(side="right", padx=(0, 10))

        # Центральная часть - кнопки вкладок на верхней панели
        self.tab_bar = ctk.CTkFrame(top_bar_inner, fg_color="transparent")
        self.tab_bar.pack(side="left", expand=True)

        self.tab_buttons['settings'] = MD3Button(
            self.tab_bar,
            text=self.translation.tr('tab_settings'),
            button_type='outlined',
            size='small',
            height=32,
            corner_radius=10,
            font=("Arial", 12),
            command=lambda: self.switch_tab("settings")
        )
        self.tab_buttons['settings'].pack(side="left", padx=(0, 6))

        self.tab_buttons['unlock'] = MD3Button(
            self.tab_bar,
            text=self.translation.tr('tab_unlock'),
            button_type='filled',
            size='small',
            height=32,
            corner_radius=10,
            font=("Arial", 12),
            command=lambda: self.switch_tab("unlock")
        )
        self.tab_buttons['unlock'].pack(side="left", padx=(0, 6))

        # Левее кнопки Mi Unlock: плажка и кнопка HyperOS 1 Bypass
        self.tab_buttons['hyperos1_bypass'] = MD3Button(
            self.tab_bar,
            text=self.translation.tr('tab_hyperos1_bypass'),
            button_type='outlined',
            size='small',
            height=32,
            corner_radius=10,
            font=("Arial", 12),
            command=lambda: self.switch_tab("hyperos1_bypass")
        )
        self.tab_buttons['hyperos1_bypass'].pack(side="left", padx=(0, 6))

        self.tab_buttons['mi_unlock'] = MD3Button(
            self.tab_bar,
            text=self.translation.tr('tab_mi_unlock'),
            button_type='outlined',
            size='small',
            height=32,
            corner_radius=10,
            font=("Arial", 12),
            command=lambda: self.switch_tab("mi_unlock")
        )
        self.tab_buttons['mi_unlock'].pack(side="left", padx=0)

        # === CONTENT AREA ===
        self.content_area = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.content_area.pack(fill="both", expand=True, padx=16)

        # Создаем контейнеры для каждой вкладки
        self.tab_containers['unlock'] = ctk.CTkFrame(self.content_area, fg_color=MaterialColors.get_color('background'))
        self.tab_containers['settings'] = ctk.CTkFrame(self.content_area, fg_color=MaterialColors.get_color('background'))
        self.tab_containers['hyperos1_bypass'] = ctk.CTkFrame(self.content_area, fg_color=MaterialColors.get_color('background'))
        self.tab_containers['mi_unlock'] = ctk.CTkFrame(self.content_area, fg_color=MaterialColors.get_color('background'))

        # Создаем UI для вкладки "Подача заявок"
        self._create_unlock_tab()

        # Создаем встроенную вкладку "Настройки и инструкции"
        self._create_settings_tab()

        # Создаем вкладку-заглушку "HyperOS 1 Bypass"
        self._create_hyperos1_bypass_tab()

        # Создаем UI для вкладки "Mi Unlock"
        self._create_mi_unlock_tab()

        # Устанавливаем Авторежим #2 по умолчанию
        self.auto_mode_index = 2
        self.mode_var.set(self.translation.tr('auto_mode_2'))
        self.toggle_mode(self.mode_var.get())

        # Показываем первую вкладку по умолчанию
        self.current_tab = None
        self.switch_tab("unlock")

    def _get_footer_tooltip_text(self, is_mi=False):
        try:
            key = 'mi_unlock_desc' if is_mi else (
                'desc_manual' if getattr(self, 'mode_var', None) and self.mode_var.get() == self.translation.tr('manual_mode') else 'desc'
            )
            raw_desc = self.translation.tr(key).strip()
            lang = getattr(self.translation, 'language', getattr(self, 'current_language', 'ru'))
            if lang == 'ru':
                hint = "\n(Нажмите, чтобы открыть раздел 'Авторы')"
            else:
                hint = "\n(Click to open 'Authors' section)"
            return f"{raw_desc}{hint}"
        except Exception:
            return f"Xiaomi Unlock Tool v{CURRENT_VERSION}\npktloss • New G3n"

    @staticmethod
    def _setup_hover_outline(btn, default_border='#202020', hover_border='#FFFFFF', default_border_width=1):
        btn.configure(border_width=default_border_width, border_color=default_border)
        def on_enter(e):
            try:
                if hasattr(btn, 'winfo_exists') and btn.winfo_exists():
                    btn.configure(border_color=hover_border)
            except Exception:
                pass
        def on_leave(e):
            try:
                if hasattr(btn, 'winfo_exists') and btn.winfo_exists():
                    btn.configure(border_color=default_border)
            except Exception:
                pass
        for target in [btn, getattr(btn, '_canvas', None), getattr(btn, '_text_label', None)]:
            if target:
                target.bind('<Enter>', on_enter, add='+')
                target.bind('<Leave>', on_leave, add='+')

    def _create_compact_footer(self, parent, is_mi=False):
        """Создает стильную и компактную плашку-подвал Material 3 (версия, разработчики, название)."""
        prefix = 'mi_' if is_mi else ''

        footer_frame = ctk.CTkFrame(
            parent,
            height=36,
            corner_radius=10,
            fg_color=MaterialColors.get_color('surface_container_low'),
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        footer_frame.pack_propagate(False)

        left_box = ctk.CTkFrame(footer_frame, fg_color="transparent")
        left_box.pack(side="left", padx=(8, 4), pady=4)

        badge_frame = ctk.CTkFrame(
            left_box,
            corner_radius=6,
            fg_color=MaterialColors.get_color('primary_container')
        )
        badge_frame.pack(side="left")

        badge_lbl = ctk.CTkLabel(
            badge_frame,
            text=f"v{CURRENT_VERSION}",
            font=("Arial", 10, "bold"),
            text_color=MaterialColors.get_color('on_primary_container')
        )
        badge_lbl.pack(padx=6, pady=1)

        title_text = self.translation.tr('tab_mi_unlock') if is_mi else self.translation.tr('main_title')
        title_lbl = FooterTitleLabel(
            footer_frame,
            outer=self,
            is_mi=is_mi,
            text=title_text,
            font=("Arial", 11),
            text_color=MaterialColors.get_color('on_surface_variant')
        )
        title_lbl.place(relx=0.5, rely=0.5, anchor="center")

        right_box = ctk.CTkFrame(footer_frame, fg_color="transparent")
        right_box.pack(side="right", padx=(4, 6), pady=4)

        def open_authors(event=None):
            self.switch_tab("settings")
            self._show_settings_section("authors")

        dev_btn = ctk.CTkButton(
            right_box,
            text="pktloss • New G3n",
            font=("Arial", 10, "bold"),
            text_color=MaterialColors.get_color('primary'),
            fg_color="transparent",
            hover_color=MaterialColors.get_color('surface_container_highest'),
            height=24,
            corner_radius=6,
            cursor="hand2",
            command=open_authors
        )
        dev_btn.pack(side="right")

        def on_enter(e):
            footer_frame.configure(fg_color=MaterialColors.get_color('surface_container'))
        def on_leave(e):
            footer_frame.configure(fg_color=MaterialColors.get_color('surface_container_low'))

        for w in (footer_frame, left_box, badge_frame, badge_lbl, title_lbl):
            try:
                w.configure(cursor="hand2")
            except Exception:
                pass
            w.bind("<Enter>", on_enter, add="+")
            w.bind("<Leave>", on_leave, add="+")
            w.bind("<Button-1>", open_authors, add="+")

        for w in (footer_frame, left_box, badge_lbl, title_lbl):
            FooterToolTip(w, lambda mi=is_mi: self._get_footer_tooltip_text(mi))

        setattr(self, f"{prefix}footer_frame", footer_frame)
        setattr(self, f"{prefix}footer_badge", badge_frame)
        setattr(self, f"{prefix}footer_badge_lbl", badge_lbl)
        setattr(self, f"{prefix}footer_title_lbl", title_lbl)
        setattr(self, f"{prefix}footer_dev_btn", dev_btn)

        if is_mi:
            self.mi_desc_label = title_lbl
        else:
            self.desc_label = title_lbl

        return footer_frame

    def _update_footer_colors(self):
        """Обновляет цвета плашек-подвалов при смене темы."""
        for pfx in ('', 'mi_'):
            ff = getattr(self, f"{pfx}footer_frame", None)
            if ff and hasattr(ff, 'winfo_exists') and ff.winfo_exists():
                ff.configure(
                    fg_color=MaterialColors.get_color('surface_container_low'),
                    border_color=MaterialColors.get_color('outline_variant')
                )
            fb = getattr(self, f"{pfx}footer_badge", None)
            if fb and hasattr(fb, 'winfo_exists') and fb.winfo_exists():
                fb.configure(fg_color=MaterialColors.get_color('primary_container'))
            fbl = getattr(self, f"{pfx}footer_badge_lbl", None)
            if fbl and hasattr(fbl, 'winfo_exists') and fbl.winfo_exists():
                fbl.configure(text_color=MaterialColors.get_color('on_primary_container'))
            fd = getattr(self, f"{pfx}footer_dev_btn", None)
            if fd and hasattr(fd, 'winfo_exists') and fd.winfo_exists():
                fd.configure(
                    text_color=MaterialColors.get_color('primary'),
                    hover_color=MaterialColors.get_color('surface_container_highest')
                )

    def _create_unlock_tab(self):
        """Создает вкладку с параметрами подачи заявок"""
        dark_mode = True
        container = self.tab_containers['unlock']

        container.grid_columnconfigure(0, weight=1, uniform='unlock_col')
        container.grid_columnconfigure(1, weight=1, uniform='unlock_col')
        container.grid_rowconfigure(0, weight=1)

        left_column = ctk.CTkFrame(container, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=8)

        right_column = ctk.CTkFrame(container, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=8)
        self.unlock_right_column = right_column

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

        # Контейнер для блока часов Пекинского времени (позволяет сворачивать часы в тонкую кнопку в рамку)
        self.beijing_clock_container = ctk.CTkFrame(card_content, fg_color="transparent")
        self.beijing_clock_container.pack(fill="x", pady=(0, 10))

        initial_bj_time = self.get_beijing_time().strftime("%H:%M:%S")

        # 1. Тонкая кнопка в рамке (отображается в свернутом виде)
        self.beijing_collapsed_btn = ctk.CTkButton(
            self.beijing_clock_container,
            text=f"🕒 {self.translation.tr('beijing_time_title')}: {initial_bj_time}   ▼ {self.translation.tr('beijing_clock_expand')}",
            height=32,
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant'),
            fg_color=MaterialColors.get_color('surface_container_high'),
            hover_color=MaterialColors.get_color('surface_container_highest'),
            text_color=MaterialColors.get_color('primary'),
            font=("Consolas", 13, "bold"),
            command=self.toggle_beijing_clock
        )

        # 2. Развернутая карточка часов (широкая, компактная по высоте, над Режимом Работы)
        self.beijing_timer_card = ctk.CTkFrame(
            self.beijing_clock_container,
            fg_color=MaterialColors.get_color('surface_container_high'),
            corner_radius=12,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )

        beijing_header = ctk.CTkFrame(self.beijing_timer_card, fg_color="transparent")
        beijing_header.pack(fill="x", padx=12, pady=(6, 0))

        self.beijing_timer_title_label = MD3Label(
            beijing_header,
            text=self.translation.tr('beijing_time_title'),
            typography='label_medium',
            text_color=MaterialColors.get_color('primary')
        )
        self.beijing_timer_title_label.pack(side="left", anchor="w")

        self.beijing_collapse_btn = ctk.CTkButton(
            beijing_header,
            text=f"▲ {self.translation.tr('beijing_clock_collapse')}",
            width=85,
            height=22,
            corner_radius=6,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant'),
            fg_color="transparent",
            hover_color=MaterialColors.get_color('surface_container_highest'),
            text_color=MaterialColors.get_color('on_surface_variant'),
            font=("Segoe UI", 10),
            command=self.toggle_beijing_clock
        )
        self.beijing_collapse_btn.pack(side="right", anchor="e")

        self.beijing_clock_label = ctk.CTkLabel(
            self.beijing_timer_card,
            text=initial_bj_time,
            font=("Consolas", 24, "bold"),
            text_color="#FFFFFF"
        )
        self.beijing_clock_label.pack(anchor="center", pady=(0, 1))

        self.beijing_timer_subtext_label = MD3Label(
            self.beijing_timer_card,
            text=self.translation.tr('beijing_submission_hint'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant'),
            justify="center"
        )
        self.beijing_timer_subtext_label.pack(anchor="center", pady=(0, 6))

        # Применяем сохраненное состояние свернутости/развернутости
        self._apply_beijing_clock_state()

        mode_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        mode_frame.pack(fill="x", pady=(0, 10))

        mode_header = ctk.CTkFrame(mode_frame, fg_color="transparent")
        mode_header.pack(fill="x", pady=(0, 4))

        self.mode_label = MD3Label(
            mode_header,
            text=self.translation.tr('mode_label'),
            typography='label_large'
        )
        self.mode_label.pack(side="left", anchor="w")

        # Короткая по высоте, но длинная по ширине панель переключения 3 профилей (без стикеров)
        self.profiles_menu_container = ctk.CTkFrame(
            mode_frame,
            fg_color=MaterialColors.get_color('surface_container'),
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        self.profiles_menu_visible = False
        self._build_profiles_menu()

        # Кнопки режимов: кнопка Профили размещена ВНУТРИ кнопки Авторежим
        self.mode_selector_container = ctk.CTkFrame(
            mode_frame,
            fg_color=MaterialColors.get_color('surface_container_high'),
            corner_radius=12,
            height=42
        )
        self.mode_selector_container.pack(fill="x")
        self.mode_selector_container.grid_columnconfigure((0, 1), weight=1)

        # 1. Левая кнопка: АВТОРЕЖИМ (внутри которой кнопка Профили)
        self.auto_mode_widget = ctk.CTkFrame(
            self.mode_selector_container,
            fg_color=MaterialColors.get_color('primary'),
            corner_radius=10,
            height=36
        )
        self.auto_mode_widget.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
        self.auto_mode_widget.pack_propagate(False)

        self.auto_mode_label = ctk.CTkLabel(
            self.auto_mode_widget,
            text=self.translation.tr('auto_mode_2'),
            font=("Arial", 13, "bold"),
            text_color=MaterialColors.get_color('on_primary')
        )
        self.auto_mode_label.pack(side="left", fill="both", expand=True, padx=(10, 4))
        self.auto_mode_label.bind("<Button-1>", lambda e: self.select_mode_auto())
        self.auto_mode_widget.bind("<Button-1>", lambda e: self.select_mode_auto())

        # Кнопка Профили ВНУТРИ кнопки Авторежим (без стикеров!)
        self.auto_profile_gear_btn = ctk.CTkButton(
            self.auto_mode_widget,
            text=self.translation.tr('profiles_btn'),
            width=70,
            height=26,
            corner_radius=8,
            font=("Arial", 11, "bold"),
            fg_color=MaterialColors.get_color('surface_container_highest'),
            hover_color=MaterialColors.get_color('surface_container'),
            text_color=MaterialColors.get_color('on_surface'),
            border_width=0,
            command=self.toggle_profiles_banner
        )
        self.auto_profile_gear_btn.pack(side="right", padx=(0, 6), pady=4)

        # 2. Правая кнопка: РУЧНОЙ РЕЖИМ
        self.manual_mode_btn = ctk.CTkButton(
            self.mode_selector_container,
            text=self.translation.tr('manual_mode'),
            height=36,
            corner_radius=10,
            font=("Arial", 13, "bold"),
            fg_color='transparent',
            hover_color=MaterialColors.get_color('surface_container_highest'),
            text_color=MaterialColors.get_color('on_surface'),
            command=self.select_mode_manual
        )
        self.manual_mode_btn.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

        class _ModeSegmentedProxy:
            def __init__(self, outer):
                self.outer = outer
            def select(self, val):
                if val == self.outer.translation.tr('manual_mode'):
                    self.outer.select_mode_manual()
                else:
                    self.outer.select_mode_auto()
            def update_values(self, vals):
                if hasattr(self.outer, 'auto_mode_label'):
                    self.outer.auto_mode_label.configure(text=self.outer.translation.tr('auto_mode_2'))
                if hasattr(self.outer, 'manual_mode_btn'):
                    self.outer.manual_mode_btn.configure(text=self.outer.translation.tr('manual_mode'))
                if hasattr(self.outer, 'auto_profile_gear_btn'):
                    self.outer.auto_profile_gear_btn.configure(text=self.outer.translation.tr('profiles_btn'))
            def update_colors(self):
                self.outer._update_mode_buttons_ui()
            def winfo_ismapped(self):
                if hasattr(self.outer, 'mode_selector_container'):
                    return self.outer.mode_selector_container.winfo_ismapped()
                return False

        self.mode_segmented = _ModeSegmentedProxy(self)

        self.manual_time_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        self.manual_time_frame.pack(fill="x", pady=(0, 10))

        manual_time_header = ctk.CTkFrame(self.manual_time_frame, fg_color="transparent")
        manual_time_header.pack(fill="x", pady=(0, 6))

        self.manual_time_label = ctk.CTkLabel(
            manual_time_header,
            text=self.translation.tr('manual_time_label'),
            font=("Arial", 14, "bold"),
            text_color=MaterialColors.get_color('on_surface')
        )
        self.manual_time_label.pack(side="left", anchor="w")

        self.timings_btn = MD3Button(
            manual_time_header,
            text=self.translation.tr('timings_btn'),
            button_type='outlined',
            size='medium',
            height=32,
            command=self.open_timings_dialog
        )
        self.timings_btn.pack(side="right")

        manual_time_input = ctk.CTkFrame(self.manual_time_frame, fg_color="transparent")
        manual_time_input.pack(fill="x", pady=(2, 0))

        self.manual_time_entry = MD3Entry(
            manual_time_input,
            textvariable=self.manual_time_var,
            placeholder_text="58.7, 59.1",
            font=("Consolas", 13, "bold"),
            width=180,
            height=36
        )
        self.manual_time_entry.pack(side="left")

        self.manual_time_hint = ctk.CTkLabel(
            manual_time_input,
            text=self.translation.tr('manual_time_hint'),
            font=("Arial", 12),
            text_color=MaterialColors.get_color('on_surface_variant')
        )
        self.manual_time_hint.pack(side="left", padx=(12, 0))

        cookie_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        cookie_frame.pack(fill="x", pady=(0, 12))
        self.cookie_frame = cookie_frame

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
            command=self.show_login_panel
        )
        self.login_btn.pack(side="right")

        # Плейсхолдер с точками на конце
        self.cookie_entry = MD3Entry(
            cookie_frame,
            textvariable=self.cookie_value,
            placeholder_text=self.translation.tr('cookie_placeholder'),
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
            fg_color='transparent',
            corner_radius=20,
            border_width=0,
            height=40
        )
        self.exit_bg.pack(side="right")

        self.exit_button = MD3Button(
            self.exit_bg,
            text=self.translation.tr('exit'),
            button_type='text',
            size='small',
            height=40,
            command=self.exit_application,
            corner_radius=20,
            fg_color='#202020',
            hover_color='#383838',
            text_color='#FFFFFF',
            border_width=0
        )
        self.exit_button.pack(fill="both", expand=True, padx=0, pady=0)

        desc_frame = self._create_compact_footer(card_content, is_mi=False)
        desc_frame.pack(fill="x", pady=(10, 0))

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
            fg_color='transparent',
            corner_radius=16,
            border_width=0,
            height=32,
            width=98
        )
        self.clear_log_bg.pack(side="left")
        self.clear_log_bg.pack_propagate(False)

        self.clear_log_btn = MD3Button(
            self.clear_log_bg,
            text=self.translation.tr('clear_log_btn'),
            button_type='text',
            size='small',
            height=32,
            command=self.clear_log,
            corner_radius=16,
            font=("Arial", 11),
            fg_color='#202020',
            hover_color='#383838',
            text_color='#FFFFFF',
            border_width=0
        )
        self.clear_log_btn.pack(fill="both", expand=True, padx=0, pady=0)

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

        sidebar = ctk.CTkFrame(
            container,
            fg_color=MaterialColors.get_color('surface_container'),
            width=220,
            corner_radius=16,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        sidebar.pack(side="left", fill="both", padx=(0, 10), pady=8)
        sidebar.pack_propagate(False)

        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(side="right", fill="both", expand=True, padx=(10, 0), pady=8)

        self.settings_sidebar_buttons = {}
        self.settings_content_area = ctk.CTkFrame(content, fg_color="transparent")
        self.settings_content_area.pack(fill="both", expand=True)
        self._settings_panels = {}

        self.sidebar_title_label = ctk.CTkLabel(
            sidebar,
            text=self.translation.tr('sections_menu'),
            font=("Arial", 16, "bold"),
            text_color=MaterialColors.get_color('on_surface')
        )
        self.sidebar_title_label.pack(anchor="w", padx=16, pady=(16, 6))

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

    def _clear_settings_cache(self):
        """Очищает кэшированные панели настроек при смене языка или темы оформления."""
        if hasattr(self, '_settings_panels') and self._settings_panels:
            for p in list(self._settings_panels.values()):
                try:
                    if p.winfo_exists():
                        p.destroy()
                except Exception:
                    pass
            self._settings_panels.clear()

    def _show_settings_section(self, section_name, animated=True):
        prev_section = getattr(self, 'settings_active_section', 'about')
        self.settings_active_section = section_name

        if hasattr(self, '_panel_anim_id') and self._panel_anim_id is not None:
            try:
                self.root.after_cancel(self._panel_anim_id)
            except Exception:
                pass
            self._panel_anim_id = None

        # Подсветка кнопок бокового меню
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

        if not hasattr(self, '_settings_panels'):
            self._settings_panels = {}

        # Ленивое кэширование: создаем панель только если её ещё нет в кэше
        new_panel = self._settings_panels.get(section_name)
        if new_panel is None or not new_panel.winfo_exists():
            new_panel = MD3Card(
                self.settings_content_area,
                fg_color=MaterialColors.get_color('surface_container_low'),
                corner_radius=16,
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant')
            )
            if section_name == 'about':
                self._show_about_section(new_panel)
            elif section_name == 'general':
                self._show_general_section(new_panel)
            elif section_name == 'cookies':
                self._show_cookies_section(new_panel)
            elif section_name == 'trouble':
                self._show_trouble_section(new_panel)
            elif section_name == 'authors':
                self._show_authors_section(new_panel)
            elif section_name == 'settings':
                self._show_settings_inner_section(new_panel)
            else:
                self._show_about_section(new_panel)
            self._settings_panels[section_name] = new_panel

        # Скрываем остальные панели (через place_forget, без разрушения виджетов!)
        for name, p in self._settings_panels.items():
            if name != section_name and p.winfo_exists():
                try:
                    p.place_forget()
                except Exception:
                    pass

        animations_on = animated and bool(self.settings.get('animations_enabled', True)) and (prev_section != section_name)

        if not animations_on:
            new_panel.place(x=0, y=0, relwidth=1.0, relheight=1.0, anchor="nw")
            new_panel.lift()
            return

        # Направленная вертикальная анимация: сверху вниз или снизу вверх
        section_order = ['about', 'general', 'cookies', 'trouble', 'authors', 'settings']
        prev_idx = section_order.index(prev_section) if prev_section in section_order else 0
        new_idx = section_order.index(section_name) if section_name in section_order else 0

        # Если новый раздел выше старого: движение сверху вниз (-32 -> 0)
        # Если новый раздел ниже старого: движение снизу вверх (+32 -> 0)
        start_y = -32 if new_idx < prev_idx else 32

        new_panel.place(x=0, y=start_y, relwidth=1.0, relheight=1.0, anchor="nw")
        new_panel.lift()

        # Анимация по системному таймеру высокой точности (time.perf_counter)
        anim_duration = 0.12  # 120 мс
        anim_start = time.perf_counter()

        def _step():
            if getattr(self, 'settings_active_section', None) != section_name:
                return
            elapsed = time.perf_counter() - anim_start
            progress = min(1.0, elapsed / anim_duration)
            factor = 1.0 - (1.0 - progress) ** 3.0
            cur_y = int(round(start_y * (1.0 - factor)))
            try:
                new_panel.place_configure(y=cur_y)
                if progress < 1.0:
                    self._panel_anim_id = self.root.after(10, _step)
                else:
                    self._finish_panel_transition(new_panel)
            except Exception:
                self._finish_panel_transition(new_panel)

        self._panel_anim_id = self.root.after(10, _step)

    def _finish_panel_transition(self, new_panel):
        self._panel_anim_id = None
        try:
            if new_panel.winfo_exists():
                new_panel.place_configure(y=0)
        except Exception:
            pass

    def _show_about_section(self, panel=None):
        if panel is None:
            self._show_settings_section('about')
            return
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)
        build_about_section(
            scroll, self.translation.language,
            self.open_telegram, self.open_4pda, self.open_github, self.open_site,
            version=CURRENT_VERSION,
            primary_color=MaterialColors.get_color('primary')
        )

    def _show_general_section(self, panel=None):
        if panel is None:
            self._show_settings_section('general')
            return
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)
        build_general_section(scroll, self.translation.language, primary_color=MaterialColors.get_color('primary'))

    def _show_cookies_section(self, panel=None):
        if panel is None:
            self._show_settings_section('cookies')
            return
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)
        build_cookies_section(scroll, self.translation.language, primary_color=MaterialColors.get_color('primary'))

    def _show_trouble_section(self, panel=None):
        if panel is None:
            self._show_settings_section('trouble')
            return
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)
        build_trouble_section(scroll, self.translation.language, self.open_telegram, primary_color=MaterialColors.get_color('primary'))

    def _show_settings_inner_section(self, panel=None):
        if panel is None:
            self._show_settings_section('settings')
            return

        # 1. Фиксированная нижняя панель: версия и кнопка проверки обновлений справа внизу
        bottom_bar = ctk.CTkFrame(panel, fg_color="transparent")
        bottom_bar.pack(side="bottom", fill="x", padx=16, pady=(6, 12))

        bottom_sep = ctk.CTkFrame(panel, fg_color=MaterialColors.get_color('outline_variant'), height=1)
        bottom_sep.pack(side="bottom", fill="x", padx=16, pady=(0, 6))

        update_block = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        update_block.pack(side="right", anchor="e")

        self.version_label = MD3Label(
            update_block,
            text=self.translation.tr('current_version').format(CURRENT_VERSION),
            typography='label_medium'
        )
        self.version_label.pack(side="left", padx=(0, 12))

        self.update_button = MD3Button(
            update_block,
            text=self.translation.tr('check_updates'),
            button_type='outlined',
            size='small',
            height=30,
            command=self.check_updates
        )
        self.update_button.pack(side="left")

        # 2. Скроллируемая область для параметров настроек (занимает всё пространство выше нижней панели)
        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(side="top", fill="both", expand=True, padx=8, pady=(8, 0))

        # Заголовок
        ctk.CTkLabel(
            scroll,
            text=self.translation.tr('settings'),
            font=("Arial", 22, "bold"),
            text_color=MaterialColors.get_color('on_surface')
        ).pack(anchor="w", padx=10, pady=(8, 4))

        language_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        language_frame.pack(fill="x", padx=10, pady=(6, 12))
        MD3Label(language_frame, text=self.translation.tr('language_label'), typography='label_large').pack(anchor="w")
        ctk.CTkOptionMenu(
            language_frame,
            values=['ru', 'en', 'ua', 'id', 'es', 'zh', 'pt'],
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
        separator_color.pack(fill="x", padx=10, pady=(6, 10))

        color_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        color_frame.pack(fill="x", padx=10, pady=10)

        MD3Label(
            color_frame,
            text=self.translation.tr('theme_color_label'),
            typography='label_large'
        ).pack(anchor="w")

        color_controls = ctk.CTkFrame(color_frame, fg_color="transparent")
        color_controls.pack(fill="x", pady=(6, 0))

        self.theme_color_preview = ctk.CTkFrame(
            color_controls,
            width=40,
            height=40,
            corner_radius=10,
            fg_color=MaterialColors.get_color('primary'),
            border_width=1,
            border_color=MaterialColors.get_color('outline')
        )
        self.theme_color_preview.pack(side="left", padx=(0, 10))
        self.theme_color_preview.pack_propagate(False)

        MD3Button(
            color_controls,
            text=self.translation.tr('theme_color_picker'),
            button_type='outlined',
            size='medium',
            command=self.choose_theme_color
        ).pack(side="left")

        separator0 = ctk.CTkFrame(scroll, fg_color=MaterialColors.get_color('outline_variant'), height=1)
        separator0.pack(fill="x", padx=10, pady=(10, 10))

        check_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        check_frame.pack(fill="x", padx=10, pady=10)

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
        anim_row = ctk.CTkFrame(check_frame, fg_color="transparent")
        anim_row.pack(anchor="w", fill="x", pady=8)

        self.animations_checkbox = ctk.CTkCheckBox(
            anim_row,
            text=self.translation.tr('animations_checkbox'),
            variable=self.animations_enabled_var,
            command=self.toggle_animations,
            **checkbox_style
        )
        self.animations_checkbox.pack(side="left")

    def _show_authors_section(self, panel=None):
        if panel is None:
            self._show_settings_section('authors')
            return

        scroll = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=12)

        # 1. Крупная надпись: Разработчики Скрипта
        dev_title = ctk.CTkLabel(
            scroll,
            text=self.translation.tr('authors_developers_title'),
            font=("Arial", 22, "bold"),
            text_color=MaterialColors.get_color('on_surface')
        )
        dev_title.pack(anchor="w", padx=10, pady=(8, 4))

        # Ники: pktloss, New G3n
        devs_names = ctk.CTkLabel(
            scroll,
            text="pktloss, New G3n",
            font=("Arial", 16, "bold"),
            text_color=MaterialColors.get_color('primary')
        )
        devs_names.pack(anchor="w", padx=10, pady=(0, 16))

        # 2. Крупная надпись: Разработчик PC и CLI версии скрипта
        pc_cli_title = ctk.CTkLabel(
            scroll,
            text=self.translation.tr('authors_pc_cli_dev'),
            font=("Arial", 18, "bold"),
            text_color=MaterialColors.get_color('on_surface')
        )
        pc_cli_title.pack(anchor="w", padx=10, pady=(4, 4))

        # Ник: New G3n
        pc_cli_name = ctk.CTkLabel(
            scroll,
            text="New G3n",
            font=("Arial", 15, "bold"),
            text_color=MaterialColors.get_color('primary')
        )
        pc_cli_name.pack(anchor="w", padx=10, pady=(0, 16))

        # 3. Надпись: Разработчик Сайта скрипта и Android версии
        web_android_title = ctk.CTkLabel(
            scroll,
            text=self.translation.tr('authors_web_android_dev'),
            font=("Arial", 18, "bold"),
            text_color=MaterialColors.get_color('on_surface')
        )
        web_android_title.pack(anchor="w", padx=10, pady=(4, 4))

        # Ник: pktloss
        web_android_name = ctk.CTkLabel(
            scroll,
            text="pktloss",
            font=("Arial", 15, "bold"),
            text_color=MaterialColors.get_color('primary')
        )
        web_android_name.pack(anchor="w", padx=10, pady=(0, 16))

        # 4. Надпись не таким уже большим шрифтом: Скрипт написан на основе скрипта
        base_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        base_frame.pack(anchor="w", padx=10, pady=(4, 16))

        base_title = ctk.CTkLabel(
            base_frame,
            text=self.translation.tr('authors_base_script'),
            font=("Arial", 13),
            text_color=MaterialColors.get_color('on_surface_variant')
        )
        base_title.pack(side="left", padx=(0, 6))

        base_name = ctk.CTkLabel(
            base_frame,
            text="Vierta",
            font=("Arial", 13, "bold"),
            text_color=MaterialColors.get_color('primary')
        )
        base_name.pack(side="left")

        # Разделитель
        sep1 = ctk.CTkFrame(scroll, fg_color=MaterialColors.get_color('outline_variant'), height=1)
        sep1.pack(fill="x", padx=10, pady=(4, 16))

        # 5. Текст: Ссылки на Соц Сети
        social_title = ctk.CTkLabel(
            scroll,
            text=self.translation.tr('authors_social_links'),
            font=("Arial", 16, "bold"),
            text_color=MaterialColors.get_color('on_surface')
        )
        social_title.pack(anchor="w", padx=10, pady=(0, 10))

        # В строчку такие же кнопки как и в главном меню с гитхабом сайтом 4пда и тд
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
            command=self.open_telegram
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
            command=self.open_4pda
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
            command=self.open_github
        )
        gh_btn.pack(side="left", padx=(0, 8))

        st_btn = ctk.CTkButton(
            social_row,
            text=self._get_site_button_text(),
            width=118,
            height=32,
            corner_radius=10,
            font=("Arial", 12, "bold"),
            fg_color=MaterialColors.get_color('surface_container_high'),
            hover_color=MaterialColors.get_color('surface_container_highest'),
            text_color=MaterialColors.get_color('on_surface'),
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant'),
            command=self.open_site
        )
        st_btn.pack(side="left")

        # Разделитель
        sep2 = ctk.CTkFrame(scroll, fg_color=MaterialColors.get_color('outline_variant'), height=1)
        sep2.pack(fill="x", padx=10, pady=(4, 16))

        # 6. Надпись: Пожертвовать на разработку
        donate_title = ctk.CTkLabel(
            scroll,
            text=self.translation.tr('authors_donate_title'),
            font=("Arial", 16, "bold"),
            text_color=MaterialColors.get_color('on_surface')
        )
        donate_title.pack(anchor="w", padx=10, pady=(0, 10))

        # Кнопка DonationAlerts: оранжевая, кликабельная, перекидывает на https://dalink.to/asinsideout
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

        # 7. Криптокошелек (копируемый текст и кнопка копирования)
        crypto_frame = ctk.CTkFrame(
            scroll,
            fg_color=MaterialColors.get_color('surface_container_high'),
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        crypto_frame.pack(fill="x", padx=10, pady=(0, 16))

        crypto_header = ctk.CTkFrame(crypto_frame, fg_color="transparent")
        crypto_header.pack(fill="x", padx=14, pady=(10, 6))

        crypto_net = ctk.CTkLabel(
            crypto_header,
            text=self.translation.tr('authors_crypto_network'),
            font=("Arial", 12, "bold"),
            text_color=MaterialColors.get_color('primary')
        )
        crypto_net.pack(side="left")

        wallet_val = "UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG"

        def copy_wallet():
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(wallet_val)
                self.root.update()
                copy_btn.configure(text=self.translation.tr('address_copied'), fg_color="#10B981")
                self.root.after(2000, lambda: copy_btn.configure(text=self.translation.tr('copy_address_btn'), fg_color=MaterialColors.get_color('surface_container_highest')))
            except Exception:
                pass

        copy_btn = ctk.CTkButton(
            crypto_header,
            text=self.translation.tr('copy_address_btn'),
            width=100,
            height=26,
            corner_radius=8,
            font=("Arial", 11, "bold"),
            fg_color=MaterialColors.get_color('surface_container_highest'),
            hover_color=MaterialColors.get_color('primary'),
            text_color=MaterialColors.get_color('on_surface'),
            command=copy_wallet
        )
        copy_btn.pack(side="right")

        crypto_entry = ctk.CTkEntry(
            crypto_frame,
            font=("Consolas", 12),
            height=32,
            corner_radius=8,
            fg_color=MaterialColors.get_color('surface_container_lowest'),
            text_color=MaterialColors.get_color('on_surface'),
            border_color=MaterialColors.get_color('outline'),
            border_width=1
        )
        crypto_entry.insert(0, wallet_val)
        crypto_entry.configure(state="readonly")
        crypto_entry.pack(fill="x", padx=14, pady=(0, 10))

    def choose_theme_color(self):
        """Открывает встроенный диалог выбора цвета."""
        try:
            initial = MaterialColors.get_color('primary')
            if CustomColorPickerDialog is not None:
                def _on_accepted(chosen_color):
                    self._set_custom_theme_color(chosen_color)
                    if hasattr(self, 'theme_color_preview') and self.theme_color_preview is not None and self.theme_color_preview.winfo_exists():
                        self.theme_color_preview.configure(fg_color=chosen_color)

                CustomColorPickerDialog(
                    self.root,
                    initial_color=initial,
                    on_accept=_on_accepted,
                    translation=self.translation
                )
            else:
                result = colorchooser.askcolor(
                    color=initial,
                    title=self.translation.tr('theme_color_picker')
                )
                if result and result[1]:
                    chosen = result[1].upper()
                    self._set_custom_theme_color(chosen)
                    if hasattr(self, 'theme_color_preview') and self.theme_color_preview is not None and self.theme_color_preview.winfo_exists():
                        self.theme_color_preview.configure(fg_color=chosen)
        except Exception as e:
            print(f"Ошибка выбора цвета: {e}")

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

        for mod_name in ('res.theme', 'theme'):
            try:
                mod = sys.modules.get(mod_name)
                if mod and hasattr(mod, 'MaterialColors'):
                    mod.MaterialColors.set_accent_color(color, colors['on_primary'], colors['primary_container'], colors['secondary'])
            except Exception:
                pass

        for mod_name in ('res.settings_ui', 'settings_ui'):
            try:
                mod = sys.modules.get(mod_name)
                if mod and hasattr(mod, 'set_primary_color'):
                    mod.set_primary_color(color)
            except Exception:
                pass

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

        for mod_name in ('res.theme', 'theme'):
            try:
                mod = sys.modules.get(mod_name)
                if mod and hasattr(mod, 'MaterialColors'):
                    mod.MaterialColors.set_accent_color(primary, on_primary, primary_container, secondary)
            except Exception:
                pass

        for mod_name in ('res.settings_ui', 'settings_ui'):
            try:
                mod = sys.modules.get(mod_name)
                if mod and hasattr(mod, 'set_primary_color'):
                    mod.set_primary_color(primary)
            except Exception:
                pass

        self.settings['custom_primary_color'] = color
        self.config['custom_primary_color'] = color
        save_config(self.config)

        self.update_md3_colors()
        try:
            self._clear_settings_cache()
            self._show_settings_section(self.settings_active_section, animated=False)
        except Exception:
            pass

    def toggle_animations(self):
        try:
            val = bool(self.animations_enabled_var.get())
            self.settings['animations_enabled'] = val
            self.config['animations_enabled'] = val
            save_config(self.config)
        except Exception as e:
            print(f"Ошибка сохранения состояния анимаций: {e}")

    def check_updates(self):
        if not hasattr(self, 'update_button') or self.update_button is None:
            return

        try:
            if hasattr(self.update_button, 'winfo_exists') and not self.update_button.winfo_exists():
                return
            self.update_button.configure(
                state="disabled",
                text=self.translation.tr('update_checking')
            )
        except Exception:
            return

        def worker():
            try:
                latest_version, message = UpdateChecker.check_for_updates(lang=self.translation.language)
            except Exception as e:
                latest_version, message = None, f"update_error: {e}"

            def finish():
                try:
                    if hasattr(self, 'update_button') and self.update_button is not None:
                        if hasattr(self.update_button, 'winfo_exists') and self.update_button.winfo_exists():
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
                                subprocess.Popen([sys.executable, autoupdate_script, "--force", f"--lang={self.translation.language}"])
                                self.root.destroy()
                                return
                            download_url = get_update_download_url(self.translation.language)
                            webbrowser.open(download_url, new=2)
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

        if hasattr(self, 'thread_coordinator'):
            self.thread_coordinator.submit_bg_task(worker)
        else:
            threading.Thread(target=worker, daemon=True).start()

    def _create_mi_unlock_tab(self):
        """Создает вкладку с полноценным Mi Unlock функционалом с интерфейсом как у Подачи заявок"""
        trans = self.translation
        dark_mode = True
        container = self.tab_containers['mi_unlock']

        container.grid_columnconfigure(0, weight=1, uniform='mi_col')
        container.grid_columnconfigure(1, weight=1, uniform='mi_col')
        container.grid_rowconfigure(0, weight=1)

        # Двухколонный layout как в unlock tab
        left_column = ctk.CTkFrame(container, fg_color="transparent")
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=8)

        right_column = ctk.CTkFrame(container, fg_color="transparent")
        right_column.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=8)

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

        process_state = {'process': None, 'closed': False, 'status_label': None}
        self.mi_status_label_var = ctk.StringVar(value=trans.tr('mi_unlock_checking_python'))
        status_label_var = self.mi_status_label_var
        self.mi_python_label_var = ctk.StringVar(value=trans.tr('mi_unlock_python_not_found'))
        python_label_var = self.mi_python_label_var
        self.mi_package_label_var = ctk.StringVar(value=trans.tr('mi_unlock_package_not_installed'))
        package_label_var = self.mi_package_label_var

        # Кнопки действия
        button_frame = ctk.CTkFrame(card_content, fg_color="transparent")
        button_frame.pack(fill="x")

        def start_mi_unlock():
            start_mi_btn.configure(state="disabled")
            if hasattr(self, 'thread_coordinator'):
                self.thread_coordinator.submit_bg_task(install_and_run_miunlock)
            else:
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
            fg_color='transparent',
            corner_radius=20,
            border_width=0,
            height=40
        )
        exit_bg.pack(side="right")

        self.mi_close_btn = MD3Button(
            exit_bg,
            text=trans.tr('exit'),
            button_type='text',
            size='small',
            height=40,
            command=close_mi_unlock,
            corner_radius=20,
            fg_color='#202020',
            hover_color='#383838',
            text_color='#FFFFFF',
            border_width=0
        )
        self.mi_close_btn.pack(fill="both", expand=True, padx=0, pady=0)

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
            fg_color='transparent',
            corner_radius=16,
            border_width=0,
            height=32,
            width=98
        )
        clear_log_bg.pack(side="left")
        clear_log_bg.pack_propagate(False)

        def clear_log_content():
            output_text.configure(state="normal")
            output_text.delete("1.0", "end")
            output_text.configure(state="disabled")

        self.mi_clear_log_btn = MD3Button(
            clear_log_bg,
            text=trans.tr('clear_log_btn'),
            button_type='text',
            size='small',
            height=32,
            command=clear_log_content,
            corner_radius=16,
            font=("Arial", 11),
            fg_color='#202020',
            hover_color='#383838',
            text_color='#FFFFFF',
            border_width=0
        )
        self.mi_clear_log_btn.pack(fill="both", expand=True, padx=0, pady=0)

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
        input_card.pack(fill="x", padx=0, pady=(0, 14), before=button_frame)

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

        mi_desc_frame = self._create_compact_footer(card_content, is_mi=True)
        mi_desc_frame.pack(fill="x", pady=(10, 0))

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
            def restore_buttons():
                try:
                    if hasattr(self, 'start_mi_btn') and self.start_mi_btn.winfo_exists():
                        self.start_mi_btn.configure(state="normal")
                    if hasattr(self, 'mi_close_btn') and self.mi_close_btn.winfo_exists():
                        self.mi_close_btn.configure(state="normal")
                except Exception:
                    pass

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
                                err_str = str(e)
                                container.after(0,
                                                lambda err=err_str: log_message(trans.tr('mi_unlock_read_error').format(err), "red"))
                            except:
                                pass

                read_output()
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
                        err_str = str(e)
                        container.after(0, lambda err=err_str: update_status(trans.tr('mi_unlock_error').format(err), "red"))
                        container.after(0, lambda err=err_str: log_message(trans.tr('mi_unlock_critical_error').format(err), "red"))
                    except:
                        pass
            finally:
                try:
                    container.after(0, restore_buttons)
                except Exception:
                    pass

    def _create_hyperos1_bypass_tab(self):
        """Создает вкладку-заглушку HyperOS 1 Bypass"""
        dark_mode = True
        container = self.tab_containers['hyperos1_bypass']
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

        bypass_card = MD3Card(container, elevation=2)
        bypass_card.pack(fill="both", expand=True, padx=4, pady=8)
        bypass_card.configure(corner_radius=18)
        self.bypass_card = bypass_card

        card_header = ctk.CTkFrame(bypass_card, fg_color="transparent", height=46)
        card_header.pack(fill="x", padx=18, pady=(12, 0))
        card_header.pack_propagate(False)

        header_label_bg = ctk.CTkFrame(
            card_header,
            fg_color='#202020',
            corner_radius=12,
            border_width=0,
            height=36
        )
        header_label_bg.pack(side="left")

        self.bypass_header_label = MD3Label(
            header_label_bg,
            text=f"⚡ {self.translation.tr('tab_hyperos1_bypass')}",
            typography='title_large',
            text_color='#FFFFFF'
        )
        self.bypass_header_label.pack(side="left", padx=12, pady=2)

        content_box = ctk.CTkFrame(bypass_card, fg_color="transparent")
        content_box.pack(expand=True, fill="both", padx=24, pady=24)

        center_panel = ctk.CTkFrame(
            content_box,
            fg_color=MaterialColors.get_color('surface_container_low'),
            corner_radius=18,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant')
        )
        center_panel.pack(anchor="center", expand=True, padx=20, pady=20)
        self.bypass_center_panel = center_panel

        icon_lbl = ctk.CTkLabel(
            center_panel,
            text="⚡",
            font=("Segoe UI", 52),
            text_color=MaterialColors.get_color('primary')
        )
        icon_lbl.pack(pady=(28, 6), padx=40)
        self.bypass_icon_lbl = icon_lbl

        self.bypass_title_label = MD3Label(
            center_panel,
            text=self.translation.tr('hyperos1_bypass_title'),
            typography='headline_medium',
            text_color=MaterialColors.get_color('on_surface')
        )
        self.bypass_title_label.pack(pady=(0, 8), padx=40)

        self.bypass_desc_label = MD3Label(
            center_panel,
            text=self.translation.tr('hyperos1_bypass_desc'),
            typography='body_large',
            text_color=MaterialColors.get_color('on_surface_variant'),
            justify="center"
        )
        self.bypass_desc_label.pack(pady=(0, 24), padx=40)

        self.bypass_return_btn = MD3Button(
            center_panel,
            text=self.translation.tr('hyperos1_bypass_return_btn'),
            button_type='filled',
            size='medium',
            height=38,
            command=lambda: self.switch_tab("unlock")
        )
        self.bypass_return_btn.pack(pady=(0, 28), padx=40)

    def switch_tab(self, tab_name, *args, **kwargs):
        """Переключает между вкладками с направленной Material 3 анимацией скольжения."""
        prev_tab = getattr(self, 'current_tab', None)
        if prev_tab == tab_name:
            return
        if tab_name not in self.tab_containers:
            return

        # Отменяем текущую анимацию, если пользователь переключает вкладки очень быстро
        if hasattr(self, '_tab_anim_id') and self._tab_anim_id is not None:
            try:
                self.root.after_cancel(self._tab_anim_id)
            except Exception:
                pass
            self._tab_anim_id = None

        tab_order = ['settings', 'unlock', 'hyperos1_bypass', 'mi_unlock']
        prev_idx = tab_order.index(prev_tab) if prev_tab in tab_order else 0
        new_idx = tab_order.index(tab_name) if tab_name in tab_order else 0

        # Анимация по сторонам:
        # Если вкладка находится левее (например, с Mi Unlock на Unlock или Settings):
        # анимация справа налево (start_x = +42 -> 0)
        # Если вкладка находится правее (например, с Settings на Unlock):
        # анимация слева направо (start_x = -42 -> 0)
        start_x = 42 if new_idx < prev_idx else -42
        self.current_tab = tab_name

        # Мгновенно обновляем подсветку кнопок для максимальной отзывчивости
        for btn_name, btn in self.tab_buttons.items():
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

        new_container = self.tab_containers[tab_name]
        animations_on = bool(self.settings.get('animations_enabled', True)) and (prev_tab is not None)

        # Скрываем все остальные вкладки СРАЗУ, чтобы под анимацией было чистое пустое поле без наложения
        for name, c in self.tab_containers.items():
            if name != tab_name:
                try:
                    c.place_forget()
                except Exception:
                    pass

        if not animations_on:
            new_container.place(x=0, y=0, relwidth=1.0, relheight=1.0, anchor="nw")
            new_container.lift()
            return

        # Плавное появление над пустым полем без наложения на старую страницу
        new_container.place(x=start_x, y=0, relwidth=1.0, relheight=1.0, anchor="nw")
        new_container.lift()

        # Анимация по системному таймеру высокой точности (time.perf_counter)
        anim_duration = 0.12  # 120 мс фиксированная длительность
        anim_start = time.perf_counter()

        def _step():
            if getattr(self, 'current_tab', None) != tab_name:
                return
            elapsed = time.perf_counter() - anim_start
            progress = min(1.0, elapsed / anim_duration)
            factor = 1.0 - (1.0 - progress) ** 3.0  # Плавная деселерация
            cur_x = int(round(start_x * (1.0 - factor)))
            try:
                new_container.place_configure(x=cur_x)
                if progress < 1.0:
                    self._tab_anim_id = self.root.after(10, _step)
                else:
                    self._finish_tab_transition(new_container, tab_name)
            except Exception:
                self._finish_tab_transition(new_container, tab_name)

        self._tab_anim_id = self.root.after(10, _step)

    def _finish_tab_transition(self, new_container, tab_name):
        self._tab_anim_id = None
        if getattr(self, 'current_tab', None) != tab_name:
            return
        try:
            if new_container.winfo_exists():
                new_container.place_configure(x=0)
        except Exception:
            pass
        for name, c in self.tab_containers.items():
            if name != tab_name:
                try:
                    c.place_forget()
                except Exception:
                    pass

    def _animate_in_card(self, widget, step=0):
        """Плавное появление карточки в правой колонке с мягким скольжением вверх."""
        try:
            if not widget.winfo_exists():
                return
        except Exception:
            return

        if hasattr(self, '_card_anim_id') and self._card_anim_id is not None:
            try:
                self.root.after_cancel(self._card_anim_id)
            except Exception:
                pass
            self._card_anim_id = None

        if not self.settings.get('animations_enabled', True):
            try:
                widget.place_forget()
                widget.pack(fill="both", expand=True)
            except Exception:
                pass
            return

        start_y = 16
        anim_duration = 0.14  # 140 мс
        anim_start = time.perf_counter()

        try:
            widget.pack_forget()
            widget.place(x=0, y=start_y, relwidth=1.0, relheight=1.0, anchor="nw")
        except Exception:
            try:
                widget.pack(fill="both", expand=True)
            except Exception:
                pass
            return

        def _step():
            elapsed = time.perf_counter() - anim_start
            progress = min(1.0, elapsed / anim_duration)
            factor = 1.0 - (1.0 - progress) ** 3.0
            current_y = int(round(start_y * (1.0 - factor)))
            try:
                widget.place_configure(y=current_y)
                if progress < 1.0:
                    self._card_anim_id = self.root.after(10, _step)
                else:
                    self._card_anim_id = None
                    widget.place_forget()
                    widget.pack(fill="both", expand=True)
            except Exception:
                try:
                    widget.place_forget()
                    widget.pack(fill="both", expand=True)
                except Exception:
                    pass
                self._card_anim_id = None

        self._card_anim_id = self.root.after(10, _step)

    def show_login_panel(self):
        """Отображает панель авторизации в правой колонке вместо лога с анимацией."""
        try:
            if not hasattr(self, 'unlock_right_column') or self.unlock_right_column is None:
                return

            if hasattr(self, 'login_panel') and self.login_panel is not None and self.login_panel.winfo_exists():
                if self.login_panel.winfo_ismapped():
                    self.hide_login_panel()
                    return
                self.login_panel.reset()
            else:
                self.login_panel = XiaomiAuthPanel(
                    self.unlock_right_column,
                    translation=self.translation,
                    config=self.config,
                    on_close=self.hide_login_panel,
                    on_success=self.on_login_success,
                    app=self
                )

            if hasattr(self, 'log_card') and self.log_card.winfo_exists():
                self.log_card.pack_forget()
                self.log_card.place_forget()

            self._animate_in_card(self.login_panel)
        except Exception as e:
            self.log_message(f"Error displaying login panel: {e}", color='red')

    def hide_login_panel(self):
        """Скрывает панель авторизации и возвращает лог выполнения с анимацией."""
        try:
            if hasattr(self, 'login_panel') and self.login_panel is not None and self.login_panel.winfo_exists():
                self.login_panel.stop()
                self.login_panel.pack_forget()
                self.login_panel.place_forget()
            if hasattr(self, 'log_card') and self.log_card is not None and self.log_card.winfo_exists():
                self._animate_in_card(self.log_card)
        except Exception as e:
            print(f"Error hiding login panel: {e}")

    def on_login_success(self, token):
        """Обработчик успешного входа: сохраняет токен и возвращает лог."""
        try:
            if token:
                self.cookie_value.set(token)
                self.auto_save_cookie()
                masked_token = token[:8] + "..." + token[-6:] if len(token) > 14 else "***"
                self.log_message(f"{self.translation.tr('login_success')} (Token: {masked_token})", color='green')
                self.root.after(700, self.hide_login_panel)
        except Exception as e:
            self.log_message(f"Error processing login token: {e}", color='red')

    def _build_profiles_menu(self):
        if not hasattr(self, 'profiles_menu_container') or self.profiles_menu_container is None:
            return
        for w in self.profiles_menu_container.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass

        inner = ctk.CTkFrame(self.profiles_menu_container, fg_color="transparent")
        inner.pack(fill="x", padx=6, pady=4)

        self.profile_buttons = {}
        curr_prof = getattr(self, 'current_timing_profile', 'europe')

        profiles_data = [
            ('europe', self.translation.tr('profile_europe')),
            ('asia', self.translation.tr('profile_asia')),
            ('usa_africa', self.translation.tr('profile_usa_africa')),
        ]

        for p_key, p_label in profiles_data:
            is_active = (p_key == curr_prof)
            btn = ctk.CTkButton(
                inner,
                text=p_label,
                height=28,
                corner_radius=8,
                font=("Arial", 11, "bold" if is_active else "normal"),
                fg_color=MaterialColors.get_color('primary') if is_active else MaterialColors.get_color('surface_container_high'),
                hover_color=MaterialColors.get_color('primary_container') if is_active else MaterialColors.get_color('surface_container_highest'),
                text_color=MaterialColors.get_color('on_primary') if is_active else MaterialColors.get_color('on_surface'),
                command=lambda pk=p_key: self.set_timing_profile(pk)
            )
            btn.pack(side="left", fill="x", expand=True, padx=3)
            self.profile_buttons[p_key] = btn

    def toggle_profiles_banner(self):
        if getattr(self, 'profiles_menu_visible', False):
            if hasattr(self, 'profiles_menu_container') and self.profiles_menu_container is not None:
                self.profiles_menu_container.pack_forget()
            self.profiles_menu_visible = False
            if hasattr(self, 'auto_profile_gear_btn') and self.auto_profile_gear_btn is not None:
                self.auto_profile_gear_btn.configure(fg_color=MaterialColors.get_color('surface_container_highest'))
        else:
            if hasattr(self, 'profiles_menu_container') and self.profiles_menu_container is not None:
                self._build_profiles_menu()
                target_before = getattr(self, 'mode_selector_container', None)
                if target_before and target_before.winfo_ismapped():
                    self.profiles_menu_container.pack(fill="x", pady=(4, 6), before=target_before)
                else:
                    self.profiles_menu_container.pack(fill="x", pady=(4, 6))
                self.profiles_menu_visible = True
            if hasattr(self, 'auto_profile_gear_btn') and self.auto_profile_gear_btn is not None:
                self.auto_profile_gear_btn.configure(fg_color=MaterialColors.get_color('primary_container'))

    def select_mode_auto(self):
        self.mode_var.set(self.translation.tr('auto_mode_2'))
        self.toggle_mode(self.translation.tr('auto_mode_2'))
        self._update_mode_buttons_ui()

    def select_mode_manual(self):
        self.mode_var.set(self.translation.tr('manual_mode'))
        self.toggle_mode(self.translation.tr('manual_mode'))
        if getattr(self, 'profiles_menu_visible', False):
            self.toggle_profiles_banner()
        self._update_mode_buttons_ui()

    def _update_mode_buttons_ui(self):
        is_auto = (self.auto_mode_index != 0)
        if hasattr(self, 'auto_mode_widget') and self.auto_mode_widget is not None:
            if is_auto:
                self.auto_mode_widget.configure(fg_color=MaterialColors.get_color('primary'))
                if hasattr(self, 'auto_mode_label') and self.auto_mode_label is not None:
                    self.auto_mode_label.configure(text_color=MaterialColors.get_color('on_primary'))
                if hasattr(self, 'auto_profile_gear_btn') and self.auto_profile_gear_btn is not None:
                    try:
                        if not self.auto_profile_gear_btn.winfo_ismapped():
                            self.auto_profile_gear_btn.pack(side="right", padx=(0, 6), pady=4)
                        self.auto_profile_gear_btn.configure(
                            fg_color=MaterialColors.get_color('surface_container_highest'),
                            text_color=MaterialColors.get_color('on_surface')
                        )
                    except Exception:
                        pass
                if hasattr(self, 'manual_mode_btn') and self.manual_mode_btn is not None:
                    self.manual_mode_btn.configure(
                        fg_color='transparent',
                        text_color=MaterialColors.get_color('on_surface')
                    )
            else:
                self.auto_mode_widget.configure(fg_color='transparent')
                if hasattr(self, 'auto_mode_label') and self.auto_mode_label is not None:
                    self.auto_mode_label.configure(text_color=MaterialColors.get_color('on_surface'))
                if hasattr(self, 'auto_profile_gear_btn') and self.auto_profile_gear_btn is not None:
                    try:
                        self.auto_profile_gear_btn.pack_forget()
                    except Exception:
                        pass
                if hasattr(self, 'manual_mode_btn') and self.manual_mode_btn is not None:
                    self.manual_mode_btn.configure(
                        fg_color=MaterialColors.get_color('primary'),
                        text_color=MaterialColors.get_color('on_primary')
                    )

    def set_timing_profile(self, profile_key):
        if profile_key not in TIMING_PROFILES:
            return
        self.current_timing_profile = profile_key
        prof_info = TIMING_PROFILES[profile_key]
        self.selected_timings = list(prof_info['timings'])
        self.settings['timing_profile'] = profile_key
        self.settings['auto_timings'] = self.selected_timings
        self.config['timing_profile'] = profile_key
        self.config['auto_timings'] = self.selected_timings

        if hasattr(self, 'manual_time_var'):
            self.manual_time_var.set(", ".join(f"{t:.3f}" for t in self.selected_timings))

        if hasattr(self, 'profile_buttons'):
            for pk, btn in self.profile_buttons.items():
                is_active = (pk == profile_key)
                try:
                    btn.configure(
                        font=("Arial", 11, "bold" if is_active else "normal"),
                        fg_color=MaterialColors.get_color('primary') if is_active else MaterialColors.get_color('surface_container_high'),
                        text_color=MaterialColors.get_color('on_primary') if is_active else MaterialColors.get_color('on_surface')
                    )
                except Exception:
                    pass

        if self.translation.language == 'ru':
            prof_name = prof_info.get('name_ru', prof_info['name_en'])
        elif self.translation.language in ('ua', 'uk'):
            prof_name = prof_info.get('name_ua', prof_info.get('name_uk', prof_info['name_en']))
        else:
            prof_name = prof_info['name_en']
        timings_str = ", ".join(f"{t:.3f}s" for t in self.selected_timings)
        self.log_message(f"[{self.translation.tr('profiles_title')}] {prof_name}: {timings_str}", color="blue")
        self.save_settings()

    def open_timings_dialog(self):
        try:
            dialog = TimingSettingsDialog(self.root, self)
            self.root.wait_window(dialog)
        except Exception as e:
            self.log_message(f"Error opening timing settings dialog: {e}", color='red')

    def check_eligibility(self):
        token = self.cookie_value.get().strip()
        if not token:
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('cookie_error'))
            return

        if getattr(self, '_checking_eligibility', False):
            return
        self._checking_eligibility = True

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
                self._checking_eligibility = False
                if hasattr(self, 'check_eligibility_btn') and self.check_eligibility_btn is not None:
                    self.root.after(0, lambda: self.check_eligibility_btn.configure(state="normal"))

        if hasattr(self, 'thread_coordinator'):
            self.thread_coordinator.submit_bg_task(worker)
        else:
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
            self.auto_mode_index = 1

        if hasattr(self, 'manual_time_frame') and self.manual_time_frame is not None:
            if selected_mode == self.translation.tr('manual_mode'):
                if hasattr(self, 'cookie_frame') and self.cookie_frame is not None:
                    self.manual_time_frame.pack(fill="x", pady=(0, 10), before=self.cookie_frame)
                else:
                    self.manual_time_frame.pack(fill="x", pady=(0, 10))
                self.ping_var.set(self.translation.tr('ping_not_measured_manual'))
                self.desc_label.configure(text=self.translation.tr('desc_manual'))
            else:
                self.manual_time_frame.pack_forget()
                self.ping_var.set(self.translation.tr('ping'))
                self.desc_label.configure(text=self.translation.tr('desc'))

    def _get_site_button_text(self):
        # Название кнопки берём из общего словаря переводов.
        # Это позволяет ей корректно меняться вместе с остальным интерфейсом.
        return self.translation.tr('social_site_script')

    def update_ui_text(self):
        def safe_config(widget, **kwargs):
            if widget is not None:
                try:
                    if hasattr(widget, 'winfo_exists') and widget.winfo_exists():
                        widget.configure(**kwargs)
                except Exception:
                    pass

        try:
            self.root.title(self.translation.tr('title'))
        except Exception:
            pass

        safe_config(getattr(self, 'update_button', None), text=self.translation.tr('check_updates'))
        safe_config(getattr(self, 'version_label', None), text=self.translation.tr('current_version').format(CURRENT_VERSION))
        safe_config(getattr(self, 'title_label', None), text=self.translation.tr('main_title'))
        if hasattr(self, 'sub_label') and self.sub_label:
            cur_domain = "miunlocktool.ru" if self.translation.language == "ru" else "miunlock.su"
            lang_display = Translation.get_display_name(self.translation.language)
            safe_config(self.sub_label, text=f"{lang_display} • {cur_domain}")
        safe_config(getattr(self, 'beijing_timer_title_label', None), text=self.translation.tr('beijing_time_title'))
        safe_config(getattr(self, 'beijing_timer_subtext_label', None), text=self.translation.tr('beijing_submission_hint'))
        safe_config(getattr(self, 'beijing_collapse_btn', None), text=f"▲ {self.translation.tr('beijing_clock_collapse')}")
        if hasattr(self, '_apply_beijing_clock_state'):
            self._apply_beijing_clock_state()
        if hasattr(self, 'header_region_label'):
            try:
                user_reg = self.settings.get('region', detect_user_region())
                safe_config(
                    self.header_region_label,
                    text=self.translation.tr('header_region').format(user_reg)
                )
            except Exception:
                pass

        # Обновляем текст кнопок вкладок
        if hasattr(self, 'tab_buttons') and self.tab_buttons:
            for key in ('unlock', 'settings', 'hyperos1_bypass', 'mi_unlock'):
                if key in self.tab_buttons:
                    safe_config(self.tab_buttons[key], text=self.translation.tr(f'tab_{key}'))

        safe_config(getattr(self, 'bypass_header_label', None), text=f"⚡ {self.translation.tr('tab_hyperos1_bypass')}")
        safe_config(getattr(self, 'bypass_title_label', None), text=self.translation.tr('hyperos1_bypass_title'))
        safe_config(getattr(self, 'bypass_desc_label', None), text=self.translation.tr('hyperos1_bypass_desc'))
        safe_config(getattr(self, 'bypass_return_btn', None), text=self.translation.tr('hyperos1_bypass_return_btn'))

        if hasattr(self, 'settings_sidebar_buttons') and self.settings_sidebar_buttons:
            section_titles = {
                'about': 'about_title',
                'general': 'general_title',
                'cookies': 'cookies_title',
                'trouble': 'trouble_title',
                'authors': 'authors_title',
                'settings': 'settings'
            }
            for section_key, button in self.settings_sidebar_buttons.items():
                if section_key in section_titles:
                    safe_config(button, text=self.translation.tr(section_titles[section_key]))
            safe_config(getattr(self, 'sidebar_title_label', None), text=self.translation.tr('sections_menu'))
            try:
                active_sec = getattr(self, 'settings_active_section', 'about')
                self._clear_settings_cache()
                self._show_settings_section(active_sec, animated=False)
            except Exception as e:
                print(f"Error re-showing settings section on language change: {e}")

        safe_config(getattr(self, 'auto_profile_gear_btn', None), text=self.translation.tr('profiles_btn'))
        if hasattr(self, 'profile_buttons') and self.profile_buttons:
            try:
                self._build_profiles_menu()
            except Exception:
                pass

        safe_config(getattr(self, 'desc_label', None), text=self.translation.tr('desc'))
        safe_config(getattr(self, 'mi_desc_label', None), text=self.translation.tr('mi_unlock_desc'))

        # Исправлено: перевод заголовка вкладки "Подача Заявок"
        safe_config(getattr(self, 'params_label', None), text=self.translation.tr('tab_unlock'))
        safe_config(getattr(self, 'mode_label', None), text=self.translation.tr('mode_label'))
        # Обновляем сегментированную кнопку - только 2 режима
        if getattr(self, 'mode_segmented', None):
            try:
                new_values = [self.translation.tr('auto_mode_2'), self.translation.tr('manual_mode')]
                self.mode_segmented.update_values(new_values)
            except Exception:
                pass

        if self.auto_mode_index == 0:
            self.mode_var.set(self.translation.tr('manual_mode'))
        else:
            self.auto_mode_index = 2
            self.mode_var.set(self.translation.tr('auto_mode_2'))

        if getattr(self, 'mode_segmented', None):
            try:
                self.mode_segmented.select(self.mode_var.get())
            except Exception:
                pass

        safe_config(getattr(self, 'manual_time_label', None), text=self.translation.tr('manual_time_label'))
        safe_config(getattr(self, 'manual_time_hint', None), text=self.translation.tr('manual_time_hint'))
        safe_config(getattr(self, 'cookie_text_label', None), text=self.translation.tr('cookie_label'))
        safe_config(getattr(self, 'login_btn', None), text=self.translation.tr('login_btn'))
        safe_config(getattr(self, 'timings_btn', None), text=self.translation.tr('timings_btn'))
        safe_config(getattr(self, 'check_eligibility_btn', None), text=self.translation.tr('check_eligibility_btn'))
        self.status_var.set(self.translation.tr('status_ready'))

        if self.auto_mode_index == 0:
            self.ping_var.set(self.translation.tr('ping_not_measured_manual'))
        else:
            self.ping_var.set(self.translation.tr('ping'))

        self.time_var.set(self.translation.tr('time'))
        safe_config(getattr(self, 'mi_label', None), text=self.translation.tr('mi_unlock_label'))
        safe_config(getattr(self, 'mi_input_label', None), text=self.translation.tr('input_label'))
        safe_config(getattr(self, 'mi_input_entry', None), placeholder_text=self.translation.tr('mi_unlock_input_placeholder'))
        safe_config(getattr(self, 'mi_log_label', None), text=self.translation.tr('mi_unlock_log_title'))
        safe_config(getattr(self, 'mi_clear_log_btn', None), text=self.translation.tr('clear_log_btn'))
        safe_config(getattr(self, 'start_mi_btn', None), text=self.translation.tr('mi_unlock_start_button'))
        safe_config(getattr(self, 'mi_drivers_btn', None), text=self.translation.tr('mi_unlock_drivers_button'))
        safe_config(getattr(self, 'mi_close_btn', None), text=self.translation.tr('exit'))
        safe_config(getattr(self, 'animations_checkbox', None), text=self.translation.tr('animations_checkbox'))

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

        safe_config(getattr(self, 'log_label', None), text=self.translation.tr('execution_log'))
        safe_config(getattr(self, 'clear_log_btn', None), text=self.translation.tr('clear_log_btn'))
        safe_config(getattr(self, 'start_button', None), text=self.translation.tr('submit_application'))
        safe_config(getattr(self, 'exit_button', None), text=self.translation.tr('exit'))

        # Плейсхолдер с точками на конце
        safe_config(getattr(self, 'cookie_entry', None), placeholder_text=self.translation.tr('cookie_placeholder'))
        safe_config(getattr(self, 'manual_time_entry', None), placeholder_text="59.1")

        if hasattr(self, 'login_panel') and self.login_panel is not None:
            try:
                if hasattr(self.login_panel, 'winfo_exists') and self.login_panel.winfo_exists():
                    self.login_panel.update_ui_text()
            except Exception as e:
                print(f"Error updating login panel language: {e}")

        try:
            self.toggle_mode(self.mode_var.get())
        except Exception:
            pass

    def update_md3_colors(self):
        dark_mode = True

        self.top_bar.configure(fg_color=MaterialColors.get_color('surface_container'))
        self.title_label.configure(text_color=MaterialColors.get_color('on_surface'))
        if hasattr(self, 'subtitle_label') and self.subtitle_label is not None:
            try:
                self.subtitle_label.configure(text_color=MaterialColors.get_color('on_surface_variant'))
            except Exception:
                pass

        if getattr(self, 'params_card', None) is not None:
            self.params_card.configure(fg_color=MaterialColors.get_color('surface_container'))
        if getattr(self, 'log_card', None) is not None:
            self.log_card.configure(fg_color=MaterialColors.get_color('surface_container'))
        if getattr(self, 'beijing_timer_card', None) is not None:
            self.beijing_timer_card.configure(
                fg_color=MaterialColors.get_color('surface_container_high'),
                border_color=MaterialColors.get_color('outline_variant')
            )
        if getattr(self, 'beijing_collapsed_btn', None) is not None:
            self.beijing_collapsed_btn.configure(
                fg_color=MaterialColors.get_color('surface_container_high'),
                hover_color=MaterialColors.get_color('surface_container_highest'),
                border_color=MaterialColors.get_color('outline_variant'),
                text_color=MaterialColors.get_color('primary')
            )
        if getattr(self, 'beijing_collapse_btn', None) is not None:
            self.beijing_collapse_btn.configure(
                border_color=MaterialColors.get_color('outline_variant'),
                hover_color=MaterialColors.get_color('surface_container_highest'),
                text_color=MaterialColors.get_color('on_surface_variant')
            )
        if getattr(self, 'beijing_timer_title_label', None) is not None:
            self.beijing_timer_title_label.configure(text_color=MaterialColors.get_color('primary'))
        if getattr(self, 'beijing_timer_subtext_label', None) is not None:
            self.beijing_timer_subtext_label.configure(text_color=MaterialColors.get_color('on_surface_variant'))
        if getattr(self, 'bypass_card', None) is not None:
            self.bypass_card.configure(fg_color=MaterialColors.get_color('surface_container'))
        if getattr(self, 'bypass_center_panel', None) is not None:
            self.bypass_center_panel.configure(
                fg_color=MaterialColors.get_color('surface_container_low'),
                border_color=MaterialColors.get_color('outline_variant')
            )
        if getattr(self, 'bypass_icon_lbl', None) is not None:
            self.bypass_icon_lbl.configure(text_color=MaterialColors.get_color('primary'))
        if getattr(self, 'bypass_title_label', None) is not None:
            self.bypass_title_label.configure(text_color=MaterialColors.get_color('on_surface'))
        if getattr(self, 'bypass_desc_label', None) is not None:
            self.bypass_desc_label.configure(text_color=MaterialColors.get_color('on_surface_variant'))
        if getattr(self, 'bypass_return_btn', None) is not None:
            self.bypass_return_btn.configure(
                fg_color=MaterialColors.get_color('primary'),
                hover_color=MaterialColors.get_color('primary_container'),
                text_color=MaterialColors.get_color('on_primary'),
                border_width=0
            )

        text_color = MaterialColors.get_color('on_surface')
        for _name in ('params_label', 'mode_label', 'manual_time_label', 'cookie_text_label', 'log_label'):
            _widget = getattr(self, _name, None)
            if _widget is not None:
                _widget.configure(text_color=text_color)

        self.log_label_bg.configure(fg_color='#1F1F1F')
        self.clear_log_bg.configure(fg_color='transparent')
        self.exit_bg.configure(fg_color='transparent')
        if hasattr(self, 'params_label_bg'):
            self.params_label_bg.configure(fg_color='#1F1F1F')

        bg_color = MaterialColors.get_color('surface_container_lowest')
        border_color = MaterialColors.get_color('outline')

        for _name in ('cookie_entry', 'manual_time_entry', 'log_text'):
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
                fg_color='#202020',
                hover_color='#383838',
                text_color='#FFFFFF',
                border_width=0
            )

        _widget = getattr(self, 'mi_close_btn', None)
        if _widget is not None:
            _widget.configure(
                fg_color='#202020',
                hover_color='#383838',
                text_color='#FFFFFF',
                border_width=0
            )

        for _btn_name in ('login_btn', 'timings_btn', 'check_eligibility_btn'):
            _widget = getattr(self, _btn_name, None)
            if _widget is not None:
                _widget.configure(
                    fg_color='transparent',
                    hover_color=MaterialColors.get_color('surface_container'),
                    text_color=MaterialColors.get_color('primary'),
                    border_color=MaterialColors.get_color('outline'),
                    border_width=1
                )

        # Обновление всех вкладок верхнего меню сразу
        if hasattr(self, 'tab_buttons') and self.tab_buttons:
            for btn_name, btn in self.tab_buttons.items():
                if btn_name == getattr(self, 'current_tab', 'unlock'):
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

        if hasattr(self, 'tab_containers') and self.tab_containers:
            for c in self.tab_containers.values():
                try:
                    c.configure(fg_color=MaterialColors.get_color('background'))
                except Exception:
                    pass

        # Обновление кнопок боковой панели настроек сразу
        if hasattr(self, 'settings_sidebar_buttons') and self.settings_sidebar_buttons:
            for key, btn in self.settings_sidebar_buttons.items():
                if key == getattr(self, 'settings_active_section', 'settings'):
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

        if hasattr(self, 'theme_color_preview') and self.theme_color_preview is not None and self.theme_color_preview.winfo_exists():
            self.theme_color_preview.configure(
                fg_color=MaterialColors.get_color('primary'),
                border_color=MaterialColors.get_color('outline')
            )

        self.exit_button.configure(
            fg_color='#202020',
            hover_color='#383838',
            text_color='#FFFFFF',
            border_width=0
        )

        self.clear_log_btn.configure(
            fg_color='#202020',
            hover_color='#383838',
            text_color='#FFFFFF',
            border_width=0
        )

        self.clear_log_bg.configure(
            fg_color='transparent',
            corner_radius=16,
            border_width=0
        )

        if self.mode_segmented:
            self.mode_segmented.update_colors()

        self.main_container.configure(fg_color=MaterialColors.get_color('background'))
        self.content_area.configure(fg_color=MaterialColors.get_color('background'))

        if hasattr(self, 'desc_label') and self.desc_label and hasattr(self.desc_label, 'winfo_exists') and self.desc_label.winfo_exists():
            self.desc_label.configure(text_color=MaterialColors.get_color('on_surface_variant'))
        if hasattr(self, 'mi_desc_label') and self.mi_desc_label and hasattr(self.mi_desc_label, 'winfo_exists') and self.mi_desc_label.winfo_exists():
            self.mi_desc_label.configure(text_color=MaterialColors.get_color('on_surface_variant'))
        self._update_footer_colors()

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
        if hasattr(self, 'thread_coordinator'):
            try:
                self.thread_coordinator.stop()
            except Exception:
                pass
        self.config['cookie'] = self.cookie_value.get()
        save_config(self.config)
        self.root.destroy()
        sys.exit(0)

    def get_beijing_time(self):
        try:
            if hasattr(self, 'thread_coordinator') and getattr(self.thread_coordinator, '_time_sync_active', False):
                synced = self.thread_coordinator.get_synced_beijing_time()
                if synced:
                    return synced
            elif getattr(self, 'start_beijing_time', None) and getattr(self, 'start_timestamp', None):
                return self.request_handler.get_synchronized_beijing_time(self.start_beijing_time, self.start_timestamp)
        except Exception:
            pass
        return datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8)))

    def toggle_beijing_clock(self):
        self.beijing_clock_collapsed = not getattr(self, 'beijing_clock_collapsed', False)
        self.config['beijing_clock_collapsed'] = self.beijing_clock_collapsed
        save_config(self.config)
        self._apply_beijing_clock_state()

    def _apply_beijing_clock_state(self):
        if not hasattr(self, 'beijing_clock_container') or not self.beijing_clock_container:
            return
        now_str = self.get_beijing_time().strftime("%H:%M:%S")
        if getattr(self, 'beijing_clock_collapsed', False):
            if hasattr(self, 'beijing_timer_card') and self.beijing_timer_card:
                self.beijing_timer_card.pack_forget()
            if hasattr(self, 'beijing_collapsed_btn') and self.beijing_collapsed_btn:
                self.beijing_collapsed_btn.configure(
                    text=f"🕒 {self.translation.tr('beijing_time_title')}: {now_str}   ▼ {self.translation.tr('beijing_clock_expand')}"
                )
                self.beijing_collapsed_btn.pack(fill="x")
        else:
            if hasattr(self, 'beijing_collapsed_btn') and self.beijing_collapsed_btn:
                self.beijing_collapsed_btn.pack_forget()
            if hasattr(self, 'beijing_timer_card') and self.beijing_timer_card:
                self.beijing_timer_card.pack(fill="x")

    def _tick_beijing_clock(self):
        try:
            now_bj = self.get_beijing_time()
            time_str = now_bj.strftime("%H:%M:%S")
            if hasattr(self, 'beijing_clock_label') and self.beijing_clock_label and hasattr(self.beijing_clock_label, 'winfo_exists') and self.beijing_clock_label.winfo_exists():
                self.beijing_clock_label.configure(text=time_str)
            if hasattr(self, 'beijing_collapsed_btn') and self.beijing_collapsed_btn and hasattr(self.beijing_collapsed_btn, 'winfo_exists') and self.beijing_collapsed_btn.winfo_exists():
                self.beijing_collapsed_btn.configure(
                    text=f"🕒 {self.translation.tr('beijing_time_title')}: {time_str}   ▼ {self.translation.tr('beijing_clock_expand')}"
                )
        except Exception:
            pass
        finally:
            if hasattr(self, 'root') and self.root:
                try:
                    if hasattr(self.root, 'winfo_exists') and self.root.winfo_exists():
                        self.root.after(200, self._tick_beijing_clock)
                except Exception:
                    pass

    def _update_clock_text(self, time_str):
        try:
            if hasattr(self, 'time_var') and self.time_var is not None:
                self.time_var.set(
                    f"{self.translation.tr('time_synchronized')}: {time_str} (UTC+8)"
                )
            parts = str(time_str).split(' ')
            t_val = parts[1] if len(parts) > 1 else str(time_str)
            if hasattr(self, 'beijing_clock_label') and self.beijing_clock_label and hasattr(self.beijing_clock_label, 'winfo_exists') and self.beijing_clock_label.winfo_exists():
                self.beijing_clock_label.configure(text=t_val)
            if hasattr(self, 'beijing_collapsed_btn') and self.beijing_collapsed_btn and hasattr(self.beijing_collapsed_btn, 'winfo_exists') and self.beijing_collapsed_btn.winfo_exists():
                self.beijing_collapsed_btn.configure(
                    text=f"🕒 {self.translation.tr('beijing_time_title')}: {t_val}   ▼ {self.translation.tr('beijing_clock_expand')}"
                )
        except Exception:
            pass

    def _ensure_log_file(self):
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

    def _ui_insert_log(self, formatted_message, color=None):
        try:
            self.log_text.configure(state="normal")
            if color:
                tag_name = f"log_tag_{color}"
                if not hasattr(self, '_configured_log_tags'):
                    self._configured_log_tags = set()
                if tag_name not in self._configured_log_tags:
                    color_map = {
                        'green': '#4ADE80',
                        'red': '#F87171',
                        'blue': '#60A5FA',
                        'orange': '#FB923C',
                        'cyan': '#38BDF8',
                        'yellow': '#FBBF24',
                        'white': '#F1F5F9',
                    }
                    fg = color_map.get(color, color if str(color).startswith('#') else '#F1F5F9')
                    try:
                        self.log_text.tag_config(tag_name, foreground=fg)
                        self._configured_log_tags.add(tag_name)
                    except Exception:
                        pass
                self.log_text.insert("end", formatted_message, (tag_name,))
            else:
                self.log_text.insert("end", formatted_message)

            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        except Exception:
            pass

    def log_message(self, message, color=None, write_to_file=True):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        if hasattr(self, 'thread_coordinator'):
            self.thread_coordinator.post_to_ui(self._ui_insert_log, formatted_message, color)
            if write_to_file:
                self.thread_coordinator.queue_log_write(formatted_message)
        else:
            if threading.current_thread() is threading.main_thread():
                self._ui_insert_log(formatted_message, color)
                try:
                    if write_to_file and self.settings.get('log_to_txt', True):
                        self._ensure_log_file()
                except Exception:
                    pass
            try:
                if write_to_file and self.settings.get('log_to_txt', True):
                    self._ensure_log_file()
                    with open(self.current_log_file, 'a', encoding='utf-8') as f:
                        f.write(formatted_message)
            except Exception as e:
                print(f"Ошибка записи лога: {e}")

    def _write_log_header(self):
        try:
            mode_str = "Auto"
            manual_str = ""
            if threading.current_thread() is threading.main_thread():
                try:
                    if hasattr(self, 'mode_var') and self.mode_var is not None:
                        mode_str = str(self.mode_var.get())
                except Exception:
                    pass
                try:
                    if hasattr(self, 'manual_time_var') and self.manual_time_var is not None:
                        manual_str = str(self.manual_time_var.get())
                except Exception:
                    pass

            with open(self.current_log_file, 'w', encoding='utf-8') as f:
                f.write("=== XIAOMI UNLOCK TOOL LOG ===\n")
                f.write(f"Version: {CURRENT_VERSION}\n")
                f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 30 + "\n")
                f.write("SETTINGS:\n")
                f.write(f"Mode: {mode_str}\n")
                if mode_str == self.translation.tr('auto_mode'):
                    f.write(f"Spam Mode: {self.settings.get('spam_mode', True)}\n")
                if mode_str == self.translation.tr('manual_mode'):
                    f.write(f"Manual Time Target: {manual_str}\n")
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

        def on_time_reached():
            now = self.request_handler.get_synchronized_beijing_time(
                self.start_beijing_time, self.start_timestamp
            )
            self.log_message(self.translation.tr('time_reached').format(
                now.strftime('%Y-%m-%d %H:%M:%S.%f')
            ))
            if hasattr(self, 'thread_coordinator'):
                self.thread_coordinator.submit_send(self.send_request_with_token)
            else:
                self.send_request_with_token()

        if hasattr(self, 'thread_coordinator'):
            self.thread_coordinator.watch_single_target(send_at, on_time_reached)
        else:
            def check_time():
                current_time = self.request_handler.get_synchronized_beijing_time(
                    self.start_beijing_time, self.start_timestamp
                )
                self.time_var.set(
                    f"{self.translation.tr('time_synchronized')}: {current_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)"
                )
                if current_time >= send_at:
                    on_time_reached()
                else:
                    self.root.after(10, check_time)

            check_time()

    def send_request_with_token(self):
        main_token = self.cookie_value.get().strip()
        if not main_token:
            self.log_message(self.translation.tr('cookie_error'), "red")
            if hasattr(self, 'thread_coordinator'):
                self.thread_coordinator.post_to_ui(
                    messagebox.showerror,
                    self.translation.tr('error_title'),
                    self.translation.tr('cookie_error')
                )
            else:
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
        try:
            if self.settings.get('log_to_txt', True):
                self._ensure_log_file()
        except Exception:
            pass

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
        if hasattr(self, 'thread_coordinator'):
            self.thread_coordinator.arm_time_sync(self.start_beijing_time, self.start_timestamp)

        if self.auto_mode_index == 0:
            self.start_manual_mode()
        else:
            self.log_message(f"[{self.translation.tr('auto_mode_2')}] {self.translation.tr('status_mode2_waiting')}", color="blue")
            self.wait_for_presync_time()

    def wait_for_presync_time(self):
        timings = sorted(getattr(self, 'selected_timings', [58.7, 58.8, 59.1, 59.3, 59.5, 59.8]))
        first_send = timings[0] if timings else 58.7
        target_midnight = self.start_beijing_time.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        base_minute = target_midnight - timedelta(minutes=1)
        target_schedule = base_minute + timedelta(seconds=max(0.0, first_send - 5.0))
        target_send_time = base_minute + timedelta(seconds=first_send)
        if target_schedule <= self.start_beijing_time:
            base_minute += timedelta(days=1)
            target_schedule += timedelta(days=1)
            target_send_time += timedelta(days=1)

        current_time = self.request_handler.get_synchronized_beijing_time(
            self.start_beijing_time, self.start_timestamp
        )

        def on_schedule_time():
            self.status_var.set(self.translation.tr('scheduling_requests'))
            if hasattr(self, 'thread_coordinator'):
                self.thread_coordinator.post_to_ui(self.schedule_multi_request)
            else:
                self.schedule_multi_request()

        if current_time >= target_schedule:
            on_schedule_time()
        else:
            self.log_message(self.translation.tr('status_mode2_waiting'), "blue")
            self.status_var.set(self.translation.tr('status_mode2_waiting'))

            if hasattr(self, 'thread_coordinator'):
                self.thread_coordinator.watch_multi_target(target_schedule, on_schedule_time)
            else:
                def check_time():
                    now = self.request_handler.get_synchronized_beijing_time(
                        self.start_beijing_time, self.start_timestamp
                    )
                    self.time_var.set(
                        f"{self.translation.tr('time_synchronized')}: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)"
                    )
                    if now >= target_schedule:
                        on_schedule_time()
                    else:
                        self.root.after(50, check_time)

                check_time()

    def measure_pings_and_send(self):
        self.schedule_multi_request()

    def schedule_multi_request(self, ping_http_ms=None, ping_tcp_ms=None):
        token = self.cookie_value.get().strip()
        if not token:
            self.log_message(self.translation.tr('cookie_error'), "red")
            return

        target_midnight = self.start_beijing_time.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        base_minute = target_midnight - timedelta(minutes=1)
        now_sync = self.request_handler.get_synchronized_beijing_time(
            self.start_beijing_time, self.start_timestamp
        )
        if base_minute + timedelta(seconds=60) <= now_sync:
            base_minute += timedelta(days=1)

        timings = sorted(getattr(self, 'selected_timings', [58.7, 58.8, 59.1, 59.3, 59.5, 59.8]))
        device_ids = [self.request_handler.generate_device_id() for _ in range(len(timings))]

        for i, t_val in enumerate(timings):
            dev_id = device_ids[i]
            send_seconds = max(55.0, min(59.999, float(t_val)))
            send_at = base_minute + timedelta(seconds=send_seconds)
            delay = max(0.0, (send_at - now_sync).total_seconds())
            self.log_message(
                f"[{self.translation.tr('auto_mode_2')}] #{i + 1} target 23:59:{send_seconds:06.3f} ({delay:.2f}s) device_id={dev_id}",
                "blue"
            )
            if hasattr(self, 'thread_coordinator'):
                self.thread_coordinator.schedule_send_in(
                    delay,
                    self.request_handler.make_single_request_with_new_device_id,
                    i + 1, send_seconds, dev_id, token
                )
            else:
                threading.Timer(
                    delay,
                    self.request_handler.make_single_request_with_new_device_id,
                    args=(i + 1, send_seconds, dev_id, token)
                ).start()

        self.log_message(self.translation.tr('scheduling_requests'), "green")

    def start_manual_mode(self):
        token = self.cookie_value.get().strip()
        if not token:
            self.log_message(self.translation.tr('cookie_error'), "red")
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('cookie_error'))
            return

        manual_str = self.manual_time_var.get().strip()
        timings = []
        if manual_str:
            for part in re.split(r'[,;\s]+', manual_str):
                try:
                    val = parse_timing_value(part)
                    if 0 <= val <= 60:
                        timings.append(val)
                except Exception:
                    pass

        if not timings:
            timings = sorted(getattr(self, 'selected_timings', [58.7, 58.8, 59.1, 59.3, 59.5, 59.8]))

        if not timings:
            self.log_message(self.translation.tr('manual_time_error'), "red")
            messagebox.showerror(self.translation.tr('error_title'), self.translation.tr('manual_time_error'))
            return

        timings = sorted(timings)
        if len(timings) == 1:
            script_time = timings[0]
            self.log_message(self.translation.tr('manual_mode_start').format(f"{script_time:.3f}"), "blue")
            self.wait_until_target_time(self.start_beijing_time, self.start_timestamp, script_time)
        else:
            self.log_message(f"[{self.translation.tr('manual_mode')}] " + ", ".join(f"{t:.3f}s" for t in timings), "blue")
            self.wait_until_target_timings_multi(self.start_beijing_time, self.start_timestamp, timings)

    def wait_until_target_timings_multi(self, start_beijing_time, start_timestamp, timings):
        target_midnight = start_beijing_time.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timedelta(days=1)
        base_minute = target_midnight - timedelta(minutes=1)
        first_send = base_minute + timedelta(seconds=timings[0])
        if first_send <= start_beijing_time:
            base_minute += timedelta(days=1)
            first_send += timedelta(days=1)

        token = self.cookie_value.get().strip()
        self.status_var.set(self.translation.tr('status_mode2_waiting'))

        schedule_time = base_minute + timedelta(seconds=max(0.0, timings[0] - 5.0))

        def on_schedule_reached():
            now = self.request_handler.get_synchronized_beijing_time(self.start_beijing_time, self.start_timestamp)
            for i, t_val in enumerate(timings):
                send_at = base_minute + timedelta(seconds=t_val)
                delay = max(0.0, (send_at - now).total_seconds())
                device_id = self.request_handler.generate_device_id()
                self.log_message(
                    f"[{self.translation.tr('manual_mode')}] #{i + 1} target 23:59:{t_val:06.3f} ({delay:.2f}s) device_id={device_id}",
                    "blue"
                )
                if hasattr(self, 'thread_coordinator'):
                    self.thread_coordinator.schedule_send_in(
                        delay,
                        self.request_handler.make_single_request_with_new_device_id,
                        i + 1, t_val, device_id, token
                    )
                else:
                    threading.Timer(
                        delay,
                        self.request_handler.make_single_request_with_new_device_id,
                        args=(i + 1, t_val, device_id, token)
                    ).start()
            self.status_var.set(self.translation.tr('scheduling_requests'))

        if hasattr(self, 'thread_coordinator'):
            self.thread_coordinator.watch_multi_target(schedule_time, on_schedule_reached)
        else:
            def check_time():
                now = self.request_handler.get_synchronized_beijing_time(self.start_beijing_time, self.start_timestamp)
                self.time_var.set(f"{self.translation.tr('time_synchronized')}: {now.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
                if now >= schedule_time:
                    on_schedule_reached()
                else:
                    self.root.after(20, check_time)

            check_time()


def main():
    global root
    root = ctk.CTk()
    app = XiaomiUnlockTool(root)
    root.app = app
    root.mainloop()


if __name__ == "__main__":
    main()