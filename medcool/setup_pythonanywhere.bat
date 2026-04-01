@echo off
chcp 65001 >nul
echo ============================================
echo   🚀 УСТАНОВКА НА PYTHONANYWHERE
echo ============================================
echo.
echo Этот скрипт поможет развернуть бота на PythonAnywhere
echo.
echo 📋 Шаги:
echo.
echo 1. Создайте аккаунт на https://www.pythonanywhere.com/
echo 2. Откройте Bash консоль на сайте
echo 3. Выполните команды из файла DEPLOY_PYTHONANYWHERE.md
echo.
echo 📁 Файлы для загрузки:
echo   • bot.py
echo   • schedule_parser.py
echo   • config.py
echo   • requirements.txt
echo   • .env
echo   • run.py
echo   • site/ (папка с копией сайта)
echo.
echo 🔗 GitHub (рекомендуется):
echo   1. Загрузите проект на GitHub
echo   2. Клонируйте через git clone на PythonAnywhere
echo   3. Установите зависимости: pip install -r requirements.txt
echo   4. Создайте Always-on task
echo.
echo ⚠️ Важно: Замените ВАШ_USERNAME в инструкциях!
echo.
echo 📖 Полная инструкция в файле: DEPLOY_PYTHONANYWHERE.md
echo.
pause
