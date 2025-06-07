from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from .models import WireGuardPeer
import qrcode
from io import BytesIO
import os

@staff_member_required
def view_peer_config(request, peer_id):
    peer = get_object_or_404(WireGuardPeer, pk=peer_id)
    config = generate_wireguard_config(peer)
    return render(request, 'vpn_bot/peer_config.html', {
        'peer': peer,
        'config': config,
    })

@staff_member_required
def download_peer_config(request, peer_id):
    peer = get_object_or_404(WireGuardPeer, pk=peer_id)
    config = generate_wireguard_config(peer)
    
    response = HttpResponse(config, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="wg-{peer.client_ip}.conf"'
    return response

@staff_member_required
def view_peer_qr(request, peer_id):
    peer = get_object_or_404(WireGuardPeer, pk=peer_id)
    config = generate_wireguard_config(peer)
    
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
    
    return FileResponse(buffer, content_type='image/png')

def generate_wireguard_config(peer):
    config = f"""[Interface]
PrivateKey = {peer.private_key}
Address = {peer.client_ip}/24
DNS = {settings.WG_SERVER_DNS}

[Peer]
PublicKey = {settings.WG_SERVER_PUBLIC_KEY}
Endpoint = {settings.WG_SERVER_ENDPOINT}:{settings.WG_SERVER_PORT}
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""
    return config 