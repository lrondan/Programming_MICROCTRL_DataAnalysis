# auth_app/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm
from panel_0.models import Dispositivo

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()

    return render(request, 'auth_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión.')
    return redirect('login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Crear dispositivo
            Dispositivo.objects.create(
                user=user,
                nombre=f"Dispositivo de {user.first_name or user.username}",
                thingspeak_channel=None,
                icono='microchip',
                label1='Temperatura',
                unidad1='°C'
            )
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.first_name}! Tu cuenta se creó con éxito.')
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'auth_app/register.html', {'form': form})

# OPCIONAL: Página de bienvenida protegida
@login_required
def home_protected(request):
    return render(request, 'auth_app/protected.html')