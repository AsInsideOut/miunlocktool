# -*- coding: utf-8 -*-
"""
Helper module for rendering modernized Material 3 settings and instruction sections:
- About (О скрипте)
- General (Требования)
- Cookies (Получение токена)
- Trouble (Решение проблем)
"""

import sys
import webbrowser
import customtkinter as ctk

try:
    from theme import MaterialColors
except ImportError:
    try:
        from .theme import MaterialColors
    except ImportError:
        from res.theme import MaterialColors

FOURPDA_TOPIC_URL = "https://4pda.to/forum/index.php?showtopic=721838&view=findpost&p=145201115"
TELEGRAM_URL = "https://t.me/miunlocktoolrevamp"
GITHUB_URL = "https://github.com/AsInsideOut/miunlocktool"
SITE_URL = "https://miunlock.su/"
MI_COMMUNITY_URL = "https://c.mi.com/global"

# Темная цветовая палитра с высоким контрастом и читаемостью
CARD_BG = "#222228"          # Темно-серый фон карточек
CARD_BG_ELEVATED = "#2C2B34" # Приподнятый темно-серый фон
CARD_BORDER = "#3E3D48"      # Аккуратная рамка карточек
TEXT_HEADER = "#FFFFFF"      # Яркий белый цвет заголовков
TEXT_BODY = "#E2E8F0"        # Светло-серый контрастный цвет текста
COLOR_PRIMARY = "#D0BCFF"    # Акцентный цвет Material 3

def set_primary_color(color):
    global COLOR_PRIMARY
    COLOR_PRIMARY = color

def get_primary_color(custom_color=None):
    if custom_color:
        return custom_color
    global COLOR_PRIMARY
    for mod_name in ('__main__', 'theme', 'res.theme'):
        if mod_name in sys.modules:
            mod = sys.modules[mod_name]
            if hasattr(mod, 'MaterialColors'):
                try:
                    c = mod.MaterialColors.get_color('primary')
                    if c:
                        return c
                except Exception:
                    pass
    try:
        return MaterialColors.get_color('primary')
    except Exception:
        pass
    return COLOR_PRIMARY

COLOR_ERROR = "#F87171"      # Яркий мягкий красный цвет для проблем
COLOR_TIP_BG = "#1E293B"     # Темно-синий фон для подсказок
COLOR_TIP_BORDER = "#3B82F6" # Синяя рамка подсказок
COLOR_TIP_TEXT = "#93C5FD"   # Четкий текст подсказок

