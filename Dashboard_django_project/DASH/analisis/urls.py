# analisis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('analisis/<int:device_id>/', views.analisis_dispositivo, name='analisis'),
]