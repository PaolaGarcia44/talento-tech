# ======================================================================
# Dashboard Unificado de Análisis de Delitos Ambientales
# GRUPO 3 – Talentotech
# ======================================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

st.set_page_config(
    page_title="Delitos Ambientales",
    layout="wide",
)

# ======================================================================
# GEOJSON LOCAL DE COLOMBIA (DEPARTAMENTOS)
# Sin URLs externas, 100% compatible con Streamlit Cloud.
# ======================================================================

colombia_geojson = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {"DPTO": "AMAZONAS"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-70, -3], [-71, -3], [-71, -4], [-70, -4], [-70, -3]]]
      }
    },
    {
      "type": "Feature",
      "properties": {"DPTO": "ANTIOQUIA"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-75, 7], [-76, 7], [-76, 6], [-75, 6], [-75, 7]]]
      }
    },
    {
      "type": "Feature",
      "properties": {"DPTO": "ARAUCA"},
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[-70, 7], [-71, 7], [-71, 6], [-70, 6], [-70, 7]]]
      }
    },
    # ------------------------------------------------------------------
    # NOTA IMPORTANTE:
    # Este geojson es simbólico y funciona para visualización básica.
    # Si quieres un mapa real con polígonos exactos, puedo incluir el completo.
    # ------------------------------------------------------------------
  ]
}

# ======================================================================
# CARGA DEL DATASET
# ======================================================================

@st.cache_data
def load_data():
    df = pd.read_csv("BD_Delitos_ambientales.csv", encoding="utf-8")

    df["FECHA HECHO"] = df["FECHA HECHO"].astype(str).str.replace("’", "").str.strip()
    df["FECHA HECHO"] = pd.to_datetime(df["FECHA HECHO"], errors="coerce")

    df["DEPARTAMENTO"] = df["DEPARTAMENTO"].astype(str).str.upper().str.strip()
    df["MUNICIPIO"] = df["MUNICIPIO"].astype(str).str.upper().str.strip()

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
col4.metric("Dpto. con más casos", depto_top)

# ======================================================================
# GRÁFICO: Casos por Departamento
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
# GRÁFICO: Conductas resumidas
# ======================================================================

st.subheader("🧩 Distribución por Tipo de Conducta")

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
# GRÁFICO: Zona
# ======================================================================

st.subheader("🏙️ Zona Urbana vs Rural")

graf3 = df.groupby("ZONA")["CANTIDAD"].sum().reset_index()

fig3 = px.pie(
    graf3,
    names="ZONA",
    values="CANTIDAD"
)
st.plotly_chart(fig3, use_container_width=True)

# ======================================================================
# MAPA (Versión estable)
# ======================================================================

st.subheader("🗺️ Mapa de Delitos Ambientales por Departamento")

map_data = df.groupby("DEPARTAMENTO")["CANTIDAD"].sum().reset_index()

# Normalización
map_data["DEPARTAMENTO"] = map_data["DEPARTAMENTO"].astype(str).str.upper()

fig_map = px.choropleth(
    map_data,
    geojson=colombia_geojson,
    locations="DEPARTAMENTO",
    featureidkey="properties.DPTO",
    color="CANTIDAD",
    color_continuous_scale="Viridis",
)

fig_map.update_geos(fitbounds="locations", visible=False)
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig_map, use_container_width=True)

# ======================================================================
# FINAL
# ======================================================================

st.markdown("---")
st.markdown("📌 *Dashboard generado automáticamente según el dataset cargado.*")
