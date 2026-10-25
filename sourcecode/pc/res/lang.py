import os
import locale


def get_system_language():
    try:
        lang = locale.getlocale()[0]
        if lang:
            lang_lower = lang.lower()
            if lang_lower.startswith("ru"):
                return "ru"
            elif lang_lower.startswith("uk") or "ukrainian" in lang_lower:
                return "uk"
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
    elif "uk" in env_lang or "ukrainian" in env_lang:
        return "uk"
    elif "id" in env_lang or "in" in env_lang or "indonesian" in env_lang:
        return "id"
    elif "es" in env_lang or "spanish" in env_lang:
        return "es"
    elif "pt" in env_lang or "portuguese" in env_lang:
        return "pt"
    elif "zh" in env_lang or "chinese" in env_lang:
        return "zh"

    return "en"


class Translation:
    SUPPORTED_LANGUAGES = ['ru', 'en', 'uk', 'id', 'es', 'zh', 'pt']
    BASE_DOWNLOAD_URL = "https://miunlock.su/download/languages"

    def __init__(self, language=None):
        if language is None:
            self.language = get_system_language()
        else:
            self.language = language
        if self.language not in self.SUPPORTED_LANGUAGES:
            self.language = 'en'

        self.languages_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'languages')
        
        # По умолчанию встроены только 2 языка: русский и английский
        self.translations = {
            'ru': self.get_russian(),
            'en': self.get_english(),
            'uk': self.get_ukrainian(),
        }

        # Если выбран внешний язык, загружаем или скачиваем его
        if self.language not in ('ru', 'en', 'uk'):
            if not self.load_language(self.language):
                self.language = 'en'

    def download_language(self, lang_code):
        os.makedirs(self.languages_dir, exist_ok=True)
        dest_path = os.path.join(self.languages_dir, f"lang-{lang_code}.py")
        temp_path = dest_path + ".tmp"

        urls = [
            f"{self.BASE_DOWNLOAD_URL}/lang-{lang_code}.py",
            f"http://miunlock.su/download/languages/lang-{lang_code}.py",
            f"http://212.113.104.87/download/languages/lang-{lang_code}.py"
        ]

        # 1. Try requests library (fastest, no Windows WPAD proxy delay)
        try:
            import requests
            try:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            except Exception:
                pass
            for url in urls:
                try:
                    resp = requests.get(
                        url,
                        timeout=(4, 8),
                        headers={
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) XiaomiUnlockTool/8.2',
                            'Host': 'miunlock.su'
                        },
                        verify=False
                    )
                    if resp.status_code == 200 and len(resp.content) > 100:
                        with open(temp_path, 'wb') as out_f:
                            out_f.write(resp.content)
                        if os.path.exists(dest_path):
                            try:
                                os.remove(dest_path)
                            except Exception:
                                pass
                        os.replace(temp_path, dest_path)
                        return dest_path
                except Exception as req_err:
                    print(f"[LanguageDownload] requests failed for {url}: {req_err}")
        except ImportError:
            pass

        # 2. Fallback to urllib.request with WPAD bypass (ProxyHandler({})) and SSL unverified context
        for url in urls:
            try:
                import urllib.request
                import ssl
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                opener = urllib.request.build_opener(
                    urllib.request.ProxyHandler({}),
                    urllib.request.HTTPSHandler(context=ctx)
                )
                req = urllib.request.Request(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) XiaomiUnlockTool/8.2',
                        'Host': 'miunlock.su'
                    }
                )
                with opener.open(req, timeout=8) as resp:
                    if resp.status == 200:
                        data = resp.read()
                        if len(data) > 100:
                            with open(temp_path, 'wb') as out_f:
                                out_f.write(data)
                            if os.path.exists(dest_path):
                                try:
                                    os.remove(dest_path)
                                except Exception:
                                    pass
                            os.replace(temp_path, dest_path)
                            return dest_path
            except Exception as e:
                print(f"[LanguageDownload] urllib failed for {url}: {e}")

        return None

    def is_download_needed(self, lang_code):
        """Возвращает True только если язык не встроен и файл еще не скачан на диск."""
        if lang_code in ('ru', 'en', 'uk'):
            return False
        dest_path = os.path.join(self.languages_dir, f"lang-{lang_code}.py")
        return not os.path.isfile(dest_path)

    @staticmethod
    def get_display_name(lang_code):
        names = {
            'ru': 'Русский (ru)',
            'en': 'English (en)',
            'uk': 'Українська (uk)',
            'es': 'Español (es)',
            'pt': 'Português (pt)',
            'id': 'Bahasa Indonesia (id)',
            'zh': '中文 (zh)'
        }
        return names.get(lang_code, str(lang_code).upper())

    def load_language(self, lang_code):
        if lang_code in self.translations:
            return True
        if lang_code == 'ru':
            self.translations['ru'] = self.get_russian()
            return True
        elif lang_code == 'en':
            self.translations['en'] = self.get_english()
            return True
        elif lang_code == 'uk':
            self.translations['uk'] = self.get_ukrainian()
            return True

        os.makedirs(self.languages_dir, exist_ok=True)
        dest_path = os.path.join(self.languages_dir, f"lang-{lang_code}.py")
        if not os.path.isfile(dest_path):
            downloaded = self.download_language(lang_code)
            if not downloaded or not os.path.isfile(dest_path):
                return False

        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(f"lang_{lang_code}", dest_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, 'get_translations'):
                    self.translations[lang_code] = mod.get_translations()
                    return True
                elif hasattr(mod, 'translations'):
                    self.translations[lang_code] = mod.translations
                    return True
        except Exception as e:
            print(f"Error loading language file '{dest_path}': {e}")
            try:
                if os.path.exists(dest_path):
                    os.remove(dest_path)
            except Exception:
                pass
        return False

    def set_language(self, language):
        if language not in self.SUPPORTED_LANGUAGES:
            language = 'en'
        if language in ('ru', 'en', 'uk'):
            self.language = language
            return True
        if self.load_language(language):
            self.language = language
            return True
        return False

    def tr(self, key, *args):
        translations = self.translations.get(self.language, self.translations.get('en', {}))
        value = translations.get(key, self.translations.get('en', {}).get(key, key))
        if args:
            try:
                return value.format(*args)
            except (IndexError, KeyError, ValueError):
                return value
        return value

    def get_russian(self):
        return {
            'title': "Xiaomi Unlock Tool",
            'main_title': "Xiaomi Unlock Tool",
            'desc': (
                "Инструмент для автоматической отправки заявки на Unlock\n"
                "От: pktloss, New G3n\n"
                "Версия: 8.2"
            ),
            'desc_manual': (
                "Ручной режим - выберите время отправки заявки вручную\n"
                "От: pktloss, New G3n\n"
                "Версия: 8.2"
            ),
            'params': "Параметры",
            'tab_unlock': "Подача заявок",
            'tab_settings': "Настройки и инструкция",
            'tab_hyperos1_bypass': "HyperOS 1 Bypass",
            'tab_mi_unlock': "Mi Unlock",
            'hyperos1_bypass_title': "HyperOS 1 Bypass",
            'hyperos1_bypass_desc': "Данная функция находится в разработке.\nОбход ограничений HyperOS 1 будет доступен в следующих обновлениях.",
            'hyperos1_bypass_return_btn': "Вернуться к подаче заявок",
            'beijing_time_title': "Пекинское время (UTC+8)",
            'beijing_submission_hint': "Подача заявки осуществляется в 23:59:58 - 59 по Пекину",
            'beijing_clock_collapse': "Свернуть",
            'beijing_clock_expand': "Развернуть",
            'log_success_prefix': "УСПЕХ!",
            'log_code_message': "Код: {code} | Сообщение: {msg}",
            'log_request_parse_error': "[Ошибка обработки ответа] Не удалось распарсить JSON: {data}",
            'log_request_failed_no_response': "[Ошибка] Не удалось отправить запрос (нет ответа)",
            'log_request_exception': "[Ошибка запроса] {error}",
            'cookie_label': "New_bbs_ServiceToken:",
            'cookie_placeholder': "Вставьте ваш токен здесь...",
            'timings_btn': "Настройка таймингов",
            'timings_dialog_title': "Настройка таймингов",
            'timings_desc': "Выберите тайминги (смещения в мс) для авто-отправки в 23:59:59:",
            'timings_region_default': "Регион: Europe (по умолчанию выбрано 6 таймингов)",
            'timings_min_warning': "Выберите хотя бы 1 тайминг!",
            'timings_risk_warning': "⚠️ Выбор слишком большого количества запросов может привести к временному бану на отправку заявок, а слишком малый выбор таймингов в неправильное время может вызвать неудачную отправку.",
            'timings_count_label': "Выбрано: {} из {}",
            'timings_reset_btn': "Сбросить по умолчанию",
            'timings_save_btn': "Сохранить и закрыть",
            'sections_menu': "Меню разделов",
            'profiles_btn': "Профили",
            'profiles_title': "Профили таймингов",
            'profile_europe': "Европейский",
            'profile_asia': "Азиатский",
            'profile_usa_africa': "США / Африка",
            'color_picker_title': "Выбор цвета темы",
            'color_picker_accept': "Принять",
            'color_picker_cancel': "Закрыть",
            'color_picker_current': "Текущий:",
            'color_picker_selected': "Выбранный цвет:",
            'color_picker_palette': "Палитра готовых цветов:",
            'color_picker_red': "Красный (R)",
            'color_picker_green': "Зеленый (G)",
            'color_picker_blue': "Синий (B)",
            'animations_coming_soon': "Анимации будут добавлены в будущем",
            'copy_address_btn': "📋 Копировать",
            'address_copied': "✓ Скопировано!",
            'timings_slots_title': "Настройка 15 таймингов (сек:мс):",
            'login_btn': "Войти в аккаунт",
            'check_eligibility_btn': "Проверить возможность подачи",
            'checking_eligibility': "Проверка возможности подачи заявки...",
            'eligibility_eligible_title': "Проверка статуса",
            'login_title': "Авторизация Xiaomi Account",
            'login_subtitle': "Автоматическое получение New_bbs_serviceToken",
            'login_tab_qr': "QR-код / Браузер",
            'login_tab_existing': "Сохраненный аккаунт",
            'login_existing_found': "Обнаружена сохраненная сессия Mi Account",
            'login_existing_id': "ID аккаунта: {}",
            'login_use_existing_btn': "⚡ Использовать этот аккаунт",
            'login_qr_scan_tip': "Отсканируйте QR-код в приложении Mi Community\nили камерой телефона Xiaomi",
            'login_open_browser_btn': "🌐 Войти через браузер",
            'login_refresh_qr': "🔄 Обновить QR-код",
            'login_waiting': "Ожидание подтверждения авторизации...",
            'login_qr_expired': "QR-код устарел. Нажмите «Обновить QR-код».",
            'login_loading_qr': "⏳ Загрузка QR-кода...",
            'login_browser_opened': "Страница входа открыта в браузере. Ожидание завершения...",
            'login_refreshing_qr': "Обновление QR-кода...",
            'login_qr_fetch_error': "Ошибка получения QR-кода: {}",
            'login_authorized_extracting': "Авторизация подтверждена! Извлечение токена...",
            'login_extracting_token': "Извлечение токена...",
            'login_session_expired': "Сессия устарела",
            'login_success': "Авторизация успешна! new_bbs_serviceToken получен.",
            'login_error': "Ошибка авторизации: {}",
            'login_token_extract_error': "Не удалось извлечь токен из ответа сервера.",
            'close_btn': "Закрыть",
            'log_token_check_success': "Проверка токена/статуса успешно пройдена.",
            'log_token_check_skipped': "Предупреждение: проверка токена отключена в настройках, продолжаем...",
            'log_mode2_selected': "Выбран Авторежим №2 (HTTP-spam по 23:59:59)",
            'log_mode2_ntp_saved': "Авторежим №2: NTP синхронизация сохранена, режим без измерения пинга",
            'status_mode2_waiting': "Авторежим №2: ожидание 23:59:59",
            'log_mode2_beijing_reached': "Авторежим №2: время 23:59:59 по Пекину достигнуто",
            'status_mode2_sending': "Авторежим №2: отправка HTTP-пакета",
            'mode2_prefix': "Авторежим #2",
            'mode2_timing': "тайминг",
            'log_mode2_plan_sent': "HTTP spam план отправлен",
            'mode2_using_device_id': "[Авторежим #2 HTTP #{}] Используется device_id: {}",
            'request_prefix': "Запрос",
            'req_using_device_id': "[Запрос #{}] Используется device_id: {}",
            'log_ping_start_http_tcp': "Начинаем измерение HTTP и TCP пингов...",
            'log_ping_avg_http': "Средний HTTP пинг: {:.2f} мс",
            'log_ping_http_failed': "HTTP пинг не удалось измерить",
            'log_ping_avg_tcp': "Средний TCP пинг: {:.2f} мс",
            'log_ping_tcp_failed': "TCP пинг не удалось измерить",
            'status_get_failed': "[Ошибка] Не удалось получить статус разблокировки.",
            'status_app_approved_checking': "[Статус] Заявка одобрена, проверка статуса...",
            'status_app_rejected_100001': "[Статус] Заявка отклонена, ошибка запроса (код 100001).",
            'status_app_possibly_approved': "[Статус] Заявка возможно одобрена, проверка статуса...",
            'success_dialog_title': "Успех!",
            'success_dialog_message': "Успешно! Попробуйте привязать аккаунт.",
            'theme_dark_only': "Тёмная тема (только тёмная тема доступна)",
            'confirm': "Я подтверждаю риск возможного бана аккаунта",
            'info': "Информация",
            'status_ready': "Готов к работе",
            'ping': "Пинг: не измерен",
            'time': "Время: не синхронизировано",
            'start_btn': "Начать подачу заявки",
            'instructions_btn': "Инструкция и настройки скрипта",
            'exit_btn': "Выход",
            'log': "Лог выполнения",
            'clear_log_btn': "Очистить",
            'unlock_start': "Начало процесса разблокировки...",
            'device_id_gen': "Сгенерирован deviceId: {}",
            'ping_start': "Начинаем вычисление пинга...",
            'ping_server': "Пинг до {}: {:.2f} мс",
            'ping_failed': "Не удалось получить пинг до сервера {}",
            'ping_error': "Ошибка при пинге {}: {}",
            'open_miflash': "MiFlash Unlock",
            'update_not_available': "Обновлений не найдено",
            'update_check_error': "Ошибка при проверке обновлений",
            'social_telegram': "Telegram",
            'social_reddit': "Reddit",
            'social_github': "GitHub",
            'social_site_script': "Сайт Скрипта",
            'theme_color_label': 'Цвет темы',
            'theme_color_picker': 'Выбрать цвет',
            'theme_color_apply': 'Применить',
            'theme_color_hint': 'Введите HEX (#RRGGBB) или RGB (R,G,B)',
            'theme_color_error_title': 'Ошибка цвета',
            'theme_color_error': 'Введите корректный HEX (#RRGGBB) или RGB (R,G,B).',
            'theme_color_placeholder': '#D0BCFF',
            'ping_default': "Не удалось получить пинг ни до одного сервера!\nИспользуем значение по умолчанию: {} мс",
            'ping_avg': "Средний пинг: {:.2f} мс",
            'ntp_connect': "Попытка подключения к NTP серверу: {}",
            'ntp_time': "Пекинское время, полученное с сервера {}: {}",
            'ntp_failed': "Не удалось подключиться ни к одному из NTP серверов.",
            'time_wait': "Ожидание времени для пинга (23:59:30 по Пекину)...",
            'target_time': "Ожидание до {} (скорректировано по пингу {} мс для достижения полуночи)",
            'target_time_manual': "Ожидание до {} (ручной режим)",
            'time_reached': "Время достигнуто: {}. Начинаем отправку запроса...",
            'cookie_skipped': "Проверка cookie пропущена согласно настройкам",
            'cookie_expired': "Cookie устарел, обновите его.",
            'account_ready': "[Статус] Аккаунт может подать заявку на разблокировку.",
            'account_blocked': "[Статус] На аккаунте блокировка на подачу заявки до {} (Месяц/День).",
            'account_new': "[Статус] Аккаунт создан менее 30 дней назад.",
            'account_approved': "[Статус] Заявка одобрена, разблокировка возможна до {}.",
            'account_unknown': "[Ошибка] Неизвестный статус.",
            'status_error': "[Ошибка проверки статуса] {}",
            'request_sent': "\nОтправка запроса в {} (UTC+8)",
            'response_received': "Ответ получен в {} (UTC+8)",
            'request_failed': "[Ошибка] Не удалось отправить запрос",
            'response_error': "[Ошибка обработки ответа] {}",
            'request_error': "[Ошибка запроса] {}",
            'confirm_warning': "Пожалуйста, подтвердите, что понимаете все риски!",
            'cookie_error': "Введите значение cookie!",
            'token_status_check_failed': "Ошибка: проверка токена/статуса не пройдена. Подача заявки остановлена. Отключите 'Отключить проверку Token Cookie перед отправкой', если хотите обойти проверку.",
            'time_error': "Не удалось синхронизировать время!",
            'settings_saved': "\nНастройки сохранены:",
            'cookie_check': "Проверка Token Cookie: {}",
            'default_ping': "Пинг по умолчанию: {} мс",
            'ping_note': "Это значение будет использовано, если не удастся измерить пинг до серверов.",
            'saved': "Настройки успешно сохранены!",
            'instructions_title': "Инструкция и настройки скрипта",
            'about_title': "О скрипте",
            'about_content': (
                "Инструмент для автоматической отправки\n"
                "заявки на разблокировку загрузчика\n"
                "устройств Xiaomi на Global HyperOS\n\n"
                "Версия скрипта: 8.2"
            ),
            'general_title': "Требования",
            'general_content': (
                "1. Mi аккаунт старше 30 дней\n \n"
                "2. Mi Community аккаунт должен быть с\n \n"
                "регионом Global\n \n"
                "3. Разблокировка устройств со всеми\n"
                "индексами кроме Китайских (CNXM)\n \n"
                "4. Устройство должно быть на HyperOS 1-3"
            ),
            'firefox_title': "FireFox | Edge",
            'firefox_content': (
                "1. Скачайте расширение Cookie Editor\n\n"
                "2. Авторизуйтесь в аккаунт, предварительно\n"
                "выйдя из него, на сайте Xiaomi Mi Community\n"
                "http://c.mi.com/global\n"
                "или на сайте\n"
                "http://mi.com\n\n"
                "3. В окне Cookie Editor извлеките\n"
                "new_bbs_token и скопируйте его\n\n"
                "Особенности работы:\n"
                "1. Все время в скрипте является Пекинским"
            ),
            'chrome_title': "Chrome",
            'chrome_content': (
                "1. Авторизуйтесь в аккаунте, предварительно\n"
                "выйдя из него, на сайте Mi Community\n"
                "https://c.mi.com/global\n"
                "или на сайте\n"
                "https://mi.com\n\n"
                "2. В строку браузера вводим команду:\n\n"
                "javascript :(function(){var token=document.cookie.match(/popRunToken=([^;]+)/);"
                "if(token){prompt(\"Copy the token:\", token[1]);}"
                "else{alert(\"Token not found\");}})()\n\n"
                "*не забудьте убрать пробел после javascript когда вставите команду в строку браузера*\n\n"
                "3. Скопируйте значение token из всплывающего окна\n\n"
                "Особенности работы:\n \n"
                "1. Все время в скрипте является Пекинским"
            ),
            'trouble_title': "Решение проблем",
            'trouble_content': """Проблема: Cookie Editor не выдает new_bbs_serviceToken

Решение:

1. Переустановите расширение Cookie Editor

2. Выйдите и зайдите в аккаунт заново

Проблема: Куки просрочен или не работает

Возможные причины:

• Регион аккаунта не Global (переключите)

• Куки действительно просрочены

Проблема: Лимит заявок исчерпан

Решение:

Проверьте статус в Mi Unlock в настройках телефона

Проблема: Ошибки 10001 и другие

Решение:

Скрипт не смог отправить заявку

Обратитесь к разработчику:

• В чат ТГК:

https://t.me/miunlocktoolrevamp""",
            'authors_title': "Авторы",
            'authors_developers_title': "Разработчики Скрипта",
            'authors_pc_cli_dev': "Разработчик PC и CLI версии скрипта",
            'authors_web_android_dev': "Разработчик Сайта скрипта и Android версии",
            'authors_base_script': "Скрипт написан на основе скрипта:",
            'authors_social_links': "Ссылки на Соц Сети",
            'authors_donate_title': "Пожертвовать на разработку",
            'authors_donate_btn': "DonationAlerts",
            'authors_crypto_network': "USDT сеть TON",
            'authors_content': """Разработчики Скрипта:
• pktloss, New G3n

Разработчик PC и CLI версии скрипта:
• New G3n

Разработчик Сайта скрипта и Android версии:
• pktloss

Скрипт написан на основе скрипта:
• Vierta

Ссылки на Соц Сети:
• Telegram: https://t.me/miunlocktoolrevamp
• 4PDA: https://4pda.to/forum/index.php?showtopic=721838&view=findpost&p=145201115
• GitHub: https://github.com/AsInsideOut/miunlocktool
• Сайт: https://miunlock.su/

Пожертвовать на разработку:
• DonationAlerts: https://dalink.to/asinsideout
• Криптокошелек:
UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG
USDT сеть TON

Версия скрипта: 8.2""",
            'cookie_checkbox': "Отключить проверку Token Cookie перед отправкой",
            'final_unlock_checkbox': "Подача окончена. Попробуйте привязать телефон при любых результатах.",
            'ping_label': "Пинг по умолчанию (мс):",
            'color_theme_label': "Цветовая тема интерфейса:",
            'color_theme_xiaomi_orange': "Xiaomi Orange",
            'color_theme_red_sun': "Red Sun",
            'color_theme_blue_world': "Blue World",
            'save_btn': "Сохранить",
            'ping_error_title': "Ошибка",
            'ping_error_msg': "Пинг должен быть положительным числом!",
            'cookie_error_title': "Ошибка",
            'error_title': "Ошибка",
            'account_blocked_title': "Информация",
            'account_new_title': "Информация",
            'account_approved_title': "Успех",
            'unknown_status_title': "Ошибка",
            'install_error': "Ошибка установки",
            'import_error': "Ошибка импорта",
            'settings': "Настройки",
            'cookie_check_state': "Отключена",
            'ban_risk': "Я подтверждаю риск возможного бана аккаунта",
            'submit_application': "Начать подачу заявки",
            'script_info': "Инструкция и настройки скрипта",
            'exit': "Выход",
            'execution_log': "Лог выполнения",
            'unlock_process': "Начало процесса разблокировки...",
            'auto_mode': "Авто режим",
            'auto_mode_1': "Авторежим №1",
            'auto_mode_2': "Авторежим",
            'manual_mode': "Ручной режим",
            'manual_time_label': "Время отправки (секунды):",
            'manual_time_hint': "58.5 - 59.8 (например: 59.1)",
            'manual_mode_start': "Ручной режим: отправка в 23:59:{}",
            'manual_time_error': "Некорректное время. Используйте формат 58.5 - 59.8",
            'application_not_submitted': "[Статус] Заявка не подана, лимит превышен, попробуйте снова {} (Месяц/День).",
            'device_binding_hint': "Попробуйте привязать устройства в Настройках Раздел Статус Mi Unlock",
            'theme_label': "Тема интерфейса:",
            'theme_system': "Как в системе",
            'theme_light': "Светлая",
            'theme_dark': "Тёмная",
            'theme_locked_notice': "Временно доступна только тёмная тема",
            'mode_label': "Режим работы:",
            'cookies_title': "Получение Cookies",
            'expand_cookies': "▶ Получение Cookies",
            'collapse_cookies': "▼ Получение Cookies",
            'check_updates': "Проверить обновления",
            'update_available': "Доступно новое обновление",
            'update_checking': "Проверка обновлений...",
            'update_error': "Ошибка при проверке обновлений",
            'current_version': "Текущая версия: {}",
            'your_region': "Ваш Регион: {}",
            'header_region': "Регион: {}",
            'latest_version': "Последняя версия: {}",
            'update_btn_ok': "Окей",
            'update_btn_update': "Обновить",
            'update_message': "Доступна новая версия {}! Хотите перейти на страницу загрузки?",
            'time_synchronized': "Время синхронизировано",
            'ms': "мс",
            'default': "по умолчанию",
            'welcome_title': "Xiaomi Unlock Tool",
            'welcome_text': (
                "Добро пожаловать в Xiaomi Unlock Tool!\n\n"
                "Благодаря нашей программе вы сможете разблокировать загрузчик на устройствах с HyperOS.\n\n"
                "ПЕРЕД ИСПОЛЬЗОВАНИЕМ ВНИМАТЕЛЬНО ПРОЧИТАЙТЕ ИНСТРУКЦИЮ!\n\n"
                "1. Использование данного инструмента может привести к блокировке отправки запросов на разблокировку загрузчика.\n\n"
                "2. Инструмент работает на всех глобальных прошивках (MIXM, EUXM, INXM, TRXM...)\n"
                "   и НЕ работает с китайскими (CNXM) прошивками.\n\n"
                "3. Обязательные требования:\n"
                "   • Mi аккаунт старше 30 дней\n"
                "   • Регин в Mi Community стоит Global\n"
                "   • Устройство на HyperOS 1-3\n\n"
                "4. Вся ответственность на вас и разработчики НЕ несут ответственность за ваше устройство.\n\n"
                "Нажмите 'Продолжить', чтобы начать работу."
            ),
            'welcome_btn': "Продолжить",
            'ping_hint': "Это значение будет использовано, если не удастся измерить пинг до серверов.",
            'color_theme_xiaomi': "Xiaomi Orange",
            'color_theme_blue': "Blue World",
            'color_theme_red': "Red Sun",
            'language_label': "Язык",
            'log_to_txt_checkbox': "Логирование в TXT файле",
            'animations_checkbox': "Анимации Интерфейса",
            'animations_development': "В разработке",
            'input_label': "Ввод",
            'application_status': "Статус заявок: {}",
            'application_status_not_sent': "Не отправлены",
            'application_status_sending': "Отправление",
            'application_status_success': "Удачно",
            'application_status_unknown': "Неизвестно",
            'application_status_failed': "Не удачно",
            'spam_mode_checkbox': "Спам-отправка (в Авто-режиме)",
            'spam_mode_desc': "Отправляет запросы в 23:59 на 58.6, 58.8 (скорректировано по пингу).\nЕсли отключено, отправляется один запрос в оптимальное время.",
            'ping_not_measured_manual': "Пинг: не измеряется (ручной режим)",
            'log_auto_mode_spam_selected': "Выбран автоматический режим (Спам-отправка - 5 запросов)",
            'log_auto_mode_single_selected': "Выбран автоматический режим (Обычная отправка)",
            'log_manual_mode_selected': "Выбран ручной режим",
            'log_time_gt_2355': "Время > 23:58. Выполняем синхронизацию времени перед стартом...",
            'log_time_sync_success': "Время успешно синхронизировано!",
            'log_ping_wait': "Ожидание измерения пинга в 23:59:30 (Пекин)...",
            'status_ping_wait': "Ожидание 23:59:30 для измерения пинга...",
            'log_ping_time_passed': "Время измерения пинга прошло. Синхронизируем и измеряем сейчас...",
            'log_ping_start': "Время измерять пинг! Выполняем измерение...",
            'log_measuring_ping': "Измеряем пинг до серверов...",
            'log_ping_measured': "Пинг измерен: {} ms",
            'log_time_updated': "Время обновлено: {}",
            'log_resync_error': "Ошибка повторной синхронизации, продолжаем с текущим таймером.",
            'log_normal_mode_ping': "Обычный режим: вычисляем пинг...",
            'log_calculated_send_time': "Расчетное время отправки (для достижения полуночи): 23:59:{}",
            'log_spam_mode_targets': "РЕЖИМ СПАМА: Целевые времена (после коррекции пинга): {}",
            'status_spam_wait': "Ожидание спам-атаки...",
            'log_spam_sending_at': "[Спам #{}] Отправка запроса в 23:59:{}s",
            'log_spam_new_device_id': "[Спам #{}] Новый deviceId: {}",
            'log_spam_response_prefix': "[Спам #{}] Время: {}s",
            'log_spam_success_prefix': "УСПЕХ!",
            'log_spam_response_format': "{} | Код: {} | {}",
            'log_spam_parse_error': "[Спам #{}] Ошибка парсинга ответа: {}",
            'log_spam_no_response': "[Спам #{}] Нет ответа от сервера",
            'log_spam_send_error': "[Спам #{}] Ошибка отправки: {}",
            'login_user_label': "ID аккаунта / Email / Телефон:",
            'login_user_placeholder': "Введите логин",
            'login_pwd_label': "Пароль:",
            'login_pwd_placeholder': "********",
            'wb_instruction': "1. Нажмите кнопку ниже, чтобы открыть страницу подтверждения в браузере.\n2. После того как увидите сообщение 'R':'','S':'OK' на странице, скопируйте полную ссылку из адресной строки.",
            'wb_instruction_after_open': "Вставьте полную ссылку в поле ниже.",
            'wb_id_label': "Ссылка подтверждения (wb_id):",
            'wb_id_placeholder': "Вставьте ссылку сюда...",
            'open_confirmation_page': "Открыть страницу подтверждения",
            'login_button': "Войти и получить токен",
            'login_disabled_notice': "Временно недоступно",
            'logging_in': "Вход...",
            'login_fields_error': "Заполните все поля (логин, пароль и ссылку)!",
            'login_failed': "Ошибка входа",
            'login_failed_generic': "Ошибка входа. Проверьте данные.",
            'mi_unlock_title': "Mi Unlock Tool",
            'mi_unlock_checking_python': "Проверка наличия Python",
            'mi_unlock_upgrading': 'Установка обновления miunlock...',
            'mi_unlock_python_found': "Найден Python: {}",
            'mi_unlock_python_error_msg': (
                "Python не найден!\n\n"
                "Для работы Mi Unlock Tool необходим Python 3.8 или выше.\n\n"
                "Скачайте Python с официального сайта:\n"
                "https://www.python.org/downloads/\n\n"
                "ВНИМАНИЕ: При установке обязательно отметьте опцию\n"
                "'Add Python to PATH' (Добавить Python в переменные среды)"
            ),
            'mi_unlock_installing': "Установка пакета miunlock...",
            'mi_unlock_install_cmd': "Выполняется: pip install miunlock",
            'mi_unlock_already_installed': "Пакет miunlock уже установлен",
            'mi_unlock_install_success': "Пакет miunlock успешно установлен",
            'mi_unlock_install_error': "Ошибка установки miunlock!",
            'mi_unlock_starting': "Запуск Mi Unlock Tool...",
            'mi_unlock_launching': "Запуск miunlock...",
            'mi_unlock_file_not_found': "Файл не найден: {}",
            'mi_unlock_not_found': "Ошибка: miunlock не найден!",
            'mi_unlock_completed': "Mi Unlock Tool завершил работу",
            'mi_unlock_finished': "Программа завершена",
            'mi_unlock_error': "Ошибка: {}",
            'mi_unlock_critical_error': "Критическая ошибка: {}",
            'mi_unlock_close': "Закрыть",
            'mi_unlock_input_label': "Ввод для программы:",
            'mi_unlock_input_placeholder': "Введите ответ и нажмите Enter...",
            'mi_unlock_send_btn': "Отправить",
            'mi_unlock_input_prefix': "→ {}",
            'mi_unlock_input_error': "Ошибка отправки ввода: {}",
            'mi_unlock_stdout_error': "Ошибка чтения stdout: {}",
            'mi_unlock_stderr_error': "Ошибка чтения stderr: {}",
            'mi_unlock_auto_sending': "→ Авто-отправка Enter...",
            'mi_unlock_auto_send_error': "Ошибка авто-отправки: {}",
            'mi_unlock_read_error': "Ошибка чтения: {}",
            'mi_unlock_process_exit': "Процесс завершен с кодом: {}",
            'mi_unlock_initial_enter': "→ Авто-отправка начального Enter...",
            'mi_unlock_auto_send_final': "→ Авто-отправка финального Enter...",
            'pre_generation_title': "ПРЕДВАРИТЕЛЬНАЯ ГЕНЕРАЦИЯ DEVICE ID:",
            'pre_generation_main': "  Основной device_id: {}",
            'pre_generation_spam1': "  Спам device_id #1: {}",
            'pre_generation_spam2': "  Спам device_id #2: {}",
            'pre_generation_spam3': "  Спам device_id #3: {}",
            'pre_generation_spam4': "  Спам device_id #4: {}",
            'pre_generation_spam5': "  Спам device_id #5: {}",
            'logs_sent': "Логи успешно отправлены на сервер",
            'logs_send_error': "Ошибка отправки логов: {}",
            'spam_using_device_id': "[Спам #{}] Используется device_id: {}",
            'send_with_token': "Отправка с токеном #{}",
            # Новые ключи для HTTP/TCP пинга и мульти-запросов
            'tcp_ping_label': "TCP пинг",
            'http_ping_label': "HTTP пинг",
            'measuring_pings': "Измерение пингов (HTTP и TCP)...",
            'scheduling_requests': "Планирование запросов...",
            'http_request': "HTTP запрос #{}",
            'tcp_request': "TCP запрос #{}",
            'ping_measure_done': "Измерение пинга завершено.",
            'ping_measure_time_come': "Время измерения пинга уже наступило, начинаем сейчас",
            'ping_http_default': "HTTP пинг не удалось измерить, используем значение по умолчанию: {} мс",
            'ping_tcp_default': "TCP пинг не удалось измерить, используем значение по умолчанию: {} мс",
            'ping_measure_result': "Измерение завершено. HTTP: {:.2f} мс, TCP: {:.2f} мс",
            'http_request_log': "HTTP запрос #{}: device_id={}, отправка через {:.3f}с",
            'tcp_request_log': "TCP запрос #{}: device_id={}, отправка через {:.3f}с",
            'mi_unlock_label': "Mi Unlock",
            'mi_unlock_desc': (
                "Инструмент для разблокировки при помощи Mi Unlock\n"
                "От: pktloss, New G3n\n"
                "Версия: 8.2"
            ),
            'mi_unlock_python_not_found': "Python: не найден",
            'mi_unlock_python_found_label': "Python: {}",
            'mi_unlock_package_not_installed': "miunlock: не установлен",
            'mi_unlock_package_installed': "miunlock: установлен",
            'mi_unlock_start_button': "Запустить Mi Unlock",
            'mi_unlock_process_interrupted': "Процесс прерван пользователем",
            'mi_unlock_log_title': "Лог выполнения",
            'mi_unlock_drivers_button': "Скачать драйверы",
            'lang_download_title': "Скачивание языка",
            'lang_download_msg': "Скачивание языкового пакета...",
            'lang_download_failed': "Не удалось загрузить языковой пакет '{}'. Проверьте интернет-соединение.",
        }

    def get_english(self):
        return {
            'title': "Xiaomi Unlock Tool",
            'main_title': "Xiaomi Unlock Tool",
            'desc': (
                "Tool for automatic unlock request submission\n"
                "By: pktloss, New G3n\n"
                "Version: 8.2"
            ),
            'desc_manual': (
                "Manual mode - select the time to submit manually\n"
                "By: pktloss, New G3n\n"
                "Version: 8.2"
            ),
            'params': "Parameters",
            'tab_unlock': "Submit Application",
            'tab_settings': "Settings and Instructions",
            'tab_hyperos1_bypass': "HyperOS 1 Bypass",
            'tab_mi_unlock': "Mi Unlock",
            'hyperos1_bypass_title': "HyperOS 1 Bypass",
            'hyperos1_bypass_desc': "This feature is currently under development.\nHyperOS 1 Bypass will be available in future updates.",
            'hyperos1_bypass_return_btn': "Back to Application Submission",
            'beijing_time_title': "Beijing Time (UTC+8)",
            'beijing_submission_hint': "Application is submitted at 23:59:58 - 59 Beijing time",
            'beijing_clock_collapse': "Collapse",
            'beijing_clock_expand': "Expand",
            'log_success_prefix': "SUCCESS!",
            'log_code_message': "Code: {code} | Message: {msg}",
            'log_request_parse_error': "[Response processing error] Failed to parse JSON: {data}",
            'log_request_failed_no_response': "[Error] Failed to send request (no response)",
            'log_request_exception': "[Request error] {error}",
            'cookie_label': "New_bbs_ServiceToken:",
            'cookie_placeholder': "Paste your token here...",
            'timings_btn': "Timing Settings",
            'timings_dialog_title': "Timing Settings",
            'timings_desc': "Select timings (offsets in ms) for auto-submission at 23:59:59:",
            'timings_region_default': "Region: Europe (6 timings selected by default)",
            'timings_min_warning': "At least 1 timing must be selected!",
            'timings_risk_warning': "⚠️ Selecting too many requests may lead to a temporary ban on submitting applications, while selecting too few timings at the wrong time may cause submission failure.",
            'timings_count_label': "Selected: {} of {}",
            'timings_reset_btn': "Reset to Defaults",
            'timings_save_btn': "Save & Close",
            'sections_menu': "Section Menu",
            'profiles_btn': "Profiles",
            'profiles_title': "Timing Profiles",
            'profile_europe': "Europe",
            'profile_asia': "Asia",
            'profile_usa_africa': "USA / Africa",
            'color_picker_title': "Theme Color Picker",
            'color_picker_accept': "Accept",
            'color_picker_cancel': "Close",
            'color_picker_current': "Current:",
            'color_picker_selected': "Selected color:",
            'color_picker_palette': "Preset color palette:",
            'color_picker_red': "Red (R)",
            'color_picker_green': "Green (G)",
            'color_picker_blue': "Blue (B)",
            'animations_coming_soon': "Animations will be added in the future",
            'copy_address_btn': "📋 Copy",
            'address_copied': "✓ Copied!",
            'timings_slots_title': "Configure 15 timing slots (sec:ms):",
            'login_btn': "Log In to Account",
            'check_eligibility_btn': "Check eligibility",
            'checking_eligibility': "Checking account eligibility...",
            'eligibility_eligible_title': "Eligibility Check",
            'login_title': "Xiaomi Account Authorization",
            'login_subtitle': "Automatic New_bbs_serviceToken extraction",
            'login_tab_qr': "QR Code / Browser",
            'login_tab_existing': "Saved Account",
            'login_existing_found': "Active Mi Account session detected",
            'login_existing_id': "Account ID: {}",
            'login_use_existing_btn': "⚡ Use this account",
            'login_qr_scan_tip': "Scan the QR code in the Mi Community app\nor with your Xiaomi phone camera",
            'login_open_browser_btn': "🌐 Login with Browser",
            'login_refresh_qr': "🔄 Refresh QR Code",
            'login_waiting': "Waiting for authorization confirmation...",
            'login_qr_expired': "QR code expired. Click 'Refresh QR Code'.",
            'login_loading_qr': "⏳ Loading QR code...",
            'login_browser_opened': "Login page opened in browser. Waiting for completion...",
            'login_refreshing_qr': "Refreshing QR code...",
            'login_qr_fetch_error': "Failed to fetch QR code: {}",
            'login_authorized_extracting': "Authorization confirmed! Extracting token...",
            'login_extracting_token': "Extracting token...",
            'login_session_expired': "Session expired",
            'login_success': "Authorization successful! new_bbs_serviceToken extracted.",
            'login_error': "Authorization error: {}",
            'login_token_extract_error': "Failed to extract token from server response.",
            'close_btn': "Close",
            'log_token_check_success': "Token and status check passed successfully.",
            'log_token_check_skipped': "Warning: token verification is disabled in settings, continuing...",
            'log_mode2_selected': "Auto Mode #2 selected (HTTP spam targeting 23:59:59)",
            'log_mode2_ntp_saved': "Auto Mode #2: NTP synchronization active, mode without ping measurement",
            'status_mode2_waiting': "Auto Mode #2: waiting for 23:59:59",
            'log_mode2_beijing_reached': "Auto Mode #2: Beijing time 23:59:59 reached",
            'status_mode2_sending': "Auto Mode #2: sending HTTP packet",
            'mode2_prefix': "Auto Mode #2",
            'mode2_timing': "timing",
            'log_mode2_plan_sent': "HTTP spam schedule dispatched",
            'mode2_using_device_id': "[Auto Mode #2 HTTP #{}] Using device_id: {}",
            'request_prefix': "Request",
            'req_using_device_id': "[Request #{}] Using device_id: {}",
            'log_ping_start_http_tcp': "Measuring HTTP and TCP pings...",
            'log_ping_avg_http': "Average HTTP ping: {:.2f} ms",
            'log_ping_http_failed': "Failed to measure HTTP ping",
            'log_ping_avg_tcp': "Average TCP ping: {:.2f} ms",
            'log_ping_tcp_failed': "Failed to measure TCP ping",
            'status_get_failed': "[Error] Failed to get unlock status.",
            'status_app_approved_checking': "[Status] Application approved, checking status...",
            'status_app_rejected_100001': "[Status] Application rejected, request error (code 100001).",
            'status_app_possibly_approved': "[Status] Application possibly approved, checking status...",
            'success_dialog_title': "Success!",
            'success_dialog_message': "Success! Try to bind your account.",
            'theme_dark_only': "Dark theme (only dark theme is available)",
            'confirm': "I acknowledge the risk of possible account ban",
            'info': "Information",
            'status_ready': "Ready to start",
            'ping': "Ping: not measured",
            'time': "Time: not synchronized",
            'start_btn': "Start Application",
            'instructions_btn': "Instructions and Script Settings",
            'exit_btn': "Exit",
            'log': "Execution Log",
            'clear_log_btn': "Clear",
            'unlock_start': "Starting unlock process...",
            'device_id_gen': "Generated deviceId: {}",
            'ping_start': "Starting ping calculation...",
            'ping_server': "Ping to {}: {:.2f} ms",
            'ping_failed': "Failed to get server ping {}",
            'ping_error': "Error pinging {}: {}",
            'ping_default': "Failed to get server ping!\nUsing default value: {} ms",
            'open_miflash': "MiFlash Unlock",
            'social_telegram': "Telegram",
            'social_reddit': "Reddit",
            'social_github': "GitHub",
            'social_site_script': "Script Website",
            'theme_color_label': 'Theme color',
            'theme_color_picker': 'Choose color',
            'theme_color_apply': 'Apply',
            'theme_color_hint': 'Enter HEX (#RRGGBB) or RGB (R,G,B)',
            'theme_color_error_title': 'Color error',
            'theme_color_error': 'Enter a valid HEX (#RRGGBB) or RGB (R,G,B).',
            'theme_color_placeholder': '#D0BCFF',
            'ping_avg': "Average ping: {:.2f} ms",
            'ntp_connect': "Attempting to connect to NTP server: {}",
            'ntp_time': "Beijing time received from server {}: {}",
            'ntp_failed': "Failed to connect to any NTP servers.",
            'time_wait': "Waiting for ping time (23:59:30 Beijing time)...",
            'target_time': "Waiting until {} (adjusted for ping {} ms to hit midnight)",
            'target_time_manual': "Waiting until {} (manual mode)",
            'time_reached': "Time reached: {}. Starting request submission...",
            'cookie_skipped': "Cookie check skipped according to settings",
            'cookie_expired': "Cookie expired, please update (see settings, Troubleshooting)",
            'account_ready': "[Status] Account can submit unlock request.",
            'account_blocked': "[Status] Account has submission ban until {} (Month/Day).",
            'account_new': "[Status] Account created less than 30 days ago.",
            'account_approved': "[Status] Application approved, unlock possible until {}.",
            'account_unknown': "[Error] Unknown status.",
            'update_not_available': "No updates found",
            'update_check_error': "Error checking for updates",
            'status_error': "[Status check error] {}",
            'request_sent': "\nSending request at {} (UTC+8)",
            'response_received': "Response received at {} (UTC+8)",
            'request_failed': "[Error] Failed to send request",
            'response_error': "[Response processing error] {}",
            'request_error': "[Request error] {}",
            'confirm_warning': "Please confirm that you understand all risks!",
            'cookie_error': "Enter cookie value!",
            'token_status_check_failed': "Error: token/status check failed. Submission is stopped. Disable 'Disable Token Cookie check before submission' if you want to bypass the check.",
            'time_error': "Failed to synchronize time!",
            'settings_saved': "\nSettings saved:",
            'cookie_check': "Token Cookie check: {}",
            'default_ping': "Default ping: {} ms",
            'ping_note': "This value will be used if measuring ping to servers fails.",
            'saved': "Settings saved successfully!",
            'instructions_title': "Settings and instructions",
            'about_title': "About",
            'about_content': (
                "Tool for automatic request send\n"
                "for bootloader unlocking on\n"
                "Xiaomi devices that runs HyperOS\n\n"
                "Script version: 8.2"
            ),
            'general_title': "Requirements",
            'general_content': (
                "1. Mi account must be older than 30 days\n \n"
                "2. Mi Community account must have\n \n"
                "Global region set\n \n"
                "3. Unlocking available for all devices\n"
                "except Chinese ROM (CNXM)\n \n"
                "4. Device is running HyperOS"
            ),
            'firefox_title': "FireFox | Edge",
            'firefox_content': (
                "1. Download Cookie Editor extension\n\n"
                "2. Log in to your account (after logging out)\n"
                "on Xiaomi Mi Community site:\n\n"
                "http://c.mi.com/global\n"
                "or \n"
                "http://mi.com\n\n"
                "3. In Cookie Editor window extract\n"
                "new_bbs_token and copy it\n\n"
                "Important notes:\n \n"
                "1. All times in script are Beijing time"
            ),
            'chrome_title': "Chrome",
            'chrome_content': (
                "1. Log in to your account (after logging out)\n"
                "on Xiaomi Mi Community site:\n"
                "https://c.mi.com/global\n"
                "or \n"
                "https://mi.com\n\n"
                "2. In browser address bar enter command:\n\n"
                "javascript :(function(){var token=document.cookie.match(/popRunToken=([^;]+)/);"
                "if(token){prompt(\"Copy the token:\", token[1]);}"
                "else{alert(\"Token not found\");}})()\n\n"
                "*remember to remove the space after javascript when pasting the command into the browser address bar*\n\n"
                "3. Copy the token value from the popup window\n\n"
                "Important notes:\n \n"
                "1. All times in script are Beijing time"
            ),
            'trouble_title': "Troubleshooting",
            'trouble_content': """Issue: CookieEditor doesn't show new_bbs_serviceToken

Solution:

1. Refresh page

2. Log out and sign in again

Issue: Cookie expired or not working

Possible reasons:

• Account region is not Global (switch it)

• Cookie is actually expired

Issue: Request limit reached

Solution:

Check status in Mi Unlock in phone settings

Issue: Errors 10001 and others

Solution:

Script failed to submit request

Contact developers:

• Via Telegram group:

https://t.me/miunlocktoolrevamp""",
            'authors_title': "Authors",
            'authors_developers_title': "Script Developers",
            'authors_pc_cli_dev': "PC & CLI Version Developer",
            'authors_web_android_dev': "Website & Android Version Developer",
            'authors_base_script': "Script is based on the script by:",
            'authors_social_links': "Social Links",
            'authors_donate_title': "Donate to Development",
            'authors_donate_btn': "DonationAlerts",
            'authors_crypto_network': "USDT TON network",
            'authors_content': """Script Developers:
• pktloss, New G3n

PC & CLI Version Developer:
• New G3n

Website & Android Version Developer:
• pktloss

Script is based on the script by:
• Vierta

Social Links:
• Telegram: https://t.me/miunlocktoolrevamp
• 4PDA: https://4pda.to/forum/index.php?showtopic=721838&view=findpost&p=145201115
• GitHub: https://github.com/AsInsideOut/miunlocktool
• Website: https://miunlock.su/

Donate to Development:
• DonationAlerts: https://dalink.to/asinsideout
• Crypto Wallet:
UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG
USDT TON network

Script version: 8.2""",
            'cookie_checkbox': "Disable Token Cookie check before submission",
            'final_unlock_checkbox': "Submission is complete. Try binding the phone regardless of the result.",
            'ping_label': "Default ping (ms):",
            'color_theme_label': "Color theme:",
            'color_theme_xiaomi_orange': "Xiaomi Orange",
            'color_theme_red_sun': "Red Sun",
            'color_theme_blue_world': "Blue World",
            'save_btn': "Save",
            'ping_error_title': "Error",
            'ping_error_msg': "Ping must be a positive number.",
            'cookie_error_title': "Error",
            'error_title': "Error",
            'account_blocked_title': "Information",
            'account_new_title': "Information",
            'account_approved_title': "Success",
            'unknown_status_title': "Error",
            'install_error': "Installation Error",
            'import_error': "Import Error",
            'settings': "Settings",
            'cookie_check_state': "Disabled",
            'ban_risk': "I acknowledge the risk of possible account ban",
            'submit_application': "Start Application",
            'script_info': "Instructions and Script Settings",
            'exit': "Exit",
            'execution_log': "Execution Log",
            'unlock_process': "Starting unlock process...",
            'auto_mode': "Auto Mode",
            'auto_mode_1': "Auto Mode #1",
            'auto_mode_2': "Auto Mode",
            'manual_mode': "Manual Mode",
            'manual_time_label': "Submission time (seconds):",
            'manual_time_hint': "58.5 - 59.8 (e.g.: 59.1)",
            'manual_mode_start': "Manual mode: sending at 23:59:{}",
            'manual_time_error': "Invalid time. Use format 58.5 - 59.8",
            'application_not_submitted': "[Status] Application not submitted, limit exceeded, try again on {} (Month/Day).",
            'device_binding_hint': "Try to bind devices in Settings, Mi Unlock Status section",
            'theme_label': "Interface theme:",
            'theme_system': "System",
            'theme_light': "Light",
            'theme_dark': "Dark",
            'theme_locked_notice': "Only the dark theme is temporarily available",
            'mode_label': "Operation mode:",
            'cookies_title': "Getting Cookies",
            'expand_cookies': "▶ Getting Cookies",
            'collapse_cookies': "▼ Getting Cookies",
            'check_updates': "Check for Updates",
            'update_available': "Update is available",
            'update_checking': "Checking for updates...",
            'update_error': "Error checking for updates",
            'current_version': "Current version: {}",
            'your_region': "Your Region: {}",
            'header_region': "Region: {}",
            'latest_version': "Latest version: {}",
            'update_btn_ok': "Alright",
            'update_btn_update': "Update",
            'update_message': "New version {} is available! Would you like to go to the download page?",
            'time_synchronized': "Time synchronized",
            'ms': "ms",
            'default': "default",
            'welcome_title': "Xiaomi Unlock Tool",
            'welcome_text': (
                "Welcome to Xiaomi Unlock Tool!\n\n"
                "IMPORTANT WARNING:\n\n"
                "BEFORE USING, CAREFULLY READ THE INSTRUCTIONS!\n\n"
                "1. Using this tool may lead to submission ban.\n\n"
                "2. The tool is ONLY for devices on Global HyperOS\n"
                "   and does NOT work with Chinese (CN) models.\n\n"
                "3. Requirements:\n"
                "   • Mi account older than 30 days\n"
                "   • Mi Community account with Global region\n\n"
                "4. By using this tool, you agree that developers dont take responsibility for your devices.\n\n"
                "Click 'Continue' to start."
            ),
            'welcome_btn': "Continue",
            'ping_hint': "This value will be used if ping to servers cannot be measured.",
            'color_theme_xiaomi': "Xiaomi Orange",
            'color_theme_blue': "Blue World",
            'color_theme_red': "Red Sun",
            'language_label': "Language",
            'log_to_txt_checkbox': "Log to TXT file",
            'animations_checkbox': "Interface Animations",
            'animations_development': "In development",
            'input_label': "Input",
            'application_status': "Application status: {}",
            'application_status_not_sent': "Not sent",
            'application_status_sending': "Sending",
            'application_status_success': "Successful",
            'application_status_unknown': "Unknown",
            'application_status_failed': "Unsuccessful",
            'spam_mode_checkbox': "Spam Sending (in Auto-Mode)",
            'spam_mode_desc': "Sends requests at 23:59:58.6, 58.8 (adjusted for ping).\nIf disabled, sends a single request at the optimal time.",
            'ping_not_measured_manual': "Ping: not measured (manual mode)",
            'log_auto_mode_spam_selected': "Auto mode selected (Spam - 5 requests)",
            'log_auto_mode_single_selected': "Auto mode selected (Single request)",
            'log_manual_mode_selected': "Manual mode selected",
            'log_time_gt_2355': "Time > 23:58. Synchronizing time before start...",
            'log_time_sync_success': "Time synchronized successfully!",
            'log_ping_wait': "Waiting for ping measurement at 23:59:30 (Beijing)...",
            'status_ping_wait': "Waiting for 23:59:30 to measure ping...",
            'log_ping_time_passed': "Ping measurement time passed. Synchronizing and measuring now...",
            'log_ping_start': "Time to measure ping! Measuring...",
            'log_measuring_ping': "Measuring ping to servers...",
            'log_ping_measured': "Ping measured: {} ms",
            'log_time_updated': "Time updated: {}",
            'log_resync_error': "Re-synchronization error, continuing with the current timer.",
            'log_normal_mode_ping': "Normal mode: calculating ping...",
            'log_calculated_send_time': "Calculated send time (to hit midnight): 23:59:{}",
            'log_spam_mode_targets': "SPAM MODE: Target times (after ping adjustment): {}",
            'status_spam_wait': "Waiting for spam attack...",
            'log_spam_sending_at': "[Spam #{}] Sending request at 23:59:{}s",
            'log_spam_new_device_id': "[Spam #{}] New deviceId: {}",
            'log_spam_response_prefix': "[Spam #{}] Time: {}s",
            'log_spam_success_prefix': "SUCCESS!",
            'log_spam_response_format': "{} | Code: {} | {}",
            'log_spam_parse_error': "[Spam #{}] Error parsing response: {}",
            'log_spam_no_response': "[Spam #{}] No response from server",
            'log_spam_send_error': "[Spam #{}] Error sending request: {}",
            'login_user_label': "Mi Account ID / Email / Phone:",
            'login_user_placeholder': "Enter your login",
            'login_pwd_label': "Password:",
            'login_pwd_placeholder': "********",
            'wb_instruction': "1. Click the button below to open the confirmation page in your browser.\n2. After you see 'R':'','S':'OK' on the page, copy the full link from the address bar.",
            'wb_instruction_after_open': "Paste the full link in the field below.",
            'wb_id_label': "Confirmation link (wb_id):",
            'wb_id_placeholder': "Paste the link here...",
            'open_confirmation_page': "Open confirmation page",
            'login_button': "Login and Get Token",
            'login_disabled_notice': "Temporarily unavailable",
            'logging_in': "Logging in...",
            'login_fields_error': "Fill in all fields (login, password, and link)!",
            'login_failed': "Login failed",
            'login_failed_generic': "Login failed. Check your credentials.",
            'mi_unlock_title': "Mi Unlock Tool",
            'mi_unlock_checking_python': "Checking Python installation",
            'mi_unlock_upgrading': 'Upgrading miunlock...',
            'mi_unlock_python_found': "Python found: {}",
            'mi_unlock_python_error_msg': (
                "Python not found!\n\n"
                "Mi Unlock Tool requires Python 3.8 or higher.\n\n"
                "Download Python from the official website:\n"
                "https://www.python.org/downloads/\n\n"
                "IMPORTANT: During installation, make sure to check\n"
                "'Add Python to PATH'"
            ),
            'mi_unlock_installing': "Installing miunlock package...",
            'mi_unlock_install_cmd': "Running: pip install miunlock",
            'mi_unlock_already_installed': "miunlock package is already installed",
            'mi_unlock_install_success': "miunlock package successfully installed",
            'mi_unlock_install_error': "Failed to install miunlock!",
            'mi_unlock_starting': "Starting Mi Unlock Tool...",
            'mi_unlock_launching': "Launching miunlock...",
            'mi_unlock_file_not_found': "File not found: {}",
            'mi_unlock_not_found': "Error: miunlock not found!",
            'mi_unlock_completed': "Mi Unlock Tool has finished",
            'mi_unlock_finished': "Program finished",
            'mi_unlock_error': "Error: {}",
            'mi_unlock_critical_error': "Critical error: {}",
            'mi_unlock_close': "Close",
            'mi_unlock_input_label': "Input",
            'mi_unlock_input_placeholder': "Enter response and press Enter...",
            'mi_unlock_send_btn': "Send",
            'mi_unlock_input_prefix': "→ {}",
            'mi_unlock_input_error': "Input send error: {}",
            'mi_unlock_stdout_error': "Stdout read error: {}",
            'mi_unlock_stderr_error': "Stderr read error: {}",
            'mi_unlock_auto_sending': "→ Auto-sending Enter...",
            'mi_unlock_auto_send_error': "Auto-send error: {}",
            'mi_unlock_read_error': "Read error: {}",
            'mi_unlock_process_exit': "Process exited with code: {}",
            'mi_unlock_initial_enter': "→ Auto-sending initial Enter...",
            'mi_unlock_auto_send_final': "→ Auto-sending final Enter...",
            'pre_generation_title': "PRELIMINARY DEVICE ID GENERATION:",
            'pre_generation_main': "  Main device_id: {}",
            'pre_generation_spam1': "  Spam device_id #1: {}",
            'pre_generation_spam2': "  Spam device_id #2: {}",
            'pre_generation_spam3': "  Spam device_id #3: {}",
            'pre_generation_spam4': "  Spam device_id #4: {}",
            'pre_generation_spam5': "  Spam device_id #5: {}",
            'logs_sent': "Logs successfully sent to server",
            'logs_send_error': "Error sending logs: {}",
            'spam_using_device_id': "[Spam #{}] Using device_id: {}",
            'send_with_token': "Sending with token #{}",
            # New keys for HTTP/TCP ping and multi-requests
            'tcp_ping_label': "TCP ping",
            'http_ping_label': "HTTP ping",
            'measuring_pings': "Measuring pings (HTTP and TCP)...",
            'scheduling_requests': "Scheduling requests...",
            'http_request': "HTTP request #{}",
            'tcp_request': "TCP request #{}",
            'ping_measure_done': "Ping measurement completed.",
            'ping_measure_time_come': "Ping measurement time has come, starting now.",
            'ping_http_default': "HTTP ping could not be measured, using default value: {} ms",
            'ping_tcp_default': "TCP ping could not be measured, using default value: {} ms",
            'ping_measure_result': "Measurement completed. HTTP: {:.2f} ms, TCP: {:.2f} ms",
            'http_request_log': "HTTP request #{}: device_id={}, sending in {:.3f}s",
            'tcp_request_log': "TCP request #{}: device_id={}, sending in {:.3f}s",
            'mi_unlock_label': "Mi Unlock",
            'mi_unlock_desc': (
                "Tool for unlocking with Mi Unlock\n"
                "By: pktloss, New G3n\n"
                "Version: 8.2"
            ),
            'mi_unlock_python_not_found': "Python: not found",
            'mi_unlock_python_found_label': "Python: {}",
            'mi_unlock_package_not_installed': "miunlock: not installed",
            'mi_unlock_package_installed': "miunlock: installed",
            'mi_unlock_start_button': "Start Mi Unlock",
            'mi_unlock_process_interrupted': "Process interrupted by user",
            'mi_unlock_log_title': "Execution Log",
            'mi_unlock_drivers_button': "Download Drivers",
            'lang_download_title': "Downloading Language",
            'lang_download_msg': "Downloading language pack...",
            'lang_download_failed': "Failed to download language pack '{}'. Please check your internet connection.",
        }

    def get_ukrainian(self):
        return {           'about_content': 'Xiaomi Unlock Tool — це комплексний інструмент для автоматизації надсилання заявок на '
                                     'розблокування завантажувача (Bootloader) пристроїв Xiaomi, Redmi та POCO.\n'
                                     '\n'
                                     'Основні можливості:\n'
                                     '• Точна мікросекундна синхронізація часу з серверами Пекіна (UTC+8).\n'
                                     '• Гнучке налаштування профілів таймінгів для Європи, Азії та інших регіонів.\n'
                                     '• Вбудована перевірка придатності акаунта та авторизація за QR-кодом.\n'
                                     '• Підтримка темної теми Material 3 з можливістю налаштування акцентного кольору.\n'
                                     '• Вбудований інструмент Mi Unlock для швидкого розблокування.',
                    'about_title': 'Про програму',
                    'account_approved': 'Заявку вже схвалено! Дійсна до: {}',
                    'account_approved_title': 'Успіх',
                    'account_blocked': 'Акаунт заблоковано до: {}',
                    'account_blocked_title': 'Інформація',
                    'account_new': '[Статус] Акаунт створено менше ніж 30 днів тому.',
                    'account_new_title': 'Інформація',
                    'account_ready': 'Акаунт готовий до розблокування!',
                    'account_unknown': '[Помилка] Невідомий статус.',
                    'address_copied': '✓ Скопійовано!',
                    'animations_checkbox': 'Увімкнути плавні анімації інтерфейсу',
                    'animations_coming_soon': 'Анімації будуть додані в майбутньому',
                    'animations_development': 'Анімації оптимізовані для темної теми.',
                    'application_not_submitted': 'Заявку не подано. Ліміт квоти вичерпано на сьогодні. Наступна спроба: {}',
                    'application_status': 'Статус заявки:',
                    'application_status_failed': 'Відхилено',
                    'application_status_not_sent': 'Не надіслано',
                    'application_status_sending': 'Надсилання...',
                    'application_status_success': 'Схвалено!',
                    'application_status_unknown': 'Невідомо',
                    'authors_base_script': 'Оригінальний базовий скрипт:',
                    'authors_content': 'Розробники та подяки:\n'
                                       '• Основний розробник ПК-версії: Franz\n'
                                       '• Автори оригінального інструменту: pktloss, New G3n\n'
                                       '• HyperOS BootLoader Bypass: MlgmXyysd (NekoYuzu) / MeowCat Studio\n'
                                       '\n'
                                       'Дякуємо всім тестувальникам та користувачам спільноти!',
                    'authors_crypto_network': 'Мережа USDT: TON',
                    'authors_developers_title': 'Розробники',
                    'authors_donate_btn': 'Підтримати розробку',
                    'authors_donate_title': 'Підтримка проєкту:',
                    'authors_pc_cli_dev': 'Розробник версії для ПК та CLI:',
                    'authors_social_links': 'Корисні посилання та соцмережі:',
                    'authors_title': 'Автори',
                    'authors_web_android_dev': 'Розробник Web та Android версій:',
                    'auto_mode': 'Авто режим',
                    'auto_mode_1': 'Авто режим 1 (спам)',
                    'auto_mode_2': 'Авто режим 2 (розклад)',
                    'ban_risk': 'Ризик блокування: {}',
                    'beijing_clock_collapse': 'Згорнути',
                    'beijing_clock_expand': 'Розгорнути',
                    'beijing_submission_hint': 'Подання заявки здійснюється о 23:59:58 - 59 за Пекіном',
                    'beijing_time_title': 'Пекінський час (UTC+8)',
                    'bypass_adb_not_found': 'ADB не знайдено',
                    'bypass_adb_ready': 'ADB готовий до роботи',
                    'bypass_adb_searching': 'Пошук ADB пристрою...',
                    'bypass_args_captured': 'Параметри запиту (args) успішно перехоплено!',
                    'bypass_cancelled': 'Операцію скасовано користувачем.',
                    'bypass_capture_failed': 'Не вдалося перехопити дані пристрою.',
                    'bypass_clear_log': 'Очистити',
                    'bypass_click_add_device': 'Будь ласка, перейдіть до: Для розробників -> Стан Mi Unlock та натисніть '
                                               "'Пов'язати акаунт із пристроєм'!",
                    'bypass_code_credentials_expired': 'Сесія акаунта закінчилася (401). Перезайдіть у Mi акаунт на телефоні.',
                    'bypass_code_device_cred_expired': 'Облікові дані пристрою закінчилися (20086).',
                    'bypass_code_invalid_signature': 'Недійсний підпис пристрою (86015).',
                    'bypass_code_success': "Успішно! Пристрій прив'язано.",
                    'bypass_code_verification_forced': 'Xiaomi примусово вимагає перевірку прав акаунта (30001).',
                    'bypass_cookie_extracted': 'Кукі авторизації вилучено',
                    'bypass_data_disabled': 'Мобільний інтернет тимчасово вимкнено для перехоплення.',
                    'bypass_data_enabled': 'Мобільний інтернет увімкнено.',
                    'bypass_data_encrypted': 'Модифіковані дані зашифровано.',
                    'bypass_decrypt_error': 'Помилка розшифрування даних',
                    'bypass_decrypted_ok': 'Дані успішно розшифровано.',
                    'bypass_dev_settings_opened': 'Відкрито налаштування для розробників на телефоні.',
                    'bypass_device_serial': 'Серійний номер пристрою',
                    'bypass_error': 'Помилка',
                    'bypass_headers_captured': 'Заголовки запиту (headers) успішно перехоплено!',
                    'bypass_headers_decrypt_error': 'Помилка розшифрування заголовків',
                    'bypass_log_title': 'Журнал обходу',
                    'bypass_multiple_devices': 'Підключено кілька пристроїв. Залиште лише один',
                    'bypass_no_cookie': 'Увага: Cookie не знайдено в заголовках.',
                    'bypass_no_device': 'Пристрій не виявлено. Підключіть телефон з увімкненим налагодженням по USB',
                    'bypass_panel_title': 'HyperOS 1 BootLoader Bypass',
                    'bypass_refresh_btn': 'Оновити ADB',
                    'bypass_region_label': 'Регіон прошивки:',
                    'bypass_request_failed': 'Помилка відправки HTTP запиту',
                    'bypass_response': 'Відповідь сервера',
                    'bypass_signature': 'Сформовано HMAC-SHA1 підпис',
                    'bypass_start_btn': 'Запустити обхід',
                    'bypass_step1': 'Перевірка пристрою',
                    'bypass_step1_checking': 'Крок 1: Перевірка підключеного пристрою...',
                    'bypass_step2': 'Підготовка та налаштування',
                    'bypass_step2_prep': 'Крок 2: Увімкнення мобільних даних та відкриття налаштувань...',
                    'bypass_step3': 'Перехоплення запиту',
                    'bypass_step3_waiting': "Крок 3: Очікування натискання 'Пов'язати акаунт із пристроєм'...",
                    'bypass_step4': 'Модифікація параметрів',
                    'bypass_step4_patching': 'Крок 4: Розшифрування, модифікація версії ROM та підпис...',
                    'bypass_step5': 'Відправка в Xiaomi',
                    'bypass_step5_sending': 'Крок 5: Відправка сформованого запиту на сервер Xiaomi...',
                    'bypass_stop_btn': 'Зупинити',
                    'bypass_success': "УСПІХ! Пристрій успішно прив'язано в обхід обмежень HyperOS!",
                    'check_eligibility_btn': 'Перевірити придатність',
                    'check_updates': 'Перевірити оновлення',
                    'checking_eligibility': 'Перевірка придатності акаунта...',
                    'chrome_content': '1. Відкрийте Chrome або Edge і перейдіть на community.mi.com.\n'
                                      '2. Авторизуйтесь під своїм обліковим записом Xiaomi.\n'
                                      '3. Натисніть F12, перейдіть на вкладку «Application» (Застосунок) -> «Cookies».\n'
                                      '4. Оберіть домен `mi.com` і знайдіть параметр `passToken` / `serviceToken`.\n'
                                      '5. Скопіюйте значення параметра та вставте в поле скрипта.',
                    'chrome_title': 'Отримання токена у Chrome / Edge',
                    'clear_log_btn': 'Очистити',
                    'close_btn': 'Закрити',
                    'collapse_cookies': 'Згорнути налаштування cookies',
                    'color_picker_accept': 'Застосувати',
                    'color_picker_blue': 'Синій (B)',
                    'color_picker_cancel': 'Закрити',
                    'color_picker_current': 'Поточний:',
                    'color_picker_green': 'Зелений (G)',
                    'color_picker_palette': 'Палітра готових кольорів:',
                    'color_picker_red': 'Червоний (R)',
                    'color_picker_selected': 'Обраний колір:',
                    'color_picker_title': 'Вибір кольору теми',
                    'color_theme_blue': 'Матеріальний Синій',
                    'color_theme_blue_world': 'Blue World',
                    'color_theme_label': 'Колірна тема інтерфейсу:',
                    'color_theme_red': 'Червоне Сонце',
                    'color_theme_red_sun': 'Red Sun',
                    'color_theme_xiaomi': 'Xiaomi Помаранчевий',
                    'color_theme_xiaomi_orange': 'Xiaomi Orange',
                    'confirm': 'Підтвердження',
                    'confirm_warning': 'Увага! Перевірте правильність введених даних.',
                    'cookie_check': 'Перевірка Token Cookie: {}',
                    'cookie_check_state': 'Перевірка токена: {}',
                    'cookie_checkbox': 'Вимкнути перевірку Token Cookie перед надсиланням',
                    'cookie_error': 'Будь ласка, введіть валідний Token Cookie перед початком!',
                    'cookie_error_title': 'Помилка',
                    'cookie_expired': 'Термін дії Token Cookie вичерпано. Будь ласка, отримайте новий токен.',
                    'cookie_label': 'New_bbs_ServiceToken:',
                    'cookie_placeholder': 'Вставте ваш токен сюди...',
                    'cookie_skipped': 'Перевірку токена пропущено.',
                    'cookies_title': 'Налаштування Cookies',
                    'copy_address_btn': '📋 Скопіювати',
                    'current_version': 'Поточна версія: {}',
                    'default': 'за замовчуванням',
                    'default_ping': 'Пінг за замовчуванням: {} мс',
                    'desc': 'Скрипт для автоматичного надсилання заявок на розблокування\nАвтор: pktloss, New G3n\nВерсія: 8.2',
                    'desc_manual': 'Ручний режим - оберіть час надсилання вручну\nАвтор: pktloss, New G3n\nВерсія: 8.2',
                    'device_binding_hint': "Підказка: після схвалення зв'яжіть акаунт у меню для розробників на телефоні.",
                    'device_id_gen': 'Згенеровано Device ID: {}',
                    'eligibility_eligible_title': 'Акаунт придатний!',
                    'error_title': 'Помилка',
                    'execution_log': 'Журнал виконання',
                    'exit': 'Вихід',
                    'exit_btn': 'Вихід',
                    'expand_cookies': 'Розгорнути налаштування cookies',
                    'final_unlock_checkbox': "Подання завершено. Спробуйте прив'язати телефон за будь-яких результатів.",
                    'firefox_content': '1. Відкрийте браузер Firefox і перейдіть на сайт community.mi.com.\n'
                                       '2. Увійдіть у свій Mi Account.\n'
                                       '3. Натисніть F12 для відкриття інструментів розробника та перейдіть на вкладку '
                                       '«Сховище» -> «Куки».\n'
                                       '4. Знайдіть кукі з назвою `passToken` або `serviceToken` (New_bbs_ServiceToken).\n'
                                       '5. Скопіюйте значення та вставте його у відповідне поле скрипта.',
                    'firefox_title': 'Отримання токена у Firefox',
                    'general_content': "1. Увійдіть у свій Mi Account на пристрої та прив'яжіть номер телефону.\n"
                                       '2. Отримайте Token Cookie (New_bbs_ServiceToken) через вхід за QR-кодом або браузер.\n'
                                       '3. Вставте токен у поле програми та натисніть «Перевірити придатність».\n'
                                       '4. Оберіть режим роботи (Авто режим 2 або Ручний режим).\n'
                                       '5. Натисніть кнопку «Подати заявку» перед настанням 00:00:00 за Пекінським часом.\n'
                                       '6. Скрипт автоматично надішле запити в найточніший момент із урахуванням таймінгів.',
                    'general_title': 'Загальна інструкція',
                    'header_region': 'Регіон: {}',
                    'http_ping_label': 'HTTP пінг: {} мс',
                    'http_request': 'HTTP запит...',
                    'http_request_log': 'HTTP пінг: {} мс',
                    'hyperos1_bypass_desc': "Обхід обмежень спільноти HyperOS 1 для прив'язки облікового запису.",
                    'hyperos1_bypass_return_btn': 'Повернутися до подання заявок',
                    'hyperos1_bypass_title': 'HyperOS 1 Bypass',
                    'import_error': 'Помилка імпорту',
                    'info': 'Інформація',
                    'input_label': 'Введіть параметри:',
                    'install_error': 'Помилка встановлення',
                    'instructions_btn': 'Інструкції',
                    'instructions_title': 'Інструкції',
                    'lang_download_failed': 'Не вдалося завантажити мовний пакет ({}). Встановлено англійську мову.',
                    'lang_download_msg': 'Завантаження мовного пакета ({}) з сервера...',
                    'lang_download_title': 'Завантаження мовного пакета',
                    'language_label': 'Мова інтерфейсу:',
                    'latest_version': 'Остання версія: {}',
                    'log': 'Журнал',
                    'log_auto_mode_single_selected': '[Режим] Обрано режим одиночного надсилання.',
                    'log_auto_mode_spam_selected': '[Режим] Обрано режим серійного надсилання.',
                    'log_calculated_send_time': '[Розрахунок] Час старту відправки: {}',
                    'log_code_message': 'Код: {code} | Повідомлення: {msg}',
                    'log_manual_mode_selected': '[Режим] Обрано ручний режим.',
                    'log_measuring_ping': 'Вимірювання пінгу до серверів Xiaomi...',
                    'log_mode2_beijing_reached': '[Розклад] Досягнуто часу початку відправки.',
                    'log_mode2_ntp_saved': '[NTP] Час синхронізовано з сервером.',
                    'log_mode2_plan_sent': '[План] Усі заплановані запити надіслано.',
                    'log_mode2_selected': '[Авто режим] Активовано режим за розкладом.',
                    'log_normal_mode_ping': '[Пінг] Застосовано значення: {} мс',
                    'log_ping_avg_http': 'Середній HTTP пінг: {:.2f} мс',
                    'log_ping_avg_tcp': 'Середній TCP пінг: {:.2f} мс',
                    'log_ping_http_failed': 'Не вдалося виміряти HTTP пінг.',
                    'log_ping_measured': '[Пінг] Вимірювання успішно завершено.',
                    'log_ping_start': '[Пінг] Початок тестових запитів...',
                    'log_ping_start_http_tcp': 'Вимірювання затримки HTTP та TCP...',
                    'log_ping_tcp_failed': 'Не вдалося виміряти TCP пінг.',
                    'log_ping_time_passed': '[Пінг] Час вимірювання вже настав.',
                    'log_ping_wait': '[Очікування] Очікування часу початку вимірювання затримки...',
                    'log_request_exception': '[Помилка запиту] {error}',
                    'log_request_failed_no_response': '[Помилка] Не вдалося надіслати запит (відповідь відсутня)',
                    'log_request_parse_error': '[Помилка обробки відповіді] Не вдалося розібрати JSON: {data}',
                    'log_resync_error': '[Помилка] Не вдалося повторно синхронізувати час.',
                    'log_spam_mode_targets': '[Серія] Кількість цільових запитів: {}',
                    'log_spam_new_device_id': '[Серія] Новий Device ID: {}',
                    'log_spam_no_response': '[Серія #{}] Відповідь відсутня.',
                    'log_spam_parse_error': '[Серія #{}] Помилка розбору JSON: {}',
                    'log_spam_response_format': '[Серія #{}] Код: {} | Повідомлення: {}',
                    'log_spam_response_prefix': '[Серія #{}] Відповідь: {}',
                    'log_spam_send_error': '[Серія #{}] Помилка надсилання: {}',
                    'log_spam_sending_at': '[Серія] Відправка #{}: {}',
                    'log_spam_success_prefix': '[Серія #{}] УСПІХ!',
                    'log_success_prefix': 'УСПІХ!',
                    'log_time_gt_2355': '[Час] Поточний час після 23:55, запити заплановано на сьогодні.',
                    'log_time_sync_success': '[Синхронізація] Точний час успішно скориговано.',
                    'log_time_updated': '[Час] Дані часу оновлено.',
                    'log_to_txt_checkbox': 'Записувати журнал у текстовий файл (.txt)',
                    'log_token_check_skipped': '[Перевірка] Перевірку Token Cookie пропущено користувачем.',
                    'log_token_check_success': '[Перевірка] Token Cookie валідний та готовий до роботи.',
                    'logging_in': 'Виконується авторизація...',
                    'login_authorized_extracting': 'Успішно авторизовано! Отримання токена...',
                    'login_browser_opened': 'Сторінку авторизації відкрито в браузері.',
                    'login_btn': 'Увійти в акаунт',
                    'login_button': 'Авторизуватися',
                    'login_disabled_notice': 'Прямий вхід за паролем тимчасово обмежено захистом Xiaomi. Рекомендується вхід '
                                             'за QR-кодом.',
                    'login_error': 'Помилка входу: {}',
                    'login_existing_found': 'Знайдено збережену сесію:',
                    'login_existing_id': 'Xiaomi ID: {}',
                    'login_extracting_token': 'Отримання токена...',
                    'login_failed': 'Помилка авторизації. Перевірте логін і пароль.',
                    'login_failed_generic': 'Не вдалося виконати вхід. Спробуйте вхід за QR-кодом.',
                    'login_fields_error': 'Будь ласка, заповніть усі поля логіна та пароля!',
                    'login_loading_qr': 'Завантаження QR-коду...',
                    'login_open_browser_btn': 'Відкрити в браузері',
                    'login_pwd_label': 'Пароль:',
                    'login_pwd_placeholder': 'Введіть пароль...',
                    'login_qr_expired': 'Час дії коду вичерпано. Оновіть QR-код.',
                    'login_qr_fetch_error': 'Помилка завантаження QR-коду: {}',
                    'login_qr_scan_tip': 'Відскануйте QR-код за допомогою камери або програми Mi Home / Сканер',
                    'login_refresh_qr': 'Оновити код',
                    'login_refreshing_qr': 'Оновлення QR-коду...',
                    'login_session_expired': 'Час очікування авторизації вичерпано.',
                    'login_subtitle': 'Швидкий вхід за QR-кодом або використання збереженого токена',
                    'login_success': 'Вхід виконано успішно!',
                    'login_tab_existing': 'Збережений акаунт',
                    'login_tab_qr': 'Вхід за QR-кодом',
                    'login_title': 'Вхід до Mi Account',
                    'login_token_extract_error': 'Не вдалося витягти токен після авторизації.',
                    'login_use_existing_btn': 'Використати цей токен',
                    'login_user_label': "Ім'я користувача / Email / Телефон:",
                    'login_user_placeholder': 'Введіть логін...',
                    'login_waiting': 'Очікування сканування...',
                    'logs_send_error': 'Помилка збереження журналу: {}',
                    'logs_sent': 'Журнал успішно збережено.',
                    'main_title': 'Xiaomi Unlock Tool',
                    'manual_mode': 'Ручний режим',
                    'manual_mode_start': 'Запуск у ручному режимі з цільовим часом: {} сек',
                    'manual_time_error': 'Введіть коректне значення секунд (0-60)!',
                    'manual_time_hint': 'Введіть секунди для відправки (наприклад, 59.1)',
                    'manual_time_label': 'Час надсилання:',
                    'measuring_pings': 'Вимірювання пінгу...',
                    'mi_unlock_already_installed': 'Усі компоненти вже встановлені.',
                    'mi_unlock_auto_send_error': 'Помилка авто-підтвердження: {}',
                    'mi_unlock_auto_send_final': 'Фінальне підтвердження надіслано.',
                    'mi_unlock_auto_sending': 'Автоматичне надсилання підтвердження...',
                    'mi_unlock_checking_python': 'Перевірка наявності Python...',
                    'mi_unlock_close': 'Закрити',
                    'mi_unlock_completed': 'Процес Mi Unlock завершено.',
                    'mi_unlock_critical_error': 'Критична помилка Mi Unlock: {}',
                    'mi_unlock_desc': 'Офіційне розблокування завантажувача через fastboot після отримання схвалення.',
                    'mi_unlock_drivers_button': 'Встановити драйвери',
                    'mi_unlock_error': 'Помилка Mi Unlock: {}',
                    'mi_unlock_file_not_found': 'Виконуваний файл не знайдено: {}',
                    'mi_unlock_finished': 'Роботу завершено.',
                    'mi_unlock_initial_enter': 'Надсилання початкового підтвердження...',
                    'mi_unlock_input_error': 'Помилка передачі вхідних даних: {}',
                    'mi_unlock_input_label': 'Введення команди:',
                    'mi_unlock_input_placeholder': 'Введіть команду або дані...',
                    'mi_unlock_input_prefix': '[Введення]: {}',
                    'mi_unlock_install_cmd': 'Виконання команди: {}',
                    'mi_unlock_install_error': 'Помилка встановлення компонентів: {}',
                    'mi_unlock_install_success': 'Компоненти успішно встановлено!',
                    'mi_unlock_installing': 'Встановлення необхідних компонентів...',
                    'mi_unlock_label': 'Mi Unlock',
                    'mi_unlock_launching': 'Запуск Mi Unlock Tool...',
                    'mi_unlock_log_title': 'Журнал Mi Unlock',
                    'mi_unlock_not_found': 'Mi Unlock не знайдено.',
                    'mi_unlock_package_installed': 'Усі необхідні пакунки встановлено.',
                    'mi_unlock_package_not_installed': 'Необхідні пакунки не встановлено.',
                    'mi_unlock_process_exit': 'Процес завершився з кодом: {}',
                    'mi_unlock_process_interrupted': 'Процес перервано користувачем.',
                    'mi_unlock_python_error_msg': 'Помилка перевірки середовища Python: {}',
                    'mi_unlock_python_found': 'Python знайдено: {}',
                    'mi_unlock_python_found_label': 'Середовище Python виявлено.',
                    'mi_unlock_python_not_found': 'Python не знайдено в системі.',
                    'mi_unlock_read_error': 'Помилка читання потоку: {}',
                    'mi_unlock_send_btn': 'Надіслати',
                    'mi_unlock_start_button': 'Запустити Mi Unlock',
                    'mi_unlock_starting': 'Запуск процесу Mi Unlock...',
                    'mi_unlock_stderr_error': 'Помилка читання виводу помилок: {}',
                    'mi_unlock_stdout_error': 'Помилка читання стандартного виводу: {}',
                    'mi_unlock_title': 'Mi Unlock Tool',
                    'mi_unlock_upgrading': 'Оновлення компонентів...',
                    'mode2_prefix': '[Авто режим]',
                    'mode2_timing': 'таймінг',
                    'mode2_using_device_id': '[Авто режим] #{}: Device ID={}',
                    'mode_label': 'Режим роботи:',
                    'ms': 'мс',
                    'ntp_connect': 'Підключення до сервера часу: {}',
                    'ntp_failed': 'Не вдалося підключитися до жодного з NTP серверів.',
                    'ntp_time': 'Пекінський час, отриманий від сервера {}: {}',
                    'open_confirmation_page': 'Відкрити сторінку підтвердження',
                    'open_miflash': 'Відкрити MiFlash Unlock',
                    'params': 'Параметри',
                    'ping': 'Пінг',
                    'ping_avg': 'Середній пінг: {:.2f} мс',
                    'ping_default': 'Не вдалося отримати пінг до сервера!\nВикористовується значення за замовчуванням: {} мс',
                    'ping_error': 'Помилка при вимірюванні пінгу: {} ({})',
                    'ping_error_msg': 'Пінг має бути додатним числом!',
                    'ping_error_title': 'Помилка',
                    'ping_failed': 'Помилка пінгу до сервера: {}',
                    'ping_hint': 'Використовується як резервне значення, якщо авто-пінг не спрацює.',
                    'ping_http_default': 'HTTP пінг за замовчуванням: {} мс',
                    'ping_label': 'Пінг за замовчуванням (мс):',
                    'ping_measure_done': 'Вимірювання пінгу завершено.',
                    'ping_measure_result': 'Результат пінгу: HTTP={} мс, TCP={} мс',
                    'ping_measure_time_come': 'Час вимірювання настав.',
                    'ping_not_measured_manual': 'Використовується ручне значення пінгу.',
                    'ping_note': 'Примітка: точний пінг допомагає скоригувати час надсилання.',
                    'ping_server': 'Сервер: {}, Пінг: {:.2f} мс',
                    'ping_start': 'Початок перевірки пінгу...',
                    'ping_tcp_default': 'TCP пінг за замовчуванням: {} мс',
                    'pre_generation_main': 'Основний Device ID: {}',
                    'pre_generation_spam1': 'Слот 1: {}',
                    'pre_generation_spam2': 'Слот 2: {}',
                    'pre_generation_spam3': 'Слот 3: {}',
                    'pre_generation_spam4': 'Слот 4: {}',
                    'pre_generation_spam5': 'Слот 5: {}',
                    'pre_generation_title': 'Попередня генерація Device ID:',
                    'profile_asia': 'Азія',
                    'profile_europe': 'Європа',
                    'profile_usa_africa': 'США / Африка',
                    'profiles_btn': 'Профілі',
                    'profiles_title': 'Профілі таймінгів',
                    'req_using_device_id': '[Запит #{}] Device ID={}',
                    'request_error': 'Помилка надсилання запиту: {}',
                    'request_failed': '[Помилка] Не вдалося надіслати запит',
                    'request_prefix': 'Запит',
                    'request_sent': 'Запит надіслано о: {}',
                    'response_error': 'Помилка розбору відповіді: {}',
                    'response_received': 'Отримано відповідь о: {}',
                    'save_btn': 'Зберегти',
                    'saved': 'Збережено',
                    'scheduling_requests': 'Планування запитів...',
                    'script_info': 'Інформація про скрипт',
                    'sections_menu': 'Меню розділів',
                    'send_with_token': 'Надсилання запиту з токеном: {}...',
                    'settings': 'Налаштування',
                    'settings_saved': 'Налаштування успішно збережено.',
                    'social_github': 'Репозиторій GitHub',
                    'social_reddit': 'Спільнота Reddit',
                    'social_site_script': 'Офіційний сайт скрипта',
                    'social_telegram': 'Telegram канал',
                    'spam_mode_checkbox': 'Режим серійного надсилання (Spam)',
                    'spam_mode_desc': 'Надсилає декілька запитів поспіль із інтервалом у мілісекунди.',
                    'spam_using_device_id': '[Серія] Використання Device ID: {}',
                    'start_btn': 'Почати',
                    'status_app_approved_checking': 'Заявку схвалено! Перевірка стану...',
                    'status_app_possibly_approved': 'Можливо, заявку схвалено! Перевірка стану...',
                    'status_app_rejected_100001': 'Ліміт заявок на сьогодні вичерпано (100001). Спробуйте завтра.',
                    'status_error': 'Помилка перевірки статусу: {}',
                    'status_get_failed': 'Не вдалося отримати статус акаунта.',
                    'status_mode2_sending': 'Надсилання запитів...',
                    'status_mode2_waiting': 'Очікування цільового часу...',
                    'status_ping_wait': 'Очікування вимірювання пінгу...',
                    'status_ready': 'Готовий до роботи',
                    'status_spam_wait': 'Очікування моменту відправки серії...',
                    'submit_application': 'Подати заявку',
                    'success_dialog_message': 'Заявку на розблокування успішно схвалено!\n'
                                              'Перевірте статус у налаштуваннях розробника на телефоні.',
                    'success_dialog_title': 'Успішно!',
                    'tab_hyperos1_bypass': 'HyperOS 1 Bypass',
                    'tab_mi_unlock': 'Mi Unlock',
                    'tab_settings': 'Налаштування та інструкція',
                    'tab_unlock': 'Подання заявок',
                    'target_time': 'Цільовий час: {} (таймінг: {} сек)',
                    'target_time_manual': 'Цільовий час (ручний режим): {}',
                    'tcp_ping_label': 'TCP пінг: {} мс',
                    'tcp_request': 'TCP запит...',
                    'tcp_request_log': 'TCP пінг: {} мс',
                    'theme_color_apply': 'Застосувати колір',
                    'theme_color_error': 'Будь ласка, введіть коректний HEX-код кольору у форматі #RRGGBB.',
                    'theme_color_error_title': 'Некоректний колір',
                    'theme_color_hint': 'Введіть HEX-код (наприклад, #D0BCFF) або оберіть у палітрі',
                    'theme_color_label': 'Акцентний колір теми:',
                    'theme_color_picker': 'Обрати колір...',
                    'theme_color_placeholder': '#D0BCFF',
                    'theme_dark': 'Темна',
                    'theme_dark_only': 'Програма працює виключно в темній темі (Material 3 Dark).',
                    'theme_label': 'Тема оформлення:',
                    'theme_light': 'Світла',
                    'theme_locked_notice': 'Інтерфейс зафіксовано в оптимізованій темній темі Material 3.',
                    'theme_system': 'Системна',
                    'time': 'Час',
                    'time_error': 'Не вдалося синхронізувати точний час із сервером.',
                    'time_reached': 'Цільовий час досягнуто: {}',
                    'time_synchronized': 'Час синхронізовано',
                    'time_wait': 'Очікування потрібного часу...',
                    'timings_btn': 'Налаштування таймінгів',
                    'timings_count_label': 'Обрано: {} з {}',
                    'timings_desc': 'Оберіть таймінги (зсуви в мс) для авто-надсилання о 23:59:59:',
                    'timings_dialog_title': 'Налаштування таймінгів',
                    'timings_min_warning': 'Необхідно обрати хоча б 1 таймінг надсилання!',
                    'timings_region_default': 'Регіон: Європа (за замовчуванням обрано 6 таймінгів)',
                    'timings_reset_btn': 'Скинути за замовчуванням',
                    'timings_risk_warning': '⚠️ Вибір занадто великої кількості запитів може призвести до тимчасового '
                                            'блокування на надсилання заявок, а занадто мала кількість таймінгів у '
                                            'невідповідний момент може призвести до невдачі.',
                    'timings_save_btn': 'Зберегти і закрити',
                    'timings_slots_title': 'Налаштування 15 слотів таймінгів (сек:мс):',
                    'title': 'Xiaomi Unlock Tool',
                    'token_status_check_failed': 'Не вдалося підтвердити валідність токена через сервер Xiaomi. Перевірте '
                                                 'токен.',
                    'trouble_content': 'Часті проблеми та їх вирішення:\n'
                                       '• Код 100001: Добовий ліміт квоти заявок вичерпано. Спробуйте наступного дня о 00:00 '
                                       'за Пекіном.\n'
                                       '• Код 100004: Термін дії токена минув. Отримайте новий токен або увійдіть через '
                                       'QR-код.\n'
                                       '• Помилка часу: Перевірте підключення до Інтернету або вимкніть VPN.\n'
                                       '• Пристрій не знайдено в Fastboot: Перевірте встановлення драйверів USB через кнопку '
                                       '«Драйвери».',
                    'trouble_title': 'Вирішення проблем',
                    'unknown_status_title': 'Помилка',
                    'unlock_process': 'Запуск процесу розблокування...',
                    'unlock_start': 'Початок процесу розблокування...',
                    'update_available': 'Доступне нове оновлення!',
                    'update_btn_ok': 'Зрозуміло',
                    'update_btn_update': 'Оновити зараз',
                    'update_check_error': 'Помилка перевірки оновлень',
                    'update_checking': 'Перевірка наявності оновлень...',
                    'update_error': 'Не вдалося перевірити оновлення',
                    'update_message': 'Доступна нова версія {}.\nБажаєте завантажити оновлення?',
                    'update_not_available': 'Оновлення відсутні. У вас встановлена остання версія.',
                    'wb_id_label': 'Ідентифікатор сесії (wb_id):',
                    'wb_id_placeholder': 'wb_id...',
                    'wb_instruction': 'Інструкція для отримання токена через браузер:',
                    'wb_instruction_after_open': 'Після відкриття сторінки авторизуйтесь та скопіюйте токен.',
                    'welcome_btn': 'Розпочати роботу',
                    'welcome_text': 'Інструмент для автоматичного розблокування завантажувача Xiaomi HyperOS та MIUI.',
                    'welcome_title': 'Ласкаво просимо до Xiaomi Unlock Tool!',
                    'your_region': 'Ваш регіон: {}'}

