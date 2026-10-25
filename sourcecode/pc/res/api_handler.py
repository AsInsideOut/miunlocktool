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
    # Pre-baked static post body & headers for minimal allocation & high throughput
    _STATIC_BASE_HEADERS = {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'okhttp/4.12.0',
        'Connection': 'keep-alive'
    }
    _STATIC_POST_BODY = b'{"is_retry":true}'
    _STATIC_POST_HEADERS = {
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Length': '17',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'okhttp/4.12.0',
        'Connection': 'keep-alive'
    }

    def __init__(self):
        self.http = urllib3.PoolManager(
            num_pools=10,
            maxsize=50,
            retries=True,
            timeout=urllib3.Timeout(connect=2.0, read=15.0),
            headers={}
        )

    def make_request(self, method, url, headers=None, body=None):
        try:
            if method == 'POST':
                if body is None:
                    body = self._STATIC_POST_BODY
                    request_headers = self._STATIC_POST_HEADERS.copy()
                else:
                    request_headers = self._STATIC_POST_HEADERS.copy()
                    request_headers['Content-Length'] = str(len(body))
            else:
                body = None
                request_headers = self._STATIC_BASE_HEADERS.copy()

            if headers:
                request_headers.update(headers)

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
    BL_AUTH_URL = "https://sgp-api.buy.mi.com/bbs/api/global/apply/bl-auth"
    BL_SWITCH_URL = "https://sgp-api.buy.mi.com/bbs/api/global/user/bl-switch/state"

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

    def generate_device_id(self):
        random_data = f"{random.random()}-{time.time()}-{random.randint(0, 1000000)}"
        device_id = hashlib.sha1(random_data.encode('utf-8')).hexdigest().upper()
        return device_id

    def measure_pings(self, duration=0):
        return None, None

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

    def check_unlock_status(self, cookie_value, device_id, force=False, show_success_dialog=False):
        if not force and self.app.settings.get('skip_cookie_check', False):
            self.app.log_message(self.app.translation.tr('cookie_skipped'))
            return True

        try:
            headers = {
                "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
            }

            response = self.session.make_request('GET', self.BL_SWITCH_URL, headers=headers)
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
                if show_success_dialog:
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
                    if show_success_dialog:
                        from tkinter import messagebox
                        messagebox.showinfo(
                            self.app.translation.tr('account_blocked_title'),
                            self.app.translation.tr('account_blocked').format(deadline_format)
                        )
                    return False
                elif button_state == 3:
                    self.app.log_message(self.app.translation.tr('account_new'), color="orange")
                    if show_success_dialog:
                        from tkinter import messagebox
                        messagebox.showinfo(
                            self.app.translation.tr('account_new_title'),
                            self.app.translation.tr('account_new')
                        )
                    return False
            elif is_pass == 1:
                self.app.log_message(self.app.translation.tr('account_approved').format(deadline_format), color="green")
                if show_success_dialog:
                    from tkinter import messagebox
                    messagebox.showinfo(
                        self.app.translation.tr('account_approved_title'),
                        self.app.translation.tr('account_approved').format(deadline_format)
                    )
                return False
            else:
                self.app.log_message(self.app.translation.tr('account_unknown'), color="red")
                if show_success_dialog:
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

        headers = {
            "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
        }

        try:
            request_time = self.get_synchronized_beijing_time(self.app.start_beijing_time, self.app.start_timestamp)
            self.app.log_message(
                self.app.translation.tr('request_sent').format(request_time.strftime('%Y-%m-%d %H:%M:%S.%f')))

            response = self.session.make_request('POST', self.BL_AUTH_URL, headers=headers)
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
                        self.app.set_application_status(self.app.translation.tr('application_status_failed'), 'application_status_failed')
                        return False
                    else:
                        msg = json_response.get("msg") or json_response.get("message") or f"apply_result={apply_result}"
                        self.app.log_message(f"Apply result: {msg}", "orange")
                        self.app.set_application_status(self.app.translation.tr('application_status_unknown'), 'application_status_unknown')
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
        """Success notification is handled via Timer HUD, status bar and logs without blocking popup windows."""
        pass

    def make_single_request_with_new_device_id(self, seq_num, offset_val, device_id, cookie_value=None):
        try:
            if cookie_value is None:
                cookie_value = self.app.cookie_value.get().strip()

            self.app.log_message(self.app.translation.tr('req_using_device_id').format(seq_num, device_id), color="blue")

            headers = {
                "Cookie": f"new_bbs_serviceToken={cookie_value};versionCode=500411;versionName=5.4.11;deviceId={device_id};"
            }

            response = self.session.make_request('POST', self.BL_AUTH_URL, headers=headers)

            if response:
                try:
                    try:
                        resp_data = response.data.decode('utf-8')
                    finally:
                        response.release_conn()
                    json_resp = json.loads(resp_data)
                    code = json_resp.get("code")
                    msg = json_resp.get("message", "")

                    prefix = f"[{self.app.translation.tr('request_prefix')} #{seq_num}]"
                    log_str = f"{prefix} {self.app.translation.tr('log_code_message').format(code=code, msg=msg)}"

                    if code == 0 or code == 100003:
                        self.app.log_message(f"{self.app.translation.tr('log_success_prefix')} {log_str}", color="green")
                        self.show_success_dialog()
                        return True
                    elif code == 100001:
                        self.app.log_message(log_str, color="orange")
                        return False
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
