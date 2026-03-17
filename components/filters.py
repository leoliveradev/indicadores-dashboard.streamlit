"""
filters.py
──────────
Widgets de filtro inline — se renderizan en el cuerpo de la página,
no en el sidebar.

Uso en cada página:
    anio, trimestre = render_period_filters(df)
    provincia = render_provincia_filter(df)
"""

import streamlit as st
import pandas as pd


def render_period_filters(
    df: pd.DataFrame,
    key_prefix: str = "",
) -> tuple[int, int]:
    """
    Barra de filtros de año y trimestre en columnas inline.
    Devuelve (anio, trimestre).
    """
    col1, col2, *_ = st.columns([1, 1, 3])  # los 2 filtros + espacio vacío

    anios = sorted(df["anio"].unique(), reverse=True)
    trimestres = sorted(df["trimestre"].unique())
    labels = {1: "T1 (Ene–Mar)", 2: "T2 (Abr–Jun)", 3: "T3 (Jul–Sep)", 4: "T4 (Oct–Dic)"}

    with col1:
        anio = st.selectbox("Año", anios, key=f"{key_prefix}_anio")
    with col2:
        trimestre = st.selectbox(
            "Trimestre",
            trimestres,
            format_func=lambda t: labels.get(t, f"T{t}"),
            key=f"{key_prefix}_trimestre",
        )

    return anio, trimestre


def render_period_and_provincia_filters(
    df: pd.DataFrame,
    key_prefix: str = "",
    include_todas: bool = True,
) -> tuple[int, int, str]:
    """
    Barra de filtros de año, trimestre y provincia en columnas inline.
    Devuelve (anio, trimestre, provincia).
    """
    col1, col2, col3 = st.columns([1, 1, 2])

    anios = sorted(df["anio"].unique(), reverse=True)
    trimestres = sorted(df["trimestre"].unique())
    labels = {1: "T1 (Ene–Mar)", 2: "T2 (Abr–Jun)", 3: "T3 (Jul–Sep)", 4: "T4 (Oct–Dic)"}

    provincias = sorted(df["provincia"].dropna().unique()) if "provincia" in df.columns else []
    if include_todas:
        provincias = ["Todas"] + provincias

    with col1:
        anio = st.selectbox("Año", anios, key=f"{key_prefix}_anio")
    with col2:
        trimestre = st.selectbox(
            "Trimestre",
            trimestres,
            format_func=lambda t: labels.get(t, f"T{t}"),
            key=f"{key_prefix}_trimestre",
        )
    with col3:
        provincia = st.selectbox("Provincia", provincias, key=f"{key_prefix}_provincia")

    return anio, trimestre, provincia


def render_range_filter(
    df: pd.DataFrame,
    key_prefix: str = "",
) -> tuple[int, int]:
    """
    Slider de rango de años para gráficos de evolución histórica.
    Devuelve (anio_desde, anio_hasta).
    """
    anios = sorted(df["anio"].unique())
    if len(anios) < 2:
        return anios[0], anios[-1]

    col1, *_ = st.columns([2, 2])
    with col1:
        return st.select_slider(
            "Rango de años",
            options=anios,
            value=(anios[0], anios[-1]),
            key=f"{key_prefix}_range",
        )
