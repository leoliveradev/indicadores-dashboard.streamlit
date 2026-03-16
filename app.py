import streamlit as st
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT
from config.theme import STREAMLIT_CSS, ENACOM

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
)

# Aplica la paleta institucional ENACOM en toda la app
st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)

st.title(f"{APP_ICON} {APP_TITLE}")

st.markdown("""
Este dashboard explora datos del sector de telecomunicaciones de Argentina,
basado en series históricas publicadas por **ENACOM**.
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **Servicios disponibles**
    - 🌐 Internet fijo
    - 📱 Telefonía móvil
    - ☎️ Telefonía fija
    - 📺 TV paga
    - 📦 Servicios postales
    """)

with col2:
    st.markdown("""
    **Dimensiones de análisis**
    - Evolución temporal (año / trimestre)
    - Desagregado por provincia
    - Desagregado por localidad
    - Por tecnología y velocidad
    """)

with col3:
    st.markdown("""
    **Fuentes**
    - [ENACOM — Datos abiertos](https://datosabiertos.enacom.gob.ar)
    - Series históricas del sector
    """)

st.divider()
st.info("Seleccioná una sección en el menú lateral.", icon="👈")