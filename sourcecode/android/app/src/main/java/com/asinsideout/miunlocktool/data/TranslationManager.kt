package com.asinsideout.miunlocktool.data

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

object TranslationManager {
    private const val TAG = "TranslationManager"
    private const val SERVER_BASE_URL = "https://miunlock.su/download/languages/android/strings-%s.json"

    val BUILTIN_EN: Map<String, String> = mapOf(
        "app_name" to "Xiaomi Unlock Tool",
        "app_subtitle" to "v8.2",
        "authors_devs_body" to "• pktloss, New G3n\\n• PC & CLI: New G3n\\n• Web & Android: pktloss\\n• Based on script by: Vierta",
        "authors_devs_title" to "Script Developers",
        "authors_donate_crypto" to "USDT (TON network):",
        "authors_donate_da" to "DonationAlerts: dalink.to/asinsideout",
        "authors_donate_title" to "Donate to Development",
        "authors_link_4pda" to "4PDA Forum",
        "authors_link_github" to "GitHub: AsInsideOut/miunlocktool",
        "authors_link_tg" to "Telegram: @miunlocktoolrevamp",
        "authors_link_web" to "Website: miunlock.su",
        "authors_social_title" to "Community & Links",
        "authors_title" to "Authors & Credits",
        "authors_wallet_address" to "UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG",
        "authors_wallet_copied" to "TON USDT address copied to clipboard!",
        "beijing_countdown_title" to "Countdown to 00:00:00",
        "beijing_time_title" to "Beijing Time (CST UTC+8)",
        "btn_check_update" to "Check for Updates",
        "btn_measure_ping" to "Measure Ping",
        "btn_send_now" to "Send Immediate Request",
        "btn_start_auto" to "Start Application",
        "btn_stop_auto" to "Stop Application",
        "btn_sync_ntp" to "Sync NTP",
        "close_btn" to "Close",
        "copy_address_btn" to "Copy Address",
        "dialog_error_title" to "Notice",
        "dialog_ok" to "OK",
        "dialog_quota_msg" to "All requests received code 0 (Success). Try binding your account in developer options.",
        "dialog_quota_title" to "Success!",
        "dialog_status_unavailable_title" to "Application Sent",
        "dialog_status_unavailable_msg" to "Application was sent successfully, but status is temporarily unavailable.\\n\\nPlease check your status in a few moments using the «Check Status» button.",
        "status_unavailable_desc" to "Status temporarily unavailable",
        "log_apply_sending" to "Submitting application...",
        "log_apply_sent_success" to "Application sent successfully",
        "log_getting_status" to "Retrieving status...",
        "log_status_unavailable" to "Failed to get status: invalid response format",
        "log_status_unavailable_summary" to "Application sent, but status is temporarily unavailable. Check later using 'Check Status'.",
        "log_apply_send_failed" to "Failed to send application: %s",
        "log_status_account_approved" to "Status confirmed: Account authorized until %s",
        "log_apply_sending_seq" to "[#%d] Submitting application...",
        "log_apply_sent_success_seq" to "[#%d] Application sent successfully",
        "log_getting_status_seq" to "[#%d] Retrieving status...",
        "log_apply_send_failed_seq" to "[#%d] Failed to send application: %s",
        "dialog_success_msg" to "Congratulations! Authorization granted. You can now bind your device in Settings > Developer Options > Mi Unlock Status.",
        "dialog_success_title" to "Success!",
        "downloading_language_pack" to "Downloading language pack: %s...",
        "guide_step1_body" to "Install firefox browser on your phone\\nInstall cookie-editor extension\\nGo to c.mi.com/global\\nOpen the cookie-editor extension and look for new_bbs_serviceToken\\nCopy the value and paste it into the app",
        "guide_step1_title" to "1. How to get new_bbs_serviceToken",
        "guide_step2_body" to "• Xiaomi Account must be active for at least 30 days.\\n• HyperOS Global/EEA/ID/TW/RU are supported (Mainland China CNXM is excluded).\\n• Xiaomi enforces a daily quota limit (~1500 devices) resetting at exactly 00:00:00 Beijing Time.\\n• Once approved, unlock authorization remains valid for 1 year.",
        "guide_step2_title" to "2. Prerequisites & Rules",
        "guide_step3_body" to "• After receiving approval in Xiaomi Unlock Tool, wait 1-2 minutes.\\n• Turn OFF Wi-Fi and turn ON Mobile Data (SIM card with active data connection is required by Xiaomi).\\n• Go to Settings > Additional Settings > Developer Options.\\n• Tap \\'Mi Unlock Status\\' > tap \\'Add account and device\\'.\\n• If successful, Xiaomi will show the standard waiting period (usually 72 hours / 168 hours).",
        "guide_step3_title" to "3. Binding Device in Developer Options",
        "guide_step4_body" to "• \\\"Couldn\\'t add. Please go to Mi Community to apply\\\": Daily 1500 device quota reached. Try again next day at 00:00:00 Beijing time with Auto Mode.\\n• \\\"System is being upgraded. Please try again later\\\": Common glitch on Redmi Note 13 series. Retry later.\\n• \\\"Code 100004 / Token expired\\\": Your web session ended. Generate a fresh new_bbs_serviceToken.",
        "guide_step4_title" to "4. Common Errors & Solutions",
        "guide_title" to "HyperOS Unlock Guide",
        "language_pack_downloaded" to "Language pack applied successfully!",
        "language_pack_error" to "Failed to download language pack. Check connection.",
        "log_auto_mode_started" to "Auto Mode started. Waiting for Beijing midnight...",
        "log_clear" to "Clear",
        "log_connecting_ntp" to "Connecting to NTP server: %s...",
        "log_copied" to "Logs copied to clipboard",
        "log_copy" to "Copy",
        "log_empty" to "Logs will appear here...",
        "log_error_token_empty" to "Error: Token is empty. Enter new_bbs_serviceToken first.",
        "log_error_token_expired" to "ERROR: Token expired. Please refresh your new_bbs_serviceToken.",
        "log_latency_measuring" to "Measuring latency to Xiaomi API...",
        "log_latency_result" to "Latency: HTTP: %d ms | TCP: %d ms (Avg: %d ms)",
        "log_manual_sending" to "Manual Mode: Sending request now with deviceId: %s...",
        "log_ntp_auto_reached" to "Beijing 23:59:00 reached: Synchronizing NTP automatically...",
        "log_ntp_failed" to "NTP synchronization failed. Using system clock.",
        "log_ntp_success" to "NTP Synchronized! Beijing Time: %s (Offset: %d ms)",
        "log_ping_result_pc" to "Ping measurement result: HTTP: %d ms | TCP: %d ms (Avg: %d ms)",
        "log_ping_wait_pc" to "Beijing 23:59:40 reached: Measuring API latency (HTTP & TCP) like PC version...",
        "log_process_stopped" to "Process stopped.",
        "log_response_code" to "[#%d] Response code: %d, message: %s",
        "log_scheduling_requests" to "[%s Profile] Scheduling %d timing requests: %s",
        "log_sending_target" to "[#%d/%d target 23:59:%s] Sending with deviceId: %s...",
        "log_success_100003" to "SUCCESS! Quota reached / Request queued (Code: 100003)! Check Developer Options for unlock binding!",
        "log_success_approved" to "SUCCESS! Application approved (Code: %d, Result: %s)! You can now bind your device!",
        "log_success_code0" to "SUCCESS: Request processed with code 0 (Success). Try binding your account in developer options.",
        "log_syncing_time" to "Syncing time with NTP...",
        "log_title" to "Execution Log",
        "log_trigger_time" to "Calculated trigger time: 23:59:%s",
        "login_authorized_extracting" to "Authorization confirmed! Extracting token...",
        "login_browser_opened" to "Login page opened in browser. Waiting for completion...",
        "login_btn" to "Log In to Account",
        "login_error" to "Authorization error: %s",
        "login_extracting_token" to "Extracting token...",
        "login_loading_qr" to "⏳ Loading QR code...",
        "login_open_browser_btn" to "🌐 Open in Browser",
        "login_qr_expired" to "QR code expired. Click \\'Refresh QR Code\\'.",
        "login_qr_fetch_error" to "Failed to fetch QR code: %s",
        "login_qr_scan_tip" to "Scan the QR code in the Mi Community app\\nor with your Xiaomi phone camera",
        "login_refresh_qr" to "🔄 Refresh QR Code",
        "login_refreshing_qr" to "Refreshing QR code...",
        "login_session_expired" to "Session expired",
        "login_subtitle" to "Automatic New_bbs_serviceToken extraction",
        "login_success" to "Authorization successful! new_bbs_serviceToken extracted.",
        "login_tab_qr" to "QR Code",
        "login_title" to "Xiaomi Account Authorization",
        "login_token_extract_error" to "Failed to extract token from server response.",
        "login_waiting" to "Waiting for authorization confirmation...",
        "mode_auto" to "Auto Mode",
        "mode_auto_desc" to "Fires high-speed requests with randomized device IDs around 23:59:58 Beijing time",
        "mode_manual" to "Manual Mode",
        "mode_manual_desc" to "Send immediate test request or manual burst",
        "modes_title" to "Execution Mode",
        "nav_apply" to "Apply",
        "nav_guide" to "Guide",
        "nav_settings" to "Settings",
        "notif_channel_desc" to "Live countdown and status of unlock application",
        "notif_channel_name" to "Application Status",
        "notif_countdown" to "Time to submit: %s",
        "notif_sending" to "Sending",
        "notif_success" to "Success!",
        "ping_measuring" to "Measuring ping...",
        "ping_title" to "API Ping Latency",
        "ping_unmeasured" to "Not measured",
        "section_token" to "Xiaomi Service Token",
        "send_offset_calc" to "Calculated time: %s",
        "settings_about_text" to "Tool for automatic request submission for bootloader unlocking on Xiaomi devices running HyperOS.\\n\\nVersion: 8.2",
        "settings_accent_color" to "Accent Color",
        "settings_apply_color" to "Apply",
        "settings_burst_count" to "Burst Request Count",
        "settings_burst_count_summary" to "%d requests",
        "settings_burst_interval" to "Burst Interval",
        "settings_burst_interval_summary" to "%d ms",
        "settings_color_applied" to "Accent color updated!",
        "settings_color_blue" to "Blue",
        "settings_color_custom" to "Custom",
        "settings_color_cyan" to "Cyan",
        "settings_color_green" to "Green",
        "settings_color_hex_hint" to "HEX: #2196F3 or #09F",
        "settings_color_orange" to "Orange",
        "settings_color_purple" to "Purple",
        "settings_color_red" to "Red",
        "settings_custom_timings_hint" to "Enter comma-separated timings (e.g. 58.700, 58.800)",
        "settings_invalid_hex" to "Invalid HEX format (e.g. #2196F3 or #09F)",
        "settings_lang_en" to "English",
        "settings_lang_es" to "Español",
        "settings_lang_id" to "Bahasa Indonesia",
        "settings_lang_pt" to "Português",
        "settings_lang_ru" to "Русский",
        "settings_lang_zh" to "简体中文",
        "settings_ntp_android" to "Android (time.android.com)",
        "settings_ntp_cloudflare" to "Cloudflare (time.cloudflare.com)",
        "settings_ntp_google" to "Google (time.google.com)",
        "settings_ntp_server" to "NTP Server",
        "settings_profile_asia" to "Asia (58.800, 59.100, 59.300, 59.500, 59.700)",
        "settings_profile_custom" to "Custom Timings",
        "settings_profile_europe" to "Europe (58.700, 58.800, 59.100, 59.300, 59.500, 59.800)",
        "settings_profile_usa_africa" to "USA / Africa (58.500, 58.800, 59.100, 59.300, 59.500, 59.700)",
        "settings_section_about" to "About & Authors",
        "settings_section_appearance" to "Appearance",
        "settings_section_language" to "Language",
        "settings_section_network" to "Network & NTP Synchronization",
        "settings_section_styling" to "Appearance & Styling",
        "settings_section_timing" to "Burst & Timing Parameters",
        "settings_section_timing_profile" to "Regional Timing Profiles",
        "settings_section_updates" to "Updates",
        "settings_theme" to "Theme",
        "settings_theme_dark" to "Dark",
        "settings_theme_light" to "Light (White)",
        "settings_theme_system" to "Follow System",
        "settings_title" to "Settings",
        "status_blocked" to "Account is temporarily blocked until %s",
        "status_checking" to "Checking account state...",
        "status_error" to "Error checking status: %s",
        "status_expired" to "Token has expired or is invalid. Please get a fresh token.",
        "status_not_checked" to "Not checked yet",
        "status_ready" to "Ready to apply! Quota resets at 00:00:00",
        "status_title" to "Account Status",
        "status_too_new" to "Account is too new. Minimum 30 days registration required.",
        "time_not_synced" to "Not synchronized",
        "time_syncing" to "Syncing NTP...",
        "toast_burst_started" to "Sending request burst...",
        "toast_started" to "Application scheduled. Waiting for Beijing midnight...",
        "toast_stopped" to "Application stopped.",
        "toast_token_required" to "Please enter or paste your new_bbs_serviceToken first!",
        "token_check_status" to "Check Status",
        "token_clear" to "Clear",
        "token_hint" to "new_bbs_serviceToken",
        "token_paste" to "Paste",
        "update_available_msg" to "A new version (%1\$s) is available!\\nCurrent version is %2\$s.\\n\\nDownload and install update?",
        "update_available_title" to "Update Available",
        "update_cancel_btn" to "Cancel",
        "update_checking" to "Checking for updates...",
        "update_download_btn" to "Download & Install",
        "update_download_error" to "Failed to download update: %s",
        "update_downloading" to "Downloading update (%d%%)...",
        "update_error_msg" to "Failed to connect to update server: %s",
        "update_error_title" to "Update Check Failed",
        "update_installing" to "Opening APK installer...",
        "update_latest_msg" to "You are using the latest version (%s).",
        "update_latest_title" to "Latest Version",
        "fastboot_title" to "Fastboot (USB OTG)",
        "fastboot_status_no_device" to "No USB device detected",
        "fastboot_status_attached" to "Device attached: %s",
        "fastboot_status_permission_required" to "Permission required",
        "fastboot_status_permission_denied" to "USB permission denied",
        "fastboot_status_connected" to "Connected: %s",
        "fastboot_status_disconnected" to "Disconnected",
        "fastboot_btn_connect" to "Connect",
        "fastboot_btn_disconnect" to "Disconnect",
        "fastboot_btn_get_product" to "Get Product",
        "fastboot_btn_get_token" to "Get Token",
        "fastboot_product_label" to "Product: %s",
        "fastboot_token_label" to "Token: %s",
        "fastboot_info_hint" to "Connect a target Xiaomi phone in Fastboot mode via USB OTG cable"
    )

