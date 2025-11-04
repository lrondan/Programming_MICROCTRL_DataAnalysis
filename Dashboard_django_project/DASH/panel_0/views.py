# panel_0/views.py
from django.shortcuts import render, get_object_or_404
from .models import Dispositivo
import requests
from django.utils import timezone
from datetime import datetime
import pytz
from analisis.models import Lectura
from django.utils import timezone


def device_detail(request, device_id):
    d = get_object_or_404(Dispositivo, id=device_id)
    campos = []

    if d.thingspeak_channel:
        try:
            url = f"https://api.thingspeak.com/channels/{d.thingspeak_channel}/feeds.json?results=1"
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                feed = response.json()['feeds'][0]
                created_at = feed.get('created_at')
                ts = timezone.now()
                if created_at:
                    from datetime import datetime
                    import pytz
                    ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)

                for i in range(1, 9):
                    field_key = f'field{i}'
                    if feed.get(field_key):
                        valor = float(feed[field_key])
                        label = getattr(d, f'label{i}', f'Field {i}')
                        unidad = getattr(d, f'unidad{i}', '')

                        # GUARDAR EN BASE DE DATOS
                        Lectura.objects.update_or_create(
                            dispositivo=d,
                            campo=field_key,
                            timestamp=ts,
                            defaults={'valor': valor}
                        )

                        campos.append({
                            'num': i,
                            'valor': valor,
                            'label': label,
                            'unidad': unidad,
                        })
                        setattr(d, f'valor{i}', valor)

                d.ultimo_dato = ts
                d.save()
        except Exception as e:
            print(f"Error: {e}")

    d.actualizar_estado()

    return render(request, 'panel_0/dashboard_iot.html', {
        'dispositivos_data': [{'dispositivo': d, 'campos': campos}]
    })


def dashboard_iot(request):
    print("=== INICIO DASHBOARD ===")
    
    # Buscar dispositivos
    dispositivos = Dispositivo.objects.filter(thingspeak_channel__isnull=False)
    print(f"Dispositivos encontrados: {[d.nombre for d in dispositivos]}")
    
    if not dispositivos.exists():
        print("¡ERROR! No hay dispositivos con Channel ID. Ve al Admin.")
        return render(request, 'panel_0/dashboard_iot.html', {'error': 'No hay dispositivos con Channel ID'})

    dispositivos_data = []
    for d in dispositivos:
        print(f"Procesando {d.nombre} (Channel: {d.thingspeak_channel})")
        
        try:
            # Leer ThingSpeak
            url = f"https://api.thingspeak.com/channels/{d.thingspeak_channel}/feeds.json?results=1"
            print(f"Llamando a: {url}")
            
            response = requests.get(url, timeout=15)  # Timeout más largo
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Datos recibidos: {data}")
                
                if data.get('feeds'):
                    feed = data['feeds'][0]
                    created_at = feed.get('created_at')
                    ts = timezone.now()
                    if created_at:
                        ts = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.UTC)
                    
                    campos = []
                    for i in range(1, 9):
                        field_key = f'field{i}'
                        if feed.get(field_key):
                            valor = float(feed[field_key])
                            label = getattr(d, f'label{i}', f'Field {i}')
                            unidad = getattr(d, f'unidad{i}', '')
                            campos.append({
                                'num': i,
                                'valor': valor,
                                'label': label,
                                'unidad': unidad,
                            })
                            setattr(d, f'valor{i}', valor)
                            print(f"  Field {i}: {valor} ({label})")
                    
                    d.ultimo_dato = ts
                    d.save()
                    
                    dispositivos_data.append({
                        'dispositivo': d,
                        'campos': campos,
                    })
                    print(f"¡ÉXITO! {len(campos)} campos cargados.")
                else:
                    print("¡ADVERTENCIA! No hay 'feeds' en la respuesta.")
                    
                    # DATOS DE PRUEBA (temporal)
                    campos = [
                        {'num': 1, 'valor': 26.0, 'label': 'Humedad', 'unidad': '%'},
                        {'num': 2, 'valor': 18.0, 'label': 'Temperatura', 'unidad': '°C'},
                        {'num': 3, 'valor': 631, 'label': 'Luz', 'unidad': ''},
                        {'num': 4, 'valor': 204, 'label': 'Lluvia', 'unidad': ''},
                    ]
                    dispositivos_data.append({'dispositivo': d, 'campos': campos})
                    print("Usando datos de prueba.")
            else:
                print(f"¡ERROR HTTP! {response.status_code}: {response.text[:200]}")
                
                # DATOS DE PRUEBA
                campos = [
                    {'num': 1, 'valor': 26.0, 'label': 'Humedad', 'unidad': '%'},
                    {'num': 2, 'valor': 18.0, 'label': 'Temperatura', 'unidad': '°C'},
                ]
                dispositivos_data.append({'dispositivo': d, 'campos': campos})
                
        except Exception as e:
            print(f"¡ERROR GENERAL! {e}")
            
            # DATOS DE PRUEBA
            campos = [{'num': 1, 'valor': 25.0, 'label': 'Prueba', 'unidad': '°C'}]
            dispositivos_data.append({'dispositivo': d, 'campos': campos})

        d.actualizar_estado()

    print(f"Total en dashboard: {len(dispositivos_data)}")
    return render(request, 'panel_0/dashboard_iot.html', {
        'dispositivos_data': dispositivos_data
    })


def home(request):
    dispositivos = Dispositivo.objects.all().order_by('nombre')
    for d in dispositivos:
        d.actualizar_estado()
    return render(request, 'panel_0/home.html', {
        'dispositivos': dispositivos
    })

def device_detail(request, device_id):
    d = get_object_or_404(Dispositivo, id=device_id)
    print(f"Detalle de: {d.nombre} (Channel: {d.thingspeak_channel})")

    campos = []
    if d.thingspeak_channel:
        try:
            url = f"https://api.thingspeak.com/channels/{d.thingspeak_channel}/feeds.json?results=1"
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
                        label = getattr(d, f'label{i}', f'Field {i}')
                        unidad = getattr(d, f'unidad{i}', '')
                        campos.append({
                            'num': i,
                            'valor': valor,
                            'label': label,
                            'unidad': unidad,
                        })
                        setattr(d, f'valor{i}', valor)

                d.ultimo_dato = ts
                d.save()
            else:
                print(f"Error HTTP: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")

    d.actualizar_estado()

    return render(request, 'panel_0/dashboard_iot.html', {
        'dispositivos_data': [{'dispositivo': d, 'campos': campos}]
    })