SECTIONS_DATA = {
    'ru': {
        'about': {
            'title': "О скрипте",
            'app_name': "Xiaomi Unlock Tool",
            'desc': "Инструмент для автоматической и ручной отправки заявки на официальную разблокировку загрузчика устройств Xiaomi на Global HyperOS.",
            'features_title': "Ключевые возможности:",
            'features': [
                ("⚡ Автоматическая подача", "Точная отправка заявки в 00:00:00 (Пекинское время / UTC+8) в первые миллисекунды открытия квот."),
                ("⏱ Синхронизация времени", "Высокоточная синхронизация с глобальными серверами NTP и автоматический расчёт сетевого пинга."),
                ("🔐 Быстрый вход", "Удобная авторизация через сканирование QR-кода или вход по сохранённой сессии на компьютере."),
                ("🌐 Поддержка всех регионов", "Работа со всеми официальными глобальными прошивками HyperOS 1, 2 и 3 (MI, EEA, RU, ID, TR, TW, IN).")
            ],
            'links_title': "Полезные ссылки:"
        },
        'general': {
            'title': "Требования",
            'subtitle': "Перед подачей заявки убедитесь, что ваш аккаунт и устройство соответствуют следующим обязательным требованиям Xiaomi:",
            'items': [
                ("1. Возраст Mi аккаунта", "Ваш Mi аккаунт должен быть создан и активен более 30 дней назад. На совсем новых аккаунтах подача заявки будет отклонена сервером."),
                ("2. Регион в Xiaomi Community", "В приложении или на сайте Xiaomi Community в настройках профиля должен быть обязательно выбран регион Global (Глобальный)."),
                ("3. Индекс прошивки устройства", "Разблокировка поддерживается для всех официальных глобальных индексов прошивок (MI, EU, RU, ID, TR, TW, IN и др.). Устройства с китайским индексом (CNXM) через Global Community не разблокируются."),
                ("4. Операционная система", "Устройство должно работать под управлением Xiaomi HyperOS (версии 1, 2 или 3).")
            ],
            'tip': "💡 После одобрения заявки в Community не забудьте связать аккаунт в меню телефона: Настройки -> Для разработчиков -> Статус Mi Unlock (только через мобильный интернет)."
        },
        'cookies': {
            'title': "Получение токена",
            'subtitle': "Пошаговая инструкция по извлечению New_bbs_ServiceToken через браузер для подачи заявки:",
            'quick_tip': "💡 Рекомендация: вы можете использовать вход по QR-коду на вкладке «Подача заявок» — в этом случае копировать токен вручную не требуется!",
            'steps': [
                ("Шаг 1: Установка расширения", "Установите расширение Cookie Editor (для Chrome, Edge, Firefox или Opera) из официального интернет-магазина расширений браузера.", None, None),
                ("Шаг 2: Вход в Mi Community", "Перейдите на сайт c.mi.com/global. Если вы уже были авторизованы, обязательно выйдите и войдите в аккаунт заново для генерации свежего токена.", MI_COMMUNITY_URL, "🌐 Открыть c.mi.com/global"),
                ("Шаг 3: Копирование токена", "Откройте окно расширения Cookie Editor на вкладке c.mi.com/global. Найдите в списке параметр New_bbs_ServiceToken, скопируйте его значение и вставьте в программу.", None, None)
            ],
            'notes': [
                "• Время отправки: все тайминги в скрипте синхронизируются по Пекинскому времени (UTC+8).",
                "• Регион профиля: обязательно проверьте, что в профиле Mi Community стоит регион Global."
            ]
        },
        'trouble': {
            'title': "Решение проблем",
            'subtitle': "Частые проблемы при работе со скриптом и рекомендации по их устранению:",
            'items': [
                ("⚠️ Cookie Editor не находит New_bbs_ServiceToken", "Решение: Выйдите из аккаунта на сайте c.mi.com/global и войдите снова. Обновите страницу через Ctrl+F5. Также вы можете использовать вход по QR-коду."),
                ("⚠️ Ошибка: Токен просрочен или не работает", "Решение: Срок действия токена ограничен. Получите новый токен за 5-10 минут до полуночи по Пекину. Проверьте, что регион в Mi Community установлен в Global."),
                ("⚠️ Ошибка: Лимит заявок исчерпан (Quota limit)", "Решение: Дневная квота одобрений на серверах Xiaomi исчерпана. Квоты обновляются ровно в 00:00:00 по Пекину. Используйте автоматический режим отправки."),
                ("⚠️ Ошибки 10001, сбои сети или отсутствие ответа", "Решение: Проверьте стабильность интернет-соединения, отключите VPN/прокси и убедитесь, что системное время на ПК синхронизировано.")
            ],
            'support_title': "💬 Нужна помощь?",
            'support_desc': "Задайте вопрос в нашем Telegram-чате поддержки:",
            'chat_btn': "Telegram Чат"
        }
    },
    'en': {
        'about': {
            'title': "About",
            'app_name': "Xiaomi Unlock Tool",
            'desc': "Tool for automatic and manual application submission for official bootloader unlocking on Xiaomi Global HyperOS devices.",
            'features_title': "Key Features:",
            'features': [
                ("⚡ Automatic Submission", "Precise request submission at 00:00:00 (Beijing Time / UTC+8) in the first milliseconds of quota opening."),
                ("⏱ Time Synchronization", "High-precision sync with global NTP servers and automatic network ping calculation."),
                ("🔐 Quick Login", "Convenient login via QR code scanning or saved PC browser session."),
                ("🌐 Multi-Region Support", "Works with all official global HyperOS 1, 2, and 3 ROMs (MI, EEA, RU, ID, TR, TW, IN).")
            ],
            'links_title': "Useful Links:"
        },
        'general': {
            'title': "Requirements",
            'subtitle': "Before submitting, ensure your account and device meet the following mandatory Xiaomi requirements:",
            'items': [
                ("1. Mi Account Age", "Your Mi account must have been registered for at least 30 days. Brand new accounts are rejected by Xiaomi servers."),
                ("2. Community Region", "Your Xiaomi Community profile region must be set to Global in the app or website settings."),
                ("3. ROM Region Index", "Unlocking is supported for all official global ROM versions (MI, EU, RU, ID, TR, TW, IN, etc.). Pure Chinese devices (CNXM) are not supported via Global Community."),
                ("4. Operating System", "Device must be running Xiaomi HyperOS (version 1, 2, or 3).")
            ],
            'tip': "💡 Once approved, remember to bind your device in Settings -> Developer options -> Mi Unlock status (using mobile data only)."
        },
        'cookies': {
            'title': "Getting Token",
            'subtitle': "Step-by-step instructions for extracting New_bbs_ServiceToken via browser:",
            'quick_tip': "💡 Tip: You can also log in via QR code on the 'Application Submission' tab without copying tokens manually!",
            'steps': [
                ("Step 1: Install Extension", "Install the Cookie Editor extension (for Chrome, Edge, Firefox, Opera) from your browser extension store.", None, None),
                ("Step 2: Log in to Mi Community", "Visit c.mi.com/global. If already logged in, log out and log in again to ensure a fresh session token is issued.", MI_COMMUNITY_URL, "🌐 Open c.mi.com/global"),
                ("Step 3: Copy Token", "Open Cookie Editor while on c.mi.com/global, locate the New_bbs_ServiceToken cookie, copy its value and paste it into the application.", None, None)
            ],
            'notes': [
                "• Timing: All server times in the script synchronize to Beijing Time (UTC+8).",
                "• Region: Double check that your Mi Community profile region is set to Global."
            ]
        },
        'trouble': {
            'title': "Troubleshooting",
            'subtitle': "Common issues when submitting applications and their solutions:",
            'items': [
                ("⚠️ Cookie Editor does not show New_bbs_ServiceToken", "Solution: Log out from c.mi.com/global and log back in. Hard refresh the page (Ctrl+F5) or use the QR code login feature instead."),
                ("⚠️ Error: Token expired or invalid", "Solution: Tokens have a limited lifetime. Extract a fresh token 5-10 minutes before Beijing midnight. Ensure your profile region is set to Global."),
                ("⚠️ Error: Quota limit reached", "Solution: The daily unlocking quota on Xiaomi servers has been exhausted. Quotas reset at 00:00:00 Beijing Time. Use automatic mode for precise submission."),
                ("⚠️ Error 10001, network timeout, or no response", "Solution: Check your internet connection, disable any third-party VPN/proxy, and ensure your PC system clock is accurate.")
            ],
            'support_title': "💬 Need help?",
            'support_desc': "Ask a question in our Telegram support chat:",
            'chat_btn': "Telegram Chat"
        }
    },
    'id': {
        'about': {
            'title': "Tentang Skrip",
            'app_name': "Xiaomi Unlock Tool",
            'desc': "Alat untuk pengiriman pengajuan otomatis dan manual untuk membuka bootloader resmi pada perangkat Xiaomi Global HyperOS.",
            'features_title': "Fitur Utama:",
            'features': [
                ("⚡ Pengiriman Otomatis", "Pengiriman permintaan tepat pada 00:00:00 (Waktu Beijing / UTC+8) di milidetik pertama kuota dibuka."),
                ("⏱ Sinkronisasi Waktu", "Sinkronisasi presisi tinggi dengan server NTP global dan perhitungan ping jaringan."),
                ("🔐 Masuk Cepat", "Otorisasi nyaman melalui pemindaian kode QR atau sesi browser yang tersimpan."),
                ("🌐 Dukungan Multi-Wilayah", "Bekerja dengan semua ROM HyperOS global resmi 1, 2, dan 3 (MI, EEA, RU, ID, TR, TW, IN).")
            ],
            'links_title': "Tautan Berguna:"
        },
        'general': {
            'title': "Persyaratan",
            'subtitle': "Sebelum mengajukan, pastikan akun dan perangkat Anda memenuhi persyaratan wajib Xiaomi berikut:",
            'items': [
                ("1. Umur Akun Mi", "Akun Mi Anda harus terdaftar setidaknya selama 30 hari. Akun baru akan ditolak oleh server."),
                ("2. Wilayah Xiaomi Community", "Wilayah di profil Xiaomi Community harus diatur ke Global."),
                ("3. Indeks ROM", "Mendukung semua ROM global resmi (MI, EU, RU, ID, TR, TW, IN, dll.). ROM versi Tiongkok (CNXM) tidak didukung."),
                ("4. Sistem Operasi", "Perangkat harus menjalankan Xiaomi HyperOS (versi 1, 2, atau 3).")
            ],
            'tip': "💡 Setelah disetujui, ikat akun di Pengaturan -> Opsi pengembang -> Status Mi Unlock (menggunakan data seluler)."
        },
        'cookies': {
            'title': "Mendapatkan Token",
            'subtitle': "Panduan langkah demi langkah mengekstrak New_bbs_ServiceToken melalui browser:",
            'quick_tip': "💡 Tips: Anda juga dapat menggunakan masuk kode QR di tab pengajuan tanpa menyalin token manual!",
            'steps': [
                ("Langkah 1: Pasang Ekstensi", "Pasang ekstensi Cookie Editor (untuk Chrome, Edge, Firefox, Opera) dari toko ekstensi browser Anda.", None, None),
                ("Langkah 2: Masuk ke Mi Community", "Buka situs c.mi.com/global. Jika sudah masuk, keluar dan masuk kembali agar token baru dibuat.", MI_COMMUNITY_URL, "🌐 Buka c.mi.com/global"),
                ("Langkah 3: Salin Token", "Buka Cookie Editor di c.mi.com/global, cari cookie New_bbs_ServiceToken, salin nilainya dan tempelkan ke aplikasi.", None, None)
            ],
            'notes': [
                "• Waktu server: Semua perhitungan waktu disinkronkan ke Waktu Beijing (UTC+8).",
                "• Wilayah: Pastikan wilayah profil Mi Community Anda diatur ke Global."
            ]
        },
        'trouble': {
            'title': "Penyelesaian Masalah",
            'subtitle': "Masalah umum dan cara mengatasinya:",
            'items': [
                ("⚠️ Cookie Editor tidak menemukan New_bbs_ServiceToken", "Solusi: Keluar dari c.mi.com/global dan masuk kembali. Muat ulang halaman (Ctrl+F5) atau gunakan masuk QR code."),
                ("⚠️ Kesalahan: Token kedaluwarsa atau tidak valid", "Solusi: Masa berlaku token terbatas. Ambil token baru 5-10 menit sebelum tengah malam Beijing. Pastikan wilayah adalah Global."),
                ("⚠️ Kesalahan: Kuota harian habis", "Solusi: Kuota harian server Xiaomi telah habis. Kuota diperbarui pukul 00:00:00 Waktu Beijing. Gunakan mode otomatis."),
                ("⚠️ Kesalahan 10001 atau jaringan bermasalah", "Solusi: Periksa koneksi internet Anda, nonaktifkan VPN/proksi, dan pastikan jam sistem akurat.")
            ],
            'support_title': "💬 Butuh bantuan?",
            'support_desc': "Ajukan pertanyaan di obrolan Telegram kami:",
            'chat_btn': "Obrolan Telegram"
        }
    },
    'es': {
        'about': {
            'title': "Acerca del Script",
            'app_name': "Xiaomi Unlock Tool",
            'desc': "Herramienta para el envío automático y manual de solicitudes de desbloqueo oficial del bootloader en dispositivos Xiaomi con Global HyperOS.",
            'features_title': "Características principales:",
            'features': [
                ("⚡ Envío automático", "Envío preciso a las 00:00:00 (Hora de Pekín / UTC+8) en los primeros milisegundos de apertura de cupos."),
                ("⏱ Sincronización horaria", "Sincronización de alta precisión con servidores NTP globales y cálculo de ping."),
                ("🔐 Inicio de sesión rápido", "Autorización cómoda escaneando código QR o mediante sesión guardada en PC."),
                ("🌐 Soporte multirregión", "Compatible con todas las ROMs globales oficiales de HyperOS 1, 2 y 3 (MI, EEA, RU, ID, TR, TW, IN).")
            ],
            'links_title': "Enlaces útiles:"
        },
        'general': {
            'title': "Requisitos",
            'subtitle': "Antes de enviar, asegúrese de que su cuenta y dispositivo cumplan con los siguientes requisitos obligatorios de Xiaomi:",
            'items': [
                ("1. Antigüedad de la cuenta Mi", "Su cuenta Mi debe tener más de 30 días de antigüedad. Cuentas recién creadas serán rechazadas."),
                ("2. Región en Xiaomi Community", "La región en su perfil de Xiaomi Community debe estar configurada en Global."),
                ("3. Índice de la ROM", "Compatible con todas las ROMs globales oficiales (MI, EU, RU, ID, TR, TW, IN, etc.). Dispositivos chinos (CNXM) no son compatibles."),
                ("4. Sistema operativo", "El dispositivo debe ejecutar Xiaomi HyperOS (versión 1, 2 o 3).")
            ],
            'tip': "💡 Tras la aprobación, recuerde vincular su teléfono en Ajustes -> Opciones de desarrollador -> Estado de Mi Unlock (usando datos móviles)."
        },
        'cookies': {
            'title': "Obtención del Token",
            'subtitle': "Guía paso a paso para extraer el New_bbs_ServiceToken a través del navegador:",
            'quick_tip': "💡 Consejo: ¡También puede iniciar sesión con código QR en la pestaña principal sin necesidad de copiar tokens manualmente!",
            'steps': [
                ("Paso 1: Instalar extensión", "Instale la extensión Cookie Editor (para Chrome, Edge, Firefox, Opera) desde la tienda de su navegador.", None, None),
                ("Paso 2: Iniciar sesión en Mi Community", "Acceda a c.mi.com/global. Si ya inició sesión, ciérrela e inicie nuevamente para generar un token limpio.", MI_COMMUNITY_URL, "🌐 Abrir c.mi.com/global"),
                ("Paso 3: Copiar el token", "Abra Cookie Editor en c.mi.com/global, busque la cookie New_bbs_ServiceToken, copie su valor y péguelo en la herramienta.", None, None)
            ],
            'notes': [
                "• Horario del servidor: Todas las horas en el script están sincronizadas con la hora de Pekín (UTC+8).",
                "• Región: Asegúrese de que la región de su perfil de Mi Community sea Global."
            ]
        },
        'trouble': {
            'title': "Solución de Problemas",
            'subtitle': "Problemas frecuentes y cómo resolverlos:",
            'items': [
                ("⚠️ Cookie Editor no muestra New_bbs_ServiceToken", "Solución: Cierre sesión en c.mi.com/global e inicie sesión nuevamente. Recargue con Ctrl+F5 o use el inicio con código QR."),
                ("⚠️ Error: Token expirado o inválido", "Solución: El token tiene una vida útil limitada. Obtenga uno nuevo 5-10 minutos antes de la medianoche de Pekín. Compruebe que su región sea Global."),
                ("⚠️ Error: Cuota diaria agotada", "Solución: El límite diario de solicitudes en Xiaomi se ha agotado. Se reinicia a las 00:00:00 hora de Pekín. Utilice el modo automático."),
                ("⚠️ Errores 10001 o fallo de red", "Solución: Verifique su conexión a Internet, desactive VPNs/proxies y asegúrese de que la hora del sistema sea precisa.")
            ],
            'support_title': "💬 ¿Necesitas ayuda?",
            'support_desc': "Haz una pregunta en nuestro chat de soporte de Telegram:",
            'chat_btn': "Chat de Telegram"
        }
    },
    'zh': {
        'about': {
            'title': "关于脚本",
            'app_name': "Xiaomi Unlock Tool",
            'desc': "用于在小米Global HyperOS设备上自动或手动提交官方Bootloader解锁申请的工具。",
            'features_title': "核心功能：",
            'features': [
                ("⚡ 自动精准提交", "在北京时间 00:00:00（UTC+8）开放额度的第一毫秒精准发送申请请求。"),
                ("⏱ 高精度时间同步", "与全球NTP服务器高精度同步，并自动计算网络延迟（Ping）。"),
                ("🔐 快捷扫码登录", "支持通过扫描二维码或PC浏览器已保存的会话快速登录小米账号。"),
                ("🌐 全球区域支持", "全面支持所有官方Global HyperOS 1、2、3固件（MI、EEA、RU、ID、TR、TW、IN等）。")
            ],
            'links_title': "常用链接："
        },
        'general': {
            'title': "申请条件",
            'subtitle': "在提交申请之前，请确保您的账号与设备满足小米官方的以下硬性条件：",
            'items': [
                ("1. 小米账号注册时间", "小米账号必须注册满 30 天以上。新注册的账号提交申请会被服务器直接拒绝。"),
                ("2. 小米社区区域设置", "小米社区（Xiaomi Community）个人资料中的区域必须设置为 Global（全球）。"),
                ("3. 设备固件版本（ROM）", "支持所有官方全球版本固件（包含 MI、EU、RU、ID、TR、TW、IN 等）。纯国行固件（CNXM）不支持通过全球社区解锁。"),
                ("4. 操作系统版本", "设备必须运行小米 HyperOS（澎湃OS 1、2 或 3）。")
            ],
            'tip': "💡 社区申请通过后，请前往手机设置 -> 开发者选项 -> 设备解锁状态（必须使用移动数据网络）进行账号绑定。"
        },
        'cookies': {
            'title': "获取令牌（Token）",
            'subtitle': "通过浏览器提取 New_bbs_ServiceToken 的详细步骤说明：",
            'quick_tip': "💡 提示：您也可以在“申请解锁”主界面直接使用二维码扫码登录，无需手动复制Cookie！",
            'steps': [
                ("第一步：安装浏览器扩展", "在您的浏览器（Chrome、Edge、Firefox 或 Opera）应用商店中安装 Cookie Editor 扩展。", None, None),
                ("第二步：登录小米全球社区", "访问 c.mi.com/global。若已经处于登录状态，请先退出账号然后重新登录，以生成全新的有效会话。", MI_COMMUNITY_URL, "🌐 打开 c.mi.com/global"),
                ("第三步：复制服务令牌", "在 c.mi.com/global 页面打开 Cookie Editor，找到名为 New_bbs_ServiceToken 的条目，复制其值并粘贴至软件中。", None, None)
            ],
            'notes': [
                "• 服务器时间：软件内所有请求与时间调度均精准对齐北京时间（UTC+8）。",
                "• 社区区域：请确认您的账号社区区域已设置为 Global。"
            ]
        },
        'trouble': {
            'title': "问题排查与解决",
            'subtitle': "常见问题及推荐解决方案：",
            'items': [
                ("⚠️ Cookie Editor 未找到 New_bbs_ServiceToken", "解决方案：在 c.mi.com/global 网站退出账号并重新登录。按 Ctrl+F5 强制刷新页面，或直接使用软件主界面的二维码扫码登录。"),
                ("⚠️ 提示：Cookie 已过期或无效", "解决方案：登录会话具有时效性。建议在临近北京时间午夜前 5-10 分钟重新获取最新Token，并确认社区区域为 Global。"),
                ("⚠️ 提示：申请额度已耗尽（Quota Limit）", "解决方案：小米服务器每日发放的解锁配额已满。配额在北京时间每天 00:00:00 重置，请开启自动模式精准抢申。"),
                ("⚠️ 错误码 10001、网络异常或无响应", "解决方案：检查网络连接稳定性，关闭可能干扰小米请求的代理/VPN软件，并确保电脑系统时间准确。")
            ],
            'support_title': "💬 需要帮助吗？",
            'support_desc': "在我们的 Telegram 群组中提问交流：",
            'chat_btn': "Telegram 群聊"
        }
    },
    'pt': {
        'about': {
            'title': "Sobre o Script",
            'app_name': "Xiaomi Unlock Tool",
            'desc': "Ferramenta para envio automático e manual de solicitações de desbloqueio oficial do bootloader em dispositivos Xiaomi com Global HyperOS.",
            'features_title': "Recursos Principais:",
            'features': [
                ("⚡ Envio Automático", "Envio preciso às 00:00:00 (Horário de Pequim / UTC+8) nos primeiros milissegundos da abertura das cotas."),
                ("⏱ Sincronização de Horário", "Sincronização de alta precisão com servidores NTP globais e cálculo automático de ping."),
                ("🔐 Login Rápido", "Autorização conveniente por código QR ou sessão salva do navegador no PC."),
                ("🌐 Suporte Multi-Região", "Compatível com todas as ROMs globais oficiais do HyperOS 1, 2 e 3 (MI, EEA, RU, ID, TR, TW, IN).")
            ],
            'links_title': "Links Úteis:"
        },
        'general': {
            'title': "Requisitos",
            'subtitle': "Antes de enviar a solicitação, certifique-se de que sua conta e dispositivo atendam aos seguintes requisitos obrigatórios:",
            'items': [
                ("1. Idade da Conta Mi", "Sua conta Mi deve ter sido criada há pelo menos 30 dias. Contas recém-criadas são rejeitadas pelos servidores."),
                ("2. Região na Xiaomi Community", "A região no seu perfil da Xiaomi Community deve estar definida como Global."),
                ("3. Índice da ROM", "Suporta todas as versões de ROMs globais oficiais (MI, EU, RU, ID, TR, TW, IN, etc.). Versões chinesas (CNXM) não são suportadas."),
                ("4. Sistema Operacional", "O dispositivo deve estar rodando o Xiaomi HyperOS (versão 1, 2 ou 3).")
            ],
            'tip': "💡 Após a aprovação, vincule seu aparelho em Configurações -> Opções do desenvolvedor -> Status do Mi Unlock (usando apenas dados móveis)."
        },
        'cookies': {
            'title': "Obtendo o Token",
            'subtitle': "Instruções passo a passo para extrair o New_bbs_ServiceToken pelo navegador:",
            'quick_tip': "💡 Dica: Você também pode fazer login via QR code na aba principal sem precisar copiar tokens manualmente!",
            'steps': [
                ("Passo 1: Instalar Extensão", "Instale a extensão Cookie Editor (para Chrome, Edge, Firefox, Opera) na loja de extensões do seu navegador.", None, None),
                ("Passo 2: Entrar na Mi Community", "Acesse c.mi.com/global. Se já estiver conectado, saia e faça login novamente para gerar um token atualizado.", MI_COMMUNITY_URL, "🌐 Abrir c.mi.com/global"),
                ("Passo 3: Copiar Token", "Abra o Cookie Editor em c.mi.com/global, localize o cookie New_bbs_ServiceToken, copie o valor e cole no programa.", None, None)
            ],
            'notes': [
                "• Horário do servidor: Todos os cálculos de horário são sincronizados com o horário de Pequim (UTC+8).",
                "• Região: Certifique-se de que a região da sua conta Mi Community esteja definida como Global."
            ]
        },
        'trouble': {
            'title': "Solução de Problemas",
            'subtitle': "Problemas frequentes e soluções recomendadas:",
            'items': [
                ("⚠️ Cookie Editor não encontra o New_bbs_ServiceToken", "Solução: Saia de c.mi.com/global e entre novamente. Atualize a página com Ctrl+F5 ou use o login por código QR."),
                ("⚠️ Erro: Token expirado ou inválido", "Solução: O token possui validade limitada. Obtenha um novo 5-10 minutos antes da meia-noite de Pequim. Verifique se a região é Global."),
                ("⚠️ Erro: Limite diário de solicitações atingido", "Solução: A cota diária nos servidores Xiaomi acabou. Ela é renovada às 00:00:00 (horário de Pequim). Use o modo automático."),
                ("⚠️ Erros 10001 ou falhas de rede", "Solução: Verifique sua conexão com a internet, desligue VPN/proxy e confira a sincronização do relógio do sistema.")
            ],
            'support_title': "💬 Precisa de ajuda?",
            'support_desc': "Tire suas dúvidas em nosso chat de suporte no Telegram:",
            'chat_btn': "Chat do Telegram"
        }
    }
}


