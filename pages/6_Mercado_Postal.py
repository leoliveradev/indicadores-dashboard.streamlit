import streamlit as st

from components.page_setup import setup_page

from pages.mercado_postal import (
    resumen,
    facturacion,
    produccion,
    provincia,
    personal_ocupado,
)

st.set_page_config(
    page_title="Postal · ENACOM",
    page_icon="📦",
    layout="wide",
)

setup_page("Postal")

st.title("📦 Mercado postal")

tabs = st.tabs(
    [
        "Resumen",
        "Actividad",
        "Personal ocupado",
    ]
)

# ============================================================
# RESUMEN
# ============================================================

with tabs[0]:
    resumen.render()

# ============================================================
# ACTIVIDAD
# ============================================================

with tabs[1]:
    vista_actividad = st.pills(
        "",
        [
            "Facturación",
            "Producción",
            "Provincia",
        ],
        selection_mode="single",
        default="Facturación",
        key="postal_actividad",
    )

    if vista_actividad == "Facturación":
        facturacion.render()

    elif vista_actividad == "Producción":
        produccion.render()

    else:
        provincia.render()

# ============================================================
# PERSONAL OCUPADO
# ============================================================

with tabs[2]:
    personal_ocupado.render()