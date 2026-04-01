@echo off
echo Тестирование реального парсинга с сайта...
cd /d c:\Users\1\Desktop\medcool
call .venv\Scripts\activate
python test_real_parser.py
pause
