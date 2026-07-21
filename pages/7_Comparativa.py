import streamlit as st

from components.page_setup import setup_page

from pages.comparativa import (
    accesos,
    penetracion,
    crecimiento,
    ingresos,
)

st.set_page_config(
    page_title="Comparativa · ENACOM",
    page_icon="📊",
    layout="wide",
)

setup_page("Comparativa")

st.title("📊 Comparativa entre servicios")

tabs = st.tabs(
    [
        "Accesos",
        "Penetración",
        "Crecimiento",
        "Ingresos",
    ]
)

with tabs[0]:
    accesos.render()

with tabs[1]:
    penetracion.render()

with tabs[2]:
    crecimiento.render()

with tabs[3]:
    ingresos.render()