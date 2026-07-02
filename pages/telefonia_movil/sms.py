import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    line_chart,
    bar_chart,
    area_chart,
)

from services.kpi_builder import build_kpis

from pages.telefonia_movil.utils import load_dataset
from pages.telefonia_movil.config import SMS_KPIS


def render():
    st.header("Mensajes de texto (SMS)")

    df = load_dataset("sms")

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="mov_sms",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs
    kpis = build_kpis(
        SMS_KPIS,
        {"sms": df_range},
        default_dataset="sms",
    )

    show_kpis(kpis)

    st.divider()

    st.subheader("📊 Evolución de SMS")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Líneas", "Barras", "Área"],
        horizontal=True,
        key="mov_sms_chart",
    )

    chart_fn = {
        "Líneas": line_chart,
        "Barras": bar_chart,
        "Área": area_chart,
    }[chart_type]

    fig = chart_fn(
        df_range,
        "periodo",
        "total",
        title="SMS enviados (miles)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range,
            use_container_width=True,
        )