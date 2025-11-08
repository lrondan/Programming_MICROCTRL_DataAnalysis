# panel_0/views.py
from .tasks import actualizar_dispositivo_task
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
        # GUARDAR HASTA 100 DATOS POR DISPOSITIVO
        actualizar_dispositivo_task.delay(d.id)
    messages.info(request, 'Los dispositivos se están actualizando en segundo plano.')
    return render(request, 'panel_0/home.html', {'dispositivos': dispositivos})

@login_required
def device_detail(request, device_id):
    d = get_object_or_404(Dispositivo, id=device_id, user=request.user)
    actualizar_dispositivo_task.delay(d.id)
    d.actualizar_estado()

    campos = []
    for i in range(1, 9):
        valor = getattr(d, f'valor{i}', None)
        if valor is not None:
            label = getattr(d, f'label{i}', f'Field {i}')
            unidad = getattr(d, f'unidad{i}', '')
            campos.append({'num': i, 'valor': valor, 'label': label, 'unidad': unidad})

    return render(request, 'panel_0/dashboard_iot.html', {
        'dispositivos_data': [{'dispositivo': d, 'campos': campos}]
    })

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
def eliminar_dispositivo(request, device_id):
    dispositivo = get_object_or_404(Dispositivo, id=device_id, user=request.user)
    if request.method == 'POST':
        nombre = dispositivo.nombre
        dispositivo.delete()
        messages.success(request, f'¡Dispositivo "{nombre}" eliminado correctamente!')
        return redirect('home')
    return render(request, 'panel_0/eliminar_dispositivo.html', {'dispositivo': dispositivo})