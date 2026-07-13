import pandas as pd
import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    bar_chart,
)

from services.kpi_builder import build_kpis
from services.chart_helpers import dual_axis_chart

from pages.internet.utils import (
    load_dataset,
)

from pages.internet.config import (
    PENETRACION_KPIS,
)


def render():

    st.header("Penetración")

    # ── Dataset ──────────────────────────────────────────

    df = load_dataset("penetracion")

    # ── Filtro ───────────────────────────────────────────

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="pen",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # ── KPIs base ────────────────────────────────────────

    kpis = build_kpis(
        PENETRACION_KPIS,
        {"pen": df_range},
        default_dataset="pen",
    )

    # ── Crecimientos acumulados ──────────────────────────

    hog_inicio = (
        df_range["accesos_cada_100_hogares"]
        .iloc[0]
    )

    hog_actual = (
        df_range["accesos_cada_100_hogares"]
        .iloc[-1]
    )

    hab_inicio = (
        df_range["accesos_cada_100_habitantes"]
        .iloc[0]
    )

    hab_actual = (
        df_range["accesos_cada_100_habitantes"]
        .iloc[-1]
    )

    crec_hog = (
        (hog_actual - hog_inicio)
        / hog_inicio
        * 100
    ) if hog_inicio else 0

    crec_hab = (
        (hab_actual - hab_inicio)
        / hab_inicio
        * 100
    ) if hab_inicio else 0

    kpis.extend([
        {
            "label": "Crecimiento hogares",
            "value": crec_hog,
            "format": "{:+.1f}%",
            "help": (
                f"Variación acumulada "
                f"{anio_desde}-{anio_hasta}"
            ),
        },
        {
            "label": "Crecimiento habitantes",
            "value": crec_hab,
            "format": "{:+.1f}%",
            "help": (
                f"Variación acumulada "
                f"{anio_desde}-{anio_hasta}"
            ),
        },
    ])

    show_kpis(kpis)

    st.divider()

    # ── Gráfico principal ────────────────────────────────

    st.subheader("Evolución histórica")

    chart_config = {
        "title": "Penetración de Internet fijo",
        "left_axis": {
            "label": "c/100 hogares",
            "series": [
                {
                    "column": "accesos_cada_100_hogares",
                    "name": "c/100 hogares",
                    "color": "#00B5E5",
                }
            ],
        },
        "right_axis": {
            "label": "c/100 habitantes",
            "series": [
                {
                    "column": "accesos_cada_100_habitantes",
                    "name": "c/100 habitantes",
                    "color": "#EEAE42",
                }
            ],
        },
    }

    fig = dual_axis_chart(
        chart_config,
        df_range,
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.divider()

    # ── Gráfico secundario ───────────────────────────────

    st.subheader(
        "Comparación inicio vs fin del período"
    )

    df_compare = pd.DataFrame(
        {
            "Indicador": [
                "Hogares inicio",
                "Hogares actual",
                "Hab. inicio",
                "Hab. actual",
            ],
            "Valor": [
                hog_inicio,
                hog_actual,
                hab_inicio,
                hab_actual,
            ],
        }
    )

    fig_comp = bar_chart(
        df_compare,
        x="Indicador",
        y="Valor",
        title="Inicio vs fin del período seleccionado",
    )

    fig_comp.update_yaxes(
        tickformat=",.2f",
    )

    fig_comp.update_traces(
        texttemplate="%{y:.2f}",
        textposition="outside",
    )

    st.plotly_chart(
        fig_comp,
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
                    "accesos_cada_100_hogares",
                    "accesos_cada_100_habitantes",
                ]
            ],
            width="stretch",
        )