import pandas as pd
import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import (
    area_chart,
    bar_chart,
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

from pages.internet.config import (
    VELOCIDAD_RANGOS_COLS,
    VELOCIDAD_RANGOS_LABELS,
)


def render():

    st.header(
        "Rangos de velocidad — por provincia"
    )

    # ── Dataset ──────────────────────────────────────────

    df = load_dataset(
        "velocidad_rangos_provincia"
    )

    # ── Filtro ───────────────────────────────────────────

    anio, trimestre = render_period_filters(
        df,
        key_prefix="prov_vrang",
    )

    df_periodo = filter_by_period(
        df,
        anio,
        trimestre,
    ).copy()

    df_periodo["pct_alta_vel"] = (
        df_periodo["mayor_30mbps"]
        / df_periodo["total"]
        * 100
    ).round(2)

    # ── KPIs ─────────────────────────────────────────────

    top = (
        df_periodo
        .nlargest(1, "pct_alta_vel")
        .iloc[0]
    )

    low = (
        df_periodo
        .nsmallest(1, "pct_alta_vel")
        .iloc[0]
    )

    show_kpis([
        {
            "label": f"Mayor % +30 Mbps ({top['provincia']})",
            "value": top["pct_alta_vel"],
            "format": "{:.1f}%",
        },
        {
            "label": f"Menor % +30 Mbps ({low['provincia']})",
            "value": low["pct_alta_vel"],
            "format": "{:.1f}%",
        },
        {
            "label": "Promedio nacional +30 Mbps",
            "value": df_periodo["pct_alta_vel"].mean(),
            "format": "{:.1f}%",
        },
        {
            "label": "Total accesos",
            "value": df_periodo["total"].sum(),
            "format": "{:,.0f}",
        },
    ])

    st.divider()

    # ── Rankings ─────────────────────────────────────────

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "% accesos +30 Mbps"
        )

        fig = province_ranking_chart(
            df_periodo,
            value_col="pct_alta_vel",
            title=f"% accesos >30 Mbps — {anio} T{trimestre}",
            tickformat=",.1f",
        )

        fig.update_xaxes(
            ticksuffix="%"
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    with col2:

        st.subheader(
            "Distribución por rangos"
        )

        df_long = melt_tecnologias(
            df_periodo,
            VELOCIDAD_RANGOS_COLS,
            id_col="provincia",
            var_name="Rango",
            value_name="Accesos",
        )

        df_long["Rango"] = (
            df_long["Rango"]
            .map(VELOCIDAD_RANGOS_LABELS)
        )

        fig = bar_chart(
            df_long,
            x="Accesos",
            y="provincia",
            color="Rango",
            barmode="stack",
            title=f"Distribución por rango — {anio} T{trimestre}",
        )

        fig.update_layout(
            height=650,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    st.divider()

    # ── Evolución provincia ──────────────────────────────

    st.subheader(
        "Evolución histórica por provincia"
    )

    provincias = sorted(
        df["provincia"].unique()
    )

    provincia = st.selectbox(
        "Provincia",
        provincias,
        key="internet_rangos_prov",
    )

    df_prov = (
        df[
            df["provincia"] == provincia
        ]
        .copy()
    )

    df_long = melt_tecnologias(
        df_prov,
        VELOCIDAD_RANGOS_COLS,
        id_col="periodo",
        var_name="Rango",
        value_name="Accesos",
    )

    df_long["Rango"] = (
        df_long["Rango"]
        .map(VELOCIDAD_RANGOS_LABELS)
    )

    orden_rangos = list(
        VELOCIDAD_RANGOS_LABELS.values()
    )

    df_long["Rango"] = pd.Categorical(
        df_long["Rango"],
        categories=orden_rangos,
        ordered=True,
    )

    df_long = df_long.sort_values(
        ["periodo", "Rango"]
    )

    tipo = st.radio(
        "Tipo de gráfico",
        [
            "Área",
            "Barras",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="rangos_prov_chart",
    )

    if tipo == "Área":

        fig = area_chart(
            df_long,
            "periodo",
            "Accesos",
            "Rango",
            title=f"{provincia} — evolución por rangos",
        )

    else:

        fig = bar_chart(
            df_long,
            "periodo",
            "Accesos",
            "Rango",
            title=f"{provincia} — distribución por rangos",
            barmode="stack",
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