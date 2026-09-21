from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import os
import random
import socket
import struct
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# Enable ANSI escape sequences and UTF-8 on Windows terminal
if sys.platform == "win32":
    os.system("")
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

VERSION = "8.0"
API_HOST = "sgp-api.buy.mi.com"
STATUS_URL = f"https://{API_HOST}/bbs/api/global/user/bl-switch/state"
APPLY_URL = f"https://{API_HOST}/bbs/api/global/apply/bl-auth"
PING_HOSTS = ["sgp-api.buy.mi.com", "api.buy.mi.com", "account.xiaomi.com"]
NTP_SERVERS = [
    "time1.google.com", "time2.google.com", "time3.google.com",
    "time4.google.com", "time.android.com", "time.aws.com",
    "time.google.com", "time.cloudflare.com", "ntp.time.in.ua",
    "stratum1.net", "ntp5.stratum2.ru",
]

# Standalone CLI config location
CLI_CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "xiaomi-unlock-tool"
CLI_CONFIG_FILE = CLI_CONFIG_DIR / "config.json"

# Desktop 8.0 config location (for cross-compatibility)
if os.name == "nt":
    DESKTOP_CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "MiUnlockTool"
else:
    DESKTOP_CONFIG_DIR = Path.home() / ".config" / "MiUnlockTool"
DESKTOP_CONFIG_FILE = DESKTOP_CONFIG_DIR / "config.json"


def detect_language() -> str:
    lang = os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES") or os.environ.get("LANG") or ""
    lang = lang.lower()
    return "ru" if lang.startswith("ru") else "en"


