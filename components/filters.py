"""
filters.py
──────────
Filtros inline con header integrado: título a la izquierda, filtros a la derecha.
Default automático: último período con datos disponible en el DataFrame.
"""

import streamlit as st
import pandas as pd


TRIMESTRE_LABELS = {
    1: "T1 — Ene/Mar",
    2: "T2 — Abr/Jun",
    3: "T3 — Jul/Sep",
    4: "T4 — Oct/Dic",
}


def _ultimo_periodo(df: pd.DataFrame) -> tuple[int, int]:
    """Devuelve (anio, trimestre) del último período con datos en el DataFrame."""
    ultimo = df.sort_values(["anio", "trimestre"]).iloc[-1]
    return int(ultimo["anio"]), int(ultimo["trimestre"])


def render_header_with_filters(
    titulo: str,
    df: pd.DataFrame,
    key_prefix: str = "",
) -> tuple[int, int]:
    """
    Header con filtros de año y trimestre en la misma línea.
    Título a la izquierda, selectboxes a la derecha.
    Incluye espaciado inferior antes del contenido.
    Devuelve (anio, trimestre).
    """
    anios = sorted(df["anio"].unique(), reverse=True)

    col_titulo, col_anio, col_trim = st.columns([3, 1, 1])

    with col_titulo:
        st.header(titulo)

    with col_anio:
        # Pequeño espaciado para alinear verticalmente con el header
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        anio = st.selectbox(
            "Año",
            options=[int(a) for a in anios],
            index=0,
            key=f"{key_prefix}_anio",
            label_visibility="collapsed",
        )

    trims_del_anio = sorted(
        df[df["anio"] == anio]["trimestre"].unique(), reverse=True
    )
    with col_trim:
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        trimestre = st.selectbox(
            "Trimestre",
            options=[int(t) for t in trims_del_anio],
            index=0,
            format_func=lambda t: TRIMESTRE_LABELS.get(t, f"T{t}"),
            key=f"{key_prefix}_trimestre",
            label_visibility="collapsed",
        )

    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

    return anio, trimestre


def render_header_with_filters_and_provincia(
    titulo: str,
    df: pd.DataFrame,
    key_prefix: str = "",
    include_todas: bool = True,
) -> tuple[int, int, str]:
    """
    Header con año, trimestre y provincia en la misma línea.
    Devuelve (anio, trimestre, provincia).
    """
    anios = sorted(df["anio"].unique(), reverse=True)
    provincias = sorted(df["provincia"].dropna().unique()) if "provincia" in df.columns else []
    if include_todas:
        provincias = ["Todas"] + provincias

    col_titulo, col_anio, col_trim, col_prov = st.columns([2, 1, 1, 1])

    with col_titulo:
        st.header(titulo)

    with col_anio:
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        anio = st.selectbox(
            "Año",
            options=[int(a) for a in anios],
            index=0,
            key=f"{key_prefix}_anio",
            label_visibility="collapsed",
        )

    trims_del_anio = sorted(
        df[df["anio"] == anio]["trimestre"].unique(), reverse=True
    )
    with col_trim:
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        trimestre = st.selectbox(
            "Trimestre",
            options=[int(t) for t in trims_del_anio],
            index=0,
            format_func=lambda t: TRIMESTRE_LABELS.get(t, f"T{t}"),
            key=f"{key_prefix}_trimestre",
            label_visibility="collapsed",
        )

    with col_prov:
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        provincia = st.selectbox(
            "Provincia",
            options=provincias,
            key=f"{key_prefix}_provincia",
            label_visibility="collapsed",
        )

    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

    return anio, trimestre, provincia


def render_period_filters(
    df: pd.DataFrame,
    key_prefix: str = "",
) -> tuple[int, int]:
    """
    Filtros sin header — año y trimestre a la derecha.
    Para secciones donde el header ya fue renderizado por separado.
    """
    anios = sorted(df["anio"].unique(), reverse=True)

    _, col_anio, col_trim = st.columns([2, 1, 1])

    with col_anio:
        anio = st.selectbox(
            "Año",
            options=[int(a) for a in anios],
            index=0,
            key=f"{key_prefix}_anio",
        )

    trims_del_anio = sorted(
        df[df["anio"] == anio]["trimestre"].unique(), reverse=True
    )
    with col_trim:
        trimestre = st.selectbox(
            "Trimestre",
            options=[int(t) for t in trims_del_anio],
            index=0,
            format_func=lambda t: TRIMESTRE_LABELS.get(t, f"T{t}"),
            key=f"{key_prefix}_trimestre",
        )

    return anio, trimestre


