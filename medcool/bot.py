import logging
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import TELEGRAM_BOT_TOKEN, DAILY_SCHEDULE_TIME, BOT_SETTINGS, ADMIN_SETTINGS, ADMIN_ID
from schedule_parser import ScheduleParser

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация парсера
schedule_parser = ScheduleParser()

# Хранилище пользовательских данных
user_data = {}
search_states = {}  # Для хранения состояния поиска
broadcast_states = {}  # Для состояния рассылки админа
admin_logs = []  # Логи действий админа

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.scheduler = AsyncIOScheduler()
        self.setup_handlers()
        self.setup_scheduler()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("raspis", self.raspis_command))
        self.application.add_handler(CommandHandler("today", self.today_command))
        self.application.add_handler(CommandHandler("tomorrow", self.tomorrow_command))
        self.application.add_handler(CommandHandler("week", self.week_command))
        self.application.add_handler(CommandHandler("nextweek", self.next_week_command))
        self.application.add_handler(CommandHandler("open", self.open_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CommandHandler("settime", self.set_time_command))
        self.application.add_handler(CommandHandler("test", self.test_schedule_command))
        # Админ команды
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        self.application.add_handler(CommandHandler("logs", self.logs_command))
        self.application.add_handler(CommandHandler("restart", self.restart_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_message))
    
    def setup_scheduler(self):
        """Настройка планировщика для ежедневной отправки расписания"""
        # Проверяем, включена ли рассылка
        if not BOT_SETTINGS['enable_daily_schedule']:
            logger.info("Ежедневная рассылка отключена в настройках")
            return
        
        # Получаем время из настроек
        hour, minute = map(int, BOT_SETTINGS['daily_schedule_time'].split(':'))
        
        # Добавляем задачу для ежедневной отправки
        self.scheduler.add_job(
            self.send_daily_schedule,
            CronTrigger(hour=hour, minute=minute),
            id='daily_schedule',
            name='Отправка ежедневного расписания',
            replace_existing=True
        )
        
        logger.info(f"Планировщик настроен на время: {BOT_SETTINGS['daily_schedule_time']}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user_id = update.effective_user.id
        
        # Автоматически устанавливаем группу Ф22 для всех пользователей
        if user_id not in user_data:
            user_data[user_id] = {}
        user_data[user_id]['group'] = 'Ф22'
        
        welcome_message = (
            "👋 *Добро пожаловать в бот расписания группы Ф22!*\n\n"
            "🎓 *Медицинский колледж - группа Ф22*\n\n"
            "📚 *Доступные команды:*\n"
            "• /raspis - Расписание на сегодня\n"
            "• /today - Расписание на сегодня\n"
            "• /tomorrow - Расписание на завтра\n"
            "• /week - Расписание на эту неделю\n"
            "• /nextweek - Расписание на следующую неделю\n"
            "• /open - Открыть веб-сайт\n"
            "• /settings - Настройки бота\n"
            "• /settime ЧЧ:ММ - Установить время рассылки\n"
            "• /test - Тестовая отправка рассылки\n"
            "• /help - Помощь\n\n"
            "💡 *Просто отправьте любое сообщение для расписания!*"
        )
        
        keyboard = [
            [
                InlineKeyboardButton("📅 Сегодня", callback_data="schedule_Ф22_today"),
                InlineKeyboardButton("📆 Завтра", callback_data="schedule_Ф22_tomorrow")
            ],
            [
                InlineKeyboardButton("📋 Эта неделя", callback_data="schedule_Ф22_week"),
                InlineKeyboardButton("📋 След. неделя", callback_data="schedule_Ф22_nextweek")
            ],
            [
                InlineKeyboardButton("🌐 Открыть сайт", callback_data="open_website")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_message = (
            "📖 *Помощь по боту расписания*\n\n"
            "🔹 *Основные команды:*\n"
            "/start - Главное меню\n"
            "/raspis - Показать расписание\n"
            "/today - Расписание на сегодня\n"
            "/tomorrow - Расписание на завтра\n"
            "/groups - Список доступных групп\n"
            "/help - Эта справка\n\n"
            "🔹 *Как использовать:*\n"
            "1. Нажмите на кнопку \"Выбрать группу\" чтобы указать свою группу\n"
            "2. Используйте кнопки для быстрого доступа к расписанию\n"
            "3. Бот будет отправлять расписание каждый день в 6:00\n\n"
            "🔹 *Дополнительные возможности:*\n"
            "• Автоматическое обновление расписания\n"
            "• Уведомления об изменениях\n"
            "• Быстрый доступ к расписанию на любой день\n\n"
            "Если у вас возникли вопросы, обратитесь к администратору."
        )
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def raspis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /raspis"""
        await self.show_schedule(update, context, 'Ф22', 'today')
    
    async def week_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /week"""
        await self.show_week_schedule(update, context, 'Ф22')
    
    async def next_week_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /nextweek"""
        # Получаем дату начала следующей недели
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7 or 7
        next_monday = today + timedelta(days=days_until_monday)
        next_week_start = next_monday.strftime('%d.%m.%Y')
        
        await self.show_week_schedule(update, context, 'Ф22', next_week_start)
    
    async def open_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /open"""
        await self.show_website(update, context)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /settings"""
        settings_message = (
            "⚙️ *Настройки бота*\n\n"
            f"🕐 *Время ежедневной рассылки:* {BOT_SETTINGS['daily_schedule_time']}\n"
            f"📧 *Рассылка включена:* {'✅ Да' if BOT_SETTINGS['enable_daily_schedule'] else '❌ Нет'}\n\n"
            "🎯 *Доступные команды:*\n"
            "• /settime ЧЧ:ММ - установить время рассылки\n"
            "• /settings - показать настройки\n\n"
            "💡 *Пример: /settime 07:30*"
        )
        
        keyboard = [
            [InlineKeyboardButton("🕐 Изменить время", callback_data="set_time")],
            [InlineKeyboardButton("📅 Расписание", callback_data="schedule_Ф22_today")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(settings_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def set_time_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /settime"""
        if len(context.args) != 1:
            await update.message.reply_text(
                "❌ *Неверный формат команды!*\n\n"
                "Используйте: /settime ЧЧ:ММ\n"
                "Например: /settime 07:30",
                parse_mode='Markdown'
            )
            return
        
        time_str = context.args[0]
        try:
            # Проверяем формат времени
            datetime.strptime(time_str, '%H:%M')
            
            # Обновляем настройку
            BOT_SETTINGS['daily_schedule_time'] = time_str
            
            # Обновляем планировщик
            self.update_scheduler_time(time_str)
            
            await update.message.reply_text(
                f"✅ *Время рассылки изменено на {time_str}*\n\n"
                f"Теперь расписание будет приходить в {time_str} каждый день.",
                parse_mode='Markdown'
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ *Неверный формат времени!*\n\n"
                "Используйте формат ЧЧ:ММ (24-часовой формат)\n"
                "Например: 07:30, 18:00",
                parse_mode='Markdown'
            )
    
    def update_scheduler_time(self, time_str: str):
        """Обновление времени планировщика"""
        try:
            hour, minute = map(int, time_str.split(':'))
            
            # Удаляем старое задание
            try:
                self.scheduler.remove_job('daily_schedule')
            except:
                pass
            
            # Добавляем новое задание, если рассылка включена
            if BOT_SETTINGS['enable_daily_schedule']:
                self.scheduler.add_job(
                    self.send_daily_schedule,
                    CronTrigger(hour=hour, minute=minute),
                    id='daily_schedule',
                    name='Отправка ежедневного расписания',
                    replace_existing=True
                )
            
            logger.info(f"Время рассылки обновлено на {time_str}")
            
        except Exception as e:
            logger.error(f"Ошибка при обновлении времени рассылки: {e}")
    
    async def test_schedule_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Тестовая отправка расписания"""
        await update.message.reply_text("🔄 *Тестирую отправку рассылки...*", parse_mode='Markdown')
        
        try:
            # Вызываем функцию отправки
            await self.send_daily_schedule()
            await update.message.reply_text("✅ *Тестовая рассылка отправлена!*", parse_mode='Markdown')
        except Exception as e:
            await update.message.reply_text(f"❌ *Ошибка при отправке: {e}*", parse_mode='Markdown')
    
    async def groups_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /groups"""
        await update.message.reply_text("🔍 *Получаю список групп...*", parse_mode='Markdown')
        
        try:
            groups = schedule_parser.get_groups()
            
            if not groups:
                await update.message.reply_text(
                    "❌ *Не удалось получить список групп.*\n"
                    "Пожалуйста, попробуйте позже.",
                    parse_mode='Markdown'
                )
                return
            
            message = "👥 *Доступные группы:*\n\n"
            for i, group in enumerate(groups[:20], 1):  # Ограничиваем вывод
                message += f"{i}. {group}\n"
            
            if len(groups) > 20:
                message += f"\n... и еще {len(groups) - 20} групп"
            
            keyboard = [[InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка при получении групп: {e}")
            await update.message.reply_text(
                "❌ *Произошла ошибка при получении списка групп.*\n"
                "Попробуйте позже.",
                parse_mode='Markdown'
            )
    
    async def today_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /today"""
        await self.show_schedule(update, context, 'Ф22', 'today')
    
    async def tomorrow_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /tomorrow"""
        await self.show_schedule(update, context, 'Ф22', 'tomorrow')
    
    async def show_website(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать информацию о веб-сайте"""
        website_message = (
            "🌐 *Веб-сайт расписания группы Ф22*\n\n"
            "📱 *Адрес сайта:* http://localhost:5000\n\n"
            "🎯 *Возможности сайта:*\n"
            "• 📅 Расписание на любой день\n"
            "• 📋 Расписание на всю неделю\n"
            "• 🔍 Поиск по датам\n"
            "• 📱 Удобный интерфейс\n\n"
            "💡 *Откройте сайт в браузере для удобного просмотра расписания!*\n\n"
            "🔗 *Прямая ссылка:* http://localhost:5000/schedule?group=Ф22"
        )
        
        keyboard = [
            [InlineKeyboardButton("🌐 Открыть сайт", url="http://localhost:5000")],
            [InlineKeyboardButton("📅 Расписание сегодня", callback_data="schedule_Ф22_today")],
            [InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.message:
            await update.message.reply_text(website_message, parse_mode='Markdown', reply_markup=reply_markup)
        elif update.callback_query:
            await update.callback_query.edit_message_text(website_message, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def show_group_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, search_query: str = None):
        """Показать выбор группы с поиском"""
        try:
            user_id = update.effective_user.id
            
            # Устанавливаем состояние поиска
            search_states[user_id] = True
            
            # Ищем группы
            if search_query:
                groups = schedule_parser.search_groups(search_query)
                message = f"🔍 *Результаты поиска по запросу:* `{search_query}`\n\n"
            else:
                groups = schedule_parser.get_groups()[:20]  # Первые 20 групп
                message = ("👥 *Выберите вашу группу:*\n\n"
                         "💡 *Введите название группы для поиска*\n"
                         "Например: Ф22, М11, А21 и т.д.\n\n")
            
            if not groups:
                error_message = "❌ *Группы не найдены.*\nПопробуйте другой запрос."
                if update.message:
                    await update.message.reply_text(error_message, parse_mode='Markdown')
                elif update.callback_query:
                    await update.callback_query.edit_message_text(error_message, parse_mode='Markdown')
                return
            
            # Создаем клавиатуру с группами
            keyboard = []
            for group in groups:
                keyboard.append([InlineKeyboardButton(group, callback_data=f"group_{group}")])
            
            # Добавляем кнопки управления
            keyboard.extend([
                [InlineKeyboardButton("🔍 Новый поиск", callback_data="new_search")],
                [InlineKeyboardButton("📋 Все группы", callback_data="show_all_groups")],
                [InlineKeyboardButton("🔙 Вернуться в меню", callback_data="back_to_menu")]
            ])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            if search_query:
                message += f"Найдено групп: {len(groups)}\n\n"
            message += "После выбора группы расписание будет показываться автоматически."
            
            if update.message:
                await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка при получении групп для выбора: {e}")
            error_message = "❌ *Произошла ошибка при получении списка групп.*\nПопробуйте позже."
            
            if update.message:
                await update.message.reply_text(error_message, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.edit_message_text(error_message, parse_mode='Markdown')
    
    async def show_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE, group: str, day: str):
        """Показать расписание для группы на указанный день"""
        try:
            # Определяем дату
            if day == 'tomorrow':
                date = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')
            else:
                date = datetime.now().strftime('%d.%m.%Y')
            
            # Получаем расписание
            schedule_data = schedule_parser.get_schedule(group, date)
            
            # Форматируем сообщение
            message = schedule_parser.format_schedule_message(schedule_data)
            
            # Создаем улучшенную клавиатуру навигации
            keyboard = [
                [
                    InlineKeyboardButton("📅 Сегодня", callback_data=f"schedule_{group}_today"),
                    InlineKeyboardButton("📆 Завтра", callback_data=f"schedule_{group}_tomorrow")
                ],
                [
                    InlineKeyboardButton("📋 Вся неделя", callback_data=f"schedule_{group}_week"),
                    InlineKeyboardButton("📆 Другой день", callback_data=f"schedule_{group}_other")
                ],
                [
                    InlineKeyboardButton("👥 Сменить группу", callback_data="select_group"),
                    InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Определяем, откуда пришел запрос (из сообщения или из callback)
            if update.message:
                await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка при показе расписания: {e}")
            error_message = "❌ *Произошла ошибка при загрузке расписания.*\nПопробуйте позже."
            
            if update.message:
                await update.message.reply_text(error_message, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.edit_message_text(error_message, parse_mode='Markdown')
    
    async def show_week_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE, group: str, start_date: str = None):
        """Показать расписание на неделю"""
        try:
            print(f"show_week_schedule вызван для группы: {group}, начальная дата: {start_date}")
            
            # Получаем недельное расписание
            week_data = schedule_parser.get_week_schedule(group, start_date)
            print(f"Получены данные недели: {len(week_data.get('week_schedule', []))} дней")
            
            # Форматируем сообщение
            message = schedule_parser.format_week_schedule_message(week_data)
            print(f"Сообщение отформатировано, длина: {len(message)}")
            
            # Создаем клавиатуру
            keyboard = [
                [
                    InlineKeyboardButton("📅 Сегодня", callback_data=f"schedule_{group}_today"),
                    InlineKeyboardButton("📆 Завтра", callback_data=f"schedule_{group}_tomorrow")
                ],
                [
                    InlineKeyboardButton("📋 Эта неделя", callback_data=f"schedule_{group}_week"),
                    InlineKeyboardButton("� След. неделя", callback_data=f"schedule_{group}_nextweek")
                ],
                [
                    InlineKeyboardButton("🌐 Открыть сайт", callback_data="open_website"),
                    InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            print("Отправляю сообщение...")
            
            # Отправляем сообщение без предварительного "Загружаю..."
            if update.message:
                await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            elif update.callback_query:
                await update.callback_query.edit_message_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            
            print("Сообщение отправлено успешно")
            
        except Exception as e:
            print(f"Ошибка в show_week_schedule: {e}")
            logger.error(f"Ошибка при показе недельного расписания: {e}")
            error_message = "❌ *Произошла ошибка при загрузке расписания на неделю.*\nПопробуйте позже."
            
            if update.message:
                await update.message.reply_text(error_message, parse_mode='Markdown')
            elif update.callback_query:
                await update.callback_query.edit_message_text(error_message, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # Отладочная информация
        print(f"Получен callback: {query.data}")
        
        # Обработка кнопок с параметрами (schedule_ГРУППА_ДЕЙСТВИЕ)
        if query.data.startswith("schedule_"):
            parts = query.data.split("_")
            print(f"Parts после split: {parts}")
            if len(parts) >= 3:
                # Группа может содержать символы, поэтому объединяем все части кроме последней
                action = parts[-1]  # Последняя часть - это действие
                group = "_".join(parts[1:-1])  # Все части между schedule и действием
                
                print(f"Group: {group}, Action: {action}")
                
                if action == "today":
                    await self.show_schedule(update, context, group, 'today')
                elif action == "tomorrow":
                    await self.show_schedule(update, context, group, 'tomorrow')
                elif action == "week":
                    print("Вызываю show_week_schedule")
                    await self.show_week_schedule(update, context, group)
                elif action == "nextweek":
                    print("Вызываю show_week_schedule для следующей недели")
                    # Получаем дату начала следующей недели
                    today = datetime.now()
                    days_until_monday = (7 - today.weekday()) % 7 or 7
                    next_monday = today + timedelta(days=days_until_monday)
                    next_week_start = next_monday.strftime('%d.%m.%Y')
                    await self.show_week_schedule(update, context, group, next_week_start)
                elif action == "other":
                    # Запрашиваем дату у пользователя
                    await query.edit_message_text(
                        "📆 *Введите дату в формате ДД.ММ.ГГГГ*\n\n"
                        "Например: 31.03.2026\n\n"
                        "💡 *Или введите 'завтра' для расписания на завтра*",
                        parse_mode='Markdown'
                    )
                    # Устанавливаем состояние ожидания даты
                    user_data[user_id]['waiting_date'] = group
                return
        
        # Старые обработчики для совместимости
        if query.data == "schedule_today":
            current_group = user_data.get(user_id, {}).get('group')
            if current_group:
                await self.show_schedule(update, context, current_group, 'today')
            else:
                await self.show_group_selection(update, context)
        
        elif query.data == "schedule_tomorrow":
            current_group = user_data.get(user_id, {}).get('group')
            if current_group:
                await self.show_schedule(update, context, current_group, 'tomorrow')
            else:
                await self.show_group_selection(update, context)
        
        elif query.data == "select_group":
            await self.show_group_selection(update, context)
        
        elif query.data == "search_group":
            await query.edit_message_text(
                "🔍 *Введите название группы для поиска:*\n\n"
                "Например: Ф22, М11, А21 и т.д.\n\n"
                "💡 *Вы можете вводить часть названия группы*",
                parse_mode='Markdown'
            )
            search_states[user_id] = True
        
        elif query.data == "new_search":
            await query.edit_message_text(
                "🔍 *Введите название группы для поиска:*\n\n"
                "Например: Ф22, М11, А21 и т.д.\n\n"
                "💡 *Вы можете вводить часть названия группы*",
                parse_mode='Markdown'
            )
        
        elif query.data == "show_all_groups":
            await self.show_group_selection(update, context)
        
        elif query.data == "show_groups":
            await self.groups_command(update, context)
        
        elif query.data.startswith("group_"):
            group = query.data[6:]  # Убираем префикс "group_"
            
            # Выходим из режима поиска
            search_states[user_id] = False
            
            # Сохраняем выбор группы
            if user_id not in user_data:
                user_data[user_id] = {}
            
            user_data[user_id]['group'] = group
            
            # Показываем расписание для выбранной группы
            await self.show_schedule(update, context, group, 'today')
            user_data[user_id]['group'] = group
            
            await query.edit_message_text(
                f"✅ *Группа {group} выбрана!*\n\n"
                f"Теперь расписание будет показываться для вашей группы.\n"
                f"Загружаю расписание...",
                parse_mode='Markdown'
            )
            
            # Показываем расписание на сегодня
            await self.show_schedule(update, context, group, 'today')
        
        elif query.data == "set_time":
            await query.edit_message_text(
                "🕐 *Установка времени рассылки*\n\n"
                "Отправьте время в формате ЧЧ:ММ\n\n"
                "💡 *Примеры:*\n"
                "• 07:00 - 7 утра\n"
                "• 08:30 - 8:30 утра\n"
                "• 18:00 - 6 вечера\n\n"
                "📝 *Используйте команду: /settime ЧЧ:ММ*",
                parse_mode='Markdown'
            )
        
        elif query.data == "open_website":
            await self.show_website(update, context)
        
        elif query.data == "back_to_menu":
            # Создаем новое сообщение для главного меню
            welcome_message = (
                "👋 *Добро пожаловать в бот расписания группы Ф22!*\n\n"
                "🎓 *Медицинский колледж - группа Ф22*\n\n"
                "📚 *Доступные команды:*\n"
                "• /raspis - Расписание на сегодня\n"
                "• /today - Расписание на сегодня\n"
                "• /tomorrow - Расписание на завтра\n"
                "• /week - Расписание на эту неделю\n"
                "• /nextweek - Расписание на следующую неделю\n"
                "• /open - Открыть веб-сайт\n"
                "• /settings - Настройки бота\n"
                "• /settime ЧЧ:ММ - Установить время рассылки\n"
                "• /help - Помощь\n\n"
                "💡 *Просто отправьте любое сообщение для расписания!*"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton("📅 Сегодня", callback_data="schedule_Ф22_today"),
                    InlineKeyboardButton("📆 Завтра", callback_data="schedule_Ф22_tomorrow")
                ],
                [
                    InlineKeyboardButton("📋 Эта неделя", callback_data="schedule_Ф22_week"),
                    InlineKeyboardButton("📋 След. неделя", callback_data="schedule_Ф22_nextweek")
                ],
                [
                    InlineKeyboardButton("🌐 Открыть сайт", callback_data="open_website")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
        
        # === ОБРАБОТКА АДМИНСКИХ КОЛБЭКОВ ===
        elif query.data.startswith("admin_"):
            # Проверяем, является ли пользователь админом
            if not self.is_admin(user_id):
                await query.answer("❌ Нет доступа!")
                return
            
            # Обрабатываем админские колбэки
            handled = await self.handle_admin_callback(update, context, query, query.data)
            if not handled:
                await query.answer("❌ Неизвестная команда")
    
    async def text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.strip()
        
        # Проверяем, ожидаем ли мы дату от пользователя
        user_id = update.effective_user.id
        if user_data.get(user_id, {}).get('waiting_date'):
            group = user_data[user_id]['waiting_date']
            del user_data[user_id]['waiting_date']  # Удаляем состояние ожидания
            
            # Обрабатываем ввод даты
            if text.lower() == 'завтра':
                date = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y')
            else:
                # Проверяем формат даты
                try:
                    datetime.strptime(text, '%d.%m.%Y')
                    date = text
                except ValueError:
                    await update.message.reply_text(
                        "❌ *Неверный формат даты.*\n\n"
                        "Пожалуйста, введите дату в формате ДД.ММ.ГГГГ\n"
                        "Например: 31.03.2026",
                        parse_mode='Markdown'
                    )
                    return
            
            # Получаем и показываем расписание
            await update.message.reply_text("🔄 *Загружаю расписание...*", parse_mode='Markdown')
            schedule_data = schedule_parser.get_schedule(group, date)
            message = schedule_parser.format_schedule_message(schedule_data)
            
            # Создаем клавиатуру
            keyboard = [
                [
                    InlineKeyboardButton("📅 Сегодня", callback_data=f"schedule_{group}_today"),
                    InlineKeyboardButton("📆 Завтра", callback_data=f"schedule_{group}_tomorrow")
                ],
                [
                    InlineKeyboardButton("📋 Вся неделя", callback_data=f"schedule_{group}_week"),
                    InlineKeyboardButton("📆 Другой день", callback_data=f"schedule_{group}_other")
                ],
                [
                    InlineKeyboardButton("🌐 Открыть сайт", callback_data="open_website"),
                    InlineKeyboardButton("🔙 Главное меню", callback_data="back_to_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(message, parse_mode='Markdown', reply_markup=reply_markup)
            return
        
        # === ОБРАБОТКА РАССЫЛКИ ДЛЯ АДМИНА ===
        # Проверяем, ожидает ли админ сообщение для рассылки
        is_broadcast = await self.handle_broadcast_message(update, context)
        if is_broadcast:
            return  # Сообщение обработано как рассылка
        
        # Для бота Ф22 - любое сообщение показывает расписание на сегодня
        await self.show_schedule(update, context, 'Ф22', 'today')
    
    async def send_daily_schedule(self):
        """Отправка ежедневного расписания всем пользователям"""
        if not user_data:
            return
        
        for user_id, data in user_data.items():
            try:
                group = data.get('group')
                if not group:
                    continue
                
                # Получаем расписание на сегодня
                schedule_data = schedule_parser.get_schedule(group, datetime.now().strftime('%d.%m.%Y'))
                message = schedule_parser.format_schedule_message(schedule_data)
                
                # Добавляем приветствие
                daily_message = f"☀️ *Доброе утро!*\n\n{message}"
                
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=daily_message,
                    parse_mode='Markdown'
                )
                
                logger.info(f"Отправлено ежедневное расписание пользователю {user_id}")
                
            except Exception as e:
                logger.error(f"Ошибка при отправке ежедневного расписания пользователю {user_id}: {e}")
    
    # ==================== АДМИН-ПАНЕЛЬ ====================
    
    def is_admin(self, user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        return user_id == ADMIN_ID
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /admin - вход в админ-панель"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ У вас нет доступа к админ-панели.")
            return
        
        # Логируем вход админа
        admin_logs.append(f"{datetime.now()}: Админ {user_id} вошел в панель")
        
        welcome_text = (
            "🔐 *АДМИН-ПАНЕЛЬ*\n\n"
            "👋 Добро пожаловать, администратор!\n\n"
            "📊 Доступные функции:\n"
            "• 📈 Статистика бота\n"
            "• 📢 Рассылка сообщений\n"
            "• ⏰ Управление временем рассылки\n"
            "• 📋 Просмотр логов\n"
            "• 🔄 Перезапуск бота\n"
            "• ⚙️ Настройки\n\n"
            "Выберите действие:"
        )
        
        # Создаем клавиатуру админ-панели
        keyboard = [
            [InlineKeyboardButton("📈 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⏰ Время рассылки", callback_data="admin_schedule_time")],
            [InlineKeyboardButton("📋 Логи", callback_data="admin_logs")],
            [InlineKeyboardButton("🔄 Перезапуск", callback_data="admin_restart")],
            [InlineKeyboardButton("🔙 Выйти", callback_data="admin_exit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats - статистика бота"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Нет доступа.")
            return
        
        stats = self.get_bot_stats()
        await update.message.reply_text(stats, parse_mode='Markdown')
    
    def get_bot_stats(self) -> str:
        """Получение статистики бота"""
        total_users = len(user_data)
        active_today = 0
        
        today = datetime.now().strftime('%d.%m.%Y')
        for user_id, data in user_data.items():
            last_activity = data.get('last_activity', '')
            if last_activity == today:
                active_today += 1
        
        stats = (
            "📊 *СТАТИСТИКА БОТА*\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"📱 Активны сегодня: {active_today}\n"
            f"📅 Текущая дата: {today}\n"
            f"⏰ Время рассылки: {BOT_SETTINGS['daily_schedule_time']}\n"
            f"✅ Рассылка включена: {'Да' if BOT_SETTINGS['enable_daily_schedule'] else 'Нет'}\n"
            f"📝 Логов админа: {len(admin_logs)}\n\n"
            "🔄 Обновлено: " + datetime.now().strftime('%H:%M:%S')
        )
        return stats
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /broadcast - рассылка сообщения всем пользователям"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Нет доступа.")
            return
        
        if not context.args:
            await update.message.reply_text(
                "📢 *Рассылка сообщений*\n\n"
                "Использование: /broadcast <текст сообщения>\n\n"
                f"Максимальная длина: {ADMIN_SETTINGS['max_broadcast_length']} символов\n"
                "Или нажмите кнопку ниже для ввода сообщения:",
                parse_mode='Markdown'
            )
            
            # Предлагаем ввести сообщение через кнопку
            keyboard = [[InlineKeyboardButton("✏️ Написать сообщение", callback_data="admin_broadcast_input")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text("Или выберите:", reply_markup=reply_markup)
            return
        
        # Получаем текст сообщения
        message_text = ' '.join(context.args)
        await self.send_broadcast(update, context, message_text)
    
    async def send_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Отправка рассылки всем пользователям"""
        if len(message_text) > ADMIN_SETTINGS['max_broadcast_length']:
            await update.message.reply_text(f"❌ Сообщение слишком длинное! Максимум {ADMIN_SETTINGS['max_broadcast_length']} символов.")
            return
        
        if not user_data:
            await update.message.reply_text("❌ Нет пользователей для рассылки.")
            return
        
        # Отправляем сообщение всем пользователям
        sent_count = 0
        failed_count = 0
        
        status_message = await update.message.reply_text("📤 Начинаю рассылку...")
        
        for user_id in user_data.keys():
            try:
                await self.application.bot.send_message(
                    chat_id=user_id,
                    text=f"📢 *Сообщение от администратора:*\n\n{message_text}",
                    parse_mode='Markdown'
                )
                sent_count += 1
                await asyncio.sleep(0.1)  # Небольшая задержка
            except Exception as e:
                failed_count += 1
                logger.error(f"Ошибка отправки рассылки пользователю {user_id}: {e}")
        
        # Логируем
        admin_logs.append(f"{datetime.now()}: Рассылка отправлена {sent_count} пользователям, ошибок: {failed_count}")
        
        result_text = (
            f"✅ *Рассылка завершена!*\n\n"
            f"📤 Отправлено: {sent_count}\n"
            f"❌ Ошибок: {failed_count}\n"
            f"👥 Всего пользователей: {len(user_data)}"
        )
        
        await status_message.edit_text(result_text, parse_mode='Markdown')
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /logs - просмотр логов бота"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Нет доступа.")
            return
        
        # Получаем последние логи
        lines = ADMIN_SETTINGS['log_lines_default']
        if context.args and context.args[0].isdigit():
            lines = min(int(context.args[0]), 100)  # Максимум 100 строк
        
        logs_text = self.get_recent_logs(lines)
        
        await update.message.reply_text(
            f"📋 *Последние {lines} действий администратора:*\n\n"
            f"```\n{logs_text[:3900]}\n```",
            parse_mode='Markdown'
        )
    
    def get_recent_logs(self, lines: int = 50) -> str:
        """Получение последних логов"""
        if not admin_logs:
            return "Логи пусты"
        
        recent_logs = admin_logs[-lines:]
        return '\n'.join(recent_logs)
    
    async def restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /restart - перезапуск бота"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text("❌ Нет доступа.")
            return
        
        await update.message.reply_text(
            "🔄 *Перезапуск бота...*\n\n"
            "Бот будет перезапущен через 3 секунды.",
            parse_mode='Markdown'
        )
        
        admin_logs.append(f"{datetime.now()}: Админ {user_id} перезапустил бота")
        
        # Перезапуск через asyncio
        asyncio.create_task(self.delayed_restart())
    
    async def delayed_restart(self):
        """Отложенный перезапуск"""
        await asyncio.sleep(3)
        # Останавливаем и запускаем бота заново
        try:
            self.application.stop()
            await asyncio.sleep(1)
            self.run()
        except Exception as e:
            logger.error(f"Ошибка при перезапуске: {e}")
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query, data):
        """Обработка колбэков админ-панели"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await query.answer("❌ Нет доступа!")
            return True
        
        if data == "admin_stats":
            stats = self.get_bot_stats()
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(stats, parse_mode='Markdown', reply_markup=reply_markup)
            
        elif data == "admin_broadcast":
            keyboard = [[InlineKeyboardButton("✏️ Написать сообщение", callback_data="admin_broadcast_input")],
                       [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📢 *Рассылка сообщений*\n\n"
                "Нажмите кнопку для ввода сообщения:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        elif data == "admin_broadcast_input":
            broadcast_states[user_id] = 'waiting_for_message'
            await query.edit_message_text(
                "✏️ *Введите текст сообщения для рассылки*\n\n"
                f"Максимальная длина: {ADMIN_SETTINGS['max_broadcast_length']} символов\n"
                "Отправьте сообщение следующим сообщением:",
                parse_mode='Markdown'
            )
            
        elif data == "admin_schedule_time":
            keyboard = [
                [InlineKeyboardButton("🕕 06:00", callback_data="admin_set_time_06:00"),
                 InlineKeyboardButton("🕗 08:00", callback_data="admin_set_time_08:00")],
                [InlineKeyboardButton("🕛 12:00", callback_data="admin_set_time_12:00"),
                 InlineKeyboardButton("🕕 18:00", callback_data="admin_set_time_18:00")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"⏰ *Текущее время рассылки: {BOT_SETTINGS['daily_schedule_time']}*\n\n"
                "Выберите новое время:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        elif data.startswith("admin_set_time_"):
            new_time = data.replace("admin_set_time_", "")
            self.update_scheduler_time(new_time)
            BOT_SETTINGS['daily_schedule_time'] = new_time
            await query.answer(f"✅ Время изменено на {new_time}")
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"✅ *Время рассылки изменено на {new_time}*",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            admin_logs.append(f"{datetime.now()}: Админ изменил время рассылки на {new_time}")
            
        elif data == "admin_logs":
            logs = self.get_recent_logs(20)
            keyboard = [
                [InlineKeyboardButton("📋 50 строк", callback_data="admin_logs_50"),
                 InlineKeyboardButton("📋 100 строк", callback_data="admin_logs_100")],
                [InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"📋 *Последние 20 действий:*\n\n```\n{logs[:3900]}\n```",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        elif data.startswith("admin_logs_"):
            lines = int(data.split("_")[2])
            logs = self.get_recent_logs(lines)
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="admin_back")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"📋 *Последние {lines} действий:*\n\n```\n{logs[:3900]}\n```",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        elif data == "admin_restart":
            keyboard = [
                [InlineKeyboardButton("✅ Да, перезапустить", callback_data="admin_restart_confirm")],
                [InlineKeyboardButton("❌ Отмена", callback_data="admin_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🔄 *Перезапуск бота*\n\n"
                "Вы уверены? Бот будет недоступен 5-10 секунд.",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        elif data == "admin_restart_confirm":
            await query.edit_message_text("🔄 *Перезапуск...*", parse_mode='Markdown')
            admin_logs.append(f"{datetime.now()}: Админ {user_id} перезапустил бота через кнопку")
            asyncio.create_task(self.delayed_restart())
            
        elif data == "admin_exit":
            await query.edit_message_text("👋 *Админ-панель закрыта*", parse_mode='Markdown')
            
        elif data == "admin_back":
            # Возвращаемся в главное меню админки
            await self.admin_menu(query)
            
        else:
            return False
            
        return True
    
    async def admin_menu(self, query):
        """Показать главное меню админ-панели"""
        welcome_text = (
            "🔐 *АДМИН-ПАНЕЛЬ*\n\n"
            "👋 Добро пожаловать, администратор!\n\n"
            "📊 Доступные функции:\n"
            "• 📈 Статистика бота\n"
            "• 📢 Рассылка сообщений\n"
            "• ⏰ Управление временем рассылки\n"
            "• 📋 Просмотр логов\n"
            "• 🔄 Перезапуск бота\n\n"
            "Выберите действие:"
        )
        
        keyboard = [
            [InlineKeyboardButton("📈 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⏰ Время рассылки", callback_data="admin_schedule_time")],
            [InlineKeyboardButton("📋 Логи", callback_data="admin_logs")],
            [InlineKeyboardButton("🔄 Перезапуск", callback_data="admin_restart")],
            [InlineKeyboardButton("🔙 Выйти", callback_data="admin_exit")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def handle_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка сообщения для рассылки"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            return False
        
        if broadcast_states.get(user_id) == 'waiting_for_message':
            message_text = update.message.text
            broadcast_states[user_id] = None  # Сбрасываем состояние
            
            await self.send_broadcast(update, context, message_text)
            return True
        
        return False
    
    def run(self):
        """Запуск бота"""
        self.scheduler.start()
        logger.info("Бот запущен")
        self.application.run_polling()

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        print("Ошибка: TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
        print("Пожалуйста, создайте файл .env и добавьте токен бота.")
    else:
        bot = TelegramBot()
        bot.run()
