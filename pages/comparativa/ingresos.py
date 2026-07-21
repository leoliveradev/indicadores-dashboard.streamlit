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

    st.header("Ingresos por servicio")

    st.caption(
        "Comparación histórica de ingresos entre los distintos servicios TIC y postales."
    )

    # =====================================================
    # DATASETS
    # =====================================================

    datasets = {
        "Internet fijo": (
            load_dataset("internet_ingresos"),
            "ingresos",
        ),
        "Telefonía móvil": (
            load_dataset("movil_ingresos"),
            "ingresos",
        ),
        "TV por suscripción": (
            load_dataset("tv_ingresos"),
            "ingresos",
        ),
        "Telefonía fija": (
            load_dataset("fija_ingresos"),
            "ingresos",
        ),
        "Mercado postal": (
            load_dataset("postal_facturacion"),
            "ingresos",
        ),
    }

    # =====================================================
    # KPIS
    # =====================================================

    kpis = []

    for servicio, (df, col) in datasets.items():
        if col not in df.columns:
            st.error(
                f"{servicio}: falta columna {col}"
            )

            st.write(df.columns.tolist())
        
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

    st.info(
        "Las magnitudes pueden diferir significativamente entre servicios. "
        "Utilice la leyenda para mostrar u ocultar series.",
        icon="ℹ️",
    )

    # =====================================================
    # GRÁFICO
    # =====================================================

    fig = go.Figure()

    for servicio, (df, col) in datasets.items():

        fig.add_trace(
            go.Scatter(
                x=df["periodo"],
                y=df[col],
                mode="lines",
                name=servicio,
                line={
                    "width": 2,
                    "color": COLOR_SERVICIO[servicio],
                },
            )
        )

    periodos = sorted(
        {
            periodo
            for df, _ in datasets.values()
            for periodo in df["periodo"]
        }
    )

    fig.update_layout(
        title="Ingresos por servicio",
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

    # =====================================================
    # TABLA
    # =====================================================

    with st.expander("Ver datos"):

        rows = []

        for servicio, (df, col) in datasets.items():

            tmp = df[
                [
                    "periodo",
                    col,
                ]
            ].copy()

            tmp["Servicio"] = servicio

            tmp = tmp.rename(
                columns={
                    col: "Ingresos",
                }
            )

            rows.append(tmp)

        st.dataframe(
            pd.concat(
                rows,
                ignore_index=True,
            ),
            width="stretch",
            hide_index=True,
        )