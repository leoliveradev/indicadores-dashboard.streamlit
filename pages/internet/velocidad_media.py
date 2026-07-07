import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import line_chart

from services.transformers import (
    last_period_delta,
)

from services.kpi_helpers import (
    build_max_kpi,
)

from pages.internet.utils import (
    load_dataset,
)


def render():

    st.header("Velocidad media de descarga")

    df = load_dataset("velocidad_media")

    # ── Filtro ───────────────────────────────────────────

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="vel",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # ── KPIs ─────────────────────────────────────────────

    vel_actual, delta_vel = last_period_delta(
        df_range,
        "mbps",
    )

    kpis = [
        {
            "label": "Velocidad actual",
            "value": vel_actual,
            "delta": delta_vel,
            "format": "{:.2f} Mbps",
        },
        build_max_kpi(
            df_range,
            "mbps",
            label="Máximo histórico",
            fmt="{:.2f} Mbps",
        ),
    ]

    # Hace 1 año (4 trimestres)

    if len(df_range) >= 5:

        vel_1y = df_range["mbps"].iloc[-5]

        yoy = (
            (vel_actual - vel_1y)
            / vel_1y
            * 100
        ) if vel_1y else 0

        kpis.extend([
            {
                "label": "Hace 1 año",
                "value": vel_1y,
                "format": "{:.2f} Mbps",
            },
            {
                "label": "Crecimiento interanual",
                "value": yoy,
                "format": "{:+.1f}%",
            },
        ])

    else:

        inicio = df_range["mbps"].iloc[0]

        multiplicador = (
            vel_actual / inicio
        ) if inicio else 0

        kpis.extend([
            {
                "label": "Inicio del período",
                "value": inicio,
                "format": "{:.2f} Mbps",
            },
            {
                "label": "Multiplicador",
                "value": multiplicador,
                "format": "{:.1f}x",
            },
        ])

    show_kpis(kpis)

    st.divider()

    # ── Gráfico principal ────────────────────────────────

    st.subheader("Evolución histórica")

    fig = line_chart(
        df_range,
        x="periodo",
        y="mbps",
        title="Velocidad media de descarga",
        labels={
            "mbps": "Mbps",
            "periodo": "Período",
        },
        markers=True,
        y_tickformat=",.2f",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.divider()

    # ── Gráfico secundario ───────────────────────────────

    st.subheader("Comparación temporal")

    comparacion = {
        "Actual": vel_actual,
    }

    if len(df_range) >= 5:
        comparacion["Hace 1 año"] = vel_1y

    comparacion["Máximo histórico"] = (
        df_range["mbps"].max()
    )

    import pandas as pd

    df_comp = pd.DataFrame(
        {
            "Indicador": comparacion.keys(),
            "Mbps": comparacion.values(),
        }
    )

    from components.charts import bar_chart

    fig_comp = bar_chart(
        df_comp,
        x="Indicador",
        y="Mbps",
        title="Actual vs hace 1 año vs máximo histórico",
    )

    fig_comp.update_yaxes(
        ticksuffix=" Mbps",
        tickformat=",.2f"
    )

    fig_comp.update_traces(
        texttemplate="%{y:.2f} Mbps",
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
                    "mbps",
                ]
            ],
            width="stretch",
        )