def get_section_data(lang, section):
    lang_dict = SECTIONS_DATA.get(lang, SECTIONS_DATA['en'])
    return lang_dict.get(section, SECTIONS_DATA['en'].get(section, {}))


def get_site_btn_text(lang):
    if lang == 'ru':
        return "Сайт"
    elif lang in ('en', 'pt'):
        return "Website"
    elif lang == 'id':
        return "Situs Web"
    elif lang == 'es':
        return "Sitio Web"
    elif lang == 'zh':
        return "网站"
    return "Website"


def build_about_section(scroll, lang, open_tg_cmd=None, open_4pda_cmd=None, open_gh_cmd=None, open_site_cmd=None, site_btn_text=None, version="8.1", primary_color=None):
    color_primary = get_primary_color(primary_color)
    if open_tg_cmd is None:
        open_tg_cmd = lambda: webbrowser.open(TELEGRAM_URL, new=2)
    if open_4pda_cmd is None:
        open_4pda_cmd = lambda: webbrowser.open(FOURPDA_TOPIC_URL, new=2)
    if open_gh_cmd is None:
        open_gh_cmd = lambda: webbrowser.open(GITHUB_URL, new=2)
    if open_site_cmd is None:
        open_site_cmd = lambda: webbrowser.open(SITE_URL, new=2)
    if site_btn_text is None:
        site_btn_text = get_site_btn_text(lang)

    data = get_section_data(lang, 'about')

    # Заголовок
    title = ctk.CTkLabel(
        scroll,
        text=data.get('title', 'About'),
        font=("Arial", 22, "bold"),
        text_color=TEXT_HEADER
    )
    title.pack(anchor="w", padx=10, pady=(8, 4))

    # Карточка приложения
    app_card = ctk.CTkFrame(
        scroll,
        fg_color=CARD_BG,
        corner_radius=12,
        border_width=1,
        border_color=CARD_BORDER
    )
    app_card.pack(fill="x", padx=10, pady=(4, 12))

    top_row = ctk.CTkFrame(app_card, fg_color="transparent")
    top_row.pack(fill="x", padx=14, pady=(12, 6))

    ctk.CTkLabel(
        top_row,
        text=data.get('app_name', 'Xiaomi Unlock Tool'),
        font=("Arial", 18, "bold"),
        text_color=TEXT_HEADER
    ).pack(side="left")

    v_badge = ctk.CTkFrame(top_row, fg_color=CARD_BG_ELEVATED, corner_radius=8)
    v_badge.pack(side="left", padx=(10, 0))
    ctk.CTkLabel(
        v_badge,
        text=f"v{version}",
        font=("Arial", 11, "bold"),
        text_color=color_primary
    ).pack(padx=8, pady=2)

    ctk.CTkLabel(
        app_card,
        text=data.get('desc', ''),
        font=("Arial", 13),
        text_color=TEXT_BODY,
        justify="left",
        wraplength=520
    ).pack(anchor="w", padx=14, pady=(0, 12))

    # Ключевые возможности
    features_card = ctk.CTkFrame(
        scroll,
        fg_color=CARD_BG,
        corner_radius=12,
        border_width=1,
        border_color=CARD_BORDER
    )
    features_card.pack(fill="x", padx=10, pady=(0, 12))

    ctk.CTkLabel(
        features_card,
        text=data.get('features_title', 'Key Features:'),
        font=("Arial", 15, "bold"),
        text_color=TEXT_HEADER
    ).pack(anchor="w", padx=14, pady=(12, 6))

    for feat_title, feat_desc in data.get('features', []):
        f_row = ctk.CTkFrame(features_card, fg_color="transparent")
        f_row.pack(fill="x", padx=14, pady=3)

        ctk.CTkLabel(
            f_row,
            text=feat_title,
            font=("Arial", 13, "bold"),
            text_color=color_primary
        ).pack(anchor="w")

        ctk.CTkLabel(
            f_row,
            text=feat_desc,
            font=("Arial", 12),
            text_color=TEXT_BODY,
            justify="left",
            wraplength=500
        ).pack(anchor="w", padx=(14, 0), pady=(1, 2))

    f_pad = ctk.CTkFrame(features_card, fg_color="transparent", height=6)
    f_pad.pack()

    # Ссылки
    ctk.CTkLabel(
        scroll,
        text=data.get('links_title', 'Useful Links:'),
        font=("Arial", 16, "bold"),
        text_color=TEXT_HEADER
    ).pack(anchor="w", padx=10, pady=(4, 8))

    links_row = ctk.CTkFrame(scroll, fg_color="transparent")
    links_row.pack(anchor="w", padx=10, pady=(0, 16))

    ctk.CTkButton(
        links_row,
        text="Telegram",
        width=100,
        height=32,
        corner_radius=10,
        font=("Arial", 12, "bold"),
        fg_color="#5B8DEF",
        hover_color="#4A7AE6",
        text_color="#FFFFFF",
        border_width=0,
        command=open_tg_cmd
    ).pack(side="left", padx=(0, 8))

    ctk.CTkButton(
        links_row,
        text="4PDA",
        width=88,
        height=32,
        corner_radius=10,
        font=("Arial", 12, "bold"),
        fg_color="#607D9B",
        hover_color="#506B85",
        text_color="#FFFFFF",
        border_width=0,
        command=open_4pda_cmd
    ).pack(side="left", padx=(0, 8))

    ctk.CTkButton(
        links_row,
        text="GitHub",
        width=96,
        height=32,
        corner_radius=10,
        font=("Arial", 12, "bold"),
        fg_color="#374151",
        hover_color="#4B5563",
        text_color="#FFFFFF",
        border_width=0,
        command=open_gh_cmd
    ).pack(side="left", padx=(0, 8))

    ctk.CTkButton(
        links_row,
        text=site_btn_text,
        width=118,
        height=32,
        corner_radius=10,
        font=("Arial", 12, "bold"),
        fg_color=CARD_BG_ELEVATED,
        hover_color="#3E3D48",
        text_color=TEXT_HEADER,
        border_width=1,
        border_color=CARD_BORDER,
        command=open_site_cmd
    ).pack(side="left")