def render_period_and_provincia_filters(
    df: pd.DataFrame,
    key_prefix: str = "",
    include_todas: bool = True,
) -> tuple[int, int, str]:
    """Filtros sin header — año, trimestre y provincia a la derecha."""
    anios = sorted(df["anio"].unique(), reverse=True)
    provincias = sorted(df["provincia"].dropna().unique()) if "provincia" in df.columns else []
    if include_todas:
        provincias = ["Todas"] + provincias

    _, col_anio, col_trim, col_prov = st.columns([1, 1, 1, 1])

    with col_anio:
        anio = st.selectbox(
            "Año", options=[int(a) for a in anios],
            index=0, key=f"{key_prefix}_anio",
        )

    trims_del_anio = sorted(
        df[df["anio"] == anio]["trimestre"].unique(), reverse=True
    )
    with col_trim:
        trimestre = st.selectbox(
            "Trimestre",
            options=[int(t) for t in trims_del_anio],
            index=0,
            format_func=lambda t: TRIMESTRE_LABELS.get(t, f"T{t}"),
            key=f"{key_prefix}_trimestre",
        )

    with col_prov:
        provincia = st.selectbox(
            "Provincia", options=provincias,
            key=f"{key_prefix}_provincia",
        )

    return anio, trimestre, provincia


def render_range_filter(
    df: pd.DataFrame,
    key_prefix: str = "",
) -> tuple[int, int]:
    """Slider de rango de años a la derecha."""
    anios = sorted(df["anio"].unique())
    if len(anios) < 2:
        return int(anios[0]), int(anios[-1])

    _, col_slider = st.columns([2, 2])
    with col_slider:
        result = st.select_slider(
            "Rango de años",
            options=[int(a) for a in anios],
            value=(int(anios[0]), int(anios[-1])),
            key=f"{key_prefix}_range",
        )
    return result

def render_header_with_range_filter(
    titulo: str,
    df: pd.DataFrame,
    key_prefix: str = "",
) -> tuple[int, int]:
    """
    Header con slider de rango de años en la misma línea.
    Título a la izquierda, slider a la derecha.
    Devuelve (anio_desde, anio_hasta).
    """
    anios = sorted(df["anio"].unique())
    if len(anios) < 2:
        return int(anios[0]), int(anios[-1])
 
    col_titulo, col_slider = st.columns([2, 2])
 
    with col_titulo:
        st.header(titulo)
 
    with col_slider:
        st.markdown("<div style='margin-top:8px'></div>", unsafe_allow_html=True)
        result = st.select_slider(
            "Rango de años",
            options=[int(a) for a in anios],
            value=(int(anios[0]), int(anios[-1])),
            key=f"{key_prefix}_range",
            label_visibility="collapsed",
        )
 
    st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)
    return result
 

# ── Compatibilidad sidebar (legacy) ──────────────────────────────────────────

def anio_selector(df: pd.DataFrame, key: str = "anio") -> int:
    anios = sorted(df["anio"].unique(), reverse=True)
    return st.sidebar.selectbox("Año", anios, key=key)


def trimestre_selector(df: pd.DataFrame, key: str = "trimestre") -> int:
    trimestres = sorted(df["trimestre"].unique())
    return st.sidebar.selectbox(
        "Trimestre", trimestres,
        format_func=lambda t: TRIMESTRE_LABELS.get(t, f"T{t}"),
        key=key,
    )


def periodo_range_selector(df: pd.DataFrame, key: str = "periodo_range") -> tuple[int, int]:
    anios = sorted(df["anio"].unique())
    if len(anios) < 2:
        return int(anios[0]), int(anios[-1])
    return st.sidebar.select_slider(
        "Rango de años", options=anios,
        value=(int(anios[0]), int(anios[-1])), key=key,
    )