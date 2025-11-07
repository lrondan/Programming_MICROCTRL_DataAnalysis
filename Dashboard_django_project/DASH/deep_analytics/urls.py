from django.urls import path
from . import views

urlpatterns = [
    path('deep_analisis/<int:device_id>/', views.deep_analisis, name='deep_analisis'),
]   