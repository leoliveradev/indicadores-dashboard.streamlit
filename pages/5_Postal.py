"""
5_Postal.py
───────────
Vista de Servicios Postales.
"""

import streamlit as st

from config.constants import PostalCSV
from services.data_manager import DataManager, DataLoadError
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col, sort_by_periodo, melt_tecnologias,
    last_period_delta,
)
from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import line_chart, bar_chart, area_chart


st.set_page_config(page_title="Postal · ENACOM", page_icon="📦", layout="wide")

setup_page()

CATEGORIES = ["Overview", "Envíos", "Ingresos"]

categoria = render_sidebar(CATEGORIES, key="postal_categoria")
st.title("📦 Servicios postales")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


# ── Overview ──────────────────────────────────────────────────────────────────

if categoria == "Overview":
    st.header("Resumen general")

    df_env = load(PostalCSV.ENVIOS)
    df_ing = load(PostalCSV.INGRESOS)

    DataValidator.validate(df_env, ["anio", "trimestre"])
    DataValidator.validate(df_ing, ["anio", "trimestre"])

    df_env = sort_by_periodo(add_periodo_col(df_env))
    df_ing = sort_by_periodo(add_periodo_col(df_ing))

    env_col = next((c for c in df_env.columns if "total" in c or "envio" in c or "pieza" in c),
                   df_env.columns[-1])
    ing_col = next((c for c in df_ing.columns if "ingreso" in c or "miles" in c),
                   df_ing.columns[-1])

    val_env, delta_env = last_period_delta(df_env, env_col)
    val_ing, delta_ing = last_period_delta(df_ing, ing_col)

    show_kpis([
        {"label": "Envíos / piezas",    "value": val_env, "delta": delta_env, "format": "{:,.0f}"},
        {"label": "Ingresos (miles $)", "value": val_ing, "delta": delta_ing, "format": "{:,.0f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig = line_chart(df_env, "periodo", env_col,
                         title="Volumen de envíos — evolución", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = bar_chart(df_ing, "periodo", ing_col, title="Ingresos por trimestre")
        st.plotly_chart(fig, use_container_width=True)


# ── Envíos ────────────────────────────────────────────────────────────────────

elif categoria == "Envíos":
    st.header("Volumen de envíos")

    df = load(PostalCSV.ENVIOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="postal_env_range")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    env_col = next((c for c in df.columns if "total" in c or "envio" in c or "pieza" in c),
                   df.columns[-1])
    val, delta = last_period_delta(df_range, env_col)

    show_kpis([
        {"label": "Envíos", "value": val, "delta": delta, "format": "{:,.0f}"},
    ])

    st.divider()

    # Si existen columnas de tipo de envío (carta, encomienda, etc.) mostrar composición
    tipo_cols = [c for c in df.columns if c not in ["anio", "trimestre", "periodo", env_col]
                 and df[c].dtype != object]

    if tipo_cols:
        df_long = melt_tecnologias(df_range, tipo_cols, var_name="Tipo", value_name="Envíos")
        tab1, tab2 = st.tabs(["Por tipo", "Composición"])
        with tab1:
            fig = line_chart(df_long, "periodo", "Envíos", "Tipo",
                             title="Envíos por tipo de servicio")
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            fig = area_chart(df_long, "periodo", "Envíos", "Tipo",
                             title="Composición del volumen postal")
            st.plotly_chart(fig, use_container_width=True)
    else:
        fig = line_chart(df_range, "periodo", env_col,
                         title="Volumen total de envíos", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(df_range, use_container_width=True)


# ── Ingresos ──────────────────────────────────────────────────────────────────

elif categoria == "Ingresos":
    st.header("Ingresos del sector postal")

    df = load(PostalCSV.INGRESOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="postal_ing_range")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    ing_col = next((c for c in df.columns if "ingreso" in c or "miles" in c), df.columns[-1])
    val, delta = last_period_delta(df_range, ing_col)

    show_kpis([
        {"label": "Ingresos (miles $)", "value": val, "delta": delta, "format": "{:,.0f}"},
    ])

    st.divider()

    tab1, tab2 = st.tabs(["Barras", "Línea"])
    with tab1:
        fig = bar_chart(df_range, "periodo", ing_col, title="Ingresos por trimestre")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_range, "periodo", ing_col,
                         title="Ingresos — evolución", markers=True)
        st.plotly_chart(fig, use_container_width=True)