def build_general_section(scroll, lang, primary_color=None):
    color_primary = get_primary_color(primary_color)
    data = get_section_data(lang, 'general')

    # Заголовок
    ctk.CTkLabel(
        scroll,
        text=data.get('title', 'Requirements'),
        font=("Arial", 22, "bold"),
        text_color=TEXT_HEADER
    ).pack(anchor="w", padx=10, pady=(8, 4))

    ctk.CTkLabel(
        scroll,
        text=data.get('subtitle', ''),
        font=("Arial", 13),
        text_color=TEXT_BODY,
        justify="left",
        wraplength=520
    ).pack(anchor="w", padx=10, pady=(0, 12))

    for item_title, item_desc in data.get('items', []):
        card = ctk.CTkFrame(
            scroll,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER
        )
        card.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            card,
            text=item_title,
            font=("Arial", 14, "bold"),
            text_color=color_primary
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            card,
            text=item_desc,
            font=("Arial", 13),
            text_color=TEXT_BODY,
            justify="left",
            wraplength=500
        ).pack(anchor="w", padx=14, pady=(0, 10))

    if data.get('tip'):
        tip_card = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_TIP_BG,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_TIP_BORDER
        )
        tip_card.pack(fill="x", padx=10, pady=(4, 16))

        ctk.CTkLabel(
            tip_card,
            text=data.get('tip', ''),
            font=("Arial", 12),
            text_color=COLOR_TIP_TEXT,
            justify="left",
            wraplength=500
        ).pack(anchor="w", padx=14, pady=10)


