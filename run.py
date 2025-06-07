import os
import sys
import subprocess
import threading
from dotenv import load_dotenv

def run_django():
    """Запуск Django сервера"""
    os.system('python manage.py runserver')

def run_bot():
    """Запуск Telegram бота"""
    os.system('python bot.py')

def run_domain_tracker():
    """Запуск отслеживания доменов"""
    os.system('python vpn_bot/domain_tracker.py')

def main():
    # Загрузка переменных окружения
    load_dotenv()
    
    # Проверка наличия необходимых переменных окружения
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'DJANGO_SECRET_KEY',
        'WG_SERVER_PUBLIC_KEY',
        'WG_SERVER_PRIVATE_KEY',
        'WG_SERVER_ENDPOINT',
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Ошибка: отсутствуют необходимые переменные окружения:")
        for var in missing_vars:
            print(f"- {var}")
        sys.exit(1)
    
    # Создание необходимых директорий
    os.makedirs('static', exist_ok=True)
    os.makedirs('media', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Применение миграций
    print("Применение миграций...")
    os.system('python manage.py migrate')
    
    # Запуск компонентов в отдельных потоках
    print("Запуск компонентов...")
    
    django_thread = threading.Thread(target=run_django)
    bot_thread = threading.Thread(target=run_bot)
    tracker_thread = threading.Thread(target=run_domain_tracker)
    
    django_thread.start()
    bot_thread.start()
    tracker_thread.start()
    
    # Ожидание завершения потоков
    django_thread.join()
    bot_thread.join()
    tracker_thread.join()

if __name__ == '__main__':
    main() 