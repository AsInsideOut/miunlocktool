"""
HyperOS 1 BootLoader Bypass — GUI Panel + Backend
Based on work by MlgmXyysd (NekoYuzu) / MeowCat Studio / Meow Mobile
https://github.com/MlgmXyysd/Xiaomi-BootLoader-Bypass

Integrated into Xiaomi Unlock Tool 8.2 by Franz
"""

import os
import sys
import re
import json
import time
import hmac
import hashlib
import base64
import subprocess
import threading
import requests

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

import customtkinter as ctk

# Imports from sibling modules inside res/
try:
    from res.theme import MaterialColors, MaterialTypography, MD3Card, MD3Button, MD3Label
except ImportError:
    from theme import MaterialColors, MaterialTypography, MD3Card, MD3Button, MD3Label


# ─────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────
AES_KEY = b"20nr1aobv2xi8ax4"
AES_IV  = b"0102030405060708"
SIGN_KEY = "10f29ff413c89c8de02349cb3eb9a5f510f29ff413c89c8de02349cb3eb9a5f5"

API_GLOBAL = "https://unlock.update.intl.miui.com/v1/unlock/applyBind"
API_CHINA  = "https://unlock.update.miui.com/v1/unlock/applyBind"


# ─────────────────────────────────────────────────────────────────
#  Crypto helpers
# ─────────────────────────────────────────────────────────────────
def decrypt_data(cipher_b64: str) -> str:
    """AES-128-CBC decrypt from base64 string."""
    raw = base64.b64decode(cipher_b64)
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    plain = unpad(cipher.decrypt(raw), AES.block_size)
    return plain.decode("utf-8")


def encrypt_data(plain: str) -> str:
    """AES-128-CBC encrypt to base64 string."""
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    ct = cipher.encrypt(pad(plain.encode("utf-8"), AES.block_size))
    return base64.b64encode(ct).decode("utf-8")


def sign_data(data_encrypted: str) -> str:
    """HMAC-SHA1 signature for the API request."""
    payload = f"POST\n/v1/unlock/applyBind\ndata={data_encrypted}&sid=miui_sec_android"
    return hmac.new(
        SIGN_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha1
    ).hexdigest().lower()


