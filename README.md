# Xiaomi Unlock Tool (Mi Unlock Tool Revamp)

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-GPL--3.0--only-blue.svg?style=for-the-badge" alt="License: GPL-3.0-only"></a>
  <a href="https://github.com/AsInsideOut/miunlocktool/releases/latest"><img src="https://img.shields.io/badge/Release-v8.1%20Stable-success.svg?style=for-the-badge" alt="Latest Release"></a>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-informational.svg?style=for-the-badge" alt="Platforms">
  <a href="https://miunlock.su"><img src="https://img.shields.io/badge/Website-miunlock.su-orange.svg?style=for-the-badge" alt="Official Website"></a>
  <a href="https://t.me/miunlocktoolrevamp"><img src="https://img.shields.io/badge/Telegram-@miunlocktoolrevamp-2CA5E0.svg?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram Community"></a>
</p>

<p align="center">
  <strong>The most advanced open-source utility for bypassing Xiaomi HyperOS & MIUI bootloader unlocking quotas with sub-millisecond NTP precision.</strong>
</p>

<p align="center">
  <a href="#english"><b>English</b></a> • <a href="#русский"><b>Русский</b></a>
</p>

---

<a name="english"></a>
## English

### Overview

**Xiaomi Unlock Tool** is an open-source, community-driven utility designed to automate the bootloader unlock authorization process on Xiaomi, Redmi, and POCO smartphones running **Xiaomi HyperOS (1, 2, and 3)** as well as **MIUI 14**.

Starting with HyperOS, Xiaomi implemented strict global daily quotas (~1,500–2,000 devices worldwide) that reset exactly at **00:00:00 Beijing Time (UTC+8)**. Manually clicking the unlock button in the Xiaomi Community app almost always results in *"Limit reached"*.

Xiaomi Unlock Tool solves this by combining:
1. **Stratum-1 NTP time synchronization** across multiple global servers (Google, Cloudflare, pool.ntp.org).
2. **Dynamic round-trip latency compensation** measuring ping directly against Xiaomi's authentication gateways (`sgp-api.buy.mi.com`).
3. **Automated sub-millisecond submission triggers** that land your request precisely as the daily quota window opens.

---

### Key Features

* **Sub-Millisecond Precision Engine:** Synchronizes against global atomic NTP clocks and auto-calibrates network round-trip time right at `23:59:59.xxx` Beijing time.
* **Safe & Direct Protocol:** Communicates directly with Xiaomi's official endpoints over HTTPS. No middleman servers, no data logging, no credentials stored.
* **Modern Desktop GUI:** Crafted with CustomTkinter (Material Design 3 style), featuring dark/light themes, custom accent colors, and real-time logs.
* **Headless CLI Version:** Standalone Python CLI (`sourcecode/cli/miunlock_cli.py`) for servers, VPS, Linux, macOS, and automated cron setups.
* **Native Android App (In Development):** A Kotlin-based native app (`sourcecode/android`) allowing direct quota application from your phone without a PC.
* **Flexible Authentication:** Supports automatic cookie extraction from Chromium-based browsers, manual token input, or instant QR-code login.
* **Multi-Language Interface:** Full native support for 10+ languages (English, Russian, Spanish, Chinese, Turkish, Portuguese, Hindi, etc.).
* **Regional Timing Profiles:** Pre-configured latency presets for Europe, Asia, and the Americas, plus up to 15 custom timing triggers.

---

### Supported Devices & Firmware

| Firmware Region | Code | Support Status | Notes |
| :--- | :---: | :---: | :--- |
| **Global** | `MI` | Supported | Official global firmware |
| **Europe** | `EEA` / `EU` | Supported | European Union devices |
| **Russia** | `RU` | Supported | Russian regional firmware |
| **India** | `IN` | Supported | Indian devices |
| **Indonesia** | `ID` | Supported | Indonesian devices |
| **Turkey / Taiwan** | `TR` / `TW` | Supported | Turkish & Taiwanese regional firmware |
| **China** | `CN` | Not Supported | Requires Mainland China Mi Community Lv.5 status |

> [!IMPORTANT]
> **Account Prerequisites:**
> 1. Your Xiaomi (Mi) account must be **older than 30 days**.
> 2. In the Xiaomi Community app / web profile, your region **MUST be set to Global**.
> 3. After the tool secures your quota, account binding in *Developer Options -> Mi Unlock Status* **must be performed strictly over mobile data (SIM card)** with Wi-Fi switched off.

---

### Installation & Quick Start

