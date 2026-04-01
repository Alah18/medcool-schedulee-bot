#!/usr/bin/env python3
"""
Тест реального парсинга с сайта
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from schedule_parser import ScheduleParser

def test_real_parsing():
    """Тест реального парсинга"""
    try:
        print("=== ТЕСТ РЕАЛЬНОГО ПАРСИНГА ===")
        
        # Создаем парсер
        parser = ScheduleParser()
        
        # Тестируем для группы Ф22 на сегодня
        from datetime import datetime
        today = datetime.now().strftime('%d.%m.%Y')
        
        print(f"\nТестируем расписание для группы Ф22 на {today}")
        
        # Получаем расписание
        schedule = parser.get_schedule('Ф22', today)
        
        print(f"\nРезультат:")
        print(f"Группа: {schedule.get('group')}")
        print(f"Дата: {schedule.get('date')}")
        print(f"Реальное: {schedule.get('real')}")
        print(f"Демо: {schedule.get('demo')}")
        print(f"Ошибок: {schedule.get('error')}")
        
        lessons = schedule.get('lessons', [])
        print(f"\nНайдено пар: {len(lessons)}")
        
        for i, lesson in enumerate(lessons):
            print(f"{i+1}. {lesson.get('time')} - {lesson.get('subject')}")
            if lesson.get('teacher'):
                print(f"   Преподаватель: {lesson.get('teacher')}")
            if lesson.get('classroom'):
                print(f"   Кабинет: {lesson.get('classroom')}")
        
        if not lessons:
            print("\nПары не найдены!")
        
    except Exception as e:
        print(f"Ошибка теста: {e}")

if __name__ == "__main__":
    test_real_parsing()
