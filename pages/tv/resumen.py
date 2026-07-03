import streamlit as st
from components.kpi_cards import show_kpis
from components.charts import area_chart, line_chart, bar_chart

from pages.tv.config import RESUMEN_KPIS
from services.kpi_builder import build_kpis

from pages.tv.utils import load_dataset


def render():
    st.header("Resumen general")

    datasets = {
        "accesos": load_dataset("accesos"),
        "ingresos": load_dataset("ingresos"),
        "penetracion": load_dataset("penetracion"),
    }

    kpis = build_kpis(RESUMEN_KPIS, datasets)
    show_kpis(kpis)

    st.divider()

    # construir totales sin modificar los originales
    df_acc = datasets["accesos"].copy()
    df_acc["total"] = (
        df_acc["tv_suscripcion"] +
        df_acc["tv_satelital"]
    )

    df_ing = datasets["ingresos"].copy()
    df_ing["total"] = (
        df_ing["tv_suscripcion"] +
        df_ing["tv_satelital"]
    )
    
    chart_type = st.radio(
        "Tipo de gráfico",
        ["Área", "Líneas", "Barras"],
        horizontal=True,
    )

    chart_fn = {
        "Área": area_chart,
        "Líneas": line_chart,
        "Barras": bar_chart,
    }[chart_type]


    fig = chart_fn(
        df_acc,
        "periodo",
        "total",
        title="Accesos totales",
    )
    st.plotly_chart(fig, width="stretch")


    fig = chart_fn(
        df_ing,
        "periodo",
        "total",
        title="Ingresos totales (miles $)",
    )
    st.plotly_chart(fig, width="stretch")
