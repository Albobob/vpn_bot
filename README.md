# VPN Telegram Bot с Django Admin Panel

Это приложение представляет собой Telegram бота для управления WireGuard VPN с админ-панелью на Django.

## Требования

- Python 3.10+
- WireGuard
- Telegram Bot Token
- Linux сервер (рекомендуется Ubuntu 22.04)

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd vpn-bot
```

2. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
venv\Scripts\activate     # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env в корневой директории:
```
TELEGRAM_BOT_TOKEN=your_bot_token
DJANGO_SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя Django:
```bash
python manage.py createsuperuser
```

## Настройка WireGuard

1. Установите WireGuard на сервер:
```bash
sudo apt update
sudo apt install wireguard
```

2. Сгенерируйте ключи для сервера:
```bash
cd /etc/wireguard
wg genkey | sudo tee /etc/wireguard/private.key
sudo cat /etc/wireguard/private.key | wg pubkey | sudo tee /etc/wireguard/public.key
```

3. Создайте конфигурацию сервера (wg0.conf):
```bash
sudo nano /etc/wireguard/wg0.conf
```

Пример конфигурации:
```ini
[Interface]
PrivateKey = <server_private_key>
Address = 10.0.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE
```

4. Включите IP forwarding:
```bash
echo "net.ipv4.ip_forward = 1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

5. Запустите WireGuard:
```bash
sudo systemctl enable wg-quick@wg0
sudo systemctl start wg-quick@wg0
```

## Запуск приложения

1. Запустите Django сервер:
```bash
python manage.py runserver
```

2. В отдельном терминале запустите Telegram бота:
```bash
python bot.py
```

## Использование

### Telegram Bot Команды

- `/start` - Начало работы с ботом
- `/newvpn` - Создание новой VPN конфигурации
- `/help` - Справка по командам
- `/status` - Проверка статуса VPN

### Django Admin Panel

Доступ к админ-панели: http://localhost:8000/admin

Функции админ-панели:
- Управление пользователями и их VPN конфигурациями
- Просмотр статистики использования
- Экспорт данных
- Управление доступами

## Безопасность

- Храните .env файл в безопасном месте
- Регулярно обновляйте зависимости
- Используйте сложные пароли для админ-панели
- Настройте брандмауэр для защиты сервера

## Лицензия

MIT 