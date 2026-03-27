"""
sidebar.py
──────────
Sidebar común para todas las páginas.
"""

import streamlit as st
from config.settings import APP_TITLE, APP_VERSION
from config.theme import ENACOM


def render_sidebar(
    categories: list[str],
    key: str = "categoria",
    default_index: int = 0,
) -> str:
    """
    Renderiza el sidebar y devuelve la categoría seleccionada.

    Parameters
    ----------
    categories    : Lista de strings con las categorías de la página actual.
    key           : Key único del selectbox (evita conflictos entre páginas).
    default_index : Índice de la categoría seleccionada por defecto.

    Returns
    -------
    str — La categoría actualmente seleccionada.
    """
    with st.sidebar:
        
        categoria = st.selectbox(
            "Sección",
            categories,
            index=default_index,
            key=key,
            label_visibility="collapsed",
        )
       
        # st.divider()

        # st.markdown(
        #     f"""
        #     <div style="margin-bottom: 8px;">
        #         <span style="
        #             font-size: 13px;
        #             font-weight: 700;
        #             color: {ENACOM['white']};
        #             letter-spacing: 0.03em;
        #         ">{APP_TITLE}</span>
        #         <br>
        #         <span style="
        #             font-size: 10px;
        #             color: {ENACOM['light_gray']};
        #         ">v{APP_VERSION}</span>
        #     </div>
        #     """,
        #     unsafe_allow_html=True,
        # )

        st.divider()
        _render_footer()

    return categoria


def _render_footer() -> None:
    st.markdown(
        f"""
        <div style="font-size: 11px; color: {ENACOM['light_gray']}; line-height: 1.8;">
            Datos: <a href="https://datosabiertos.enacom.gob.ar"
                      target="_blank"
                      style="color: {ENACOM['cyan']}; text-decoration: none;">
                ENACOM
            <br>
            </a>
                <span style="
                     font-size: 13px;
                     font-weight: 700;
                     color: {ENACOM['white']};
                     letter-spacing: 0.03em;
                ">{APP_TITLE}</span>
            <br>
            Series históricas del sector<br>
            de telecomunicaciones de Argentina
        </div>
        """,
        unsafe_allow_html=True,
    )