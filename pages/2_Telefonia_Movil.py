"""
2_Movil.py
──────────
Vista de Comunicaciones Móviles.
"""

import streamlit as st

from config.constants import MovilCSV
from services.data_manager import DataManager, DataLoadError
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col, sort_by_periodo, filter_by_period,
    melt_tecnologias, last_period_delta,
)
from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import line_chart, bar_chart, area_chart


st.set_page_config(page_title="Móvil · ENACOM", page_icon="📱", layout="wide")

setup_page()

CATEGORIES = ["Resumen general", "Accesos", "Ingresos", "Minutos de voz", "SMS"]

categoria = render_sidebar(CATEGORIES, key="movil_categoria")
st.title("📱 Comunicaciones móviles")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


# ── Resumen general ──────────────────────────────────────────────────────────────────

if categoria == "Resumen general":
    st.header("Resumen general")

    df_acc = load(MovilCSV.ACCESOS)
    df_ing = load(MovilCSV.INGRESOS)

    DataValidator.validate(df_acc, ["anio", "trimestre"])
    DataValidator.validate(df_ing, ["anio", "trimestre"])

    df_acc = sort_by_periodo(add_periodo_col(df_acc))
    df_ing = sort_by_periodo(add_periodo_col(df_ing))

    acc_col = next((c for c in df_acc.columns if "total" in c or "linea" in c or "acceso" in c),
                   df_acc.columns[-1])
    ing_col = next((c for c in df_ing.columns if "ingreso" in c or "miles" in c),
                   df_ing.columns[-1])

    val_acc, delta_acc = last_period_delta(df_acc, acc_col)
    val_ing, delta_ing = last_period_delta(df_ing, ing_col)

    # Prepago vs pospago si existen
    pre_col  = next((c for c in df_acc.columns if "prepago" in c), None)
    pos_col  = next((c for c in df_acc.columns if "pospago" in c), None)

    kpis = [
        {"label": "Líneas activas",    "value": val_acc, "delta": delta_acc, "format": "{:,.0f}"},
        {"label": "Ingresos (miles $)","value": val_ing, "delta": delta_ing, "format": "{:,.0f}"},
    ]
    if pre_col:
        val_pre, delta_pre = last_period_delta(df_acc, pre_col)
        kpis.append({"label": "Prepago", "value": val_pre, "delta": delta_pre, "format": "{:,.0f}"})
    if pos_col:
        val_pos, delta_pos = last_period_delta(df_acc, pos_col)
        kpis.append({"label": "Pospago", "value": val_pos, "delta": delta_pos, "format": "{:,.0f}"})

    show_kpis(kpis)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig = line_chart(df_acc, "periodo", acc_col,
                         title="Evolución de líneas activas", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = bar_chart(df_ing, "periodo", ing_col, title="Ingresos por trimestre")
        st.plotly_chart(fig, use_container_width=True)


# ── Accesos ───────────────────────────────────────────────────────────────────

elif categoria == "Accesos":
    st.header("Líneas móviles activas")

    df = load(MovilCSV.ACCESOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_acc_range")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    acc_col = next((c for c in df.columns if "total" in c or "linea" in c), df.columns[-1])
    val, delta = last_period_delta(df_range, acc_col)

    show_kpis([
        {"label": "Líneas activas", "value": val, "delta": delta, "format": "{:,.0f}"},
    ])

    st.divider()

    pre_col = next((c for c in df.columns if "prepago" in c), None)
    pos_col = next((c for c in df.columns if "pospago" in c), None)

    if pre_col and pos_col:
        df_long = melt_tecnologias(
            df_range, [pre_col, pos_col],
            var_name="Modalidad", value_name="Líneas",
        )
        tab1, tab2 = st.tabs(["Líneas", "Área apilada"])
        with tab1:
            fig = line_chart(df_long, "periodo", "Líneas", "Modalidad",
                             title="Prepago vs pospago")
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            fig = area_chart(df_long, "periodo", "Líneas", "Modalidad",
                             title="Composición prepago / pospago")
            st.plotly_chart(fig, use_container_width=True)
    else:
        fig = line_chart(df_range, "periodo", acc_col,
                         title="Líneas activas — evolución", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver datos"):
        st.dataframe(df_range, use_container_width=True)


# ── Ingresos ──────────────────────────────────────────────────────────────────

elif categoria == "Ingresos":
    st.header("Ingresos del sector móvil")

    df = load(MovilCSV.INGRESOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_ing_range")
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
        fig = line_chart(df_range, "periodo", ing_col, title="Ingresos — evolución", markers=True)
        st.plotly_chart(fig, use_container_width=True)


# ── Minutos de voz ────────────────────────────────────────────────────────────

elif categoria == "Minutos de voz":
    st.header("Minutos de voz cursados")

    df = load(MovilCSV.MINUTOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_min_range")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    min_col = next((c for c in df.columns if "minuto" in c or "total" in c), df.columns[-1])
    val, delta = last_period_delta(df_range, min_col)

    show_kpis([
        {"label": "Minutos (miles)", "value": val, "delta": delta, "format": "{:,.0f}"},
    ])
    st.divider()

    fig = line_chart(df_range, "periodo", min_col,
                     title="Minutos de voz — evolución", markers=True)
    st.plotly_chart(fig, use_container_width=True)


# ── SMS ───────────────────────────────────────────────────────────────────────

elif categoria == "SMS":
    st.header("Mensajes de texto (SMS)")

    df = load(MovilCSV.SMS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_sms_range")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    sms_col = next((c for c in df.columns if "sms" in c or "mensaje" in c or "total" in c),
                   df.columns[-1])
    val, delta = last_period_delta(df_range, sms_col)

    show_kpis([
        {"label": "SMS enviados (miles)", "value": val, "delta": delta, "format": "{:,.0f}"},
    ])
    st.divider()

    tab1, tab2 = st.tabs(["Línea", "Barras"])
    with tab1:
        fig = line_chart(df_range, "periodo", sms_col,
                         title="SMS — evolución histórica", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = bar_chart(df_range, "periodo", sms_col, title="SMS por trimestre")
        st.plotly_chart(fig, use_container_width=True)