    val BUILTIN_RU: Map<String, String> = mapOf(
        "app_name" to "Xiaomi Unlock Tool",
        "app_subtitle" to "v8.2",
        "authors_devs_body" to "• pktloss, New G3n\\n• Разработчик PC и CLI версии: New G3n\\n• Разработчик Сайта и Android версии: pktloss\\n• На основе скрипта: Vierta",
        "authors_devs_title" to "Разработчики Скрипта",
        "authors_donate_crypto" to "USDT сеть TON:",
        "authors_donate_da" to "DonationAlerts: dalink.to/asinsideout",
        "authors_donate_title" to "Пожертвовать на разработку",
        "authors_link_4pda" to "Тема на 4PDA",
        "authors_link_github" to "GitHub: AsInsideOut/miunlocktool",
        "authors_link_tg" to "Telegram: @miunlocktoolrevamp",
        "authors_link_web" to "Сайт: miunlocktool.ru",
        "authors_social_title" to "Ссылки на Соц Сети",
        "authors_title" to "Авторы",
        "authors_wallet_address" to "UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG",
        "authors_wallet_copied" to "Адрес TON USDT скопирован в буфер обмена!",
        "beijing_countdown_title" to "Обратный отсчёт до 00:00:00",
        "beijing_time_title" to "Пекинское время (CST UTC+8)",
        "btn_check_update" to "Проверить обновления",
        "btn_measure_ping" to "Измерить пинг",
        "btn_send_now" to "Отправить запрос сейчас",
        "btn_start_auto" to "Начать подачу заявки",
        "btn_stop_auto" to "Остановить подачу",
        "btn_sync_ntp" to "Синхр. NTP",
        "close_btn" to "Закрыть",
        "copy_address_btn" to "Копировать адрес",
        "dialog_error_title" to "Уведомление",
        "dialog_ok" to "OK",
        "dialog_quota_msg" to "Все заявки получили код 0 (Успех). Попробуйте привязать аккаунт в настройках разработчика.",
        "dialog_quota_title" to "Успех!",
        "dialog_status_unavailable_title" to "Заявка отправлена",
        "dialog_status_unavailable_msg" to "Заявка успешно отправлена, но статус временно недоступен.\\n\\nПроверьте статус через некоторое время нажатием кнопки «Проверить статус».",
        "status_unavailable_desc" to "Статус временно недоступен",
        "log_apply_sending" to "Отправка заявки...",
        "log_apply_sent_success" to "Заявка успешно отправлена",
        "log_getting_status" to "Получение статуса...",
        "log_status_unavailable" to "Не удалось получить статус: некорректный формат ответа",
        "log_status_unavailable_summary" to "Заявка отправлена, но статус временно недоступен. Проверьте статус позже кнопкой «Проверить статус».",
        "log_apply_send_failed" to "Не удалось отправить заявку: %s",
        "log_status_account_approved" to "Статус подтверждён: Аккаунт авторизован до %s",
        "log_apply_sending_seq" to "[#%d] Отправка заявки...",
        "log_apply_sent_success_seq" to "[#%d] Заявка успешно отправлена",
        "log_getting_status_seq" to "[#%d] Получение статуса...",
        "log_apply_send_failed_seq" to "[#%d] Ошибка отправки заявки: %s",
        "dialog_success_msg" to "Поздравляем! Авторизация успешно получена. Теперь вы можете привязать аккаунт в Настройки > Для разработчиков > Статус Mi Unlock.",
        "dialog_success_title" to "Успех!",
        "downloading_language_pack" to "Загрузка языкового пакета: %s...",
        "guide_step1_body" to "Установите браузер Firefox на свой телефон\\nУстановите расширение cookie-editor\\nПерейдите на c.mi.com/global\\nОткройте расширение cookie-editor и найдите new_bbs_serviceToken\\nСкопируйте значение и вставьте его в приложение",
        "guide_step1_title" to "1. Как получить new_bbs_serviceToken",
        "guide_step2_body" to "• Xiaomi аккаунт должен быть активен не менее 30 дней.\\n• Поддерживаются все прошивки HyperOS Global/EEA/ID/TW/RU (Китайская CNXM не поддерживается).\\n• Xiaomi ограничивает количество устройств (~1500 в день). Квота сбрасывается ровно в 00:00:00 по Пекину.\\n• Полученное разрешение действует 1 год.",
        "guide_step2_title" to "2. Требования и правила",
        "guide_step3_body" to "• После успешного получения разрешения в Xiaomi Unlock Tool подождите 1-2 минуты.\\n• Выключите Wi-Fi и включите Мобильный интернет (SIM-карта обязательна для привязки Xiaomi).\\n• Перейдите в Настройки > Расширенные настройки > Для разработчиков.\\n• Нажмите \\'Статус Mi Unlock\\' > затем \\'Связать аккаунт с устройством\\'.\\n• При успехе отобразится стандартный таймер ожидания разблокировки (обычно 72 или 168 часов).",
        "guide_step3_title" to "3. Привязка устройства в меню разработчика",
        "guide_step4_body" to "• \\\"Не удалось добавить. Перейдите в Mi Community\\\": Дневной лимит (1500) исчерпан. Попробуйте завтра ровно в 00:00:00 по Пекину с Авторежимом.\\n• \\\"Система обновляется. Попробуйте позже\\\": Известный временный сбой серверов (часто на Redmi Note 13).\\n• \\\"Код 100004 / Токен устарел\\\": Сессия входа завершилась. Получите свежий new_bbs_serviceToken.",
        "guide_step4_title" to "4. Частые ошибки и решения",
        "guide_title" to "Инструкция по HyperOS Unlock",
        "language_pack_downloaded" to "Языковой пакет успешно применён!",
        "language_pack_error" to "Не удалось скачать языковой пакет. Проверьте сеть.",
        "log_auto_mode_started" to "Авто-режим запущен. Ожидание полуночи по Пекину...",
        "log_clear" to "Очистить",
        "log_connecting_ntp" to "Подключение к NTP серверу: %s...",
        "log_copied" to "Лог скопирован в буфер обмена",
        "log_copy" to "Копировать",
        "log_empty" to "Здесь появятся логи выполнения...",
        "log_error_token_empty" to "Ошибка: Токен пуст. Сначала введите new_bbs_serviceToken.",
        "log_error_token_expired" to "ОШИБКА: Срок действия токена истёк. Обновите new_bbs_serviceToken.",
        "log_latency_measuring" to "Измерение задержки до Xiaomi API...",
        "log_latency_result" to "Задержка: HTTP: %d мс | TCP: %d мс (Средняя: %d мс)",
        "log_manual_sending" to "Ручной режим: Отправка запроса с deviceId: %s...",
        "log_ntp_auto_reached" to "23:59:00 по Пекину: Автоматическая синхронизация NTP...",
        "log_ntp_failed" to "Ошибка синхронизации NTP. Используются системные часы.",
        "log_ntp_success" to "NTP синхронизирован! Пекинское время: %s (Смещение: %d мс)",
        "log_ping_result_pc" to "Результат пинга: HTTP: %d мс | TCP: %d мс (Средний: %d мс)",
        "log_ping_wait_pc" to "23:59:40 по Пекину: Измерение задержки API (HTTP и TCP)...",
        "log_process_stopped" to "Процесс остановлен.",
        "log_response_code" to "[#%d] Ответ сервера: код: %d, сообщение: %s",
        "log_scheduling_requests" to "[Профиль %s] Запланировано %d запросов: %s",
        "log_sending_target" to "[#%d/%d цель 23:59:%s] Отправка с deviceId: %s...",
        "log_success_100003" to "УСПЕХ! Квота достигнута / Запрос поставлен в очередь (Код: 100003)! Проверьте привязку в меню разработчика!",
        "log_success_approved" to "УСПЕХ! Заявка одобрена (Код: %d, Результат: %s)! Теперь можно привязать устройство!",
        "log_success_code0" to "УСПЕХ: Запрос успешно обработан (Код 0). Попробуйте привязать аккаунт в меню разработчика.",
        "log_syncing_time" to "Синхронизация времени через NTP...",
        "log_title" to "Лог выполнения",
        "log_trigger_time" to "Расчётное время отправки: 23:59:%s",
        "login_authorized_extracting" to "Авторизация подтверждена! Извлечение токена...",
        "login_browser_opened" to "Страница входа открыта в браузере. Ожидание завершения...",
        "login_btn" to "Войти в аккаунт",
        "login_error" to "Ошибка авторизации: %s",
        "login_extracting_token" to "Извлечение токена...",
        "login_loading_qr" to "⏳ Загрузка QR-кода...",
        "login_open_browser_btn" to "🌐 Войти через браузер",
        "login_qr_expired" to "QR-код устарел. Нажмите «Обновить QR-код».",
        "login_qr_fetch_error" to "Ошибка получения QR-кода: %s",
        "login_qr_scan_tip" to "Отсканируйте QR-код в приложении Mi Community\\nили камерой телефона Xiaomi",
        "login_refresh_qr" to "🔄 Обновить QR-код",
        "login_refreshing_qr" to "Обновление QR-кода...",
        "login_session_expired" to "Сессия устарела",
        "login_subtitle" to "Автоматическое получение New_bbs_serviceToken",
        "login_success" to "Авторизация успешна! new_bbs_serviceToken получен.",
        "login_tab_qr" to "QR-код",
        "login_title" to "Авторизация Xiaomi Account",
        "login_token_extract_error" to "Не удалось извлечь токен из ответа сервера.",
        "login_waiting" to "Ожидание подтверждения авторизации...",
        "mode_auto" to "Авторежим",
        "mode_auto_desc" to "Отправляет скоростную серию запросов со случайными deviceId около 23:59:58 по Пекину",
        "mode_manual" to "Ручной режим",
        "mode_manual_desc" to "Отправить тестовый запрос или серию прямо сейчас",
        "modes_title" to "Режим работы",
        "nav_apply" to "Подача заявок",
        "nav_guide" to "Инструкция",
        "nav_settings" to "Настройки",
        "notif_channel_desc" to "Таймер и статус отправки заявки на разблокировку",
        "notif_channel_name" to "Статус подачи заявки",
        "notif_countdown" to "До отправки: %s",
        "notif_sending" to "Отправка",
        "notif_success" to "Успех!",
        "ping_measuring" to "Измерение пинга...",
        "ping_title" to "Пинг до API",
        "ping_unmeasured" to "Не измерен",
        "section_token" to "Токен Xiaomi Service",
        "send_offset_calc" to "Расчётное время: %s",
        "settings_about_text" to "Инструмент для автоматической отправки заявки на разблокировку загрузчика устройств Xiaomi на Global HyperOS.\\n\\nВерсия скрипта: 8.2",
        "settings_accent_color" to "Цвет оформления",
        "settings_apply_color" to "Применить",
        "settings_burst_count" to "Количество запросов в серии",
        "settings_burst_count_summary" to "%d запросов",
        "settings_burst_interval" to "Интервал серии",
        "settings_burst_interval_summary" to "%d мс",
        "settings_color_applied" to "Цвет оформления обновлён!",
        "settings_color_blue" to "Синий",
        "settings_color_custom" to "Свой цвет",
        "settings_color_cyan" to "Бирюзовый",
        "settings_color_green" to "Зелёный",
        "settings_color_hex_hint" to "HEX: #2196F3 или #09F",
        "settings_color_orange" to "Оранжевый",
        "settings_color_purple" to "Фиолетовый",
        "settings_color_red" to "Красный",
        "settings_custom_timings_hint" to "Введите тайминги через запятую (например, 58.700, 58.800)",
        "settings_invalid_hex" to "Неверный формат HEX (напр. #2196F3 или #09F)",
        "settings_lang_en" to "English",
        "settings_lang_es" to "Español",
        "settings_lang_id" to "Bahasa Indonesia",
        "settings_lang_pt" to "Português",
        "settings_lang_ru" to "Русский",
        "settings_lang_zh" to "简体中文",
        "settings_ntp_android" to "Android (time.android.com)",
        "settings_ntp_cloudflare" to "Cloudflare (time.cloudflare.com)",
        "settings_ntp_google" to "Google (time.google.com)",
        "settings_ntp_server" to "Сервер точного времени (NTP)",
        "settings_profile_asia" to "Азиатский (58.800, 59.100, 59.300, 59.500, 59.700)",
        "settings_profile_custom" to "Пользовательские тайминги",
        "settings_profile_europe" to "Европейский (58.700, 58.800, 59.100, 59.300, 59.500, 59.800)",
        "settings_profile_usa_africa" to "США / Африка (58.500, 58.800, 59.100, 59.300, 59.500, 59.700)",
        "settings_section_about" to "О программе и авторы",
        "settings_section_appearance" to "Внешний вид",
        "settings_section_language" to "Язык интерфейса",
        "settings_section_network" to "Сеть и синхронизация NTP",
        "settings_section_styling" to "Внешний вид и стиль",
        "settings_section_timing" to "Параметры серии запросов",
        "settings_section_timing_profile" to "Региональные профили таймингов",
        "settings_section_updates" to "Обновления",
        "settings_theme" to "Тема оформления",
        "settings_theme_dark" to "Тёмная",
        "settings_theme_light" to "Светлая (Белая)",
        "settings_theme_system" to "Как в системе",
        "settings_title" to "Настройки",
        "status_approved" to "Аккаунт уже авторизован до %s",
        "status_blocked" to "Аккаунт временно заблокирован до %s",
        "status_checking" to "Проверка статуса аккаунта...",
        "status_error" to "Ошибка проверки статуса: %s",
        "status_expired" to "Токен устарел или недействителен. Получите новый токен.",
        "status_not_checked" to "Ещё не проверено",
        "status_ready" to "Готов к подаче! Квота сбрасывается в 00:00:00",
        "status_title" to "Статус аккаунта",
        "status_too_new" to "Аккаунт слишком новый. Требуется регистрация от 30 дней.",
        "time_not_synced" to "Не синхронизировано",
        "time_syncing" to "Синхронизация NTP...",
        "toast_burst_started" to "Отправка серии запросов...",
        "toast_started" to "Процесс запущен. Ожидание полуночи по Пекину...",
        "toast_stopped" to "Подача заявок остановлена.",
        "toast_token_required" to "Сначала введите или вставьте ваш new_bbs_serviceToken!",
        "token_check_status" to "Проверить статус",
        "token_clear" to "Очистить",
        "token_hint" to "new_bbs_serviceToken",
        "token_paste" to "Вставить",
        "update_available_msg" to "Доступна новая версия (%1\$s)!\\nТекущая версия: %2\$s.\\n\\nСкачать и установить обновление?",
        "update_available_title" to "Доступно обновление",
        "update_cancel_btn" to "Отмена",
        "update_checking" to "Проверка наличия обновлений...",
        "update_download_btn" to "Скачать и установить",
        "update_download_error" to "Ошибка загрузки обновления: %s",
        "update_downloading" to "Загрузка обновления (%d%%)...",
        "update_error_msg" to "Не удалось связаться с сервером обновлений: %s",
        "update_error_title" to "Ошибка проверки обновлений",
        "update_installing" to "Запуск установщика APK...",
        "update_latest_msg" to "У вас установлена последняя версия (%s).",
        "update_latest_title" to "Актуальная версия",
        "fastboot_title" to "Fastboot (USB OTG)",
        "fastboot_status_no_device" to "USB-устройство не обнаружено",
        "fastboot_status_attached" to "Подключено: %s",
        "fastboot_status_permission_required" to "Требуется разрешение",
        "fastboot_status_permission_denied" to "В разрешении USB отказано",
        "fastboot_status_connected" to "Подключено: %s",
        "fastboot_status_disconnected" to "Отключено",
        "fastboot_btn_connect" to "Подключить",
        "fastboot_btn_disconnect" to "Отключить",
        "fastboot_btn_get_product" to "Получить Product",
        "fastboot_btn_get_token" to "Получить Token",
        "fastboot_product_label" to "Product: %s",
        "fastboot_token_label" to "Token: %s",
        "fastboot_info_hint" to "Подключите разблокируемый Xiaomi в режиме Fastboot через USB OTG кабель"
    )