def build_cookies_section(scroll, lang, primary_color=None):
    color_primary = get_primary_color(primary_color)
    data = get_section_data(lang, 'cookies')

    # Заголовок
    ctk.CTkLabel(
        scroll,
        text=data.get('title', 'Getting Token'),
        font=("Arial", 22, "bold"),
        text_color=TEXT_HEADER
    ).pack(anchor="w", padx=10, pady=(8, 4))

    ctk.CTkLabel(
        scroll,
        text=data.get('subtitle', ''),
        font=("Arial", 13),
        text_color=TEXT_BODY,
        justify="left",
        wraplength=520
    ).pack(anchor="w", padx=10, pady=(0, 10))

    if data.get('quick_tip'):
        q_card = ctk.CTkFrame(
            scroll,
            fg_color=COLOR_TIP_BG,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_TIP_BORDER
        )
        q_card.pack(fill="x", padx=10, pady=(0, 12))

        ctk.CTkLabel(
            q_card,
            text=data.get('quick_tip'),
            font=("Arial", 12, "bold"),
            text_color=COLOR_TIP_TEXT,
            justify="left",
            wraplength=500
        ).pack(anchor="w", padx=14, pady=10)

    for step_title, step_desc, btn_url, btn_text in data.get('steps', []):
        step_card = ctk.CTkFrame(
            scroll,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER
        )
        step_card.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            step_card,
            text=step_title,
            font=("Arial", 14, "bold"),
            text_color=color_primary
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            step_card,
            text=step_desc,
            font=("Arial", 13),
            text_color=TEXT_BODY,
            justify="left",
            wraplength=500
        ).pack(anchor="w", padx=14, pady=(0, 8 if btn_url else 10))

        if btn_url and btn_text:
            ctk.CTkButton(
                step_card,
                text=btn_text,
                width=190,
                height=32,
                corner_radius=8,
                font=("Arial", 12, "bold"),
                fg_color="#4F46E5",
                hover_color="#4338CA",
                text_color="#FFFFFF",
                border_width=0,
                command=lambda u=btn_url: webbrowser.open(u, new=2)
            ).pack(anchor="w", padx=14, pady=(0, 10))

    if data.get('notes'):
        notes_card = ctk.CTkFrame(
            scroll,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER
        )
        notes_card.pack(fill="x", padx=10, pady=(4, 16))

        ctk.CTkLabel(
            notes_card,
            text="📌 Важные примечания:" if lang == 'ru' else "📌 Important Notes:",
            font=("Arial", 14, "bold"),
            text_color=TEXT_HEADER
        ).pack(anchor="w", padx=14, pady=(10, 4))

        for note in data.get('notes', []):
            ctk.CTkLabel(
                notes_card,
                text=note,
                font=("Arial", 12),
                text_color=TEXT_BODY,
                justify="left",
                wraplength=500
            ).pack(anchor="w", padx=14, pady=3)

        pad = ctk.CTkFrame(notes_card, fg_color="transparent", height=4)
        pad.pack()


