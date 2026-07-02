import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import area_chart, bar_chart

from services.kpi_builder import build_kpis

from pages.tv.utils import load_dataset
from services.modality_helpers import split_tipo

from pages.tv.config import INGRESOS_KPIS, TV_COLOR_MAP


def render():
    st.header("Ingresos del sector")

    df = load_dataset("ingresos")

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tv_ing")

    df_range = df[
        (df["anio"] >= anio_desde) &
        (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs dinámicos
    datasets = {"ingresos": df_range}

    kpis = build_kpis(INGRESOS_KPIS, datasets, default_dataset="ingresos")

    show_kpis(kpis)

    st.divider()

    df_long = split_tipo(df_range, "Ingresos")

    tab1, tab2 = st.tabs(["Área", "Barras"])

    with tab1:
        fig = area_chart(
            df_long,
            "periodo",
            "Ingresos",
            "Tipo",
            title="Ingresos — suscripción vs satelital",
            color_map=TV_COLOR_MAP,
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = bar_chart(
            df_long,
            "periodo",
            "Ingresos",
            "Tipo",
            title="Ingresos por trimestre",
            barmode="stack",
            color_map=TV_COLOR_MAP,
        )
        st.plotly_chart(fig, use_container_width=True)

    # tabla opcional (igual que antes)
    with st.expander("Ver datos completos"):
        df_table = df_range.copy()
        df_table["total"] = (
            df_table["tv_suscripcion"] +
            df_table["tv_satelital"]
        )

        st.dataframe(
            df_table[[
                "anio", "trimestre", "periodo",
                "tv_suscripcion", "tv_satelital", "total"
            ]],
            use_container_width=True,
        )