import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.kpi_cards import show_kpis

from services.transformers import (
    last_period_delta,
)

from pages.comparativa.config import (
    COLOR_SERVICIO,
)

from pages.comparativa.utils import (
    load_dataset,
)


def render():

    st.header(
        "Penetración comparada entre servicios"
    )

    st.caption(
        "Servicios fijos en accesos cada 100 hogares. "
        "Telefonía móvil en accesos cada 100 habitantes."
    )

    # =====================================================
    # DATASETS
    # =====================================================

    hogares = {
        "Internet fijo": (
            load_dataset("internet_penetracion"),
            "accesos_cada_100_hogares",
        ),
        "TV por suscripción": (
            load_dataset("tv_penetracion"),
            "tv_suscripcion_100_hogares",
        ),
        "Telefonía fija": (
            load_dataset("fija_penetracion"),
            "accesos_100_hog",
        ),
    }

    habitantes = {
        "Telefonía móvil": (
            load_dataset("movil_penetracion"),
            "accesos_100_hab",
        ),
    }

    # =====================================================
    # KPIs
    # =====================================================

    kpis = []

    for servicio, (df, col) in {
        **hogares,
        **habitantes,
    }.items():

        valor, delta = last_period_delta(
            df,
            col,
        )

        unidad = (
            "c/100 hab."
            if servicio == "Telefonía móvil"
            else "c/100 hog."
        )

        kpis.append(
            {
                "label": f"{servicio} ({unidad})",
                "value": valor,
                "delta": delta,
                "format": "{:.2f}",
            }
        )

    show_kpis(kpis)

    st.divider()

    # =====================================================
    # GRÁFICO
    # =====================================================

    fig = go.Figure()

    # hogares

    for servicio, (df, col) in hogares.items():

        fig.add_trace(
            go.Scatter(
                x=df["periodo"],
                y=df[col],
                mode="lines",
                name=f"{servicio} (hog.)",
                yaxis="y",
                line={
                    "color": COLOR_SERVICIO[servicio],
                    "width": 2,
                },
            )
        )

    # habitantes

    for servicio, (df, col) in habitantes.items():

        fig.add_trace(
            go.Scatter(
                x=df["periodo"],
                y=df[col],
                mode="lines",
                name=f"{servicio} (hab.)",
                yaxis="y2",
                line={
                    "color": COLOR_SERVICIO[servicio],
                    "width": 2,
                    "dash": "dot",
                },
            )
        )

    periodos = sorted(
        {
            periodo
            for grupo in (
                list(hogares.values())
                + list(habitantes.values())
            )
            for periodo in grupo[0]["periodo"]
        }
    )

    fig.update_layout(
        title="Penetración por servicio",
        hovermode="x unified",
        xaxis={
            "categoryorder": "array",
            "categoryarray": periodos,
        },
        yaxis={
            "title": "Accesos c/100 hogares",
        },
        yaxis2={
            "title": "Accesos c/100 hab.",
            "overlaying": "y",
            "side": "right",
            "showgrid": False,
        },
        legend={
            "orientation": "h",
        },
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.divider()

    # =====================================================
    # TABLA
    # =====================================================

    rows = []

    for servicio, (df, col) in hogares.items():

        ultimo = (
            df.dropna(subset=[col])
            .iloc[-1]
        )

        rows.append(
            {
                "Servicio": servicio,
                "Período": ultimo["periodo"],
                "Penetración": round(
                    float(ultimo[col]),
                    2,
                ),
                "Unidad": "c/100 hogares",
            }
        )

    for servicio, (df, col) in habitantes.items():

        ultimo = (
            df.dropna(subset=[col])
            .iloc[-1]
        )

        rows.append(
            {
                "Servicio": servicio,
                "Período": ultimo["periodo"],
                "Penetración": round(
                    float(ultimo[col]),
                    2,
                ),
                "Unidad": "c/100 habitantes",
            }
        )

    st.dataframe(
        pd.DataFrame(rows),
        width="stretch",
        hide_index=True,
    )