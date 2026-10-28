import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

# Configuración de la página
st.set_page_config(
    page_title="Visor Analítico de Seguridad - Panamá",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- SISTEMA DE AUTENTICACIÓN / CLAVE ---
CLAVE_CORRECTA = "MiClaveSecreta123"

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔒 Acceso Restringido")
    password_input = st.text_input("Ingrese la contraseña de acceso:", type="password")
    if st.button("Ingresar"):
        if password_input == CLAVE_CORRECTA:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    st.stop()  # Detiene la ejecución hasta que se autentique

# --- APPLICACIÓN PRINCIPAL (UNA VEZ INICIADA SESIÓN) ---
st.title("🗺️ Visor Geográfico de Seguridad - Panamá")
st.markdown("Análisis espacial e inteligencia de datos.")

# Cargar el archivo espacial GeoJSON con GeoPandas
@st.cache_data
def cargar_datos():
    # GeoPandas gestiona automáticamente el CRS y la geometría
    gdf = gpd.read_file("Pandillas_2026.json")
    # Asegurar reproyección a WGS84 si viene en coordenadas UTM en metros
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf

try:
    gdf = cargar_datos()

    # Métricas ejecutivas en tarjetas
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Registros", len(gdf))
    # Ejemplo si tienes columnas específicas:
    # col2.metric("Provincias Impactadas", gdf['PROVINCIA'].nunique())

    st.markdown("---")

    # Crear el mapa base centrado en Panamá con Folium
    m = folium.Map(location=[8.538, -80.7821], zoom_start=8, tiles="OpenStreetMap")

    # Agregar la capa GeoJSON con popups interactivos
    folium.GeoJson(
        gdf,
        name="Capas Georreferenciadas",
        popup=folium.GeoJsonPopup(fields=list(gdf.columns.drop("geometry"))),
        tooltip=folium.GeoJsonTooltip(fields=list(gdf.columns.drop("geometry"))[:2]),
    ).add_to(m)

    # Renderizar el mapa interactivo en la app web
    st_folium(m, width="100%", height=600)

except Exception as e:
    st.error(f"Error al cargar la capa geográfica: {e}")