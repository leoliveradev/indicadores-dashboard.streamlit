"""
3_TV.py
───────
Vista de TV Paga.
"""

import streamlit as st

from config.constants import TVCSVs
from services.data_manager import DataManager, DataLoadError
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col, sort_by_periodo, filter_by_period,
    melt_tecnologias, last_period_delta, aggregate_by_periodo,
)
from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.filters import anio_selector, trimestre_selector, periodo_range_selector
from components.charts import line_chart, bar_chart, area_chart


st.set_page_config(page_title="TV Paga · ENACOM", page_icon="📺", layout="wide")

setup_page()

CATEGORIES = ["Overview", "Accesos", "Ingresos"]

categoria = render_sidebar(CATEGORIES, key="tv_categoria")
st.title("📺 TV paga")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


# ── Overview ──────────────────────────────────────────────────────────────────

if categoria == "Overview":
    st.header("Resumen general")

    df_acc = load(TVCSVs.ACCESOS)
    df_ing = load(TVCSVs.INGRESOS)

    DataValidator.validate(df_acc, ["anio", "trimestre"])
    DataValidator.validate(df_ing, ["anio", "trimestre"])

    df_acc = sort_by_periodo(add_periodo_col(df_acc))
    df_ing = sort_by_periodo(add_periodo_col(df_ing))

    acc_col = next((c for c in df_acc.columns if "total" in c or "acceso" in c), df_acc.columns[-1])
    ing_col = next((c for c in df_ing.columns if "ingreso" in c or "miles" in c or "monto" in c), df_ing.columns[-1])

    val_acc, delta_acc = last_period_delta(df_acc, acc_col)
    val_ing, delta_ing = last_period_delta(df_ing, ing_col)

    show_kpis([
        {"label": "Suscripciones activas", "value": val_acc, "delta": delta_acc, "format": "{:,.0f}"},
        {"label": "Ingresos (miles $)",    "value": val_ing, "delta": delta_ing, "format": "{:,.0f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        fig = line_chart(df_acc, x="periodo", y=acc_col,
                         title="Evolución de suscripciones", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = bar_chart(df_ing, x="periodo", y=ing_col,
                        title="Ingresos por trimestre")
        st.plotly_chart(fig, use_container_width=True)


# ── Accesos ───────────────────────────────────────────────────────────────────

elif categoria == "Accesos":
    st.header("Accesos a TV paga")

    df = load(TVCSVs.ACCESOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = periodo_range_selector(df, key="tv_acc_range")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    acc_col = next((c for c in df.columns if "total" in c or "acceso" in c), df.columns[-1])
    val, delta = last_period_delta(df_range, acc_col)

    show_kpis([
        {"label": "Suscripciones", "value": val, "delta": delta, "format": "{:,.0f}"},
    ])

    st.divider()

    # Si hay columnas de tecnología (cable, satélite, IPTV), mostrarlas
    tec_cols = [c for c in df.columns if c not in ["anio", "trimestre", "periodo", acc_col]
                and df[c].dtype != object]

    if tec_cols:
        st.subheader("Evolución por tipo de servicio")
        df_long = melt_tecnologias(df_range, tec_cols, var_name="Tipo", value_name="Suscripciones")
        tab1, tab2 = st.tabs(["Líneas", "Área apilada"])
        with tab1:
            fig = line_chart(df_long, "periodo", "Suscripciones", "Tipo",
                             title="Suscripciones por tipo de servicio")
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            fig = area_chart(df_long, "periodo", "Suscripciones", "Tipo",
                             title="Composición en el tiempo")
            st.plotly_chart(fig, use_container_width=True)
    else:
        fig = line_chart(df_range, "periodo", acc_col,
                         title="Accesos a TV paga", markers=True)
        st.plotly_chart(fig, use_container_width=True)


# ── Ingresos ──────────────────────────────────────────────────────────────────

elif categoria == "Ingresos":
    st.header("Ingresos del sector")

    df = load(TVCSVs.INGRESOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = periodo_range_selector(df, key="tv_ing_range")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    ing_col = next((c for c in df.columns if "ingreso" in c or "miles" in c or "monto" in c),
                   df.columns[-1])
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
        fig = line_chart(df_range, "periodo", ing_col, title="Ingresos — evolución", markers=True)
        st.plotly_chart(fig, use_container_width=True)