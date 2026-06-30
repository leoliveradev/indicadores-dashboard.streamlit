import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import bar_chart, line_chart

from services.transformers import filter_by_period, add_periodo_col, sort_by_periodo

from pages.telefonia_fija.utils import (
    load_dataset,
    build_kpis_agg,
    get_top_bottom,
    melt_segmentos,
)
from pages.telefonia_fija.config import (
    ACCESOS_PROV_KPIS,
    SEGMENTOS_COLS,
    SEGMENTOS_LABELS,
)


def render():
    st.header("Accesos telefonía fija — por provincia")

    df = load_dataset("accesos_provincia")

    df = df.rename(columns={"hogres": "hogares"})

    anio, trimestre = render_period_filters(df, key_prefix="tel_prov_acc")

    df_periodo = filter_by_period(df, anio, trimestre)

    if df_periodo.empty:
        st.warning("No hay datos para el período seleccionado")
        return

    # KPIs base (agregados)
    kpis = build_kpis_agg(ACCESOS_PROV_KPIS, df_periodo)

    kpis.extend(
        get_top_bottom(df_periodo, "total", label_col="provincia")
    )

    show_kpis(kpis)

    st.divider()

    col1, col2 = st.columns(2)

    # ranking total
    with col1:
        st.subheader("Ranking por accesos totales")

        df_rank = df_periodo[["provincia", "total"]].sort_values(
            "total", ascending=True
        )

        fig = bar_chart(
            df_rank,
            x="total",
            y="provincia",
            title=f"{anio} T{trimestre}",
        )

        fig.update_layout(
            height=650,
            yaxis={"categoryorder": "total ascending"},
            xaxis={"tickformat": ",.0f"},
        )
        fig.update_traces(marker_color="#00B5E5", orientation="h")

        st.plotly_chart(fig, use_container_width=True)

    # composición por segmento
    with col2:
        st.subheader("Composición por segmento")

        df_long = melt_segmentos(
            df_periodo,
            SEGMENTOS_COLS,
            SEGMENTOS_LABELS,
            id_col="provincia"
        )

        df_long = df_long.merge(
            df_periodo[["provincia", "total"]],
            on="provincia"
        ).sort_values("total", ascending=False)

        fig = bar_chart(
            df_long,
            x="Accesos",
            y="provincia",
            color="Segmento",
            title=f"{anio} T{trimestre}",
            barmode="stack",
        )

        fig.update_layout(
            height=650,
            yaxis={"categoryorder": "total ascending"},
            xaxis={"tickformat": ",.0f"},
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # comparativa multi-provincia
    st.subheader("Comparar evolución entre provincias")

    provincias = sorted(df["provincia"].unique())

    prov_multi = st.multiselect(
        "Seleccionar provincias",
        provincias,
        default=["Buenos Aires", "CABA", "Córdoba", "Santa Fe"],
        key="tel_prov_multi",
    )

    if prov_multi:
        df_multi = df[df["provincia"].isin(prov_multi)].copy()
        df_multi = sort_by_periodo(add_periodo_col(df_multi))

        fig = line_chart(
            df_multi,
            "periodo",
            "total",
            "provincia",
            title="Accesos totales — comparativa provincial",
            labels={"total": "Accesos"},
        )

        st.plotly_chart(fig, use_container_width=True)
