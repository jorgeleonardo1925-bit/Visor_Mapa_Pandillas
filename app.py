import folium
from folium.plugins import HeatMap
import geopandas as gpd
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="MAPA DE PANDILLAS 2026",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- SISTEMA DE AUTENTICACIÓN ---
CLAVE_CORRECTA = "MiClaveSecreta123"

if "autenticado" not in st.session_state:
  st.session_state.autenticado = False

if not st.session_state.autenticado:
  st.title("🔒 Acceso Restringido")
  password_input = st.text_input(
      "Ingrese la contraseña de acceso:", type="password"
  )
  if st.button("Ingresar"):
    if password_input == CLAVE_CORRECTA:
      st.session_state.autenticado = True
      st.rerun()
    else:
      st.error("Contraseña incorrecta.")
  st.stop()


# --- CARGA Y PROCESAMIENTO DE DATOS ---
@st.cache_data
def cargar_datos():
  gdf = gpd.read_file("Pandillas_2026.json")
  if gdf.crs and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)
  return gdf


try:
  df_original = cargar_datos()
except Exception as e:
  st.error(
      f"Error al cargar el archivo 'Pandillas_2026.json': {e}. Verifique que"
      " esté en el repositorio."
  )
  st.stop()


# Detección inteligente de columnas en el archivo GeoJSON
def buscar_columna(df, posibles_nombres):
  for col in df.columns:
    if col.lower() in [p.lower() for p in posibles_nombres]:
      return col
  return None


col_prov = buscar_columna(df_original, ["provincia", "prov", "nombre_prov"])
col_dist = buscar_columna(df_original, ["distrito", "dist", "nombre_dist"])
col_corr = buscar_columna(df_original, ["corregimiento", "corr", "nombre_corr"])
col_lug = buscar_columna(
    df_original, ["lugar", "ubicacion", "sitio", "direccion", "lug"]
)
col_banda = buscar_columna(
    df_original, ["banda", "pandilla", "nombre_pandilla", "gang", "grupo", "pan"]
)

# --- PANEL DE FILTROS EN LA BARRA LATERAL ---
st.sidebar.header("🎯 Filtros Geográficos")

df_filtrado = df_original.copy()

# 1. Filtro de Provincia (Multiselect para elegir libremente)
if col_prov:
  provincias_disponibles = sorted(
      df_original[col_prov].dropna().unique().tolist()
  )
  provincias_sel = st.sidebar.multiselect(
      "Seleccionar Provincia(s)", provincias_disponibles
  )
  if provincias_sel:
    df_filtrado = df_filtrado[df_filtrado[col_prov].isin(provincias_sel)]

# 2. Filtro de Distrito (Dependiente de la provincia o total)
if col_dist:
  distritos_disponibles = sorted(
      df_filtrado[col_dist].dropna().unique().tolist()
  )
  distritos_sel = st.sidebar.multiselect(
      "Seleccionar Distrito(s)", distritos_disponibles
  )
  if distritos_sel:
    df_filtrado = df_filtrado[df_filtrado[col_dist].isin(distritos_sel)]

# 3. Filtro de Corregimiento
if col_corr:
  corregimientos_disponibles = sorted(
      df_filtrado[col_corr].dropna().unique().tolist()
  )
  corregimientos_sel = st.sidebar.multiselect(
      "Seleccionar Corregimiento(s)", corregimientos_disponibles
  )
  if corregimientos_sel:
    df_filtrado = df_filtrado[
        df_filtrado[col_corr].isin(corregimientos_sel)
    ]

st.sidebar.markdown("---")
# 4. Casilla para Mapa de Calor ubicada debajo de los filtros
ver_heatmap = st.sidebar.checkbox(
    "🔥 Activar Mapa de Calor (Heatmap)", value=False
)

# --- CUERPO PRINCIPAL ---
st.title("🗺️ MAPA DE PANDILLAS 2026")
st.markdown(
    "**Sistema de Inteligencia Geoespacial y Análisis Operativo de Seguridad**"
)

# Métricas superiores en tiempo real
m1, m2, m3 = st.columns(3)
with m1:
  st.metric("Registros en Vista", len(df_filtrado))
with m2:
  if col_prov and not df_filtrado.empty:
    st.metric("Provincias Activas", df_filtrado[col_prov].nunique())
with m3:
  if col_banda and not df_filtrado.empty:
    st.metric("Grupos Identificados", df_filtrado[col_banda].nunique())

st.markdown("---")

# --- RENDERIZADO DEL MAPA EN PANTALLA COMPLETA ---
try:
  if not df_filtrado.empty:
    lat_centro = df_filtrado.geometry.y.mean()
    lon_centro = df_filtrado.geometry.x.mean()
    zoom_inicial = 9 if len(df_filtrado) < len(df_original) else 8
  else:
    lat_centro, lon_centro, zoom_inicial = 8.538, -80.7821, 8

  m = folium.Map(
      location=[lat_centro, lon_centro],
      zoom_start=zoom_inicial,
      tiles="OpenStreetMap",
  )

  if ver_heatmap:
    heat_data = [[point.y, point.x] for point in df_filtrado.geometry if point]
    if heat_data:
      HeatMap(heat_data, radius=16, blur=10, max_zoom=1).add_to(m)
  else:
    campos_popup = [c for c in df_filtrado.columns if c != "geometry"]
    folium.GeoJson(
        df_filtrado,
        name="Puntos de Pandillas",
        popup=folium.GeoJsonPopup(fields=campos_popup),
    ).add_to(m)

  st_folium(m, use_container_width=True, height=650)

except Exception as map_err:
  st.error(f"Error al renderizar el mapa: {map_err}")


# --- SECCIÓN: DESGLOSE DE GRUPOS REGISTRADOS ---
st.markdown("---")
st.subheader("📋 DESGLOSE DE GRUPOS REGISTRADOS")

if not df_filtrado.empty:
  # Construir un DataFrame limpio con las columnas requeridas: PRO, DIS, COR, LUG, PAN
  df_tabla = pd.DataFrame()
  df_tabla["PRO"] = (
      df_filtrado[col_prov] if col_prov else "No especificado"
  )
  df_tabla["DIS"] = (
      df_filtrado[col_dist] if col_dist else "No especificado"
  )
  df_tabla["COR"] = (
      df_filtrado[col_corr] if col_corr else "No especificado"
  )
  df_tabla["LUG"] = (
      df_filtrado[col_lug] if col_lug else "Sin especificar"
  )
  df_tabla["PAN"] = (
      df_filtrado[col_banda] if col_banda else "Sin nombre"
  )

  # Mostrar la tabla interactiva adaptada
  st.dataframe(df_tabla, use_container_width=True, height=350)

  # Botón de descarga para el reporte filtrado en CSV
  csv_export = df_tabla.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar Desglose en CSV",
      data=csv_export,
      file_name="desglose_grupos_registrados_2026.csv",
      mime="text/csv",
  )
else:
  st.warning("No hay registros para mostrar con los filtros seleccionados.")