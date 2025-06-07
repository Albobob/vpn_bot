import os
import subprocess
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class WireGuardManager:
    def __init__(self):
        self.interface = 'wg0'
        self.config_path = '/etc/wireguard/wg0.conf'
        self.server_public_key = settings.WG_SERVER_PUBLIC_KEY
        self.server_private_key = settings.WG_SERVER_PRIVATE_KEY
        self.server_endpoint = settings.WG_SERVER_ENDPOINT
        self.server_port = settings.WG_SERVER_PORT
        self.server_network = settings.WG_SERVER_NETWORK

    def generate_keys(self):
        """Генерация ключей для нового peer'а"""
        try:
            private_key = subprocess.check_output(['wg', 'genkey']).decode().strip()
            public_key = subprocess.check_output(
                ['wg', 'pubkey'],
                input=private_key.encode()
            ).decode().strip()
            return private_key, public_key
        except Exception as e:
            logger.error(f"Error generating keys: {e}")
            raise

    def add_peer(self, peer):
        """Добавление нового peer'а в конфигурацию WireGuard"""
        try:
            # Формируем конфигурацию peer'а
            peer_config = f"""
[Peer]
PublicKey = {peer.public_key}
AllowedIPs = {peer.client_ip}/32
"""
            # Добавляем peer в конфигурацию
            with open(self.config_path, 'a') as f:
                f.write(peer_config)
            
            # Перезапускаем WireGuard
            self.restart_wireguard()
            
            return True
        except Exception as e:
            logger.error(f"Error adding peer: {e}")
            return False

    def remove_peer(self, peer):
        """Удаление peer'а из конфигурации WireGuard"""
        try:
            # Читаем текущую конфигурацию
            with open(self.config_path, 'r') as f:
                config_lines = f.readlines()
            
            # Удаляем секцию peer'а
            new_config = []
            skip_peer = False
            for line in config_lines:
                if f"PublicKey = {peer.public_key}" in line:
                    skip_peer = True
                    continue
                if skip_peer and line.strip() == "":
                    skip_peer = False
                    continue
                if not skip_peer:
                    new_config.append(line)
            
            # Записываем обновленную конфигурацию
            with open(self.config_path, 'w') as f:
                f.writelines(new_config)
            
            # Перезапускаем WireGuard
            self.restart_wireguard()
            
            return True
        except Exception as e:
            logger.error(f"Error removing peer: {e}")
            return False

    def restart_wireguard(self):
        """Перезапуск WireGuard"""
        try:
            subprocess.run(['wg-quick', 'down', self.interface], check=True)
            subprocess.run(['wg-quick', 'up', self.interface], check=True)
            return True
        except Exception as e:
            logger.error(f"Error restarting WireGuard: {e}")
            return False

    def get_peer_status(self, peer):
        """Получение статуса peer'а"""
        try:
            output = subprocess.check_output(['wg', 'show', self.interface]).decode()
            for line in output.split('\n'):
                if peer.public_key in line:
                    return True
            return False
        except Exception as e:
            logger.error(f"Error getting peer status: {e}")
            return False

    def update_peer_status(self, peer):
        """Обновление статуса peer'а в базе данных"""
        try:
            is_active = self.get_peer_status(peer)
            peer.is_active = is_active
            peer.save()
            return is_active
        except Exception as e:
            logger.error(f"Error updating peer status: {e}")
            return False 