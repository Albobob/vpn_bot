from django.urls import path
from . import views

app_name = 'vpn_bot'

urlpatterns = [
    path('admin/peer/<int:peer_id>/config/', views.view_peer_config, name='view_peer_config'),
    path('admin/peer/<int:peer_id>/download/', views.download_peer_config, name='download_peer_config'),
    path('admin/peer/<int:peer_id>/qr/', views.view_peer_qr, name='view_peer_qr'),
] 