# ─────────────────────────────────────────────────────────────────
#  ADB helpers
# ─────────────────────────────────────────────────────────────────
def find_adb() -> str | None:
    """Locate adb.exe: bundled in res/adb/ first, then PATH."""
    base = os.path.dirname(os.path.abspath(__file__))
    bundled = os.path.join(base, "adb", "adb.exe")
    if os.path.isfile(bundled):
        return bundled
    # Try PATH
    try:
        result = subprocess.run(
            ["where", "adb"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            first = result.stdout.strip().splitlines()[0]
            if os.path.isfile(first):
                return first
    except Exception:
        pass
    return None


def adb_devices(adb_path: str) -> list[str]:
    """Return list of connected device serials in 'device' state."""
    try:
        r = subprocess.run(
            [adb_path, "devices"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        serials = []
        for line in r.stdout.splitlines():
            line = line.strip()
            if line and not line.startswith("List") and "\tdevice" in line:
                serials.append(line.split("\t")[0])
        return serials
    except Exception:
        return []


def adb_shell(adb_path: str, cmd: str) -> str:
    """Run an adb shell command, return stdout."""
    try:
        r = subprocess.run(
            [adb_path, "shell", cmd],
            capture_output=True, text=True, timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return r.stdout.strip()
    except Exception:
        return ""


# ─────────────────────────────────────────────────────────────────
#  Response-code translation
# ─────────────────────────────────────────────────────────────────
RESPONSE_CODES = {
    0:     ("success",            "✅"),
    401:   ("credentials_expired","⚠️"),
    20086: ("device_cred_expired","⚠️"),
    30001: ("verification_forced","❌"),
    86015: ("invalid_signature",  "❌"),
}


# ─────────────────────────────────────────────────────────────────
#  Main Panel  (ctk.CTkFrame subclass)
# ─────────────────────────────────────────────────────────────────
class HyperOSBypassPanel(ctk.CTkFrame):
    """Full GUI panel for HyperOS 1 BootLoader Bypass."""

    def __init__(self, master, translation=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.tr = translation
        self.adb_path: str | None = None
        self._logcat_proc: subprocess.Popen | None = None
        self._worker_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._use_global = True  # default Global ROM

        self._build_ui()
        # Auto-detect ADB on init
        self.after(300, self._detect_adb)

    # ── translation helper ──────────────────────────────────────
    def _t(self, key: str, **fmt) -> str:
        if self.tr:
            raw = self.tr.tr(key)
            if fmt:
                try:
                    return raw.format(**fmt)
                except Exception:
                    return raw
            return raw
        return key

    # ── UI construction ─────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Top card: status + controls ─────────────────────────
        top_card = MD3Card(self, elevation=2, corner_radius=18)
        top_card.pack(fill="x", padx=4, pady=(0, 6))
        self._top_card = top_card

        # Header row
        hdr = ctk.CTkFrame(top_card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 4))

        header_bg = ctk.CTkFrame(hdr, fg_color="#202020", corner_radius=12, height=36)
        header_bg.pack(side="left")
        self._header_bg = header_bg

        MD3Label(
            header_bg,
            text=f"⚡ {self._t('bypass_panel_title')}",
            typography='title_large',
            text_color='#FFFFFF'
        ).pack(side="left", padx=12, pady=2)

        # Credit line
        credit = MD3Label(
            hdr,
            text="by MlgmXyysd (NekoYuzu) / MeowCat Studio",
            typography='body_small',
            text_color=MaterialColors.get_color('on_surface_variant')
        )
        credit.pack(side="right", padx=8)

        # ── Status row ──────────────────────────────────────────
        status_row = ctk.CTkFrame(top_card, fg_color="transparent")
        status_row.pack(fill="x", padx=16, pady=(4, 4))

        # ADB status indicator
        self._adb_indicator = ctk.CTkFrame(
            status_row, width=12, height=12, corner_radius=6,
            fg_color=MaterialColors.get_color('error')
        )
        self._adb_indicator.pack(side="left", padx=(0, 6))

        self._adb_status_label = MD3Label(
            status_row,
            text=self._t('bypass_adb_searching'),
            typography='body_medium',
            text_color=MaterialColors.get_color('on_surface_variant')
        )
        self._adb_status_label.pack(side="left")

        # Device info
        self._device_label = MD3Label(
            status_row,
            text="",
            typography='body_medium',
            text_color=MaterialColors.get_color('primary')
        )
        self._device_label.pack(side="left", padx=(16, 0))

        # ── Region selector ─────────────────────────────────────
        region_row = ctk.CTkFrame(top_card, fg_color="transparent")
        region_row.pack(fill="x", padx=16, pady=(2, 4))

        MD3Label(
            region_row,
            text=self._t('bypass_region_label'),
            typography='label_large',
            text_color=MaterialColors.get_color('on_surface')
        ).pack(side="left", padx=(0, 8))

        self._region_var = ctk.StringVar(value="Global")
        region_seg = ctk.CTkSegmentedButton(
            region_row,
            values=["Global", "China"],
            variable=self._region_var,
            command=self._on_region_change,
            font=MaterialTypography.LABEL_MEDIUM,
            fg_color=MaterialColors.get_color('surface_container_low'),
            selected_color=MaterialColors.get_color('primary'),
            selected_hover_color=MaterialColors.get_color('primary_container'),
            unselected_color=MaterialColors.get_color('surface_container'),
            unselected_hover_color=MaterialColors.get_color('surface_container_high'),
            text_color=MaterialColors.get_color('on_surface'),
            text_color_disabled=MaterialColors.get_color('on_surface_variant'),
            corner_radius=12,
            height=32
        )
        region_seg.pack(side="left")
        self._region_seg = region_seg

        # ── Step indicators ─────────────────────────────────────
        steps_frame = ctk.CTkFrame(top_card, fg_color="transparent")
        steps_frame.pack(fill="x", padx=16, pady=(4, 4))

        self._step_labels = []
        step_names = [
            self._t('bypass_step1'),
            self._t('bypass_step2'),
            self._t('bypass_step3'),
            self._t('bypass_step4'),
            self._t('bypass_step5'),
        ]
        for i, name in enumerate(step_names):
            dot = ctk.CTkFrame(
                steps_frame, width=22, height=22, corner_radius=11,
                fg_color=MaterialColors.get_color('surface_container_high'),
                border_width=1,
                border_color=MaterialColors.get_color('outline_variant')
            )
            dot.pack(side="left", padx=(0, 2))
            dot_num = ctk.CTkLabel(
                dot, text=str(i + 1), font=("Segoe UI", 10, "bold"),
                text_color=MaterialColors.get_color('on_surface_variant'),
                fg_color="transparent"
            )
            dot_num.place(relx=0.5, rely=0.5, anchor="center")

            lbl = MD3Label(
                steps_frame, text=name, typography='body_small',
                text_color=MaterialColors.get_color('on_surface_variant')
            )
            lbl.pack(side="left", padx=(2, 10))

            self._step_labels.append((dot, dot_num, lbl))

        # ── Button row ──────────────────────────────────────────
        btn_row = ctk.CTkFrame(top_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(6, 12))

        self._start_btn = MD3Button(
            btn_row,
            text=self._t('bypass_start_btn'),
            button_type='filled',
            size='medium',
            height=42,
            command=self._on_start,
            state="disabled"
        )
        self._start_btn.pack(side="left", padx=(0, 8))

        self._stop_btn = MD3Button(
            btn_row,
            text=self._t('bypass_stop_btn'),
            button_type='outlined',
            size='medium',
            height=42,
            command=self._on_stop,
            state="disabled"
        )
        self._stop_btn.pack(side="left", padx=(0, 8))

        self._refresh_btn = MD3Button(
            btn_row,
            text=self._t('bypass_refresh_btn'),
            button_type='text',
            size='small',
            height=34,
            command=self._detect_adb
        )
        self._refresh_btn.pack(side="left")

        # ── Log card (scrollable) ───────────────────────────────
        log_card = MD3Card(self, elevation=1, corner_radius=16)
        log_card.pack(fill="both", expand=True, padx=4, pady=(0, 4))
        self._log_card = log_card

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.pack(fill="x", padx=14, pady=(10, 2))

        MD3Label(
            log_header,
            text=self._t('bypass_log_title'),
            typography='title_small',
            text_color=MaterialColors.get_color('on_surface')
        ).pack(side="left")

        self._clear_btn = MD3Button(
            log_header,
            text=self._t('bypass_clear_log'),
            button_type='text',
            size='small',
            height=28,
            command=self._clear_log
        )
        self._clear_btn.pack(side="right")

        self._log_text = ctk.CTkTextbox(
            log_card,
            font=("Consolas", 12),
            fg_color=MaterialColors.get_color('surface_container_lowest'),
            text_color=MaterialColors.get_color('on_surface'),
            corner_radius=10,
            border_width=1,
            border_color=MaterialColors.get_color('outline_variant'),
            wrap="word",
            state="disabled"
        )
        self._log_text.pack(fill="both", expand=True, padx=14, pady=(2, 12))

        # Tag colors for log
        self._log_text.tag_config("info",    foreground=MaterialColors.get_color('on_surface'))
        self._log_text.tag_config("success", foreground="#4CAF50")
        self._log_text.tag_config("warning", foreground="#FFC107")
        self._log_text.tag_config("error",   foreground="#F44336")
        self._log_text.tag_config("step",    foreground=MaterialColors.get_color('primary'))
        self._log_text.tag_config("data",    foreground="#80CBC4")

    # ── Region toggle ───────────────────────────────────────────
    def _on_region_change(self, value):
        self._use_global = (value == "Global")

    # ── ADB detection ───────────────────────────────────────────
    def _detect_adb(self):
        def _do():
            path = find_adb()
            if path:
                devs = adb_devices(path)
                self.after(0, lambda: self._adb_found(path, devs))
            else:
                self.after(0, self._adb_not_found)
        threading.Thread(target=_do, daemon=True).start()

    def _adb_found(self, path, devices):
        self.adb_path = path
        self._adb_indicator.configure(fg_color="#4CAF50")
        if len(devices) == 1:
            self._adb_status_label.configure(
                text=self._t('bypass_adb_ready'),
                text_color="#4CAF50"
            )
            self._device_label.configure(
                text=f"📱 {devices[0]}",
                text_color=MaterialColors.get_color('primary')
            )
            self._start_btn.configure(state="normal")
        elif len(devices) == 0:
            self._adb_status_label.configure(
                text=self._t('bypass_no_device'),
                text_color=MaterialColors.get_color('error')
            )
            self._device_label.configure(text="")
            self._start_btn.configure(state="disabled")
        else:
            self._adb_status_label.configure(
                text=self._t('bypass_multiple_devices'),
                text_color=MaterialColors.get_color('error')
            )
            self._device_label.configure(text=f"({len(devices)})")
            self._start_btn.configure(state="disabled")

    def _adb_not_found(self):
        self.adb_path = None
        self._adb_indicator.configure(fg_color=MaterialColors.get_color('error'))
        self._adb_status_label.configure(
            text=self._t('bypass_adb_not_found'),
            text_color=MaterialColors.get_color('error')
        )
        self._start_btn.configure(state="disabled")

    # ── Step highlight ──────────────────────────────────────────
    def _set_step(self, idx: int, status: str = "active"):
        """Highlight step indicator. status: 'active', 'done', 'error', 'pending'."""
        colors = {
            "active":  (MaterialColors.get_color('primary'), '#FFFFFF'),
            "done":    ("#4CAF50", '#FFFFFF'),
            "error":   (MaterialColors.get_color('error'), '#FFFFFF'),
            "pending": (MaterialColors.get_color('surface_container_high'),
                        MaterialColors.get_color('on_surface_variant')),
        }
        bg, fg = colors.get(status, colors["pending"])
        dot, dot_num, lbl = self._step_labels[idx]
        dot.configure(fg_color=bg, border_width=0 if status != "pending" else 1)
        dot_num.configure(text_color=fg)
        if status == "active":
            lbl.configure(text_color=MaterialColors.get_color('primary'))
        elif status == "done":
            lbl.configure(text_color="#4CAF50")
        elif status == "error":
            lbl.configure(text_color=MaterialColors.get_color('error'))
        else:
            lbl.configure(text_color=MaterialColors.get_color('on_surface_variant'))

    def _reset_steps(self):
        for i in range(5):
            self._set_step(i, "pending")

    # ── Logging ─────────────────────────────────────────────────
    def _log(self, msg: str, tag: str = "info"):
        ts = time.strftime("%H:%M:%S")
        def _do():
            self._log_text.configure(state="normal")
            self._log_text.insert("end", f"[{ts}] {msg}\n", tag)
            self._log_text.see("end")
            self._log_text.configure(state="disabled")
        self.after(0, _do)

    def _clear_log(self):
        self._log_text.configure(state="normal")
        self._log_text.delete("1.0", "end")
        self._log_text.configure(state="disabled")

    # ── Start / Stop ────────────────────────────────────────────
    def _on_start(self):
        self._stop_event.clear()
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._refresh_btn.configure(state="disabled")
        self._region_seg.configure(state="disabled")
        self._reset_steps()
        self._clear_log()
        self._worker_thread = threading.Thread(target=self._run_bypass, daemon=True)
        self._worker_thread.start()

    def _on_stop(self):
        self._stop_event.set()
        self._kill_logcat()
        self._log(self._t('bypass_cancelled'), "warning")
        self._finish()

    def _finish(self):
        def _do():
            self._start_btn.configure(state="normal")
            self._stop_btn.configure(state="disabled")
            self._refresh_btn.configure(state="normal")
            self._region_seg.configure(state="normal")
        self.after(0, _do)

    def _kill_logcat(self):
        if self._logcat_proc and self._logcat_proc.poll() is None:
            try:
                self._logcat_proc.terminate()
                self._logcat_proc.wait(timeout=3)
            except Exception:
                try:
                    self._logcat_proc.kill()
                except Exception:
                    pass
        self._logcat_proc = None

    # ── Main bypass logic ───────────────────────────────────────
    def _run_bypass(self):
        adb = self.adb_path
        if not adb:
            self._log(self._t('bypass_adb_not_found'), "error")
            self._finish()
            return

        try:
            self._do_bypass(adb)
        except Exception as e:
            self._log(f"{self._t('bypass_error')}: {e}", "error")
        finally:
            self._kill_logcat()
            self._finish()

    def _do_bypass(self, adb: str):
        # ── Step 1: Check device ────────────────────────────────
        self.after(0, lambda: self._set_step(0, "active"))
        self._log(self._t('bypass_step1_checking'), "step")

        devs = adb_devices(adb)
        if self._stop_event.is_set():
            return

        if len(devs) == 0:
            self._log(self._t('bypass_no_device'), "error")
            self.after(0, lambda: self._set_step(0, "error"))
            return
        if len(devs) > 1:
            self._log(self._t('bypass_multiple_devices'), "error")
            self.after(0, lambda: self._set_step(0, "error"))
            return

        serial = devs[0]
        self._log(f"{self._t('bypass_device_serial')}: {serial}", "data")
        self.after(0, lambda: self._set_step(0, "done"))

        # ── Step 2: Prep device & open Dev Settings ─────────────
        self.after(0, lambda: self._set_step(1, "active"))
        self._log(self._t('bypass_step2_prep'), "step")

        adb_shell(adb, "svc data enable")
        self._log(self._t('bypass_data_enabled'), "info")

        adb_shell(adb, "am start -a android.settings.APPLICATION_DEVELOPMENT_SETTINGS")
        self._log(self._t('bypass_dev_settings_opened'), "info")

        self.after(0, lambda: self._set_step(1, "done"))

        # ── Step 3: Listen logcat ───────────────────────────────
        self.after(0, lambda: self._set_step(2, "active"))
        self._log(self._t('bypass_step3_waiting'), "step")
        self._log(self._t('bypass_click_add_device'), "warning")

        # Clear logcat first
        subprocess.run(
            [adb, "logcat", "-c"],
            capture_output=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        self._logcat_proc = subprocess.Popen(
            [adb, "logcat", "*:S", "CloudDeviceStatus:V"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        args_raw = None
        headers_raw = None

        for line in iter(self._logcat_proc.stdout.readline, ''):
            if self._stop_event.is_set():
                return

            line = line.strip()
            if not line:
                continue

            # Capture args
            m_args = re.search(r"CloudDeviceStatus:\s*args:(.*)", line)
            if m_args and args_raw is None:
                args_raw = m_args.group(1).strip()
                self._log(self._t('bypass_args_captured'), "data")
                # Immediately disable data to block the original request
                adb_shell(adb, "svc data disable")
                self._log(self._t('bypass_data_disabled'), "info")

            # Capture headers
            m_hdrs = re.search(r"CloudDeviceStatus:\s*headers:(.*)", line)
            if m_hdrs and headers_raw is None:
                headers_raw = m_hdrs.group(1).strip()
                self._log(self._t('bypass_headers_captured'), "data")

            if args_raw and headers_raw:
                break

        self._kill_logcat()

        if not args_raw or not headers_raw:
            self._log(self._t('bypass_capture_failed'), "error")
            self.after(0, lambda: self._set_step(2, "error"))
            adb_shell(adb, "svc data enable")
            return

        self.after(0, lambda: self._set_step(2, "done"))

        # ── Step 4: Decrypt, patch, sign ────────────────────────
        self.after(0, lambda: self._set_step(3, "active"))
        self._log(self._t('bypass_step4_patching'), "step")

        try:
            args_dec = decrypt_data(args_raw)
        except Exception as e:
            self._log(f"{self._t('bypass_decrypt_error')}: {e}", "error")
            self.after(0, lambda: self._set_step(3, "error"))
            adb_shell(adb, "svc data enable")
            return

        self._log(f"{self._t('bypass_decrypted_ok')}", "data")

        data = json.loads(args_dec)
        original_rom = data.get("rom_version", "")
        # Replace V816 (HyperOS identifier) with V14 (MIUI identifier)
        data["rom_version"] = original_rom.replace("V816", "V14")
        self._log(f"rom_version: {original_rom} → {data['rom_version']}", "data")

        patched_json = json.dumps(data, separators=(',', ':'))
        data_enc = encrypt_data(patched_json)
        self._log(self._t('bypass_data_encrypted'), "data")

        signature = sign_data(data_enc)
        self._log(f"{self._t('bypass_signature')}: {signature[:20]}…", "data")

        # Decrypt headers and extract cookie
        try:
            headers_dec = decrypt_data(headers_raw)
        except Exception as e:
            self._log(f"{self._t('bypass_headers_decrypt_error')}: {e}", "error")
            self.after(0, lambda: self._set_step(3, "error"))
            adb_shell(adb, "svc data enable")
            return

        cookie = ""
        # Try JSON format: {"Cookie": "..."}
        try:
            h_json = json.loads(headers_dec)
            if isinstance(h_json, dict):
                cookie = h_json.get("Cookie", "")
        except (json.JSONDecodeError, ValueError):
            pass
        # Try Cookie=[...] format
        if not cookie:
            m_ck = re.search(r"Cookie=\[(.+?)\]", headers_dec)
            if m_ck:
                cookie = m_ck.group(1).strip()

        self._log(f"{self._t('bypass_cookie_extracted')}: {cookie[:40]}…" if cookie else self._t('bypass_no_cookie'), "data")

        # Determine API endpoint
        region = data.get("region", "")
        if not self._use_global or region == "CN":
            url = API_CHINA
        else:
            url = API_GLOBAL
        self._log(f"API: {url}", "data")

        self.after(0, lambda: self._set_step(3, "done"))

        # ── Step 5: Send request ────────────────────────────────
        self.after(0, lambda: self._set_step(4, "active"))
        self._log(self._t('bypass_step5_sending'), "step")

        # Re-enable data for sending
        adb_shell(adb, "svc data enable")
        self._log(self._t('bypass_data_enabled'), "info")

        time.sleep(3)  # Give a moment for data to come up

        if self._stop_event.is_set():
            return

        try:
            resp = requests.post(
                url,
                data={
                    "data": data_enc,
                    "sid": "miui_sec_android",
                    "sign": signature,
                },
                headers={
                    "Cookie": cookie,
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=15,
                verify=False
            )
            resp_json = resp.json()
        except Exception as e:
            self._log(f"{self._t('bypass_request_failed')}: {e}", "error")
            self.after(0, lambda: self._set_step(4, "error"))
            return

        self._log(f"{self._t('bypass_response')}: {json.dumps(resp_json, ensure_ascii=False)}", "data")

        code = resp_json.get("code", -1)
        info = RESPONSE_CODES.get(code, ("unknown_code", "❓"))
        key, emoji = info

        if code == 0:
            user_id = resp_json.get("data", {}).get("userId", "?")
            self._log(f"{emoji} {self._t('bypass_success')} (userId: {user_id})", "success")
            self.after(0, lambda: self._set_step(4, "done"))
        else:
            desc_en = resp_json.get("descEN", "")
            msg = self._t(f'bypass_code_{key}') if self.tr else key
            self._log(f"{emoji} {msg} ({code}) {desc_en}", "error" if "❌" in emoji else "warning")
            self.after(0, lambda: self._set_step(4, "error"))

    # ── Cleanup on destroy ──────────────────────────────────────
    def destroy(self):
        self._stop_event.set()
        self._kill_logcat()
        super().destroy()
