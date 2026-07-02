import streamlit as st
import plotly.graph_objects as go

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    line_chart,
    area_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis

from pages.telefonia_movil.utils import load_dataset
from services.modality_helpers import melt_modalidad

from pages.telefonia_movil.config import (
    ACCESOS_KPIS,
    MODALIDAD_COLOR_MAP,
)


def render():
    st.header("Líneas móviles activas")

    df = load_dataset("accesos")

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="mov_acc",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs
    kpis = build_kpis(
        ACCESOS_KPIS,
        {"accesos": df_range},
        default_dataset="accesos",
    )

    show_kpis(kpis)

    st.divider()

    # datos para gráficos
    df_long = melt_modalidad(
        df_range,
        "Líneas",
    )

    # selector único
    st.subheader("📊 Evolución por modalidad")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Área", "Líneas", "Barras"],
        horizontal=True,
        key="mov_acc_chart",
    )

    chart_fn = {
        "Área": area_chart,
        "Líneas": line_chart,
        "Barras": bar_chart,
    }[chart_type]

    fig = chart_fn(
        df_long,
        "periodo",
        "Líneas",
        "Modalidad",
        title="Líneas móviles — pospago vs prepago",
        color_map=MODALIDAD_COLOR_MAP,
    )

    if chart_type == "Barras":
        fig.update_layout(barmode="stack")

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    # participación pospago
    st.subheader("% líneas pospago sobre el total")

    df_pct = df_range.copy()

    total = (
        df_pct["pospago"]
        + df_pct["prepago"]
    )

    df_pct["pct_pospago"] = (
        df_pct["pospago"] / total * 100
    ).round(2)

    fig_pct = go.Figure(
        go.Scatter(
            x=df_pct["periodo"],
            y=df_pct["pct_pospago"],
            mode="lines+markers",
            fill="tozeroy",
            line={
                "color": "#00B5E5",
                "width": 2,
            },
            fillcolor="rgba(0,181,229,0.08)",
            marker={"size": 4},
        )
    )

    fig_pct.update_layout(
        title="% líneas pospago sobre el total",
        yaxis={"ticksuffix": "%"},
        hovermode="x unified",
        margin={
            "t": 40,
            "b": 40,
            "l": 40,
            "r": 20,
        },
    )

    st.plotly_chart(
        fig_pct,
        use_container_width=True,
    )

    with st.expander("Ver datos"):
        st.dataframe(
            df_range,
            use_container_width=True,
        )