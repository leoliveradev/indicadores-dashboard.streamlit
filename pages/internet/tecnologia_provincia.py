import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import (
    line_chart,
    area_chart,
    bar_chart,
)

from services.transformers import (
    filter_by_period,
    melt_tecnologias,
)

from services.chart_helpers import (
    province_ranking_chart,
)

from pages.internet.utils import (
    load_dataset,
)

from pages.internet.config import (
    TECNOLOGIAS_COLS,
    TECNOLOGIAS_LABELS,
)


def render():

    st.header("Accesos por tecnología — por provincia")

    df = load_dataset(
        "tecnologias_provincia"
    )

    # ── Filtro ───────────────────────────────────────────

    anio, trimestre = render_period_filters(
        df,
        key_prefix="prov_tec",
    )

    df_periodo = filter_by_period(
        df,
        anio,
        trimestre,
    ).copy()

    # ── KPIs ─────────────────────────────────────────────

    show_kpis([
        {
            "label": "Total nacional",
            "value": df_periodo["total"].sum(),
            "format": "{:,.0f}",
        },
        {
            "label": "Fibra óptica",
            "value": df_periodo["fibra_optica"].sum(),
            "format": "{:,.0f}",
        },
        {
            "label": "Cablemodem",
            "value": df_periodo["cablemodem"].sum(),
            "format": "{:,.0f}",
        },
        {
            "label": "ADSL",
            "value": df_periodo["adsl"].sum(),
            "format": "{:,.0f}",
        },
    ])

    st.divider()

    # ── Ranking + composición ────────────────────────────

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            f"Ranking — {anio} T{trimestre}"
        )

        fig_rank = province_ranking_chart(
            df_periodo,
            value_col="total",
            title="Accesos totales por provincia",
        )

        st.plotly_chart(
            fig_rank,
            width="stretch",
        )

    with col2:

        st.subheader(
            "Composición por tecnología"
        )

        df_long = melt_tecnologias(
            df_periodo,
            TECNOLOGIAS_COLS,
            id_col="provincia",
            var_name="Tecnología",
            value_name="Accesos",
        )

        df_long["Tecnología"] = (
            df_long["Tecnología"]
            .map(TECNOLOGIAS_LABELS)
        )

        fig_comp = bar_chart(
            df_long,
            x="Accesos",
            y="provincia",
            color="Tecnología",
            barmode="stack",
            title="Distribución tecnológica",
        )

        fig_comp.update_layout(
            height=650,
        )

        st.plotly_chart(
            fig_comp,
            width="stretch",
        )

    st.divider()

    # ── Evolución histórica ──────────────────────────────

    st.subheader(
        "Evolución histórica por provincia"
    )

    provincia = st.selectbox(
        "Provincia",
        sorted(df["provincia"].unique()),
        key="internet_tec_prov",
    )

    df_prov = (
        df[
            df["provincia"] == provincia
        ]
        .copy()
    )

    df_long_prov = melt_tecnologias(
        df_prov,
        TECNOLOGIAS_COLS,
    )

    df_long_prov["Tecnología"] = (
        df_long_prov["Tecnología"]
        .map(TECNOLOGIAS_LABELS)
    )

    chart_type = st.radio(
        "Tipo de gráfico",
        [
            "Líneas",
            "Área",
        ],
        horizontal=True,
        key="internet_tec_prov_chart",
    )

    if chart_type == "Líneas":

        fig = line_chart(
            df_long_prov,
            "periodo",
            "Accesos",
            "Tecnología",
            title=f"{provincia} — evolución tecnológica",
        )

    else:

        fig = area_chart(
            df_long_prov,
            "periodo",
            "Accesos",
            "Tecnología",
            title=f"{provincia} — composición en el tiempo",
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