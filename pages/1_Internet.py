import streamlit as st

from components.page_setup import setup_page

from pages.internet import (
    resumen,
    tecnologia,
    tecnologia_provincia,
    velocidad_media,
    velocidad_media_provincia,
    rangos_velocidad,
    rangos_velocidad_provincia,
    banda_ancha,
    banda_ancha_provincia,
    penetracion,
    penetracion_provincia,
    ingresos,
)

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Internet · ENACOM",
    page_icon="🌐",
    layout="wide",
)

setup_page("Internet")
# ============================================================
# HEADER
# ============================================================

st.title("🌐 Internet fijo")

# st.caption(
#     "Indicadores de accesos, velocidad, tecnología, penetración e ingresos del servicio de internet fijo."
# )

# ============================================================
# TABS PRINCIPALES
# ============================================================

tabs = st.tabs(
    [
        "Resumen",
        "Velocidad",
        "Tecnología",
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
# VELOCIDAD
# ============================================================

with tabs[1]:

    vista_velocidad = st.pills(
        "vista_velocidad",
        [
            "Velocidad media",
            "Velocidad media - provincia",
            "Rangos de velocidad",
            "Rangos - provincia",
        ],
        selection_mode="single",
        default="Velocidad media",
        key="internet_velocidad",
        label_visibility="collapsed",
    )

    if vista_velocidad == "Velocidad media":
        velocidad_media.render()

    elif vista_velocidad == "Velocidad media - provincia":
        velocidad_media_provincia.render()

    elif vista_velocidad == "Rangos de velocidad":
        rangos_velocidad.render()

    else:
        rangos_velocidad_provincia.render()

# ============================================================
# TECNOLOGÍA
# ============================================================

with tabs[2]:
    vista_tecnologia = st.radio(
        "vista_tecnologia",
        [
            "Nacional",
            "Provincia",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="internet_tecnologia",
    )

    if vista_tecnologia == "Nacional":
        tecnologia.render()

    else:
        tecnologia_provincia.render()

# ============================================================
# ACCESOS
# ============================================================

with tabs[3]:
    vista_accesos = st.radio(
        "vista_accesos",
        [
            "Banda ancha vs Dial-Up",
            "Provincia",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="internet_accesos",
    )

    if vista_accesos == "Banda ancha vs Dial-Up":
        banda_ancha.render()

    else:
        banda_ancha_provincia.render()

# ============================================================
# PENETRACIÓN
# ============================================================

with tabs[4]:
    vista_penetracion = st.radio(
        "vista_penetracion",
        [
            "Nacional",
            "Provincia",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="internet_penetracion",
    )

    if vista_penetracion == "Nacional":
        penetracion.render()

    else:
        penetracion_provincia.render()

# ============================================================
# INGRESOS
# ============================================================

with tabs[5]:
    ingresos.render()