    val BUILTIN_UK: Map<String, String> = mapOf(
        "app_name" to "Xiaomi Unlock Tool",
        "app_subtitle" to "v8.2",
        "authors_devs_body" to "• pktloss, New G3n\\n• Розробник PC та CLI версії: New G3n\\n• Розробник Сайту та Android версії: pktloss\\n• На основі скрипта: Vierta",
        "authors_devs_title" to "Розробники Скрипта",
        "authors_donate_crypto" to "USDT мережа TON:",
        "authors_donate_da" to "DonationAlerts: dalink.to/asinsideout",
        "authors_donate_title" to "Пожертвувати на розробку",
        "authors_link_4pda" to "Тема на 4PDA",
        "authors_link_github" to "GitHub: AsInsideOut/miunlocktool",
        "authors_link_tg" to "Telegram: @miunlocktoolrevamp",
        "authors_link_web" to "Сайт: miunlock.su",
        "authors_social_title" to "Посилання на соцмережі",
        "authors_title" to "Автори",
        "authors_wallet_address" to "UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG",
        "authors_wallet_copied" to "Адресу TON USDT скопійовано в буфер обміну!",
        "beijing_countdown_title" to "Зворотний відлік до 00:00:00",
        "beijing_time_title" to "Пекінський час (CST UTC+8)",
        "btn_check_update" to "Перевірити оновлення",
        "btn_measure_ping" to "Виміряти пінг",
        "btn_send_now" to "Надіслати запит зараз",
        "btn_start_auto" to "Почати подання заявки",
        "btn_stop_auto" to "Зупинити подання",
        "btn_sync_ntp" to "Синхр. NTP",
        "close_btn" to "Закрити",
        "copy_address_btn" to "Копіювати адресу",
        "dialog_error_title" to "Сповіщення",
        "dialog_ok" to "OK",
        "dialog_quota_msg" to "Усі заявки отримали код 0 (Успіх). Спробуйте прив'язати акаунт у налаштуваннях розробника.",
        "dialog_quota_title" to "Успіх!",
        "dialog_status_unavailable_msg" to "Заявку успішно надіслано, але статус тимчасово недоступний.\\n\\nБудь ласка, перевірте статус трохи пізніше за допомогою кнопки «Перевірити статус».",
        "dialog_status_unavailable_title" to "Заявку надіслано",
        "dialog_success_msg" to "Вітаємо! Авторизацію успішно отримано. Тепер ви можете прив'язати акаунт у Налаштування > Для розробників > Стан Mi Unlock.",
        "dialog_success_title" to "Успіх!",
        "downloading_language_pack" to "Завантаження мовного пакета: %s...",
        "fastboot_btn_connect" to "Підключити",
        "fastboot_btn_disconnect" to "Відключити",
        "fastboot_btn_get_product" to "Отримати Product",
        "fastboot_btn_get_token" to "Отримати Token",
        "fastboot_info_hint" to "Підключіть розблоковуваний Xiaomi в режимі Fastboot через кабель USB OTG",
        "fastboot_product_label" to "Product: %s",
        "fastboot_status_attached" to "Підключено: %s",
        "fastboot_status_connected" to "Підключено: %s",
        "fastboot_status_disconnected" to "Відключено",
        "fastboot_status_no_device" to "USB-пристрій не виявлено",
        "fastboot_status_permission_denied" to "У дозволі USB відмовлено",
        "fastboot_status_permission_required" to "Потрібен дозвіл",
        "fastboot_title" to "Fastboot (USB OTG)",
        "fastboot_token_label" to "Token: %s",
        "guide_step1_body" to "Встановіть браузер Firefox на свій телефон\\nВстановіть розширення cookie-editor\\nПерейдіть на c.mi.com/global\\nВідкрийте розширення cookie-editor та знайдіть new_bbs_serviceToken\\nСкопіюйте значення та вставте його у додаток",
        "guide_step1_title" to "1. Як отримати new_bbs_serviceToken",
        "guide_step2_body" to "• Xiaomi акаунт повинен бути активний не менше 30 днів.\\n• Підтримуються всі прошивки HyperOS Global/EEA/ID/TW/RU (Китайська CNXM не підтримується).\\n• Xiaomi обмежує кількість пристроїв (~1500 на день). Квота скидається рівно о 00:00:00 за Пекіном.\\n• Отриманий дозвіл діє 1 рік.",
        "guide_step2_title" to "2. Вимоги та правила",
        "guide_step3_body" to "• Після успішного отримання дозволу в Xiaomi Unlock Tool зачекайте 1-2 хвилини.\\n• Вимкніть Wi-Fi та увімкніть Мобільний інтернет (SIM-карта обов'язкова для прив'язки Xiaomi).\\n• Перейдіть у Налаштування > Додаткові налаштування > Для розробників.\\n• Натисніть \\'Стан Mi Unlock\\' > потім \\'Зв\\'язати акаунт із пристроєм\\'.\\n• У разі успіху відобразиться стандартний таймер очікування розблокування (зазвичай 72 або 168 годин).",
        "guide_step3_title" to "3. Прив'язка пристрою в меню розробника",
        "guide_step4_body" to "• \\\"Не вдалося додати. Перейдіть у Mi Community\\\": Денний ліміт (1500) вичерпано. Спробуйте завтра рівно о 00:00:00 за Пекіном в Авторежимі.\\n• \\\"Система оновлюється. Спробуйте пізніше\\\": Відомий тимчасовий збій серверів (часто на Redmi Note 13).\\n• \\\"Код 100004 / Токен застарів\\\": Сесія входу завершилася. Отримайте свіжий new_bbs_serviceToken.",
        "guide_step4_title" to "4. Часті помилки та рішення",
        "guide_title" to "Інструкція з HyperOS Unlock",
        "language_pack_downloaded" to "Мовний пакет успішно застосовано!",
        "language_pack_error" to "Не вдалося завантажити мовний пакет. Перевірте мережу.",
        "log_apply_send_failed" to "Не вдалося надіслати заявку: %s",
        "log_apply_send_failed_seq" to "[#%d] Не вдалося надіслати заявку: %s",
        "log_apply_sending" to "Надсилання заявки...",
        "log_apply_sending_seq" to "[#%d] Надсилання заявки...",
        "log_apply_sent_success" to "Заявку надіслано успішно",
        "log_apply_sent_success_seq" to "[#%d] Заявку надіслано успішно",
        "log_auth_failed" to "Помилка авторизації: %s",
        "log_auth_flow_started" to "Запуск процесу авторизації через Xiaomi Account...",
        "log_auth_qr_ready" to "QR-код згенеровано, очікування сканування...",
        "log_auth_success" to "Авторизація успішна! Токен збережено.",
        "log_auth_timeout" to "Час очікування авторизації вичерпано. Спробуйте ще раз.",
        "log_burst_all_failed" to "Усі %d запитів серії завершилися помилкою.",
        "log_burst_all_succeeded" to "Усі %d запитів серії надіслано успішно!",
        "log_burst_batch_start" to "Запуск серії із %d запитів...",
        "log_burst_completed_summary" to "Серія запитів завершена. Успішно надіслано: %d з %d",
        "log_burst_partial_summary" to "Серія частково завершена: успішно %d, помилок %d",
        "log_clear" to "Очистити",
        "log_copied" to "Лог скопійовано в буфер обміну",
        "log_copy" to "Копіювати",
        "log_device_fastboot_detected" to "Виявлено пристрій Fastboot: %s",
        "log_empty" to "Тут з'являться логи виконання...",
        "log_fastboot_reading_product" to "Зчитування кодового імені пристрою...",
        "log_fastboot_reading_token" to "Зчитування токена розблокування...",
        "log_fastboot_ready_to_unlock" to "Пристрій готовий до подання та розблокування.",
        "log_getting_status" to "Отримання статусу...",
        "log_getting_status_seq" to "[#%d] Отримання статусу...",
        "log_status_account_approved" to "Статус підтверджено: Акаунт авторизовано до %s",
        "log_status_unavailable" to "Не вдалося отримати статус: невірний формат відповіді",
        "log_status_unavailable_seq" to "[#%d] Статус тимчасово недоступний",
        "log_status_unavailable_summary" to "Заявку надіслано, але статус тимчасово недоступний. Перевірте пізніше через 'Перевірити статус'.",
        "log_title" to "Лог виконання",
        "log_token_cookie_detected" to "Виявлено формат cookie, вилучено значення new_bbs_serviceToken",
        "log_token_length_warning" to "Попередження: довжина токена незвичайна (%d символів)",
        "login_authorized_extracting" to "Авторизацію підтверджено! Вилучення токена...",
        "login_browser_opened" to "Сторінку входу відкрито в браузері. Очікування завершення...",
        "login_btn" to "Увійти в акаунт",
        "login_error" to "Помилка авторизації: %s",
        "login_extracting_token" to "Вилучення токена...",
        "login_loading_qr" to "⏳ Завантаження QR-коду...",
        "login_open_browser_btn" to "🌐 Увійти через браузер",
        "login_qr_expired" to "QR-код застарів. Натисніть «Оновити QR-код».",
        "login_qr_fetch_error" to "Помилка отримання QR-кода: %s",
        "login_qr_scan_tip" to "Відскануйте QR-код у додатку Mi Community\\nабо камерою телефона Xiaomi",
        "login_refresh_qr" to "🔄 Оновити QR-код",
        "login_refreshing_qr" to "Оновлення QR-коду...",
        "login_session_expired" to "Сесія застаріла",
        "login_subtitle" to "Автоматичне отримання New_bbs_serviceToken",
        "login_success" to "Авторизація успішна! new_bbs_serviceToken отримано.",
        "login_tab_qr" to "QR-код",
        "login_title" to "Авторизація Xiaomi Account",
        "login_token_extract_error" to "Не вдалося вилучити токен із відповіді сервера.",
        "login_waiting" to "Очікування підтвердження авторизації...",
        "mode_auto" to "Авторежим",
        "mode_auto_desc" to "Надсилає швидкісну серію запитів із випадковими deviceId близько 23:59:58 за Пекіном",
        "mode_manual" to "Ручний режим",
        "mode_manual_desc" to "Надіслати тестовий запит або серію прямо зараз",
        "modes_title" to "Режим роботи",
        "nav_apply" to "Подання заявок",
        "nav_guide" to "Інструкція",
        "nav_settings" to "Налаштування",
        "notif_channel_desc" to "Таймер і статус надсилання заявки на розблокування",
        "notif_channel_name" to "Статус подання заявки",
        "notif_countdown" to "До надсилання: %s",
        "notif_sending" to "Надсилання",
        "notif_success" to "Успіх!",
        "ping_measuring" to "Вимірювання пінгу...",
        "ping_title" to "Пінг до API",
        "ping_unmeasured" to "Не виміряно",
        "section_token" to "Токен Xiaomi Service",
        "send_offset_calc" to "Розрахунковий час: %s",
        "settings_about_text" to "Інструмент для автоматичного надсилання заявки на розблокування завантажувача пристроїв Xiaomi на Global HyperOS.\\n\\nВерсія скрипта: 8.2",
        "settings_accent_color" to "Колір оформлення",
        "settings_apply_color" to "Застосувати",
        "settings_burst_count" to "Кількість запитів у серії",
        "settings_burst_count_summary" to "%d запитів",
        "settings_burst_interval" to "Інтервал серії",
        "settings_burst_interval_summary" to "%d мс",
        "settings_color_applied" to "Колір оформлення оновлено!",
        "settings_color_blue" to "Синій",
        "settings_color_custom" to "Свій колір",
        "settings_color_cyan" to "Бірюзовий",
        "settings_color_green" to "Зелений",
        "settings_color_hex_hint" to "HEX: #2196F3 або #09F",
        "settings_color_orange" to "Помаранчевий",
        "settings_color_purple" to "Фіолетовий",
        "settings_color_red" to "Червоний",
        "settings_custom_timings_hint" to "Введіть таймінги через кому (наприклад, 58.700, 58.800)",
        "settings_invalid_hex" to "Невірний формат HEX (напр. #2196F3 або #09F)",
        "settings_lang_en" to "English",
        "settings_lang_es" to "Español",
        "settings_lang_id" to "Bahasa Indonesia",
        "settings_lang_pt" to "Português",
        "settings_lang_ru" to "Русский",
        "settings_lang_uk" to "Українська",
        "settings_lang_zh" to "简体中文",
        "settings_ntp_android" to "Android (time.android.com)",
        "settings_ntp_cloudflare" to "Cloudflare (time.cloudflare.com)",
        "settings_ntp_google" to "Google (time.google.com)",
        "settings_ntp_server" to "Сервер точного часу (NTP)",
        "settings_profile_asia" to "Азійський (58.800, 59.100, 59.300, 59.500, 59.700)",
        "settings_profile_custom" to "Користувацькі таймінги",
        "settings_profile_europe" to "Європейський (58.700, 58.800, 59.100, 59.300, 59.500, 59.800)",
        "settings_profile_usa_africa" to "США / Африка (58.500, 58.800, 59.100, 59.300, 59.500, 59.700)",
        "settings_section_about" to "Про програму та автори",
        "settings_section_appearance" to "Зовнішній вигляд",
        "settings_section_language" to "Мова інтерфейсу",
        "settings_section_network" to "Мережа та синхронізація NTP",
        "settings_section_styling" to "Зовнішній вигляд та стиль",
        "settings_section_timing" to "Параметри серії запитів",
        "settings_section_timing_profile" to "Регіональні профілі таймінгів",
        "settings_section_updates" to "Оновлення",
        "settings_theme" to "Тема оформлення",
        "settings_theme_dark" to "Темна",
        "settings_theme_light" to "Світла (Біла)",
        "settings_theme_system" to "Як у системі",
        "settings_title" to "Налаштування",
        "status_approved" to "Акаунт уже авторизовано до %s",
        "status_blocked" to "Акаунт тимчасово заблоковано до %s",
        "status_checking" to "Перевірка статусу акаунта...",
        "status_error" to "Помилка перевірки статусу: %s",
        "status_expired" to "Токен застарів або недійсний. Отримайте новий токен.",
        "status_not_checked" to "Ще не перевірено",
        "status_ready" to "Готовий до подання! Квота скидається о 00:00:00",
        "status_title" to "Статус акаунта",
        "status_too_new" to "Акаунт занадто новий. Потрібна реєстрація від 30 днів.",
        "status_unavailable_desc" to "Статус тимчасово недоступний",
        "time_not_synced" to "Не синхронізовано",
        "time_syncing" to "Синхронізація NTP...",
        "toast_burst_started" to "Надсилання серії запитів...",
        "toast_started" to "Процес запущено. Очікування півночі за Пекіном...",
        "toast_stopped" to "Подання заявок зупинено.",
        "toast_token_required" to "Спочатку введіть або вставте ваш new_bbs_serviceToken!",
        "token_check_status" to "Перевірити статус",
        "token_clear" to "Очистити",
        "token_hint" to "new_bbs_serviceToken",
        "token_paste" to "Вставити",
        "update_available_msg" to "Доступна нова версія (%1\$s)!\\nПоточна версія: %2\$s.\\n\\nЗавантажити та встановити оновлення?",
        "update_available_title" to "Доступне оновлення",
        "update_cancel_btn" to "Скасувати",
        "update_checking" to "Перевірка наявності оновлень...",
        "update_download_btn" to "Завантажити та встановити",
        "update_download_error" to "Помилка завантаження оновлення: %s",
        "update_downloading" to "Завантаження оновлення (%d%%)...",
        "update_error_msg" to "Не вдалося зв'язатися із сервером оновлень: %s",
        "update_error_title" to "Помилка перевірки оновлень",
        "update_installing" to "Запуск установника APK...",
        "update_latest_msg" to "У вас встановлена остання версія (%s).",
        "update_latest_title" to "Актуальна версія"
    )

