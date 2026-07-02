import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import bar_chart

from services.transformers import filter_by_period
from services.kpi_builder import build_kpis_agg

from pages.telefonia_fija.utils import (
    load_dataset,
    get_top_bottom,
)
from services.chart_helpers import compare_vs_national

from pages.telefonia_fija.config import PENETRACION_PROV_KPIS


def render():
    st.header("Penetración telefonía fija — por provincia")

    df = load_dataset("penetracion_provincia")

    anio, trimestre = render_period_filters(df, key_prefix="tel_prov_pen")

    df_periodo = filter_by_period(df, anio, trimestre)

    if df_periodo.empty:
        st.warning("No hay datos para el período seleccionado")
        return

    # KPIs base (nacional)
    kpis = build_kpis_agg(PENETRACION_PROV_KPIS, df_periodo)

    # top / bottom (hogares)
    kpis.extend(
        get_top_bottom(
            df_periodo,
            "accesos_100_hog",
            label_col="provincia",
            fmt="{:.2f}",
        )
    )

    show_kpis(kpis)

    st.divider()

    # rankings
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ranking — c/100 hogares")

        df_hog = df_periodo[["provincia", "accesos_100_hog"]].sort_values(
            "accesos_100_hog", ascending=True
        )

        fig = bar_chart(
            df_hog,
            x="accesos_100_hog",
            y="provincia",
            title=f"{anio} T{trimestre}",
        )

        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Ranking — c/100 habitantes")

        df_hab = df_periodo[["provincia", "accesos_100_hab"]].sort_values(
            "accesos_100_hab", ascending=True
        )

        fig = bar_chart(
            df_hab,
            x="accesos_100_hab",
            y="provincia",
            title=f"{anio} T{trimestre}",
        )

        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#EEAE42", orientation="h")

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # comparativa vs nacional
    st.subheader("Evolución provincia vs nacional")

    provincias = sorted(df["provincia"].unique())

    prov_sel = st.selectbox(
        "Seleccionar provincia",
        provincias,
        key="tel_prov_pen_evol",
    )

    fig = compare_vs_national(
        df,
        group_col="provincia",
        value_col="accesos_100_hog",
        selected=prov_sel,
        title=f"{prov_sel} vs penetración nacional",
    )


    st.plotly_chart(fig, use_container_width=True)