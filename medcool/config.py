import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SCHEDULE_URL = 'https://raspisanie.medcoll.ru/'
STUDENT_SCHEDULE_URL = 'https://raspisanie.medcoll.ru/students/'
TEACHER_SCHEDULE_URL = 'https://raspisanie.medcoll.ru/teachers/'

# ID администратора бота
ADMIN_ID = 2084899177

# Время для ежедневной отправки расписания (можно изменить)
DAILY_SCHEDULE_TIME = os.getenv('DAILY_SCHEDULE_TIME', '06:00')

# Настройки бота
BOT_SETTINGS = {
    'daily_schedule_time': DAILY_SCHEDULE_TIME,
    'enable_daily_schedule': os.getenv('ENABLE_DAILY_SCHEDULE', 'true').lower() == 'true',
    'welcome_message': os.getenv('WELCOME_MESSAGE', 'Добро пожаловать в бот расписания группы Ф22!')
}

# Настройки админ-панели
ADMIN_SETTINGS = {
    'admin_id': ADMIN_ID,
    'broadcast_cooldown': 60,  # секунд между рассылками
    'max_broadcast_length': 4000,  # максимальная длина сообщения рассылки
    'log_lines_default': 50  # строк логов по умолчанию
}
