import os
import sys
import json
import time
import base64
import hashlib
import threading
import webbrowser
from urllib.parse import quote
from pathlib import Path
import tkinter as tk

import requests
import customtkinter as ctk

try:
    from theme import MD3Card, MD3Label, MD3Button, MaterialColors, MaterialTypography
except ImportError:
    try:
        from .theme import MD3Card, MD3Label, MD3Button, MaterialColors, MaterialTypography
    except (ImportError, ValueError):
        from res.theme import MD3Card, MD3Label, MD3Button, MaterialColors, MaterialTypography


class XiaomiAuthDialog(ctk.CTkToplevel):
    """
    Диалоговое окно авторизации в Xiaomi Account с автоматическим
    извлечением new_bbs_serviceToken.
    
    Поддерживает:
    1. Использование уже сохраненной сессии Mi Account на ПК (в 1 клик).
    2. Вход по QR-коду (сканирование камерой или приложением Mi Community).
    3. Вход через системный веб-браузер (официальный вход на account.xiaomi.com).
    """

    LONGPOLLING_URL = "https://account.xiaomi.com/longPolling/loginUrl"
    SERVICELOGIN_URL = "https://account.xiaomi.com/pass/serviceLogin"
    SID = "18n_bbs_global"
    CALLBACK_URL = "https://sgp-api.buy.mi.com/bbs/api/global/user/login-back"

    def __init__(self, parent, translation, config):
        super().__init__(parent)
        self.parent = parent
        self.translation = translation
        self.config = config

        self.title(self.translation.tr('login_title'))
        self.geometry("480x590")
        self.minsize(460, 560)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        self.token = None
        self.success = False
        self.error_message = None
        self.closed = False

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json;charset=UTF-8",
        })

        self.qr_image_tk = None
        self.lp_url = None
        self.login_url = None
        self.qr_timeout = 300
        self.polling_thread = None

        self.saved_session_info = self._detect_saved_session()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_ui()

        self.update_idletasks()
        try:
            x = self.parent.winfo_x() + (self.parent.winfo_width() - self.winfo_width()) // 2
            y = self.parent.winfo_y() + (self.parent.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
        except Exception:
            pass

        # Запускаем генерацию QR-кода по умолчанию
        self._start_qr_process()

    def _on_close(self):
        self.closed = True
        self.destroy()

    def _detect_saved_session(self):
        """Проверяет наличие ранее сохраненной сессии Mi Account"""
        base = Path.home() / ".migatesession"
        if not base.exists():
            return None
        for sub in ["unlockApi", "18n_bbs_global", "passport"]:
            f = base / sub / "session.json"
            if f.exists():
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        if data.get("passToken") and data.get("userId"):
                            return sub, data
                except Exception:
                    pass
        return None

    def _create_ui(self):
        dark_mode = ctk.get_appearance_mode() == "Dark"
        bg_color = MaterialColors.get_color('background', dark_mode)

        self.configure(fg_color=bg_color)

        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=16)

        # Header
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 12))

        header_icon = ctk.CTkLabel(
            header_frame,
            text="🔐",
            font=("Segoe UI", 24)
        )
        header_icon.pack(side="left", padx=(0, 10))

        header_text_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_text_frame.pack(side="left", fill="x", expand=True)

        title_label = MD3Label(
            header_text_frame,
            text=self.translation.tr('login_title'),
            typography='title_large'
        )
        title_label.pack(anchor="w")

        subtitle_label = MD3Label(
            header_text_frame,
            text=self.translation.tr('login_subtitle'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant', dark_mode)
        )
        subtitle_label.pack(anchor="w")

        # Навигация между методами входа (только если найдена сохраненная сессия)
        tab_values = [self.translation.tr('login_tab_qr')]
        if self.saved_session_info:
            tab_values.append(self.translation.tr('login_tab_existing'))

        if len(tab_values) > 1:
            self.tab_selector = ctk.CTkSegmentedButton(
                self.main_frame,
                values=tab_values,
                command=self._switch_tab,
                font=MaterialTypography.LABEL_MEDIUM,
                height=36,
                corner_radius=10,
                selected_color=MaterialColors.get_color('primary', dark_mode),
                selected_hover_color=MaterialColors.get_color('primary_container', dark_mode)
            )
            self.tab_selector.pack(fill="x", pady=(0, 12))
        else:
            self.tab_selector = None

        # Bottom Frame (docked at bottom)
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=(10, 0))

        close_btn = MD3Button(
            bottom_frame,
            text=self.translation.tr('close_btn'),
            button_type='outlined',
            size='medium',
            height=36,
            command=self._on_close
        )
        close_btn.pack(side="right")

        # Контейнер для содержимого табов
        self.content_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_container.pack(fill="both", expand=True)

        self.tab_frames = {}

        # 1. QR-код и браузер
        self._build_qr_tab()

        # 2. Сохраненная сессия (если есть)
        if self.saved_session_info:
            self._build_saved_session_tab()

        # По умолчанию показываем QR-код и вход через браузер
        initial_tab = self.translation.tr('login_tab_qr')
        if self.tab_selector:
            self.tab_selector.set(initial_tab)
        self._switch_tab(initial_tab)

    def _switch_tab(self, tab_name):
        for name, frame in self.tab_frames.items():
            if name == tab_name:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

    # ==================== ТАБ 1: QR-КОД И БРАУЗЕР ====================
    def _build_qr_tab(self):
        dark_mode = ctk.get_appearance_mode() == "Dark"
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_frames[self.translation.tr('login_tab_qr')] = frame

        card = MD3Card(frame, elevation=1)
        card.pack(fill="both", expand=True)
        card.configure(corner_radius=14)

        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="both", expand=True, padx=16, pady=10)

        tip_label = MD3Label(
            card_inner,
            text=self.translation.tr('login_qr_scan_tip'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant', dark_mode),
            justify="center"
        )
        tip_label.pack(pady=(0, 4))

        # QR Code Display
        self.qr_display_frame = ctk.CTkFrame(
            card_inner,
            width=260,
            height=260,
            fg_color=MaterialColors.get_color('surface_container_low', dark_mode),
            corner_radius=12
        )
        self.qr_display_frame.pack(pady=4)
        self.qr_display_frame.pack_propagate(False)

        self.qr_label = tk.Label(
            self.qr_display_frame,
            bg="#FFFFFF",
            text=self.translation.tr('login_loading_qr'),
            font=("Arial", 11)
        )
        self.qr_label.pack(fill="both", expand=True, padx=6, pady=6)

        # Status Label
        self.qr_status_var = ctk.StringVar(value=self.translation.tr('login_waiting'))
        self.qr_status_label = MD3Label(
            card_inner,
            textvariable=self.qr_status_var,
            typography='body_small',
            justify="center"
        )
        self.qr_status_label.pack(pady=(4, 6))

        # Buttons Row
        btn_row = ctk.CTkFrame(card_inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(2, 0))

        self.browser_btn = MD3Button(
            btn_row,
            text=self.translation.tr('login_open_browser_btn'),
            button_type='filled',
            size='medium',
            height=36,
            command=self._open_in_browser
        )
        self.browser_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.refresh_btn = MD3Button(
            btn_row,
            text=self.translation.tr('login_refresh_qr'),
            button_type='tonal',
            size='medium',
            height=36,
            command=self._reload_qr
        )
        self.refresh_btn.pack(side="right")

    def _open_in_browser(self):
        if self.login_url:
            webbrowser.open(self.login_url)
            self.qr_status_var.set(self.translation.tr('login_browser_opened'))

    def _reload_qr(self):
        self.qr_status_var.set(self.translation.tr('login_refreshing_qr'))
        self.qr_label.configure(image="", text=self.translation.tr('login_loading_qr'))
        self._start_qr_process()

    def _start_qr_process(self):
        def worker():
            try:
                params = {
                    "sid": self.SID,
                    "_json": "false",
                    "callback": self.CALLBACK_URL
                }
                resp = self.session.get(self.LONGPOLLING_URL, params=params, timeout=12)
                text = resp.text
                if text.startswith("&&&START&&&"):
                    text = text[11:]
                data = json.loads(text)

                self.login_url = data.get("loginUrl")
                self.lp_url = data.get("lp")
                self.qr_timeout = data.get("timeout", 300)
                qr_img_url = data.get("qr")

                if qr_img_url and not self.closed:
                    r_img = self.session.get(qr_img_url, timeout=12)
                    if r_img.status_code == 200:
                        self.after(0, lambda b=r_img.content: self._render_qr_image(b))

                if self.lp_url and not self.closed:
                    self._start_polling_thread()

            except Exception as e:
                if not self.closed:
                    self.after(0, lambda err=str(e): self.qr_status_var.set(self.translation.tr('login_qr_fetch_error').format(err)))

        threading.Thread(target=worker, daemon=True).start()

    def _render_qr_image(self, img_bytes):
        if self.closed:
            return
        try:
            self.qr_image_tk = tk.PhotoImage(data=img_bytes)
            self.qr_label.configure(image=self.qr_image_tk, text="")
            self.qr_status_var.set(self.translation.tr('login_waiting'))
        except Exception as e:
            self.qr_label.configure(text=self.translation.tr('login_qr_fetch_error').format(e))

    def _start_polling_thread(self):
        def poll_worker():
            start_time = time.time()
            while not self.closed and (time.time() - start_time < self.qr_timeout):
                try:
                    resp = self.session.get(self.lp_url, timeout=40)
                    if resp.status_code == 200:
                        text = resp.text
                        if text.startswith("&&&START&&&"):
                            text = text[11:]
                        data = json.loads(text)
                        code = data.get("code")

                        if code == 0:
                            # Успешная авторизация!
                            self.after(0, lambda: self.qr_status_var.set(self.translation.tr('login_authorized_extracting')))
                            self._process_successful_auth(data)
                            return
                        elif code in (70016, 87001):
                            self.after(0, lambda: self.qr_status_var.set(f"Status: {data.get('description', code)}"))
                except requests.exceptions.Timeout:
                    continue
                except Exception as e:
                    if not self.closed:
                        time.sleep(2)
                    continue

            if not self.closed and not self.success:
                self.after(0, lambda: self.qr_status_var.set(self.translation.tr('login_qr_expired')))

        self.polling_thread = threading.Thread(target=poll_worker, daemon=True)
        self.polling_thread.start()

    def _process_successful_auth(self, auth_data):
        """Завершает процесс входа и получает new_bbs_serviceToken"""
        def worker():
            try:
                cookies = self.session.cookies.get_dict()
                nonce = auth_data.get("nonce")
                ssecurity = auth_data.get("ssecurity")
                location = auth_data.get("location")

                if location and nonce and ssecurity:
                    client_sign = quote(base64.b64encode(
                        hashlib.sha1(f"nonce={nonce}&{ssecurity}".encode()).digest()
                    ))
                    final_url = f"{location}&clientSign={client_sign}"
                    self.session.get(final_url, allow_redirects=True, timeout=15)
                else:
                    params = {"sid": self.SID, "_json": "true"}
                    resp = self.session.get(self.SERVICELOGIN_URL, params=params, timeout=12)
                    text = resp.text
                    if text.startswith("&&&START&&&"):
                        text = text[11:]
                    res_json = json.loads(text)
                    nonce = res_json.get("nonce")
                    ssecurity = res_json.get("ssecurity")
                    location = res_json.get("location")

                    if nonce and ssecurity and location:
                        client_sign = quote(base64.b64encode(
                            hashlib.sha1(f"nonce={nonce}&{ssecurity}".encode()).digest()
                        ))
                        final_url = f"{location}&clientSign={client_sign}"
                        self.session.get(final_url, allow_redirects=True, timeout=15)

                token = self.session.cookies.get("new_bbs_serviceToken") or self.session.cookies.get("serviceToken")
                if token:
                    self._save_session_cache(cookies)
                    self.token = token
                    self.success = True
                    self.after(0, self._on_login_success)
                else:
                    self.after(0, lambda: self.qr_status_var.set(self.translation.tr('login_token_extract_error')))

            except Exception as e:
                self.after(0, lambda err=str(e): self.qr_status_var.set(self.translation.tr('login_error').format(err)))

        threading.Thread(target=worker, daemon=True).start()

    def _save_session_cache(self, cookies):
        try:
            required = {"deviceId", "passToken", "userId"}
            if required.issubset(cookies.keys()):
                save_dir = Path.home() / ".migatesession" / self.SID
                save_dir.mkdir(parents=True, exist_ok=True)
                with open(save_dir / "session.json", "w", encoding="utf-8") as f:
                    json.dump({k: cookies[k] for k in required}, f)
        except Exception:
            pass

    def _on_login_success(self):
        self.qr_status_var.set(self.translation.tr('login_success'))
        self.after(600, self.destroy)

    # ==================== ТАБ 2: СОХРАНЕННАЯ СЕССИЯ ====================
    def _build_saved_session_tab(self):
        dark_mode = ctk.get_appearance_mode() == "Dark"
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_frames[self.translation.tr('login_tab_existing')] = frame

        card = MD3Card(frame, elevation=1)
        card.pack(fill="both", expand=True)
        card.configure(corner_radius=14)

        card_inner = ctk.CTkFrame(card, fg_color="transparent")
        card_inner.pack(fill="both", expand=True, padx=20, pady=24)

        check_icon = ctk.CTkLabel(
            card_inner,
            text="⚡",
            font=("Segoe UI", 48),
            text_color=MaterialColors.get_color('primary', dark_mode)
        )
        check_icon.pack(pady=(10, 10))

        title = MD3Label(
            card_inner,
            text=self.translation.tr('login_existing_found'),
            typography='title_medium',
            justify="center"
        )
        title.pack(pady=(0, 6))

        user_id = self.saved_session_info[1].get("userId", "Unknown")
        sub_dir = self.saved_session_info[0]

        id_label = MD3Label(
            card_inner,
            text=f"Xiaomi ID: {user_id} ({sub_dir})",
            typography='body_medium',
            text_color=MaterialColors.get_color('primary', dark_mode),
            justify="center"
        )
        id_label.pack(pady=(0, 20))

        self.existing_status_var = ctk.StringVar(value="")
        self.existing_status_label = MD3Label(
            card_inner,
            textvariable=self.existing_status_var,
            typography='body_small',
            justify="center"
        )
        self.existing_status_label.pack(pady=(0, 14))

        self.use_existing_btn = MD3Button(
            card_inner,
            text=self.translation.tr('login_use_existing_btn'),
            button_type='filled',
            size='large',
            height=44,
            command=self._extract_from_saved_session
        )
        self.use_existing_btn.pack(fill="x", pady=(0, 12))

    def _extract_from_saved_session(self):
        self.use_existing_btn.configure(state="disabled")
        self.existing_status_var.set(self.translation.tr('login_extracting_token'))

        def worker():
            try:
                auth_cookies = self.saved_session_info[1]
                for k, v in auth_cookies.items():
                    self.session.cookies.set(k, v)

                params = {"sid": self.SID, "_json": "true"}
                resp = self.session.get(self.SERVICELOGIN_URL, params=params, timeout=12)
                text = resp.text
                if text.startswith("&&&START&&&"):
                    text = text[11:]
                res_json = json.loads(text)

                if res_json.get("code") != 0:
                    err = res_json.get("description") or res_json.get("desc") or self.translation.tr('login_session_expired')
                    self.after(0, lambda: self.existing_status_var.set(self.translation.tr('login_error').format(err)))
                    self.after(0, lambda: self.use_existing_btn.configure(state="normal"))
                    return

                nonce = res_json.get("nonce")
                ssecurity = res_json.get("ssecurity")
                location = res_json.get("location")

                if nonce and ssecurity and location:
                    client_sign = quote(base64.b64encode(
                        hashlib.sha1(f"nonce={nonce}&{ssecurity}".encode()).digest()
                    ))
                    final_url = f"{location}&clientSign={client_sign}"
                    self.session.get(final_url, allow_redirects=True, timeout=15)

                token = self.session.cookies.get("new_bbs_serviceToken") or self.session.cookies.get("serviceToken")
                if token:
                    self.token = token
                    self.success = True
                    self.after(0, lambda: self.existing_status_var.set(self.translation.tr('login_success')))
                    self.after(600, self.destroy)
                else:
                    self.after(0, lambda: self.existing_status_var.set(self.translation.tr('login_token_extract_error')))
                    self.after(0, lambda: self.use_existing_btn.configure(state="normal"))

            except Exception as e:
                self.after(0, lambda err=str(e): self.existing_status_var.set(self.translation.tr('login_error').format(err)))
                self.after(0, lambda: self.use_existing_btn.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()