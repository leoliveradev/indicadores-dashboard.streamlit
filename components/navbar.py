import streamlit as st
from streamlit_option_menu import option_menu


PAGES = {
    "Inicio": "app.py",
    "Internet": "pages/1_Internet.py",
    "Telefonía móvil": "pages/2_Telefonia_Movil.py",
    "Telefonía fija": "pages/3_Telefonia_Fija.py",
    "TV": "pages/5_Television_por_Suscripcion.py",
    "Postal": "pages/6_Mercado_Postal.py",
    "Comparativa": "pages/7_Comparativa.py",
}


def render_navbar(current_page: str | None = None):

    selected = option_menu(
        menu_title=None,
        options=list(PAGES.keys()),
        icons=[
            "house",
            "globe",
            "phone",
            "telephone",
            "tv",
            "box",
            "bar-chart",
        ],
        orientation="horizontal",
        default_index=(
            list(PAGES.keys()).index(current_page)
            if current_page in PAGES
            else 0
        ),
    )

    if selected != current_page:
        st.switch_page(PAGES[selected])

    return selected