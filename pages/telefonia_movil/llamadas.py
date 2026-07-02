import streamlit as st
import plotly.graph_objects as go

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    area_chart,
    line_chart,
    bar_chart,
)

from services.chart_helpers import participation_chart
from services.kpi_builder import build_kpis

from services.modality_helpers import melt_modalidad

from pages.telefonia_movil.utils import load_dataset

from pages.telefonia_movil.config import (
    LLAMADAS_KPIS,
    MODALIDAD_COLOR_MAP,
)


def render():
    st.header("Llamadas cursadas")

    # dataset
    df = load_dataset("llamadas")

    # filtro
    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="mov_llam",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs
    kpis = build_kpis(
        LLAMADAS_KPIS,
        {"llamadas": df_range},
        default_dataset="llamadas",
    )

    show_kpis(kpis)

    st.divider()

    # datos gráficos
    df_long = melt_modalidad(
        df_range,
        "Llamadas",
    )

    st.subheader("📊 Evolución por modalidad")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Área", "Líneas", "Barras"],
        horizontal=True,
        key="mov_llam_chart",
    )

    chart_fn = {
        "Área": area_chart,
        "Líneas": line_chart,
        "Barras": bar_chart,
    }[chart_type]

    fig = chart_fn(
        df_long,
        "periodo",
        "Llamadas",
        "Modalidad",
        title="Llamadas — pospago vs prepago",
        color_map=MODALIDAD_COLOR_MAP,
    )

    if chart_type == "Barras":
        fig.update_layout(barmode="stack")

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("% llamadas pospago sobre el total")

    df_pct = df_range.copy()

    df_pct["pct_pospago"] = (
        df_pct["pospago"]
        / df_pct["total"]
        * 100
    ).round(2)

    fig_pct = participation_chart(
        df_range,
        numerator="pospago",
        denominator="total",
        title="% llamadas pospago sobre el total",
    )

    st.plotly_chart(
        fig_pct,
        use_container_width=True,
    )

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range,
            use_container_width=True,
        )