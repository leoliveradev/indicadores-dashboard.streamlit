import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import (
    area_chart,
)

from services.chart_helpers import (
    province_ranking_chart,
)

from services.transformers import (
    filter_by_period,
    melt_tecnologias,
)

from pages.internet.utils import (
    load_dataset,
)


def render():

    st.header(
        "Banda ancha fija vs Dial-up — por provincia"
    )

    # ── Dataset ──────────────────────────────────────────

    df = load_dataset(
        "baf_provincia"
    )

    # ── Filtro ───────────────────────────────────────────

    anio, trimestre = render_period_filters(
        df,
        key_prefix="prov_baf",
    )

    df_periodo = filter_by_period(
        df,
        anio,
        trimestre,
    ).copy()

    df_periodo["pct_banda_ancha"] = (
        df_periodo["banda_ancha_fija"]
        / df_periodo["total"]
        * 100
    ).round(2)

    # ── KPIs ─────────────────────────────────────────────

    top_baf = (
        df_periodo
        .nlargest(1, "pct_banda_ancha")
        .iloc[0]
    )

    low_baf = (
        df_periodo
        .nsmallest(1, "pct_banda_ancha")
        .iloc[0]
    )

    show_kpis([
        {
            "label": "Banda ancha total",
            "value": df_periodo["banda_ancha_fija"].sum(),
            "format": "{:,.0f}",
        },
        {
            "label": "Dial-up total",
            "value": df_periodo["dial_up"].sum(),
            "format": "{:,.0f}",
        },
        {
            "label": f"Mayor % BA ({top_baf['provincia']})",
            "value": top_baf["pct_banda_ancha"],
            "format": "{:.1f}%",
        },
        {
            "label": f"Menor % BA ({low_baf['provincia']})",
            "value": low_baf["pct_banda_ancha"],
            "format": "{:.1f}%",
        },
    ])

    st.divider()

    # ── Rankings ─────────────────────────────────────────

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "Accesos banda ancha"
        )

        fig = province_ranking_chart(
            df_periodo,
            value_col="banda_ancha_fija",
            title=f"Accesos banda ancha — {anio} T{trimestre}",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    with col2:

        st.subheader(
            "% Banda ancha sobre total"
        )

        fig = province_ranking_chart(
            df_periodo,
            value_col="pct_banda_ancha",
            title=f"Proporción banda ancha — {anio} T{trimestre}",
            tickformat=",.1f",
        )

        fig.update_xaxes(
            ticksuffix="%"
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    st.divider()

    # ── Evolución histórica ──────────────────────────────

    st.subheader(
        "Evolución banda ancha vs dial-up"
    )

    provincias = sorted(
        df["provincia"].unique()
    )

    provincia = st.selectbox(
        "Provincia",
        provincias,
        key="internet_baf_prov",
    )

    df_prov = (
        df[
            df["provincia"] == provincia
        ]
        .copy()
    )

    df_long = melt_tecnologias(
        df_prov,
        [
            "banda_ancha_fija",
            "dial_up",
        ],
        id_col="periodo",
        var_name="Tipo",
        value_name="Accesos",
    )

    df_long["Tipo"] = df_long["Tipo"].map(
        {
            "banda_ancha_fija": "Banda ancha fija",
            "dial_up": "Dial-up",
        }
    )

    fig = area_chart(
        df_long,
        "periodo",
        "Accesos",
        "Tipo",
        title=f"{provincia} — evolución banda ancha vs dial-up",
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