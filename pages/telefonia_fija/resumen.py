import streamlit as st
import plotly.express as px

from components.kpi_cards import show_kpis
from components.charts import area_chart, line_chart, bar_chart

from pages.telefonia_fija.utils import (
    load_dataset,
    build_kpis,
    get_last_period_composition,
)
from pages.telefonia_fija.config import (
    RESUMEN_KPIS,
    SEGMENTOS_COLS,
    SEGMENTOS_LABELS,
)


def render():
    st.header("Resumen general")

    datasets = {
        "accesos": load_dataset("accesos"),
        "ingresos": load_dataset("ingresos"),
        "penetracion": load_dataset("penetracion"),
    }

    df_acc = datasets["accesos"]
    df_ing = datasets["ingresos"]
    df_pen = datasets["penetracion"]

    kpis = build_kpis(RESUMEN_KPIS, datasets)
    show_kpis(kpis)

    st.divider()

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Líneas", "Área", "Barras"],
        horizontal=True,
        key="tel_resumen_chart",
    )

    chart_fn = {
        "Líneas": line_chart,
        "Área": area_chart,
        "Barras": bar_chart,
    }[chart_type]

    col1, col2 = st.columns(2)

    with col1:
        fig = chart_fn(
            df_acc,
            "periodo",
            "total",
            title="Accesos totales",
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = chart_fn(
            df_ing,
            "periodo",
            "ingresos",
            title="Ingresos (miles $)",
        )
        st.plotly_chart(fig, use_container_width=True)

