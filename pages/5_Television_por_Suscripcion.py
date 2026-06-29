import streamlit as st
from components.page_setup import setup_page
from components.sidebar import render_sidebar

from pages.tv import (
    resumen,
    accesos,
    accesos_provincia,
    penetracion,
    penetracion_provincia,
    ingresos,
)

st.set_page_config(page_title="TV Paga · ENACOM", page_icon="📺", layout="wide")
setup_page()

CATEGORIES = [
    "Resumen general",
    "Accesos",
    "Accesos - provincia",
    "Penetración",
    "Penetración - provincia",
    "Ingresos",
]

categoria = render_sidebar(CATEGORIES, key="tv_categoria")
st.title("📺 Televisión por suscripción")

if categoria == "Resumen general":
    resumen.render()

elif categoria == "Accesos":
    accesos.render()

elif categoria == "Accesos - provincia":
    accesos_provincia.render()

elif categoria == "Penetración":
    penetracion.render()

elif categoria == "Penetración - provincia":
    penetracion_provincia.render()

elif categoria == "Ingresos":
    ingresos.render()
