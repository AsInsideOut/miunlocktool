import os
import locale


def get_system_language():
    try:
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


class Translation:
    def __init__(self, language=None):
        if language is None:
            self.language = get_system_language()
        else:
            self.language = language
        if self.language not in {'ru', 'en', 'id', 'es', 'zh', 'pt'}:
            self.language = 'en'
        self.translations = {
            'ru': self.get_russian(),
            'en': self.get_english(),
            'id': self.get_indonesian(),
            'es': self.get_spanish(),
            'zh': self.get_chinese(),
            'pt': self.get_portuguese(),
        }

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
                "Версия: 8.0"
            ),
            'desc_manual': (
                "Ручной режим - выберите время отправки заявки вручную\n"
                "От: pktloss, New G3n\n"
                "Версия: 8.0"
            ),
            'params': "Параметры",
            'tab_unlock': "Подача заявок",
            'tab_settings': "Настройки и инструкция",
            'tab_mi_unlock': "Mi Unlock",
            'log_success_prefix': "УСПЕХ!",
            'log_code_message': "Код: {code} | Сообщение: {msg}",
            'log_request_parse_error': "[Ошибка обработки ответа] Не удалось распарсить JSON: {data}",
            'log_request_failed_no_response': "[Ошибка] Не удалось отправить запрос (нет ответа)",
            'log_request_exception': "[Ошибка запроса] {error}",
            'cookie_label': "New_bbs_ServiceToken:",
            'cookie_placeholder': "Вставьте ваш токен здесь...",
            'login_btn': "🔑 Войти в аккаунт",
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
                "Версия скрипта: 8.0"
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
            'authors_content': """Разработчики:

• pktloss | Tg: @hyeplet231

• New Gen | Tg: @new_g3n

Ссылки:

Telegram: https://t.me/miunlocktoolrevamp

GitHub: https://github.com/AsInsideOut/miunlocktool

Reddit: https://www.reddit.com/r/miunlocktool

Cкрипт построен на базе скрипта от:

• Vierta

Версия скрипта: 8.0""",
            'cookie_checkbox': "Отключить проверку Token Cookie перед отправкой",
            'final_unlock_checkbox': "Подача окончена. Попробуйте привязать телефон при любых результатах.",
            'ping_label': "Пинг по умолчанию (мс):",
            'color_theme_label': "Цветовая тема интерфейса:",
            'color_theme_xiaomi_orange': "Xiaomi Orange",
            'color_theme_red_sun': "Red Sun",
            'color_theme_blue_world': "Blue World",
            'save_btn': "Сохранить",
            'close_btn': "Закрыть",
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
            'clear_log_btn': "Очистить",
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
            'update_not_available': "Обновлений не найдено",
            'update_checking': "Проверка обновлений...",
            'update_error': "Ошибка при проверке обновлений",
            'current_version': "Текущая версия: {}",
            'your_region': "Ваш Регион: {}",
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
            'animations_checkbox': "Отключить анимации",
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
            'login_title': "Вход в аккаунт Xiaomi",
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
            'login_success': "Вход выполнен успешно! Токен получен.",
            'login_failed': "Ошибка входа",
            'login_failed_generic': "Ошибка входа. Проверьте данные.",
            'login_token_extract_error': "Не удалось автоматически извлечь токен. Скопируйте его вручную с сайта c.mi.com/global.",
            'mi_unlock_title': "Mi Unlock Tool",
            'mi_unlock_checking_python': "Проверка наличия Python",
            'mi_unlock_upgrading': 'Установка обновления miunlock...',
            'mi_unlock_python_found': "Найден Python: {}",
            'mi_unlock_python_not_found': "Python не найден!",
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
                "Версия: 8.0"
            ),
            'mi_unlock_python_not_found': "Python: не найден",
            'mi_unlock_python_found_label': "Python: {}",
            'mi_unlock_package_not_installed': "miunlock: не установлен",
            'mi_unlock_package_installed': "miunlock: установлен",
            'mi_unlock_start_button': "Запустить Mi Unlock",
            'mi_unlock_process_interrupted': "Процесс прерван пользователем",
            'mi_unlock_log_title': "Лог выполнения",
            'mi_unlock_drivers_button': "Скачать драйверы",
        }

    def get_english(self):
        return {
            'title': "Xiaomi Unlock Tool",
            'main_title': "Xiaomi Unlock Tool",
            'desc': (
                "Tool for automatic unlock request submission\n"
                "By: pktloss, New G3n\n"
                "Version: 8.0"
            ),
            'desc_manual': (
                "Manual mode - select the time to submit manually\n"
                "By: pktloss, New G3n\n"
                "Version: 8.0"
            ),
            'params': "Parameters",
            'tab_unlock': "Submit Application",
            'tab_settings': "Settings and Instructions",
            'tab_mi_unlock': "Mi Unlock",
            'log_success_prefix': "SUCCESS!",
            'log_code_message': "Code: {code} | Message: {msg}",
            'log_request_parse_error': "[Response processing error] Failed to parse JSON: {data}",
            'log_request_failed_no_response': "[Error] Failed to send request (no response)",
            'log_request_exception': "[Request error] {error}",
            'cookie_label': "New_bbs_ServiceToken:",
            'cookie_placeholder': "Paste your token here...",
            'login_btn': "🔑 Log In to Account",
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
                "Script version: 8.0"
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
            'authors_content': """Developers:

• pktloss | Tg: @hyeplet231

• New Gen | Tg: @new_g3n

Links:

Telegram group: https://t.me/miunlocktoolrevamp

GitHub: https://github.com/AsInsideOut/miunlocktool

Reddit: https://www.reddit.com/r/miunlocktool

Script is based on:

• Vierta

Script version: 8.0""",
            'cookie_checkbox': "Disable Token Cookie check before submission",
            'final_unlock_checkbox': "Submission is complete. Try binding the phone regardless of the result.",
            'ping_label': "Default ping (ms):",
            'color_theme_label': "Color theme:",
            'color_theme_xiaomi_orange': "Xiaomi Orange",
            'color_theme_red_sun': "Red Sun",
            'color_theme_blue_world': "Blue World",
            'save_btn': "Save",
            'close_btn': "Close",
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
            'clear_log_btn': "Clear",
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
            'update_not_available': "No updates found",
            'update_checking': "Checking for updates...",
            'update_error': "Error checking for updates",
            'current_version': "Current version: {}",
            'your_region': "Your Region: {}",
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
            'animations_checkbox': "Disable animations",
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
            'login_title': "Xiaomi Account Login",
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
            'login_success': "Login successful! Token obtained.",
            'login_failed': "Login failed",
            'login_failed_generic': "Login failed. Check your credentials.",
            'login_token_extract_error': "Could not automatically extract token. Please copy it manually from c.mi.com/global.",
            'mi_unlock_title': "Mi Unlock Tool",
            'mi_unlock_checking_python': "Checking Python installation",
            'mi_unlock_upgrading': 'Upgrading miunlock...',
            'mi_unlock_python_found': "Python found: {}",
            'mi_unlock_python_not_found': "Python not found!",
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
                "Version: 8.0"
            ),
            'mi_unlock_python_not_found': "Python: not found",
            'mi_unlock_python_found_label': "Python: {}",
            'mi_unlock_package_not_installed': "miunlock: not installed",
            'mi_unlock_package_installed': "miunlock: installed",
            'mi_unlock_start_button': "Start Mi Unlock",
            'mi_unlock_process_interrupted': "Process interrupted by user",
            'mi_unlock_log_title': "Execution Log",
            'mi_unlock_drivers_button': "Download Drivers",
        }

    def get_indonesian(self):
        return {
            'title': "Xiaomi Unlock Tool",
            'main_title': "Xiaomi Unlock Tool",
            'desc': (
                "Alat untuk pengajuan permintaan buka kunci otomatis\n"
                "Oleh: pktloss, New G3n\n"
                "Versi: 8.0"
            ),
            'desc_manual': (
                "Mode manual - pilih waktu pengiriman secara manual\n"
                "Oleh: pktloss, New G3n\n"
                "Versi: 8.0"
            ),
            'params': "Parameter",
            'tab_unlock': "Pengajuan Aplikasi",
            'tab_settings': "Pengaturan dan Instruksi",
            'tab_mi_unlock': "Mi Unlock",
            'log_success_prefix': "SUKSES!",
            'log_code_message': "Kode: {code} | Pesan: {msg}",
            'log_request_parse_error': "[Kesalahan pemrosesan respons] Gagal mengurai JSON: {data}",
            'log_request_failed_no_response': "[Kesalahan] Gagal mengirim permintaan (tidak ada respons)",
            'log_request_exception': "[Kesalahan permintaan] {error}",
            'cookie_label': "New_bbs_ServiceToken:",
            'cookie_placeholder': "Tempel token Anda di sini...",
            'login_btn': "🔑 Masuk ke Akun",
            'check_eligibility_btn': "Periksa kelayakan",
            'checking_eligibility': "Memeriksa kelayakan akun...",
            'eligibility_eligible_title': "Pemeriksaan Kelayakan",
            'login_title': "Otorisasi Akun Xiaomi",
            'login_subtitle': "Pengambilan New_bbs_serviceToken otomatis",
            'login_tab_qr': "Kode QR / Browser",
            'login_tab_existing': "Akun Tersimpan",
            'login_existing_found': "Sesi Akun Mi tersimpan terdeteksi",
            'login_existing_id': "ID Akun: {}",
            'login_use_existing_btn': "⚡ Gunakan akun ini",
            'login_qr_scan_tip': "Pindai kode QR di aplikasi Mi Community\natau dengan kamera ponsel Xiaomi Anda",
            'login_open_browser_btn': "🌐 Masuk dengan Browser",
            'login_refresh_qr': "🔄 Perbarui Kode QR",
            'login_waiting': "Menunggu konfirmasi otorisasi...",
            'login_qr_expired': "Kode QR kedaluwarsa. Klik 'Perbarui Kode QR'.",
            'login_loading_qr': "⏳ Memuat kode QR...",
            'login_browser_opened': "Halaman login dibuka di browser. Menunggu penyelesaian...",
            'login_refreshing_qr': "Memperbarui kode QR...",
            'login_qr_fetch_error': "Gagal memuat kode QR: {}",
            'login_authorized_extracting': "Otorisasi dikonfirmasi! Mengekstrak token...",
            'login_extracting_token': "Mengekstrak token...",
            'login_session_expired': "Sesi telah berakhir",
            'login_success': "Otorisasi berhasil! new_bbs_serviceToken diperoleh.",
            'login_error': "Kesalahan otorisasi: {}",
            'login_token_extract_error': "Gagal mengekstrak token dari respons server.",
            'close_btn': "Tutup",
            'log_token_check_success': "Pemeriksaan token dan status berhasil diselesaikan.",
            'log_token_check_skipped': "Peringatan: verifikasi token dinonaktifkan di pengaturan, melanjutkan...",
            'log_mode2_selected': "Mode Otomatis #2 dipilih (spam HTTP menuju 23:59:59)",
            'log_mode2_ntp_saved': "Mode Otomatis #2: Sinkronisasi NTP tersimpan, mode tanpa pengukuran ping",
            'status_mode2_waiting': "Mode Otomatis #2: menunggu 23:59:59",
            'log_mode2_beijing_reached': "Mode Otomatis #2: waktu Beijing 23:59:59 tercapai",
            'status_mode2_sending': "Mode Otomatis #2: mengirim paket HTTP",
            'mode2_prefix': "Mode Otomatis #2",
            'mode2_timing': "penentuan waktu",
            'log_mode2_plan_sent': "Rencana spam HTTP dikirim",
            'mode2_using_device_id': "[Mode Otomatis #2 HTTP #{}] Menggunakan device_id: {}",
            'request_prefix': "Permintaan",
            'req_using_device_id': "[Permintaan #{}] Menggunakan device_id: {}",
            'log_ping_start_http_tcp': "Memulai pengukuran ping HTTP dan TCP...",
            'log_ping_avg_http': "Rata-rata ping HTTP: {:.2f} ms",
            'log_ping_http_failed': "Gagal mengukur ping HTTP",
            'log_ping_avg_tcp': "Rata-rata ping TCP: {:.2f} ms",
            'log_ping_tcp_failed': "Gagal mengukur ping TCP",
            'status_get_failed': "[Kesalahan] Gagal mendapatkan status buka kunci.",
            'status_app_approved_checking': "[Status] Pengajuan disetujui, memeriksa status...",
            'status_app_rejected_100001': "[Status] Pengajuan ditolak, kesalahan permintaan (kode 100001).",
            'status_app_possibly_approved': "[Status] Pengajuan kemungkinan disetujui, memeriksa status...",
            'success_dialog_title': "Berhasil!",
            'success_dialog_message': "Berhasil! Coba tautkan akun Anda.",
            'theme_dark_only': "Tema gelap (hanya tema gelap yang tersedia)",
            'confirm': "Saya menyadari risiko kemungkinan pemblokiran akun",
            'info': "Informasi",
            'status_ready': "Siap memulai",
            'ping': "Ping: tidak diukur",
            'time': "Waktu: tidak disinkronkan",
            'start_btn': "Mulai Aplikasi",
            'instructions_btn': "Instruksi dan Pengaturan Skrip",
            'exit_btn': "Keluar",
            'log': "Log Eksekusi",
            'clear_log_btn': "Bersihkan",
            'unlock_start': "Memulai proses buka kunci...",
            'device_id_gen': "DeviceId yang dihasilkan: {}",
            'ping_start': "Memulai perhitungan ping...",
            'ping_server': "Ping ke {}: {:.2f} ms",
            'ping_failed': "Gagal mendapatkan ping server {}",
            'ping_error': "Kesalahan ping {}: {}",
            'open_miflash': "MiFlash Unlock",
            'social_telegram': "Telegram",
            'social_reddit': "Reddit",
            'social_github': "GitHub",
            'social_site_script': "Situs Skrip",
            'theme_color_label': 'Warna tema',
            'theme_color_picker': 'Pilih warna',
            'theme_color_apply': 'Terapkan',
            'theme_color_hint': 'Masukkan HEX (#RRGGBB) atau RGB (R,G,B)',
            'theme_color_error_title': 'Kesalahan warna',
            'theme_color_error': 'Masukkan HEX (#RRGGBB) atau RGB (R,G,B) yang valid.',
            'theme_color_placeholder': '#D0BCFF',
            'social_telegram': "Telegram",
            'social_reddit': "Reddit",
            'social_github': "GitHub",
            'social_site_script': "Situs Skrip",
            'theme_color_label': 'Warna tema',
            'theme_color_picker': 'Pilih warna',
            'theme_color_apply': 'Terapkan',
            'theme_color_hint': 'Masukkan HEX (#RRGGBB) atau RGB (R,G,B)',
            'theme_color_error_title': 'Kesalahan warna',
            'theme_color_error': 'Masukkan HEX (#RRGGBB) atau RGB (R,G,B) yang valid.',
            'theme_color_placeholder': '#D0BCFF',
            'ping_default': "Gagal mendapatkan ping server!\nMenggunakan nilai default: {} ms",
            'ping_avg': "Rata-rata ping: {:.2f} ms",
            'ntp_connect': "Mencoba terhubung ke server NTP: {}",
            'ntp_time': "Waktu Beijing diterima dari server {}: {}",
            'ntp_failed': "Gagal terhubung ke server NTP mana pun.",
            'time_wait': "Menunggu waktu ping (23:59:30 waktu Beijing)...",
            'target_time': "Menunggu hingga {} (disesuaikan dengan ping {} ms untuk mencapai tengah malam)",
            'target_time_manual': "Menunggu hingga {} (mode manual)",
            'time_reached': "Waktu tercapai: {}. Memulai pengiriman permintaan...",
            'cookie_skipped': "Pemeriksaan cookie dilewati sesuai pengaturan",
            'cookie_expired': "Cookie kedaluwarsa, harap perbarui",
            'account_ready': "[Status] Akun dapat mengirim permintaan buka kunci.",
            'account_blocked': "[Status] Akun diblokir hingga {} (Bulan/Hari).",
            'account_new': "[Status] Akun dibuat kurang dari 30 hari yang lalu.",
            'account_approved': "[Status] Aplikasi disetujui, buka kunci hingga {}.",
            'account_unknown': "[Kesalahan] Status tidak dikenal.",
            'status_error': "[Kesalahan pemeriksaan status] {}",
            'request_sent': "\nMengirim permintaan pada {} (UTC+8)",
            'response_received': "Respons diterima pada {} (UTC+8)",
            'update_not_available': "Tidak ada pembaruan",
            'update_check_error': "Kesalahan saat memeriksa pembaruan",
            'request_failed': "[Kesalahan] Gagal mengirim permintaan",
            'response_error': "[Kesalahan pemrosesan respons] {}",
            'request_error': "[Kesalahan permintaan] {}",
            'confirm_warning': "Harap konfirmasi bahwa Anda memahami semua risiko!",
            'cookie_error': "Masukkan nilai cookie!",
            'token_status_check_failed': "Kesalahan: pemeriksaan token/status gagal. Pengiriman dibatalkan. Nonaktifkan 'Nonaktifkan pemeriksaan Token Cookie sebelum pengiriman' jika Anda ingin melewati pemeriksaan.",
            'time_error': "Gagal menyinkronkan waktu!",
            'settings_saved': "\nPengaturan disimpan:",
            'cookie_check': "Pemeriksaan Token Cookie: {}",
            'default_ping': "Ping default: {} ms",
            'ping_note': "Nilai ini akan digunakan jika pengukuran ping ke server gagal.",
            'saved': "Pengaturan berhasil disimpan!",
            'instructions_title': "Instruksi dan Pengaturan Skrip",
            'about_title': "Tentang",
            'about_content': (
                "Alat untuk pengiriman permintaan otomatis\n"
                "untuk membuka kunci bootloader pada\n"
                "perangkat Xiaomi yang menjalankan HyperOS\n\n"
                "Versi skrip: 8.0"
            ),
            'general_title': "Persyaratan",
            'general_content': (
                "1. Akun Mi harus lebih dari 30 hari\n \n"
                "2. Akun Mi Community harus memiliki\n \n"
                "region Global\n \n"
                "3. Buka kunci tersedia untuk semua perangkat\n"
                "kecuali ROM China (CNXM)\n \n"
                "4. Perangkat menjalankan HyperOS"
            ),
            'firefox_title': "FireFox | Edge",
            'firefox_content': (
                "1. Unduh ekstensi Cookie Editor\n\n"
                "2. Masuk ke akun Anda (setelah keluar)\n"
                "di situs Xiaomi Mi Community:\n\n"
                "http://c.mi.com/global\n"
                "atau \n"
                "http://mi.com\n\n"
                "3. Di jendela Cookie Editor, ekstrak\n"
                "new_bbs_token dan salin\n\n"
                "Catatan penting:\n \n"
                "1. Semua waktu dalam skrip adalah waktu Beijing"
            ),
            'chrome_title': "Chrome",
            'chrome_content': (
                "1. Masuk ke akun Anda (setelah keluar)\n"
                "di situs Xiaomi Mi Community:\n"
                "https://c.mi.com/global\n"
                "atau \n"
                "https://mi.com\n\n"
                "2. Di bilah alamat browser, masukkan perintah:\n\n"
                "javascript :(function(){var token=document.cookie.match(/popRunToken=([^;]+)/);"
                "if(token){prompt(\"Salin token:\", token[1]);}"
                "else{alert(\"Token tidak ditemukan\");}})()\n\n"
                "*ingat untuk menghapus spasi setelah javascript saat menempelkan perintah ke bilah alamat browser*\n\n"
                "3. Salin nilai token dari jendela popup\n\n"
                "Catatan penting:\n \n"
                "1. Semua waktu dalam skrip adalah waktu Beijing"
            ),
            'trouble_title': "Pemecahan Masalah",
            'trouble_content': """Masalah: CookieEditor tidak menampilkan new_bbs_serviceToken

Solusi:

1. Segarkan halaman

2. Keluar dari akun Anda dan masuk kembali.

Masalah: Cookie kedaluwarsa atau tidak berfungsi

Kemungkinan penyebab:

• Region akun bukan Global (ganti)

• Cookie benar-benar kedaluwarsa

Masalah: Batas permintaan tercapai

Solusi:

Periksa status di Mi Unlock di pengaturan ponsel

Masalah: Kesalahan 10001 dan lainnya

Solusi:

Skrip gagal mengirim permintaan

Hubungi pengembang:

• Melalui grup Telegram:

https://t.me/miunlocktoolrevamp""",
            'authors_title': "Pengembang",
            'authors_content': """Pengembang:

• pktloss | Tg: @hyeplet231

• New Gen | Tg: @new_g3n

Tautan:

Grup Telegram: https://t.me/miunlocktoolrevamp

GitHub: https://github.com/AsInsideOut/miunlocktool

Reddit: https://www.reddit.com/r/miunlocktool

Skrip ini didasarkan pada:

• Vierta

Versi skrip: 8.0""",
            'cookie_checkbox': "Nonaktifkan pemeriksaan Token Cookie sebelum pengiriman",
            'final_unlock_checkbox': "Pengajuan selesai. Coba pasang telepon terlepas dari hasilnya.",
            'ping_label': "Ping default (ms):",
            'color_theme_label': "Tema warna:",
            'color_theme_xiaomi_orange': "Xiaomi Orange",
            'color_theme_red_sun': "Red Sun",
            'color_theme_blue_world': "Blue World",
            'save_btn': "Simpan",
            'close_btn': "Tutup",
            'ping_error_title': "Kesalahan",
            'ping_error_msg': "Ping harus berupa angka positif.",
            'cookie_error_title': "Kesalahan",
            'error_title': "Kesalahan",
            'account_blocked_title': "Informasi",
            'account_new_title': "Informasi",
            'account_approved_title': "Sukses",
            'unknown_status_title': "Kesalahan",
            'install_error': "Kesalahan Instalasi",
            'import_error': "Kesalahan Impor",
            'settings': "Pengaturan",
            'cookie_check_state': "Dinonaktifkan",
            'ban_risk': "Saya menyadari risiko kemungkinan pemblokiran akun",
            'submit_application': "Mulai Aplikasi",
            'script_info': "Instruksi dan Pengaturan Skrip",
            'exit': "Keluar",
            'execution_log': "Log Eksekusi",
            'clear_log_btn': "Bersihkan",
            'unlock_process': "Memulai proses buka kunci...",
            'auto_mode': "Mode Otomatis",
            'auto_mode_1': "Mode Otomatis #1",
            'auto_mode_2': "Mode Otomatis",
            'manual_mode': "Mode Manual",
            'manual_time_label': "Waktu pengiriman (detik):",
            'manual_time_hint': "58.5 - 59.8 (contoh: 59.1)",
            'manual_mode_start': "Mode manual: mengirim pada 23:59:{}",
            'manual_time_error': "Waktu tidak valid. Gunakan format 58.5 - 59.8",
            'application_not_submitted': "[Status] Aplikasi tidak terkirim, batas terlampaui, coba lagi pada {} (Bulan/Hari).",
            'device_binding_hint': "Coba ikat perangkat di Pengaturan, Bagian Status Mi Unlock",
            'theme_label': "Tema antarmuka:",
            'theme_system': "Sistem",
            'theme_light': "Terang",
            'theme_dark': "Gelap",
            'theme_locked_notice': "Saat ini hanya tema gelap yang tersedia",
            'mode_label': "Mode operasi:",
            'cookies_title': "Mendapatkan Cookies",
            'expand_cookies': "▶ Mendapatkan Cookies",
            'collapse_cookies': "▼ Mendapatkan Cookies",
            'check_updates': "Periksa Pembaruan",
            'update_available': "Pembaruan tersedia",
            'update_not_available': "Tidak ada pembaruan",
            'update_checking': "Memeriksa pembaruan...",
            'update_error': "Kesalahan saat memeriksa pembaruan",
            'current_version': "Versi saat ini: {}",
            'your_region': "Wilayah Anda: {}",
            'latest_version': "Versi terbaru: {}",
            'update_btn_ok': "Baik",
            'update_btn_update': "Perbarui",
            'update_message': "Versi baru {} tersedia! Apakah Anda ingin membuka halaman unduhan?",
            'time_synchronized': "Waktu disinkronkan",
            'ms': "ms",
            'default': "default",
            'welcome_title': "Xiaomi Unlock Tool",
            'welcome_text': (
                "Selamat datang di Xiaomi Unlock Tool!\n\n"
                "PERINGATAN PENTING:\n\n"
                "SEBELUM MENGGUNAKAN, BACA INSTRUKSI DENGAN SEKSAMA!\n\n"
                "1. Menggunakan alat ini dapat menyebabkan pemblokiran pengiriman.\n\n"
                "2. Alat ini HANYA untuk perangkat dengan HyperOS Global\n"
                "   dan TIDAK bekerja dengan model China.\n\n"
                "3. Persyaratan:\n"
                "   • Akun Mi lebih dari 30 hari\n"
                "   • Akun Mi Community dengan region Global\n"
                "   • Perangkat pada HyperOS 1-3\n\n"
                "4. Dengan menggunakan alat ini, Anda setuju bahwa pengembang tidak bertanggung jawab atas perangkat Anda.\n\n"
                "Klik 'Lanjutkan' untuk memulai."
            ),
            'welcome_btn': "Lanjutkan",
            'ping_hint': "Nilai ini akan digunakan jika ping ke server tidak dapat diukur.",
            'color_theme_xiaomi': "Xiaomi Orange",
            'color_theme_blue': "Blue World",
            'color_theme_red': "Red Sun",
            'language_label': "Bahasa",
            'log_to_txt_checkbox': "Log ke file TXT",
            'animations_checkbox': "Nonaktifkan animasi",
            'animations_development': "Sedang dikembangkan",
            'input_label': "Input",
            'application_status': "Status pengajuan: {}",
            'application_status_not_sent': "Belum dikirim",
            'application_status_sending': "Mengirim",
            'application_status_success': "Berhasil",
            'application_status_unknown': "Tidak diketahui",
            'application_status_failed': "Tidak berhasil",
            'spam_mode_checkbox': "Pengiriman Spam (dalam Mode Otomatis)",
            'spam_mode_desc': "Mengirim permintaan pada 23:59:58.6, 58.8 (disesuaikan dengan ping).\nJika dinonaktifkan, mengirim satu permintaan pada waktu optimal.",
            'ping_not_measured_manual': "Ping: tidak diukur (mode manual)",
            'log_auto_mode_spam_selected': "Mode otomatis dipilih (Spam - 5 permintaan)",
            'log_auto_mode_single_selected': "Mode otomatis dipilih (Permintaan tunggal)",
            'log_manual_mode_selected': "Mode manual dipilih",
            'log_time_gt_2355': "Waktu > 23:58. Menyinkronkan waktu sebelum memulai...",
            'log_time_sync_success': "Waktu berhasil disinkronkan!",
            'log_ping_wait': "Menunggu pengukuran ping pada 23:59:30 (Beijing)...",
            'status_ping_wait': "Menunggu 23:59:30 untuk mengukur ping...",
            'log_ping_time_passed': "Waktu pengukuran ping telah lewat. Menyinkronkan dan mengukur sekarang...",
            'log_ping_start': "Waktunya mengukur ping! Melakukan pengukuran...",
            'log_measuring_ping': "Mengukur ping ke server...",
            'log_ping_measured': "Ping terukur: {} ms",
            'log_time_updated': "Waktu diperbarui: {}",
            'log_resync_error': "Kesalahan sinkronisasi ulang, melanjutkan dengan pengatur waktu saat ini.",
            'log_normal_mode_ping': "Mode normal: menghitung ping...",
            'log_calculated_send_time': "Perkiraan waktu pengiriman (untuk mencapai tengah malam): 23:59:{}",
            'log_spam_mode_targets': "MODE SPAM: Waktu target (setelah penyesuaian ping): {}",
            'status_spam_wait': "Menunggu serangan spam...",
            'log_spam_sending_at': "[Spam #{}] Mengirim permintaan pada 23:59:{}s",
            'log_spam_new_device_id': "[Spam #{}] DeviceId baru: {}",
            'log_spam_response_prefix': "[Spam #{}] Waktu: {}s",
            'log_spam_success_prefix': "SUKSES!",
            'log_spam_response_format': "{} | Kode: {} | {}",
            'log_spam_parse_error': "[Spam #{}] Kesalahan mengurai respons: {}",
            'log_spam_no_response': "[Spam #{}] Tidak ada respons dari server",
            'log_spam_send_error': "[Spam #{}] Kesalahan mengirim permintaan: {}",
            'login_title': "Login Akun Xiaomi",
            'login_user_label': "ID Mi Account / Email / Telepon:",
            'login_user_placeholder': "Masukkan login Anda",
            'login_pwd_label': "Kata Sandi:",
            'login_pwd_placeholder': "********",
            'wb_instruction': "1. Klik tombol di bawah untuk membuka halaman konfirmasi di browser Anda.\n2. Setelah Anda melihat 'R':'','S':'OK' di halaman, salin tautan lengkap dari bilah alamat.",
            'wb_instruction_after_open': "Tempel tautan lengkap di bidang di bawah.",
            'wb_id_label': "Tautan konfirmasi (wb_id):",
            'wb_id_placeholder': "Tempel tautan di sini...",
            'open_confirmation_page': "Buka halaman konfirmasi",
            'login_button': "Masuk dan Dapatkan Token",
            'login_disabled_notice': "Sementara tidak tersedia",
            'logging_in': "Masuk...",
            'login_fields_error': "Isi semua bidang (login, kata sandi, dan tautan)!",
            'login_success': "Login berhasil! Token diperoleh.",
            'login_failed': "Login gagal",
            'login_failed_generic': "Login gagal. Periksa kredensial Anda.",
            'login_token_extract_error': "Tidak dapat mengekstrak token secara otomatis. Silakan salin secara manual dari c.mi.com/global.",
            'mi_unlock_title': "Mi Unlock Tool",
            'mi_unlock_checking_python': "Memeriksa instalasi Python",
            'mi_unlock_upgrading': 'Memperbarui miunlock...',
            'mi_unlock_python_found': "Python ditemukan: {}",
            'mi_unlock_python_not_found': "Python tidak ditemukan!",
            'mi_unlock_python_error_msg': (
                "Python tidak ditemukan!\n\n"
                "Mi Unlock Tool memerlukan Python 3.8 atau lebih tinggi.\n\n"
                "Unduh Python dari situs resmi:\n"
                "https://www.python.org/downloads/\n\n"
                "PENTING: Saat instalasi, pastikan untuk mencentang\n"
                "'Add Python to PATH'"
            ),
            'mi_unlock_installing': "Menginstal paket miunlock...",
            'mi_unlock_install_cmd': "Menjalankan: pip install miunlock",
            'mi_unlock_already_installed': "Paket miunlock sudah terinstal",
            'mi_unlock_install_success': "Paket miunlock berhasil diinstal",
            'mi_unlock_install_error': "Gagal menginstal miunlock!",
            'mi_unlock_starting': "Memulai Mi Unlock Tool...",
            'mi_unlock_launching': "Menjalankan miunlock...",
            'mi_unlock_file_not_found': "File tidak ditemukan: {}",
            'mi_unlock_not_found': "Error: miunlock tidak ditemukan!",
            'mi_unlock_completed': "Mi Unlock Tool telah selesai",
            'mi_unlock_finished': "Program selesai",
            'mi_unlock_error': "Error: {}",
            'mi_unlock_critical_error': "Error kritis: {}",
            'mi_unlock_close': "Tutup",
            'mi_unlock_input_label': "Input",
            'mi_unlock_input_placeholder': "Masukkan respons dan tekan Enter...",
            'mi_unlock_send_btn': "Kirim",
            'mi_unlock_input_prefix': "→ {}",
            'mi_unlock_input_error': "Kesalahan pengiriman input: {}",
            'mi_unlock_stdout_error': "Kesalahan membaca stdout: {}",
            'mi_unlock_stderr_error': "Kesalahan membaca stderr: {}",
            'mi_unlock_auto_sending': "→ Mengirim Enter otomatis...",
            'mi_unlock_auto_send_error': "Kesalahan kirim otomatis: {}",
            'mi_unlock_read_error': "Kesalahan baca: {}",
            'mi_unlock_process_exit': "Proses keluar dengan kode: {}",
            'mi_unlock_initial_enter': "→ Mengirim Enter awal otomatis...",
            'mi_unlock_auto_send_final': "→ Mengirim Enter akhir otomatis...",
            'pre_generation_title': "GENERASI DEVICE ID AWAL:",
            'pre_generation_main': "  Device_id utama: {}",
            'pre_generation_spam1': "  Spam device_id #1: {}",
            'pre_generation_spam2': "  Spam device_id #2: {}",
            'pre_generation_spam3': "  Spam device_id #3: {}",
            'pre_generation_spam4': "  Spam device_id #4: {}",
            'pre_generation_spam5': "  Spam device_id #5: {}",
            'logs_sent': "Log berhasil dikirim ke server",
            'logs_send_error': "Kesalahan mengirim log: {}",
            'spam_using_device_id': "[Spam #{}] Menggunakan device_id: {}",
            'send_with_token': "Mengirim dengan token #{}",
            # New keys
            'tcp_ping_label': "Ping TCP",
            'http_ping_label': "Ping HTTP",
            'measuring_pings': "Mengukur ping (HTTP dan TCP)...",
            'scheduling_requests': "Menjadwalkan permintaan...",
            'http_request': "Permintaan HTTP #{}",
            'tcp_request': "Permintaan TCP #{}",
            'ping_measure_done': "Pengukuran ping selesai.",
            'ping_measure_time_come': "Waktu pengukuran ping telah tiba, memulai sekarang.",
            'ping_http_default': "Ping HTTP tidak dapat diukur, menggunakan nilai default: {} ms",
            'ping_tcp_default': "Ping TCP tidak dapat diukur, menggunakan nilai default: {} ms",
            'ping_measure_result': "Pengukuran selesai. HTTP: {:.2f} ms, TCP: {:.2f} ms",
            'http_request_log': "Permintaan HTTP #{}: device_id={}, mengirim dalam {:.3f}s",
            'tcp_request_log': "Permintaan TCP #{}: device_id={}, mengirim dalam {:.3f}s",
            'mi_unlock_label': "Mi Unlock",
            'mi_unlock_desc': (
                "Alat untuk membuka kunci dengan Mi Unlock\n"
                "Oleh: pktloss, New G3n\n"
                "Versi: 8.0"
            ),
            'mi_unlock_python_not_found': "Python: tidak ditemukan",
            'mi_unlock_python_found_label': "Python: {}",
            'mi_unlock_package_not_installed': "miunlock: tidak terinstal",
            'mi_unlock_package_installed': "miunlock: terinstal",
            'mi_unlock_start_button': "Mulai Mi Unlock",
            'mi_unlock_process_interrupted': "Proses dihentikan oleh pengguna",
            'mi_unlock_log_title': "Log Eksekusi",
            'mi_unlock_drivers_button': "Unduh Driver",
        }

    def get_spanish(self):
        return {
            'title': "Xiaomi Unlock Tool",
            'main_title': "Xiaomi Unlock Tool",
            'desc': (
                "Herramienta para el envío automático de solicitudes de desbloqueo\n"
                "Por: pktloss, New G3n\n"
                "Versión: 8.0"
            ),
            'desc_manual': (
                "Modo manual - seleccione la hora de envío manualmente\n"
                "Por: pktloss, New G3n\n"
                "Versión: 8.0"
            ),
            'params': "Parámetros",
            'tab_unlock': "Enviar Solicitud",
            'tab_settings': "Configuración e Instrucciones",
            'tab_mi_unlock': "Mi Unlock",
            'log_success_prefix': "¡ÉXITO!",
            'log_code_message': "Código: {code} | Mensaje: {msg}",
            'log_request_parse_error': "[Error al procesar respuesta] No se pudo analizar JSON: {data}",
            'log_request_failed_no_response': "[Error] No se pudo enviar la solicitud (sin respuesta)",
            'log_request_exception': "[Error de solicitud] {error}",
            'cookie_label': "New_bbs_ServiceToken:",
            'cookie_placeholder': "Pegue su token aquí...",
            'login_btn': "🔑 Iniciar sesión en la cuenta",
            'check_eligibility_btn': "Verificar elegibilidad",
            'checking_eligibility': "Comprobando elegibilidad de la cuenta...",
            'eligibility_eligible_title': "Verificación de elegibilidad",
            'login_title': "Autorización de cuenta Xiaomi",
            'login_subtitle': "Extracción automática de New_bbs_serviceToken",
            'login_tab_qr': "Código QR / Navegador",
            'login_tab_existing': "Cuenta guardada",
            'login_existing_found': "Sesión de cuenta Mi guardada detectada",
            'login_existing_id': "ID de cuenta: {}",
            'login_use_existing_btn': "⚡ Usar esta cuenta",
            'login_qr_scan_tip': "Escanee el código QR en la aplicación Mi Community\no con la cámara de su teléfono Xiaomi",
            'login_open_browser_btn': "🌐 Iniciar sesión con el navegador",
            'login_refresh_qr': "🔄 Actualizar código QR",
            'login_waiting': "Esperando confirmación de autorización...",
            'login_qr_expired': "El código QR ha caducado. Haga clic en 'Actualizar código QR'.",
            'login_loading_qr': "⏳ Cargando código QR...",
            'login_browser_opened': "Página de inicio de sesión abierta en el navegador. Esperando finalización...",
            'login_refreshing_qr': "Actualizando código QR...",
            'login_qr_fetch_error': "Error al obtener código QR: {}",
            'login_authorized_extracting': "¡Autorización confirmada! Extrayendo token...",
            'login_extracting_token': "Extrayendo token...",
            'login_session_expired': "La sesión ha caducado",
            'login_success': "¡Autorización exitosa! new_bbs_serviceToken obtenido.",
            'login_error': "Error de autorización: {}",
            'login_token_extract_error': "No se pudo extraer el token de la respuesta del servidor.",
            'close_btn': "Cerrar",
            'log_token_check_success': "Verificación de token y estado aprobada con éxito.",
            'log_token_check_skipped': "Advertencia: la verificación de token está desactivada en la configuración, continuando...",
            'log_mode2_selected': "Modo Automático #2 seleccionado (spam HTTP hacia 23:59:59)",
            'log_mode2_ntp_saved': "Modo Automático #2: Sincronización NTP guardada, modo sin medición de ping",
            'status_mode2_waiting': "Modo Automático #2: esperando a las 23:59:59",
            'log_mode2_beijing_reached': "Modo Automático #2: hora de Pekín 23:59:59 alcanzada",
            'status_mode2_sending': "Modo Automático #2: enviando paquete HTTP",
            'mode2_prefix': "Modo Automático #2",
            'mode2_timing': "temporización",
            'log_mode2_plan_sent': "Plan de spam HTTP enviado",
            'mode2_using_device_id': "[Modo Automático #2 HTTP #{}] Usando device_id: {}",
            'request_prefix': "Solicitud",
            'req_using_device_id': "[Solicitud #{}] Usando device_id: {}",
            'log_ping_start_http_tcp': "Iniciando medición de pings HTTP y TCP...",
            'log_ping_avg_http': "Ping HTTP promedio: {:.2f} ms",
            'log_ping_http_failed': "No se pudo medir el ping HTTP",
            'log_ping_avg_tcp': "Ping TCP promedio: {:.2f} ms",
            'log_ping_tcp_failed': "No se pudo medir el ping TCP",
            'status_get_failed': "[Error] No se pudo obtener el estado de desbloqueo.",
            'status_app_approved_checking': "[Estado] Solicitud aprobada, verificando estado...",
            'status_app_rejected_100001': "[Estado] Solicitud rechazada, error de solicitud (código 100001).",
            'status_app_possibly_approved': "[Estado] Solicitud posiblemente aprobada, verificando estado...",
            'success_dialog_title': "¡Éxito!",
            'success_dialog_message': "¡Éxito! Intente vincular su cuenta.",
            'theme_dark_only': "Tema oscuro (solo el tema oscuro está disponible)",
            'confirm': "Reconozco el riesgo de posible bloqueo de cuenta",
            'info': "Información",
            'status_ready': "Listo para comenzar",
            'ping': "Ping: no medido",
            'time': "Hora: no sincronizada",
            'start_btn': "Iniciar Solicitud",
            'instructions_btn': "Instrucciones y Configuración",
            'exit_btn': "Salir",
            'log': "Registro de Ejecución",
            'clear_log_btn': "Limpiar",
            'update_not_available': "No se encontraron actualizaciones",
            'update_check_error': "Error al buscar actualizaciones",
            'unlock_start': "Iniciando proceso de desbloqueo...",
            'device_id_gen': "DeviceId generado: {}",
            'ping_start': "Calculando ping...",
            'ping_server': "Ping a {}: {:.2f} ms",
            'ping_failed': "No se pudo obtener ping del servidor {}",
            'ping_error': "Error al hacer ping a {}: {}",
            'open_miflash': "MiFlash Unlock",
            'social_telegram': "Telegram",
            'social_reddit': "Reddit",
            'social_github': "GitHub",
            'social_site_script': "Sitio del Script",
            'theme_color_label': 'Color del tema',
            'theme_color_picker': 'Elegir color',
            'theme_color_apply': 'Aplicar',
            'theme_color_hint': 'Introduce HEX (#RRGGBB) o RGB (R,G,B)',
            'theme_color_error_title': 'Error de color',
            'theme_color_error': 'Introduce un HEX (#RRGGBB) o RGB (R,G,B) válido.',
            'theme_color_placeholder': '#D0BCFF',
            'ping_default': "¡No se pudo obtener ping de ningún servidor!\nUsando valor predeterminado: {} ms",
            'ping_avg': "Ping promedio: {:.2f} ms",
            'ntp_connect': "Intentando conectar al servidor NTP: {}",
            'ntp_time': "Hora de Pekín recibida del servidor {}: {}",
            'ntp_failed': "No se pudo conectar a ningún servidor NTP.",
            'time_wait': "Esperando hora para ping (23:59:30 hora de Pekín)...",
            'target_time': "Esperando hasta {} (ajustado por ping {} ms para llegar a la medianoche)",
            'target_time_manual': "Esperando hasta {} (modo manual)",
            'time_reached': "Hora alcanzada: {}. Iniciando envío de solicitud...",
            'cookie_skipped': "Verificación de cookie omitida según configuración",
            'cookie_expired': "Cookie caducada, por favor actualícela",
            'account_ready': "[Estado] La cuenta puede enviar solicitud de desbloqueo.",
            'account_blocked': "[Estado] La cuenta tiene bloqueo de envío hasta {} (Mes/Día).",
            'account_new': "[Estado] La cuenta fue creada hace menos de 30 días.",
            'account_approved': "[Estado] Solicitud aprobada, desbloqueo posible hasta {}.",
            'account_unknown': "[Error] Estado desconocido.",
            'status_error': "[Error al verificar estado] {}",
            'request_sent': "\nEnviando solicitud a las {} (UTC+8)",
            'response_received': "Respuesta recibida a las {} (UTC+8)",
            'request_failed': "[Error] No se pudo enviar la solicitud",
            'response_error': "[Error al procesar respuesta] {}",
            'request_error': "[Error de solicitud] {}",
            'confirm_warning': "¡Por favor confirme que comprende todos los riesgos!",
            'cookie_error': "¡Ingrese el valor de la cookie!",
            'token_status_check_failed': "Error: la comprobación del token/estado falló. Se detuvo el envío. Desactive 'Desactivar verificación de Token Cookie antes del envío' si desea omitir la comprobación.",
            'time_error': "¡No se pudo sincronizar la hora!",
            'settings_saved': "\nConfiguración guardada:",
            'cookie_check': "Verificación de Token Cookie: {}",
            'default_ping': "Ping predeterminado: {} ms",
            'ping_note': "Este valor se usará si falla la medición de ping a los servidores.",
            'saved': "¡Configuración guardada exitosamente!",
            'instructions_title': "Instrucciones y Configuración",
            'about_title': "Acerca de",
            'about_content': (
                "Herramienta para envío automático de solicitudes\n"
                "de desbloqueo de gestor de arranque en\n"
                "dispositivos Xiaomi con HyperOS\n\n"
                "Versión del script: 8.0"
            ),
            'general_title': "Requisitos",
            'general_content': (
                "1. La cuenta Mi debe tener más de 30 días\n \n"
                "2. La cuenta de Mi Community debe tener\n \n"
                "región Global configurada\n \n"
                "3. Desbloqueo disponible para todos los dispositivos\n"
                "excepto ROM China (CNXM)\n \n"
                "4. El dispositivo debe tener HyperOS"
            ),
            'firefox_title': "FireFox | Edge",
            'firefox_content': (
                "1. Descargue la extensión Cookie Editor\n\n"
                "2. Inicie sesión en su cuenta (después de cerrar sesión)\n"
                "en el sitio de Xiaomi Mi Community:\n\n"
                "http://c.mi.com/global\n"
                "o \n"
                "http://mi.com\n\n"
                "3. En la ventana de Cookie Editor, extraiga\n"
                "new_bbs_token y cópielo\n\n"
                "Notas importantes:\n \n"
                "1. Todas las horas en el script son hora de Pekín"
            ),
            'chrome_title': "Chrome",
            'chrome_content': (
                "1. Inicie sesión en su cuenta (después de cerrar sesión)\n"
                "en el sitio de Xiaomi Mi Community:\n"
                "https://c.mi.com/global\n"
                "o \n"
                "https://mi.com\n\n"
                "2. En la barra de direcciones del navegador, ingrese el comando:\n\n"
                "javascript :(function(){var token=document.cookie.match(/popRunToken=([^;]+)/);"
                "if(token){prompt(\"Copiar token:\", token[1]);}"
                "else{alert(\"Token no encontrado\");}})()\n\n"
                "*recuerde quitar el espacio después de javascript al pegar el comando en la barra de direcciones del navegador*\n\n"
                "3. Copie el valor del token de la ventana emergente\n\n"
                "Notas importantes:\n \n"
                "1. Todas las horas en el script son hora de Pekín"
            ),
            'trouble_title': "Solución de Problemas",
            'trouble_content': """Problema: CookieEditor no muestra new_bbs_serviceToken

Solución:

1. Actualice la página

2. Cierre sesión y vuelva a iniciarla

Problema: Cookie caducada o no funciona

Posibles causas:

• La región de la cuenta no es Global (cámbiela)

• La cookie realmente ha caducado

Problema: Límite de solicitudes alcanzado

Solución:

Verifique el estado en Mi Unlock en la configuración del teléfono

Problema: Errores 10001 y otros

Solución:

El script no pudo enviar la solicitud

Contacte a los desarrolladores:

• A través del grupo de Telegram:

https://t.me/miunlocktoolrevamp""",
            'authors_title': "Autores",
            'authors_content': """Desarrolladores:

• pktloss | Tg: @hyeplet231

• New Gen | Tg: @new_g3n

Enlaces:

Grupo de Telegram: https://t.me/miunlocktoolrevamp

GitHub: https://github.com/AsInsideOut/miunlocktool

Reddit: https://www.reddit.com/r/miunlocktool

El script está basado en:

• Vierta

Versión del script: 8.0""",
            'cookie_checkbox': "Desactivar verificación de Token Cookie antes del envío",
            'final_unlock_checkbox': "La solicitud ha terminado. Intente vincular el teléfono sin importar el resultado.",
            'ping_label': "Ping predeterminado (ms):",
            'color_theme_label': "Tema de color:",
            'color_theme_xiaomi_orange': "Xiaomi Orange",
            'color_theme_red_sun': "Red Sun",
            'color_theme_blue_world': "Blue World",
            'save_btn': "Guardar",
            'close_btn': "Cerrar",
            'ping_error_title': "Error",
            'ping_error_msg': "¡El ping debe ser un número positivo!",
            'cookie_error_title': "Error",
            'error_title': "Error",
            'account_blocked_title': "Información",
            'account_new_title': "Información",
            'account_approved_title': "Éxito",
            'unknown_status_title': "Error",
            'install_error': "Error de Instalación",
            'import_error': "Error de Importación",
            'settings': "Configuración",
            'cookie_check_state': "Desactivada",
            'ban_risk': "Reconozco el riesgo de posible bloqueo de cuenta",
            'submit_application': "Iniciar Solicitud",
            'script_info': "Instrucciones y Configuración",
            'exit': "Salir",
            'execution_log': "Registro de Ejecución",
            'clear_log_btn': "Limpiar",
            'unlock_process': "Iniciando proceso de desbloqueo...",
            'auto_mode': "Modo Automático",
            'auto_mode_1': "Modo Automático #1",
            'auto_mode_2': "Modo Automático",
            'manual_mode': "Modo Manual",
            'manual_time_label': "Hora de envío (segundos):",
            'manual_time_hint': "58.5 - 59.8 (ejemplo: 59.1)",
            'manual_mode_start': "Modo manual: enviando a las 23:59:{}",
            'manual_time_error': "Hora inválida. Use formato 58.5 - 59.8",
            'application_not_submitted': "[Estado] Solicitud no enviada, límite excedido, intente de nuevo el {} (Mes/Día).",
            'device_binding_hint': "Intente vincular dispositivos en Configuración, Sección Estado Mi Unlock",
            'theme_label': "Tema de interfaz:",
            'theme_system': "Sistema",
            'theme_light': "Claro",
            'theme_dark': "Oscuro",
            'theme_locked_notice': "Temporalmente solo está disponible el tema oscuro",
            'mode_label': "Modo de operación:",
            'cookies_title': "Obtener Cookies",
            'expand_cookies': "▶ Obtener Cookies",
            'collapse_cookies': "▼ Obtener Cookies",
            'check_updates': "Buscar Actualizaciones",
            'update_available': "Actualización disponible",
            'update_not_available': "No se encontraron actualizaciones",
            'update_checking': "Buscando actualizaciones...",
            'update_error': "Error al buscar actualizaciones",
            'current_version': "Versión actual: {}",
            'your_region': "Su región: {}",
            'latest_version': "Última versión: {}",
            'update_btn_ok': "Bien",
            'update_btn_update': "Actualizar",
            'update_message': "¡Nueva versión {} disponible! ¿Desea ir a la página de descarga?",
            'time_synchronized': "Hora sincronizada",
            'ms': "ms",
            'default': "predeterminado",
            'welcome_title': "Xiaomi Unlock Tool",
            'welcome_text': (
                "¡Bienvenido a Xiaomi Unlock Tool!\n\n"
                "ADVERTENCIA IMPORTANTE:\n\n"
                "¡ANTES DE USAR, LEA CUIDADOSAMENTE LAS INSTRUCCIONES!\n\n"
                "1. El uso de esta herramienta puede provocar bloqueo de envío.\n\n"
                "2. La herramienta es SOLO para dispositivos con HyperOS Global\n"
                "   y NO funciona con modelos chinos.\n\n"
                "3. Requisitos:\n"
                "   • Cuenta Mi con más de 30 días\n"
                "   • Cuenta Mi Community con región Global\n"
                "   • Dispositivo con HyperOS 1-3\n\n"
                "4. Al usar esta herramienta, acepta que los desarrolladores no asumen responsabilidad por sus dispositivos.\n\n"
                "Haga clic en 'Continuar' para comenzar."
            ),
            'welcome_btn': "Continuar",
            'ping_hint': "Este valor se usará si no se puede medir el ping a los servidores.",
            'color_theme_xiaomi': "Xiaomi Orange",
            'color_theme_blue': "Blue World",
            'color_theme_red': "Red Sun",
            'language_label': "Idioma",
            'log_to_txt_checkbox': "Registrar en archivo TXT",
            'animations_checkbox': "Desactivar animaciones",
            'animations_development': "En desarrollo",
            'input_label': "Entrada",
            'application_status': "Estado de la solicitud: {}",
            'application_status_not_sent': "No enviada",
            'application_status_sending': "Enviando",
            'application_status_success': "Exitosa",
            'application_status_unknown': "Desconocido",
            'application_status_failed': "No exitosa",
            'spam_mode_checkbox': "Envío Spam (en Modo Automático)",
            'spam_mode_desc': "Envía solicitudes a las 23:59:58.6, 58.8 (ajustado por ping).\nSi está desactivado, envía una sola solicitud en el tiempo óptimo.",
            'ping_not_measured_manual': "Ping: no medido (modo manual)",
            'log_auto_mode_spam_selected': "Modo automático seleccionado (Spam - 5 solicitudes)",
            'log_auto_mode_single_selected': "Modo automático seleccionado (Solicitud única)",
            'log_manual_mode_selected': "Modo manual seleccionado",
            'log_time_gt_2355': "Hora > 23:58. Sincronizando hora antes de comenzar...",
            'log_time_sync_success': "¡Hora sincronizada exitosamente!",
            'log_ping_wait': "Esperando medición de ping a las 23:59:30 (Pekín)...",
            'status_ping_wait': "Esperando 23:59:30 para medir ping...",
            'log_ping_time_passed': "Hora de medición de ping pasada. Sincronizando y midiendo ahora...",
            'log_ping_start': "¡Hora de medir ping! Midiendo...",
            'log_measuring_ping': "Midiendo ping a los servidores...",
            'log_ping_measured': "Ping medido: {} ms",
            'log_time_updated': "Hora actualizada: {}",
            'log_resync_error': "Error de resincronización, continuando con el temporizador actual.",
            'log_normal_mode_ping': "Modo normal: calculando ping...",
            'log_calculated_send_time': "Tiempo de envío calculado (para llegar a la medianoche): 23:59:{}",
            'log_spam_mode_targets': "MODO SPAM: Tiempos objetivo (después del ajuste de ping): {}",
            'status_spam_wait': "Esperando ataque spam...",
            'log_spam_sending_at': "[Spam #{}] Enviando solicitud a las 23:59:{}s",
            'log_spam_new_device_id': "[Spam #{}] Nuevo deviceId: {}",
            'log_spam_response_prefix': "[Spam #{}] Tiempo: {}s",
            'log_spam_success_prefix': "¡ÉXITO!",
            'log_spam_response_format': "{} | Código: {} | {}",
            'log_spam_parse_error': "[Spam #{}] Error al analizar respuesta: {}",
            'log_spam_no_response': "[Spam #{}] No hay respuesta del servidor",
            'log_spam_send_error': "[Spam #{}] Error al enviar solicitud: {}",
            'login_title': "Inicio de sesión en cuenta Xiaomi",
            'login_user_label': "ID de Mi Account / Email / Teléfono:",
            'login_user_placeholder': "Ingrese su usuario",
            'login_pwd_label': "Contraseña:",
            'login_pwd_placeholder': "********",
            'wb_instruction': "1. Haga clic en el botón de abajo para abrir la página de confirmación en su navegador.\n2. Después de ver 'R':'','S':'OK' en la página, copie el enlace completo de la barra de direcciones.",
            'wb_instruction_after_open': "Pegue el enlace completo en el campo de abajo.",
            'wb_id_label': "Enlace de confirmación (wb_id):",
            'wb_id_placeholder': "Pegue el enlace aquí...",
            'open_confirmation_page': "Abrir página de confirmación",
            'login_button': "Iniciar sesión y obtener token",
            'login_disabled_notice': "Temporalmente no disponible",
            'logging_in': "Iniciando sesión...",
            'login_fields_error': "¡Complete todos los campos (usuario, contraseña y enlace)!",
            'login_success': "¡Inicio de sesión exitoso! Token obtenido.",
            'login_failed': "Error de inicio de sesión",
            'login_failed_generic': "Error de inicio de sesión. Verifique sus credenciales.",
            'login_token_extract_error': "No se pudo extraer el token automáticamente. Cópielo manualmente de c.mi.com/global.",
            'mi_unlock_title': "Mi Unlock Tool",
            'mi_unlock_checking_python': "Verificando instalación de Python",
            'mi_unlock_upgrading': 'Actualizando miunlock...',
            'mi_unlock_python_found': "Python encontrado: {}",
            'mi_unlock_python_not_found': "¡Python no encontrado!",
            'mi_unlock_python_error_msg': (
                "¡Python no encontrado!\n\n"
                "Mi Unlock Tool requiere Python 3.8 o superior.\n\n"
                "Descargue Python desde el sitio oficial:\n"
                "https://www.python.org/downloads/\n\n"
                "IMPORTANTE: Durante la instalación, asegúrese de marcar\n"
                "'Add Python to PATH'"
            ),
            'mi_unlock_installing': "Instalando paquete miunlock...",
            'mi_unlock_install_cmd': "Ejecutando: pip install miunlock",
            'mi_unlock_already_installed': "El paquete miunlock ya está instalado",
            'mi_unlock_install_success': "Paquete miunlock instalado correctamente",
            'mi_unlock_install_error': "¡Error al instalar miunlock!",
            'mi_unlock_starting': "Iniciando Mi Unlock Tool...",
            'mi_unlock_launching': "Lanzando miunlock...",
            'mi_unlock_file_not_found': "Archivo no encontrado: {}",
            'mi_unlock_not_found': "Error: ¡miunlock no encontrado!",
            'mi_unlock_completed': "Mi Unlock Tool ha finalizado",
            'mi_unlock_finished': "Programa finalizado",
            'mi_unlock_error': "Error: {}",
            'mi_unlock_critical_error': "Error crítico: {}",
            'mi_unlock_close': "Cerrar",
            'mi_unlock_input_label': "Entrada",
            'mi_unlock_input_placeholder': "Ingrese respuesta y presione Enter...",
            'mi_unlock_send_btn': "Enviar",
            'mi_unlock_input_prefix': "→ {}",
            'mi_unlock_input_error': "Error al enviar entrada: {}",
            'mi_unlock_stdout_error': "Error al leer stdout: {}",
            'mi_unlock_stderr_error': "Error al leer stderr: {}",
            'mi_unlock_auto_sending': "→ Enviando Enter automáticamente...",
            'mi_unlock_auto_send_error': "Error de envío automático: {}",
            'mi_unlock_read_error': "Error de lectura: {}",
            'mi_unlock_process_exit': "Proceso finalizado con código: {}",
            'mi_unlock_initial_enter': "→ Enviando Enter inicial automáticamente...",
            'mi_unlock_auto_send_final': "→ Enviando Enter final automáticamente...",
            'pre_generation_title': "GENERACIÓN PRELIMINAR DE DEVICE ID:",
            'pre_generation_main': "  Device_id principal: {}",
            'pre_generation_spam1': "  Spam device_id #1: {}",
            'pre_generation_spam2': "  Spam device_id #2: {}",
            'pre_generation_spam3': "  Spam device_id #3: {}",
            'pre_generation_spam4': "  Spam device_id #4: {}",
            'pre_generation_spam5': "  Spam device_id #5: {}",
            'logs_sent': "Logs enviados correctamente al servidor",
            'logs_send_error': "Error al enviar logs: {}",
            'spam_using_device_id': "[Spam #{}] Usando device_id: {}",
            'send_with_token': "Enviando con token #{}",
            # New keys
            'tcp_ping_label': "Ping TCP",
            'http_ping_label': "Ping HTTP",
            'measuring_pings': "Midiendo pings (HTTP y TCP)...",
            'scheduling_requests': "Programando solicitudes...",
            'http_request': "Solicitud HTTP #{}",
            'tcp_request': "Solicitud TCP #{}",
            'ping_measure_done': "Medición de ping completada.",
            'ping_measure_time_come': "Ha llegado el momento de medir el ping, comenzando ahora.",
            'ping_http_default': "No se pudo medir el ping HTTP, usando valor predeterminado: {} ms",
            'ping_tcp_default': "No se pudo medir el ping TCP, usando valor predeterminado: {} ms",
            'ping_measure_result': "Medición completada. HTTP: {:.2f} ms, TCP: {:.2f} ms",
            'http_request_log': "Solicitud HTTP #{}: device_id={}, enviando en {:.3f}s",
            'tcp_request_log': "Solicitud TCP #{}: device_id={}, enviando en {:.3f}s",
            'mi_unlock_label': "Mi Unlock",
            'mi_unlock_desc': (
                "Herramienta para desbloquear con Mi Unlock\n"
                "Por: pktloss, New G3n\n"
                "Versión: 8.0"
            ),
            'mi_unlock_python_not_found': "Python: no encontrado",
            'mi_unlock_python_found_label': "Python: {}",
            'mi_unlock_package_not_installed': "miunlock: no instalado",
            'mi_unlock_package_installed': "miunlock: instalado",
            'mi_unlock_start_button': "Iniciar Mi Unlock",
            'mi_unlock_process_interrupted': "Proceso interrumpido por el usuario",
            'mi_unlock_log_title': "Registro de Ejecución",
            'mi_unlock_drivers_button': "Descargar controladores",
        }

    def get_chinese(self):
        return {
            'title': "小米解锁工具",
            'main_title': "小米解锁工具",
            'desc': (
                "自动提交解锁申请的工具\n"
                "作者: pktloss, New G3n\n"
                "版本: 8.0"
            ),
            'desc_manual': (
                "手动模式 - 手动选择提交时间\n"
                "作者: pktloss, New G3n\n"
                "版本: 8.0"
            ),
            'params': "参数",
            'tab_unlock': "提交申请",
            'tab_settings': "设置和说明",
            'tab_mi_unlock': "Mi Unlock",
            'log_success_prefix': "成功！",
            'log_code_message': "代码: {code} | 消息: {msg}",
            'log_request_parse_error': "[响应处理错误] 无法解析JSON: {data}",
            'log_request_failed_no_response': "[错误] 无法发送请求（无响应）",
            'log_request_exception': "[请求错误] {error}",
            'cookie_label': "New_bbs_ServiceToken:",
            'cookie_placeholder': "在此粘贴您的令牌...",
            'login_btn': "🔑 登录小米账号",
            'check_eligibility_btn': "检查申请资格",
            'checking_eligibility': "正在检查账户申请资格...",
            'eligibility_eligible_title': "资格检查",
            'login_title': "小米账号授权",
            'login_subtitle': "自动获取 New_bbs_serviceToken",
            'login_tab_qr': "二维码 / 浏览器",
            'login_tab_existing': "已保存账号",
            'login_existing_found': "检测到已保存的小米账号会话",
            'login_existing_id': "账号 ID: {}",
            'login_use_existing_btn': "⚡ 使用此账号",
            'login_qr_scan_tip': "请使用小米社区 App 或小米手机相机扫描二维码",
            'login_open_browser_btn': "🌐 在浏览器中登录",
            'login_refresh_qr': "🔄 刷新二维码",
            'login_waiting': "等待授权确认...",
            'login_qr_expired': "二维码已过期，请点击“刷新二维码”。",
            'login_loading_qr': "⏳ 正在加载二维码...",
            'login_browser_opened': "已在浏览器中打开登录页面，等待完成...",
            'login_refreshing_qr': "正在刷新二维码...",
            'login_qr_fetch_error': "获取二维码失败: {}",
            'login_authorized_extracting': "授权已确认！正在提取令牌...",
            'login_extracting_token': "正在提取令牌...",
            'login_session_expired': "会话已过期",
            'login_success': "授权成功！已获取 new_bbs_serviceToken。",
            'login_error': "授权错误: {}",
            'login_token_extract_error': "未能从服务器响应中提取令牌。",
            'close_btn': "关闭",
            'log_token_check_success': "令牌与状态检查成功通过。",
            'log_token_check_skipped': "警告：设置中已禁用令牌验证，继续执行...",
            'log_mode2_selected': "已选择自动模式 #2（在 23:59:59 进行 HTTP 连续请求）",
            'log_mode2_ntp_saved': "自动模式 #2：NTP 时间同步已保存，无需测量延迟模式",
            'status_mode2_waiting': "自动模式 #2：等待 23:59:59",
            'log_mode2_beijing_reached': "自动模式 #2：已到达北京时间 23:59:59",
            'status_mode2_sending': "自动模式 #2：正在发送 HTTP 数据包",
            'mode2_prefix': "自动模式 #2",
            'mode2_timing': "计时",
            'log_mode2_plan_sent': "HTTP 连续请求计划已分发",
            'mode2_using_device_id': "[自动模式 #2 HTTP #{}] 使用 device_id: {}",
            'request_prefix': "请求",
            'req_using_device_id': "[请求 #{}] 使用 device_id: {}",
            'log_ping_start_http_tcp': "开始测量 HTTP 和 TCP 延迟...",
            'log_ping_avg_http': "平均 HTTP 延迟: {:.2f} 毫秒",
            'log_ping_http_failed': "无法测量 HTTP 延迟",
            'log_ping_avg_tcp': "平均 TCP 延迟: {:.2f} 毫秒",
            'log_ping_tcp_failed': "无法测量 TCP 延迟",
            'status_get_failed': "[错误] 无法获取解锁状态。",
            'status_app_approved_checking': "[状态] 申请已获批准，正在检查状态...",
            'status_app_rejected_100001': "[状态] 申请被拒绝，请求错误（代码 100001）。",
            'status_app_possibly_approved': "[状态] 申请可能已获批准，正在检查状态...",
            'success_dialog_title': "成功！",
            'success_dialog_message': "成功！请尝试绑定您的账号。",
            'theme_dark_only': "深色主题（仅提供深色主题）",
            'confirm': "我确认可能面临账户封禁的风险",
            'info': "信息",
            'status_ready': "准备就绪",
            'ping': "延迟: 未测量",
            'time': "时间: 未同步",
            'start_btn': "开始申请",
            'instructions_btn': "说明和脚本设置",
            'exit_btn': "退出",
            'log': "执行日志",
            'clear_log_btn': "清除",
            'unlock_start': "开始解锁过程...",
            'device_id_gen': "生成的deviceId: {}",
            'ping_start': "开始计算延迟...",
            'ping_server': "{} 的延迟: {:.2f} 毫秒",
            'ping_failed': "无法获取服务器 {} 的延迟",
            'ping_error': "ping {} 时出错: {}",
            'open_miflash': "小米解锁工具",
            'social_telegram': "Telegram",
            'social_reddit': "Reddit",
            'social_github': "GitHub",
            'social_site_script': "脚本网站",
            'theme_color_label': '主题颜色',
            'theme_color_picker': '选择颜色',
            'theme_color_apply': '应用',
            'theme_color_hint': '输入 HEX (#RRGGBB) 或 RGB (R,G,B)',
            'theme_color_error_title': '颜色错误',
            'theme_color_error': '请输入有效的 HEX (#RRGGBB) 或 RGB (R,G,B)。',
            'theme_color_placeholder': '#D0BCFF',
            'ping_default': "无法获取任何服务器的延迟！\n使用默认值: {} 毫秒",
            'ping_avg': "平均延迟: {:.2f} 毫秒",
            'ntp_connect': "尝试连接到NTP服务器: {}",
            'ntp_time': "从服务器 {} 接收到的北京时间: {}",
            'update_not_available': "未找到更新",
            'update_check_error': "检查更新时出错",
            'ntp_failed': "无法连接到任何NTP服务器。",
            'time_wait': "等待ping时间（北京时间23:59:30）...",
            'target_time': "等待至 {}（根据延迟 {} 毫秒调整以在午夜到达）",
            'target_time_manual': "等待至 {}（手动模式）",
            'time_reached': "时间到达: {}. 开始发送请求...",
            'cookie_skipped': "根据设置跳过cookie检查",
            'cookie_expired': "Cookie已过期，请更新",
            'account_ready': "[状态] 账户可以提交解锁申请。",
            'account_blocked': "[状态] 账户被禁止提交申请直至 {} (月/日)。",
            'account_new': "[状态] 账户创建不足30天。",
            'account_approved': "[状态] 申请已批准，可在 {} 前解锁。",
            'account_unknown': "[错误] 未知状态。",
            'status_error': "[状态检查错误] {}",
            'request_sent': "\n在 {} (UTC+8) 发送请求",
            'response_received': "在 {} (UTC+8) 收到响应",
            'request_failed': "[错误] 无法发送请求",
            'response_error': "[响应处理错误] {}",
            'request_error': "[请求错误] {}",
            'confirm_warning': "请确认您了解所有风险！",
            'cookie_error': "请输入cookie值！",
            'token_status_check_failed': "错误：令牌/状态检查失败。提交已停止。若要绕过检查，请关闭“在提交前禁用Token Cookie检查”。",
            'time_error': "无法同步时间！",
            'settings_saved': "\n设置已保存：",
            'cookie_check': "Token Cookie检查: {}",
            'default_ping': "默认延迟: {} 毫秒",
            'ping_note': "如果无法测量服务器延迟，将使用此值。",
            'saved': "设置保存成功！",
            'instructions_title': "说明和脚本设置",
            'about_title': "关于",
            'about_content': (
                "自动发送解锁引导加载程序请求的工具\n"
                "适用于运行HyperOS的小米设备\n\n"
                "脚本版本: 8.0"
            ),
            'general_title': "要求",
            'general_content': (
                "1. 小米账户必须超过30天\n \n"
                "2. Mi Community账户必须设置为\n \n"
                "全球区域\n \n"
                "3. 除中国ROM (CNXM)外的所有设备\n"
                "均可解锁\n \n"
                "4. 设备运行HyperOS"
            ),
            'firefox_title': "FireFox | Edge",
            'firefox_content': (
                "1. 下载Cookie Editor扩展\n\n"
                "2. 登录您的账户（先退出）\n"
                "在小米社区网站:\n\n"
                "http://c.mi.com/global\n"
                "或 \n"
                "http://mi.com\n\n"
                "3. 在Cookie Editor窗口中提取\n"
                "new_bbs_token并复制\n\n"
                "重要说明:\n \n"
                "1. 脚本中的所有时间均为北京时间"
            ),
            'chrome_title': "Chrome",
            'chrome_content': (
                "1. 登录您的账户（先退出）\n"
                "在小米社区网站:\n"
                "https://c.mi.com/global\n"
                "或 \n"
                "https://mi.com\n\n"
                "2. 在浏览器地址栏输入命令:\n\n"
                "javascript :(function(){var token=document.cookie.match(/popRunToken=([^;]+)/);"
                "if(token){prompt(\"复制令牌:\", token[1]);}"
                "else{alert(\"未找到令牌\");}})()\n\n"
                "*将命令粘贴到浏览器地址栏时，请记得删除javascript后面的空格*\n\n"
                "3. 从弹出窗口复制令牌值\n\n"
                "重要说明:\n \n"
                "1. 脚本中的所有时间均为北京时间"
            ),
            'trouble_title': "故障排除",
            'trouble_content': """问题：CookieEditor不显示new_bbs_serviceToken

解决方案：

1. 刷新页面

2. 退出并重新登录

问题：Cookie过期或不起作用

可能的原因：

• 账户区域不是全球（切换它）

• Cookie确实已过期

问题：达到请求限制

解决方案：

在手机设置中检查Mi Unlock状态

问题：错误10001和其他

解决方案：

脚本无法提交请求

联系开发者：

• 通过Telegram群组：

https://t.me/miunlocktoolrevamp""",
            'authors_title': "作者",
            'authors_content': """开发者：

• pktloss | Tg: @hyeplet231

• New Gen | Tg: @new_g3n

链接：

Telegram群组：https://t.me/miunlocktoolrevamp

GitHub：https://github.com/AsInsideOut/miunlocktool

Reddit：https://www.reddit.com/r/miunlocktool

脚本基于：

• Vierta

脚本版本：8.0""",
            'cookie_checkbox': "在提交前禁用Token Cookie检查",
            'final_unlock_checkbox': "提交已完成。无论结果如何，都请尝试绑定手机。",
            'ping_label': "默认延迟（毫秒）:",
            'color_theme_label': "颜色主题:",
            'color_theme_xiaomi_orange': "小米橙色",
            'color_theme_red_sun': "红日",
            'color_theme_blue_world': "蓝色世界",
            'save_btn': "保存",
            'close_btn': "关闭",
            'ping_error_title': "错误",
            'ping_error_msg': "延迟必须为正数！",
            'cookie_error_title': "错误",
            'error_title': "错误",
            'account_blocked_title': "信息",
            'account_new_title': "信息",
            'account_approved_title': "成功",
            'unknown_status_title': "错误",
            'install_error': "安装错误",
            'import_error': "导入错误",
            'settings': "设置",
            'cookie_check_state': "已禁用",
            'ban_risk': "我确认可能面临账户封禁的风险",
            'submit_application': "开始申请",
            'script_info': "说明和脚本设置",
            'exit': "退出",
            'execution_log': "执行日志",
            'clear_log_btn': "清除",
            'unlock_process': "开始解锁过程...",
            'auto_mode': "自动模式",
            'auto_mode_1': "自动模式 1",
            'auto_mode_2': "自动模式",
            'manual_mode': "手动模式",
            'manual_time_label': "提交时间（秒）:",
            'manual_time_hint': "58.5 - 59.8（例如：59.1）",
            'manual_mode_start': "手动模式：在23:59:{}发送",
            'manual_time_error': "时间无效。请使用格式58.5 - 59.8",
            'application_not_submitted': "[状态] 申请未提交，超出限制，请在 {} (月/日) 重试。",
            'device_binding_hint': "尝试在设置中的Mi Unlock状态部分绑定设备",
            'theme_label': "界面主题:",
            'theme_system': "系统",
            'theme_light': "浅色",
            'theme_dark': "深色",
            'theme_locked_notice': "暂时仅可使用深色主题",
            'mode_label': "操作模式:",
            'cookies_title': "获取Cookies",
            'expand_cookies': "▶ 获取Cookies",
            'collapse_cookies': "▼ 获取Cookies",
            'check_updates': "检查更新",
            'update_available': "有新更新可用",
            'update_not_available': "未找到更新",
            'update_checking': "正在检查更新...",
            'update_error': "检查更新时出错",
            'current_version': "当前版本: {}",
            'your_region': "您的地区: {}",
            'latest_version': "最新版本: {}",
            'update_btn_ok': "好的",
            'update_btn_update': "更新",
            'update_message': "新版本 {} 可用！是否前往下载页面？",
            'time_synchronized': "时间已同步",
            'ms': "毫秒",
            'default': "默认",
            'welcome_title': "小米解锁工具",
            'welcome_text': (
                "欢迎使用小米解锁工具！\n\n"
                "重要警告：\n\n"
                "使用前请仔细阅读说明！\n\n"
                "1. 使用此工具可能导致提交申请被禁止。\n\n"
                "2. 此工具仅适用于全球版HyperOS设备\n"
                "   不适用于中国型号。\n\n"
                "3. 要求：\n"
                "   • 小米账户超过30天\n"
                "   • Mi Community账户设置为全球区域\n"
                "   • 设备运行HyperOS 1-3\n\n"
                "4. 使用此工具即表示您同意开发者不对您的设备承担任何责任。\n\n"
                "点击'继续'开始。"
            ),
            'welcome_btn': "继续",
            'ping_hint': "如果无法测量到服务器的延迟，将使用此值。",
            'color_theme_xiaomi': "小米橙色",
            'color_theme_blue': "蓝色世界",
            'color_theme_red': "红日",
            'language_label': "语言",
            'log_to_txt_checkbox': "记录到TXT文件",
            'animations_checkbox': "禁用动画",
            'animations_development': "开发中",
            'input_label': "输入",
            'application_status': "申请状态：{}",
            'application_status_not_sent': "未发送",
            'application_status_sending': "发送中",
            'application_status_success': "成功",
            'application_status_unknown': "未知",
            'application_status_failed': "未成功",
            'spam_mode_checkbox': "垃圾邮件发送（自动模式下）",
            'spam_mode_desc': "在23:59:58.6、58.8秒发送请求（根据延迟调整）。\n如果禁用，则在最佳时间发送单个请求。",
            'ping_not_measured_manual': "延迟: 未测量（手动模式）",
            'log_auto_mode_spam_selected': "选择了自动模式（垃圾邮件 - 5个请求）",
            'log_auto_mode_single_selected': "选择了自动模式（单个请求）",
            'log_manual_mode_selected': "选择了手动模式",
            'log_time_gt_2355': "时间 > 23:58。开始前同步时间...",
            'log_time_sync_success': "时间同步成功！",
            'log_ping_wait': "等待在23:59:30（北京时间）测量延迟...",
            'status_ping_wait': "等待23:59:30测量延迟...",
            'log_ping_time_passed': "延迟测量时间已过。正在同步并立即测量...",
            'log_ping_start': "延迟测量时间到！正在测量...",
            'log_measuring_ping': "正在测量服务器延迟...",
            'log_ping_measured': "测得延迟: {} ms",
            'log_time_updated': "时间更新: {}",
            'log_resync_error': "重新同步错误，继续使用当前计时器。",
            'log_normal_mode_ping': "正常模式：计算延迟...",
            'log_calculated_send_time': "计算发送时间（以在午夜到达）: 23:59:{}",
            'log_spam_mode_targets': "垃圾邮件模式：目标时间（延迟调整后）: {}",
            'status_spam_wait': "等待垃圾邮件攻击...",
            'log_spam_sending_at': "[垃圾邮件 #{}] 在23:59:{}s发送请求",
            'log_spam_new_device_id': "[垃圾邮件 #{}] 新deviceId: {}",
            'log_spam_response_prefix': "[垃圾邮件 #{}] 时间: {}s",
            'log_spam_success_prefix': "成功！",
            'log_spam_response_format': "{} | 代码: {} | {}",
            'log_spam_parse_error': "[垃圾邮件 #{}] 解析响应错误: {}",
            'log_spam_no_response': "[垃圾邮件 #{}] 服务器无响应",
            'log_spam_send_error': "[垃圾邮件 #{}] 发送请求错误: {}",
            'login_title': "小米账户登录",
            'login_user_label': "小米账户ID / 邮箱 / 电话:",
            'login_user_placeholder': "输入您的登录名",
            'login_pwd_label': "密码:",
            'login_pwd_placeholder': "********",
            'wb_instruction': "1. 点击下面的按钮在浏览器中打开确认页面。\n2. 在页面上看到 'R':'','S':'OK' 后，从地址栏复制完整链接。",
            'wb_instruction_after_open': "将完整链接粘贴到下面的字段中。",
            'wb_id_label': "确认链接 (wb_id):",
            'wb_id_placeholder': "在此粘贴链接...",
            'open_confirmation_page': "打开确认页面",
            'login_button': "登录并获取令牌",
            'login_disabled_notice': "暂时不可用",
            'logging_in': "登录中...",
            'login_fields_error': "请填写所有字段（登录名、密码和链接）！",
            'login_success': "登录成功！已获取令牌。",
            'login_failed': "登录失败",
            'login_failed_generic': "登录失败。请检查您的凭据。",
            'login_token_extract_error': "无法自动提取令牌。请从 c.mi.com/global 手动复制。",
            'mi_unlock_title': "Mi Unlock 工具",
            'mi_unlock_checking_python': "检查 Python 安装",
            'mi_unlock_upgrading': '正在升级 miunlock...',
            'mi_unlock_python_found': "找到 Python: {}",
            'mi_unlock_python_not_found': "未找到 Python！",
            'mi_unlock_python_error_msg': (
                "未找到 Python！\n\n"
                "Mi Unlock 工具需要 Python 3.8 或更高版本。\n\n"
                "从官方网站下载 Python：\n"
                "https://www.python.org/downloads/\n\n"
                "重要：安装时，请确保勾选\n"
                "'Add Python to PATH'（将 Python 添加到 PATH）"
            ),
            'mi_unlock_installing': "正在安装 miunlock 包...",
            'mi_unlock_install_cmd': "正在执行：pip install miunlock",
            'mi_unlock_already_installed': "miunlock 包已安装",
            'mi_unlock_install_success': "miunlock 包安装成功",
            'mi_unlock_install_error': "安装 miunlock 失败！",
            'mi_unlock_starting': "正在启动 Mi Unlock 工具...",
            'mi_unlock_launching': "正在启动 miunlock...",
            'mi_unlock_file_not_found': "文件未找到：{}",
            'mi_unlock_not_found': "错误：未找到 miunlock！",
            'mi_unlock_completed': "Mi Unlock 工具已完成",
            'mi_unlock_finished': "程序已完成",
            'mi_unlock_error': "错误：{}",
            'mi_unlock_critical_error': "严重错误：{}",
            'mi_unlock_close': "关闭",
            'mi_unlock_input_label': "输入",
            'mi_unlock_input_placeholder': "输入响应并按 Enter...",
            'mi_unlock_send_btn': "发送",
            'mi_unlock_input_prefix': "→ {}",
            'mi_unlock_input_error': "输入发送错误：{}",
            'mi_unlock_stdout_error': "读取 stdout 错误：{}",
            'mi_unlock_stderr_error': "读取 stderr 错误：{}",
            'mi_unlock_auto_sending': "→ 自动发送 Enter...",
            'mi_unlock_auto_send_error': "自动发送错误: {}",
            'mi_unlock_read_error': "读取错误: {}",
            'mi_unlock_process_exit': "进程退出代码: {}",
            'mi_unlock_initial_enter': "→ 自动发送初始 Enter...",
            'mi_unlock_auto_send_final': "→ 自动发送最终 Enter...",
            'pre_generation_title': "预生成 DEVICE ID：",
            'pre_generation_main': "  主 device_id: {}",
            'pre_generation_spam1': "  垃圾请求 device_id #1: {}",
            'pre_generation_spam2': "  垃圾请求 device_id #2: {}",
            'pre_generation_spam3': "  垃圾请求 device_id #3: {}",
            'pre_generation_spam4': "  垃圾请求 device_id #4: {}",
            'pre_generation_spam5': "  垃圾请求 device_id #5: {}",
            'logs_sent': "日志已成功发送到服务器",
            'logs_send_error': "发送日志时出错：{}",
            'spam_using_device_id': "[垃圾请求 #{}] 使用 device_id: {}",
            'send_with_token': "使用令牌 #{} 发送",
            # New keys
            'tcp_ping_label': "TCP 延迟",
            'http_ping_label': "HTTP 延迟",
            'measuring_pings': "正在测量延迟 (HTTP 和 TCP)...",
            'scheduling_requests': "正在安排请求...",
            'http_request': "HTTP 请求 #{}",
            'tcp_request': "TCP 请求 #{}",
            'ping_measure_done': "延迟测量完成。",
            'ping_measure_time_come': "延迟测量时间已到，现在开始。",
            'ping_http_default': "无法测量 HTTP 延迟，使用默认值：{} 毫秒",
            'ping_tcp_default': "无法测量 TCP 延迟，使用默认值：{} 毫秒",
            'ping_measure_result': "测量完成。HTTP：{:.2f} 毫秒，TCP：{:.2f} 毫秒",
            'http_request_log': "HTTP 请求 #{}：device_id={}，将在 {:.3f} 秒后发送",
            'tcp_request_log': "TCP 请求 #{}：device_id={}，将在 {:.3f} 秒后发送",
            'mi_unlock_label': "Mi Unlock",
            'mi_unlock_desc': (
                "使用 Mi Unlock 解锁的工具\n"
                "作者：pktloss, New G3n\n"
                "版本：8.0"
            ),
            'mi_unlock_python_not_found': "Python：未找到",
            'mi_unlock_python_found_label': "Python：{}",
            'mi_unlock_package_not_installed': "miunlock：未安装",
            'mi_unlock_package_installed': "miunlock：已安装",
            'mi_unlock_start_button': "启动 Mi Unlock",
            'mi_unlock_process_interrupted': "进程被用户中断",
            'mi_unlock_log_title': "执行日志",
            'mi_unlock_drivers_button': "下载驱动",
        }

    def get_portuguese(self):
        return {
            'title': "Xiaomi Unlock Tool",
            'main_title': "Xiaomi Unlock Tool",
            'desc': (
                "Ferramenta para envio automático de solicitação de desbloqueio\n"
                "Por: pktloss, New G3n\n"
                "Versão: 8.0"
            ),
            'desc_manual': (
                "Modo manual - selecione o horário de envio manualmente\n"
                "Por: pktloss, New G3n\n"
                "Versão: 8.0"
            ),
            'params': "Parâmetros",
            'tab_unlock': "Enviar Aplicação",
            'tab_settings': "Configurações e Instruções",
            'tab_mi_unlock': "Mi Unlock",
            'log_success_prefix': "SUCESSO!",
            'log_code_message': "Código: {code} | Mensagem: {msg}",
            'log_request_parse_error': "[Erro ao processar resposta] Falha ao analisar JSON: {data}",
            'log_request_failed_no_response': "[Erro] Falha ao enviar solicitação (sem resposta)",
            'log_request_exception': "[Erro na solicitação] {error}",
            'cookie_label': "New_bbs_ServiceToken:",
            'cookie_placeholder': "Cole seu token aqui...",
            'login_btn': "🔑 Entrar na Conta",
            'check_eligibility_btn': "Verificar elegibilidade",
            'checking_eligibility': "Verificando elegibilidade da conta...",
            'eligibility_eligible_title': "Verificação de elegibilidade",
            'login_title': "Autorização de Conta Xiaomi",
            'login_subtitle': "Extração automática de New_bbs_serviceToken",
            'login_tab_qr': "Código QR / Navegador",
            'login_tab_existing': "Conta Salva",
            'login_existing_found': "Sessão de Conta Mi salva detectada",
            'login_existing_id': "ID da Conta: {}",
            'login_use_existing_btn': "⚡ Usar esta conta",
            'login_qr_scan_tip': "Escaneie o código QR no app Mi Community\nou com a câmera do seu celular Xiaomi",
            'login_open_browser_btn': "🌐 Fazer Login no Navegador",
            'login_refresh_qr': "🔄 Atualizar Código QR",
            'login_waiting': "Aguardando confirmação de autorização...",
            'login_qr_expired': "Código QR expirado. Clique em 'Atualizar Código QR'.",
            'login_loading_qr': "⏳ Carregando código QR...",
            'login_browser_opened': "Página de login aberta no navegador. Aguardando conclusão...",
            'login_refreshing_qr': "Atualizando código QR...",
            'login_qr_fetch_error': "Falha ao obter código QR: {}",
            'login_authorized_extracting': "Autorização confirmada! Extraindo token...",
            'login_extracting_token': "Extraindo token...",
            'login_session_expired': "Sessão expirada",
            'login_success': "Autorização bem-sucedida! new_bbs_serviceToken obtido.",
            'login_error': "Erro de autorização: {}",
            'login_token_extract_error': "Falha ao extrair token da resposta do servidor.",
            'close_btn': "Fechar",
            'log_token_check_success': "Verificação de token e status aprovada com sucesso.",
            'log_token_check_skipped': "Aviso: a verificação de token está desativada nas configurações, continuando...",
            'log_mode2_selected': "Modo Automático #2 selecionado (spam HTTP visando 23:59:59)",
            'log_mode2_ntp_saved': "Modo Automático #2: Sincronização NTP ativa, modo sem medição de ping",
            'status_mode2_waiting': "Modo Automático #2: aguardando 23:59:59",
            'log_mode2_beijing_reached': "Modo Automático #2: hora de Pequim 23:59:59 atingida",
            'status_mode2_sending': "Modo Automático #2: enviando pacote HTTP",
            'mode2_prefix': "Modo Automático #2",
            'mode2_timing': "temporização",
            'log_mode2_plan_sent': "Plano de spam HTTP enviado",
            'mode2_using_device_id': "[Modo Automático #2 HTTP #{}] Usando device_id: {}",
            'request_prefix': "Solicitação",
            'req_using_device_id': "[Solicitação #{}] Usando device_id: {}",
            'log_ping_start_http_tcp': "Iniciando medição de pings HTTP e TCP...",
            'log_ping_avg_http': "Ping HTTP médio: {:.2f} ms",
            'log_ping_http_failed': "Falha ao medir ping HTTP",
            'log_ping_avg_tcp': "Ping TCP médio: {:.2f} ms",
            'log_ping_tcp_failed': "Falha ao medir ping TCP",
            'status_get_failed': "[Erro] Falha ao obter status de desbloqueio.",
            'status_app_approved_checking': "[Status] Aplicação aprovada, verificando status...",
            'status_app_rejected_100001': "[Status] Aplicação rejeitada, erro de requisição (código 100001).",
            'status_app_possibly_approved': "[Status] Aplicação possivelmente aprovada, verificando status...",
            'success_dialog_title': "Sucesso!",
            'success_dialog_message': "Sucesso! Tente vincular sua conta.",
            'theme_dark_only': "Tema escuro (apenas tema escuro disponível)",
            'confirm': "Eu assumo o risco de possível banimento da conta",
            'info': "Informação",
            'status_ready': "Pronto para começar",
            'ping': "Ping: não medido",
            'time': "Hora: não sincronizada",
            'start_btn': "Iniciar Aplicação",
            'instructions_btn': "Instruções e Configurações do Script",
            'exit_btn': "Sair",
            'log': "Registro de Execução",
            'clear_log_btn': "Limpar",
            'unlock_start': "Iniciando processo de desbloqueio...",
            'device_id_gen': "DeviceId gerado: {}",
            'ping_start': "Iniciando cálculo do ping...",
            'ping_server': "Ping para {}: {:.2f} ms",
            'ping_failed': "Falha ao obter ping do servidor {}",
            'ping_error': "Erro ao fazer ping em {}: {}",
            'open_miflash': "MiFlash Unlock",
            'social_telegram': "Telegram",
            'social_reddit': "Reddit",
            'social_github': "GitHub",
            'social_site_script': "Site do Script",
            'theme_color_label': 'Cor do tema',
            'theme_color_picker': 'Escolher cor',
            'theme_color_apply': 'Aplicar',
            'theme_color_hint': 'Digite HEX (#RRGGBB) ou RGB (R,G,B)',
            'theme_color_error_title': 'Erro de cor',
            'theme_color_error': 'Digite um HEX (#RRGGBB) ou RGB (R,G,B) válido.',
            'theme_color_placeholder': '#D0BCFF',
            'ping_default': "Falha ao obter ping de qualquer servidor!\nUsando valor padrão: {} ms",
            'ping_avg': "Ping médio: {:.2f} ms",
            'ntp_connect': "Tentando conectar ao servidor NTP: {}",
            'ntp_time': "Horário de Pequim recebido do servidor {}: {}",
            'ntp_failed': "Falha ao conectar a qualquer servidor NTP.",
            'time_wait': "Aguardando horário para ping (23:59:30 Horário de Pequim)...",
            'target_time': "Aguardando até {} (ajustado para ping {} ms para chegar à meia-noite)",
            'target_time_manual': "Aguardando até {} (modo manual)",
            'update_not_available': "Nenhuma atualização encontrada",
            'update_check_error': "Erro ao verificar atualizações",
            'time_reached': "Horário atingido: {}. Iniciando envio da solicitação...",
            'cookie_skipped': "Verificação de cookie ignorada conforme configurações",
            'cookie_expired': "Cookie expirou, por favor atualize-o.",
            'account_ready': "[Status] A conta pode enviar solicitação de desbloqueio.",
            'account_blocked': "[Status] A conta tem bloqueio de envio até {} (Mês/Dia).",
            'account_new': "[Status] Conta criada há menos de 30 dias.",
            'account_approved': "[Status] Solicitação aprovada, desbloqueio possível até {}.",
            'account_unknown': "[Erro] Status desconhecido.",
            'status_error': "[Erro na verificação de status] {}",
            'request_sent': "\nEnviando solicitação às {} (UTC+8)",
            'response_received': "Resposta recebida às {} (UTC+8)",
            'request_failed': "[Erro] Falha ao enviar solicitação",
            'response_error': "[Erro ao processar resposta] {}",
            'request_error': "[Erro na solicitação] {}",
            'confirm_warning': "Por favor, confirme que você entende todos os riscos!",
            'cookie_error': "Insira o valor do cookie!",
            'token_status_check_failed': "Erro: a verificação do token/status falhou. O envio foi interrompido. Desative 'Desativar verificação do Token Cookie antes do envio' se quiser ignorar a verificação.",
            'time_error': "Falha ao sincronizar a hora!",
            'settings_saved': "\nConfigurações salvas:",
            'cookie_check': "Verificação do Token Cookie: {}",
            'default_ping': "Ping padrão: {} ms",
            'ping_note': "Este valor será usado se a medição de ping para os servidores falhar.",
            'saved': "Configurações salvas com sucesso!",
            'instructions_title': "Instruções e Configurações",
            'about_title': "Sobre",
            'about_content': (
                "Ferramenta para envio automático de solicitação\n"
                "para desbloqueio do bootloader em\n"
                "dispositivos Xiaomi com HyperOS\n\n"
                "Versão do script: 8.0"
            ),
            'general_title': "Requisitos",
            'general_content': (
                "1. A conta Mi deve ter mais de 30 dias\n \n"
                "2. A conta da Mi Community deve ter\n \n"
                "a região definida como Global\n \n"
                "3. Desbloqueio disponível para todos os dispositivos\n"
                "exceto ROM Chinesa (CNXM)\n \n"
                "4. O dispositivo está executando HyperOS"
            ),
            'firefox_title': "FireFox | Edge",
            'firefox_content': (
                "1. Baixe a extensão Cookie Editor\n\n"
                "2. Faça login na sua conta (depois de sair)\n"
                "no site da Xiaomi Mi Community:\n\n"
                "http://c.mi.com/global\n"
                "ou \n"
                "http://mi.com\n\n"
                "3. Na janela do Cookie Editor, extraia\n"
                "new_bbs_token e copie-o\n\n"
                "Notas importantes:\n \n"
                "1. Todos os horários no script são de Pequim"
            ),
            'chrome_title': "Chrome",
            'chrome_content': (
                "1. Faça login na sua conta (depois de sair)\n"
                "no site da Xiaomi Mi Community:\n"
                "https://c.mi.com/global\n"
                "ou \n"
                "https://mi.com\n\n"
                "2. Na barra de endereços do navegador, digite o comando:\n\n"
                "javascript :(function(){var token=document.cookie.match(/popRunToken=([^;]+)/);"
                "if(token){prompt(\"Copie o token:\", token[1]);}"
                "else{alert(\"Token não encontrado\");}})()\n\n"
                "*lembre-se de remover o espaço após javascript ao colar o comando na barra de endereços*\n\n"
                "3. Copie o valor do token da janela pop-up\n\n"
                "Notas importantes:\n \n"
                "1. Todos os horários no script são de Pequim"
            ),
            'trouble_title': "Solução de Problemas",
            'trouble_content': """Problema: O CookieEditor não mostra new_bbs_serviceToken

Solução:

1. Atualize a página

2. Saia e entre novamente

Problema: Cookie expirado ou não funciona

Possíveis causas:

• A região da conta não é Global (altere)

• O cookie realmente expirou

Problema: Limite de solicitações atingido

Solução:

Verifique o status no Mi Unlock nas configurações do telefone

Problema: Erros 10001 e outros

Solução:

O script não conseguiu enviar a solicitação

Contate os desenvolvedores:

• Via grupo do Telegram:

https://t.me/miunlocktoolrevamp""",
            'authors_title': "Autores",
            'authors_content': """Desenvolvedores:

• pktloss | Tg: @hyeplet231

• New Gen | Tg: @new_g3n

Links:

Grupo do Telegram: https://t.me/miunlocktoolrevamp

GitHub: https://github.com/AsInsideOut/miunlocktool

Reddit: https://www.reddit.com/r/miunlocktool

O script é baseado em:

• Vierta

Versão do script: 8.0""",
            'cookie_checkbox': "Desativar verificação do Token Cookie antes do envio",
            'final_unlock_checkbox': "A submissão foi concluída. Tente vincular o telefone independentemente do resultado.",
            'ping_label': "Ping padrão (ms):",
            'color_theme_label': "Tema de cor:",
            'color_theme_xiaomi_orange': "Xiaomi Laranja",
            'color_theme_red_sun': "Sol Vermelho",
            'color_theme_blue_world': "Mundo Azul",
            'save_btn': "Salvar",
            'close_btn': "Fechar",
            'ping_error_title': "Erro",
            'ping_error_msg': "O ping deve ser um número positivo!",
            'cookie_error_title': "Erro",
            'error_title': "Erro",
            'account_blocked_title': "Informação",
            'account_new_title': "Informação",
            'account_approved_title': "Sucesso",
            'unknown_status_title': "Erro",
            'install_error': "Erro de Instalação",
            'import_error': "Erro de Importação",
            'settings': "Configurações",
            'cookie_check_state': "Desativada",
            'ban_risk': "Eu assumo o risco de possível banimento da conta",
            'submit_application': "Iniciar Aplicação",
            'script_info': "Instruções e Configurações",
            'exit': "Sair",
            'execution_log': "Registro de Execução",
            'clear_log_btn': "Limpar",
            'unlock_process': "Iniciando processo de desbloqueio...",
            'auto_mode': "Modo Automático",
            'auto_mode_1': "Modo Automático #1",
            'auto_mode_2': "Modo Automático",
            'manual_mode': "Modo Manual",
            'manual_time_label': "Horário de envio (segundos):",
            'manual_time_hint': "58.5 - 59.8 (ex: 59.1)",
            'manual_mode_start': "Modo manual: enviando às 23:59:{}",
            'manual_time_error': "Horário inválido. Use o formato 58.5 - 59.8",
            'application_not_submitted': "[Status] Solicitação não enviada, limite excedido, tente novamente em {} (Mês/Dia).",
            'device_binding_hint': "Tente vincular dispositivos em Configurações, Seção Status do Mi Unlock",
            'theme_label': "Tema da interface:",
            'theme_system': "Sistema",
            'theme_light': "Claro",
            'theme_dark': "Escuro",
            'theme_locked_notice': "Temporariamente, apenas o tema escuro está disponível",
            'mode_label': "Modo de operação:",
            'cookies_title': "Obtendo Cookies",
            'expand_cookies': "▶ Obtendo Cookies",
            'collapse_cookies': "▼ Obtendo Cookies",
            'check_updates': "Verificar Atualizações",
            'update_available': "Nova atualização disponível",
            'update_not_available': "Nenhuma atualização encontrada",
            'update_checking': "Verificando atualizações...",
            'update_error': "Erro ao verificar atualizações",
            'current_version': "Versão atual: {}",
            'your_region': "Sua região: {}",
            'latest_version': "Última versão: {}",
            'update_btn_ok': "Ok",
            'update_btn_update': "Atualizar",
            'update_message': "Nova versão {} disponível! Deseja ir para a página de download?",
            'time_synchronized': "Hora sincronizada",
            'ms': "ms",
            'default': "padrão",
            'welcome_title': "Xiaomi Unlock Tool",
            'welcome_text': (
                "Bem-vindo ao Xiaomi Unlock Tool!\n\n"
                "AVISO IMPORTANTE:\n\n"
                "ANTES DE USAR, LEIA ATENTAMENTE AS INSTRUÇÕES!\n\n"
                "1. O uso desta ferramenta pode levar ao bloqueio de envio.\n\n"
                "2. A ferramenta é SOMENTE para dispositivos com HyperOS Global\n"
                "   e NÃO funciona com modelos chineses.\n\n"
                "3. Requisitos:\n"
                "   • Conta Mi com mais de 30 dias\n"
                "   • Conta da Mi Community com região Global\n"
                "   • Dispositivo com HyperOS 1-3\n\n"
                "4. Ao usar esta ferramenta, você concorda que os desenvolvedores não se responsabilizam por seus dispositivos.\n\n"
                "Clique em 'Continuar' para começar."
            ),
            'welcome_btn': "Continuar",
            'ping_hint': "Este valor será usado se o ping para os servidores não puder ser medido.",
            'color_theme_xiaomi': "Xiaomi Laranja",
            'color_theme_blue': "Mundo Azul",
            'color_theme_red': "Sol Vermelho",
            'language_label': "Idioma",
            'log_to_txt_checkbox': "Registrar em arquivo TXT",
            'animations_checkbox': "Desativar animações",
            'animations_development': "Em desenvolvimento",
            'input_label': "Entrada",
            'application_status': "Status da aplicação: {}",
            'application_status_not_sent': "Não enviada",
            'application_status_sending': "Enviando",
            'application_status_success': "Bem-sucedida",
            'application_status_unknown': "Desconhecido",
            'application_status_failed': "Sem sucesso",
            'spam_mode_checkbox': "Envio Spam (no Modo Automático)",
            'spam_mode_desc': "Envia solicitações em 23:59:58.6 e 58.8 (ajustado pelo ping).\nSe desativado, envia uma única solicitação no horário ideal.",
            'ping_not_measured_manual': "Ping: não medido (modo manual)",
            'log_auto_mode_spam_selected': "Modo automático selecionado (Spam - 5 solicitações)",
            'log_auto_mode_single_selected': "Modo automático selecionado (Solicitação única)",
            'log_manual_mode_selected': "Modo manual selecionado",
            'log_time_gt_2355': "Hora > 23:58. Sincronizando hora antes de começar...",
            'log_time_sync_success': "Hora sincronizada com sucesso!",
            'log_ping_wait': "Aguardando medição de ping às 23:59:30 (Pequim)...",
            'status_ping_wait': "Aguardando 23:59:30 para medir ping...",
            'log_ping_time_passed': "Hora de medição de ping passou. Sincronizando e medindo agora...",
            'log_ping_start': "Hora de medir ping! Executando medição...",
            'log_measuring_ping': "Medindo ping para os servidores...",
            'log_ping_measured': "Ping medido: {} ms",
            'log_time_updated': "Hora atualizada: {}",
            'log_resync_error': "Erro na ressincronização, continuando com o temporizador atual.",
            'log_normal_mode_ping': "Modo normal: calculando ping...",
            'log_calculated_send_time': "Hora de envio calculada (para chegar à meia-noite): 23:59:{}",
            'log_spam_mode_targets': "MODO SPAM: Horários alvo (após ajuste de ping): {}",
            'status_spam_wait': "Aguardando ataque spam...",
            'log_spam_sending_at': "[Spam #{}] Enviando solicitação às 23:59:{}s",
            'log_spam_new_device_id': "[Spam #{}] Novo deviceId: {}",
            'log_spam_response_prefix': "[Spam #{}] Hora: {}s",
            'log_spam_success_prefix': "SUCESSO!",
            'log_spam_response_format': "{} | Código: {} | {}",
            'log_spam_parse_error': "[Spam #{}] Erro ao analisar resposta: {}",
            'log_spam_no_response': "[Spam #{}] Sem resposta do servidor",
            'log_spam_send_error': "[Spam #{}] Erro ao enviar solicitação: {}",
            'login_title': "Login na Conta Xiaomi",
            'login_user_label': "ID do Mi Account / Email / Telefone:",
            'login_user_placeholder': "Digite seu login",
            'login_pwd_label': "Senha:",
            'login_pwd_placeholder': "********",
            'wb_instruction': "1. Clique no botão abaixo para abrir a página de confirmação no seu navegador.\n2. Após ver a mensagem 'R':'','S':'OK' na página, copie o link completo da barra de endereços.",
            'wb_instruction_after_open': "Cole o link completo no campo abaixo.",
            'wb_id_label': "Link de confirmação (wb_id):",
            'wb_id_placeholder': "Cole o link aqui...",
            'open_confirmation_page': "Abrir página de confirmação",
            'login_button': "Fazer Login e Obter Token",
            'login_disabled_notice': "Temporariamente indisponível",
            'logging_in': "Entrando...",
            'login_fields_error': "Preencha todos os campos (login, senha e link)!",
            'login_success': "Login bem-sucedido! Token obtido.",
            'login_failed': "Falha no login",
            'login_failed_generic': "Falha no login. Verifique seus dados.",
            'login_token_extract_error': "Não foi possível extrair o token automaticamente. Copie-o manualmente do site c.mi.com/global.",
            'mi_unlock_title': "Mi Unlock Tool",
            'mi_unlock_checking_python': "Verificando instalação do Python",
            'mi_unlock_upgrading': 'Atualizando miunlock...',
            'mi_unlock_python_found': "Python encontrado: {}",
            'mi_unlock_python_not_found': "Python não encontrado!",
            'mi_unlock_python_error_msg': (
                "Python não encontrado!\n\n"
                "Mi Unlock Tool requer Python 3.8 ou superior.\n\n"
                "Baixe o Python do site oficial:\n"
                "https://www.python.org/downloads/\n\n"
                "⚠️ IMPORTANTE: Durante a instalação, certifique-se de marcar\n"
                "'Add Python to PATH'"
            ),
            'mi_unlock_installing': "Instalando pacote miunlock...",
            'mi_unlock_install_cmd': "Executando: pip install miunlock",
            'mi_unlock_already_installed': "Pacote miunlock já está instalado",
            'mi_unlock_install_success': "Pacote miunlock instalado com sucesso",
            'mi_unlock_install_error': "Falha ao instalar miunlock!",
            'mi_unlock_starting': "Iniciando Mi Unlock Tool...",
            'mi_unlock_launching': "Executando miunlock...",
            'mi_unlock_file_not_found': "Arquivo não encontrado: {}",
            'mi_unlock_not_found': "Erro: miunlock não encontrado!",
            'mi_unlock_completed': "Mi Unlock Tool foi finalizado",
            'mi_unlock_finished': "Programa finalizado",
            'mi_unlock_error': "Erro: {}",
            'mi_unlock_critical_error': "Erro crítico: {}",
            'mi_unlock_close': "Fechar",
            'mi_unlock_input_label': "Entrada",
            'mi_unlock_input_placeholder': "Digite a resposta e pressione Enter...",
            'mi_unlock_send_btn': "Enviar",
            'mi_unlock_input_prefix': "→ {}",
            'mi_unlock_input_error': "Erro ao enviar entrada: {}",
            'mi_unlock_stdout_error': "Erro ao ler stdout: {}",
            'mi_unlock_stderr_error': "Erro ao ler stderr: {}",
            'mi_unlock_auto_sending': "→ Enviando Enter automaticamente...",
            'mi_unlock_auto_send_error': "Erro de envio automático: {}",
            'mi_unlock_read_error': "Erro de leitura: {}",
            'mi_unlock_process_exit': "Processo encerrado com código: {}",
            'mi_unlock_initial_enter': "→ Enviando Enter inicial automaticamente...",
            'mi_unlock_auto_send_final': "→ Enviando Enter final automaticamente...",
            'pre_generation_title': "GERAÇÃO PRELIMINAR DE DEVICE ID:",
            'pre_generation_main': "  Device_id principal: {}",
            'pre_generation_spam1': "  Spam device_id #1: {}",
            'pre_generation_spam2': "  Spam device_id #2: {}",
            'pre_generation_spam3': "  Spam device_id #3: {}",
            'pre_generation_spam4': "  Spam device_id #4: {}",
            'pre_generation_spam5': "  Spam device_id #5: {}",
            'logs_sent': "Logs enviados com sucesso ao servidor",
            'logs_send_error': "Erro ao enviar logs: {}",
            'spam_using_device_id': "[Spam #{}] Usando device_id: {}",
            'send_with_token': "Enviando com token #{}",
            # New keys
            'tcp_ping_label': "Ping TCP",
            'http_ping_label': "Ping HTTP",
            'measuring_pings': "Medindo pings (HTTP e TCP)...",
            'scheduling_requests': "Agendando solicitações...",
            'http_request': "Solicitação HTTP #{}",
            'tcp_request': "Solicitação TCP #{}",
            'ping_measure_done': "Medição de ping concluída.",
            'ping_measure_time_come': "O momento da medição de ping chegou, começando agora.",
            'ping_http_default': "Não foi possível medir o ping HTTP, usando valor padrão: {} ms",
            'ping_tcp_default': "Não foi possível medir o ping TCP, usando valor padrão: {} ms",
            'ping_measure_result': "Medição concluída. HTTP: {:.2f} ms, TCP: {:.2f} ms",
            'http_request_log': "Solicitação HTTP #{}: device_id={}, enviando em {:.3f}s",
            'tcp_request_log': "Solicitação TCP #{}: device_id={}, enviando em {:.3f}s",
            'mi_unlock_label': "Mi Unlock",
            'mi_unlock_desc': (
                "Ferramenta para desbloqueio com Mi Unlock\n"
                "Por: pktloss, New G3n\n"
                "Versão: 8.0"
            ),
            'mi_unlock_python_not_found': "Python: não encontrado",
            'mi_unlock_python_found_label': "Python: {}",
            'mi_unlock_package_not_installed': "miunlock: não instalado",
            'mi_unlock_package_installed': "miunlock: instalado",
            'mi_unlock_start_button': "Iniciar Mi Unlock",
            'mi_unlock_process_interrupted': "Processo interrompido pelo usuário",
            'mi_unlock_log_title': "Registro de Execução",
            'mi_unlock_drivers_button': "Baixar Drivers",
        }

    def _get_version(self):
        try:
            from .. import CURRENT_VERSION
            return CURRENT_VERSION
        except:
            return "8.0"

    def tr(self, key):
        return self.translations[self.language].get(key, key)