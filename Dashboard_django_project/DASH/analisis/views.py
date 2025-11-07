# analisis/views.py
from django.shortcuts import render, get_object_or_404
from panel_0.models import Dispositivo
from .models import Lectura
from django.db.models import Avg, Max, Min, Count
from django.utils import timezone
from datetime import timedelta
import json

def analisis_dispositivo(request, device_id):
    dispositivo = get_object_or_404(Dispositivo, id=device_id, user=request.user)
    campo = request.GET.get('campo', 'field1')
    dias = int(request.GET.get('dias', 7))

    # FILTRO DE TIEMPO
    desde = timezone.now() - timedelta(days=dias)
    lecturas = Lectura.objects.filter(
        dispositivo=dispositivo,
        campo=campo,
        timestamp__gte=desde
    ).order_by('timestamp')

    # ESTADÍSTICAS
    stats = lecturas.aggregate(
        promedio=Avg('valor'),
        maximo=Max('valor'),
        minimo=Min('valor'),
        total=Count('valor')
    )

    # DATOS PARA GRÁFICO
    datos_grafico = [
        {'x': l.timestamp.strftime('%Y-%m-%d %H:%M'), 'y': l.valor}
        for l in lecturas
    ]

    # OBTENER LABEL Y UNIDAD DINÁMICAMENTE
    num_campo = int(campo[-1])  # 'field1' → 1
    label = getattr(dispositivo, f'label{num_campo}', f'Field {num_campo}')
    unidad = getattr(dispositivo, f'unidad{num_campo}', '')

    # CAMPOS DISPONIBLES CON LABELS
    campos_disponibles = []
    for i in range(1, 9):
        if hasattr(dispositivo, f'valor{i}') and getattr(dispositivo, f'valor{i}') is not None:
            label_i = getattr(dispositivo, f'label{i}', f'Field {i}')
            unidad_i = getattr(dispositivo, f'unidad{i}', '')
            campos_disponibles.append({
                'value': f'field{i}',
                'label': f'{label_i} ({unidad_i})'.strip(' ()')
            })

    return render(request, 'analisis/analisis.html', {
        'dispositivo': dispositivo,
        'campo': campo,
        'label': label,
        'unidad': unidad,
        'stats': stats,
        'datos_grafico': json.dumps(datos_grafico),
        'dias': dias,
        'campos_disponibles': campos_disponibles,
    })