TEXT = {
    "ru": {
        "title": "Xiaomi Unlock Tool 8.0",
        "tab_settings": "Настройки",
        "tab_submit": "Подача заявки",
        "tab_miunlock": "Mi Unlock",
        "back": "Назад",
        "select_tab": "Выберите вкладку: ",
        "settings_token": "ServiceToken",
        "settings_language": "Язык",
        "settings_check": "Проверка статуса перед заявкой",
        "settings_config": "Файл конфигурации",
        "settings_desktop_config": "Конфиг Desktop 8.0",
        "settings_ping": "Проверить соединение с Xiaomi API",
        "settings_set_token": "Изменить ServiceToken",
        "settings_toggle_check": "Переключить проверку статуса",
        "submit_run": "Подать заявку (Авторежим #2)",
        "submit_status": "Проверить статус аккаунта",
        "submit_ping": "Ping Xiaomi API",
        "mi_install_run": "Установить / запустить Mi Unlock",
        "mi_status": "Проверить установку Mi Unlock",
        "mi_note": "Mi Unlock запускается через пакет Python `miunlock`.",
        "mi_python": "Python",
        "mi_package": "Пакет miunlock",
        "installed": "установлен",
        "not_installed": "не установлен",
        "python_not_found": "Python не найден.",
        "mi_installing": "Устанавливаю пакет miunlock...",
        "mi_install_failed": "Не удалось установить пакет miunlock.",
        "mi_launching": "Запускаю Mi Unlock...",
        "mi_launch_failed": "Не удалось запустить Mi Unlock: {error}",
        "menu_apply": "Подать заявку",
        "menu_status": "Проверить статус аккаунта",
        "menu_ping": "Ping Xiaomi API",
        "menu_token": "Установить ServiceToken",
        "menu_settings": "Настройки",
        "menu_exit": "Выход",
        "choose": "Выберите: ",
        "token_prompt": "New_bbs_ServiceToken: ",
        "token_empty": "Cookie/token не указан.",
        "checking": "Проверка токена и статуса аккаунта...",
        "cookie_bad": "Cookie устарел или недействителен (100004).",
        "ready": "Аккаунт готов к подаче заявки.",
        "blocked": "Аккаунт заблокирован до: {value}",
        "not_ready": "Аккаунт ещё не готов (менее 30 дней в Mi Community).",
        "approved": "Аккаунт уже одобрен. Дата: {value}",
        "unknown_status": "Неизвестный статус. code={code}, data={data}",
        "wait": "Ожидание 23:59:59 по Пекину ({seconds:.1f} сек.)...",
        "reached": "Время 23:59:59 по Пекину достигнуто. Отправка пакета запросов (Авторежим #2)...",
        "interrupted": "Процесс прерван пользователем.",
        "saved": "ServiceToken сохранён.",
        "not_saved": "Пустой токен не сохранён.",
        "status_fail": "Проверка статуса не пройдена. Заявка не отправлена.",
        "skip": "Проверка статуса отключена.",
        "done": "Завершено. Успешных ответов: {success}/{total}",
        "apply": "{label}: заявка одобрена! (код: {code})",
        "not_submitted": "{label}: заявка не отправлена. Повторить можно: {value}",
        "maybe_approved": "{label}: сервер сообщает, что заявка, возможно, одобрена (100003).",
        "rejected": "{label}: запрос отклонён сервером (100001 - лимит квоты исчерпан).",
        "unknown_response": "{label}: ответ: {result}",
        "bad_json": "Сервер вернул некорректный JSON.",
        "bad_json_label": "{label}: сервер вернул некорректный JSON.",
        "request_error": "Ошибка запроса: {error}",
        "ntp": "NTP: {server}",
        "beijing": "Время Пекина: {value} (UTC+8)",
        "ntp_fail": "Не удалось подключиться ни к одному NTP-серверу.",
        "ping_title": "Xiaomi API Ping",
        "unknown_choice": "Неизвестный пункт.",
        "status_off": "Проверка статуса перед заявкой: OFF",
        "status_on": "Проверка статуса перед заявкой: ON",
        "disable_check": "Отключить проверку? [y/N]: ",
        "invalid_token": "Cookie/token недействителен.",
        "config_error": "Не удалось загрузить конфигурацию: {error}",
        "save_error": "Не удалось сохранить конфигурацию: {error}",
        "device": "{label}: device_id={device_id}",
        "response": "{label}: code={code} | {message}",
        "found_desktop_token": "Найден сохранённый токен из Desktop 8.0: {token_preview}",
        "found_saved_session": "Обнаружена сохранённая сессия Mi Account ({source}).",
    },
    "en": {
        "title": "Xiaomi Unlock Tool 8.0",
        "tab_settings": "Settings",
        "tab_submit": "Submit application",
        "tab_miunlock": "Mi Unlock",
        "back": "Back",
        "select_tab": "Choose tab: ",
        "settings_token": "ServiceToken",
        "settings_language": "Language",
        "settings_check": "Status check before application",
        "settings_config": "Configuration file",
        "settings_desktop_config": "Desktop 8.0 Config",
        "settings_ping": "Test connection to Xiaomi API",
        "settings_set_token": "Change ServiceToken",
        "settings_toggle_check": "Toggle status check",
        "submit_run": "Submit application (Auto Mode #2)",
        "submit_status": "Check account status",
        "submit_ping": "Ping Xiaomi API",
        "mi_install_run": "Install / launch Mi Unlock",
        "mi_status": "Check Mi Unlock installation",
        "mi_note": "Mi Unlock is launched through the Python `miunlock` package.",
        "mi_python": "Python",
        "mi_package": "miunlock package",
        "installed": "installed",
        "not_installed": "not installed",
        "python_not_found": "Python was not found.",
        "mi_installing": "Installing the miunlock package...",
        "mi_install_failed": "Could not install the miunlock package.",
        "mi_launching": "Launching Mi Unlock...",
        "mi_launch_failed": "Could not launch Mi Unlock: {error}",
        "menu_apply": "Submit application",
        "menu_status": "Check account status",
        "menu_ping": "Ping Xiaomi API",
        "menu_token": "Set ServiceToken",
        "menu_settings": "Settings",
        "menu_exit": "Exit",
        "choose": "Choose: ",
        "token_prompt": "New_bbs_ServiceToken: ",
        "token_empty": "Cookie/token is not specified.",
        "checking": "Checking token and account status...",
        "cookie_bad": "Cookie is expired or invalid (100004).",
        "ready": "Account is ready to submit the application.",
        "blocked": "Account is blocked until: {value}",
        "not_ready": "Account is not ready yet (under 30 days registered in Mi Community).",
        "approved": "Account is already approved. Date: {value}",
        "unknown_status": "Unknown status. code={code}, data={data}",
        "wait": "Waiting for 23:59:59 Beijing time ({seconds:.1f} sec.)...",
        "reached": "23:59:59 Beijing time reached. Sending scheduled requests (Auto Mode #2)...",
        "interrupted": "Process interrupted by user.",
        "saved": "ServiceToken saved.",
        "not_saved": "Empty token was not saved.",
        "status_fail": "Status check failed. Application was not sent.",
        "skip": "Status check disabled.",
        "done": "Finished. Successful responses: {success}/{total}",
        "apply": "{label}: application approved! (code: {code})",
        "not_submitted": "{label}: application was not submitted. Retry after: {value}",
        "maybe_approved": "{label}: server reports that the application may be approved (100003).",
        "rejected": "{label}: request rejected (100001 - daily quota exceeded).",
        "unknown_response": "{label}: unknown response: {result}",
        "bad_json": "Server returned invalid JSON.",
        "bad_json_label": "{label}: server returned invalid JSON.",
        "request_error": "Request error: {error}",
        "ntp": "NTP: {server}",
        "beijing": "Beijing time: {value} (UTC+8)",
        "ntp_fail": "Could not connect to any NTP server.",
        "ping_title": "Xiaomi API Ping",
        "unknown_choice": "Unknown option.",
        "status_off": "Status check before application: OFF",
        "status_on": "Status check before application: ON",
        "disable_check": "Disable check? [y/N]: ",
        "invalid_token": "Cookie/token is invalid.",
        "config_error": "Could not load configuration: {error}",
        "save_error": "Could not save configuration: {error}",
        "device": "{label}: device_id={device_id}",
        "response": "{label}: code={code} | {message}",
        "found_desktop_token": "Found saved token from Desktop 8.0: {token_preview}",
        "found_saved_session": "Detected saved Mi Account session ({source}).",
    },
}

