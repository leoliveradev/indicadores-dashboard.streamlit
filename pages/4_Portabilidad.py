import streamlit as st

from components.page_setup import setup_page
from components.sidebar import render_sidebar

from pages.portabilidad import (
    resumen,
    movil,
)

st.set_page_config(
    page_title="Portabilidad · ENACOM",
    page_icon="🔄",
    layout="wide",
)

setup_page()

CATEGORIES = [
    "Resumen general",
    "Telefonía móvil",
]

categoria = render_sidebar(
    CATEGORIES,
    key="port_categoria",
)

st.title("🔄 Portabilidad numérica")

if categoria == "Resumen general":
    resumen.render()

elif categoria == "Telefonía móvil":
    movil.render()