import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter

from pages.tv.config import PENETRACION_KPIS, DUAL_AXIS_CONFIG
from pages.tv.utils import load_dataset, build_kpis
from services.chart_helpers import dual_axis_chart

def render():
    st.header("Penetración")

    df = load_dataset("penetracion")

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tv_pen")

    df_range = df[
        (df["anio"] >= anio_desde) &
        (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs dinámicos
    datasets = {"penetracion": df_range}

    kpis = build_kpis(PENETRACION_KPIS, datasets, default_dataset="penetracion")

    show_kpis(kpis)

    st.divider()

    # gráfico doble eje (hogares vs habitantes)
    st.subheader("Evolución — c/100 hogares vs c/100 habitantes")

    fig = dual_axis_chart(DUAL_AXIS_CONFIG, df_range)

    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # YoY (reusable)
    # st.subheader("Variación interanual — suscripción c/100 hogares")

    # df_yoy = compute_yoy(df_range, "tv_suscripcion_100_hogares")

    # fig_yoy = go.Figure(go.Bar(
    #     x=df_yoy["periodo"],
    #     y=df_yoy["yoy"].round(2),
    #     marker_color=[
    #         "#00B5E5" if v >= 0 else "#E74242"
    #         for v in df_yoy["yoy"]
    #     ],
    # ))

    # fig_yoy.update_layout(
    #     yaxis={"ticksuffix": "%"},
    #     margin={"t": 20, "b": 40, "l": 40, "r": 20},
    #     showlegend=False,
    # )

    # st.plotly_chart(fig_yoy, use_container_width=True)