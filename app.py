import folium
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

try:
  # Crear el mapa base centrado en Panamá
  m = folium.Map(location=[8.538, -80.7821], zoom_start=8, tiles="OpenStreetMap")

  # Cargar el archivo JSON/GeoJSON con los puntos directamente
  folium.GeoJson(
      "Pandillas_2026.json",
      name="Puntos de Pandillas",
  ).add_to(m)

  # Renderizar el mapa interactivo en Streamlit
  st_folium(m, width="100%", height=600)

except Exception as e:
  st.error(f"Error al cargar la capa geográfica: {e}")