import streamlit as st

from components.kpi_cards import show_kpis
from components.charts import bar_chart

from services.transformers import (
    last_period_delta,
)
from services.kpi_helpers import (
    build_max_kpi,
    build_growth_kpi,
)

from pages.internet.utils import (
    load_dataset,
)


def render():

    # st.header("Ingresos del sector")
    st.caption(
        "Evolución de los ingresos del sector de telecomunicaciones."
    )

    df = load_dataset("ingresos")

    val_actual, delta = last_period_delta(
        df,
        "ingresos",
    )

    kpis = [
        {
            "label": "Ingresos (miles $)",
            "value": val_actual,
            "delta": delta,
            "format": "{:,.0f}",
        },
        build_max_kpi(
            df,
            "ingresos",
            fmt="{:,.0f}",
        ),
        build_growth_kpi(
            df,
            "ingresos",
        ),
    ]

    show_kpis(kpis)

    st.divider()

    fig = bar_chart(
        df,
        x="periodo",
        y="ingresos",
        title="Ingresos por trimestre (miles de pesos)",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    with st.expander("Ver datos completos"):

        st.dataframe(
            df[
                [
                    "anio",
                    "trimestre",
                    "periodo",
                    "ingresos",
                ]
            ],
            width="stretch",
        )
