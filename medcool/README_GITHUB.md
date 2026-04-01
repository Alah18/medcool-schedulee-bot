# 🤖 Telegram Бот Расписания - Медицинский Колледж

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![python-telegram-bot](https://img.shields.io/badge/PTB-20.3-green)](https://github.com/python-telegram-bot/python-telegram-bot)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

> 📚 Бот для получения расписания группы Ф22 из медицинского колледжа. Парсит реальное расписание с официального сайта.

## ✨ Возможности

- 📅 **Расписание на сегодня/завтра**
- 📋 **Расписание на неделю**
- 🔔 **Ежедневная рассылка** в установленное время
- 🔐 **Админ-панель** с рассылкой и статистикой
- 🚀 **Работает 24/7** на PythonAnywhere (бесплатно!)

## 🚀 Быстрый старт

### 1. Установка

```bash
# Клонируйте репозиторий
git clone https://github.com/ВАШ_ЛОГИН/medcool-schedule-bot.git
cd medcool-schedule-bot

# Создайте виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate    # Windows

# Установите зависимости
pip install -r requirements.txt
```

### 2. Настройка

Создайте файл `.env`:

```env
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
DAILY_SCHEDULE_TIME=06:00
ENABLE_DAILY_SCHEDULE=true
```

### 3. Запуск

```bash
# Windows
start_bot.bat

# Linux/Mac
python run.py
```

## 🤖 Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Начать работу с ботом |
| `/today` | Расписание на сегодня |
| `/tomorrow` | Расписание на завтра |
| `/week` | Расписание на неделю |
| `/nextweek` | Расписание на след. неделю |
| `/admin` | Админ-панель (только для админа) |
| `/stats` | Статистика бота |
| `/broadcast` | Рассылка сообщений |
| `/help` | Помощь |

## 🔐 Админ-панель

Админ ID: `2084899177`

**Функции:**
- 📊 Статистика пользователей
- 📢 Массовая рассылка
- ⏰ Управление временем рассылки
- 📋 Просмотр логов
- 🔄 Перезапуск бота

## 🌐 Бесплатный хостинг 24/7

### PythonAnywhere (рекомендуется)

1. Регистрация: https://www.pythonanywhere.com/
2. Загрузка файлов
3. Создание Always-on задачи

**Подробная инструкция:** [`DEPLOY_PYTHONANYWHERE.md`](DEPLOY_PYTHONANYWHERE.md)

## 📁 Структура проекта

```
medcool-schedule-bot/
├── 🤖 bot.py              # Telegram бот
├── ⚙️ schedule_parser.py   # Парсер расписания
├── ⚙️ config.py           # Конфигурация
├── 🚀 run.py              # Точка входа
├── 📦 requirements.txt    # Зависимости
├── 🔧 .env.example        # Пример .env
├── 📖 README.md           # Этот файл
└── 📁 site/               # Копия сайта (опционально)
```

## 🛠️ Технологии

- **Python 3.11**
- **python-telegram-bot 20.3**
- **BeautifulSoup4** - парсинг HTML
- **Requests** - HTTP запросы
- **APScheduler** - планировщик задач

## 📊 Сайт-источник

- 🌐 https://raspisanie.medcoll.ru/students/
- Группа: Ф22 (ID: 148663)

## 🤝 Участие в проекте

PR приветствуются! Особенно:
- Улучшение парсера
- Новые функции
- Исправление багов

## 📜 Лицензия

MIT License - свободное использование!

---

⭐ **Если бот полезен - поставьте звезду на GitHub!**

👨‍💻 **Создатель:** @ваш_телеграм
📧 **Email:** ваш@email.com
