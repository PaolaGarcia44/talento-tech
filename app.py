# ======================================================================
# Dashboard Unificado de Delitos Ambientales - Talentotech
# Carga automática del archivo BD_Delitos_ambientales.csv
# ======================================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Delitos Ambientales",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌱 Dashboard Delitos Ambientales – Colombia")


# ----------------------------------------------------------------------
# CARGA Y LIMPIEZA DE DATOS
# ----------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    df = pd.read_csv("BD_Delitos_ambientales.csv", encoding="latin1")

    # Ajuste del nombre de la columna rara
    df = df.rename(columns={"ï»¿FECHA HECHO": "FECHA_HECHO"})

    # Normalizar nombres
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")

    # Convertir fecha
    df["FECHA_HECHO"] = pd.to_datetime(
        df["FECHA_HECHO"],
        format="%d/%m/%Y",
        errors="coerce"
    )

    df["AÑO"] = df["FECHA_HECHO"].dt.year

    # Resumen automático de la conducta
    df["CONDUCTA_RESUMIDA"] = df["DESCRIPCION_CONDUCTA"].str.slice(0, 40) + "..."

    return df


# Cargar dataset automáticamente
try:
    df = cargar_datos()
except:
    st.error("No se encontró el archivo BD_Delitos_ambientales.csv")
    st.stop()

# Vista previa
st.subheader("Vista previa del dataset")
st.dataframe(df.head(), use_container_width=True)


# ----------------------------------------------------------------------
# FILTROS
# ----------------------------------------------------------------------
st.sidebar.header("Filtros del análisis")

años = sorted(df["AÑO"].dropna().unique())
dep = sorted(df["DEPARTAMENTO"].dropna().unique())
muni = sorted(df["MUNICIPIO"].dropna().unique())
conductas = sorted(df["DESCRIPCION_CONDUCTA"].dropna().unique())
zonas = sorted(df["ZONA"].dropna().unique())

filtro_año = st.sidebar.multiselect("Año", años)
filtro_dep = st.sidebar.multiselect("Departamento", dep)
filtro_muni = st.sidebar.multiselect("Municipio", muni)
filtro_conducta = st.sidebar.multiselect("Conducta", conductas)
filtro_zona = st.sidebar.multiselect("Zona", zonas)

df_filtrado = df.copy()

if filtro_año:
    df_filtrado = df_filtrado[df_filtrado["AÑO"].isin(filtro_año)]
if filtro_dep:
    df_filtrado = df_filtrado[df_filtrado["DEPARTAMENTO"].isin(filtro_dep)]
if filtro_muni:
    df_filtrado = df_filtrado[df_filtrado["MUNICIPIO"].isin(filtro_muni)]
if filtro_conducta:
    df_filtrado = df_filtrado[df_filtrado["DESCRIPCION_CONDUCTA"].isin(filtro_conducta)]
if filtro_zona:
    df_filtrado = df_filtrado[df_filtrado["ZONA"].isin(filtro_zona)]


# ----------------------------------------------------------------------
# MÉTRICAS
# ----------------------------------------------------------------------
st.subheader("Indicadores generales")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de casos", int(df_filtrado["CANTIDAD"].sum()))
col2.metric("Departamentos", df_filtrado["DEPARTAMENTO"].nunique())
col3.metric("Municipios", df_filtrado["MUNICIPIO"].nunique())

if not df_filtrado.empty:
    col4.metric("Rango años", f"{int(df_filtrado['AÑO'].min())} - {int(df_filtrado['AÑO'].max())}")
else:
    col4.metric("Rango años", "Sin datos")


# ----------------------------------------------------------------------
# GRÁFICAS
# ----------------------------------------------------------------------
st.subheader("Visualizaciones")


# === 1. Casos por departamento (colores diferentes)
fig_dep = px.bar(
    df_filtrado.groupby("DEPARTAMENTO")["CANTIDAD"].sum().sort_values(ascending=False).head(15),
    title="Casos por Departamento",
    labels={"value": "Casos", "DEPARTAMENTO": "Departamento"},
    color=df_filtrado.groupby("DEPARTAMENTO")["CANTIDAD"].sum().sort_values(ascending=False).head(15).values,
    color_continuous_scale="turbo"
)
st.plotly_chart(fig_dep, use_container_width=True)


# === 2. Municipios (otra paleta de color)
fig_muni = px.bar(
    df_filtrado.groupby("MUNICIPIO")["CANTIDAD"].sum().sort_values(ascending=False).head(20),
    title="Top 20 Municipios con más Casos",
    labels={"value": "Casos", "MUNICIPIO": "Municipio"},
    color=df_filtrado.groupby("MUNICIPIO")["CANTIDAD"].sum().sort_values(ascending=False).head(20).values,
    color_continuous_scale="plasma"
)
st.plotly_chart(fig_muni, use_container_width=True)


# === 3. Conductas (usando CONDUCTA_RESUMIDA y otra paleta)
fig_cond = px.bar(
    df_filtrado["CONDUCTA_RESUMIDA"].value_counts().head(15),
    title="Conductas Ambientales (resumidas)",
    labels={"value": "Cantidad", "index": "Conducta"},
    color=df_filtrado["CONDUCTA_RESUMIDA"].value_counts().head(15).values,
    color_continuous_scale="viridis"
)
st.plotly_chart(fig_cond, use_container_width=True)


# === 4. Serie temporal (línea con colores suaves)
serie = df_filtrado.groupby("AÑO")["CANTIDAD"].sum().reset_index()

fig_year = px.line(
    serie,
    x="AÑO",
    y="CANTIDAD",
    markers=True,
    title="Tendencia Anual de Delitos Ambientales",
    color_discrete_sequence=["#00A6FB"]
)
st.plotly_chart(fig_year, use_container_width=True)


# === 5. Distribución por zona (paleta diferente)
fig_zona = px.pie(
    df_filtrado,
    names="ZONA",
    values="CANTIDAD",
    title="Distribución por Zona",
    color="ZONA",
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.plotly_chart(fig_zona, use_container_width=True)

st.markdown("---")
st.markdown("© 2024 Talentotech. Todos los derechos reservados.")