LANG = detect_language()


def t(key: str, **kwargs) -> str:
    return TEXT.get(LANG, TEXT["en"]).get(key, TEXT["en"].get(key, key)).format(**kwargs)


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    CYAN = "\033[36m"


def supports_color() -> bool:
    if not sys.stdout.isatty():
        return False
    if os.environ.get("TERM", "") == "dumb":
        return False
    return True


def color(text: str, code: str) -> str:
    return f"{code}{text}{C.RESET}" if supports_color() else text


def log(message: str, level: str = "info") -> None:
    codes = {"error": C.RED, "ok": C.GREEN, "warn": C.YELLOW, "info": C.CYAN}
    prefix = {"error": "[!]", "ok": "[+]", "warn": "[*]", "info": "[>]"}
    print(color(f"{prefix.get(level, '[>]')} {message}", codes.get(level, C.CYAN)), flush=True)


def generate_device_id() -> str:
    random_data = f"{random.random()}-{time.time()}-{random.randint(0, 1000000)}"
    return hashlib.sha1(random_data.encode("utf-8")).hexdigest().upper()


def detect_saved_desktop_session() -> tuple[str, str] | None:
    """Checks for saved Mi Account sessions in ~/.migatesession (same as res/xiaomi_auth.py)."""
    base = Path.home() / ".migatesession"
    if not base.exists():
        return None
    for sub in ["unlockApi", "18n_bbs_global", "passport"]:
        session_file = base / sub / "session.json"
        if session_file.exists():
            try:
                data = json.loads(session_file.read_text(encoding="utf-8"))
                if data.get("passToken") and data.get("userId"):
                    return sub, str(data.get("userId"))
            except Exception:
                pass
    return None


