# about/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('como-funciona/', views.como_funciona, name='como_funciona'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
]