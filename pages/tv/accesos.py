import streamlit as st
import plotly.graph_objects as go

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import area_chart, line_chart, bar_chart

from services.kpi_builder import build_kpis

from pages.tv.utils import load_dataset
from services.modality_helpers import split_tipo

from pages.tv.config import ACCESOS_KPIS, TV_COLOR_MAP

def render():
    st.header("Accesos a TV por suscripción")

    df = load_dataset("accesos")

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tv_acc")

    df_range = df[
        (df["anio"] >= anio_desde) &
        (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs dinámicos
    datasets = {"accesos": df_range}
    kpis = build_kpis(ACCESOS_KPIS, datasets, default_dataset="accesos")

    show_kpis(kpis)

    st.divider()

    # datos long para charts
    df_long = split_tipo(df_range, "Accesos")

    tab1, tab2, tab3 = st.tabs(["Área", "Líneas", "Barras"])

    with tab1:
        fig = area_chart(
            df_long,
            "periodo", "Accesos", "Tipo",
            title="Accesos — suscripción vs satelital",
            color_map=TV_COLOR_MAP,
        )
        st.plotly_chart(fig, width="stretch")

    with tab2:
        fig = line_chart(
            df_long,
            "periodo", "Accesos", "Tipo",
            title="Evolución de accesos",
            color_map=TV_COLOR_MAP,
        )
        st.plotly_chart(fig, width="stretch")

    with tab3:
        fig = bar_chart(
            df_long,
            "periodo", "Accesos", "Tipo",
            title="Accesos por trimestre",
            barmode="stack",
            color_map=TV_COLOR_MAP,
        )
        st.plotly_chart(fig, width="stretch")

    st.divider()

    # % suscripción (visual destacado)
    st.subheader("% participación de TV suscripción")

    df_pct = df_range.copy()
    total = df_pct["tv_suscripcion"] + df_pct["tv_satelital"]
    df_pct["pct"] = (df_pct["tv_suscripcion"] / total) * 100

    fig = go.Figure(go.Scatter(
        x=df_pct["periodo"],
        y=df_pct["pct"].round(2),
        mode="lines+markers",
        fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
    ))

    fig.update_layout(
        title="% participación de suscripción",
        yaxis={"ticksuffix": "%"},
        hovermode="x unified",
        margin={"t": 40, "b": 40, "l": 40, "r": 20},
    )

    st.plotly_chart(fig, width="stretch")