    @Volatile
    var currentLanguage: String = PreferencesManager.LANG_EN
        private set

    @Volatile
    private var activeMap: Map<String, String> = BUILTIN_EN

    fun init(context: Context, langCode: String) {
        currentLanguage = langCode
        activeMap = when (langCode) {
            PreferencesManager.LANG_RU -> BUILTIN_RU
            PreferencesManager.LANG_UK -> BUILTIN_UK
            PreferencesManager.LANG_EN -> BUILTIN_EN
            else -> {
                val cached = loadCachedLanguage(context, langCode)
                cached ?: BUILTIN_EN
            }
        }
    }

    fun getLanguageDisplayName(code: String): String {
        return when (code) {
            PreferencesManager.LANG_EN -> "English"
            PreferencesManager.LANG_RU -> "Русский"
            PreferencesManager.LANG_UK -> "Українська"
            PreferencesManager.LANG_ES -> "Español"
            PreferencesManager.LANG_PT -> "Português"
            PreferencesManager.LANG_ID -> "Bahasa Indonesia"
            PreferencesManager.LANG_ZH -> "简体中文"
            else -> code
        }
    }

    private fun getCacheFile(context: Context, langCode: String): File {
        val dir = File(context.filesDir, "languages")
        if (!dir.exists()) dir.mkdirs()
        return File(dir, "strings-$langCode.json")
    }

