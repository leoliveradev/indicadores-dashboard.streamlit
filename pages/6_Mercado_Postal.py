import streamlit as st

from components.page_setup import setup_page
from components.sidebar import render_sidebar

from pages.mercado_postal import (
    resumen,
    facturacion,
)

st.set_page_config(
    page_title="Postal · ENACOM",
    page_icon="📦",
    layout="wide",
)

setup_page()

CATEGORIES = [
    "Resumen general",
    "Facturación",
    "Producción",
    "Facturación y producción - provincia",
    "Personal ocupado",
]

categoria = render_sidebar(
    CATEGORIES,
    key="postal_categoria",
)

st.title("📦 Mercado postal")

if categoria == "Resumen general":
    resumen.render()

elif categoria == "Facturación":
    facturacion.render()

elif categoria == "Producción":
    produccion.render()

elif categoria == "Facturación y producción - provincia":
    provincia.render()

elif categoria == "Personal ocupado":
    personal_ocupado.render()