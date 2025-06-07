from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import TelegramUser, WireGuardPeer, DomainVisit

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'username', 'first_name', 'last_name', 'created_at', 'is_active', 'has_peer')
    list_filter = ('is_active', 'created_at')
    search_fields = ('telegram_id', 'username', 'first_name', 'last_name')
    readonly_fields = ('created_at',)

    def has_peer(self, obj):
        return bool(obj.peer)
    has_peer.boolean = True
    has_peer.short_description = 'Имеет VPN'

@admin.register(WireGuardPeer)
class WireGuardPeerAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_ip', 'created_at', 'last_handshake', 'is_active', 'view_config')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__telegram_id', 'user__username', 'client_ip', 'public_key')
    readonly_fields = ('created_at', 'last_handshake')

    def view_config(self, obj):
        url = reverse('admin:view_peer_config', args=[obj.pk])
        return format_html('<a href="{}">Просмотр конфига</a>', url)
    view_config.short_description = 'Конфигурация'

@admin.register(DomainVisit)
class DomainVisitAdmin(admin.ModelAdmin):
    list_display = ('domain', 'peer', 'visited_at', 'ip_address')
    list_filter = ('visited_at', 'peer')
    search_fields = ('domain', 'peer__user__username', 'ip_address')
    readonly_fields = ('visited_at',)
    date_hierarchy = 'visited_at' 