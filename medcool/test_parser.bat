@echo off
echo Тестирование парсера...
cd /d c:\Users\1\Desktop\medcool
call .venv\Scripts\activate
python test_parser.py
pause
