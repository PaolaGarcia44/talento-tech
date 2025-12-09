# app.py

"""
Dashboard Unificado de Análisis de Delitos Ambientales
=====================================================
GRUPO 3 de Talentotech.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple

# ==============================================================================
# CONFIGURACIÓN INICIAL Y ESTILO (SIN BARRA LATERAL)
# ==============================================================================

# Se establece la configuración de la página de Streamlit para el dashboard
st.set_page_config(
    page_title="🌎 Delitos Ambientales - Análisis Explorador", 
    layout="wide",
    # CAMBIO 1 CLAVE: Se cambia a "collapsed" para esconder la barra lateral por defecto
    initial_sidebar_state="collapsed", 
)

# Diccionario de reemplazos 
REEMPLAZOS_CARACTERES: Dict[str, str] = {
    "Ã‘O": "NO", "Ã‘o": "NO", "Ã‘": "N", "Ã±": "N", "Ñ": "N", "ñ": "N",
    "Ã¡": "A", "Ã©": "E", "Ã­": "I", "Ã³": "O", "Ãº": "U", "Á": "A", "É": "E",
    "Í": "I", "Ó": "O", "Ú": "U", "ÃÁ": "A", "ÃÉ": "E", "ÃÍ": "I", "ÃÓ": "O", 
    "ÃÚ": "U", "ÃA": "A", "ÃE": "E", "ÃI": "I", "ÃO": "O", "ÃU": "U", "á": "A", 
    "é": "E", "í": "I", "ó": "O", "ú": "U", "Ã¼": "U", "Ãœ": "U", "Ü": "U", 
    "ü": "U", "¿": "", "?": "", "¡": "", "!": "", "Â¿": "", "Â¡": "",
    "ï¿½": "", "Â": "", "â€œ": "", "â€": "", "â€™": "", "â€¢": "", "â€“": "",
    "â€”": "", "™": "", "®": "", "©": "", "º": "", "ª": "", "€": "", "$": "", 
    "£": "", "¼": "", "½": "", "¾": "",
}

# --- ESTILO CSS ---
st.markdown("""
<style>
/* Estilo para la imagen de fondo de toda la aplicación */
.stApp {
    background-image: url("https://i.pinimg.com/736x/39/c7/1e/39c71e43cd06601a698edc75859dd674.jpg"); 
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed; 
}

/* Capa de superposición para difuminar y oscurecer/atenuar la imagen */
.stApp::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.4); /* Fondo oscuro semitransparente */
    filter: blur(15px);
    z-index: -1; 
}

