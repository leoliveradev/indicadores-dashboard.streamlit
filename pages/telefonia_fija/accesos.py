import streamlit as st
import plotly.graph_objects as go

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import area_chart, line_chart, bar_chart

from services.kpi_builder import build_kpis

from pages.telefonia_fija.utils import (
    load_dataset,
    melt_segmentos,
)
from pages.telefonia_fija.config import (
    ACCESOS_KPIS,
    SEGMENTOS_COLS,
    SEGMENTOS_LABELS,
)


def render():
    st.header("Accesos de telefonía fija")

    df = load_dataset("accesos")

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tel_acc")

    df_range = df[
        (df["anio"] >= anio_desde) &
        (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs dinámicos
    datasets = {"accesos": df_range}

    kpis = build_kpis(
        ACCESOS_KPIS,
        datasets,
        default_dataset="accesos"
    )

    show_kpis(kpis)

    st.divider()

    # transformar datos (reutilizable)
    df_long = melt_segmentos(
        df_range,
        SEGMENTOS_COLS,
        SEGMENTOS_LABELS
    )

    # selector único de gráfico (UX mejorada)
    st.subheader("📊 Evolución de accesos")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Área", "Líneas", "Barras"],
        horizontal=True,
        key="tel_acc_chart",
    )

    chart_fn = {
        "Área": area_chart,
        "Líneas": line_chart,
        "Barras": bar_chart,
    }[chart_type]

    # gráfico dinámico
    fig = chart_fn(
        df_long,
        "periodo",
        "Accesos",
        "Segmento",
        title="Accesos por segmento — evolución",
    )

    if chart_type == "Barras":
        fig.update_layout(barmode="stack")

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # participación hogares (KPI analítico)
    st.subheader("% participación hogares sobre el total")

    df_pct = df_range.copy()
    total = (
        df_pct["hogares"] +
        df_pct["comercial"] +
        df_pct["gobierno"] +
        df_pct["otros"]
    )

    df_pct["pct_hogares"] = (df_pct["hogares"] / total * 100).round(2)

    fig_pct = go.Figure(go.Scatter(
        x=df_pct["periodo"],
        y=df_pct["pct_hogares"],
        mode="lines+markers",
        fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
        marker={"size": 4},
    ))

    fig_pct.update_layout(
        title="% accesos hogares sobre el total",
        yaxis={"ticksuffix": "%"},
        hovermode="x unified",
        margin={"t": 40, "b": 40, "l": 40, "r": 20},
    )

    st.plotly_chart(fig_pct, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(df_range, use_container_width=True)