"""
page_setup.py
─────────────
Helper para configurar cada página con el tema institucional.

Llamar al inicio de cada página, DESPUÉS de st.set_page_config():

    from components.page_setup import setup_page
    setup_page()
"""

import streamlit as st
from config.theme import STREAMLIT_CSS


def setup_page() -> None:
    """Inyecta el CSS institucional de ENACOM en la página actual."""
    st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)