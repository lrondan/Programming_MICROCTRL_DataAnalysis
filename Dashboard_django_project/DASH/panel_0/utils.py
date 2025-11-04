# panel_0/utils.py
import requests
from django.utils import timezone
from datetime import datetime
import pytz
from analisis.models import Lectura
from .models import Dispositivo

def guardar_datos_thingspeak(dispositivo):
    if not dispositivo.thingspeak_channel:
        return

    try:
        url = f"https://api.thingspeak.com/channels/{dispositivo.thingspeak_channel}/feeds.json?results=1"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            feed = response.json()['feeds'][0]
            created_at = feed.get('created_at')
            ts = timezone.now()
            if created_at:
                ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)

            for i in range(1, 9):
                field_key = f'field{i}'
                if feed.get(field_key):
                    valor = float(feed[field_key])
                    # GUARDAR
                    Lectura.objects.update_or_create(
                        dispositivo=dispositivo,
                        campo=field_key,
                        timestamp=ts,
                        defaults={'valor': valor}
                    )
                    # Actualizar valor en dispositivo
                    setattr(dispositivo, f'valor{i}', valor)

            dispositivo.ultimo_dato = ts
            dispositivo.save()
    except Exception as e:
        print(f"Error guardando datos: {e}")