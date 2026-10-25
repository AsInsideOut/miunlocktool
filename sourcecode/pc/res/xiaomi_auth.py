import os
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




class XiaomiAuthPanel(MD3Card):
    """
    Встроенная в интерфейс панель авторизации Xiaomi Account.
    Отображается в правой колонке вместо Лога выполнения.
    """

    LONGPOLLING_URL = "https://account.xiaomi.com/longPolling/loginUrl"
    SERVICELOGIN_URL = "https://account.xiaomi.com/pass/serviceLogin"
    SID = "18n_bbs_global"
    CALLBACK_URL = "https://sgp-api.buy.mi.com/bbs/api/global/user/login-back"

    def __init__(self, master, translation, config, on_close=None, on_success=None, app=None, **kwargs):
        kwargs.setdefault('elevation', 2)
        kwargs.setdefault('corner_radius', 18)
        super().__init__(master, **kwargs)

        self.translation = translation
        self.config = config
        self.on_close = on_close
        self.on_success = on_success
        self.app = app

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

        self._create_ui()
        self._start_qr_process()

    def _on_close_clicked(self):
        self.stop()
        if self.on_close:
            self.on_close()

    def stop(self):
        self.closed = True

    def reset(self):
        self.closed = False
        self.success = False
        self.token = None
        if hasattr(self, 'qr_status_var'):
            self.qr_status_var.set(self.translation.tr('login_waiting'))
        if hasattr(self, 'qr_label') and self.qr_label.winfo_exists():
            self.qr_label.configure(image="", text=self.translation.tr('login_loading_qr'))
        self._start_qr_process()

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

    def update_ui_text(self):
        tr = self.translation.tr
        if hasattr(self, 'title_label') and self.title_label and self.title_label.winfo_exists():
            self.title_label.configure(text=f"🔐 {tr('login_title')}")
        if hasattr(self, 'close_btn') and self.close_btn and self.close_btn.winfo_exists():
            self.close_btn.configure(text=f"✕ {tr('close_btn')}")
        if hasattr(self, 'qr_tip_label') and self.qr_tip_label and self.qr_tip_label.winfo_exists():
            self.qr_tip_label.configure(text=tr('login_qr_scan_tip'))
        if hasattr(self, 'browser_btn') and self.browser_btn and self.browser_btn.winfo_exists():
            self.browser_btn.configure(text=tr('login_open_browser_btn'))
        if hasattr(self, 'refresh_btn') and self.refresh_btn and self.refresh_btn.winfo_exists():
            self.refresh_btn.configure(text=tr('login_refresh_qr'))
        if hasattr(self, 'saved_session_title') and self.saved_session_title and self.saved_session_title.winfo_exists():
            self.saved_session_title.configure(text=tr('login_existing_found'))
        if hasattr(self, 'use_existing_btn') and self.use_existing_btn and self.use_existing_btn.winfo_exists():
            self.use_existing_btn.configure(text=tr('login_use_existing_btn'))
        if hasattr(self, 'qr_status_var') and not self.login_url:
            self.qr_status_var.set(tr('login_waiting'))

        # Update tab selector values and re-map frames
        if hasattr(self, 'tab_selector') and self.tab_selector and self.tab_selector.winfo_exists():
            new_tabs = [tr('login_tab_qr')]
            if self.saved_session_info:
                new_tabs.append(tr('login_tab_existing'))
            old_frames = list(self.tab_frames.values())
            self.tab_frames = {}
            for i, val in enumerate(new_tabs):
                if i < len(old_frames):
                    self.tab_frames[val] = old_frames[i]
            cur_val = self.tab_selector.get()
            is_second = (len(new_tabs) > 1 and cur_val != new_tabs[0])
            self.tab_selector.configure(values=new_tabs)
            target_val = new_tabs[1] if is_second else new_tabs[0]
            self.tab_selector.set(target_val)
            self._switch_tab(target_val)

    def _detect_saved_session(self):
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
        dark_mode = True

        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=46)
        header_frame.pack(fill="x", padx=18, pady=(12, 0))
        header_frame.pack_propagate(False)

        header_label_bg = ctk.CTkFrame(
            header_frame,
            fg_color='#202020',
            corner_radius=6,
            border_width=0,
            height=34
        )
        header_label_bg.pack(side="left")

        self.title_label = MD3Label(
            header_label_bg,
            text=f"🔐 {self.translation.tr('login_title')}",
            typography='title_large',
            text_color='#FFFFFF'
        )
        self.title_label.pack(side="left", padx=12, pady=2)

        self.close_btn_bg = ctk.CTkFrame(
            header_frame,
            fg_color='#202020',
            corner_radius=12,
            border_width=0,
            height=36
        )
        self.close_btn_bg.pack(side="right")

        self.close_btn = MD3Button(
            self.close_btn_bg,
            text=f"✕ {self.translation.tr('close_btn')}",
            button_type='text',
            size='small',
            command=self._on_close_clicked,
            corner_radius=12
        )
        self.close_btn.pack(fill="both", expand=True, padx=0, pady=0)
        self._setup_hover_outline(self.close_btn)

        tab_values = [self.translation.tr('login_tab_qr')]
        if self.saved_session_info:
            tab_values.append(self.translation.tr('login_tab_existing'))

        if len(tab_values) > 1:
            self.tab_selector = ctk.CTkSegmentedButton(
                self,
                values=tab_values,
                command=self._switch_tab,
                font=MaterialTypography.LABEL_MEDIUM,
                height=34,
                corner_radius=10,
                selected_color=MaterialColors.get_color('primary', dark_mode),
                selected_hover_color=MaterialColors.get_color('primary_container', dark_mode)
            )
            self.tab_selector.pack(fill="x", padx=18, pady=(4, 2))
        else:
            self.tab_selector = None

        self.content_container = ctk.CTkFrame(
            self,
            fg_color=MaterialColors.get_color('surface_container_lowest', dark_mode),
            corner_radius=8,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant', dark_mode)
        )
        self.content_container.pack(fill="both", expand=True, padx=18, pady=(8, 12))

        self.tab_frames = {}
        self._build_qr_tab()
        if self.saved_session_info:
            self._build_saved_session_tab()

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

    def _build_qr_tab(self):
        dark_mode = True
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_frames[self.translation.tr('login_tab_qr')] = frame

        center_box = ctk.CTkFrame(frame, fg_color="transparent", width=280)
        center_box.pack(anchor="center", expand=True, padx=12, pady=10)

        self.qr_tip_label = MD3Label(
            center_box,
            text=self.translation.tr('login_qr_scan_tip'),
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant', dark_mode),
            justify="center"
        )
        self.qr_tip_label.pack(pady=(0, 4))

        self.qr_display_frame = ctk.CTkFrame(
            center_box,
            width=200,
            height=200,
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

        self.qr_status_var = ctk.StringVar(value=self.translation.tr('login_waiting'))
        self.qr_status_label = MD3Label(
            center_box,
            textvariable=self.qr_status_var,
            typography='body_small',
            justify="center"
        )
        self.qr_status_label.pack(pady=(4, 6))

        btn_row = ctk.CTkFrame(center_box, fg_color="transparent", width=280)
        btn_row.pack(fill="x", pady=(4, 0))

        self.browser_btn = MD3Button(
            btn_row,
            text=self.translation.tr('login_open_browser_btn'),
            button_type='filled',
            size='small',
            height=34,
            command=self._open_in_browser
        )
        self.browser_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.refresh_btn = MD3Button(
            btn_row,
            text=self.translation.tr('login_refresh_qr'),
            button_type='tonal',
            size='small',
            height=34,
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
            try:
                from PIL import Image, ImageTk
                import io
                img = Image.open(io.BytesIO(img_bytes)).resize((188, 188), Image.Resampling.LANCZOS)
                self.qr_image_tk = ImageTk.PhotoImage(img)
            except Exception:
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
        if hasattr(self, 'existing_status_var'):
            self.existing_status_var.set(self.translation.tr('login_success'))
        if self.on_success:
            self.on_success(self.token)

    def _build_saved_session_tab(self):
        dark_mode = True
        frame = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.tab_frames[self.translation.tr('login_tab_existing')] = frame

        center_box = ctk.CTkFrame(frame, fg_color="transparent", width=280)
        center_box.pack(anchor="center", expand=True, padx=12, pady=16)

        check_icon = ctk.CTkLabel(
            center_box,
            text="⚡",
            font=("Segoe UI", 42),
            text_color=MaterialColors.get_color('primary', dark_mode)
        )
        check_icon.pack(pady=(4, 6))

        self.saved_session_title = MD3Label(
            center_box,
            text=self.translation.tr('login_existing_found'),
            typography='title_medium',
            justify="center"
        )
        self.saved_session_title.pack(pady=(0, 4))

        user_id = self.saved_session_info[1].get("userId", "Unknown")
        sub_dir = self.saved_session_info[0]

        self.saved_session_id_label = MD3Label(
            center_box,
            text=f"Xiaomi ID: {user_id} ({sub_dir})",
            typography='body_medium',
            text_color=MaterialColors.get_color('primary', dark_mode),
            justify="center"
        )
        self.saved_session_id_label.pack(pady=(0, 14))

        self.existing_status_var = ctk.StringVar(value="")
        self.existing_status_label = MD3Label(
            center_box,
            textvariable=self.existing_status_var,
            typography='body_small',
            justify="center"
        )
        self.existing_status_label.pack(pady=(0, 10))

        self.use_existing_btn = MD3Button(
            center_box,
            text=self.translation.tr('login_use_existing_btn'),
            button_type='filled',
            size='large',
            height=40,
            command=self._extract_from_saved_session
        )
        self.use_existing_btn.pack(fill="x", pady=(0, 8))

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
                    self.after(0, self._on_login_success)
                else:
                    self.after(0, lambda: self.existing_status_var.set(self.translation.tr('login_token_extract_error')))
                    self.after(0, lambda: self.use_existing_btn.configure(state="normal"))

            except Exception as e:
                self.after(0, lambda err=str(e): self.existing_status_var.set(self.translation.tr('login_error').format(err)))
                self.after(0, lambda: self.use_existing_btn.configure(state="normal"))

        threading.Thread(target=worker, daemon=True).start()