def build_trouble_section(scroll, lang, open_tg_cmd=None, open_4pda_cmd=None, primary_color=None):
    color_primary = get_primary_color(primary_color)
    if open_tg_cmd is None:
        open_tg_cmd = lambda: webbrowser.open(TELEGRAM_URL, new=2)

    data = get_section_data(lang, 'trouble')

    # Заголовок
    ctk.CTkLabel(
        scroll,
        text=data.get('title', 'Troubleshooting'),
        font=("Arial", 22, "bold"),
        text_color=TEXT_HEADER
    ).pack(anchor="w", padx=10, pady=(8, 4))

    ctk.CTkLabel(
        scroll,
        text=data.get('subtitle', ''),
        font=("Arial", 13),
        text_color=TEXT_BODY,
        justify="left",
        wraplength=520
    ).pack(anchor="w", padx=10, pady=(0, 12))

    for prob_title, prob_sol in data.get('items', []):
        card = ctk.CTkFrame(
            scroll,
            fg_color=CARD_BG,
            corner_radius=12,
            border_width=1,
            border_color=CARD_BORDER
        )
        card.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            card,
            text=prob_title,
            font=("Arial", 14, "bold"),
            text_color=COLOR_ERROR
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            card,
            text=prob_sol,
            font=("Arial", 13),
            text_color=TEXT_BODY,
            justify="left",
            wraplength=500
        ).pack(anchor="w", padx=14, pady=(0, 10))

    # Разделитель
    sep = ctk.CTkFrame(scroll, fg_color=CARD_BORDER, height=1)
    sep.pack(fill="x", padx=10, pady=(4, 14))

    # Блок поддержки
    ctk.CTkLabel(
        scroll,
        text=data.get('support_title', 'Need Help?'),
        font=("Arial", 16, "bold"),
        text_color=TEXT_HEADER
    ).pack(anchor="w", padx=10, pady=(0, 4))

    ctk.CTkLabel(
        scroll,
        text=data.get('support_desc', ''),
        font=("Arial", 13),
        text_color=TEXT_BODY,
        justify="left",
        wraplength=520
    ).pack(anchor="w", padx=10, pady=(0, 10))

    btn_row = ctk.CTkFrame(scroll, fg_color="transparent")
    btn_row.pack(anchor="w", padx=10, pady=(0, 16))

    ctk.CTkButton(
        btn_row,
        text=data.get('chat_btn', 'Telegram Chat'),
        width=130,
        height=34,
        corner_radius=10,
        font=("Arial", 12, "bold"),
        fg_color="#5B8DEF",
        hover_color="#4A7AE6",
        text_color="#FFFFFF",
        border_width=0,
        command=open_tg_cmd
    ).pack(side="left")
