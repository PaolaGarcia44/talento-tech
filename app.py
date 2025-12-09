import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re

st.set_page_config(page_title="Dashboard Delitos Ambientales", layout="wide")

# ---------------------------------------------------------
# CARGAR DATASET
# ---------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("BD_Delitos_ambientales.csv", encoding="latin1")

    # Normalizar nombres de departamentos para que coincidan con GeoJSON
    df["DEPARTAMENTO"] = (
        df["DEPARTAMENTO"]
        .str.upper()
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('utf-8')
        .str.replace(r'[^A-Z ]', '', regex=True)
        .str.strip()
    )

    # Resumir descripciones de conducta para que no sean kilometros de texto
    def resumir_texto(text):
        text = str(text)
        text = re.sub(r'[^A-Za-z0-9ÁÉÍÓÚÑáéíóúñ ]', '', text)
        return text[:40] + "..." if len(text) > 40 else text

    df["DESCRIPCION_CONDUCTA_RESUMIDA"] = df["DESCRIPCION_CONDUCTA"].apply(resumir_texto)

    return df

df = load_data()

# ---------------------------------------------------------
# TÍTULO PRINCIPAL
# ---------------------------------------------------------
st.markdown("""
<h1 style='color:#32CD32;'>
📊 Dashboard Unificado de Delitos Ambientales
</h1>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GRÁFICA: DISTRIBUCIÓN DE TIPO DE CONDUCTA
# ---------------------------------------------------------
st.subheader("📌 Distribución por Tipo de Conducta")

conducta = df.groupby("DESCRIPCION_CONDUCTA_RESUMIDA")["CANTIDAD"].sum().reset_index()

fig1 = px.bar(
    conducta,
    x="DESCRIPCION_CONDUCTA_RESUMIDA",
    y="CANTIDAD",
    color="DESCRIPCION_CONDUCTA_RESUMIDA",
    color_discrete_sequence=px.colors.qualitative.Dark24,
)

fig1.update_layout(
    xaxis_tickangle=-45,
    height=500,
    legend_title="Conductas"
)

st.plotly_chart(fig1, use_container_width=True)

# ---------------------------------------------------------
# MAPA CHOROPLETH POR DEPARTAMENTO
# ---------------------------------------------------------
st.subheader("🗺️ Mapa de Delitos por Departamento")

@st.cache_data
def load_geojson():
    with open("colombia_departamentos.geojson", "r", encoding="utf-8") as f:
        return json.load(f)

geojson = load_geojson()

# Agrupar data por departamento
map_data = df.groupby("DEPARTAMENTO")["CANTIDAD"].sum().reset_index()

# Crear diccionario para emparejar nombres con códigos del GeoJSON
geo_departamentos = {
    feature["properties"]["NOMBRE_DPT"].upper(): feature["properties"]["DPTO_CCDGO"]
    for feature in geojson["features"]
}

# Asignar código de departamento a cada fila
map_data["DPTO_CCDGO"] = map_data["DEPARTAMENTO"].map(geo_departamentos)

# Evitar filas sin coincidencia
map_data = map_data.dropna(subset=["DPTO_CCDGO"])

fig2 = px.choropleth(
    map_data,
    geojson=geojson,
    locations="DPTO_CCDGO",
    featureidkey="properties.DPTO_CCDGO",
    color="CANTIDAD",
    color_continuous_scale="Viridis",
    hover_name="DEPARTAMENTO",
    labels={"CANTIDAD": "Cantidad"}
)

fig2.update_geos(fitbounds="locations", visible=False)
fig2.update_layout(height=600)

st.plotly_chart(fig2, use_container_width=True)
