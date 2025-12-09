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

# Diccionario de reemplazos (CORREGIDO)
REEMPLAZOS_CARACTERES: Dict[str, str] = {
    "Ã‘O": "NO", "Ã‘o": "NO", "Ã‘": "N", "Ã±": "N", "Ñ": "N", "ñ": "N",
    "Ã¡": "A", "Ã©": "E", "Ã­": "I", "Ã³": "O", "Ãº": "U", "Á": "A", "É": "E",
    "Í": "I", "Ó": "O", "Ú": "U", "ÃÁ": "A", "ÃÉ": "E", "ÃÍ": "I", "ÃÓ": "O", 
    "ÃÚ": "U", "ÃA": "A", "ÃE": "E", "ÃI": "I", "ÃO": "O", "ÃU": "U", "á": "A", 
    "é": "E", "í": "I", "ó": "O", "ú": "U", "Ã¼": "U", "Ãœ": "U", "Ü": "U", 
    "ü": "U", "¿": "", "?": "", "¡": "", "!": "", "Â¿": "", "Â¡": "",
    "ï¿½": "", "Â": "", "â€œ": "", "â€": "", "â€™": "", "â€¢": "", "â€“": "",
    "â€”": "", "\u2122": "", "\u00AE": "", "\u00A9": "", "\u00BA": "", "\u00AA": "", 
    "\u20AC": "", "$": "", "\u00A3": "", "\u00BC": "", "\u00BD": "", "\u00BE": "",
}

