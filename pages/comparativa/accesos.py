import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.kpi_cards import show_kpis

from pages.comparativa.config import (
    COLOR_SERVICIO,
)

from pages.comparativa.utils import (
    load_dataset,
    indice_base_100,
)

from services.transformers import (
    last_period_delta,
)


def render():

    st.header("Accesos por servicio")

    # ============================================================
    # CARGA
    # ============================================================

    datasets = {
        "Internet fijo": (
            load_dataset("internet_accesos"),
            "total",
        ),
        "Telefonía móvil": (
            load_dataset("movil_accesos"),
            "total",
        ),
        "TV por suscripción": (
            load_dataset("tv_accesos"),
            "total",
        ),
        "Telefonía fija": (
            load_dataset("fija_accesos"),
            "total",
        ),
    }

    # ============================================================
    # KPIs
    # ============================================================

    kpis = []

    for servicio, (df, col) in datasets.items():
        
        valor, delta = last_period_delta(
            df,
            col,
        )

        kpis.append(
            {
                "label": servicio,
                "value": valor,
                "delta": delta,
                "format": "{:,.0f}",
            }
        )

    show_kpis(kpis)

    st.divider()

    # ============================================================
    # MODO VISUALIZACIÓN
    # ============================================================

    modo = st.pills(
        "visualizacion_modo",
        [
            "Valores absolutos",
            "Índice base 100",
        ],
        selection_mode="single",
        default="Valores absolutos",
        key="comp_acc_modo",
        label_visibility="collapsed",
    )

    # ============================================================
    # VALORES ABSOLUTOS
    # ============================================================

    if modo == "Valores absolutos":

        st.info(
            "Telefonía móvil posee una escala significativamente mayor que el resto de los servicios.",
            icon="ℹ️",
        )

        fig = go.Figure()

        for servicio, (df, col) in datasets.items():

            fig.add_trace(
                go.Scatter(
                    x=df["periodo"],
                    y=df[col],
                    mode="lines",
                    name=servicio,
                    line={
                        "color": COLOR_SERVICIO[servicio],
                        "width": 2,
                    },
                )
            )

        periodos = sorted(
            {periodo for df, _ in datasets.values() for periodo in df["periodo"]}
        )

        fig.update_layout(
            title="Accesos por servicio",
            hovermode="x unified",
            xaxis={
                "categoryorder": "array",
                "categoryarray": periodos,
            },
            yaxis={
                "tickformat": ",.0f",
            },
            legend={
                "orientation": "h",
            },
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    # ============================================================
    # ÍNDICE BASE 100
    # ============================================================

    else:

        anios = sorted({int(df["anio"].min()) for df, _ in datasets.values()})

        base_anio = st.select_slider(
            "Año base (=100)",
            options=anios,
            value=max(anios[0], 2014),
            key="comp_acc_base",
        )

        frames = []

        for servicio, (df, col) in datasets.items():
            print(servicio, df.columns.tolist())
            tmp = df[
                [
                    "anio",
                    "periodo",
                    col,
                ]
            ].copy()

            tmp["Servicio"] = servicio

            tmp = tmp.rename(
                columns={
                    col: "valor",
                }
            )

            frames.append(tmp)

        df_long = pd.concat(
            frames,
            ignore_index=True,
        )

        df_idx = indice_base_100(
            df_long,
            base_anio,
        )

        if df_idx.empty:

            st.warning("No hay datos disponibles para el año seleccionado.")
            return

        fig = go.Figure()

        fig.add_hline(
            y=100,
            line_dash="dot",
            line_width=1,
        )

        for servicio in df_idx["Servicio"].unique():

            sub = df_idx[df_idx["Servicio"] == servicio]

            fig.add_trace(
                go.Scatter(
                    x=sub["periodo"],
                    y=sub["indice"],
                    mode="lines",
                    name=servicio,
                    line={
                        "color": COLOR_SERVICIO[servicio],
                        "width": 2,
                    },
                )
            )

        fig.update_layout(
            title=f"Índice base 100 ({base_anio})",
            hovermode="x unified",
            yaxis={
                "title": "Índice",
            },
            legend={
                "orientation": "h",
            },
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

        st.caption(
            f"Base 100 utilizando el primer trimestre disponible de {base_anio}."
        )

        with st.expander("Ver datos"):

            st.dataframe(
                df_idx,
                width="stretch",
                hide_index=True,
            )
