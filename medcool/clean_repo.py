#!/usr/bin/env python3
"""
Скрипт для очистки репозитория от лишних файлов
"""

import os
import shutil
import subprocess

def remove_unnecessary_files():
    """Удаление лишних файлов и папок"""
    
    files_to_remove = [
        'enhanced_response_Ф22.html',
        'setup_git.py'
    ]
    
    folders_to_remove = [
        'site'
    ]
    
    print("🧹 Очистка репозитория...")
    
    # Удаление файлов
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"✅ Удален файл: {file_name}")
            except Exception as e:
                print(f"❌ Ошибка при удалении файла {file_name}: {e}")
    
    # Удаление папок
    for folder_name in folders_to_remove:
        if os.path.exists(folder_name):
            try:
                shutil.rmtree(folder_name)
                print(f"✅ Удалена папка: {folder_name}")
            except Exception as e:
                print(f"❌ Ошибка при удалении папки {folder_name}: {e}")
    
    print("\n🎉 Очистка завершена!")
    
    # Показываем что осталось
    print("\n📁 Остальные файлы:")
    for item in os.listdir('.'):
        if not item.startswith('.') and os.path.isfile(item):
            size = os.path.getsize(item)
            print(f"   📄 {item} ({size} bytes)")
        elif not item.startswith('.') and os.path.isdir(item):
            print(f"   📁 {item}/")

if __name__ == "__main__":
    remove_unnecessary_files()