def load_config() -> dict:
    defaults = {"cookie": "", "skip_cookie_check": False}

    # 1. Check Desktop 8.0 config first
    if DESKTOP_CONFIG_FILE.exists():
        try:
            desktop_data = json.loads(DESKTOP_CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(desktop_data, dict):
                if desktop_data.get("cookie"):
                    defaults["cookie"] = str(desktop_data["cookie"]).strip()
                if "skip_cookie_check" in desktop_data:
                    defaults["skip_cookie_check"] = bool(desktop_data["skip_cookie_check"])
        except Exception:
            pass

    # 2. Check CLI standalone config (takes precedence if customized)
    try:
        if CLI_CONFIG_FILE.exists():
            cli_data = json.loads(CLI_CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(cli_data, dict):
                if cli_data.get("cookie"):
                    defaults["cookie"] = str(cli_data["cookie"]).strip()
                if "skip_cookie_check" in cli_data:
                    defaults["skip_cookie_check"] = bool(cli_data["skip_cookie_check"])
    except Exception as exc:
        log(t("config_error", error=exc), "warn")

    return defaults


def save_config(config: dict) -> None:
    try:
        CLI_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CLI_CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as exc:
        log(t("save_error", error=exc), "warn")

    # Also sync token to Desktop 8.0 config if Desktop directory exists
    try:
        if DESKTOP_CONFIG_DIR.exists():
            desktop_cfg = {}
            if DESKTOP_CONFIG_FILE.exists():
                try:
                    desktop_cfg = json.loads(DESKTOP_CONFIG_FILE.read_text(encoding="utf-8"))
                except Exception:
                    desktop_cfg = {}
            desktop_cfg["cookie"] = config.get("cookie", "")
            desktop_cfg["skip_cookie_check"] = config.get("skip_cookie_check", False)
            DESKTOP_CONFIG_FILE.write_text(json.dumps(desktop_cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass


class XiaomiClient:
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "okhttp/4.12.0",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        })

    @staticmethod
    def cookie_header(token: str, device_id: str) -> str:
        return (
            f"new_bbs_serviceToken={token};"
            f"versionCode=500411;versionName=5.4.11;deviceId={device_id};"
        )

    def request(self, method: str, url: str, token: str, device_id: str, json_body: dict | None = None):
        """
        Executes an HTTP request matching the behavior of res/api_handler.py.
        For POST requests to the bl-auth endpoint, sends {"is_retry":true} by default.
        """
        headers = {
            "Cookie": self.cookie_header(token, device_id),
            "Content-Type": "application/json; charset=utf-8",
        }
        data = None
        if json_body is not None:
            data = json.dumps(json_body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            headers["Content-Length"] = str(len(data))
        elif method.upper() == "POST":
            # Matching res/api_handler.py line 35: body = '{"is_retry":true}'.encode('utf-8')
            data = b'{"is_retry":true}'
            headers["Content-Length"] = str(len(data))

        try:
            return self.session.request(method, url, headers=headers, data=data, timeout=(5, 15))
        except requests.RequestException as exc:
            log(t("request_error", error=exc), "error")
            return None

    def check_status(self, token: str) -> bool:
        device_id = generate_device_id()
        log(t("checking"))
        response = self.request("GET", STATUS_URL, token, device_id)
        if response is None:
            return False
        try:
            data = response.json()
        except ValueError:
            log(t("bad_json"), "error")
            return False

        code = data.get("code")
        # Matching res/api_handler.py checking both 100004 and 10004
        if code in (100004, 10004):
            log(t("cookie_bad"), "error")
            return False

        payload = data.get("data") or {}
        is_pass = payload.get("is_pass")
        button_state = payload.get("button_state")
        deadline = payload.get("deadline_format", "")

        if is_pass == 4 and button_state == 1:
            log(t("ready"), "ok")
            return True
        if is_pass == 4 and button_state == 2:
            log(t("blocked", value=deadline or ("не указано" if LANG == "ru" else "not specified")), "warn")
            return False
        if is_pass == 4 and button_state == 3:
            log(t("not_ready"), "warn")
            return False
        if is_pass == 1:
            log(t("approved", value=deadline or ("не указано" if LANG == "ru" else "not specified")), "ok")
            return False

        log(t("unknown_status", code=code, data=payload), "warn")
        return False

    def apply_once(self, token: str, device_id: str | None = None, label: str = "Запрос") -> bool:
        device_id = device_id or generate_device_id()
        log(t("device", label=label, device_id=device_id))
        response = self.request("POST", APPLY_URL, token, device_id)
        if response is None:
            return False

        try:
            result = response.json()
        except ValueError:
            log(t("bad_json_label", label=label), "error")
            return False

        code = result.get("code")
        message = result.get("message", "")
        payload = result.get("data") or {}
        log(t("response", label=label, code=code, message=message))

        if code == 0:
            apply_result = payload.get("apply_result")
            if apply_result == 1:
                log(t("apply", label=label, code=code), "ok")
                return True
            if apply_result == 3:
                deadline = payload.get("deadline_format", "не указано" if LANG == "ru" else "not specified")
                log(t("not_submitted", label=label, value=deadline), "warn")
                return False

        if code == 100003:
            log(t("maybe_approved", label=label), "ok")
            return True
        if code in (100004, 10004):
            log(t("cookie_bad"), "error")
            return False
        if code == 100001:
            log(t("rejected", label=label), "warn")
            return False

        log(t("unknown_response", label=label, result=result), "warn")
        return False


def ntp_time(server: str, timeout: float = 3.0) -> datetime | None:
    packet = b"\x1b" + 47 * b"\0"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    try:
        sock.sendto(packet, (server, 123))
        data, _ = sock.recvfrom(48)
        if len(data) < 48:
            return None
        seconds, fraction = struct.unpack("!II", data[40:48])
        timestamp = seconds - 2208988800 + fraction / 2**32
        # Standard Beijing UTC+8 time matching 8.0.py
        return datetime.fromtimestamp(timestamp, timezone.utc).astimezone(timezone(timedelta(hours=8)))
    except (OSError, struct.error):
        return None
    finally:
        sock.close()


def get_beijing_time() -> tuple[datetime, float] | tuple[None, None]:
    """Returns (beijing_time, local_monotonic_timestamp) calibrated to NTP."""
    for server in NTP_SERVERS:
        log(t("ntp", server=server))
        current = ntp_time(server)
        local_ts = time.time()
        if current:
            log(t("beijing", value=current.strftime("%Y-%m-%d %H:%M:%S.%f")), "ok")
            return current, local_ts
    log(t("ntp_fail"), "error")
    return None, None


def tcp_ping(host: str, port: int = 443, timeout: float = 3.0) -> float | None:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (time.perf_counter() - start) * 1000
    except OSError:
        return None


def http_ping(host: str, timeout: float = 3.0) -> float | None:
    start = time.perf_counter()
    try:
        response = requests.get(
            f"https://{host}",
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        elapsed = (time.perf_counter() - start) * 1000
        return elapsed if response.status_code < 500 else None
    except requests.RequestException:
        return None


def ping_command() -> None:
    print("\n" + color(t("ping_title"), C.BOLD))
    print("-" * 40)
    for host in PING_HOSTS:
        tcp = tcp_ping(host)
        http = http_ping(host)
        tcp_text = f"{tcp:.2f} ms" if tcp is not None else "N/A"
        http_text = f"{http:.2f} ms" if http is not None else "N/A"
        print(f"{host:24} TCP: {tcp_text:>10}   HTTP: {http_text:>10}")


def run_application(client: XiaomiClient, token: str, skip_check: bool = False) -> int:
    print("\n" + color(t("title"), C.BOLD))
    print("=" * 40)

    if not token:
        log(t("token_empty"), "error")
        return 2

    if not skip_check:
        if not client.check_status(token):
            log(t("status_fail"), "error")
            return 1
    else:
        log(t("skip"), "warn")

    beijing, start_ts = get_beijing_time()
    if beijing is None or start_ts is None:
        return 1

    target = beijing.replace(hour=23, minute=59, second=59, microsecond=0)
    if target <= beijing:
        target += timedelta(days=1)

    # Calculate calibrated time remaining until 23:59:59 Beijing
    delay = (target - beijing).total_seconds()
    log(t("wait", seconds=delay))

    # Wait until 23:59:59 using NTP-synchronized time
    try:
        while True:
            now_sync = beijing + timedelta(seconds=(time.time() - start_ts))
            diff = (target - now_sync).total_seconds()
            if diff <= 0:
                break
            if diff > 1.0:
                time.sleep(min(diff - 0.5, 1.0))
            else:
                time.sleep(max(0.0, min(diff, 0.01)))
    except KeyboardInterrupt:
        log(t("interrupted"), "warn")
        return 130

    # Auto Mode #2: Micro-offsets matching 8.0.py (lines 2657-2680)
    # Target offsets are 58.6, 58.8, 59.1, 59.3, 59.5, 59.8 ms after 23:59:59.000
    offsets_ms = [58.6, 58.8, 59.1, 59.3, 59.5, 59.8]
    log(t("reached"), "info")

    base = target
    threads: list[threading.Thread] = []
    results: list[bool] = []
    results_lock = threading.Lock()

    def dispatch_worker(seq: int, offset_val: float, dev_id: str):
        label = f"Auto #2 HTTP #{seq} (+{offset_val:.1f}ms)" if LANG == "en" else f"Авторежим #2 HTTP #{seq} (+{offset_val:.1f}мс)"
        res = client.apply_once(token, device_id=dev_id, label=label)
        with results_lock:
            results.append(res)

    # Schedule requests concurrently via threading.Timer matching 8.0.py architecture
    for index, offset in enumerate(offsets_ms, 1):
        send_at = base + timedelta(milliseconds=offset)
        now_sync = beijing + timedelta(seconds=(time.time() - start_ts))
        timer_delay = max(0.0, (send_at - now_sync).total_seconds())
        dev_id = generate_device_id()
        timer = threading.Timer(timer_delay, dispatch_worker, args=(index, offset, dev_id))
        threads.append(timer)
        timer.start()

    # Await completion of all parallel requests
    for t_worker in threads:
        t_worker.join()

    success = sum(1 for r in results if r)
    log(t("done", success=success, total=len(offsets_ms)), "ok" if success else "warn")
    return 0 if success else 1


def clear_screen() -> None:
    if sys.stdout.isatty():
        os.system("cls" if os.name == "nt" else "clear")


def header(title: str) -> None:
    print("\n" + color("╭──────────────────────────────────────╮", C.CYAN))
    print(color(f"│ {title:^36} │", C.CYAN))
    print(color("╰──────────────────────────────────────╯", C.CYAN))


def token_menu(client: XiaomiClient, config: dict) -> None:
    token = getpass.getpass(t("token_prompt")).strip()
    if not token:
        log(t("not_saved"), "error")
        return
    config["cookie"] = token
    save_config(config)
    log(t("saved"), "ok")


def settings_tab(client: XiaomiClient, config: dict) -> None:
    while True:
        clear_screen()
        header(t("tab_settings"))
        token = config.get("cookie", "").strip()
        check_enabled = not bool(config.get("skip_cookie_check", False))
        token_status = ("✓ " + ("установлен" if LANG == "ru" else "set")) if token else ("✗ " + ("не установлен" if LANG == "ru" else "not set"))
        print(f"{t('settings_token')}: " + color(token_status, C.GREEN if token else C.YELLOW))
        print(f"{t('settings_language')}: {'Русский' if LANG == 'ru' else 'English'}")
        print(f"{t('settings_check')}: " + ("ON" if check_enabled else "OFF"))
        print(f"{t('settings_config')}: {CLI_CONFIG_FILE}")
        if DESKTOP_CONFIG_FILE.exists():
            print(f"{t('settings_desktop_config')}: {DESKTOP_CONFIG_FILE}")
        print()
        print(f"[1] {t('settings_set_token')}")
        print(f"[2] {t('settings_toggle_check')}")
        print(f"[3] {t('settings_ping')}")
        print(f"[0] {t('back')}")
        choice = input("\n" + t("choose")).strip()

        if choice == "1":
            token_menu(client, config)
            input("\nPress Enter..." if LANG == "en" else "\nНажмите Enter...")
        elif choice == "2":
            config["skip_cookie_check"] = not config.get("skip_cookie_check", False)
            save_config(config)
            log(t("status_off") if config["skip_cookie_check"] else t("status_on"), "ok")
            time.sleep(0.8)
        elif choice == "3":
            ping_command()
            input("\nPress Enter..." if LANG == "en" else "\nНажмите Enter...")
        elif choice == "0":
            return
        else:
            log(t("unknown_choice"), "warn")
            time.sleep(0.8)


def submit_tab(client: XiaomiClient, config: dict) -> None:
    while True:
        clear_screen()
        header(t("tab_submit"))
        token = config.get("cookie", "").strip()
        print(f"{t('settings_token')}: " + ("✓" if token else "✗"))
        print(f"{t('settings_check')}: " + ("ON" if not config.get("skip_cookie_check", False) else "OFF"))
        print()
        print(f"[1] {t('submit_run')}")
        print(f"[2] {t('submit_status')}")
        print(f"[3] {t('submit_ping')}")
        print(f"[0] {t('back')}")
        choice = input("\n" + t("choose")).strip()

        if choice == "1":
            if not token:
                token = getpass.getpass(t("token_prompt")).strip()
                if token:
                    config["cookie"] = token
                    save_config(config)
            if token:
                run_application(client, token, bool(config.get("skip_cookie_check", False)))
            input("\nPress Enter..." if LANG == "en" else "\nНажмите Enter...")
        elif choice == "2":
            if not token:
                token = getpass.getpass(t("token_prompt")).strip()
            if token:
                config["cookie"] = token
                save_config(config)
                client.check_status(token)
            input("\nPress Enter..." if LANG == "en" else "\nНажмите Enter...")
        elif choice == "3":
            ping_command()
            input("\nPress Enter..." if LANG == "en" else "\nНажмите Enter...")
        elif choice == "0":
            return
        else:
            log(t("unknown_choice"), "warn")
            time.sleep(0.8)


def find_miunlock() -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "miunlock", "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0:
            return True, sys.executable
    except (OSError, subprocess.SubprocessError):
        pass
    return False, sys.executable


def install_and_run_miunlock() -> None:
    installed, python_cmd = find_miunlock()
    if not installed:
        log(t("mi_installing"), "info")
        try:
            result = subprocess.run(
                [python_cmd, "-m", "pip", "install", "miunlock"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                log(t("mi_install_failed"), "error")
                if result.stderr:
                    print(result.stderr[-1200:])
                return
        except (OSError, subprocess.SubprocessError) as exc:
            log(t("mi_install_failed"), "error")
            print(str(exc))
            return

    log(t("mi_launching"), "info")
    try:
        result = subprocess.run([python_cmd, "-m", "miunlock"])
        if result.returncode != 0:
            log(t("mi_launch_failed", error=f"exit code {result.returncode}"), "error")
    except (OSError, subprocess.SubprocessError) as exc:
        log(t("mi_launch_failed", error=exc), "error")


def miunlock_tab(client: XiaomiClient, config: dict) -> None:
    while True:
        clear_screen()
        header(t("tab_miunlock"))
        installed, python_cmd = find_miunlock()
        print(f"{t('mi_python')}: {python_cmd}")
        print(f"{t('mi_package')}: " + (t("installed") if installed else t("not_installed")))
        print()
        print(t("mi_note"))
        print()
        print(f"[1] {t('mi_install_run')}")
        print(f"[2] {t('mi_status')}")
        print(f"[0] {t('back')}")
        choice = input("\n" + t("choose")).strip()

        if choice == "1":
            install_and_run_miunlock()
            input("\nPress Enter..." if LANG == "en" else "\nНажмите Enter...")
        elif choice == "2":
            installed, _ = find_miunlock()
            log(t("installed") if installed else t("not_installed"), "ok" if installed else "warn")
            input("\nPress Enter..." if LANG == "en" else "\nНажмите Enter...")
        elif choice == "0":
            return
        else:
            log(t("unknown_choice"), "warn")
            time.sleep(0.8)


def interactive(client: XiaomiClient, config: dict) -> int:
    saved_session = detect_saved_desktop_session()
    if saved_session and not config.get("cookie"):
        log(t("found_saved_session", source=saved_session[0]), "info")

    while True:
        clear_screen()
        header(t("title"))
        print(f"[1] {t('tab_settings')}")
        print(f"[2] {t('tab_submit')}")
        print(f"[3] {t('tab_miunlock')}")
        print(f"[0] {t('menu_exit')}")
        choice = input("\n" + t("select_tab")).strip()

        if choice == "1":
            settings_tab(client, config)
        elif choice == "2":
            submit_tab(client, config)
        elif choice == "3":
            miunlock_tab(client, config)
        elif choice == "0":
            return 0
        else:
            log(t("unknown_choice"), "warn")
            time.sleep(0.8)


def build_parser() -> argparse.ArgumentParser:
    if LANG == "ru":
        description = "Xiaomi Unlock Tool 8.0 — CLI / Termux версия"
        token_help = "New_bbs_ServiceToken (не рекомендуется: останется в shell history)"
        skip_help = "Пропустить предварительную проверку статуса аккаунта"
        run_help = "Запустить отправку заявки (Авторежим #2)"
        status_help = "Проверить статус аккаунта"
        ping_help = "Проверить TCP/HTTP задержку серверов Xiaomi API"
        token_cmd_help = "Установить ServiceToken интерактивно"
        config_help = "Показать пути к файлам конфигурации"
    else:
        description = "Xiaomi Unlock Tool 8.0 — CLI / Termux edition"
        token_help = "New_bbs_ServiceToken (not recommended: will remain in shell history)"
        skip_help = "Skip preliminary account status check"
        run_help = "Run the application submission process (Auto Mode #2)"
        status_help = "Check account status"
        ping_help = "Check Xiaomi API TCP/HTTP latency"
        token_cmd_help = "Set ServiceToken interactively"
        config_help = "Show configuration file paths"

    # Shared parent parser so --token and --skip-status-check work both before and after subcommands
    common_parent = argparse.ArgumentParser(add_help=False)
    common_parent.add_argument("--token", help=token_help, default=argparse.SUPPRESS)
    common_parent.add_argument("--skip-status-check", action="store_true", help=skip_help, default=argparse.SUPPRESS)

    parser = argparse.ArgumentParser(
        prog="miunlock",
        description=description,
        parents=[common_parent],
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("run", help=run_help, parents=[common_parent])
    sub.add_parser("status", help=status_help, parents=[common_parent])
    sub.add_parser("ping", help=ping_help)
    sub.add_parser("token", help=token_cmd_help)
    sub.add_parser("config", help=config_help)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    config = load_config()
    client = XiaomiClient(config)

    if args.command == "config":
        print(f"CLI Config:     {CLI_CONFIG_FILE}")
        if DESKTOP_CONFIG_FILE.exists():
            print(f"Desktop Config: {DESKTOP_CONFIG_FILE}")
        return 0

    if args.command == "ping":
        ping_command()
        return 0

    if args.command == "token":
        token = getpass.getpass(t("token_prompt")).strip()
        if not token:
            log(t("not_saved"), "error")
            return 2
        config["cookie"] = token
        save_config(config)
        log(t("saved"), "ok")
        return 0

    token = (getattr(args, "token", None) or config.get("cookie", "")).strip()

    if args.command == "status":
        if not token:
            token = getpass.getpass(t("token_prompt")).strip()
        return 0 if token and client.check_status(token) else 1

    if args.command == "run":
        skip_status = getattr(args, "skip_status_check", False) or bool(config.get("skip_cookie_check", False))
        return run_application(client, token, skip_status)

    return interactive(client, config)


if __name__ == "__main__":
    raise SystemExit(main())
