import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import bar_chart

from services.transformers import filter_by_period
from services.kpi_builder import build_kpis_agg
from services.chart_helpers import compare_vs_national

from pages.tv.utils import load_dataset, get_top_bottom

from pages.tv.config import PENETRACION_PROV_KPIS


def render():
    st.header("Penetración TV suscripción — por provincia")

    df = load_dataset("penetracion_provincia")

    df = df.rename(columns={
        "tv_suscripcion_100habitantes": "tv_suscripcion_100_habitantes",
        "tv_suscripcion_100hogares": "tv_suscripcion_100_hogares",
    })

    anio, trimestre = render_period_filters(df, key_prefix="tv_prov_pen")

    df_periodo = filter_by_period(df, anio, trimestre)

    if df_periodo.empty:
        st.warning("No hay datos para el período seleccionado")
        return

    # KPIs base (promedios)
    kpis = build_kpis_agg(PENETRACION_PROV_KPIS, df_periodo)

    # top/bottom
    kpis.extend(
        get_top_bottom(
            df_periodo,
            "tv_suscripcion_100_hogares",
            label_col="provincia",
            fmt="{:.2f}"
        )
    )

    show_kpis(kpis)

    st.divider()

    # rankings
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ranking — c/100 hogares")

        df_hog = df_periodo.sort_values(
            "tv_suscripcion_100_hogares", ascending=True
        )[["provincia", "tv_suscripcion_100_hogares"]]

        fig = bar_chart(
            df_hog,
            x="tv_suscripcion_100_hogares",
            y="provincia",
            title=f"{anio} T{trimestre}",
        )

        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")

        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Ranking — c/100 habitantes")

        df_hab = df_periodo.sort_values(
            "tv_suscripcion_100_habitantes", ascending=True
        )[["provincia", "tv_suscripcion_100_habitantes"]]

        fig = bar_chart(
            df_hab,
            x="tv_suscripcion_100_habitantes",
            y="provincia",
            title=f"{anio} T{trimestre}",
        )

        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#EEAE42", orientation="h")

        st.plotly_chart(fig, width="stretch")

    st.divider()

    # comparativa vs promedio nacional
    st.subheader("Evolución provincia vs promedio nacional")

    provincias = sorted(df["provincia"].unique())

    prov_sel = st.selectbox(
        "Seleccionar provincia",
        provincias,
        key="tv_prov_pen_evol",
    )

    # serie provincia
    fig = compare_vs_national(
        df,
        "provincia",
        "tv_suscripcion_100_hogares",
        prov_sel,
        title="Provincia vs promedio nacional",
        y_suffix="%"
    )

    st.plotly_chart(fig, width="stretch")