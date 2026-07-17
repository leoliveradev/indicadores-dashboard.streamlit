import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import (
    bar_chart,
    line_chart,
)

from services.kpi_builder import build_kpis_agg

from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
    filter_by_period,
)

from pages.mercado_postal.utils import (
    load_dataset,
    limpiar_provincias,
)

from pages.mercado_postal.config import (
    PROVINCIA_KPIS,
)


def render():

    st.header(
        "Facturación y producción — por provincia"
    )

    st.caption(
        "Datos disponibles desde 2015. "
        "CABA y GBA aparecen agrupados en la fuente original."
    )

    # Dataset
    df = load_dataset("provincia")

    df = limpiar_provincias(df)

    df = sort_by_periodo(
        add_periodo_col(df)
    )

    # Filtros
    anio, trimestre = render_period_filters(
        df,
        key_prefix="postal_prov",
    )

    df_periodo = filter_by_period(
        df,
        anio,
        trimestre,
    ).copy()

    # KPIs base
    kpis = build_kpis_agg(
        PROVINCIA_KPIS,
        df_periodo,
    )

    top_fact = (
        df_periodo
        .loc[df_periodo["pesos"].idxmax()]
    )

    top_prod = (
        df_periodo
        .loc[df_periodo["unidades"].idxmax()]
    )

    kpis.extend([
        {
            "label": f"Mayor facturación ({top_fact['provincia']})",
            "value": top_fact["pesos"],
            "format": "{:,.0f}",
        },
        {
            "label": f"Mayor producción ({top_prod['provincia']})",
            "value": top_prod["unidades"],
            "format": "{:,.0f}",
        },
    ])

    show_kpis(kpis)

    st.divider()

    col1, col2 = st.columns(2)

    # Ranking facturación
    with col1:

        st.subheader("Ranking — facturación")

        df_rank = (
            df_periodo[
                ["provincia", "pesos"]
            ]
            .sort_values(
                "pesos",
                ascending=True,
            )
        )

        fig = bar_chart(
            df_rank,
            x="pesos",
            y="provincia",
            title=f"{anio} T{trimestre}",
        )

        fig.update_layout(
            height=700,
            yaxis={
                "categoryorder": "total ascending",
            },
            xaxis={
                "tickformat": ",.0f",
            },
        )

        fig.update_traces(
            marker_color="#00B5E5",
            orientation="h",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    # Ranking producción
    with col2:

        st.subheader("Ranking — producción")

        df_rank = (
            df_periodo[
                ["provincia", "unidades"]
            ]
            .sort_values(
                "unidades",
                ascending=True,
            )
        )

        fig = bar_chart(
            df_rank,
            x="unidades",
            y="provincia",
            title=f"{anio} T{trimestre}",
        )

        fig.update_layout(
            height=700,
            yaxis={
                "categoryorder": "total ascending",
            },
            xaxis={
                "tickformat": ",.0f",
            },
        )

        fig.update_traces(
            marker_color="#EEAE42",
            orientation="h",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    st.divider()

    st.subheader(
        "Comparar evolución entre provincias"
    )

    metric = st.radio(
        "Métrica",
        [
            "Facturación ($)",
            "Producción (unidades)",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="postal_metric",
    )

    value_col = (
        "pesos"
        if metric == "Facturación ($)"
        else "unidades"
    )

    provincias = sorted(
        df["provincia"].unique()
    )

    default_provincias = [
        p for p in [
            "CABA y GBA",
            "Buenos Aires",
            "Córdoba",
            "Santa Fe",
        ]
        if p in provincias
    ]

    seleccion = st.multiselect(
        "Seleccionar provincias",
        provincias,
        default=default_provincias,
        key="postal_prov_multi",
    )

    if seleccion:

        df_multi = sort_by_periodo(
            add_periodo_col(
                df[
                    df["provincia"]
                    .isin(seleccion)
                ].copy()
            )
        )

        fig = line_chart(
            df_multi,
            "periodo",
            value_col,
            "provincia",
            title=f"{metric} — comparativa provincial",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )