"""
Widgets de filtros para el dashboard de ENACOM.
Cada página importa `render_filters` y llama con sus propios filtros.
"""

import streamlit as st
import pandas as pd

def anio_selector(df: pd.DataFrame, key: str = "anio") -> int:
    """Selectbox de año, ordenado descendente (más reciente primero)."""
    anios = sorted(df["anio"].unique(), reverse=True)
    return st.sidebar.selectbox("Año", anios, key=key)

def trimestre_selector(df: pd.DataFrame, key: str = "trimestre") -> int:
    """Selectbox de trimestre, ordenado ascendente (1, 2, 3, 4)."""
    trimestres = sorted(df["trimestre"].unique())
    labels = {1: "T1 (Ene-Mar)", 2: "T2 (Abr-Jun)", 3: "T3 (Jul-Sep)", 4: "T4 (Oct-Dic)"}
    options = trimestres
    return st.sidebar.selectbox(
        "Trimestre",
        options,
        format_func=lambda t: labels.get(t, f"T{t}"),
        key=key
    )

def provincia_selector(
        df: pd.DataFrame,
        key: str = "provincia",
        include_all: bool = True
) -> str:
    """Selectbox de provincia, con opción "Todas" al inicio si `include_all` es True."""
    provincias = sorted(df["provincia"].dropna().unique())
    if include_all:
        provincias = ["Todas"] + provincias
    return st.sidebar.selectbox("Provincia", provincias, key=key)

def periodo_range_selector(
    df: pd.DataFrame,
    key: str = "periodo_range"
) -> tuple[int, int]:
    """
    Slider de rango de años para gráficos de evolución.
    Devuelve (anio_desde, anio_hasta)
    """
    anios = sorted(df["anio"].unique())
    if len(anios) < 2:
        return anios[0], anios[-1]
    
    return st.sidebar.select_slider(
        "Rango de años",
        options=anios,
        value=(anios[0], anios[-1]),
        key=key
    )