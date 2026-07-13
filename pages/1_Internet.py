import streamlit as st

from components.page_setup import setup_page
from components.sidebar import render_sidebar

from pages.internet import (
    resumen,
    tecnologia,
    tecnologia_provincia,
    velocidad_media,
    # velocidad_media_provincia,
    rangos_velocidad,
    # rangos_velocidad_provincia,
    banda_ancha,
    # banda_ancha_provincia,
    penetracion,
    # penetracion_provincia,
    ingresos,
)


st.set_page_config(
    page_title="Internet · ENACOM",
    page_icon="🌐",
    layout="wide",
)

setup_page()

CATEGORIES = [
    "Resumen general",
    "Tecnología",
    "Tecnología - provincia",
    "Velocidad media",
    "Velocidad media - provincia",
    "Rangos de velocidad",
    "Rangos de velocidad - provincia",
    "Banda ancha vs Dial-up",
    "Banda ancha - provincia",
    "Penetración",
    "Penetración - provincia",
    "Ingresos",
]

categoria = render_sidebar(
    CATEGORIES,
    key="internet_categoria",
)

st.title("🌐 Internet fijo")


if categoria == "Resumen general":
    resumen.render()

elif categoria == "Tecnología":
    tecnologia.render()

elif categoria == "Tecnología - provincia":
    tecnologia_provincia.render()

elif categoria == "Velocidad media":
    velocidad_media.render()

elif categoria == "Velocidad media - provincia":
    velocidad_media_provincia.render()

elif categoria == "Rangos de velocidad":
    rangos_velocidad.render()

elif categoria == "Rangos de velocidad - provincia":
    rangos_velocidad_provincia.render()

elif categoria == "Banda ancha vs Dial-up":
    banda_ancha.render()

elif categoria == "Banda ancha - provincia":
    banda_ancha_provincia.render()

elif categoria == "Penetración":
    penetracion.render()

elif categoria == "Penetración - provincia":
    penetracion_provincia.render()

elif categoria == "Ingresos":
    ingresos.render()