# panel_0/utils.py
import requests
from django.utils.dateparse import parse_datetime
from .models import Dispositivo, Lectura

def guardar_datos_thingspeak(dispositivo, resultados=10):
    if not dispositivo.thingspeak_channel or not dispositivo.thingspeak_read_key:
        return False

    url = f"https://api.thingspeak.com/channels/{dispositivo.thingspeak_channel}/feeds.json"
    params = {
        'api_key': dispositivo.thingspeak_read_key,
        'results': min(resultados, 100)
    }

    try:
        response = requests.get(url, params=params, timeout=12)
        if response.status_code != 200:
            return False
        data = response.json()
    except Exception as e:
        print(f"[ERROR THINGSPEAK] {e}")
        return False

    feeds = data.get('feeds', [])
    if not feeds:
        return False

    actualizado = False
    ultimo_dt = None

    for feed in feeds:
        created_at_str = feed.get('created_at')
        if not created_at_str:
            continue
        dt = parse_datetime(created_at_str)
        if not dt:
            continue

        # GUARDAR COMO Lectura (auto_now_add = ahora)
        lectura = Lectura(dispositivo=dispositivo)
        for i in range(1, 9):
            field = f'field{i}'
            valor = feed.get(field)
            if valor is not None:
                try:
                    setattr(lectura, field, float(valor))
                except:
                    pass
        lectura.save()  # creado_en se guarda automáticamente

        # Actualizar último valor en Dispositivo
        if not ultimo_dt or dt > ultimo_dt:
            ultimo_dt = dt
            for i in range(1, 9):
                field = f'field{i}'
                valor = feed.get(field)
                if valor is not None:
                    try:
                        setattr(dispositivo, f'valor{i}', float(valor))
                        actualizado = True
                    except:
                        pass

    if ultimo_dt:
        dispositivo.ultimo_dato = ultimo_dt
        if actualizado:
            dispositivo.save()
        dispositivo.actualizar_estado()
        return True
    return False