#### Option A: Windows (Pre-compiled Portable EXE)
1. Download the latest `Xiaomi Unlock Tool 8.1.zip` from [Releases](https://github.com/AsInsideOut/miunlocktool/releases/latest) or our official website [miunlock.su](https://miunlock.su).
2. Extract the ZIP archive to any folder.
3. Launch `Xiaomi Unlock Tool 8.1.exe`. No installation or Python setup needed.

#### Option B: Linux / macOS / Run from Python Source
1. Ensure Python **3.10 or newer** is installed:
   ```bash
   python --version
   ```
2. Clone this repository:
   ```bash
   git clone https://github.com/AsInsideOut/miunlocktool.git
   cd miunlocktool
   ```
3. Install required Python packages:
   ```bash
   pip install customtkinter packaging ntplib darkdetect pytz urllib3 icmplib requests pygame-ce
   ```
4. Run the GUI application:
   ```bash
   python sourcecode/pc/8.1.py
   ```
   Or run the lightweight Terminal CLI version:
   ```bash
   python sourcecode/cli/miunlock_cli.py
   ```

---

### Step-by-Step Instructions

1. **Launch the tool** and review the initial welcome dialogue.
2. Open **"Instructions and Script settings"** -> **"Getting Cookies"** and select your browser (or use the built-in QR Code login).
3. Retrieve your `new_bbs_token` and paste it into the main token field.
4. Click **"Start application"**.
5. **Timeline of operation (Beijing Time GMT+8):**
   * **23:58:00** — Precision clock resynchronization via NTP.
   * **23:59:40** — Real-time latency (ping) calculation to Xiaomi's servers.
   * **23:59:58 – 23:59:59.xxx** — Timed authorization requests are dispatched.
6. At **00:01:00 Beijing Time**, proceed to your smartphone's *Settings -> Additional settings -> Developer options -> Mi Unlock status* and tap **"Add account and device"** (using mobile SIM data).

---

### Common Issues & Solutions

| Error Message | Cause & Recommended Action |
| :--- | :--- |
| **"Couldn't add. Please go to Mi Community to apply..."** | Daily quota full. The server limit (~1,500/day) was exhausted before your request landed. Re-run the tool tomorrow with adjusted timing offsets. |
| **"System is being upgraded. Please try again later"** | Known Xiaomi firmware glitch (frequent on Redmi 13 / Note 13 series). Wait for the next HyperOS OTA or retry in a few days. |
| **"The account is not authorized"** | Account is younger than 30 days or Community region is not set to Global. |
| **"Wait timer (168 / 360 hours)"** | **Success!** Your account is approved and bound. You only need to wait out the mandatory security timer before running the official PC unlocker. |

---

### License

This project is licensed under the **GNU General Public License v3.0 only** (`GPL-3.0-only`).  
See the [LICENSE](LICENSE) file for the full legal text.

* **Summary of Terms:**
  * **Freedom:** You may run, study, modify, and redistribute this software.
  * **Copyleft (Section 6):** All forks, modifications, and derivative distributions **MUST** be open-sourced under the exact same `GPL-3.0-only` license. Closed-source binary redistribution or proprietary repackaging is strictly prohibited.
  * **Attribution (Sections 4, 5a, 5d):** Any derivative work **must preserve** all original copyright notices (`Copyright (C) 2026 AsInsideOut`), state that it was modified, and maintain visible legal notices in the UI / CLI.
  * **No Warranty:** Provided "AS IS", without warranty of any kind.

```text
SPDX-License-Identifier: GPL-3.0-only
Copyright (C) 2026 AsInsideOut
```

---

### Credits & Acknowledgments

* **[offici5l](https://github.com/offici5l/)** — Creator of the original Python-based *Xiaomi Flash Unlock* concept and pioneer in community unlock research.
* **[AsInsideOut](https://github.com/AsInsideOut)** — Complete project revamp, custom NTP timing engine, CustomTkinter modern UI, CLI edition, and cross-platform ecosystem.

---

### Contacts & Community

* **Official Website:** [https://miunlock.su](https://miunlock.su) (Mirror: [https://miunlocktool.ru](https://miunlocktool.ru))
* **Telegram Channel & Chat:** [@miunlocktoolrevamp](https://t.me/miunlocktoolrevamp)
* **4PDA Discussion Topic:** [4PDA Xiaomi Unlock Tool Forum](https://4pda.to/forum/index.php?showtopic=721838&view=findpost&p=145201115)
* **Reddit:** [u/AsInsideOut](https://reddit.com/u/AsInsideOut)
* **Support Email:** `support@miunlock.su`

#### Support the Project
* **Crypto (USDT / TON):** `UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG`
* **Bitcoin (BTC):** `bc1qzzt00sk0zdxgskw8xx8cjh4jl69wl7fvlshhsh`
* **DonationAlerts:** [https://www.donationalerts.com/r/asinsideout](https://www.donationalerts.com/r/asinsideout)
* **DaLink:** [https://dalink.to/asinsideout](https://dalink.to/asinsideout)

---

<a name="русский"></a>
## Русский

### О проекте

**Xiaomi Unlock Tool** — это универсальная открытая утилита для автоматической и ручной подачи официальной заявки на разблокировку загрузчика (Bootloader Unlock) смартфонов Xiaomi, Redmi и POCO под управлением **Xiaomi HyperOS (версии 1, 2 и 3)**, а также **MIUI 14**.

С переходом на HyperOS компания Xiaomi ввела жесткие глобальные лимиты (всего ~1500–2000 квот в сутки на весь мир), которые обновляются строго в **00:00:00 по Пекинскому времени (UTC+8)**. Вручную через официальное приложение Mi Community поймать квоту практически невозможно — лимит разбирают за доли секунды.

Xiaomi Unlock Tool решает эту проблему благодаря:
1. **Высокоточной синхронизации времени по протоколу NTP** с эталонными атомными серверами (Google, Cloudflare, pool.ntp.org).
2. **Динамическому расчету пинга** и сетевой задержки до авторизационных серверов Xiaomi (`sgp-api.buy.mi.com`).
3. **Автоматической отправке запросов** с точностью до миллисекунд в момент открытия окна квот.

---

### Ключевые возможности

* **Субмиллисекундный тайминг-движок:** Автоматическая калибровка времени и задержки сети прямо перед `23:59:59.xxx` по Пекину.
* **Безопасность и прямое подключение:** Запросы идут строго по HTTPS напрямую на серверы Xiaomi. Без прокси, без сторонних серверов и без сбора данных.
* **Современный графический интерфейс:** Построен на CustomTkinter (стиль Material Design 3) с поддержкой темной/светлой темы, выбором акцентных цветов и подробным логом.
* **Консольная версия (CLI):** Автономный терминальный скрипт (`sourcecode/cli/miunlock_cli.py`) для Linux, macOS, выделенных серверов (VPS) и Docker.
* **Нативное приложение Android (в разработке):** Приложение на Kotlin (`sourcecode/android`) для подачи заявки прямо со смартфона без ПК.
* **Несколько способов авторизации:** Автоматический захват Cookies из браузеров, ручной ввод токена или быстрый вход по QR-коду.
* **Полная мультиязычность:** Встроенная поддержка более 10 языков (русский, английский, испанский, китайский, турецкий и др.).
* **Региональные профили:** Готовые пресеты задержек для Европы, Азии и Америки, плюс до 15 настраиваемых миллисекундных слотов отправки.

---

### Поддерживаемые устройства и прошивки

| Регион прошивки | Индекс | Статус | Примечание |
| :--- | :---: | :---: | :--- |
| **Глобальная** | `MI` | Поддерживается | Официальная международная прошивка |
| **Европейская** | `EEA` / `EU` | Поддерживается | Прошивка для стран ЕС |
| **Россия** | `RU` | Поддерживается | Официальная русская прошивка |
| **Индия** | `IN` | Поддерживается | Прошивка для индийского региона |
| **Индонезия** | `ID` | Поддерживается | Прошивка для Индонезии |
| **Турция / Тайвань** | `TR` / `TW` | Поддерживается | Региональные прошивки |
| **Китай** | `CN` | Не поддерживается | Требует аккаунт 5 уровня в Mi Community Китая |

> [!IMPORTANT]
> **Обязательные требования к аккаунту:**
> 1. Ваш аккаунт Xiaomi (Mi) должен быть активен **более 30 дней**.
> 2. В приложении или на сайте Mi Community в настройках профиля должен быть строго выбран регион **Global (Глобальный)**.
> 3. Привязка аккаунта в *Настройки -> Для разработчиков -> Статус Mi Unlock* выполняется **СТРОГО через мобильный интернет с SIM-карты** (Wi-Fi должен быть отключен).

---

### Установка и запуск

#### Вариант 1: Windows (Готовый EXE-файл)
1. Скачайте архив `Xiaomi Unlock Tool 8.1.zip` со страницы [Релизов](https://github.com/AsInsideOut/miunlocktool/releases/latest) или с официального сайта [miunlock.su](https://miunlock.su).
2. Распакуйте ZIP в отдельную папку.
3. Запустите `Xiaomi Unlock Tool 8.1.exe`. Никаких дополнительных настроек Python не требуется.

#### Вариант 2: Linux / macOS / Запуск из исходников Python
1. Убедитесь, что установлен Python **3.10 или новее**:
   ```bash
   python --version
   ```
2. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/AsInsideOut/miunlocktool.git
   cd miunlocktool
   ```
3. Установите зависимости:
   ```bash
   pip install customtkinter packaging ntplib darkdetect pytz urllib3 icmplib requests pygame-ce
   ```
4. Запустите графическую утилиту:
   ```bash
   python sourcecode/pc/8.1.py
   ```
   Либо консольный вариант:
   ```bash
   python sourcecode/cli/miunlock_cli.py
   ```

---

### Пошаговая инструкция

1. Запустите программу и ознакомьтесь с приветственным окном.
2. Откройте **«Инструкции и настройки скрипта»** -> **«Получить Cookies»** и выберите ваш браузер (или используйте вход по QR-коду).
3. Получите `new_bbs_token` и вставьте его в поле ввода главной программы.
4. Нажмите **«Запустить приложение»**.
5. **График работы программы (по Пекинскому времени UTC+8):**
   * **23:58:00** — точная синхронизация времени через атомные серверы NTP.
   * **23:59:40** — расчет пинга и сетевой задержки до серверов Xiaomi.
   * **23:59:58 – 23:59:59.xxx** — отправка запросов на авторизацию.
6. В **00:01:00 по Пекину** зайдите на телефоне в *Настройки -> Расширенные настройки -> Для разработчиков -> Статус Mi Unlock* и нажмите **«Связать аккаунт и устройство»** (через мобильный интернет).

---

### Частые ошибки и их решения

| Ошибка | Причина и что делать |
| :--- | :--- |
| **"Couldn't add. Please go to Mi Community to apply..."** | Лимит квот исчерпан. 1500 ежедневных квот разобрали быстрее, чем запрос дошел до сервера. Попробуйте снова на следующий день, скорректировав тайминги в настройках. |
| **"System is being upgraded. Please try again later"** | Известный системный глюк серверов Xiaomi (часто встречается на смартфонах Redmi 13 / Note 13 series). Остается только ждать обновления прошивки или пробовать через несколько дней. |
| **"The account is not authorized"** | Аккаунту менее 30 дней, либо в профиле Mi Community не выбран регион Global. |
| **"Таймер ожидания (168 / 360 часов)"** | **Успех!** Заявка одобрена, аккаунт привязан. Остается лишь подождать указанное время и завершить процедуру в официальном Mi Flash Unlock на ПК. |

---

### Лицензия

Проект распространяется на условиях лицензии **GNU General Public License v3.0 only** (`GPL-3.0-only`).  
Полный текст лицензии находится в файле [LICENSE](LICENSE).

* **Основные условия:**
  * **Свобода:** Разрешено свободное использование, изучение, изменение и распространение утилиты.
  * **Строгий Copyleft (Секция 6):** Любые форки, производные сборки и модификации **ОБЯЗАНЫ** публиковаться под той же лицензией `GPL-3.0-only` с открытием полного исходного кода. Запрещено закрывать код или делать платные сборки.
  * **Сохранение авторства (Секции 4, 5a, 5d):** Форки **обязаны сохранять** оригинальные копирайты (`Copyright (C) 2026 AsInsideOut`), уведомление о том, что код модифицирован, и правовые ссылки в интерфейсе.
  * **Без гарантий:** Программа предоставляется «как есть», без явных или косвенных гарантий.

```text
SPDX-License-Identifier: GPL-3.0-only
Copyright (C) 2026 AsInsideOut
```

---

### Благодарности

* **[offici5l](https://github.com/offici5l/)** — Автор оригинальной концепции Python-скрипта *Xiaomi Flash Unlock* и первопроходец в исследовании протоколов разблокировки.
* **[AsInsideOut](https://github.com/AsInsideOut)** — Полный ревамп проекта, разработка NTP тайминг-движка, графического интерфейса CustomTkinter, CLI-версии и экосистемы утилиты.

---

### Контакты и сообщество

* **Официальный сайт:** [https://miunlock.su](https://miunlock.su) (Зеркало: [https://miunlocktool.ru](https://miunlocktool.ru))
* **Telegram канал и чат:** [@miunlocktoolrevamp](https://t.me/miunlocktoolrevamp)
* **Тема на 4PDA:** [4PDA Xiaomi Unlock Tool](https://4pda.to/forum/index.php?showtopic=721838&view=findpost&p=145201115)
* **Reddit:** [u/AsInsideOut](https://reddit.com/u/AsInsideOut)
* **Электронная почта:** `support@miunlock.su`

#### Поддержать проект
* **Криптовалюта (USDT / TON):** `UQBCkvXTF-NiT7P8g0G-4oiAdsU81rMWJNYBTxDrbl76FabG`
* **Bitcoin (BTC):** `bc1qzzt00sk0zdxgskw8xx8cjh4jl69wl7fvlshhsh`
* **DonationAlerts:** [https://www.donationalerts.com/r/asinsideout](https://www.donationalerts.com/r/asinsideout)
* **DaLink:** [https://dalink.to/asinsideout](https://dalink.to/asinsideout)
