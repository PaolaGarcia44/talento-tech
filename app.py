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
from typing import Dict, List, Any, Optional

# ======================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ======================================================================
st.set_page_config(
    page_title="🌎 Delitos Ambientales - Análisis Explorador",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ======================================================================
# REEMPLAZOS DE CARACTERES
# ======================================================================
REEMPLAZOS_CARACTERES: Dict[str, str] = {
    "Ã‘O": "NO", "Ã‘o": "NO", "Ã‘": "N", "Ã±": "N", "Ñ": "N", "ñ": "N",
    "Ã¡": "A", "Ã©": "E", "Ã­": "I", "Ã³": "O", "Ãº": "U",
    "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U",
    "ü": "U", "Ü": "U", "Ã¼": "U", "Ãœ": "U",
    "¿": "", "?": "", "¡": "", "!": "",
    "â€œ": "", "â€": "", "â€™": "", "â€¢": "",
    "â€“": "", "â€”": "", "Â¿": "", "Â¡": "",
    "ï¿½": "", "Â": "", "™": "", "®": "", "©": "",
    "º": "", "ª": "", "€": "", "$": "", "£": ""
}

# ======================================================================
# ESTILO GENERAL (CSS)
# ======================================================================
st.markdown("""
<style>

/* Fondo general */
.stApp {
    background-image: url("https://i.pinimg.com/736x/39/c7/1e/39c71e43cd06601a698edc75859dd674.jpg"); 
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Capa difuminada */
.stApp::before {
    content: "";
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(0,0,0,0.35);
    backdrop-filter: blur(10px);
    z-index: -1;
}

/* TITULOS */
h1, h2, h3 {
    color: #000 !important;
    text-shadow: none !important;
}

h1 {
    font-weight: 900;
    background: rgba(255,255,255,0.8);
    padding: 12px;
    border-radius: 8px;
    border-bottom: 3px solid #333;
}

h2 {
    padding-left: 10px;
    border-left: 5px solid #333;
}

/* TEXTO GENERAL */
p, li, .stMarkdown {
    color: #000 !important;
}

/* ALERTS */
.stAlert {
    background: rgba(255,255,255,0.95) !important;
    border-left: 5px solid #333 !important;
    color: #000 !important;
}

/* METRICS */
.stMetric > div {
    background: rgba(255,255,255,0.92) !important;
    border: 2px solid #222 !important;
    border-radius: 10px;
    padding: 20px;
    color: #000 !important;
    box-shadow: 3px 3px 10px rgba(0,0,0,0.4);
}

.stMetric label, 
.stMetric div[data-testid="stMetricValue"],
.stMetric div[data-testid="stMetricDelta"] {
    color: #000 !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] button {
    background: rgba(255,255,255,0.85);
    color: #000;
    border: 2px solid #333 !important;
    border-radius: 6px 6px 0 0;
    font-weight: bold;
}

.stTabs [data-baseweb="tab-list"] button:hover {
    background: rgba(230,230,230,0.95);
}

/* TEXTO DE GRÁFICOS */
.gtitle, .legendtext, .xtick, .ytick {
    fill: #000 !important;
    color: #000 !important;
}

</style>
""", unsafe_allow_html=True)

# ======================================================================
# FUNCIONES DE LIMPIEZA
# ======================================================================

def _corregir_caracteres(texto: Any) -> str:
    if pd.isna(texto):
        return ""
    texto = str(texto).strip()
    for malo, bueno in REEMPLAZOS_CARACTERES.items():
        texto = texto.replace(malo, bueno)
    return texto

def limpiar_texto(texto: Any, mayusculas=True, espacios_a_guion=False) -> str:
    if pd.isna(texto):
        return ""
    texto = _corregir_caracteres(str(texto).strip())
    texto = " ".join(texto.split())
    if mayusculas:
        texto = texto.upper()
    if espacios_a_guion:
        texto = texto.replace(" ", "_")
    return "" if texto in ["NAN", "NONE", "NULL", ""] else texto

def estandarizar_nombres_columnas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [
        limpiar_texto(col, mayusculas=True, espacios_a_guion=True)
        for col in df.columns
    ]
    return df

def limpiar_columnas_texto(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.select_dtypes(include=['object']).columns:
        usar_guion = col not in ["DEPARTAMENTO", "MUNICIPIO"]
        df[col] = df[col].apply(lambda x: limpiar_texto(x, espacios_a_guion=usar_guion))
    return df

# ======================================================================
# MAPA INTERACTIVO POR DEPARTAMENTO
# ======================================================================

import requests
import json

st.subheader("🗺️ Distribución geográfica de delitos ambientales por departamento")

# Cargar geojson de departamentos de Colombia
@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/marcovega/colombia-json/master/colombia.json"
    response = requests.get(url)
    return response.json()

colombia_geojson = load_geojson()

# Agrupación por departamento
map_data = df.groupby("DEPARTAMENTO")["CANTIDAD"].sum().reset_index()

# Normalizar nombres del GeoJSON (vienen en mayúsculas)
for feature in colombia_geojson["features"]:
    feature["properties"]["NOMBRE_DPT"] = feature["properties"]["NOMBRE_DPT"].upper()

# Crear mapa coroplético
fig_map = px.choropleth(
    map_data,
    geojson=colombia_geojson,
    locations="DEPARTAMENTO",
    featureidkey="properties.NOMBRE_DPT",
    color="CANTIDAD",
    color_continuous_scale="Viridis",
    hover_name="DEPARTAMENTO",
    hover_data={"CANTIDAD": True},
)

fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

st.plotly_chart(fig_map, use_container_width=True)


