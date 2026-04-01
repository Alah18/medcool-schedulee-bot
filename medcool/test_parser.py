#!/usr/bin/env python3
"""
Улучшенный тестовый парсер для проверки структуры HTML
"""

import os
import re
from bs4 import BeautifulSoup

def test_html_structure():
    """Проверяем структуру HTML файла и ищем расписание"""
    try:
        # Путь к локальной копии сайта
        site_path = os.path.join(os.path.dirname(__file__), 'site', 'My_Archive_Site', 'raspisanie.medcoll.ru')
        index_path = os.path.join(site_path, 'index.html')
        
        print(f"Путь к файлу: {index_path}")
        print(f"Файл существует: {os.path.exists(index_path)}")
        
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            print(f"Размер HTML: {len(html_content)} символов")
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Метод 1: Ищем таблицы
            print("\n=== МЕТОД 1: ПОИСК ТАБЛИЦ ===")
            tables = soup.find_all('table')
            print(f"Найдено таблиц: {len(tables)}")
            
            for i, table in enumerate(tables):
                print(f"\nТаблица {i+1}:")
                rows = table.find_all('tr')
                for j, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        print(f"  Строка {j+1}: {cell_texts}")
            
            # Метод 2: Ищем все тексты с временем
            print("\n=== МЕТОД 2: ПОИСК ТЕКСТА С ВРЕМЕНЕМ ===")
            all_text = soup.get_text()
            lines = [line.strip() for line in all_text.split('\n') if line.strip()]
            
            time_pattern = re.compile(r'\b(08:30|09:15|10:15|11:00|12:00|12:45|13:30|14:15|15:00|15:45|16:30)\b')
            
            for i, line in enumerate(lines):
                if time_pattern.search(line):
                    print(f"Строка {i}: {line}")
                    # Показываем следующие строки
                    for j in range(1, 4):
                        if i+j < len(lines):
                            next_line = lines[i+j]
                            if next_line and next_line not in ['-', '—', '']:
                                print(f"  Следующая строка {i+j}: {next_line}")
            
            # Метод 3: Ищем по ключевым словам
            print("\n=== МЕТОД 3: ПОИСК КЛЮЧЕВЫХ СЛОВ ===")
            subject_keywords = ['анатом', 'физиолог', 'патолог', 'фармаколог', 'хирург', 'терап', 'педиатр', 'акушер', 'гигиен', 'стоматолог', 'офтальмолог', 'латин', 'психолог']
            
            for keyword in subject_keywords:
                elements = soup.find_all(text=re.compile(keyword, re.IGNORECASE))
                if elements:
                    print(f"\nНайдено ключевое слово '{keyword}':")
                    for elem in elements[:3]:  # Показываем первые 3
                        parent = elem.parent
                        if parent:
                            text = parent.get_text(strip=True)
                            # Ищем время рядом
                            time_match = re.search(r'(\d{1,2}:\d{2})', text)
                            if time_match:
                                print(f"  С временем: {time_match.group(1)} - {text[:100]}")
                            else:
                                print(f"  Без времени: {text[:100]}")
                    
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    test_html_structure()
