# ======================================================================
# Dashboard Unificado de Delitos Ambientales - Talentotech
# Adaptado automáticamente al dataset BD_Delitos_ambientales.csv
# ======================================================================

import streamlit as st
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------
# CONFIGURACIÓN INICIAL
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
def cargar_datos(uploaded):
    df = pd.read_csv(uploaded, encoding="latin1")
    
    # Arreglo de nombre raro
    df = df.rename(columns={"ï»¿FECHA HECHO": "FECHA_HECHO"})

    # Limpieza de columnas
    df.columns = df.columns.str.strip().str.upper().str.replace(" ", "_")

    # Conversión de fecha
    df["FECHA_HECHO"] = pd.to_datetime(df["FECHA_HECHO"], format="%d/%m/%Y", errors='coerce')

    # Año
    df["AÑO"] = df["FECHA_HECHO"].dt.year

    return df


uploaded_file = st.sidebar.file_uploader("Sube el archivo BD_Delitos_ambientales.csv", type=["csv"])

if uploaded_file:

    df = cargar_datos(uploaded_file)

    st.subheader("Vista previa del dataset")
    st.dataframe(df.head(), use_container_width=True)

    # ------------------------------------------------------------------
    # FILTROS DEL DASHBOARD
    # ------------------------------------------------------------------
    st.sidebar.header("Filtros")

    años = sorted(df["AÑO"].dropna().unique())
    dep = sorted(df["DEPARTAMENTO"].dropna().unique())
    muni = sorted(df["MUNICIPIO"].dropna().unique())
    conductas = sorted(df["DESCRIPCION_CONDUCTA"].dropna().unique())
    zonas = sorted(df["ZONA"].dropna().unique())

    filtro_año = st.sidebar.multiselect("Año", años)
    filtro_dep = st.sidebar.multiselect("Departamento", dep)
    filtro_muni = st.sidebar.multiselect("Municipio", muni)
    filtro_conducta = st.sidebar.multiselect("Tipo de conducta", conductas)
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

    # ------------------------------------------------------------------
    # TARJETAS KPI
    # ------------------------------------------------------------------
    st.subheader("Indicadores generales")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total de casos", int(df_filtrado["CANTIDAD"].sum()))
    col2.metric("Departamentos analizados", df_filtrado["DEPARTAMENTO"].nunique())
    col3.metric("Municipios analizados", df_filtrado["MUNICIPIO"].nunique())

    if not df_filtrado.empty:
        año_min = int(df_filtrado["AÑO"].min())
        año_max = int(df_filtrado["AÑO"].max())
        col4.metric("Rango de años", f"{año_min} - {año_max}")
    else:
        col4.metric("Rango de años", "Sin datos")

    # ------------------------------------------------------------------
    # GRÁFICOS PRINCIPALES
    # ------------------------------------------------------------------
    st.subheader("Visualizaciones")

    # --- 1. Casos por departamento ---
    fig_dep = px.bar(
        df_filtrado.groupby("DEPARTAMENTO")["CANTIDAD"].sum().sort_values(ascending=False).head(15),
        title="Casos por departamento",
        labels={"value": "Casos", "DEPARTAMENTO": "Departamento"}
    )
    st.plotly_chart(fig_dep, use_container_width=True)

    # --- 2. Top 20 municipios ---
    fig_muni = px.bar(
        df_filtrado.groupby("MUNICIPIO")["CANTIDAD"].sum().sort_values(ascending=False).head(20),
        title="Top 20 municipios con más casos",
        labels={"value": "Casos", "MUNICIPIO": "Municipio"}
    )
    st.plotly_chart(fig_muni, use_container_width=True)

    # --- 3. Conductas más comunes ---
    fig_cond = px.bar(
        df_filtrado["DESCRIPCION_CONDUCTA"].value_counts().head(15),
        title="Tipos de conducta más frecuentes",
        labels={"value": "Número de registros", "index": "Conducta"}
    )
    st.plotly_chart(fig_cond, use_container_width=True)

    # --- 4. Serie temporal anual ---
    serie = df_filtrado.groupby("AÑO")["CANTIDAD"].sum().reset_index()
    fig_year = px.line(
        serie,
        x="AÑO",
        y="CANTIDAD",
        markers=True,
        title="Tendencia anual de delitos ambientales"
    )
    st.plotly_chart(fig_year, use_container_width=True)

    # --- 5. Distribución por zona ---
    fig_zona = px.pie(
        df_filtrado,
        names="ZONA",
        values="CANTIDAD",
        title="Distribución entre zona Urbana y Rural"
    )
    st.plotly_chart(fig_zona, use_container_width=True)

    # ------------------------------------------------------------------
    # TABLA RESULTANTE
    # ------------------------------------------------------------------
    st.subheader("Tabla filtrada")
    st.dataframe(df_filtrado, use_container_width=True)

else:
    st.info("Sube el archivo BD_Delitos_ambientales.csv para iniciar.")
