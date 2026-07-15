import streamlit as st
from components.page_setup import setup_page
from config.settings import APP_TITLE, APP_ICON, APP_LAYOUT
from config.theme import CARD_CSS, STREAMLIT_CSS, ENACOM

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=APP_LAYOUT,
    initial_sidebar_state="collapsed",
)

setup_page("Inicio")

def service_card(icon, title, desc, page):
    st.markdown(f"""
    <a href="{page}" target="_self" class="card-link">
        <div class="card">
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-desc">{desc}</div>
        </div>
    </a>
    """, unsafe_allow_html=True)

# Aplica la paleta institucional ENACOM en toda la app
st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)
st.markdown(CARD_CSS, unsafe_allow_html=True)

st.title(f"{APP_ICON} {APP_TITLE}")

st.markdown("""
Este dashboard explora datos del sector de telecomunicaciones de Argentina,
basado en series históricas publicadas por **ENACOM**.
""")

col1, col2, col3 = st.columns(3)

with col1:
    service_card(
        "🌐",
        "Internet fijo",
        "Conectividad, velocidad y accesos",
        "/Internet"
    )

with col2:
    service_card(
        "📱",
        "Telefonía móvil",
        "Líneas, tráfico y penetración",
        "/Telefonia_Movil"
    )

with col3:
    service_card(
        "☎️",
        "Telefonía fija",
        "Evolución del servicio tradicional",
        "/Telefonia_Fija"
    )

col4, col5, col6 = st.columns(3)

with col4:
    service_card(
        "📺",
        "TV por suscripción",
        "Suscripciones y tecnologías",
        "/Television_por_Suscripcion"
    )

with col5:
    service_card(
        "📦",
        "Servicios postales",
        "Logística y volumen de envíos",
        "/Mercado_Postal"
    )

st.divider()

st.markdown("""
**Fuentes**
- [ENACOM — Datos abiertos](https://datosabiertos.enacom.gob.ar)
""")
