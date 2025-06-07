import os
import logging
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv
import django
import qrcode
from io import BytesIO

# Загрузка переменных окружения
load_dotenv()

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vpn_project.settings')
django.setup()

# Импорт моделей после настройки Django
from vpn_bot.models import TelegramUser, WireGuardPeer
from vpn_bot.views import generate_wireguard_config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    telegram_user, created = TelegramUser.objects.get_or_create(
        telegram_id=user.id,
        defaults={
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    )
    
    welcome_message = (
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот для управления WireGuard VPN.\n\n"
        "Доступные команды:\n"
        "/newvpn - Создать новую VPN конфигурацию\n"
        "/status - Проверить статус VPN\n"
        "/help - Показать это сообщение"
    )
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_message = (
        "Доступные команды:\n\n"
        "/newvpn - Создать новую VPN конфигурацию\n"
        "Создаст новую конфигурацию WireGuard и отправит её вам в виде файла и QR-кода.\n\n"
        "/status - Проверить статус VPN\n"
        "Покажет текущий статус вашей VPN конфигурации.\n\n"
        "/help - Показать это сообщение"
    )
    
    await update.message.reply_text(help_message)

async def newvpn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /newvpn"""
    user = update.effective_user
    telegram_user = TelegramUser.objects.get(telegram_id=user.id)
    
    # Проверяем, есть ли уже активный peer
    if hasattr(telegram_user, 'peer') and telegram_user.peer.is_active:
        await update.message.reply_text(
            "У вас уже есть активная VPN конфигурация. "
            "Пожалуйста, обратитесь к администратору для создания новой."
        )
        return
    
    try:
        # Генерируем ключи и создаем peer
        private_key = os.popen('wg genkey').read().strip()
        public_key = os.popen(f'echo {private_key} | wg pubkey').read().strip()
        
        # Генерируем IP адрес (простой пример)
        last_peer = WireGuardPeer.objects.order_by('-client_ip').first()
        if last_peer:
            last_ip = int(last_peer.client_ip.split('.')[-1])
            new_ip = f"10.0.0.{last_ip + 1}"
        else:
            new_ip = "10.0.0.2"
        
        # Создаем peer
        peer = WireGuardPeer.objects.create(
            user=telegram_user,
            public_key=public_key,
            private_key=private_key,
            client_ip=new_ip
        )
        
        # Генерируем конфигурацию
        config = generate_wireguard_config(peer)
        
        # Создаем QR-код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(config)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Отправляем файл конфигурации
        await update.message.reply_document(
            document=BytesIO(config.encode()),
            filename=f"wg-{new_ip}.conf",
            caption="Ваша конфигурация WireGuard"
        )
        
        # Отправляем QR-код
        await update.message.reply_photo(
            photo=buffer,
            caption="QR-код для быстрой настройки"
        )
        
        await update.message.reply_text(
            "Ваша VPN конфигурация готова! "
            "Вы можете скачать файл конфигурации или отсканировать QR-код для настройки."
        )
        
    except Exception as e:
        logger.error(f"Error creating VPN config: {e}")
        await update.message.reply_text(
            "Произошла ошибка при создании VPN конфигурации. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status"""
    user = update.effective_user
    telegram_user = TelegramUser.objects.get(telegram_id=user.id)
    
    if not hasattr(telegram_user, 'peer'):
        await update.message.reply_text(
            "У вас нет активной VPN конфигурации. "
            "Используйте команду /newvpn для создания новой."
        )
        return
    
    peer = telegram_user.peer
    status_message = (
        f"Статус вашей VPN конфигурации:\n\n"
        f"IP адрес: {peer.client_ip}\n"
        f"Статус: {'Активна' if peer.is_active else 'Неактивна'}\n"
        f"Создана: {peer.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    )
    
    if peer.last_handshake:
        status_message += f"Последнее подключение: {peer.last_handshake.strftime('%d.%m.%Y %H:%M')}"
    
    await update.message.reply_text(status_message)

def main():
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("newvpn", newvpn))
    application.add_handler(CommandHandler("status", status))
    
    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main() 