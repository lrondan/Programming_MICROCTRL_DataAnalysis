# panel_0/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('device/<int:dispositivo_id>/', views.device_detail, name='device_detail'),
    path('add_device/', views.agregar_dispositivo, name='agregar_dispositivo'),
    path('dispositivo/<int:dispositivo_id>/eliminar/', views.eliminar_dispositivo, name='eliminar_dispositivo'),
]