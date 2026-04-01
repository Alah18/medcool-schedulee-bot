# 🚀 PythonAnywhere - Бесплатный хостинг бота 24/7

## 📋 **ШАГ 1: Регистрация**

1. Откройте: https://www.pythonanywhere.com/
2. Нажмите **"Start running Python online for free"**
3. Зарегистрируйтесь (email, username, password)
4. Подтвердите email

## 📁 **ШАГ 2: Загрузка файлов**

### Способ A: Через Git (рекомендуется)

```bash
# В консоли PythonAnywhere:
git clone https://github.com/ВАШ_ЛОГИН/medcool-schedule-bot.git
cd medcool-schedule-bot
```

### Способ B: Через веб-интерфейс

1. Зайдите на **Files** tab
2. Создайте папку: `medcool-schedule-bot`
3. Загрузите все файлы через **Upload a file**

## ⚙️ **ШАГ 3: Настройка окружения**

### Откройте Bash консоль:

```bash
# Создайте виртуальное окружение
python3.11 -m venv venv

# Активируйте
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

## 🔐 **ШАГ 4: Создание .env файла**

```bash
# Создайте файл:
nano .env

# Добавьте:
TELEGRAM_BOT_TOKEN=8734742940:AAHGMyIz4YTB7s5RxlW59GjN_Qu2WvloXlw
DAILY_SCHEDULE_TIME=06:00
ENABLE_DAILY_SCHEDULE=true
```

**Сохраните:** Ctrl+O, Enter, Ctrl+X

## 🚀 **ШАГ 5: Запуск бота**

### Создайте файл запуска:

```bash
nano start_bot.py
```

**Содержимое:**
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/ВАШ_USERNAME/medcool-schedule-bot')

from bot import TelegramBot

if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()
```

### Запуск:

```bash
# В консоли (с активированным venv):
python start_bot.py
```

## 🔄 **ШАГ 6: Настройка Always-on задачи (ВАЖНО!)**

1. Перейдите на **Tasks** tab
2. В **Scheduled task** введите:

```bash
cd /home/ВАШ_USERNAME/medcool-schedule-bot && source venv/bin/activate && python start_bot.py
```

3. Нажмите **Create**
4. Выберите время: **00:00** (для перезапуска)

## ⚡ **ШАГ 7: Постоянный процесс (ЛУЧШИЙ СПОСОБ)**

### Создайте Always-on процесс:

1. Перейдите на **Always-on tasks** (в меню Tasks)
2. В поле команда:

```bash
cd /home/ВАШ_USERNAME/medcool-schedule-bot && source venv/bin/activate && python run.py
```

3. Нажмите **Create always-on task**
4. Бот будет работать **24/7 без перерыва!**

## 🎯 **Проверка работы**

1. Откройте Telegram
2. Найдите своего бота
3. Отправьте `/start`
4. Бот должен ответить!

## 🛠️ **Управление ботом**

### Перезапуск:

```bash
# Найдите процесс бота
ps aux | grep python

# Убейте процесс
kill <PID>

# Или перезапустите через веб-интерфейс Tasks
```

### Просмотр логов:

1. Перейдите на **Dashboard**
2. Найдите раздел **Always-on tasks**
3. Нажмите **View log** - увидите логи бота

### Обновление бота:

```bash
# Через Git:
cd /home/ВАШ_USERNAME/medcool-schedule-bot
git pull origin main

# Перезапуск:
# Остановите задачу в веб-интерфейсе и запустите снова
```

## ⚠️ **Ограничения бесплатного плана:**

- ✅ **1 Always-on задача** (достаточно для бота)
- ✅ **1 Scheduled задача**
- ✅ **512 MB RAM** (хватит для бота)
- ✅ **100 MB диска**
- ❌ **Web приложения спят** (но Always-on работает 24/7!)

## 🎉 **Готово!**

**Ваш бот теперь работает 24/7 на PythonAnywhere бесплатно!**

### Альтернативы (если PythonAnywhere не подходит):

1. **Railway.app** - $5/месяц (но есть free tier с ограничениями)
2. **Render.com** - бесплатно, но спит после 15 мин бездействия
3. **Fly.io** - $5/месяц кредитов (хватит на 1-2 малых приложения)
4. **Oracle Cloud** - бесплатно навсегда, но сложная настройка

**PythonAnywhere - лучший выбор для бесплатного хостинга бота!** 🚀