# --- ESTILO CSS CON FONDO NEGRO PROFESIONAL ---
st.markdown("""
<style>
/* FONDO NEGRO PROFESIONAL */
.stApp {
    background-color: #0a0a0a !important;
    background-image: none !important;
    color: #ffffff;
}

/* ELIMINAR CAPA DE SUPERPOSICIÓN ANTERIOR */
.stApp::before {
    content: none;
}

/* AJUSTES GENERALES: TODO EL TEXTO CLARO */
h1 {
    color: #ffffff !important; 
    font-weight: 800; 
    border-bottom: 3px solid #00d4ff;
    text-shadow: 0 2px 4px rgba(0, 212, 255, 0.3);
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(10, 10, 10, 0.9));
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    border-left: 5px solid #00d4ff;
} 

h2 {
    color: #ffffff !important;
    border-left: 4px solid #00ff88;
    padding-left: 12px;
    background: rgba(20, 20, 20, 0.7);
    padding: 10px;
    border-radius: 5px;
    margin-top: 20px;
}

h3 {
    color: #ffffff !important;
    border-left: 3px solid #ff6b00;
    padding-left: 10px;
    background: rgba(30, 30, 30, 0.6);
    padding: 8px;
    border-radius: 4px;
}

/* Texto normal, párrafos y listas */
p, li, .stMarkdown, .stText {
    color: #e0e0e0 !important;
} 

/* Fondo para las cajas de información */
.stAlert {
    background: rgba(25, 25, 35, 0.9) !important;
    color: #ffffff !important;
    border-left: 5px solid #00d4ff !important;
    border-radius: 8px;
    border: 1px solid rgba(0, 212, 255, 0.3);
}

.stSuccess {
    background: rgba(25, 35, 25, 0.9) !important;
    border-left: 5px solid #00ff88 !important;
}

.stWarning {
    background: rgba(35, 25, 25, 0.9) !important;
    border-left: 5px solid #ff6b00 !important;
}

.stError {
    background: rgba(35, 25, 25, 0.9) !important;
    border-left: 5px solid #ff4444 !important;
}

/* ESTILO PARA LOS KPIS (Fondo Oscuro, Texto Claro) */
.stMetric>div {
    border: 1px solid rgba(0, 212, 255, 0.4) !important;
    padding: 20px !important;
    border-radius: 10px !important;
    background: linear-gradient(145deg, rgba(20, 25, 35, 0.95), rgba(15, 20, 30, 0.95)) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5) !important;
    color: #ffffff !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stMetric>div:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 212, 255, 0.2) !important;
    border-color: rgba(0, 212, 255, 0.7) !important;
}

.stMetric label {
    color: #00d4ff !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}

.stMetric div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.stMetric div[data-testid="stMetricDelta"] {
    color: #00ff88 !important;
    font-weight: 600 !important;
}

/* ESTILO PARA LA NAVEGACIÓN DE PESTAÑAS (Fondo Oscuro) */
.stTabs [data-baseweb="tab-list"] {
    gap: 5px;
    padding: 5px;
    background: rgba(20, 20, 30, 0.8);
    border-radius: 10px;
}

.stTabs [data-baseweb="tab-list"] button {
    background: rgba(30, 30, 40, 0.8) !important;
    color: #b0b0b0 !important;
    font-weight: 600;
    border-radius: 8px !important;
    border: 1px solid rgba(100, 100, 150, 0.3) !important;
    transition: all 0.3s ease-in-out;
    padding: 10px 20px;
    margin: 0 2px;
}

.stTabs [data-baseweb="tab-list"] button:hover {
    background: rgba(40, 40, 60, 0.9) !important;
    color: #ffffff !important;
    border-color: rgba(0, 212, 255, 0.5) !important;
    transform: translateY(-2px);
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 150, 255, 0.2)) !important;
    color: #00d4ff !important;
    border: 1px solid rgba(0, 212, 255, 0.7) !important;
    box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
}

/* ESTILO PARA EXPANDERS */
.streamlit-expanderHeader {
    background: rgba(25, 25, 35, 0.9) !important;
    color: #ffffff !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0, 212, 255, 0.3) !important;
    font-weight: 600;
}

.streamlit-expanderContent {
    background: rgba(20, 20, 30, 0.8) !important;
    border-radius: 0 0 8px 8px !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-top: none !important;
}

/* ESTILO PARA TABLAS */
.stDataFrame {
    background: rgba(20, 20, 30, 0.9) !important;
    border-radius: 8px;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
}

/* ESTILO PARA SELECTBOX Y CONTROLES */
.stSelectbox, .stFileUploader {
    background: rgba(25, 25, 35, 0.9) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0, 212, 255, 0.3) !important;
}

/* ESTILO PARA GRÁFICOS PLOTLY */
.plotly-graph-div {
    background: rgba(15, 15, 25, 0.95) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4) !important;
    padding: 15px !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.plotly-graph-div:hover {
    box-shadow: 0 12px 40px rgba(0, 212, 255, 0.1) !important;
    border-color: rgba(0, 212, 255, 0.4) !important;
}

/* ESTILO PARA SEPARADORES */
hr {
    border: none;
    height: 2px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.5), transparent);
    margin: 30px 0;
}

/* ESTILO PARA FOOTER */
.stCaption {
    color: #888888 !important;
    text-align: center;
    padding: 20px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    margin-top: 30px;
}

/* ESTILO PARA BOTONES */
.stButton button {
    background: linear-gradient(135deg, #0066cc, #00d4ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.stButton button:hover {
    background: linear-gradient(135deg, #0052a3, #00b8e6) !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 212, 255, 0.3) !important;
}

/* ESTILO PARA SPINNER */
.stSpinner > div {
    border-color: #00d4ff transparent transparent transparent !important;
}

/* AJUSTES DE SCROLLBAR */
::-webkit-scrollbar {
    width: 10px;
    background: rgba(20, 20, 30, 0.8);
}

::-webkit-scrollbar-track {
    background: rgba(30, 30, 40, 0.6);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #00d4ff, #0066cc);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #00e4ff, #0077dd);
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
# FUNCIONES DE VISUALIZACIÓN (MEJORADAS PARA FONDO NEGRO)
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
        color_continuous_scale='Viridis',  # Escala que funciona bien en fondo oscuro
        text_auto=True,
        template='plotly_dark'  # Tema oscuro para Plotly
    )
    
    # Mejoras en la visualización para fondo negro
    fig.update_traces(
        texttemplate='%{value:,.0f}', 
        textposition='outside',
        textfont=dict(color='#ffffff', size=12),
        marker_line_color='rgba(255, 255, 255, 0.3)',
        marker_line_width=1,
        opacity=0.9
    )
    
    fig.update_layout(
        title_text="<b>📈 Tendencia de Casos por Intervalos de Año</b>", 
        title_font=dict(size=18, color='#ffffff'),
        xaxis_title="Intervalo de Años", 
        yaxis_title="Número de Casos", 
        margin=dict(t=60, b=50, l=50, r=50),
        plot_bgcolor='rgba(15, 15, 25, 0.8)',
        paper_bgcolor='rgba(15, 15, 25, 0.5)',
        font=dict(size=12, color='#e0e0e0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0')
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
        color_continuous_scale='Plasma',  # Escala vibrante para fondo oscuro
        text_auto=True,
        template='plotly_dark'
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}',
        textposition='outside',
        textfont=dict(color='#ffffff', size=11),
        marker_line_color='rgba(255, 255, 255, 0.3)',
        marker_line_width=1,
        opacity=0.9
    )
    
    fig.update_layout(
        title_text=f"<b>🔥 Top {n_top} Artículos de Conductas Delictivas Ambientales</b>", 
        title_font=dict(size=18, color='#ffffff'),
        xaxis_title="Número de Casos", 
        yaxis_title="Artículo de Delito", 
        margin=dict(t=60, b=50, l=200, r=50),
        plot_bgcolor='rgba(15, 15, 25, 0.8)',
        paper_bgcolor='rgba(15, 15, 25, 0.5)',
        font=dict(size=12, color='#e0e0e0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0')
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0', size=11),
            autorange="reversed",
            categoryorder='total ascending'
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
        color_continuous_scale='Oranges',
        text_auto=True,
        template='plotly_dark'
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}',
        textposition='outside',
        textfont=dict(color='#ffffff', size=11),
        marker_line_color='rgba(255, 255, 255, 0.3)',
        marker_line_width=1,
        opacity=0.9
    )
    
    fig.update_layout(
        title_text=f"<b>📍 Top {n_top} Departamentos más Afectados</b>", 
        title_font=dict(size=18, color='#ffffff'),
        xaxis_title="Departamento", 
        yaxis_title="Número de Casos", 
        xaxis_tickangle=-45, 
        margin=dict(t=60, b=120, l=50, r=50),
        plot_bgcolor='rgba(15, 15, 25, 0.8)',
        paper_bgcolor='rgba(15, 15, 25, 0.5)',
        font=dict(size=12, color='#e0e0e0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0', size=10)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0')
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
        template='plotly_dark',
        text_auto=False,
        labels=dict(color="Log(1 + Casos)")
    )

    # Mejoras en la visualización
    fig.update_layout(
        title_text="<b>🌡️ Mapa de Calor: Evolución Temporal por Tipo de Delito (Log)</b>", 
        title_font=dict(size=18, color='#ffffff'),
        xaxis_title="Año", 
        yaxis_title="Artículo de Delito", 
        xaxis_tickangle=-45, 
        height=700, 
        margin=dict(t=70, b=50, l=200, r=50),
        plot_bgcolor='rgba(15, 15, 25, 0.8)',
        paper_bgcolor='rgba(15, 15, 25, 0.5)',
        font=dict(size=12, color='#e0e0e0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0', size=10)
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0', size=9)
        )
    )
    fig.update_coloraxes(
        colorbar_title='Log(1 + Casos)',
        colorbar_title_font=dict(size=12, color='#e0e0e0'),
        colorbar_tickfont=dict(size=10, color='#b0b0b0')
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
        template='plotly_dark',
        line_dash_sequence=['solid', 'dash', 'dot', 'dashdot', 'longdash'],
        symbol_sequence=['circle', 'square', 'diamond', 'cross', 'x']
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        mode='lines+markers',
        marker=dict(size=9),
        line=dict(width=3.5)
    )
    
    fig.update_layout(
        title="<b>📊 Evolución Anual de las 5 Conductas más Frecuentes</b>",
        title_font=dict(size=18, color='#ffffff'),
        xaxis_title="Año", 
        yaxis_title="Cantidad de Casos", 
        legend_title="Artículo", 
        hovermode="x unified",
        font=dict(color="#e0e0e0"),
        hoverlabel=dict(
            bgcolor="rgba(20, 20, 30, 0.9)", 
            font_color="white",
            font_size=12
        ), 
        margin=dict(t=70, b=50, l=50, r=50),
        plot_bgcolor='rgba(15, 15, 25, 0.8)',
        paper_bgcolor='rgba(15, 15, 25, 0.5)',
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickformat="d",
            tickfont=dict(color='#b0b0b0')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0')
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color='#e0e0e0'),
            bgcolor='rgba(20, 20, 30, 0.7)',
            bordercolor='rgba(0, 212, 255, 0.3)',
            borderwidth=1
        )
    )
    
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
        title=f'<b>📋 Composición del Delito en: {depto_critico}</b>',
        template='plotly_dark',
        color='CANTIDAD',
        color_continuous_scale='Reds',
        text_auto=True
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}',
        textposition='outside',
        textfont=dict(color='#ffffff', size=11),
        marker_line_color='rgba(255, 255, 255, 0.3)',
        marker_line_width=1,
        opacity=0.9
    )
    
    fig.update_layout(
        title_font=dict(size=16, color='#ffffff'),
        yaxis_title="Artículo de Delito", 
        xaxis_title="Número de Casos", 
        margin=dict(t=60, b=50, l=200, r=50),
        plot_bgcolor='rgba(15, 15, 25, 0.8)',
        paper_bgcolor='rgba(15, 15, 25, 0.5)',
        font=dict(size=12, color='#e0e0e0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0')
        ),
        yaxis=dict(
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0', size=11),
            autorange="reversed",
            categoryorder='total ascending'
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
        title=f'<b>📅 Estacionalidad Mensual del Delito: {delito_critico}</b>',
        template='plotly_dark',
        color='CANTIDAD',
        color_continuous_scale='Viridis',
        text_auto=True,
        category_orders={"NOMBRE_MES": meses}
    )
    
    # Mejoras en la visualización
    fig.update_traces(
        texttemplate='%{value:,.0f}',
        textposition='outside',
        textfont=dict(color='#ffffff', size=11),
        marker_line_color='rgba(255, 255, 255, 0.3)',
        marker_line_width=1,
        opacity=0.9
    )
    
    fig.update_layout(
        title_font=dict(size=16, color='#ffffff'),
        xaxis_title="Mes", 
        yaxis_title="Casos Acumulados", 
        margin=dict(t=60, b=50, l=50, r=50),
        plot_bgcolor='rgba(15, 15, 25, 0.8)',
        paper_bgcolor='rgba(15, 15, 25, 0.5)',
        font=dict(size=12, color='#e0e0e0'),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickangle=0,
            tickfont=dict(color='#b0b0b0')
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(100, 100, 150, 0.2)',
            title_font=dict(size=14, color='#00d4ff'),
            tickfont=dict(color='#b0b0b0')
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
    plotly_theme = 'plotly_dark'  # Tema oscuro por defecto
    data_input = None

    # Título principal con estilo profesional
    col_title1, col_title2, col_title3 = st.columns([1, 3, 1])
    with col_title2:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1 style="color: #00d4ff; font-size: 2.8rem; margin-bottom: 10px;">
                🌍 DASHBOARD DE DELITOS AMBIENTALES
            </h1>
        </div>
        """, unsafe_allow_html=True)

    
    # 🔗 CONFIGURACIÓN Y CARGA DE DATOS 
 with st.expander("⚙️ **CONFIGURACIÓN Y CARGA DE DATOS**", expanded=True):
    
    # Versión simple centrada
    st.markdown("""
    <div style="text-align: center;">
    """, unsafe_allow_html=True)
    
    # Opción de carga de archivo
    uploaded_file = st.file_uploader(
        "**📁 Subir archivo CSV:**",
        type=["csv"],
        help="Sube tu archivo 'BD_Delitos_ambientales.csv' aquí."
    )
    archivo_path_default = "BD_Delitos_ambientales.csv"
    data_input = uploaded_file if uploaded_file is not None else archivo_path_default
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.subheader("🔍 Estado de Procesamiento")

    # --- Carga de Datos y Verificación de la Integridad ---
    with st.spinner('🔄 Cargando, limpiando y estandarizando datos...'):
        df = cargar_y_limpiar_datos(data_input) 

    # Verificación de datos
    if df.empty:
        st.error("""
        ⚠️ **No se pudo cargar o procesar el archivo de datos.**  
        Por favor, suba un archivo CSV válido o verifique la ruta del archivo.
        """)
        return 
    
    st.success("✅ **¡Datos cargados y listos para análisis!**")
    
    with st.expander("📊 **VISTA PREVIA DE LOS DATOS**"):
        col_data1, col_data2 = st.columns([2, 1])
        with col_data1:
            st.dataframe(df.head(5).style.set_properties(**{
                'background-color': 'rgba(20, 20, 30, 0.7)',
                'color': '#e0e0e0',
                'border-color': 'rgba(0, 212, 255, 0.2)'
            }))
        with col_data2:
            st.metric("**Registros Totales**", f"{len(df):,}")
            st.metric("**Columnas**", len(df.columns))
            st.metric("**Años Cubiertos**", f"{df['ANIO'].min()} - {df['ANIO'].max()}")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --------------------------------------------------------------------------
    # RESUMEN (KPIs DINÁMICOS)
    # --------------------------------------------------------------------------
    st.subheader("📊 **PANORAMA GENERAL: KPIs CLAVE**")
    
    kpis = generar_kpis_y_analisis(df)
    
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    with col_kpi1: 
        st.metric(
            label="🚨 **TOTAL CASOS REGISTRADOS**", 
            value=f"{kpis.get('Total Casos', 0):,}",
            delta=kpis.get('Rango Años', 'N/A'),
            delta_color="off"
        )

    with col_kpi2:
        st.metric(
            label="💥 **DELITO PRINCIPAL**",
            value=kpis.get('Delito Mas Frecuente', 'N/A')[:20] + "..." if len(str(kpis.get('Delito Mas Frecuente', 'N/A'))) > 20 else kpis.get('Delito Mas Frecuente', 'N/A'),
            delta="Artículo más frecuente"
        )

    with col_kpi3:
        st.metric(
            label="📍 **GEOGRAFÍA CRÍTICA**",
            value=kpis.get('Departamento Mas Afecstado', 'N/A')[:15] + "..." if len(str(kpis.get('Departamento Mas Afecstado', 'N/A'))) > 15 else kpis.get('Departamento Mas Afecstado', 'N/A'),
            delta="Departamento más afectado"
        )

    tendencia_value = f"{kpis.get('Tendencia General', 'N/A').upper()}"
    tendencia_delta = kpis.get('Tendencia Diff', 0)
    
    with col_kpi4:
        st.metric(
            label="📈 **VARIACIÓN HISTÓRICA**",
            value=tendencia_value,
            delta=f"{tendencia_delta:.1f}% vs Año Inicial",
            delta_color="inverse" if tendencia_delta < -5 else "normal"
        )
        
    st.markdown("<hr>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # 📑 ESTRUCTURA MODULAR CON PESTAÑAS
    # --------------------------------------------------------------------------
    
    tab1, tab2, tab3 = st.tabs([
        "📉 **EVOLUCIÓN TEMPORAL**", 
        "🗺️ **CONCENTRACIÓN GEOGRÁFICA**", 
        "🎯 **FOCOS DE DECISIÓN**"
    ])

    # --- PESTAÑA EVOLUCIÓN TEMPORAL ---
    with tab1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), transparent); 
                    padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h2>📈 ANÁLISIS DE LA DINÁMICA DEL DELITO AMBIENTAL</h2>
            <p style="color: #b0b0b0;">Evolución histórica y patrones temporales de los delitos ambientales</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_t1_1, col_t1_2 = st.columns(2)
        
        with col_t1_1:
            fig_evolucion = generar_evolucion_top5_conductas(df, theme=plotly_theme)
            st.plotly_chart(fig_evolucion, use_container_width=True)

        with col_t1_2:
            fig_heatmap = generar_heatmap_conducta_anual(df, theme=plotly_theme)
            st.plotly_chart(fig_heatmap, use_container_width=True)
            
        st.info("""
        💡 **ANÁLISIS DE LA PESTAÑA:**  
        • El gráfico de líneas muestra la trayectoria individual de los delitos más significativos.  
        • El Mapa de Calor (con escala logarítmica) revela visualmente qué delitos persisten o emergen con fuerza a lo largo de los años.
        """)

    # --- PESTAÑA CONCENTRACIÓN GEOGRÁFICA Y TIPOLÓGICA ---
    with tab2:
        st.markdown("""
        <div style="background: linear-gradient(90deg, rgba(0, 255, 136, 0.1), transparent); 
                    padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h2>🗺️ DISTRIBUCIÓN DE CASOS POR UBICACIÓN Y TIPOLOGÍA</h2>
            <p style="color: #b0b0b0;">Análisis espacial y clasificación de tipos de delito</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_t2_1, col_t2_2 = st.columns(2)

        with col_t2_1:
            fig_depto = generar_top_departamentos(df, theme=plotly_theme)
            st.plotly_chart(fig_depto, use_container_width=True)
        
        with col_t2_2:
            fig_conducta = generar_top_conductas(df, theme=plotly_theme)
            st.plotly_chart(fig_conducta, use_container_width=True)
            
        st.info("""
        💡 **ANÁLISIS DE LA PESTAÑA:**  
        • Comparación de concentraciones por Departamento (dónde ocurre) y por Artículo (qué ocurre).  
        • El gráfico de tendencia a largo plazo proporciona contexto histórico general.
        """)
        
        fig_tendencia = generar_tendencia_anual(df, theme=plotly_theme)
        st.plotly_chart(fig_tendencia, use_container_width=True)

    # --- PESTAÑA FOCOS DE DECISIÓN (Conclusiones Visuales) ---
    with tab3:
        st.markdown("""
        <div style="background: linear-gradient(90deg, rgba(255, 107, 0, 0.1), transparent); 
                    padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h2>🎯 RECOMENDACIONES ESTRATÉGICAS BASADAS EN HALLAZGOS</h2>
            <p style="color: #b0b0b0;">Enfoque en puntos críticos para maximizar impacto en mitigación</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Uso de kpis para obtener los focos
        depto_critico = kpis.get('Departamento Mas Afecstado', 'N/A')
        delito_critico = kpis.get('Delito Mas Frecuente', 'N/A')
        
        col_t3_1, col_t3_2 = st.columns(2)
        
        # Desglose Geográfico (Gráfico de barras horizontal)
        with col_t3_1:
            st.markdown(f"""
            <div style="background: rgba(20, 20, 30, 0.7); padding: 15px; border-radius: 8px; border-left: 4px solid #00d4ff;">
                <h3>📍 COMPOSICIÓN DEL DELITO EN: {depto_critico}</h3>
                <p style="color: #b0b0b0;">
                <strong>Recomendación:</strong> Priorizar los <strong>2-3 artículos</strong> más relevantes en este gráfico 
                para maximizar la reducción del delito en <strong>{depto_critico}</strong>.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if depto_critico != 'N/A':
                fig_dist_depto = generar_distribucion_top_depto_bar(df, depto_critico, theme=plotly_theme)
                st.plotly_chart(fig_dist_depto, use_container_width=True)
            else:
                st.warning("⚠️ **Datos insuficientes para desglose geográfico.**")
        
        # Estacionalidad del Delito Principal
        with col_t3_2:
            st.markdown(f"""
            <div style="background: rgba(20, 20, 30, 0.7); padding: 15px; border-radius: 8px; border-left: 4px solid #ff6b00;">
                <h3>⏱️ ESTACIONALIDAD DEL DELITO PRINCIPAL: {delito_critico}</h3>
                <p style="color: #b0b0b0;">
                <strong>Recomendación:</strong> Asignar recursos operativos <strong>1-2 meses antes</strong> 
                de los <strong>picos de casos</strong> observados en este gráfico de estacionalidad.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if delito_critico != 'N/A':
                fig_dist_mensual = generar_distribucion_mensual(df, delito_critico, theme=plotly_theme)
                st.plotly_chart(fig_dist_mensual, use_container_width=True)
            else:
                st.warning("⚠️ **Datos insuficientes para análisis de estacionalidad.**")

    
    # --- Pie de página profesional ---
    st.markdown("<hr>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 30px; padding: 20px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
        <p style="color: #444444; font-size: 0.8rem; margin-top: 10px;">
        © 2024 Análisis de Delitos Ambientales. Todos los derechos reservados.
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
