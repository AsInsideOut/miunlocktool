#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Xiaomi Unlock Tool - Auto Updater
Downloads, verifies, extracts updates, updates itself if needed, and restarts the tool.
"""

import os
import sys
import json
import re
import time
import shutil
import zipfile
import hashlib
import tempfile
import threading
import argparse
import subprocess
import urllib.request
import urllib.error

# Default URLs
UPDATE_CHECK_URL = "https://miunlock.su/version.txt"
PRIMARY_DOWNLOAD_URL = "https://miunlock.su/download/stable/pc/Latest_Release.zip"
FALLBACK_DOWNLOAD_URL = "https://miunlock.su/Latest_Release.zip"

# Multilingual localization dictionaries
LOCALES = {
    'en': {
        'app_title': 'Xiaomi Unlock Tool - Auto Update',
        'checking': 'Checking for updates...',
        'up_to_date_title': 'Up to Date',
        'up_to_date_msg': 'You are already using the latest version ({version}).',
        'update_found_title': 'Update Available',
        'update_found_msg': 'New version {latest} is available! (Current: {current})\n\nWould you like to download and install the update now?',
        'downloading': 'Downloading update... {percent:.1f}% ({dl_mb:.1f} MB / {total_mb:.1f} MB)',
        'download_complete': 'Download complete. Preparing files...',
        'extracting': 'Extracting and replacing files...',
        'updating_self': 'Updating autoupdate.py...',
        'launching': 'Update finished! Launching Xiaomi Unlock Tool...',
        'btn_update': 'Update Now',
        'btn_cancel': 'Cancel',
        'btn_ok': 'OK',
        'btn_close': 'Close',
        'error_title': 'Update Error',
        'error_msg': 'An error occurred during update:\n{error}',
    },
    'ru': {
        'app_title': 'Xiaomi Unlock Tool - Автообновление',
        'checking': 'Проверка наличия обновлений...',
        'up_to_date_title': 'Обновлений нет',
        'up_to_date_msg': 'У вас уже установлена последняя версия ({version}).',
        'update_found_title': 'Доступно обновление',
        'update_found_msg': 'Доступна новая версия {latest}! (Текущая: {current})\n\nХотите загрузить и установить обновление сейчас?',
        'downloading': 'Загрузка обновления... {percent:.1f}% ({dl_mb:.1f} МБ / {total_mb:.1f} МБ)',
        'download_complete': 'Загрузка завершена. Подготовка файлов...',
        'extracting': 'Распаковка и замена файлов...',
        'updating_self': 'Обновление autoupdate.py...',
        'launching': 'Обновление завершено! Запуск Xiaomi Unlock Tool...',
        'btn_update': 'Обновить сейчас',
        'btn_cancel': 'Отмена',
        'btn_ok': 'OK',
        'btn_close': 'Закрыть',
        'error_title': 'Ошибка обновления',
        'error_msg': 'Произошла ошибка при обновлении:\n{error}',
    },
    'id': {
        'app_title': 'Xiaomi Unlock Tool - Pembaruan Otomatis',
        'checking': 'Memeriksa pembaruan...',
        'up_to_date_title': 'Sudah Terbaru',
        'up_to_date_msg': 'Anda sudah menggunakan versi terbaru ({version}).',
        'update_found_title': 'Pembaruan Tersedia',
        'update_found_msg': 'Versi baru {latest} tersedia! (Saat ini: {current})\n\nApakah Anda ingin mengunduh dan memasang pembaruan sekarang?',
        'downloading': 'Mengunduh pembaruan... {percent:.1f}% ({dl_mb:.1f} MB / {total_mb:.1f} MB)',
        'download_complete': 'Pengunduhan selesai. Menyiapkan file...',
        'extracting': 'Mengekstrak dan mengganti file...',
        'updating_self': 'Memperbarui autoupdate.py...',
        'launching': 'Pembaruan selesai! Menjalankan Xiaomi Unlock Tool...',
        'btn_update': 'Perbarui Sekarang',
        'btn_cancel': 'Batal',
        'btn_ok': 'OK',
        'btn_close': 'Tutup',
        'error_title': 'Kesalahan Pembaruan',
        'error_msg': 'Terjadi kesalahan saat pembaruan:\n{error}',
    },
    'es': {
        'app_title': 'Xiaomi Unlock Tool - Actualización Automática',
        'checking': 'Buscando actualizaciones...',
        'up_to_date_title': 'Actualizado',
        'up_to_date_msg': 'Ya tienes instalada la última versión ({version}).',
        'update_found_title': 'Actualización disponible',
        'update_found_msg': '¡La nueva versión {latest} está disponible! (Actual: {current})\n\n¿Deseas descargar e instalar la actualización ahora?',
        'downloading': 'Descargando actualización... {percent:.1f}% ({dl_mb:.1f} MB / {total_mb:.1f} MB)',
        'download_complete': 'Descarga completada. Preparando archivos...',
        'extracting': 'Extrayendo y reemplazando archivos...',
        'updating_self': 'Actualizando autoupdate.py...',
        'launching': '¡Actualización completada! Iniciando Xiaomi Unlock Tool...',
        'btn_update': 'Actualizar ahora',
        'btn_cancel': 'Cancelar',
        'btn_ok': 'Aceptar',
        'btn_close': 'Cerrar',
        'error_title': 'Error de actualización',
        'error_msg': 'Ocurrió un error durante la actualización:\n{error}',
    },
    'zh': {
        'app_title': 'Xiaomi Unlock Tool - 自动更新',
        'checking': '正在检查更新...',
        'up_to_date_title': '已是最新版本',
        'up_to_date_msg': '您当前正在使用最新版本 ({version})。',
        'update_found_title': '发现新版本',
        'update_found_msg': '发现新版本 {latest}！（当前版本：{current}）\n\n是否立即下载并安装更新？',
        'downloading': '正在下载更新... {percent:.1f}% ({dl_mb:.1f} MB / {total_mb:.1f} MB)',
        'download_complete': '下载完成，准备替换文件...',
        'extracting': '正在解压并替换文件...',
        'updating_self': '正在更新 autoupdate.py...',
        'launching': '更新完成！正在启动 Xiaomi Unlock Tool...',
        'btn_update': '立即更新',
        'btn_cancel': '取消',
        'btn_ok': '确定',
        'btn_close': '关闭',
        'error_title': '更新失败',
        'error_msg': '更新过程中发生错误：\n{error}',
    },
    'pt': {
        'app_title': 'Xiaomi Unlock Tool - Atualização Automática',
        'checking': 'Verificando atualizações...',
        'up_to_date_title': 'Atualizado',
        'up_to_date_msg': 'Você já está usando a versão mais recente ({version}).',
        'update_found_title': 'Atualização disponível',
        'update_found_msg': 'Nova versão {latest} disponível! (Atual: {current})\n\nDeseja baixar e instalar a atualização agora?',
        'downloading': 'Baixando atualização... {percent:.1f}% ({dl_mb:.1f} MB / {total_mb:.1f} MB)',
        'download_complete': 'Download concluído. Preparando arquivos...',
        'extracting': 'Extraindo e substituindo arquivos...',
        'updating_self': 'Atualizando autoupdate.py...',
        'launching': 'Atualização concluída! Iniciando Xiaomi Unlock Tool...',
        'btn_update': 'Atualizar agora',
        'btn_cancel': 'Cancelar',
        'btn_ok': 'OK',
        'btn_close': 'Fechar',
        'error_title': 'Erro de atualização',
        'error_msg': 'Ocorreu um erro durante a atualização:\n{error}',
    },
}


def get_user_language():
    """Detects preferred language from user config or system."""
    try:
        if os.name == 'nt':
            config_dir = os.path.join(os.environ.get('APPDATA', ''), 'MiUnlockTool')
        else:
            config_dir = os.path.join(os.path.expanduser('~'), '.config', 'MiUnlockTool')
        config_file = os.path.join(config_dir, 'config.json')
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                lang = cfg.get('language')
                if lang in LOCALES:
                    return lang
    except Exception:
        pass
    return 'en'


def get_text(key, lang=None, **kwargs):
    """Retrieves localized text with formatting."""
    if not lang or lang not in LOCALES:
        lang = get_user_language()
    template = LOCALES.get(lang, LOCALES['en']).get(key, LOCALES['en'].get(key, key))
    try:
        return template.format(**kwargs)
    except Exception:
        return template


def detect_base_dir():
    """Detects the main root folder of Xiaomi Unlock Tool."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(current_dir).lower() == 'res':
        return os.path.abspath(os.path.join(current_dir, '..'))
    return current_dir


