import streamlit as st

from components.page_setup import setup_page
from components.sidebar import render_sidebar

from pages.telefonia_movil import (
    resumen,
    
)

st.set_page_config(
    page_title="Móvil · ENACOM",
    page_icon="📱",
    layout="wide"
)

setup_page()

CATEGORIES = [
    "Resumen general",
    "Accesos",
    "Llamadas",
    "Minutos de voz",
    "SMS",
    "Penetración",
    "Ingresos",
]

categoria = render_sidebar(CATEGORIES, key="movil_categoria")

st.title("📱 Comunicaciones móviles")

if categoria == "Resumen general":
    resumen.render()

elif categoria == "Accesos":
    accesos.render()

elif categoria == "Llamadas":
    llamadas.render()

elif categoria == "Minutos de voz":
    minutos.render()

elif categoria == "SMS":
    sms.render()

elif categoria == "Penetración":
    penetracion.render()

elif categoria == "Ingresos":
    ingresos.render()