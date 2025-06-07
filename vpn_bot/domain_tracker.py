import os
import logging
import subprocess
from datetime import datetime
from django.conf import settings
from .models import WireGuardPeer, DomainVisit

logger = logging.getLogger(__name__)

def get_peer_by_ip(ip_address):
    """Получение peer'а по IP адресу"""
    try:
        return WireGuardPeer.objects.get(client_ip=ip_address)
    except WireGuardPeer.DoesNotExist:
        return None

def parse_dns_logs():
    """Парсинг логов DNS для отслеживания посещений доменов"""
    try:
        # Чтение логов DNS (пример для dnsmasq)
        log_file = '/var/log/dnsmasq.log'
        if not os.path.exists(log_file):
            logger.error(f"DNS log file not found: {log_file}")
            return
        
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    # Пример формата лога: "query[A] example.com from 10.0.0.2"
                    if 'query[A]' in line:
                        parts = line.split()
                        domain = parts[1].split(']')[1]
                        ip_address = parts[-1]
                        
                        # Получаем peer по IP
                        peer = get_peer_by_ip(ip_address)
                        if peer:
                            # Создаем запись о посещении
                            DomainVisit.objects.create(
                                peer=peer,
                                domain=domain,
                                ip_address=ip_address
                            )
                            
                            # Обновляем время последнего подключения
                            peer.last_handshake = datetime.now()
                            peer.save()
                            
                except Exception as e:
                    logger.error(f"Error parsing DNS log line: {e}")
                    
    except Exception as e:
        logger.error(f"Error reading DNS logs: {e}")

def start_domain_tracking():
    """Запуск отслеживания доменов"""
    try:
        # Проверяем наличие необходимых прав
        if os.geteuid() != 0:
            logger.error("Domain tracking requires root privileges")
            return
        
        # Запускаем отслеживание в фоновом режиме
        while True:
            parse_dns_logs()
            time.sleep(60)  # Проверяем каждую минуту
            
    except Exception as e:
        logger.error(f"Error in domain tracking: {e}")

if __name__ == '__main__':
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Запуск отслеживания
    start_domain_tracking() 