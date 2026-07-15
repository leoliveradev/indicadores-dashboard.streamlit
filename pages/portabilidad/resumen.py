import streamlit as st

from components.kpi_cards import show_kpis

from components.charts import (
    line_chart,
    bar_chart,
)

from services.transformers import last_period_delta

from services.kpi_helpers import build_max_kpi

from pages.portabilidad.utils import load_dataset

from services.aggregation_helpers import mensual_a_trimestral, mensual_a_anual


def render():

    st.header("Resumen general")

    df = load_dataset("movil")

    df_t = mensual_a_trimestral(
        df,
        "total",
    )

    df_a = mensual_a_anual(df)

    val_ult, delta_ult = last_period_delta(
        df_t,
        "total",
    )

    kpis = [
        {
            "label": "Portaciones (último trim.)",
            "value": val_ult,
            "delta": delta_ult,
            "format": "{:,.0f}",
        },
        {
            "label": "Total acumulado",
            "value": df["total"].sum(),
            "format": "{:,.0f}",
        },
        {
            "label": "Promedio mensual histórico",
            "value": df["total"].mean(),
            "format": "{:,.0f}",
        },
        build_max_kpi(
            df,
            "total",
            label="Pico histórico",
            period_col="mes",
        ),
    ]

    show_kpis(kpis)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        fig = line_chart(
            df_t,
            "periodo",
            "total",
            title="Portaciones móviles por trimestre",
            markers=False,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    with col2:

        fig = bar_chart(
            df_a,
            "anio",
            "total",
            title="Total anual de portaciones",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )
