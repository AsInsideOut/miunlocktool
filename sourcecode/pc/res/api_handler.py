import json
import time
import hashlib
import random
import statistics
import socket
import threading
from datetime import datetime, timedelta, timezone

import ntplib
import pytz
import urllib3
import requests


class HTTP11Session:
    def __init__(self):
        self.http = urllib3.PoolManager(
            maxsize=10,
            retries=True,
            timeout=urllib3.Timeout(connect=2.0, read=15.0),
            headers={}
        )

    def make_request(self, method, url, headers=None, body=None):
        try:
            request_headers = {}
            if headers:
                request_headers.update(headers)

            request_headers['Content-Type'] = 'application/json; charset=utf-8'

            if method == 'POST':
                if body is None:
                    body = '{"is_retry":true}'.encode('utf-8')
                request_headers['Content-Length'] = str(len(body))
            else:
                body = None

            request_headers['Accept-Encoding'] = 'gzip, deflate, br'
            request_headers['User-Agent'] = 'okhttp/4.12.0'
            request_headers['Connection'] = 'keep-alive'

            response = self.http.request(
                method,
                url,
                headers=request_headers,
                body=body,
                preload_content=False
            )
            return response
        except Exception:
            return None


class RequestHandler:
    def __init__(self, app):
        self.app = app
        self.session = HTTP11Session()
        self.ntp_servers = [
            "time1.google.com", "time2.google.com", "time3.google.com", "time4.google.com", "time.android.com",
            "time.aws.com", "time.google.com", "time.cloudflare.com",
            "ntp.time.in.ua", "stratum1.net", "ntp5.stratum2.ru"
        ]
        self.mi_servers = ['sgp-api.buy.mi.com']
        self.last_success_dialog_shown = False
        # HTTP endpoints для измерения пинга
        self.ping_http_hosts = [
            "sgp-api.buy.mi.com",
            "api.buy.mi.com",
            "account.xiaomi.com"
        ]
        # TCP хосты и порты
        self.ping_tcp_hosts = [
            ("sgp-api.buy.mi.com", 443),
            ("api.buy.mi.com", 443),
            ("account.xiaomi.com", 443)
        ]

    def generate_device_id(self):
        random_data = f"{random.random()}-{time.time()}-{random.randint(0, 1000000)}"
        device_id = hashlib.sha1(random_data.encode('utf-8')).hexdigest().upper()
        return device_id

    def http_ping(self, url, timeout=3):
        """Измеряет время HTTP запроса до указанного URL"""
        try:
            start_time = time.time()
            response = requests.get(
                url,
                timeout=timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
                verify=True
            )
            end_time = time.time()
            ping_ms = (end_time - start_time) * 1000
            return ping_ms if response.status_code < 500 else None
        except requests.exceptions.Timeout:
            self.app.log_message(f"HTTP ping timeout for {url}", "orange")
            return None
        except requests.exceptions.ConnectionError:
            self.app.log_message(f"HTTP ping connection error for {url}", "orange")
            return None
        except Exception as e:
            self.app.log_message(f"HTTP ping error for {url}: {e}", "orange")
            return None

    def tcp_ping(self, host, port=443, timeout=3):
        """Измеряет время TCP handshake до хоста:порт"""
        try:
            start = time.time()
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            return (time.time() - start) * 1000  # в мс
        except Exception as e:
            self.app.log_message(f"TCP ping error for {host}:{port} - {e}", "orange")
            return None

    def measure_pings(self, duration=20):
        """
        Измеряет HTTP и TCP пинг в течение duration секунд,
        возвращает кортеж (avg_http, avg_tcp) или (None, None) при ошибке.
        """
        http_pings = []
        tcp_pings = []
        start_time = time.time()
        end_time = start_time + duration

        self.app.log_message(self.app.translation.tr('log_ping_start_http_tcp'), "blue")
        while time.time() < end_time:
            # HTTP
            for host in self.ping_http_hosts:
                ping = self.http_ping(f"https://{host}")
                if ping is not None:
                    http_pings.append(ping)
            # TCP
            for host, port in self.ping_tcp_hosts:
                ping = self.tcp_ping(host, port)
                if ping is not None:
                    tcp_pings.append(ping)
            time.sleep(0.5)  # пауза между замерами

        avg_http = None
        if http_pings:
            avg_http = statistics.mean(http_pings)
            self.app.log_message(self.app.translation.tr('log_ping_avg_http').format(avg_http), "green")
        else:
            self.app.log_message(self.app.translation.tr('log_ping_http_failed'), "orange")

        avg_tcp = None
        if tcp_pings:
            avg_tcp = statistics.mean(tcp_pings)
            self.app.log_message(self.app.translation.tr('log_ping_avg_tcp').format(avg_tcp), "green")
        else:
            self.app.log_message(self.app.translation.tr('log_ping_tcp_failed'), "orange")

        return avg_http, avg_tcp

    def get_initial_beijing_time(self):
        client = ntplib.NTPClient()
        beijing_tz = pytz.timezone("Asia/Shanghai")
        for server in self.ntp_servers:
            try:
                self.app.log_message(self.app.translation.tr('ntp_connect').format(server))
                response = client.request(server, version=3)
                ntp_time = datetime.fromtimestamp(response.tx_time, timezone.utc)
                beijing_time = ntp_time.astimezone(beijing_tz)
                self.app.log_message(self.app.translation.tr('ntp_time').format(
                    server, beijing_time.strftime('%Y-%m-%d %H:%M:%S.%f')))
                self.app.time_var.set(
                    f"{self.app.translation.tr('time_synchronized')}: {beijing_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
                return beijing_time
            except Exception as e:
                self.app.log_message(f"Error connecting to {server}: {e}")
        self.app.log_message(self.app.translation.tr('ntp_failed'))
        return None

    def get_synchronized_beijing_time(self, start_beijing_time, start_timestamp):
        elapsed = time.time() - start_timestamp
        current_time = start_beijing_time + timedelta(seconds=elapsed)
        return current_time

    def calculate_script_time(self, ping_ms):
        ping_seconds = ping_ms / 1000.0
        send_time = 60.0 - ping_seconds
        if send_time < 56.0:
            send_time = 56.0
        if send_time > 59.9:
            send_time = 59.9
        return send_time

    def check_unlock_status(self, cookie_value, device_id, force=False, show_success_dialog=False):
        if not force and self.app.settings.get('skip_cookie_check', False):
            self.app.log_message(self.app.translation.tr('cookie_skipped'))
            return True

        try:
            url = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"
            headers = {
                "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
            }

            response = self.session.make_request('GET', url, headers=headers)
            if response is None:
                self.app.log_message(self.app.translation.tr('status_get_failed'), color="red")
                if show_success_dialog:
                    from tkinter import messagebox
                    messagebox.showerror(self.app.translation.tr('error_title'), self.app.translation.tr('status_get_failed'))
                return False

            response_data = json.loads(response.data.decode('utf-8'))
            response.release_conn()

            if response_data.get("code") == 100004:
                self.app.log_message(self.app.translation.tr('cookie_expired'), color="red")
                from tkinter import messagebox
                messagebox.showerror(self.app.translation.tr('cookie_error_title'), self.app.translation.tr('cookie_expired'))
                return False

            data = response_data.get("data", {})
            is_pass = data.get("is_pass")
            button_state = data.get("button_state")
            deadline_format = data.get("deadline_format", "")

            if is_pass == 4:
                if button_state == 1:
                    self.app.log_message(self.app.translation.tr('account_ready'), color="green")
                    if show_success_dialog:
                        from tkinter import messagebox
                        messagebox.showinfo(
                            self.app.translation.tr('eligibility_eligible_title'),
                            self.app.translation.tr('account_ready')
                        )
                    return True
                elif button_state == 2:
                    self.app.log_message(self.app.translation.tr('account_blocked').format(deadline_format), color="orange")
                    from tkinter import messagebox
                    messagebox.showinfo(
                        self.app.translation.tr('account_blocked_title'),
                        self.app.translation.tr('account_blocked').format(deadline_format)
                    )
                    return False
                elif button_state == 3:
                    self.app.log_message(self.app.translation.tr('account_new'), color="orange")
                    from tkinter import messagebox
                    messagebox.showinfo(
                        self.app.translation.tr('account_new_title'),
                        self.app.translation.tr('account_new')
                    )
                    return False
            elif is_pass == 1:
                self.app.log_message(self.app.translation.tr('account_approved').format(deadline_format), color="green")
                from tkinter import messagebox
                messagebox.showinfo(
                    self.app.translation.tr('account_approved_title'),
                    self.app.translation.tr('account_approved').format(deadline_format)
                )
                return False
            else:
                self.app.log_message(self.app.translation.tr('account_unknown'), color="red")
                from tkinter import messagebox
                messagebox.showerror(
                    self.app.translation.tr('unknown_status_title'),
                    self.app.translation.tr('account_unknown')
                )
                return False
        except Exception as e:
            self.app.log_message(self.app.translation.tr('status_error').format(e), color="red")
            if show_success_dialog:
                from tkinter import messagebox
                messagebox.showerror(
                    self.app.translation.tr('error_title'),
                    self.app.translation.tr('status_error').format(e)
                )
            return False

    def single_request(self, cookie_value=None, device_id=None):
        if cookie_value is None:
            cookie_value = self.app.cookie_value.get().strip()
        if device_id is None:
            device_id = self.generate_device_id()

        url = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
        headers = {
            "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
        }

        try:
            request_time = self.get_synchronized_beijing_time(self.app.start_beijing_time, self.app.start_timestamp)
            self.app.log_message(
                self.app.translation.tr('request_sent').format(request_time.strftime('%Y-%m-%d %H:%M:%S.%f')))

            response = self.session.make_request('POST', url, headers=headers)
            if response is None:
                self.app.set_application_status(self.app.translation.tr('application_status_failed'), 'application_status_failed')
                self.app.log_message(self.app.translation.tr('request_failed'))
                return False

            response_time = self.get_synchronized_beijing_time(self.app.start_beijing_time, self.app.start_timestamp)
            self.app.log_message(
                self.app.translation.tr('response_received').format(response_time.strftime('%Y-%m-%d %H:%M:%S.%f')))

            try:
                response_data = response.data
                response.release_conn()
                json_response = json.loads(response_data.decode('utf-8'))
                code = json_response.get("code")
                data = json_response.get("data", {})

                self.app.log_message(f"Response code: {code}", "blue")
                self.app.log_message(f"Response data: {json_response}", "blue")

                if code == 0:
                    apply_result = data.get("apply_result")
                    if apply_result == 1:
                        self.app.log_message(self.app.translation.tr('status_app_approved_checking'))
                        self.check_unlock_status(cookie_value, device_id)
                        self.app.set_application_status(self.app.translation.tr('application_status_success'), 'application_status_success')
                        self.show_success_dialog()
                        return True
                    elif apply_result == 3:
                        deadline_format = data.get("deadline_format", "Not specified")
                        self.app.log_message(
                            self.app.translation.tr('application_not_submitted').format(deadline_format))
                        from tkinter import messagebox
                        messagebox.showinfo(
                            "Information",
                            f"{self.app.translation.tr('application_not_submitted').format(deadline_format)}\n\n{self.app.translation.tr('device_binding_hint')}"
                        )
                        self.app.set_application_status(self.app.translation.tr('application_status_failed'), 'application_status_failed')
                        return False
                elif code == 100001:
                    self.app.log_message(self.app.translation.tr('status_app_rejected_100001'))
                    self.app.set_application_status(self.app.translation.tr('application_status_failed'), 'application_status_failed')
                    return False
                elif code == 100003:
                    self.app.log_message(self.app.translation.tr('status_app_possibly_approved'))
                    self.check_unlock_status(cookie_value, device_id)
                    self.app.set_application_status(self.app.translation.tr('application_status_success'), 'application_status_success')
                    self.show_success_dialog()
                    return True
                elif code == 100004 or code == 10004:
                    error_msg = self.app.translation.tr('cookie_expired')
                    self.app.log_message(f"[Error] {error_msg}", color="red")
                    from tkinter import messagebox
                    messagebox.showerror(
                        self.app.translation.tr('cookie_error_title'),
                        error_msg
                    )
                    self.app.set_application_status(self.app.translation.tr('application_status_failed'), 'application_status_failed')
                    return False
                else:
                    msg = json_response.get("message", "Unknown error")
                    self.app.log_message(f"[Error] Code: {code}, Message: {msg}", color="red")
                    self.app.set_application_status(self.app.translation.tr('application_status_unknown'), 'application_status_unknown')
                    return False

            except Exception as e:
                self.app.log_message(self.app.translation.tr('response_error').format(e))
                self.app.set_application_status(self.app.translation.tr('application_status_unknown'), 'application_status_unknown')
                return False

        except Exception as e:
            self.app.log_message(self.app.translation.tr('request_error').format(e))
            self.app.set_application_status(self.app.translation.tr('application_status_unknown'), 'application_status_unknown')
            return False

    def show_success_dialog(self):
        if not hasattr(self, '_success_dialog_shown') or not self._success_dialog_shown:
            self._success_dialog_shown = True
            from tkinter import messagebox

            title = self.app.translation.tr('success_dialog_title')
            message = self.app.translation.tr('success_dialog_message')

            messagebox.showinfo(title, message)

            def reset_flag():
                self._success_dialog_shown = False

            threading.Timer(5.0, reset_flag).start()

    def make_single_request_with_new_device_id(self, seq_num, offset_val, device_id, cookie_value=None):
        try:
            if cookie_value is None:
                cookie_value = self.app.cookie_value.get().strip()

            self.app.log_message(self.app.translation.tr('req_using_device_id').format(seq_num, device_id), color="blue")

            url = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
            headers = {
                "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
            }

            response = self.session.make_request('POST', url, headers=headers)

            if response:
                try:
                    resp_data = response.data.decode('utf-8')
                    response.release_conn()
                    json_resp = json.loads(resp_data)
                    code = json_resp.get("code")
                    msg = json_resp.get("message", "")

                    prefix = f"[{self.app.translation.tr('request_prefix')} #{seq_num}]"
                    log_str = f"{prefix} {self.app.translation.tr('log_code_message').format(code=code, msg=msg)}"

                    if code == 0 or code == 100003:
                        self.app.log_message(f"{self.app.translation.tr('log_success_prefix')} {log_str}", color="green")
                        if code == 0 or code == 100003:
                            self.show_success_dialog()
                        return True
                    elif code == 100004 or code == 10004:
                        self.app.log_message(f"[Error] {self.app.translation.tr('cookie_expired')}", color="red")
                        return False
                    else:
                        self.app.log_message(log_str, color="orange")
                        return False

                except Exception as e:
                    self.app.log_message(f"[{self.app.translation.tr('request_prefix')} #{seq_num}] {self.app.translation.tr('log_request_parse_error').format(data=e)}", color="red")
                    return False
            else:
                self.app.log_message(f"[{self.app.translation.tr('request_prefix')} #{seq_num}] {self.app.translation.tr('log_request_failed_no_response')}", color="red")
                return False

        except Exception as e:
            self.app.log_message(f"[{self.app.translation.tr('request_prefix')} #{seq_num}] {self.app.translation.tr('log_request_exception').format(error=e)}", color="red")
            return False

    def send_auto_mode_2_http_request(self, seq_num, device_id, cookie_value=None):
        try:
            if cookie_value is None:
                cookie_value = self.app.cookie_value.get().strip()

            self.app.log_message(self.app.translation.tr('mode2_using_device_id').format(seq_num, device_id), color="blue")

            url = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
            headers = {
                "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
            }

            response = self.session.make_request('POST', url, headers=headers)
            if response:
                try:
                    resp_data = response.data.decode('utf-8')
                    response.release_conn()
                    json_resp = json.loads(resp_data)
                    code = json_resp.get("code")
                    msg = json_resp.get("message", "")
                    self.app.log_message(f"[{self.app.translation.tr('mode2_prefix')} HTTP #{seq_num}] {self.app.translation.tr('log_code_message').format(code=code, msg=msg)}", "blue")

                    if code == 0 or code == 100003:
                        self.app.log_message(f"[{self.app.translation.tr('mode2_prefix')} HTTP #{seq_num}] {self.app.translation.tr('log_success_prefix')} {self.app.translation.tr('log_code_message').format(code=code, msg=msg)}", "green")
                        return True
                    elif code == 100004 or code == 10004:
                        self.app.log_message(f"[{self.app.translation.tr('mode2_prefix')} HTTP #{seq_num}] {self.app.translation.tr('cookie_expired')}", "red")
                        return False
                    else:
                        self.app.log_message(f"[{self.app.translation.tr('mode2_prefix')} HTTP #{seq_num}] {self.app.translation.tr('log_code_message').format(code=code, msg=msg)}", "orange")
                        return False
                except Exception as e:
                    self.app.log_message(f"[{self.app.translation.tr('mode2_prefix')} HTTP #{seq_num}] {self.app.translation.tr('log_request_parse_error').format(data=e)}", "red")
                    return False
            else:
                self.app.log_message(f"[{self.app.translation.tr('mode2_prefix')} HTTP #{seq_num}] {self.app.translation.tr('log_request_failed_no_response')}", "red")
                return False
        except Exception as e:
            self.app.log_message(f"[{self.app.translation.tr('mode2_prefix')} HTTP #{seq_num}] {self.app.translation.tr('log_request_exception').format(error=e)}", "red")
            return False