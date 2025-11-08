# panel_0/tasks.py
from celery import shared_task
from .models import Dispositivo
from .utils import guardar_datos_thingspeak  # Asegúrate de tener esta función

@shared_task
def actualizar_dispositivo_task(dispositivo_id):
    try:
        d = Dispositivo.objects.get(id=dispositivo_id)
        guardar_datos_thingspeak(d, resultados=100)  # ← SOLO 100
        d.actualizar_estado()
    except Dispositivo.DoesNotExist:
        pass