def extract_version_number(version_str):
    """Extracts semantic digits from a version string."""
    if not version_str:
        return None
    text = str(version_str).strip()
    match = re.search(r'(\d+\.\d+\.\d+)', text)
    if not match:
        match = re.search(r'(\d+\.\d+)', text)
    return match.group(1) if match else None


def compare_versions(v1, v2):
    """Compares two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal."""
    try:
        v1_parts = [int(p) for p in str(v1).split('.') if p.isdigit()]
        v2_parts = [int(p) for p in str(v2).split('.') if p.isdigit()]
        for i in range(max(len(v1_parts), len(v2_parts))):
            a = v1_parts[i] if i < len(v1_parts) else 0
            b = v2_parts[i] if i < len(v2_parts) else 0
            if a > b:
                return 1
            elif a < b:
                return -1
        return 0
    except Exception:
        return 0


def get_current_version(base_dir):
    """Finds current application version from 8.0.py or directory contents."""
    # 1. Search for version in 8.0.py or main files
    for fname in os.listdir(base_dir):
        if fname.endswith('.py') and re.match(r'^\d+(\.\d+)*\.py$', fname):
            fpath = os.path.join(base_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(4096)
                    m = re.search(r'CURRENT_VERSION\s*=\s*["\']([^"\']+)["\']', content)
                    if m:
                        return m.group(1)
            except Exception:
                pass
            return fname[:-3]
    return "8.0"


def check_remote_version(check_url=UPDATE_CHECK_URL):
    """Queries the remote version endpoint."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) XiaomiUnlockTool-Updater'}
    req = urllib.request.Request(check_url, headers=headers)
    with urllib.request.urlopen(req, timeout=8) as resp:
        text = resp.read().decode('utf-8', errors='ignore').strip()
        return text


def get_archive_prefix(zip_file):
    """
    Detects if the zip archive has a single common top-level directory
    (e.g., 'Xiaomi Unlock Tool 7.3/').
    """
    entries = [m.filename for m in zip_file.infolist() if not m.is_dir()]
    if not entries:
        return ""
    
    first_parts = set()
    for name in entries:
        norm = name.replace('\\', '/')
        parts = norm.split('/')
        if len(parts) > 1:
            first_parts.add(parts[0])
        else:
            return ""
            
    if len(first_parts) == 1:
        return list(first_parts)[0] + '/'
    return ""


def find_autoupdate_in_zip(zip_file, prefix=""):
    """Finds autoupdate.py entry inside the zip archive."""
    for info in zip_file.infolist():
        if info.is_dir():
            continue
        norm = info.filename.replace('\\', '/')
        if prefix and norm.startswith(prefix):
            norm = norm[len(prefix):]
        norm = norm.strip('/')
        if norm in ("res/autoupdate.py", "autoupdate.py"):
            return info, norm
    return None, None


def is_autoupdate_different(zip_file, autoupdate_info, current_autoupdate_path):
    """Checks if the zip's autoupdate.py is different from current on disk."""
    if not os.path.exists(current_autoupdate_path):
        return True
    
    current_size = os.path.getsize(current_autoupdate_path)
    zip_size = autoupdate_info.file_size
    
    if current_size != zip_size:
        return True
    
    # If same size, compare SHA256 checksums
    try:
        with open(current_autoupdate_path, 'rb') as cf:
            current_hash = hashlib.sha256(cf.read()).hexdigest()
        with zip_file.open(autoupdate_info) as zf:
            zip_hash = hashlib.sha256(zf.read()).hexdigest()
        return current_hash != zip_hash
    except Exception:
        return True


def download_file(urls, dest_path, progress_callback=None, cancel_event=None):
    """Downloads a file trying multiple URLs with progress reporting."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) XiaomiUnlockTool-Updater'}
    last_error = None
    
    for url in urls:
        if cancel_event and cancel_event.is_set():
            return False, "Cancelled"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    last_error = f"HTTP status {resp.status}"
                    continue
                
                total_size = int(resp.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_size = 1024 * 64
                
                part_path = dest_path + ".part"
                with open(part_path, 'wb') as out_file:
                    while True:
                        if cancel_event and cancel_event.is_set():
                            out_file.close()
                            if os.path.exists(part_path):
                                os.remove(part_path)
                            return False, "Cancelled"
                        
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress_callback(downloaded, total_size)
                
                if os.path.exists(dest_path):
                    os.remove(dest_path)
                os.replace(part_path, dest_path)
                return True, url
        except Exception as e:
            last_error = str(e)
            part_path = dest_path + ".part"
            if os.path.exists(part_path):
                try:
                    os.remove(part_path)
                except Exception:
                    pass
            continue
            
    return False, last_error or "All download sources failed"


def extract_and_update(zip_path, base_dir, current_autoupdate_path, status_callback=None):
    """
    1. Unarchives all files except autoupdate.py, replacing existing ones.
    2. Checks for new autoupdate.py in the archive.
    3. If autoupdate.py is different, updates autoupdate.py itself by extracting only that file.
    4. Launches the tool.
    """
    with zipfile.ZipFile(zip_path, 'r') as zf:
        prefix = get_archive_prefix(zf)
        
        # Step 1: Check for new autoupdate.py in archive
        auto_info, auto_rel = find_autoupdate_in_zip(zf, prefix)
        need_self_update = False
        if auto_info is not None:
            need_self_update = is_autoupdate_different(zf, auto_info, current_autoupdate_path)
            if status_callback:
                status_callback(get_text('extracting') + f" (autoupdate difference detected: {need_self_update})")
        
        # Step 2: Unarchive all files EXCEPT autoupdate.py
        if status_callback:
            status_callback(get_text('extracting'))
            
        for member in zf.infolist():
            if member.is_dir():
                continue
            norm = member.filename.replace('\\', '/')
            if prefix and norm.startswith(prefix):
                norm = norm[len(prefix):]
            norm = norm.strip('/')
            if not norm:
                continue
            
            # Skip autoupdate.py in the main extraction pass
            if norm in ("res/autoupdate.py", "autoupdate.py"):
                continue
            
            target_path = os.path.join(base_dir, norm)
            # Security guard against directory traversal
            if not os.path.abspath(target_path).startswith(os.path.abspath(base_dir)):
                continue
            
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with zf.open(member) as src, open(target_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
        
        # Step 3: Update autoupdate.py itself if different
        if need_self_update and auto_info is not None:
            if status_callback:
                status_callback(get_text('updating_self'))
            
            target_autoupdate = current_autoupdate_path
            os.makedirs(os.path.dirname(target_autoupdate), exist_ok=True)
            temp_autoupdate = target_autoupdate + ".new"
            with zf.open(auto_info) as src, open(temp_autoupdate, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            
            if os.path.exists(target_autoupdate):
                os.replace(temp_autoupdate, target_autoupdate)
            else:
                os.rename(temp_autoupdate, target_autoupdate)

    # Step 4: Launch the tool
    if status_callback:
        status_callback(get_text('launching'))
    
    time.sleep(0.5)
    return launch_tool(base_dir)


def launch_tool(base_dir):
    """Finds and launches the latest version of Xiaomi Unlock Tool."""
    # 1. Look for versioned python files (e.g., 8.0.py, 8.1.py, etc.)
    py_files = []
    for f in os.listdir(base_dir):
        if f.endswith('.py') and re.match(r'^\d+(\.\d+)*\.py$', f):
            parts = [int(p) for p in f[:-3].split('.') if p.isdigit()]
            py_files.append((parts, f))
    
    if py_files:
        py_files.sort(key=lambda x: x[0], reverse=True)
        target_script = os.path.join(base_dir, py_files[0][1])
        subprocess.Popen([sys.executable, target_script], cwd=base_dir)
        return target_script
    
    # 2. Look for standard fallback files
    for fname in ('8.0.py', 'main.py'):
        fpath = os.path.join(base_dir, fname)
        if os.path.exists(fpath):
            subprocess.Popen([sys.executable, fpath], cwd=base_dir)
            return fpath
            
    # 3. Look for executable
    for f in os.listdir(base_dir):
        if f.lower().endswith('.exe') and 'updater' not in f.lower() and 'uninstall' not in f.lower():
            fpath = os.path.join(base_dir, f)
            subprocess.Popen([fpath], cwd=base_dir)
            return fpath
            
    return None


class AutoUpdateApp:
    """GUI Auto-updater application using CustomTkinter with Tkinter fallback."""
    
    def __init__(self, base_dir, force=False, custom_url=None, lang=None):
        self.base_dir = base_dir
        self.force = force
        self.custom_url = custom_url
        self.lang = lang or get_user_language()
        self.current_autoupdate_path = os.path.abspath(__file__)
        self.cancel_event = threading.Event()
        self.worker_thread = None
        
        # UI Setup
        self._init_ui()
        
    def _init_ui(self):
        try:
            import customtkinter as ctk
            self.use_ctk = True
            ctk.set_appearance_mode("Dark")
            ctk.set_default_color_theme("dark-blue")
            self.root = ctk.CTk()
        except ImportError:
            import tkinter as tk
            self.use_ctk = False
            self.root = tk.Tk()
            
        self.root.title(get_text('app_title', self.lang))
        self.root.geometry("460x240")
        self.root.resizable(False, False)
        
        # Center window
        self.root.update_idletasks()
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws - 460) // 2
        y = (hs - 240) // 2
        self.root.geometry(f"+{x}+{y}")
        
        if self.use_ctk:
            self._build_ctk_ui()
        else:
            self._build_tk_ui()
            
        # Start check after window loads
        self.root.after(300, self.start_check_flow)

    def _build_ctk_ui(self):
        import customtkinter as ctk
        
        self.main_frame = ctk.CTkFrame(self.root, fg_color="#1D1B20")
        self.main_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        self.title_lbl = ctk.CTkLabel(
            self.main_frame,
            text="Xiaomi Unlock Tool",
            font=("Segoe UI", 18, "bold"),
            text_color="#D0BCFF"
        )
        self.title_lbl.pack(anchor="w", pady=(0, 8))
        
        self.status_lbl = ctk.CTkLabel(
            self.main_frame,
            text=get_text('checking', self.lang),
            font=("Segoe UI", 13),
            wraplength=410,
            justify="left",
            text_color="#E6E0E9"
        )
        self.status_lbl.pack(anchor="w", pady=(0, 12))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame,
            fg_color="#49454F",
            progress_color="#D0BCFF",
            height=10
        )
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        self.details_lbl = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Segoe UI", 11),
            text_color="#CAC4D0"
        )
        self.details_lbl.pack(anchor="w", pady=(0, 12))
        
        self.btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.btn_frame.pack(fill="x", side="bottom")
        
        self.cancel_btn = ctk.CTkButton(
            self.btn_frame,
            text=get_text('btn_cancel', self.lang),
            command=self.on_cancel,
            width=100,
            fg_color="transparent",
            border_color="#938F99",
            border_width=1,
            text_color="#D0BCFF"
        )
        self.cancel_btn.pack(side="right", padx=(8, 0))
        
        self.action_btn = ctk.CTkButton(
            self.btn_frame,
            text=get_text('btn_update', self.lang),
            command=self.on_confirm_update,
            width=120,
            fg_color="#D0BCFF",
            text_color="#381E72",
            hover_color="#E8DEF8"
        )
        self.action_btn.pack(side="right")
        self.action_btn.pack_forget()

    def _build_tk_ui(self):
        import tkinter as tk
        from tkinter import ttk
        
        self.root.configure(bg="#1D1B20")
        self.main_frame = tk.Frame(self.root, bg="#1D1B20")
        self.main_frame.pack(fill="both", expand=True, padx=16, pady=16)
        
        self.title_lbl = tk.Label(
            self.main_frame,
            text="Xiaomi Unlock Tool",
            font=("Segoe UI", 14, "bold"),
            fg="#D0BCFF",
            bg="#1D1B20"
        )
        self.title_lbl.pack(anchor="w", pady=(0, 8))
        
        self.status_lbl = tk.Label(
            self.main_frame,
            text=get_text('checking', self.lang),
            font=("Segoe UI", 10),
            wraplength=410,
            justify="left",
            fg="#E6E0E9",
            bg="#1D1B20"
        )
        self.status_lbl.pack(anchor="w", pady=(0, 12))
        
        self.progress_bar = ttk.Progressbar(self.main_frame, mode="indeterminate", length=410)
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.start(10)
        
        self.details_lbl = tk.Label(
            self.main_frame,
            text="",
            font=("Segoe UI", 9),
            fg="#CAC4D0",
            bg="#1D1B20"
        )
        self.details_lbl.pack(anchor="w", pady=(0, 12))
        
        self.btn_frame = tk.Frame(self.main_frame, bg="#1D1B20")
        self.btn_frame.pack(fill="x", side="bottom")
        
        self.cancel_btn = tk.Button(
            self.btn_frame,
            text=get_text('btn_cancel', self.lang),
            command=self.on_cancel,
            bg="#2B2930",
            fg="#D0BCFF"
        )
        self.cancel_btn.pack(side="right", padx=(8, 0))
        
        self.action_btn = tk.Button(
            self.btn_frame,
            text=get_text('btn_update', self.lang),
            command=self.on_confirm_update,
            bg="#D0BCFF",
            fg="#381E72"
        )

    def set_status(self, text, details=""):
        def _update():
            if self.use_ctk:
                self.status_lbl.configure(text=text)
                self.details_lbl.configure(text=details)
            else:
                self.status_lbl.config(text=text)
                self.details_lbl.config(text=details)
        self.root.after(0, _update)

    def set_progress(self, current, total):
        def _update():
            if total > 0:
                pct = current / total
                if self.use_ctk:
                    self.progress_bar.configure(mode="determinate")
                    self.progress_bar.set(pct)
                else:
                    self.progress_bar.stop()
                    self.progress_bar.config(mode="determinate", maximum=total, value=current)
                    
                dl_mb = current / (1024 * 1024)
                tot_mb = total / (1024 * 1024)
                self.details_lbl.configure(
                    text=f"{dl_mb:.1f} MB / {tot_mb:.1f} MB ({pct * 100:.1f}%)"
                ) if self.use_ctk else self.details_lbl.config(
                    text=f"{dl_mb:.1f} MB / {tot_mb:.1f} MB ({pct * 100:.1f}%)"
                )
        self.root.after(0, _update)

    def start_check_flow(self):
        self.worker_thread = threading.Thread(target=self._check_worker, daemon=True)
        self.worker_thread.start()

    def _check_worker(self):
        current_ver = get_current_version(self.base_dir)
        if self.force:
            # Skip check when forced
            self.root.after(0, self.start_download_flow)
            return

        try:
            remote_ver_str = check_remote_version()
            latest_num = extract_version_number(remote_ver_str)
            current_num = extract_version_number(current_ver)
            
            if latest_num and compare_versions(latest_num, current_num) > 0:
                # Update found! Prompt confirmation
                self.latest_ver = latest_num
                msg = get_text('update_found_msg', self.lang, latest=latest_num, current=current_ver)
                def _show_prompt():
                    if self.use_ctk:
                        self.progress_bar.stop()
                        self.progress_bar.set(0)
                        self.action_btn.pack(side="right")
                    else:
                        self.progress_bar.stop()
                        self.action_btn.pack(side="right")
                    self.set_status(msg)
                self.root.after(0, _show_prompt)
            else:
                # Up to date
                msg = get_text('up_to_date_msg', self.lang, version=current_ver)
                def _show_up_to_date():
                    if self.use_ctk:
                        self.progress_bar.stop()
                        self.progress_bar.set(1.0)
                        self.cancel_btn.configure(text=get_text('btn_close', self.lang))
                    else:
                        self.progress_bar.stop()
                        self.cancel_btn.config(text=get_text('btn_close', self.lang))
                    self.set_status(msg)
                self.root.after(0, _show_up_to_date)
        except Exception as e:
            err_msg = get_text('error_msg', self.lang, error=str(e))
            self.set_status(err_msg)
            self.root.after(0, lambda: self.cancel_btn.configure(text=get_text('btn_close', self.lang)))

    def on_confirm_update(self):
        if self.use_ctk:
            self.action_btn.pack_forget()
        else:
            self.action_btn.pack_forget()
        self.start_download_flow()

    def start_download_flow(self):
        self.set_status(get_text('downloading', self.lang, percent=0, dl_mb=0, total_mb=0))
        self.worker_thread = threading.Thread(target=self._download_and_extract_worker, daemon=True)
        self.worker_thread.start()

    def _download_and_extract_worker(self):
        temp_zip = os.path.join(tempfile.gettempdir(), f"XiaomiUnlockTool_Update_{int(time.time())}.zip")
        urls = [self.custom_url] if self.custom_url else [PRIMARY_DOWNLOAD_URL, FALLBACK_DOWNLOAD_URL]
        
        success, info = download_file(
            urls,
            temp_zip,
            progress_callback=self.set_progress,
            cancel_event=self.cancel_event
        )
        
        if not success:
            if info == "Cancelled":
                self.root.after(0, self.root.destroy)
            else:
                self.set_status(get_text('error_msg', self.lang, error=info))
                if self.use_ctk:
                    self.cancel_btn.configure(text=get_text('btn_close', self.lang))
            return
            
        self.set_status(get_text('download_complete', self.lang))
        time.sleep(0.5)
        
        # Extract, check autoupdate.py, self-update if different, launch
        try:
            launched = extract_and_update(
                temp_zip,
                self.base_dir,
                self.current_autoupdate_path,
                status_callback=lambda s: self.set_status(s)
            )
            
            # Clean up zip
            try:
                if os.path.exists(temp_zip):
                    os.remove(temp_zip)
            except Exception:
                pass
                
            self.set_status(get_text('launching', self.lang))
            self.root.after(1500, self.root.destroy)
        except Exception as e:
            self.set_status(get_text('error_msg', self.lang, error=str(e)))
            if self.use_ctk:
                self.cancel_btn.configure(text=get_text('btn_close', self.lang))

    def on_cancel(self):
        self.cancel_event.set()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def run_cli(base_dir, force=False, custom_url=None, check_only=False):
    """Command-line updater execution."""
    current_ver = get_current_version(base_dir)
    print(f"Current version: {current_ver}")
    print("Checking for updates...")
    
    try:
        remote_str = check_remote_version()
        latest_num = extract_version_number(remote_str)
        current_num = extract_version_number(current_ver)
        
        has_update = latest_num and compare_versions(latest_num, current_num) > 0
        if check_only:
            if has_update:
                print(f"Update available: {latest_num}")
                return 1
            else:
                print("Tool is up to date.")
                return 0
                
        if not has_update and not force:
            print(f"Already up to date ({current_ver}).")
            return 0
            
        if has_update and not force:
            ans = input(f"New version {latest_num} available! Update now? [Y/n]: ").strip().lower()
            if ans not in ('', 'y', 'yes'):
                print("Update cancelled.")
                return 0
    except Exception as e:
        if not force:
            print(f"Error checking version: {e}")
            return 1

    print("Downloading update...")
    temp_zip = os.path.join(tempfile.gettempdir(), f"XiaomiUnlockTool_Update_{int(time.time())}.zip")
    urls = [custom_url] if custom_url else [PRIMARY_DOWNLOAD_URL, FALLBACK_DOWNLOAD_URL]
    
    def cli_progress(dl, total):
        if total > 0:
            pct = dl / total * 100
            sys.stdout.write(f"\rDownloading: {dl / (1024*1024):.1f} MB / {total / (1024*1024):.1f} MB ({pct:.1f}%)")
            sys.stdout.flush()

    success, info = download_file(urls, temp_zip, progress_callback=cli_progress)
    print()
    if not success:
        print(f"Download failed: {info}")
        return 1

    print("Extracting files and checking autoupdate.py...")
    current_auto = os.path.abspath(__file__)
    launched = extract_and_update(temp_zip, base_dir, current_auto, status_callback=print)
    print("Update complete! Launched:", launched)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Xiaomi Unlock Tool - Auto Updater")
    parser.add_argument("-f", "--force", action="store_true", help="Force update without prompt")
    parser.add_argument("-c", "--check", action="store_true", help="Check for update and exit")
    parser.add_argument("--cli", action="store_true", help="Run in command line mode without GUI")
    parser.add_argument("--target-dir", help="Base directory of the application")
    parser.add_argument("--url", help="Override update download URL")
    
    args = parser.parse_args()
    base_dir = os.path.abspath(args.target_dir) if args.target_dir else detect_base_dir()
    
    if args.cli or args.check:
        code = run_cli(base_dir, force=args.force, custom_url=args.url, check_only=args.check)
        sys.exit(code)
    else:
        app = AutoUpdateApp(base_dir, force=args.force, custom_url=args.url)
        app.run()


if __name__ == "__main__":
    main()
