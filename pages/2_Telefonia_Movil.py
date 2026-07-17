import streamlit as st

from components.page_setup import setup_page

from pages.telefonia_movil import (
    resumen,
    accesos,
    llamadas,
    minutos,
    sms,
    penetracion,
    ingresos,
)

from pages.portabilidad import movil as portabilidad

st.set_page_config(
    page_title="Móvil · ENACOM",
    page_icon="📱",
    layout="wide",
)

setup_page("Telefonía móvil")

st.title("📱 Comunicaciones móviles")

tabs = st.tabs(
    [
        "Resumen",
        "Accesos",
        "Llamadas",
        "Minutos",
        "SMS",
        "Penetración",
        "Ingresos",
        "Portabilidad",
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
    accesos.render()

# ============================================================
# LLAMADAS
# ============================================================

with tabs[2]:
    llamadas.render()

# ============================================================
# MINUTOS
# ============================================================

with tabs[3]:
    minutos.render()

# ============================================================
# SMS
# ============================================================

with tabs[4]:
    sms.render()

# ============================================================
# PENETRACIÓN
# ============================================================

with tabs[5]:
    penetracion.render()

# ============================================================
# INGRESOS
# ============================================================

with tabs[6]:
    ingresos.render()

# ============================================================
# PORTABILIDAD
# ============================================================

with tabs[7]:
    portabilidad.render()