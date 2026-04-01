import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class ScheduleParser:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        self.demo_mode = False  # Выключаем демо-режим для реальной работы
    
    def get_groups(self) -> List[str]:
        """Получить список групп (только Ф22 для специализированного бота)"""
        return ['Ф22']
    
    def get_schedule(self, group: str = None, date: str = None) -> Dict:
        """Получить расписание для группы на указанную дату"""
        try:
            # Если демо-режим, возвращаем тестовые данные
            if self.demo_mode:
                return self._get_demo_schedule(group, date)
            
            # Реальный парсинг сайта
            return self._parse_real_schedule(group, date)
            
        except Exception as e:
            return {
                'group': group,
                'date': date or datetime.now().strftime('%d.%m.%Y'),
                'lessons': [],
                'real': False,
                'error': str(e),
                'update_time': datetime.now().strftime('%H:%M:%S')
            }
    
    def _get_group_schedule(self, group: str, date: str = None) -> Dict:
        """Получить расписание для конкретной группы через AJAX"""
        try:
            # Локальные ID групп
            group_dict = {
                'Ф22': '148663', 'М11': '80983', 'А11': '80962',
                'Ф21': '148662', 'Ф11': '81042', 'Ф12': '81043',
                'М21': '80993', 'М22': '80994', 'А21': '80964', 'А22': '80965'
            }
            
            group_id = group_dict.get(group)
            if not group_id:
                return {
                    'group': group,
                    'date': date or datetime.now().strftime('%d.%m.%Y'),
                    'lessons': [],
                    'error': f'Группа {group} не найдена'
                }
            
            # Настраиваем сессию для AJAX запроса
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'Referer': 'https://raspisanie.medcoll.ru/students/',
                'Connection': 'keep-alive'
            })
            
            # Сначала получаем главную страницу для cookies
            session.get('https://raspisanie.medcoll.ru/students/')
            
            # Отправляем AJAX запрос
            url = 'https://raspisanie.medcoll.ru/students/'
            params = {
                'group': group_id,
                'date_edu1c': date or datetime.now().strftime('%d.%m.%Y'),
                'ajax': '1'
            }
            
            response = session.get(url, params=params)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                return {
                    'group': group,
                    'date': date or datetime.now().strftime('%d.%m.%Y'),
                    'lessons': [],
                    'error': f'Ошибка сервера: {response.status_code}'
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            lessons = []
            
            # Ищем расписание в контейнере raspcontent
            raspcontent = soup.find('div', {'name': 'raspcontent'})
            if raspcontent:
                # Ищем все таблицы с расписанием
                tables = raspcontent.find_all('table', class_='table')
                
                for table in tables:
                    # Ищем заголовок с датой
                    panel = table.find_parent('div', class_='panel-body')
                    date_heading = None
                    if panel:
                        heading = panel.find_previous('h2')
                        if heading:
                            date_heading = heading.get_text(strip=True)
                    
                    # Парсим строки таблицы
                    rows = table.find('tbody').find_all('tr') if table.find('tbody') else table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 5:  # Номер пары, время, дисциплина, аудитория, преподаватель
                            try:
                                pair_number = cells[0].get_text(strip=True)
                                time_text = cells[1].get_text(strip=True)
                                subject = cells[2].get_text(strip=True)
                                classroom = cells[3].get_text(strip=True)
                                teacher = cells[4].get_text(strip=True)
                                
                                # Пропускаем заголовки
                                if (pair_number.isdigit() or 
                                    any(keyword in subject.lower() for keyword in ['мдк', 'основы', 'психология', 'здоровый'])):
                                    
                                    lessons.append({
                                        'time': time_text,
                                        'subject': subject,
                                        'teacher': teacher,
                                        'classroom': classroom,
                                        'pair_number': pair_number,
                                        'date_heading': date_heading
                                    })
                            except Exception as e:
                                continue  # Пропускаем некорректные строки
            
            # Фильтруем занятия на конкретную дату
            target_date = date or datetime.now().strftime('%d.%m.%Y')
            filtered_lessons = []
            
            for lesson in lessons:
                lesson_date = self._extract_date_from_heading(lesson.get('date_heading', ''), target_date)
                if lesson_date == target_date:
                    filtered_lessons.append(lesson)
            
            # Если не удалось отфильтровать по дате, берем все занятия
            if not filtered_lessons and lessons:
                filtered_lessons = lessons[:10]  # Ограничиваем количество
            
            return {
                'group': group,
                'date': target_date,
                'lessons': filtered_lessons,
                'update_time': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                'real': True  # Флаг, что это реальные данные
            }
            
        except Exception as e:
            print(f"Ошибка при получении расписания для группы {group}: {e}")
            return {
                'group': group,
                'date': date or datetime.now().strftime('%d.%m.%Y'),
                'lessons': [],
                'error': str(e)
            }
    
    def _extract_date_from_heading(self, heading: str, target_date: str) -> str:
        """Извлекает дату из заголовка дня"""
        try:
            # Ищем дату в формате "31 марта 2026, вторник"
            import re
            date_pattern = r'(\d{1,2})\s+(\w+)\s+(\d{4})'
            match = re.search(date_pattern, heading)
            
            if match:
                day, month, year = match.groups()
                month_map = {
                    'января': '01', 'февраля': '02', 'марта': '03', 'апреля': '04',
                    'мая': '05', 'июня': '06', 'июля': '07', 'августа': '08',
                    'сентября': '09', 'октября': '10', 'ноября': '11', 'декабря': '12'
                }
                
                month_num = month_map.get(month.lower())
                if month_num:
                    extracted_date = f"{day.zfill(2)}.{month_num}.{year}"
                    return extracted_date
            
            return target_date
        except:
            return target_date
    
    def get_week_schedule(self, group: str, start_date: str = None) -> Dict:
        """Получить расписание на неделю"""
        try:
            if not start_date:
                start_date = datetime.now().strftime('%d.%m.%Y')
            
            # Получаем дату начала недели
            start_dt = datetime.strptime(start_date, '%d.%m.%Y')
            day_of_week = start_dt.weekday()
            
            # Находим понедельник
            monday = start_dt - timedelta(days=day_of_week)
            
            week_schedule = []
            all_lessons = []
            
            # Получаем расписание на каждый день недели
            for i in range(7):  # Понедельник - Воскресенье
                current_date = monday + timedelta(days=i)
                date_str = current_date.strftime('%d.%m.%Y')
                
                daily_schedule = self.get_schedule(group, date_str)
                daily_lessons = daily_schedule.get('lessons', [])
                
                day_name = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'][i]
                
                week_schedule.append({
                    'date': date_str,
                    'day_name': day_name,
                    'lessons': daily_lessons,
                    'has_lessons': len(daily_lessons) > 0
                })
                
                all_lessons.extend(daily_lessons)
            
            return {
                'group': group,
                'week_start': monday.strftime('%d.%m.%Y'),
                'week_end': (monday + timedelta(days=6)).strftime('%d.%m.%Y'),
                'week_schedule': week_schedule,
                'total_lessons': len(all_lessons),
                'update_time': datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                'real': True
            }
            
        except Exception as e:
            print(f"Ошибка при получении недельного расписания: {e}")
            return {
                'group': group,
                'week_schedule': [],
                'error': str(e)
            }
    
    def format_week_schedule_message(self, week_data: Dict) -> str:
        """Форматирует недельное расписание"""
        try:
            group = week_data.get('group', 'Не указана')
            week_start = week_data.get('week_start', '')
            week_end = week_data.get('week_end', '')
            week_schedule = week_data.get('week_schedule', [])
            total_lessons = week_data.get('total_lessons', 0)
            update_time = week_data.get('update_time', '')
            
            # Заголовок
            message = f"📚 *Расписание группы {group} на неделю*\n"
            message += f"📅 *{week_start} - {week_end}*\n"
            message += "✅ _Актуальное расписание с сайта_\n\n"
            
            if total_lessons == 0:
                message += "📝 *На неделе занятий не запланировано*\n"
            else:
                message += f"📋 *Всего занятий: {total_lessons}*\n\n"
                
                for day_data in week_schedule:
                    date = day_data['date']
                    day_name = day_data['day_name']
                    lessons = day_data['lessons']
                    
                    # Воскресенье - всегда выходной
                    if day_name == 'Воскресенье':
                        message += f"🎉 *{day_name} ({date})* - Выходной день\n\n"
                        continue
                    
                    message += f"📅 *{day_name} ({date})*\n"
                    
                    if not lessons:
                        # Проверяем, это выходной или просто нет занятий
                        day_dt = datetime.strptime(date, '%d.%m.%Y')
                        if day_dt.weekday() >= 5:  # Суббота
                            message += "🎉 _Выходной день_\n\n"
                        else:
                            message += "   📝 Занятий нет\n\n"
                    else:
                        for lesson in lessons:
                            time = lesson.get('time', 'Не указано')
                            subject = lesson.get('subject', 'Не указано')
                            teacher = lesson.get('teacher', 'Не указано')
                            classroom = lesson.get('classroom', 'Не указано')
                            pair_number = lesson.get('pair_number', '')
                            
                            message += f"   🔹 Пара {pair_number} • {time}\n"
                            message += f"   📖 {subject}\n"
                            message += f"   🏫 {classroom}\n\n"
                    
                    message += "\n"
            
            # Добавляем информацию об обновлении
            if update_time:
                message += f"🔄 _Обновлено: {update_time}_\n"
            
            message += "\n💡 _Расписание получено с официального сайта колледжа_"
            message += "\n🎉 _Воскресенье - выходной день_"
            
            return message
            
        except Exception as e:
            return f"❌ Ошибка при форматировании недельного расписания: {e}"
        """Получить ID группы по ее названию"""
        try:
            response = self.session.get('https://raspisanie.medcoll.ru/students/')
            response.encoding = 'utf-8'
            content = response.text
            
            # Ищем pattern <option value="ID">GROUP_NAME</option>
            import re
            options = re.findall(r'<option value="(\d+)">' + re.escape(group_name) + r'</option>', content)
            
            if options:
                return options[0]
            
            return None
            
        except Exception as e:
            print(f"Ошибка при получении ID группы {group_name}: {e}")
            return None
    
    def _parse_lesson_row(self, cells) -> Optional[Dict]:
        """Парсит строку с информацией о занятии"""
        try:
            # Ожидаемая структура: время, предмет, преподаватель, аудитория
            if len(cells) < 3:
                return None
            
            time_text = cells[0].get_text(strip=True) if len(cells) > 0 else 'Не указано'
            subject_text = cells[1].get_text(strip=True) if len(cells) > 1 else 'Не указано'
            teacher_text = cells[2].get_text(strip=True) if len(cells) > 2 else 'Не указано'
            classroom_text = cells[3].get_text(strip=True) if len(cells) > 3 else 'Не указано'
            
            # Фильтруем пустые значения
            if not subject_text or subject_text.lower() in ['-', '—', '']:
                return None
            
            return {
                'time': time_text,
                'subject': subject_text,
                'teacher': teacher_text,
                'classroom': classroom_text
            }
            
        except Exception as e:
            print(f"Ошибка при парсинге строки занятия: {e}")
            return None
    
    def search_groups(self, query: str) -> List[str]:
        """Поиск групп по запросу"""
        try:
            groups = self.get_groups()
            if not query:
                return groups[:20]  # Возвращаем первые 20 групп если запрос пустой
            
            query_lower = query.lower()
            filtered_groups = []
            
            for group in groups:
                group_lower = group.lower()
                # Ищем точное совпадение или вхождение
                if (query_lower in group_lower or 
                    group_lower in query_lower or
                    self._fuzzy_match(query_lower, group_lower)):
                    filtered_groups.append(group)
            
            # Сортируем по релевантности (точные совпадения сначала)
            filtered_groups.sort(key=lambda x: (
                0 if x.lower() == query_lower else  # Точное совпадение
                1 if x.lower().startswith(query_lower) else  # Начинается с запроса
                2 if query_lower in x.lower() else  # Содержит запрос
                3  # Нечеткое совпадение
            ))
            
            return filtered_groups[:20]  # Ограничиваем результат
            
        except Exception as e:
            print(f"Ошибка при поиске групп: {e}")
            return []
    
    def _fuzzy_match(self, query: str, group: str) -> bool:
        """Простой нечеткий поиск"""
        # Проверяем совпадение по отдельным символам
        query_chars = set(query.replace(' ', ''))
        group_chars = set(group.replace(' ', ''))
        
        # Если хотя бы 60% символов запроса есть в названии группы
        if len(query_chars) > 0:
            intersection = len(query_chars.intersection(group_chars))
            similarity = intersection / len(query_chars)
            return similarity >= 0.6
        
        return False
    
    def format_schedule_message(self, schedule_data: Dict) -> str:
        """Форматирует расписание в красивое сообщение"""
        try:
            group = schedule_data.get('group', 'Не указана')
            date = schedule_data.get('date', datetime.now().strftime('%d.%m.%Y'))
            lessons = schedule_data.get('lessons', [])
            update_time = schedule_data.get('update_time', '')
            is_real = schedule_data.get('real', False)
            is_demo = schedule_data.get('demo', False)
            
            # Заголовок
            message = f"📚 *Расписание группы {group}*\n"
            message += f"📅 *Дата: {date}*\n"
            
            # Добавляем уведомление о типе данных
            if is_real:
                message += "✅ _Актуальное расписание с сайта_\n\n"
            elif is_demo:
                message += "⚠️ _Демонстрационный режим_\n\n"
            
            if not lessons:
                day_of_week = datetime.strptime(date, '%d.%m.%Y').weekday()
                if day_of_week >= 5:  # Суббота, Воскресенье
                    message += "🎉 *Выходной день!*\n\n"
                else:
                    message += "📝 *Занятий не запланировано*\n\n"
            else:
                message += "📋 *Занятия:*\n\n"
                
                for i, lesson in enumerate(lessons, 1):
                    time = lesson.get('time', 'Не указано')
                    subject = lesson.get('subject', 'Не указано')
                    teacher = lesson.get('teacher', 'Не указано')
                    classroom = lesson.get('classroom', 'Не указано')
                    pair_number = lesson.get('pair_number', str(i))
                    
                    message += f"🔹 *Пара {pair_number}*\n"
                    message += f"⏰ {time}\n"
                    message += f"📖 {subject}\n"
                    message += f"👨‍🏫 {teacher}\n"
                    message += f"🏫 {classroom}\n\n"
            
            # Добавляем информацию об обновлении
            if update_time:
                message += f"🔄 _Обновлено: {update_time}_\n"
            
            # Добавляем подсказку
            if is_real:
                message += "\n💡 _Расписание получено с официального сайта колледжа_"
            elif is_demo:
                message += "\n💡 _Это демо-версия расписания. В реальной версии здесь будет актуальное расписание с сайта._"
            
            return message
            
        except Exception as e:
            return f"❌ Ошибка при форматировании расписания: {e}"
    
    def _get_demo_schedule(self, group: str, date: str) -> Dict:
        """Демо-расписание для тестирования"""
        current_date = datetime.strptime(date or datetime.now().strftime('%d.%m.%Y'), '%d.%m.%Y')
        day_of_week = current_date.weekday()
        
        # Демо-данные для разных дней
        demo_lessons = {
            0: [  # Понедельник
                {'time': '08:30', 'subject': 'Анатомия и физиология', 'teacher': 'Иванова И.И.', 'classroom': '201'},
                {'time': '10:15', 'subject': 'Основы патологии', 'teacher': 'Петров П.П.', 'classroom': '305'},
                {'time': '12:00', 'subject': 'Фармакология', 'teacher': 'Сидорова С.С.', 'classroom': '102'}
            ],
            1: [  # Вторник
                {'time': '08:30', 'subject': 'Латинский язык', 'teacher': 'Козлов К.К.', 'classroom': '203'},
                {'time': '10:15', 'subject': 'Психология', 'teacher': 'Михайлова М.М.', 'classroom': '301'}
            ],
            2: [  # Среда
                {'time': '08:30', 'subject': 'Хирургия', 'teacher': 'Николаев Н.Н.', 'classroom': '401'},
                {'time': '10:15', 'subject': 'Терапия', 'teacher': 'Алексеев А.А.', 'classroom': '205'},
                {'time': '12:00', 'subject': 'Педиатрия', 'teacher': 'Васильева В.В.', 'classroom': '103'}
            ],
            3: [  # Четверг
                {'time': '08:30', 'subject': 'Акушерство', 'teacher': 'Зайцева З.З.', 'classroom': '302'},
                {'time': '10:15', 'subject': 'Гигиена', 'teacher': 'Федоров Ф.Ф.', 'classroom': '204'}
            ],
            4: [  # Пятница
                {'time': '08:30', 'subject': 'Реаниматология', 'teacher': 'Сергеев С.С.', 'classroom': '401'},
                {'time': '10:15', 'subject': 'Стоматология', 'teacher': 'Орлова О.О.', 'classroom': '303'},
                {'time': '12:00', 'subject': 'Офтальмология', 'teacher': 'Павлова П.П.', 'classroom': '105'}
            ],
            5: [],  # Суббота
            6: []   # Воскресенье
        }
        
        return {
            'group': group,
            'date': current_date.strftime('%d.%m.%Y'),
            'lessons': demo_lessons.get(day_of_week, []),
            'real': False,
            'demo': True,
            'update_time': datetime.now().strftime('%H:%M:%S')
        }
    
    def _parse_real_schedule(self, group: str, date: str) -> Dict:
        """Парсинг реального расписания с сайта колледжа по конкретному дню"""
        try:
            # ID группы Ф22
            group_id = '148663'
            
            # Формируем URL с параметрами
            if not date:
                date = datetime.now().strftime('%d.%m.%Y')
            
            # Определяем день недели
            date_obj = datetime.strptime(date, '%d.%m.%Y')
            day_of_week = date_obj.weekday()
            day_names = ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота', 'воскресенье']
            target_day_name = day_names[day_of_week]
            
            # Воскресенье - выходной
            if day_of_week == 6:
                return {
                    'group': group,
                    'date': date,
                    'lessons': [],
                    'real': True,
                    'demo': False,
                    'update_time': datetime.now().strftime('%H:%M:%S'),
                    'message': 'Воскресенье - выходной день'
                }
            
            base_url = "https://raspisanie.medcoll.ru/students/"
            params = {
                'group': group_id,
                'date_edu1c': date,
                'send': 'Показать'
            }
            
            print(f"Парсинг расписания для группы {group} на дату {date} ({target_day_name})")
            
            # Делаем запрос
            response = self.session.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            print(f"Статус: {response.status_code}, Размер HTML: {len(response.text)} символов")
            
            # Находим все таблицы
            tables = soup.find_all('table')
            print(f"Найдено таблиц: {len(tables)}")
            
            # Словарь: день -> список пар
            schedule_by_day = {}
            
            for table in tables:
                # Находим предыдущий ЗАГОЛОВОК (только h2, h3, h4) перед таблицей
                # Пропускаем div, p и другие теги
                prev_heading = table.find_previous(['h2', 'h3', 'h4'])
                
                if prev_heading:
                    heading_text = prev_heading.get_text(strip=True).lower()
                    print(f"\nЗаголовок перед таблицей: {heading_text[:80]}")
                    
                    # Определяем какому дню принадлежит таблица
                    day_key = None
                    for day_name in day_names:
                        if day_name in heading_text:
                            day_key = day_name
                            print(f"  ✓ Определен день: {day_key}")
                            break
                    
                    if day_key:
                        # Парсим пары из таблицы
                        day_lessons = []
                        rows = table.find_all('tr')
                        print(f"  Таблица: {len(rows)} строк")
                        
                        for row in rows:
                            cells = row.find_all(['td', 'th'])
                            
                            # Пропускаем заголовки таблицы (первая ячейка - текст, не число)
                            if len(cells) >= 4:
                                pair_num = cells[0].get_text(strip=True)
                                
                                # Проверяем что это номер пары (число), а не заголовок
                                if pair_num.isdigit():
                                    time_text = cells[1].get_text(strip=True)
                                    subject_text = cells[2].get_text(strip=True)
                                    room_teacher = cells[3].get_text(strip=True)
                                    
                                    # Проверяем что время содержит двоеточие
                                    if ':' in time_text:
                                        # Очищаем предмет
                                        subject_clean = subject_text.strip().replace('\n', ' ')
                                        
                                        # Убираем лишние пробелы
                                        while '  ' in subject_clean:
                                            subject_clean = subject_clean.replace('  ', ' ')
                                        
                                        if subject_clean and subject_clean != 'Дисциплина' and len(subject_clean) > 3:
                                            lesson = {
                                                'time': time_text,
                                                'subject': subject_clean,
                                                'teacher': room_teacher if any(c.isalpha() for c in room_teacher) else '',
                                                'classroom': room_teacher
                                            }
                                            day_lessons.append(lesson)
                                            print(f"    ✓ Пара {pair_num}: {time_text} - {subject_clean[:40]}")
                        
                        # Сохраняем пары для этого дня
                        if day_key and day_lessons:
                            if day_key not in schedule_by_day:
                                schedule_by_day[day_key] = []
                            schedule_by_day[day_key].extend(day_lessons)
                            print(f"  Сохранено {len(day_lessons)} пар для {day_key}")
            
            # Выводим что нашли
            print(f"\n=== НАЙДЕНО РАСПИСАНИЙ ===")
            for day, lessons in schedule_by_day.items():
                print(f"{day}: {len(lessons)} пар")
            
            # Берем пары для нужного дня
            target_lessons = schedule_by_day.get(target_day_name, [])
            
            print(f"\n=== ИТОГО ===")
            print(f"Найдено пар на {target_day_name}: {len(target_lessons)}")
            
            return {
                'group': group,
                'date': date,
                'day_name': target_day_name.capitalize(),
                'lessons': target_lessons,
                'real': True,
                'demo': False,
                'update_time': datetime.now().strftime('%H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Ошибка парсинга: {e}")
            return self._get_demo_schedule(group, date)
