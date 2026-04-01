@echo off
chcp 65001 >nul
echo ============================================
echo   🚀 ЗАГРУЗКА НА GITHUB
echo ============================================
echo.
echo 📋 Шаги для загрузки на GitHub:
echo.
echo 1. Создайте репозиторий на https://github.com/new
echo    Название: medcool-schedule-bot
echo    Описание: Telegram бот расписания для группы Ф22
echo.
echo 2. НЕ добавляйте README, .gitignore, license (они уже есть)
echo.
echo 3. Запустите эти команды в терминале (PowerShell):
echo.
echo    cd c:\Users\1\Desktop\medcool
echo    git init
echo    git add .
echo    git commit -m "Initial commit"
echo    git branch -M main
echo    git remote add origin https://github.com/ВАШ_ЛОГИН/medcool-schedule-bot.git
echo    git push -u origin main
echo.
echo ⚠️ ВАЖНО: Замените ВАШ_ЛОГИН на ваш GitHub логин!
echo.
echo 🔐 Безопасность:
echo   - Файл .env НЕ будет загружен (защищен в .gitignore)
echo   - Токен бота останется в секрете
.
echo 📦 Будут загружены:
echo   ✅ bot.py
echo   ✅ schedule_parser.py
echo   ✅ config.py
echo   ✅ run.py
echo   ✅ requirements.txt
echo   ✅ README_GITHUB.md (переименуйте в README.md)
echo   ✅ DEPLOY_PYTHONANYWHERE.md
echo   ✅ .gitignore
echo   ✅ site/ (копия сайта)
echo   ❌ .env (токен - в секрете!)
echo   ❌ .venv/ (виртуальное окружение)
echo.
echo 🎉 После загрузки:
echo   - Перейдите на PythonAnywhere
echo   - Клонируйте: git clone https://github.com/ВАШ_ЛОГИН/medcool-schedule-bot.git
echo   - Следуйте инструкции DEPLOY_PYTHONANYWHERE.md
echo.
pause
