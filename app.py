import folium
import geopandas as gpd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Visor Analítico de Seguridad - Panamá", layout="wide"
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

# --- APLICACIÓN PRINCIPAL ---
st.title("🗺️ Visor Geográfico de Seguridad - Panamá")
st.markdown("Inteligencia de datos y análisis espacial.")


# Cargar y reproyectar datos automáticamente con GeoPandas
@st.cache_data
def cargar_y_reproyectar():
  # Lee el archivo GeoJSON sin importar su sistema de coordenadas original
  gdf = gpd.read_file("Pandillas_2026.json")

  # Si el sistema de coordenadas no es WGS84 (EPSG:4326), lo convierte automáticamente
  if gdf.crs and gdf.crs.to_epsg() != 4326:
    gdf = gdf.to_crs(epsg=4326)

  return gdf


try:
  gdf = cargar_y_reproyectar()

  # Métricas rápidas
  st.metric("Total de Registros Georreferenciados", len(gdf))

  # Crear el mapa base centrado en Panamá
  m = folium.Map(location=[8.538, -80.7821], zoom_start=8, tiles="OpenStreetMap")

  # Agregar la capa corregida al mapa de Folium
  folium.GeoJson(
      gdf,
      name="Puntos de Pandillas",
      popup=folium.GeoJsonPopup(
          fields=[
              col for col in gdf.columns if col != "geometry"
          ]  # Muestra todas las propiedades al hacer clic
      ),
  ).add_to(m)

  # Renderizar el mapa en Streamlit
  st_folium(m, width="100%", height=600)

except Exception as e:
  st.error(f"Error al procesar las capas geográficas: {e}")