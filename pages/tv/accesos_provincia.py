import streamlit as st

from pages.tv.config import ACCESOS_PROV_KPIS
from pages.tv.utils import load_dataset, get_top_bottom

from services.transformers import filter_by_period, add_periodo_col, sort_by_periodo
from services.kpi_builder import build_kpis_agg

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import bar_chart, line_chart

def render():
    st.header("Accesos — por provincia")

    df = load_dataset("accesos_provincia")

    anio, trimestre = render_period_filters(df, key_prefix="tv_prov_acc")

    df_periodo = filter_by_period(df, anio, trimestre)

    if df_periodo.empty:
        st.warning("No hay datos para el período seleccionado")
        return

    kpis = build_kpis_agg(ACCESOS_PROV_KPIS, df_periodo)

    kpis.extend(get_top_bottom(df_periodo, "tv_suscripcion"))

    show_kpis(kpis)

    st.divider()

    # ranking
    st.subheader("Ranking por accesos")

    df_rank = df_periodo.sort_values("tv_suscripcion", ascending=True)[
        ["provincia", "tv_suscripcion"]
    ]

    fig = bar_chart(
        df_rank,
        x="tv_suscripcion",
        y="provincia",
        title=f"{anio} T{trimestre}",
    )

    fig.update_layout(
        height=650,
        yaxis={"categoryorder": "total ascending"},
        xaxis={"tickformat": ",.0f"},
    )
    fig.update_traces(marker_color="#00B5E5", orientation="h")

    st.plotly_chart(fig, width="stretch")

    st.divider()

    # comparativa multi-provincia
    st.subheader("Comparar evolución entre provincias")

    provincias = sorted(df["provincia"].unique())

    prov_multi = st.multiselect(
        "Seleccionar provincias",
        provincias,
        default=["Buenos Aires", "CABA", "Córdoba", "Santa Fe"],
        key="tv_prov_multi",
    )

    if prov_multi:
        df_multi = df[df["provincia"].isin(prov_multi)].copy()
        df_multi = sort_by_periodo(add_periodo_col(df_multi))

        fig = line_chart(
            df_multi,
            "periodo",
            "tv_suscripcion",
            "provincia",
            title="Comparativa provincial de accesos",
        )

        st.plotly_chart(fig, width="stretch")