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

# Detección automática de columnas estándar
columnas_disponibles = [col for col in df_original.columns if col != "geometry"]


def buscar_columna_exacta(posibles):
  for p in posibles:
    for c in columnas_disponibles:
      if p.lower() == c.lower() or p.lower() in c.lower():
        return c
  return columnas_disponibles[0] if columnas_disponibles else None


col_prov = buscar_columna_exacta(["PRO", "provincia", "prov"])
col_dist = buscar_columna_exacta(["DIS", "distrito", "dist"])
col_corr = buscar_columna_exacta(["COR", "corregimiento", "corr"])
col_lug = buscar_columna_exacta(["LUG", "lugar", "ubicacion"])
col_banda = buscar_columna_exacta(["PAN", "banda", "pandilla", "grupo"])


# --- ESTILOS CSS PROFESIONALES ---
st.markdown(
    """
    <style>
    .header-card {
        background: linear-gradient(135deg, #0d6efd 0%, #0043a8 100%);
        color: white;
        padding: 18px 25px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
        margin-bottom: 25px;
    }
    .header-title {
        font-size: 24px;
        font-weight: 700;
        letter-spacing: 1px;
        margin: 0;
        text-transform: uppercase;
    }
    .sub-header-container {
        display: flex;
        align-items: center;
        border-left: 5px solid #0d6efd;
        padding-left: 15px;
        margin-bottom: 20px;
    }
    .sub-header-title {
        font-size: 22px;
        font-weight: 700;
        color: #2b2b2b;
        letter-spacing: 0.5px;
        margin: 0;
        text-transform: uppercase;
    }
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(0, 123, 255, 0.25);
    }
    .metric-title {
        font-size: 14px;
        color: #555555;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 30px;
        color: #0d6efd;
        font-weight: 700;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- PANEL DE FILTROS EN LA BARRA LATERAL ---
st.sidebar.header("🎯 Filtros Geográficos")

df_filtrado = df_original.copy()

# 1. Filtro de Provincia
if col_prov:
  provincias_disponibles = sorted(
      df_original[col_prov].dropna().unique().tolist()
  )
  provincias_sel = st.sidebar.multiselect(
      "Seleccionar Provincia(s)", provincias_disponibles
  )
  if provincias_sel:
    df_filtrado = df_filtrado[df_filtrado[col_prov].isin(provincias_sel)]

# 2. Filtro de Distrito
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
# 4. Casilla para Mapa de Calor
ver_heatmap = st.sidebar.checkbox(
    "🔥 Activar Mapa de Calor (Heatmap)", value=False
)


# --- CUERPO PRINCIPAL ---

# 1. Cuadro superior institucional con sombra azul
st.markdown(
    """
    <div class="header-card">
        <div class="header-title">SISTEMA INTEGRADO DE ESTADISTICAS CRIMINALES</div>
    </div>
""",
    unsafe_allow_html=True,
)

# 2. Subtítulo rediseñado con barra lateral azul y estilo profesional
st.markdown(
    """
    <div class="sub-header-container">
        <div class="sub-header-title">🗺️ MAPA DE PANDILLAS 2026</div>
    </div>
""",
    unsafe_allow_html=True,
)


# --- TARJETAS DE MÉTRICAS PROFESIONALES ---
reg_count = len(df_filtrado)
prov_count = (
    df_filtrado[col_prov].nunique() if col_prov and not df_filtrado.empty else 0
)
banda_count = (
    df_filtrado[col_banda].nunique()
    if col_banda and not df_filtrado.empty
    else 0
)

col1, col2, col3 = st.columns(3)

with col1:
  st.markdown(
      f"""
        <div class="metric-card">
            <div class="metric-title">Registros en Vista</div>
            <div class="metric-value">{reg_count}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with col2:
  st.markdown(
      f"""
        <div class="metric-card">
            <div class="metric-title">Provincias Activas</div>
            <div class="metric-value">{prov_count}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

with col3:
  st.markdown(
      f"""
        <div class="metric-card">
            <div class="metric-title">Grupos Identificados</div>
            <div class="metric-value">{banda_count}</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

st.markdown("<br>", unsafe_allow_html=True)


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

  st.dataframe(df_tabla, use_container_width=True, height=350)

  csv_export = df_tabla.to_csv(index=False).encode("utf-8")
  st.download_button(
      label="📥 Descargar Desglose en CSV",
      data=csv_export,
      file_name="desglose_grupos_registrados_2026.csv",
      mime="text/csv",
  )
else:
  st.warning("No hay registros para mostrar con los filtros seleccionados.")