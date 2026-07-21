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


def render():

    st.header(
        "Crecimiento relativo de accesos"
    )

    st.caption(
        "Compara la evolución de cada servicio eliminando las diferencias de escala."
    )

    # =====================================================
    # DATASETS
    # =====================================================

    datasets = {
        "Internet fijo": (
            load_dataset("internet_accesos"),
            "total",
        ),
        "Telefonía móvil": (
            load_dataset("movil_accesos"),
            "operativos",
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

    # =====================================================
    # FILTROS
    # =====================================================

    col1, col2 = st.columns([1, 2])

    with col1:

        anios = sorted(
            {
                int(df["anio"].min())
                for df, _ in datasets.values()
            }
        )

        base_anio = st.selectbox(
            "Año base (=100)",
            anios,
            index=anios.index(
                max(
                    anios[0],
                    2014,
                )
            ),
            key="comp_crec_base",
        )

    with col2:

        servicios_sel = st.multiselect(
            "Servicios",
            list(datasets.keys()),
            default=list(datasets.keys()),
            key="comp_crec_servicios",
        )

    if not servicios_sel:

        st.warning(
            "Seleccioná al menos un servicio.",
            icon="⚠️",
        )
        return

    # =====================================================
    # DATAFRAME LARGO
    # =====================================================

    frames = []

    for servicio in servicios_sel:

        df, col = datasets[servicio]

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

        st.warning(
            "No hay datos para el año base seleccionado."
        )
        return

    # =====================================================
    # KPIS
    # =====================================================

    kpis = []

    for servicio in servicios_sel:

        sub = df_idx[
            df_idx["Servicio"] == servicio
        ]

        if sub.empty:
            continue

        ultimo = sub["indice"].iloc[-1]

        kpis.append(
            {
                "label": servicio,
                "value": ultimo - 100,
                "format": "{:+.1f}%",
            }
        )

    show_kpis(kpis)

    st.divider()

    # =====================================================
    # GRÁFICO
    # =====================================================

    fig = go.Figure()

    fig.add_hline(
        y=100,
        line_dash="dot",
        line_width=1,
        annotation_text=f"Base = {base_anio}",
    )

    for servicio in servicios_sel:

        sub = df_idx[
            df_idx["Servicio"] == servicio
        ]

        fig.add_trace(
            go.Scatter(
                x=sub["periodo"],
                y=sub["indice"],
                mode="lines",
                name=servicio,
                line={
                    "width": 2,
                    "color": COLOR_SERVICIO[servicio],
                },
            )
        )

    periodos = sorted(
        df_idx["periodo"].unique()
    )

    fig.update_layout(
        title=f"Crecimiento relativo (base 100 = {base_anio})",
        hovermode="x unified",
        xaxis={
            "categoryorder": "array",
            "categoryarray": periodos,
        },
        legend={
            "orientation": "h",
        },
        yaxis={
            "title": "Índice",
        },
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.caption(
        "Un valor de 150 implica un crecimiento de 50% respecto al año base."
    )

    with st.expander("Ver datos"):

        pivot = (
            df_idx
            .pivot_table(
                index="periodo",
                columns="Servicio",
                values="indice",
            )
            .round(2)
        )

        st.dataframe(
            pivot,
            width="stretch",
        )