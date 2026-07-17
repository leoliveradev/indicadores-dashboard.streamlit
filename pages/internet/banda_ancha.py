import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    area_chart,
    line_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis
from services.transformers import (
    melt_tecnologias,
)

from pages.internet.utils import (
    load_dataset,
)

from pages.internet.config import (
    BAF_KPIS,
)


def render():

    # st.header("Banda ancha vs Dial-up")
    st.caption(
        "Evolución de los accesos a Internet por banda ancha fija y Dial-up."
    )

    df = load_dataset("baf")

    # ── Filtros ──────────────────────────────────────────

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="baf",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # ── KPIs ─────────────────────────────────────────────

    kpis = build_kpis(
        BAF_KPIS,
        {"baf": df_range},
        default_dataset="baf",
    )

    show_kpis(kpis)

    st.divider()

    # ── Gráfico principal ────────────────────────────────

    df_long = melt_tecnologias(
        df_range,
        [
            "banda_ancha_fija",
            "dial_up",
        ],
        id_col="periodo",
        var_name="Tipo",
        value_name="Accesos",
    )

    df_long["Tipo"] = df_long["Tipo"].map({
        "banda_ancha_fija": "Banda ancha fija",
        "dial_up": "Dial-up",
    })

    tipo_grafico = st.radio(
        "Tipo de gráfico",
        [
            "Área",
            "Líneas",
            "Barras",
        ],
        horizontal=True,
        label_visibility="collapsed",
        key="baf_chart_type",
    )

    if tipo_grafico == "Área":

        fig = area_chart(
            df_long,
            "periodo",
            "Accesos",
            "Tipo",
            title="Evolución banda ancha vs dial-up",
        )

    elif tipo_grafico == "Líneas":

        fig = line_chart(
            df_long,
            "periodo",
            "Accesos",
            "Tipo",
            title="Evolución banda ancha vs dial-up",
        )

    else:

        fig = bar_chart(
            df_long,
            "periodo",
            "Accesos",
            "Tipo",
            title="Banda ancha vs dial-up por trimestre",
            barmode="stack",
        )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.divider()

    # ── Gráfico secundario ───────────────────────────────

    st.subheader(
        "Participación de banda ancha sobre el total"
    )

    df_pct = df_range.copy()

    df_pct["pct_baf"] = (
        df_pct["banda_ancha_fija"]
        / df_pct["total"]
        * 100
    )

    fig_pct = line_chart(
        df_pct,
        x="periodo",
        y="pct_baf",
        title="% Banda ancha sobre total de accesos",
        labels={
            "pct_baf": "%",
        },
        markers=True,
    )

    fig_pct.update_yaxes(
        ticksuffix=" %",
    )

    st.plotly_chart(
        fig_pct,
        width="stretch",
    )

    # ── Tabla ────────────────────────────────────────────

    with st.expander("Ver datos completos"):

        st.dataframe(
            df_range[
                [
                    "anio",
                    "trimestre",
                    "periodo",
                    "banda_ancha_fija",
                    "dial_up",
                    "total",
                ]
            ],
            width="stretch",
        )