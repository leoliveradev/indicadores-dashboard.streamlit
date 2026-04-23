import streamlit as st

API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:3000/api")
TIMEOUT_CONEXION = 50

# ── App ────────────────────────────────────────────────────────────────────
APP_TITLE = "ENACOM - Indicadores"
APP_ICON = "📡"
APP_LAYOUT = "wide"
APP_VERSION = "1.0.0"