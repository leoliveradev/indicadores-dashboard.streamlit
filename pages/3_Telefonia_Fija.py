import streamlit as st

from components.page_setup import setup_page

from pages.telefonia_fija import (
    resumen,
    accesos,
    accesos_provincia,
    penetracion,
    penetracion_provincia,
    ingresos,
)

st.set_page_config(
    page_title="Telefonía Fija · ENACOM",
    page_icon="☎️",
    layout="wide",
)

setup_page("Telefonía fija")

st.title("☎️ Telefonía fija")

tabs = st.tabs(
    [
        "Resumen",
        "Accesos",
        "Penetración",
        "Ingresos",
    ]
)

# ============================================================
# RESUMEN
# ============================================================

with tabs[0]:
    resumen.render()

# ============================================================
# ACCESOS
# ============================================================

with tabs[1]:
    vista_accesos = st.pills(
        "",
        [
            "General",
            "Provincia",
        ],
        selection_mode="single",
        default="General",
        key="tel_fija_accesos",
    )

    if vista_accesos == "General":
        accesos.render()
    else:
        accesos_provincia.render()

# ============================================================
# PENETRACIÓN
# ============================================================

with tabs[2]:
    vista_penetracion = st.pills(
        "",
        [
            "General",
            "Provincia",
        ],
        selection_mode="single",
        default="General",
        key="tel_fija_penetracion",
    )

    if vista_penetracion == "General":
        penetracion.render()
    else:
        penetracion_provincia.render()

# ============================================================
# INGRESOS
# ============================================================

with tabs[3]:
    ingresos.render()