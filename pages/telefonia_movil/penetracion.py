import streamlit as st
import plotly.graph_objects as go

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    line_chart,
    area_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis

from pages.telefonia_movil.utils import load_dataset
from pages.telefonia_movil.config import PENETRACION_KPIS


def render():
    st.header("Penetración de telefonía móvil")

    df = load_dataset("penetracion")

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="mov_pen",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # KPI principal
    kpis = build_kpis(
        PENETRACION_KPIS,
        {"penetracion": df_range},
        default_dataset="penetracion",
    )

    # máximo histórico
    max_val = df_range["accesos_100_hab"].max()

    periodo_max = df_range.loc[
        df_range["accesos_100_hab"].idxmax(),
        "periodo",
    ]

    # variación acumulada
    val_inicio = df_range["accesos_100_hab"].iloc[0]
    val_actual = df_range["accesos_100_hab"].iloc[-1]

    variacion_acum = (
        (val_actual - val_inicio)
        / val_inicio
        * 100
        if val_inicio
        else None
    )

    kpis.extend([
        {
            "label": f"Máximo histórico ({periodo_max})",
            "value": max_val,
            "format": "{:.2f}",
        },
        {
            "label": "Variación acumulada",
            "value": variacion_acum,
            "format": "{:+.1f}%",
            "help": (
                f"Variación desde "
                f"{anio_desde} hasta {anio_hasta}"
            ),
        },
    ])

    show_kpis(kpis)

    st.divider()

    st.caption(
        "Valores superiores a 100 indican que puede haber "
        "más de una línea móvil activa por habitante."
    )

    st.subheader("📊 Evolución de la penetración")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Líneas", "Área", "Barras"],
        horizontal=True,
        key="mov_pen_chart",
    )

    if chart_type == "Líneas":

        fig = line_chart(
            df_range,
            "periodo",
            "accesos_100_hab",
            title="Accesos móviles por cada 100 habitantes",
            markers=False,
        )

        fig.add_hline(
            y=100,
            line_dash="dot",
            line_color="#C6C6C6",
            annotation_text="100 accesos/100 hab.",
            annotation_position="top right",
        )

    elif chart_type == "Área":

        fig = area_chart(
            df_range,
            "periodo",
            "accesos_100_hab",
            title="Accesos móviles por cada 100 habitantes",
        )

        fig.add_hline(
            y=100,
            line_dash="dot",
            line_color="#C6C6C6",
            annotation_text="100 accesos/100 hab.",
            annotation_position="top right",
        )

    else:

        fig = bar_chart(
            df_range,
            "periodo",
            "accesos_100_hab",
            title="Accesos móviles por cada 100 habitantes",
        )

        fig.add_hline(
            y=100,
            line_dash="dot",
            line_color="#C6C6C6",
            annotation_text="100 accesos/100 hab.",
            annotation_position="top right",
        )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range[
                [
                    "anio",
                    "trimestre",
                    "periodo",
                    "accesos_100_hab",
                ]
            ],
            use_container_width=True,
        )