import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import (
    line_chart,
)

from services.chart_helpers import (
    province_ranking_chart,
)

from services.transformers import (
    filter_by_period,
)

from pages.internet.utils import (
    load_dataset,
)


def render():

    st.header(
        "Velocidad media de descarga — por provincia"
    )

    # ── Dataset ──────────────────────────────────────────

    df = load_dataset(
        "velocidad_media_provincia"
    )

    # ── Filtro ───────────────────────────────────────────

    anio, trimestre = render_period_filters(
        df,
        key_prefix="prov_vel",
    )

    df_periodo = filter_by_period(
        df,
        anio,
        trimestre,
    ).copy()

    # ── KPIs ─────────────────────────────────────────────

    top3 = (
        df_periodo
        .nlargest(3, "mbps")
        [["provincia", "mbps"]]
        .values
    )

    low = (
        df_periodo
        .nsmallest(1, "mbps")
        .iloc[0]
    )

    show_kpis([
        {
            "label": f"1° {top3[0][0]}",
            "value": top3[0][1],
            "format": "{:.1f} Mbps",
        },
        {
            "label": f"2° {top3[1][0]}",
            "value": top3[1][1],
            "format": "{:.1f} Mbps",
        },
        {
            "label": f"3° {top3[2][0]}",
            "value": top3[2][1],
            "format": "{:.1f} Mbps",
        },
        {
            "label": f"Menor ({low['provincia']})",
            "value": low["mbps"],
            "format": "{:.1f} Mbps",
        },
    ])

    st.divider()

    # ── Ranking ──────────────────────────────────────────

    st.subheader(
        f"Ranking — {anio} T{trimestre}"
    )

    fig_rank = province_ranking_chart(
        df_periodo,
        value_col="mbps",
        title="Velocidad media por provincia",
        tickformat=",.1f",
    )

    fig_rank.update_xaxes(
        ticksuffix=" Mbps"
    )

    st.plotly_chart(
        fig_rank,
        width="stretch",
    )

    st.divider()

    # ── Evolución comparativa ─────────────────────────────

    st.subheader(
        "Comparar evolución entre provincias"
    )

    provincias = sorted(
        df["provincia"].unique()
    )

    defaults = [
        p for p in [
            "Buenos Aires",
            "CABA",
            "Córdoba",
            "Santa Fe",
        ]
        if p in provincias
    ]

    provincias_sel = st.multiselect(
        "Seleccionar provincias",
        provincias,
        default=defaults,
        key="internet_vmd_prov_multi",
    )

    if provincias_sel:

        df_multi = (
            df[
                df["provincia"]
                .isin(provincias_sel)
            ]
            .copy()
        )

        fig = line_chart(
            df_multi,
            x="periodo",
            y="mbps",
            color="provincia",
            title="Velocidad media — comparativa provincial",
            labels={
                "mbps": "Mbps",
            },
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    # ── Tabla ────────────────────────────────────────────

    with st.expander(
        "Ver datos completos"
    ):

        st.dataframe(
            df_periodo,
            width="stretch",
        )