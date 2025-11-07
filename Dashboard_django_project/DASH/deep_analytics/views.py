# deep_analytics/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from panel_0.models import Dispositivo
from analisis.models import Lectura
from django.db.models import Avg, Max, Min, Count
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
import json

@login_required
def deep_analisis(request, device_id):
    dispositivo = get_object_or_404(Dispositivo, id=device_id, user=request.user)
    dias = int(request.GET.get('dias', 7))
    desde = timezone.now() - timedelta(days=dias)

    # OBTENER DATOS MULTI-VARIABLE
    lecturas_data = Lectura.objects.filter(
        dispositivo=dispositivo,
        timestamp__gte=desde
    ).values('campo', 'timestamp', 'valor')

    if not lecturas_data:
        return render(request, 'deep_analytics/deep_analytics.html', {
            'dispositivo': dispositivo,
            'error': 'No hay datos suficientes para análisis profundo.'
        })

    # CONVERTIR A PANDAS
    df = pd.DataFrame(lecturas_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.pivot(index='timestamp', columns='campo', values='valor').fillna(0)

    # 1. CORRELACIÓN (mapa de calor)
    correlacion = df.corr()
    correlacion_html = correlacion.to_html(classes='table table-striped', float_format='%.3f')

    # 2. DETECCIÓN DE ANOMALÍAS (Isolation Forest)
    anomalias = []
    for campo in df.columns:
        if len(df[campo].dropna()) > 10:
            model = IsolationForest(contamination=0.1)
            df[f'{campo}_anomalia'] = model.fit_predict(df[[campo]].dropna())
            anomalias_count = (df[f'{campo}_anomalia'] == -1).sum()
            if anomalias_count > 0:
                anomalias.append({'campo': campo, 'anomalias': anomalias_count})

    # 3. PREDICCIÓN (regresión lineal simple)
    predicciones = {}
    for campo in df.columns:
        if len(df[campo].dropna()) > 5:
            X = np.arange(len(df[campo].dropna())).reshape(-1, 1)
            y = df[campo].dropna().values
            model = LinearRegression().fit(X, y)
            next_value = model.predict([[len(X)]])[0]
            
            # ← AÑADE ESTO:
            tendencia = "↑" if next_value > y[-1] else "↓" if next_value < y[-1] else "→"
            
            predicciones[campo] = {
                'actual': y[-1],
                'prediccion': next_value,
                'tendencia': tendencia  # ← NUEVO
            }

    # 4. CLUSTERING (K-means para variables similares)
    if len(df.columns) > 2:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df.dropna())
        kmeans = KMeans(n_clusters=min(3, len(df.columns)), random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        # Gráfico de scatter
        fig_cluster = px.scatter(df, x=df.columns[0], y=df.columns[1], color=clusters, title='Clustering de Variables')
        cluster_html = fig_cluster.to_html(full_html=False)

    # GRÁFICO MULTI-VARIABLE (Plotly)
    fig = make_subplots(rows=1, cols=1, subplot_titles=['Tendencias Multi-Variable'])
    for campo in df.columns:
        fig.add_trace(go.Scatter(x=df.index, y=df[campo], mode='lines', name=campo))
    fig.update_layout(height=500, showlegend=True)
    grafico_html = fig.to_html(full_html=False)

    return render(request, 'deep_analytics/deep_analytics.html', {
        'dispositivo': dispositivo,
        'correlacion_html': correlacion_html,
        'anomalias': anomalias,
        'predicciones': predicciones,
        'grafico_html': grafico_html,
        'cluster_html': cluster_html if 'fig_cluster' in locals() else None,
        'dias': dias,
    })
