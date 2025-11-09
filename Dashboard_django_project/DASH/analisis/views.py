# analisis/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
import json

# IMPORTAMOS DE panel_0
from panel_0.models import Dispositivo
from panel_0.utils import guardar_datos_thingspeak


@login_required
def analisis_dispositivo(request, device_id):
    # 1. Obtener dispositivo
    dispositivo = get_object_or_404(Dispositivo, id=device_id, user=request.user)

    # 2. Forzar actualización desde ThingSpeak
    guardar_datos_thingspeak(dispositivo, resultados=100)

    # 3. Parámetros de la URL
    campo = request.GET.get('campo', 'field1')  # Ej: field1, field2...
    dias = int(request.GET.get('dias', 7))

    # Validar campo
    if campo not in [f'field{i}' for i in range(1, 9)]:
        campo = 'field1'

    # 4. Filtrar lecturas por tiempo
    desde = timezone.now() - timedelta(days=dias)
    lecturas = dispositivo.panel_lecturas.filter(
        creado_en__gte=desde
    ).order_by('creado_en')

    # 5. Extraer valores del campo seleccionado
    valores = []
    for lectura in lecturas:
        valor = getattr(lectura, campo, None)
        if valor is not None:
            valores.append({
                'x': lectura.creado_en.strftime('%Y-%m-%d %H:%M'),
                'y': float(valor)
            })

    # 6. Estadísticas del campo seleccionado
    stats = {
        'promedio': None,
        'maximo': None,
        'minimo': None,
        'total': len(valores)
    }

    if valores:
        ys = [v['y'] for v in valores]
        stats['promedio'] = round(sum(ys) / len(ys), 2)
        stats['maximo'] = max(ys)
        stats['minimo'] = min(ys)

    # 7. Obtener label y unidad del campo
    num_campo = int(campo[-1])
    label = getattr(dispositivo, f'label{num_campo}', f'Field {num_campo}')
    unidad = getattr(dispositivo, f'unidad{num_campo}', '')

    # 8. Campos disponibles (solo los que tienen valor actual)
    campos_disponibles = []
    for i in range(1, 9):
        valor_actual = getattr(dispositivo, f'valor{i}', None)
        if valor_actual is not None:
            label_i = getattr(dispositivo, f'label{i}', f'Field {i}')
            unidad_i = getattr(dispositivo, f'unidad{i}', '')
            campos_disponibles.append({
                'value': f'field{i}',
                'label': f'{label_i} ({unidad_i})'.strip(' ()')
            })

    # 9. Renderizar
    return render(request, 'analisis/analisis.html', {
        'dispositivo': dispositivo,
        'campo': campo,
        'label': label,
        'unidad': unidad,
        'stats': stats,
        'datos_grafico': json.dumps(valores),
        'dias': dias,
        'campos_disponibles': campos_disponibles,
    })