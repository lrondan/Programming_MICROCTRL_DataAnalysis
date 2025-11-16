from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.preprocessing import StandardScaler

# AHORA USAMOS sensors
from panel_0.models import Dispositivo, Lectura
from panel_0.utils import guardar_datos_thingspeak


@login_required
def deep_analisis(request, device_id):
    dispositivo = get_object_or_404(Dispositivo, id=device_id)
    dias = int(request.GET.get('dias', 7))
    desde = timezone.now() - timedelta(days=dias)

    # 1. FORZAR ACTUALIZACIÓN
    guardar_datos_thingspeak(dispositivo, resultados=500)

    # 2. OBTENER LECTURAS
    lecturas = dispositivo.panel_lecturas.filter(creado_en__gte=desde).order_by('creado_en')

    if not lecturas.exists():
        return render(request, 'deep_analytics/deep_analytics.html', {
            'dispositivo': dispositivo,
            'error': 'No hay datos suficientes para análisis profundo.',
            'dias': dias,
        })

    # 3. CONSTRUIR DATAFRAME
    data = {}
    for lectura in lecturas:
        ts = lectura.creado_en.strftime('%Y-%m-%d %H:%M:%S')
        for i in range(1, 9):
            field_name = f'field{i}'
            valor = getattr(lectura, field_name, None)
            if valor is not None:
                data.setdefault(ts, {})[field_name] = float(valor)

    if not data:
        return render(request, 'deep_analytics/deep_analytics.html', {
            'dispositivo': dispositivo,
            'error': 'No hay valores numéricos en el rango seleccionado.',
            'dias': dias,
        })

    df = pd.DataFrame.from_dict(data, orient='index')
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # 4. CORRELACIÓN
    correlacion = df.corr()
    correlacion_html = correlacion.to_html(classes='table table-striped', float_format='%.3f')

    # 5. ANOMALÍAS
    anomalias = []
    for campo in df.columns:
        serie = df[campo].dropna()
        if len(serie) > 10:
            model = IsolationForest(contamination=0.1, random_state=42)
            preds = model.fit_predict(serie.values.reshape(-1, 1))
            anomalias_count = (preds == -1).sum()
            if anomalias_count > 0:
                label = getattr(dispositivo, f'label{campo[-1]}', campo)
                anomalias.append({
                    'campo': label,
                    'anomalias': int(anomalias_count),
                    'porcentaje': round(anomalias_count / len(serie) * 100, 1)
                })

    # 6. PREDICCIÓN LINEAL
    predicciones = {}
    for campo in df.columns:
        serie = df[campo].dropna()
        if len(serie) > 5:
            X = np.arange(len(serie)).reshape(-1, 1)
            y = serie.values
            model = LinearRegression().fit(X, y)
            next_val = model.predict([[len(X)]])[0]
            tendencia = "up" if next_val > y[-1] else "down" if next_val < y[-1] else "flat"
            label = getattr(dispositivo, f'label{campo[-1]}', campo)
            unidad = getattr(dispositivo, f'unidad{campo[-1]}', '')

            predicciones[campo] = {
                'label': label,
                'unidad': unidad,
                'actual': round(y[-1], 2),
                'prediccion': round(next_val, 2),
                'tendencia': tendencia
            }

    # 7. CLUSTERING
    cluster_html = None
    if len(df.columns) >= 2:
        df_clean = df.dropna()
        if len(df_clean) > 3:
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(df_clean)
            n_clusters = min(3, len(df_clean))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)

            df_plot = df_clean.reset_index().rename(columns={'index': 'creado_en'})

            fig_cluster = px.scatter(
                df_plot,
                x=df_clean.columns[0],
                y=df_clean.columns[1],
                color=clusters.astype(str),
                title='Clustering de Variables (K-Means)',
                labels={
                    df_clean.columns[0]: getattr(dispositivo, f'label{df_clean.columns[0][-1]}', df_clean.columns[0]),
                    df_clean.columns[1]: getattr(dispositivo, f'label{df_clean.columns[1][-1]}', df_clean.columns[1])
                },
                hover_data={'creado_en': True}
            )
            cluster_html = fig_cluster.to_html(full_html=False)

    # 8. GRÁFICO MULTIVARIABLE
    fig = make_subplots(rows=1, cols=1, subplot_titles=[f'Tendencias Últimos {dias} Días'])
    colors = px.colors.qualitative.Plotly

    for idx, campo in enumerate(df.columns):
        label = getattr(dispositivo, f'label{campo[-1]}', campo)
        unidad = getattr(dispositivo, f'unidad{campo[-1]}', '')
        fig.add_trace(
            go.Scatter(
                x=df.index, y=df[campo],
                mode='lines+markers',
                name=f'{label} ({unidad})'.strip(),
                line=dict(color=colors[idx % len(colors)])
            )
        )

    fig.update_layout(height=600, showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    grafico_html = fig.to_html(full_html=False)

    # 9. RENDER
    return render(request, 'deep_analytics/deep_analisis.html', {
        'dispositivo': dispositivo,
        'correlacion_html': correlacion_html,
        'anomalias': anomalias,
        'predicciones': predicciones,
        'grafico_html': grafico_html,
        'cluster_html': cluster_html,
        'dias': dias,
    })