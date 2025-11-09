# panel_0/views.py
from .utils import guardar_datos_thingspeak
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Dispositivo 
from .forms import DispositivoForm
from django.contrib import messages

@login_required
def home(request):
    dispositivos = request.user.dispositivos.all().order_by('nombre')
    for d in dispositivos:
        guardar_datos_thingspeak(d, resultados=10)
    return render(request, 'panel_0/home.html', {'dispositivos': dispositivos})

@login_required
def device_detail(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id, user=request.user)
    guardar_datos_thingspeak(dispositivo, resultados=10)
    return render(request, 'panel_0/dashboard_iot.html', {'dispositivo': dispositivo})

@login_required
def agregar_dispositivo(request):
    if request.method == 'POST':
        form = DispositivoForm(request.POST)
        if form.is_valid():
            dispositivo = form.save(commit=False)
            dispositivo.user = request.user
            dispositivo.save()
            messages.success(request, f'¡Dispositivo "{dispositivo.nombre}" agregado!')
            return redirect('home')
    else:
        form = DispositivoForm()

    return render(request, 'panel_0/add_dispositivo.html', {'form': form})

@login_required
def eliminar_dispositivo(request, dispositivo_id):
    dispositivo = get_object_or_404(Dispositivo, id=dispositivo_id, user=request.user)
    
    if request.method == 'POST':
        dispositivo.delete()
        messages.success(request, f"Dispositivo '{dispositivo.nombre}' eliminado.")
        return redirect('home')

    return render(request, 'panel_0/eliminar_dispositivo.html', {'dispositivo': dispositivo})