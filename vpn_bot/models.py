from django.db import models
from django.utils import timezone

class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username or self.telegram_id}"

    class Meta:
        verbose_name = "Пользователь Telegram"
        verbose_name_plural = "Пользователи Telegram"

class WireGuardPeer(models.Model):
    user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, related_name='peer')
    public_key = models.CharField(max_length=255, unique=True)
    private_key = models.CharField(max_length=255)
    client_ip = models.GenericIPAddressField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_handshake = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Peer {self.client_ip} ({self.user})"

    class Meta:
        verbose_name = "WireGuard Peer"
        verbose_name_plural = "WireGuard Peers"

class DomainVisit(models.Model):
    peer = models.ForeignKey(WireGuardPeer, on_delete=models.CASCADE, related_name='visits')
    domain = models.CharField(max_length=255)
    visited_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.domain} - {self.visited_at}"

    class Meta:
        verbose_name = "Посещение домена"
        verbose_name_plural = "Посещения доменов"
        indexes = [
            models.Index(fields=['domain']),
            models.Index(fields=['visited_at']),
        ] 