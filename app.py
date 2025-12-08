# ======================================================================
# Dashboard Unificado de Análisis de Delitos Ambientales
# GRUPO 3 – Talentotech
# ======================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import unidecode

st.set_page_config(
    page_title="Delitos Ambientales",
    layout="wide",
)

# ======================================================================
# CARGA DEL DATASET
# ======================================================================

@st.cache_data
def load_data():
    df = pd.read_csv("BD_Delitos_ambientales.csv", encoding="utf-8")

    # Limpieza de fecha
    df["FECHA HECHO"] = df["FECHA HECHO"].astype(str).str.replace("’", "").str.strip()
    df["FECHA HECHO"] = pd.to_datetime(df["FECHA HECHO"], errors="coerce")

    # Limpieza de textos
    df["DEPARTAMENTO"] = df["DEPARTAMENTO"].astype(str).str.upper().str.strip()
    df["MUNICIPIO"] = df["MUNICIPIO"].astype(str).str.upper().str.strip()

    # Normalizar tildes (para el mapa)
    df["DEPARTAMENTO"] = df["DEPARTAMENTO"].apply(lambda x: unidecode.unidecode(x))

    # Resumir descripción de conducta
    df["DESCRIPCION_CONDUCTA_RESUMIDA"] = df["DESCRIPCION_CONDUCTA"].apply(
        lambda x: x[:40] + "..." if len(x) > 40 else x
    )

    return df


df = load_data()

# ======================================================================
# TÍTULO
# ======================================================================

st.title("🌿 Dashboard de Delitos Ambientales en Colombia")
st.markdown("Análisis automático basado en el dataset suministrado.")

# ======================================================================
# KPIs
# ======================================================================
total_casos = df["CANTIDAD"].sum()
total_registros = len(df)
delito_top = df.groupby("DESCRIPCION_CONDUCTA")["CANTIDAD"].sum().idxmax()
depto_top = df.groupby("DEPARTAMENTO")["CANTIDAD"].sum().idxmax()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de Casos", f"{total_casos}")
col2.metric("Registros Analizados", f"{total_registros}")
col3.metric("Delito más frecuente", delito_top)
col4.metric("Departamento con más casos", depto_top)

# ======================================================================
# GRÁFICO 1 – Delitos por Departamento
# ======================================================================

st.subheader("📌 Casos por Departamento")

graf1 = df.groupby("DEPARTAMENTO")["CANTIDAD"].sum().sort_values(ascending=False).reset_index()

fig1 = px.bar(
    graf1,
    x="DEPARTAMENTO",
    y="CANTIDAD",
    color="CANTIDAD",
    color_continuous_scale="Turbo",
)
st.plotly_chart(fig1, use_container_width=True)

# ======================================================================
# GRÁFICO 2 – Delitos por Conducta (Resumen)
# ======================================================================

st.subheader("🧩 Distribución por tipo de conducta")

graf2 = df.groupby("DESCRIPCION_CONDUCTA_RESUMIDA")["CANTIDAD"].sum().reset_index()

fig2 = px.bar(
    graf2,
    x="DESCRIPCION_CONDUCTA_RESUMIDA",
    y="CANTIDAD",
    color="DESCRIPCION_CONDUCTA_RESUMIDA",
)
fig2.update_layout(xaxis={'categoryorder':'total descending'})
st.plotly_chart(fig2, use_container_width=True)

# ======================================================================
# GRÁFICO 3 – Zona (Urbana vs Rural)
# ======================================================================

st.subheader("🏙️ Casos por Zona")

graf3 = df.groupby("ZONA")["CANTIDAD"].sum().reset_index()

fig3 = px.pie(
    graf3,
    names="ZONA",
    values="CANTIDAD"
)
st.plotly_chart(fig3, use_container_width=True)

# ======================================================================
# PARTE 2 – MAPA POR DEPARTAMENTO
# ======================================================================

st.subheader("🗺️ Mapa de Delitos Ambientales por Departamento")

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/marcovega/colombia-json/master/colombia.json"
    response = requests.get(url)
    geo = response.json()

    # Normalizar nombres del geojson
    for f in geo["features"]:
        f["properties"]["NOMBRE_DPT"] = unidecode.unidecode(
            f["properties"]["NOMBRE_DPT"].upper().strip()
        )
    return geo

geojson = load_geojson()

# Agrupar data
map_data = df.groupby("DEPARTAMENTO")["CANTIDAD"].sum().reset_index()

# Mapa
fig_map = px.choropleth(
    map_data,
    geojson=geojson,
    locations="DEPARTAMENTO",
    featureidkey="properties.NOMBRE_DPT",
    color="CANTIDAD",
    color_continuous_scale="Viridis",
    hover_name="DEPARTAMENTO",
)

fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map, use_container_width=True)

# ======================================================================
# FINAL
# ======================================================================

st.markdown("---")
st.markdown("📌 *Dashboard generado automáticamente según el dataset cargado.*")
