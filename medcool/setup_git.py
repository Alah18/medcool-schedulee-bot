#!/usr/bin/env python3
"""
Скрипт для инициализации Git репозитория и первого коммита
"""

import os
import subprocess
from datetime import datetime

def run_command(command, description):
    """Выполнение команды с выводом"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} выполнено успешно")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при {description}: {e}")
        return None

def setup_git():
    """Настройка Git репозитория"""
    
    print("🚀 Начинаю настройку Git репозитория...")
    
    # Инициализация Git
    run_command("git init", "Инициализация Git репозитория")
    
    # Добавление файлов
    run_command("git add .", "Добавление файлов в Git")
    
    # Первый коммит
    commit_message = f"Initial commit - Медицинский колледж бот расписания Ф22\n\n🎓 Telegram бот + Веб-сайт\n⏰ Ежедневная рассылка\n📅 Расписание на день/неделю/следующую неделю\n🌐 Веб-интерфейс\n⚙️ Настраиваемое время"
    
    run_command(f'git commit -m "{commit_message}"', "Создание первого коммита")
    
    # Информация о следующих шагах
    print("\n" + "="*50)
    print("🎉 Git репозиторий настроен успешно!")
    print("="*50)
    print("\n📋 Следующие шаги:")
    print("1. Создайте репозиторий на GitHub:")
    print("   https://github.com/new")
    print("\n2. Добавьте remote:")
    print("   git remote add origin https://github.com/yourusername/medcool-schedule-bot.git")
    print("\n3. Отправьте на GitHub:")
    print("   git push -u origin main")
    print("\n4. Настройте хостинг по инструкции DEPLOYMENT.md")
    print("="*50)
    
    # Проверка статуса
    run_command("git status", "Проверка статуса Git")

if __name__ == "__main__":
    setup_git()
