#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота в продакшене
"""

import sys
import os
import logging
from pathlib import Path

# Добавляем текущую директорию в Python path
sys.path.append(str(Path(__file__).parent))

from bot import TelegramBot

def main():
    """Основная функция для запуска бота"""
    
    # Настройка логирования
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger(__name__)
    logger.info("Запуск Telegram бота расписания...")
    
    try:
        # Проверяем наличие токена
        from config import TELEGRAM_BOT_TOKEN
        if not TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")
            print("❌ Ошибка: TELEGRAM_BOT_TOKEN не найден!")
            print("Пожалуйста, создайте файл .env и добавьте токен бота:")
            print("TELEGRAM_BOT_TOKEN=your_token_here")
            sys.exit(1)
        
        # Создаем и запускаем бота
        bot = TelegramBot()
        logger.info("Бот успешно запущен и готов к работе!")
        print("🤖 Бот запущен! Нажмите Ctrl+C для остановки.")
        
        # Запускаем бота
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        print("\n👋 Бот остановлен.")
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