    private fun loadCachedLanguage(context: Context, langCode: String): Map<String, String>? {
        val file = getCacheFile(context, langCode)
        if (!file.exists() || file.length() == 0L) return null
        return try {
            val jsonStr = file.readText(Charsets.UTF_8)
            parseJson(jsonStr)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load cached language $langCode", e)
            null
        }
    }

    private fun parseJson(jsonStr: String): Map<String, String> {
        val json = JSONObject(jsonStr)
        val map = mutableMapOf<String, String>()
        val keys = json.keys()
        while (keys.hasNext()) {
            val key = keys.next()
            map[key] = json.optString(key, "")
        }
        return map
    }

    suspend fun setLanguage(context: Context, langCode: String): Result<Unit> = withContext(Dispatchers.IO) {
        currentLanguage = langCode
        if (langCode == PreferencesManager.LANG_EN) {
            activeMap = BUILTIN_EN
            return@withContext Result.success(Unit)
        }
        if (langCode == PreferencesManager.LANG_RU) {
            activeMap = BUILTIN_RU
            return@withContext Result.success(Unit)
        }
        if (langCode == PreferencesManager.LANG_UK) {
            activeMap = BUILTIN_UK
            return@withContext Result.success(Unit)
        }

        // Check if cached
        val cached = loadCachedLanguage(context, langCode)
        if (cached != null && cached.isNotEmpty()) {
            activeMap = cached
            return@withContext Result.success(Unit)
        }

        // Download from server
        try {
            val urlStr = String.format(Locale.US, SERVER_BASE_URL, langCode)
            val url = URL(urlStr)
            val conn = url.openConnection() as HttpURLConnection
            conn.connectTimeout = 10000
            conn.readTimeout = 10000
            conn.requestMethod = "GET"
            conn.connect()

            val responseCode = conn.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val text = conn.inputStream.bufferedReader(Charsets.UTF_8).use { it.readText() }
                val map = parseJson(text)
                if (map.isNotEmpty()) {
                    val file = getCacheFile(context, langCode)
                    file.writeText(text, Charsets.UTF_8)
                    activeMap = map
                    return@withContext Result.success(Unit)
                }
            }
            return@withContext Result.failure(Exception("Server returned code " + responseCode))
        } catch (e: Exception) {
            Log.e(TAG, "Failed to download language pack for $langCode", e)
            return@withContext Result.failure(e)
        }
    }

    private fun unescape(text: String): String {
        return text
            .replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\t", "\t")
            .replace("\\'", "'")
            .replace("\\\"", "\"")
    }

    fun tr(key: String, vararg args: Any): String {
        val raw = activeMap[key] ?: BUILTIN_EN[key] ?: key
        val template = unescape(raw)
        return if (args.isEmpty()) {
            template
        } else {
            try {
                unescape(String.format(Locale.ROOT, template, *args))
            } catch (e: Exception) {
                template
            }
        }
    }

    fun trOrNull(key: String): String? {
        val raw = activeMap[key] ?: BUILTIN_EN[key] ?: return null
        return unescape(raw)
    }

    fun getString(context: Context, resId: Int, vararg args: Any): String {
        val entryName = try {
            context.resources.getResourceEntryName(resId)
        } catch (e: Exception) {
            null
        }
        return if (entryName != null) {
            tr(entryName, *args)
        } else {
            try {
                context.getString(resId, *args)
            } catch (e: Exception) {
                ""
            }
        }
    }
}
