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

# ==============================================================================
# CONFIGURACIÓN INICIAL Y ESTILO
# ==============================================================================

st.set_page_config(
    page_title="🌎 Delitos Ambientales - Explorador",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==============================================================================
# ESTILO GLOBAL (CSS) — VISUAL MODERNO Y LIMPIO
# ==============================================================================

st.markdown("""
<style>

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
    inset: 0;
    background: rgba(0,0,0,0.45);
    backdrop-filter: blur(12px);
    z-index: -1;
}

/* TITULOS */
h1, h2, h3 {
    color: #111 !important;
    text-shadow: none !important;
}

h1 {
    font-weight: 800;
    margin-bottom: 15px;
    background: rgba(255,255,255,0.75);
    padding: 12px 18px;
    border-left: 6px solid #333;
    border-radius: 6px;
}

h2 {
    border-left: 5px solid #222;
    padding-left: 10px;
}

/* Texto general */
p, li, span, div {
    color: #111 !important;
}

/* MODO TARJETAS PARA KPIs */
.stMetric > div {
    background: rgba(255,255,255,0.9);
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #222;
    box-shadow: 0 3px 10px rgba(0,0,0,0.4);
}

.stMetric label {
    color: #222 !important;
    font-weight: 600;
}

/* Tabs */
.stTabs button {
    background: rgba(255,255,255,0.85) !important;
    color: #111 !important;
    font-weight: 700 !important;
    border-radius: 6px 6px 0 0 !important;
    border: 1px solid #333 !important;
}

.stTabs button:hover {
    background: #e6e6e6 !important;
}

/* Plotly texto negro */
.xtick, .ytick, .legendtext, .gtitle, .xaxislayer-title, .yaxislayer-title {
    fill: #000 !important;
    color: #000 !important;
}

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# FUNCIONES DE LIMPIEZA Y PREPROCESAMIENTO
# ==============================================================================

REEMPLAZOS = {
    "Ã‘": "N", "Ã±": "N", "Ñ": "N", "ñ": "N",
    "Ã¡": "A", "Ã©": "E", "Ã­": "I", "Ã³": "O", "Ãº": "U",
    "á": "A", "é": "E", "í": "I", "ó": "O", "ú": "U"
}

def corregir(txt):
    if pd.isna(txt): return ""
    txt = str(txt)
    for malo, bueno in REEMPLAZOS.items():
        txt = txt.replace(malo, bueno)
    return txt.strip()

def limpiar_texto(txt):
    if pd.isna(txt): return ""
    return corregir(txt).upper().strip()

def estandarizar_columnas(df):
    df = df.copy()
    df.columns = [limpiar_texto(c).replace(" ", "_") for c in df.columns]
    return df

@st.cache_data
def cargar_datos(archivo):
    if archivo is None:
        return pd.DataFrame()

    df = pd.read_csv(archivo)
    df = estandarizar_columnas(df)

    for col in df.select_dtypes(include=["object"]):
        df[col] = df[col].apply(limpiar_texto)

    if "FECHA_HECHO" in df.columns:
        df["ANIO"] = df["FECHA_HECHO"].astype(str).str[-4:].astype(int)

    if "CANTIDAD" not in df.columns:
        df["CANTIDAD"] = 1

    df["CANTIDAD"] = pd.to_numeric(df["CANTIDAD"], errors="coerce").fillna(1)

    df.drop_duplicates(inplace=True)
    df.fillna("", inplace=True)

    if "DESCRIPCION_CONDUCTA" in df.columns:
        df["ARTICULO"] = df["DESCRIPCION_CONDUCTA"].str.split('.').str[0]

    return df

# ==============================================================================
# FUNCIONES DE VISUALIZACIÓN
# ==============================================================================

def tendencia_anual(df):
    if df.empty:
        return go.Figure()

    max_a = df["ANIO"].max()
    bins = [2000, 2005, 2010, 2015, 2020, max_a + 1]
    labels = [f"{bins[i]}-{bins[i+1]-1}" for i in range(len(bins)-1)]

    df2 = df[df["ANIO"] >= 2000].copy()
    df2["INTERVALO"] = pd.cut(df2["ANIO"], bins=bins, labels=labels, right=False)

    data = df2.groupby("INTERVALO")["CANTIDAD"].sum().reset_index()

    fig = px.bar(
        data, x="INTERVALO", y="CANTIDAD",
        color="CANTIDAD", text_auto='.2s',
        color_continuous_scale=px.colors.sequential.Teal,
    )
    fig.update_layout(
        title="Tendencia de Casos por Intervalos de Año",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

def top_conductas(df):
    if df.empty:
        return go.Figure()

    data = df.groupby("ARTICULO")["CANTIDAD"].sum().nlargest(8).reset_index()

    fig = px.bar(
        data, y="ARTICULO", x="CANTIDAD",
        orientation="h", text_auto='.2s',
        color="CANTIDAD",
        color_continuous_scale=px.colors.sequential.Plasma,
    )
    fig.update_layout(
        title="Top 8 Conductas",
        yaxis={"autorange": "reversed"},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig

# Puedes agregar el resto de gráficos siguiendo el mismo estilo limpio.

# ==============================================================================
# INTERFAZ PRINCIPAL
# ==============================================================================

st.title("🌱 Dashboard de Delitos Ambientales")

archivo = st.file_uploader("Cargar archivo CSV", type=["csv"])

df = cargar_datos(archivo)

if df.empty:
    st.info("Sube un archivo CSV para iniciar el análisis.")
    st.stop()

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total Casos", f"{df['CANTIDAD'].sum():,}")
col2.metric("Años Analizados", f"{df['ANIO'].min()} - {df['ANIO'].max()}")
col3.metric("Conductas Únicas", df["ARTICULO"].nunique())

# Tabs
t1, t2 = st.tabs(["📈 Tendencia", "📊 Top Conductas"])

with t1:
    st.plotly_chart(tendencia_anual(df), use_container_width=True)

with t2:
    st.plotly_chart(top_conductas(df), use_container_width=True)
