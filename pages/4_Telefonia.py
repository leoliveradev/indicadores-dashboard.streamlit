"""
4_Telefonia.py
──────────────
Vista de Telefonía Fija.
"""

import streamlit as st

from config.constants import TelefoniaCSV
from services.data_manager import DataManager, DataLoadError
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col, sort_by_periodo, filter_by_period,
    last_period_delta, aggregate_by_periodo,
)
from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.filters import anio_selector, trimestre_selector, periodo_range_selector
from components.charts import line_chart, bar_chart


st.set_page_config(page_title="Telefonía Fija · ENACOM", page_icon="☎️", layout="wide")

setup_page()

CATEGORIES = ["Overview", "Accesos", "Penetración", "Ingresos"]

categoria = render_sidebar(CATEGORIES, key="tel_categoria")
st.title("☎️ Telefonía fija")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


# ── Overview ──────────────────────────────────────────────────────────────────

if categoria == "Overview":
    st.header("Resumen general")

    df_acc = load(TelefoniaCSV.FIJA_ACCESOS)
    # df_min = load(TelefoniaCSV.FIJA_MINUTOS)
    df_ing = load(TelefoniaCSV.FIJA_INGRESOS)

    for df, cols in [
        (df_acc, ["anio", "trimestre"]),
        # (df_min, ["anio", "trimestre"]),
        (df_ing, ["anio", "trimestre"]),
    ]:
        DataValidator.validate(df, cols)

    df_acc = sort_by_periodo(add_periodo_col(df_acc))
    # df_min = sort_by_periodo(add_periodo_col(df_min))
    df_ing = sort_by_periodo(add_periodo_col(df_ing))

    acc_col = next((c for c in df_acc.columns if "total" in c or "acceso" in c or "linea" in c),
                   df_acc.columns[-1])
    # min_col = next((c for c in df_min.columns if "minuto" in c or "total" in c),
    #                df_min.columns[-1])
    ing_col = next((c for c in df_ing.columns if "ingreso" in c or "miles" in c),
                   df_ing.columns[-1])

    val_acc, delta_acc = last_period_delta(df_acc, acc_col)
    # val_min, delta_min = last_period_delta(df_min, min_col)
    val_ing, delta_ing = last_period_delta(df_ing, ing_col)

    show_kpis([
        {"label": "Líneas activas",    "value": val_acc, "delta": delta_acc, "format": "{:,.0f}"},
        # {"label": "Minutos de voz",    "value": val_min, "delta": delta_min, "format": "{:,.0f}"},
        {"label": "Ingresos (miles $)","value": val_ing, "delta": delta_ing, "format": "{:,.0f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig = line_chart(df_acc, "periodo", acc_col,
                         title="Líneas activas — evolución", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    # with col2:
    #     fig = line_chart(df_min, "periodo", min_col,
    #                      title="Minutos de voz — evolución", markers=True)
    #     st.plotly_chart(fig, use_container_width=True)


# ── Accesos ───────────────────────────────────────────────────────────────────

elif categoria == "Accesos":
    st.header("Líneas de telefonía fija")

    df = load(TelefoniaCSV.FIJA_ACCESOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))
    anio_desde, anio_hasta = periodo_range_selector(df, key="tel_acc_range")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    acc_col = next((c for c in df.columns if "total" in c or "acceso" in c or "linea" in c),
                   df.columns[-1])
    val, delta = last_period_delta(df_range, acc_col)

    show_kpis([
        {"label": "Líneas activas", "value": val, "delta": delta,
         "format": "{:,.0f}",
         "help": "Líneas de telefonía fija en servicio al cierre del período"},
    ])

    st.divider()
    fig = line_chart(df_range, "periodo", acc_col,
                     title="Evolución de líneas activas", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # Tabla de datos
    with st.expander("Ver datos completos"):
        st.dataframe(df_range, use_container_width=True)


# ── Minutos de voz ────────────────────────────────────────────────────────────

# elif categoria == "Minutos de voz":
    # st.header("Minutos de voz cursados")

    # df = load(TelefoniaCSV.FIJA_MINUTOS)
    # DataValidator.validate(df, ["anio", "trimestre"])

    # df = sort_by_periodo(add_periodo_col(df))
    # anio_desde, anio_hasta = periodo_range_selector(df, key="tel_min_range")
    # df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    # min_col = next((c for c in df.columns if "minuto" in c or "total" in c), df.columns[-1])
    # val, delta = last_period_delta(df_range, min_col)

    # show_kpis([
    #     {"label": "Minutos (miles)", "value": val, "delta": delta, "format": "{:,.0f}"},
    # ])

    # st.divider()

    # # Llamadas locales vs larga distancia si existen las columnas
    # local_col = next((c for c in df.columns if "local" in c), None)
    # ld_col    = next((c for c in df.columns if "larga" in c or "distancia" in c), None)

    # if local_col and ld_col:
    #     from services.transformers import melt_tecnologias
    #     df_long = melt_tecnologias(
    #         df_range, [local_col, ld_col],
    #         var_name="Tipo", value_name="Minutos",
    #     )
    #     fig = line_chart(df_long, "periodo", "Minutos", "Tipo",
    #                      title="Minutos locales vs larga distancia")
    # else:
    #     fig = line_chart(df_range, "periodo", min_col,
    #                      title="Minutos de voz — evolución", markers=True)

    # st.plotly_chart(fig, use_container_width=True)


# ── Ingresos ──────────────────────────────────────────────────────────────────

elif categoria == "Ingresos":
    st.header("Ingresos del sector")

    df = load(TelefoniaCSV.FIJA_INGRESOS)
    DataValidator.validate(df, ["anio", "trimestre"])

    df = sort_by_periodo(add_periodo_col(df))
    anio_desde, anio_hasta = periodo_range_selector(df, key="tel_ing_range")
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