/* AJUSTES GENERALES: TODO EL TEXTO OSCURO */
h1 {color: #000000; font-weight: 800; border-bottom: 2px solid #333333; text-shadow: none; background-color: rgba(255, 255, 255, 0.7); padding: 10px; border-radius: 5px;} 
h2 {color: #333333; border-left: 5px solid #333333; padding-left: 10px; text-shadow: none;}
h3 {color: #333333; text-shadow: none;}

/* Texto normal, párrafos y listas */
p, li, .stMarkdown {color: #333333 !important;} 
/* Fondo claro para las cajas de información (st.info, st.success, etc.) */
.stAlert {background-color: rgba(255, 255, 255, 0.9); color: #000000 !important; border-left: 5px solid #333333;} 


/* ESTILO PARA LOS KPIS (Fondo Claro, Texto Oscuro) */
.stMetric>div {
    border: 1px solid #333333; 
    padding: 15px; 
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.9); /* Fondo claro y opaco */
    box-shadow: 3px 3px 8px rgba(0, 0, 0, 0.5); 
    color: #333333; /* Texto general oscuro */
}
.stMetric label {color: #333333;} /* Etiqueta oscura */
.stMetric div[data-testid="stMetricValue"] {color: #000000;} /* Valor oscuro */
.stMetric div[data-testid="stMetricDelta"] {color: #cc0000;} /* Delta en color contrastante */


/* ESTILO PARA LA NAVEGACIÓN DE PESTAÑAS (Fondo Claro, Texto Oscuro) */
.stTabs [data-baseweb="tab-list"] button {
    background-color: rgba(255, 255, 255, 0.9); /* Fondo claro opaco */
    color: #333333; /* Texto oscuro */
    font-weight: bold;
    border-radius: 5px 5px 0px 0px;
    border: 1px solid #333333;
    transition: all 0.2s ease-in-out;
}
.stTabs [data-baseweb="tab-list"] button:hover {
    background-color: rgba(200, 200, 200, 0.9);
    color: #000000;
}
.stTabs [data-baseweb="tab-list"] button:focus {
    border-bottom: 3px solid #333333;
    background-color: rgba(200, 200, 200, 0.95); 
    color: #000000;
}

/* CAMBIO 2: ELIMINACIÓN DEL CSS ESPECÍFICO DE LA BARRA LATERAL 
.css-1d391kg {} */


/* AJUSTE DE COLOR DEL TEXTO EN GRÁFICOS PLOTLY */

/* Títulos de ejes, Leyendas y Etiquetas en general */
.modebar, .legendtext, .xaxislayer-title, .yaxislayer-title {
    color: #000000 !important; 
    fill: #000000 !important; /* Para asegurar el color en SVG/Plotly */
}
/* Forzar texto de los ticks de los ejes */
.xtick, .ytick {
    color: #000000 !important;
    fill: #000000 !important;
}
/* Para asegurar los títulos principales de los gráficos */
.gtitle {
    fill: #000000 !important;
}

/* MEJORAS PARA GRÁFICOS MÁS LEGIBLES */
.plotly-graph-div {
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    background-color: rgba(255, 255, 255, 0.85);
    padding: 10px;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Forzar color negro en TODOS los encabezados */
h1, h2, h3, h4, h5, h6 {
    color: black !important;
}

/* También afecta a títulos creados dentro de st.markdown */
.css-10trblm, .css-1v3fvcr {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)



# ==============================================================================
# LAS FUNCIONES CLAVE DE PREPROCESAMIENTO Y LIMPIEZA DE DATOS
# ==============================================================================

def _corregir_caracteres(texto: Any) -> str:
    # Esta pequeña función se hizo para corregir caracteres uno a uno.
    if pd.isna(texto): return ""
    texto = str(texto).strip()
    for malo, bueno in REEMPLAZOS_CARACTERES.items(): texto = texto.replace(malo, bueno)
    return texto

def limpiar_texto(texto: Any, mayusculas: bool = True, espacios_a_guion: bool = False) -> str:
    # Función general que se usó para estandarizar el formato de las celdas.
    if pd.isna(texto): return ""
    texto = str(texto).strip()
    texto = _corregir_caracteres(texto)
    texto = " ".join(texto.split())
    if mayusculas: texto = texto.upper()
    if espacios_a_guion: texto = texto.replace(" ", "_")
    if texto in ["NAN", "NONE", "NULL", ""]: return ""
    return texto

def estandarizar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
    # Aquí se hizo el trabajo de limpiar los nombres de las columnas para facilitar el manejo.
    df_copy = df.copy()
    columnas_nuevas: List[str] = []
    for col in df_copy.columns:
        col_limpia = limpiar_texto(col, mayusculas=True, espacios_a_guion=True)
        columnas_nuevas.append(col_limpia)
    df_copy.columns = columnas_nuevas
    return df_copy

def limpiar_columnas_texto(df: pd.DataFrame) -> pd.DataFrame:
    # Esta parte se trabajó para asegurar la consistencia del texto en las celdas.
    df_copy = df.copy()
    columnas_texto = df_copy.select_dtypes(include=['object']).columns.tolist()

    for col in columnas_texto:
        usar_guion = col not in ['DEPARTAMENTO', 'MUNICIPIO']
        df_copy[col] = df_copy[col].apply(
            lambda x: limpiar_texto(x, mayusculas=True, espacios_a_guion=usar_guion)
        )
    return df_copy


@st.cache_data
def cargar_y_limpiar_datos(data_input: Any) -> pd.DataFrame:
    """
    Función donde se hizo la carga inicial del CSV, la limpieza de caracteres especiales 
    y la estandarización de columnas.
    """
    if data_input is None: return pd.DataFrame()
        
    try:
        df_delitos = pd.read_csv(data_input)
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

    df = estandarizar_nombres_columnas(df_delitos)
    df = limpiar_columnas_texto(df)
    
    # Se extrajo el año de la fecha.
    if 'FECHA_HECHO' in df.columns:
        df['ANIO'] = pd.to_numeric(df['FECHA_HECHO'].astype(str).str[-4:], errors='coerce').fillna(0).astype(int)
    else: df['ANIO'] = 0 
        
    # Se hizo la unificación de la columna de cantidad.
    columnas_cantidad = [col for col in df.columns if 'CANTIDAD' in col]
    if columnas_cantidad:
        col_cantidad = columnas_cantidad[0]
        if col_cantidad != 'CANTIDAD':
            df = df.rename(columns={col_cantidad: 'CANTIDAD'})
        df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce').fillna(0).astype(int)
    else: df['CANTIDAD'] = 1 

    # Se eliminaron los duplicados encontrados en el set de datos.
    if df.duplicated().sum() > 0:
        df = df.drop_duplicates().reset_index(drop=True)
        
    df = df.fillna("")
    
    # Se hizo la extracción del artículo de delito para una mejor categorización.
    if 'DESCRIPCION_CONDUCTA' in df.columns:
        df['ARTICULO'] = df['DESCRIPCION_CONDUCTA'].astype(str).str.split('.').str[0]
        df['ARTICULO'] = df['ARTICULO'].apply(lambda x: limpiar_texto(x, espacios_a_guion=False))

    return df

def generar_kpis_y_analisis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculamos los KPIs clave para tener un Resumen Ejecutivo rápido de los hallazgos.
    Se hizo un cálculo para la tendencia histórica.
    """
    if df.empty: return {}

    kpis = {}
    kpis["Total Casos"] = df['CANTIDAD'].sum()
    
    min_anio = df['ANIO'].min() if df['ANIO'].min() > 0 else None
    max_anio = df['ANIO'].max() if df['ANIO'].max() > 0 else None
    kpis["Rango Años"] = f"{min_anio} - {max_anio}" if min_anio and max_anio else "N/A"
    
    if 'ARTICULO' in df.columns and len(df['ARTICULO'].unique()) > 1:
        kpis["Delito Mas Frecuente"] = df.groupby('ARTICULO')['CANTIDAD'].sum().idxmax()
        
    if 'DEPARTAMENTO' in df.columns and len(df['DEPARTAMENTO'].unique()) > 1:
        kpis["Departamento Mas Afecstado"] = df.groupby('DEPARTAMENTO')['CANTIDAD'].sum().idxmax()
        
    kpis["Tendencia Diff"] = 0
    kpis["Tendencia General"] = "N/A"
    # Se hizo la lógica para calcular la variación entre el año inicial y final
    if min_anio and max_anio and min_anio != max_anio:
        casos_inicial = df[df['ANIO'] == min_anio]['CANTIDAD'].sum()
        casos_final = df[df['ANIO'] == max_anio]['CANTIDAD'].sum()
        
        if casos_inicial > 0 and casos_final > 0:
            crecimiento_porcentual = ((casos_final - casos_inicial) / casos_inicial) * 100
            kpis["Tendencia Diff"] = crecimiento_porcentual
            if crecimiento_porcentual > 5: kpis["Tendencia General"] = "crecimiento"
            elif crecimiento_porcentual < -5: kpis["Tendencia General"] = "disminución"
            else: kpis["Tendencia General"] = "estable"
        elif casos_final > 0 and casos_inicial == 0: kpis["Tendencia General"] = "crecimiento explosivo"
        else: kpis["Tendencia General"] = "datos insuficientes"
        
    return kpis

# ==============================================================================
# FUNCIONES DE VISUALIZACIÓN (MEJORADAS)
# ==============================================================================

def generar_tendencia_anual(df: pd.DataFrame, theme: Optional[str] = None) -> go.Figure:
    """Se hizo este gráfico de barras para visualizar la tendencia histórica por intervalos de año."""
    if df.empty or 'ANIO' not in df.columns: return go.Figure()
    max_anio = df['ANIO'].max() if not df.empty else 2025
    bins = [2000, 2005, 2010, 2015, 2020, max_anio + 1]
    labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]
    df_tendencia = df[(df['ANIO'] >= 2000) & (df['ANIO'] <= max_anio)].copy()
    df_tendencia['INTERVALO_ANIO'] = pd.cut(df_tendencia['ANIO'], bins=bins, labels=labels, right=False)
    df_tendencia_intervalos = (df_tendencia.groupby('INTERVALO_ANIO', observed=False)['CANTIDAD'].sum().reset_index())

    fig = px.bar(
        df_tendencia_intervalos, 
        x='INTERVALO_ANIO', 
        y='CANTIDAD', 
        color='CANTIDAD',
        color_continuous_scale=px.colors.sequential.Tealgrn,  # Mejor escala de color
        text_auto=True,  # Cambiado para mejor visualización
        template=theme
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}', 
        textposition='outside',
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.9
    )
    
    fig.update_layout(
        title_text="<b>Tendencia de Casos por Intervalos de Año</b>", 
        xaxis_title="Intervalo de Años", 
        yaxis_title="Número de Casos", 
        margin=dict(t=50, b=50, l=50, r=50),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        font=dict(size=12, color='#333333'),
        title_font=dict(size=16, color='#000000'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14)
        )
    )
    return fig


def generar_top_conductas(df: pd.DataFrame, n_top: int = 8, theme: Optional[str] = None) -> go.Figure:
    """Se hizo este gráfico de barras horizontales para identificar el Top N de Artículos de delito (Visión General)."""
    if df.empty or 'ARTICULO' not in df.columns: return go.Figure()
    df_conducta_top = (df.groupby('ARTICULO')['CANTIDAD'].sum().nlargest(n_top).reset_index())

    fig = px.bar(
        df_conducta_top, 
        x='CANTIDAD', 
        y='ARTICULO', 
        orientation='h', 
        color='CANTIDAD',
        color_continuous_scale=px.colors.sequential.Plasma_r,  # Invertido para mejor visualización
        text_auto=True,  # Mejor visualización de valores
        template=theme
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}',
        textposition='outside',
        marker_line_color='rgb(8,48,107)',
        marker_line_width=1.5,
        opacity=0.9
    )
    
    fig.update_layout(
        title_text=f"<b>Top {n_top} Artículos de Conductas Delictivas Ambientales</b>", 
        xaxis_title="Número de Casos", 
        yaxis_title="Artículo de Delito", 
        yaxis={'autorange': "reversed", 'categoryorder': 'total ascending'}, 
        margin=dict(t=50, b=50, l=150, r=50),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        font=dict(size=12, color='#333333'),
        title_font=dict(size=16, color='#000000'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14)
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=11)
        )
    )
    return fig


def generar_top_departamentos(df: pd.DataFrame, n_top: int = 10, theme: Optional[str] = None) -> go.Figure:
    """Este gráfico se hizo para mostrar el Top N de departamentos más afectados, el foco geográfico."""
    if df.empty or 'DEPARTAMENTO' not in df.columns: return go.Figure()
    df_depto_top = (df.groupby('DEPARTAMENTO')['CANTIDAD'].sum().nlargest(n_top).reset_index())

    fig = px.bar(
        df_depto_top, 
        x='DEPARTAMENTO', 
        y='CANTIDAD', 
        color='CANTIDAD',
        color_continuous_scale=px.colors.sequential.Oranges,
        text_auto=True,  # Mejor visualización
        template=theme
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}',
        textposition='outside',
        marker_line_color='rgb(140,81,10)',
        marker_line_width=1.5,
        opacity=0.9
    )
    
    fig.update_layout(
        title_text=f"<b>Top {n_top} Departamentos más Afectados</b>", 
        xaxis_title="Departamento", 
        yaxis_title="Número de Casos", 
        xaxis_tickangle=-45, 
        margin=dict(t=50, b=100, l=50, r=50),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        font=dict(size=12, color='#333333'),
        title_font=dict(size=16, color='#000000'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14)
        )
    )
    return fig


def generar_heatmap_conducta_anual(df: pd.DataFrame, theme: Optional[str] = None) -> go.Figure:
    """Se hizo un Mapa de calor para mostrar la evolución de los delitos por año (usando Escala Log para suavizar)."""
    if df.empty or 'ARTICULO' not in df.columns or 'ANIO' not in df.columns: return go.Figure()
    df_heatmap_data = (df.groupby(['ANIO', 'ARTICULO'])['CANTIDAD'].sum().reset_index())
    df_heatmap_pivot = df_heatmap_data.pivot_table(index='ARTICULO', columns='ANIO', values='CANTIDAD', fill_value=0)
    df_heatmap_log = np.log1p(df_heatmap_pivot)

    fig = px.imshow(
        df_heatmap_log, 
        x=df_heatmap_log.columns.astype(str), 
        y=df_heatmap_log.index,
        color_continuous_scale='YlOrRd',
        aspect="auto", 
        template=theme,
        text_auto=False,
        labels=dict(color="Log(1 + Casos)")
    )

    # Mejoras en la visualización
    fig.update_layout(
        title_text="<b>Mapa de Calor: Evolución Temporal por Tipo de Delito (Log)</b>", 
        xaxis_title="Año", 
        yaxis_title="Artículo de Delito", 
        xaxis_tickangle=-45, 
        height=650, 
        margin=dict(t=50, b=50, l=150, r=50),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        font=dict(size=12, color='#333333'),
        title_font=dict(size=16, color='#000000'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14),
            tickfont=dict(size=10)
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=9)
        )
    )
    fig.update_coloraxes(
        colorbar_title='Log(1 + Casos)',
        colorbar_title_font=dict(size=12),
        colorbar_tickfont=dict(size=10)
    )
    
    # Agregar anotaciones para valores altos
    if len(df_heatmap_pivot.columns) * len(df_heatmap_pivot.index) <= 50:  # Solo si no hay demasiadas celdas
        for i, articulo in enumerate(df_heatmap_pivot.index):
            for j, anio in enumerate(df_heatmap_pivot.columns):
                valor = df_heatmap_pivot.iloc[i, j]
                if valor > 0:  # Solo mostrar valores positivos
                    fig.add_annotation(
                        x=str(anio),
                        y=articulo,
                        text=str(int(valor)),
                        showarrow=False,
                        font=dict(size=8, color='white' if df_heatmap_log.iloc[i, j] > df_heatmap_log.values.mean() else 'black')
                    )
    
    return fig


def generar_evolucion_top5_conductas(df: pd.DataFrame, theme: Optional[str] = None) -> go.Figure:
    """Se hizo este gráfico de líneas para rastrear la evolución anual de las 5 conductas más frecuentes."""
    if df.empty or 'ARTICULO' not in df.columns or 'ANIO' not in df.columns: return go.Figure()

    top5_articulos = df.groupby('ARTICULO')['CANTIDAD'].sum().nlargest(5).index.tolist()
    df_top5_filtrado = df[df['ARTICULO'].isin(top5_articulos)].copy()
    df_tendencia = (df_top5_filtrado.groupby(['ANIO', 'ARTICULO'])['CANTIDAD'].sum().reset_index())
    
    fig = px.line(
        df_tendencia, 
        x='ANIO', 
        y='CANTIDAD', 
        color='ARTICULO', 
        markers=True, 
        line_shape='spline', 
        template=theme,
        line_dash_sequence=['solid', 'dash', 'dot', 'dashdot', 'longdash'],
        symbol_sequence=['circle', 'square', 'diamond', 'cross', 'x']
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        mode='lines+markers',
        marker=dict(size=8),
        line=dict(width=3)
    )
    
    fig.update_layout(
        title="<b>Evolución Anual de las 5 Conductas más Frecuentes</b>",
        xaxis_title="Año", 
        yaxis_title="Cantidad de Casos", 
        legend_title="Artículo", 
        hovermode="x unified",
        font=dict(color="#333333"),
        hoverlabel=dict(
            bgcolor="white", 
            font_color="black",
            font_size=12
        ), 
        margin=dict(t=50, b=50, l=50, r=50),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        title_font=dict(size=16, color='#000000'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14),
            tickformat="d"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14)
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=11)
        )
    )
    
    # Agregar área sombreada para mejor visualización
    for trace in fig.data:
        fig.add_trace(go.Scatter(
            x=trace.x,
            y=trace.y,
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip',
            fill='toself',
            fillcolor=trace.line.color.replace('rgb', 'rgba').replace(')', ', 0.1)')
        ))
    
    return fig


def generar_distribucion_top_depto_bar(df: pd.DataFrame, depto_critico: str, theme: Optional[str] = None) -> go.Figure:
    """Generamos un gráfico de barras horizontal de la distribución de delitos en el departamento más afectado."""
    if df.empty or 'DEPARTAMENTO' not in df.columns or depto_critico == "N/A": return go.Figure()
    
    df_filtrado = df[df['DEPARTAMENTO'] == depto_critico].copy()
    df_distribucion = df_filtrado.groupby('ARTICULO')['CANTIDAD'].sum().nlargest(5).reset_index()
    
    fig = px.bar(
        df_distribucion, 
        x='CANTIDAD', 
        y='ARTICULO', 
        orientation='h',
        title=f'Composición del Delito en el Foco Geográfico: **{depto_critico}**',
        template=theme,
        color='CANTIDAD',
        color_continuous_scale=px.colors.sequential.Reds,
        text_auto=True
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}',
        textposition='outside',
        marker_line_color='rgb(103,0,13)',
        marker_line_width=1.5,
        opacity=0.9
    )
    
    fig.update_layout(
        yaxis={'autorange': "reversed", 'categoryorder': 'total ascending'}, 
        yaxis_title="Artículo de Delito", 
        xaxis_title="Número de Casos", 
        margin=dict(t=50, b=50, l=150, r=50),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        font=dict(size=12, color='#333333'),
        title_font=dict(size=15, color='#000000'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14)
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=11)
        )
    )
    return fig


def generar_distribucion_mensual(df: pd.DataFrame, delito_critico: str, theme: Optional[str] = None) -> go.Figure:
    """Generamos un gráfico de barras para la distribución mensual del delito más frecuente (Estacionalidad)."""
    if df.empty or 'FECHA_HECHO' not in df.columns or delito_critico == "N/A": return go.Figure()
    
    df_filtrado = df[df['ARTICULO'] == delito_critico].copy()
    
    try:
        # Se hizo la conversión segura a datetime
        df_filtrado['FECHA_DT'] = pd.to_datetime(df_filtrado['FECHA_HECHO'], errors='coerce')
        df_filtrado = df_filtrado.dropna(subset=['FECHA_DT'])
    except Exception: return go.Figure()
        
    df_filtrado['MES'] = df_filtrado['FECHA_DT'].dt.month
    df_mensual = (df_filtrado.groupby('MES')['CANTIDAD'].sum().reset_index())
    
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    df_mensual['NOMBRE_MES'] = df_mensual['MES'].apply(lambda x: meses[x-1])
    
    fig = px.bar(
        df_mensual, 
        x='NOMBRE_MES', 
        y='CANTIDAD', 
        title=f'Estacionalidad Mensual del Delito Prioritario: **{delito_critico}**',
        template=theme,
        color='CANTIDAD',
        color_continuous_scale=px.colors.sequential.Viridis,
        text_auto=True,
        category_orders={"NOMBRE_MES": meses}
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}',
        textposition='outside',
        marker_line_color='rgb(68,1,84)',
        marker_line_width=1.5,
        opacity=0.9
    )
    
    fig.update_layout(
        xaxis_title="Mes", 
        yaxis_title="Casos Acumulados", 
        margin=dict(t=50, b=50, l=50, r=50),
        plot_bgcolor='rgba(255,255,255,0.9)',
        paper_bgcolor='rgba(255,255,255,0.9)',
        font=dict(size=12, color='#333333'),
        title_font=dict(size=15, color='#000000'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14),
            tickangle=0
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200,200,200,0.3)',
            title_font=dict(size=14)
        )
    )
    return fig


# ==============================================================================
# APLICACIÓN PRINCIPAL DE STREAMLIT (Montaje Final)
# ==============================================================================

def main():
    """Se hizo el montaje del layout minimalista y estructurado usando pestañas (st.tabs)."""
    
    # --- 1. INICIALIZACIÓN DE VARIABLES CRÍTICAS ---
    df = pd.DataFrame()
    plotly_theme = None
    data_input = None

    
    st.title("🌎 Dashboard-Delitos Ambientales")
    st.markdown("Análisis Exploratorio de Tendencias y Focos Críticos.")
    
    # --- SECCIÓN: INTEGRANTES DEL GRUPO (Ajuste solicitado) ---
    st.info("""
    ✨ **GRUPO 3 Talento_tech.**
    
    **Integrantes del Equipo:**
    * Edwin hernan velez urrego
    * Paola andrea garcia tangarife
    * yeraldin campo espinal
    * valentina restrepo angel
    * sara melisa londoño
    
    """)
    st.markdown("---")
    
    
    # 🔗 CONFIGURACIÓN Y CARGA DE DATOS 
   
    with st.expander("🛠️ Configuración y Carga de Datos"):
        
        # Opción de carga de archivo (Define data_input)
        uploaded_file = st.file_uploader(
            "1. Cargar archivo CSV:",
            type=["csv"],
            help="Sube tu archivo 'BD_Delitos_ambientales.csv' aquí."
        )
        archivo_path_default = "BD_Delitos_ambientales.csv"
        data_input = uploaded_file if uploaded_file is not None else archivo_path_default
        
        # Configuración del Tema (Define plotly_theme)
        theme_options = {
            "Claro (Default y Alto Contraste)": "plotly_white", 
            "Sin Tema (Para usar solo CSS)": None,
        }
        selected_theme_key = st.selectbox(
            "Tema de Visualización:", 
            list(theme_options.keys())
        )
        # Asignación segura del tema
        plotly_theme = theme_options[selected_theme_key]
        
        st.subheader("Estado de Procesamiento")

    # --- Carga de Datos y Verificación de la Integridad ---
    with st.spinner('Cargando, limpiando y estandarizando datos...'):
        df = cargar_y_limpiar_datos(data_input) 

    # Verificación de datos
    if df.empty:
        st.error("⚠️ No se pudo cargar o procesar el archivo de datos. Por favor, suba un archivo CSV válido.")
        return 
    
    st.success("✅ ¡Datos cargados y listos para análisis!")
    with st.expander("Ver Metadatos del DataFrame"):
        st.dataframe(df.head(3))
        st.info(f"Registros finales: **{len(df):,}**")
    
    st.markdown("---") # Separador entre el estado de carga y los KPIs
    
    # --------------------------------------------------------------------------
    # RESUMEN (KPIs DINÁMICOS)
    # --------------------------------------------------------------------------
    st.subheader("📊 Panorama General: KPIs Clave")
    
    kpis = generar_kpis_y_analisis(df)
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    with col_kpi1: 
        st.metric(
            label="🚨 Total Casos Registrados", 
            value=f"{kpis.get('Total Casos', 0):,}",
            delta=kpis.get('Rango Años', 'N/A')
        )

    with col_kpi2:
        st.metric(
            label="💥 Foco de Delito (Artículo Principal)",
            value=kpis.get('Delito Mas Frecuente', 'N/A')
        )

    with col_kpi3:
        st.metric(
            label="📍 Geografía Crítica (Departamento)",
            value=kpis.get('Departamento Mas Afecstado', 'N/A')
        )

    tendencia_value = f"{kpis.get('Tendencia General', 'N/A').upper()}"
    tendencia_delta = kpis.get('Tendencia Diff', 0)
    
    with col_kpi4:
        st.metric(
            label="📈 Variación Histórica (%)",
            value=tendencia_value,
            delta=f"{tendencia_delta:.1f}% vs Año Inicial",
            delta_color="inverse" if tendencia_delta < -5 else "normal"
        )
        
    st.markdown("---") # Separador entre los KPIs y las Pestañas

    # --------------------------------------------------------------------------
    # 📑 ESTRUCTURA MODULAR CON PESTAÑAS
    # --------------------------------------------------------------------------
    
    tab1, tab2, tab3 = st.tabs(["📉 Evolución Temporal", "🗺️ Concentración Geográfica", "🎯 Focos de Decisión"])

    # --- PESTAÑA EVOLUCIÓN TEMPORAL ---
    with tab1:
        st.header("Análisis de la Dinámica del Delito Ambiental")
        
        col_t1_1, col_t1_2 = st.columns(2)
        
        with col_t1_1:
            fig_evolucion = generar_evolucion_top5_conductas(df, theme=plotly_theme)
            st.plotly_chart(fig_evolucion, use_container_width=True)

        with col_t1_2:
            fig_heatmap = generar_heatmap_conducta_anual(df, theme=plotly_theme)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
        st.info("💡 **Análisis de la Pestaña:** El gráfico de líneas muestra la trayectoria individual de los delitos más grandes. El Mapa de Calor (**se hizo** con escala logarítmica) revela visualmente cuáles delitos persisten o emergen con fuerza a lo largo de los años.")

    # --- PESTAÑA CONCENTRACIÓN GEOGRÁFICA Y TIPOLÓGICA ---
    with tab2:
        st.header("Distribución de Casos por Ubicación y Tipología")
        
        col_t2_1, col_t2_2 = st.columns(2)

        with col_t2_1:
            fig_depto = generar_top_departamentos(df, theme=plotly_theme)
            st.plotly_chart(fig_depto, use_container_width=True)
        
        with col_t2_2:
            fig_conducta = generar_top_conductas(df, theme=plotly_theme)
            st.plotly_chart(fig_conducta, use_container_width=True)
            
        st.info("💡 **Análisis de la Pestaña:** Se hizo una comparación de las concentraciones por Departamento (dónde ocurre) y por Artículo (qué ocurre). El gráfico de tendencia a largo plazo nos sirve de contexto general.")
        
        fig_tendencia = generar_tendencia_anual(df, theme=plotly_theme)
        st.plotly_chart(fig_tendencia, use_container_width=True)


    # --- PESTAÑA FOCOS DE DECISIÓN (Conclusiones Visuales) ---
    with tab3:
        st.header("Recomendaciones Estratégicas Basadas en Hallazgos")
        st.markdown("**Se trabajó** para que la estrategia de mitigación se enfoque en los puntos de mayor impacto: Geografía Crítica y Estacionalidad.")
        
        # Uso de kpis para obtener los focos
        depto_critico = kpis.get('Departamento Mas Afecstado', 'N/A')
        delito_critico = kpis.get('Delito Mas Frecuente', 'N/A')
        
        col_t3_1, col_t3_2 = st.columns(2)
        
        # Desglose Geográfico (Gráfico de barras horizontal)
        with col_t3_1:
            st.subheader(f"📍 1. Composición del Delito en: {depto_critico}")
            st.markdown(f"**Recomendación:** Priorizar los **2-3 artículos** más largos en este gráfico para maximizar la reducción del delito en **{depto_critico}**.")
            
            if depto_critico != 'N/A':
                fig_dist_depto = generar_distribucion_top_depto_bar(df, depto_critico, theme=plotly_theme)
                st.plotly_chart(fig_dist_depto, use_container_width=True)
            else:
                st.warning("Datos insuficientes para desglose geográfico.")
        
        # Estacionalidad del Delito Principal
        with col_t3_2:
            st.subheader(f"⏱️ 2. Estacionalidad del Delito Principal: {delito_critico}")
            st.markdown(f"**Recomendación:** Asignar recursos operativos 1-2 meses antes de los **picos de casos** observados en este gráfico de estacionalidad.")
            
            if delito_critico != 'N/A':
                fig_dist_mensual = generar_distribucion_mensual(df, delito_critico, theme=plotly_theme)
                st.plotly_chart(fig_dist_mensual, use_container_width=True)
            else:
                st.warning("Datos insuficientes para análisis de estacionalidad.")

    # --- Pie de página profesional ---
    st.markdown("---")
    st.caption("Dashboard desarrollado para el **Proyecto Final de Análisis de Datos** | Diseño con Streamlit y Plotly.")


if __name__ == '__main__':
    main()
