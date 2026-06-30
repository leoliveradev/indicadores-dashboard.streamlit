import streamlit as st
import plotly.graph_objects as go

from components.kpi_cards import show_kpis
from components.filters import render_range_filter

from pages.telefonia_fija.utils import (
    load_dataset,
    build_kpis,
    compute_yoy
)
from services.chart_helpers import dual_axis_chart
from pages.telefonia_fija.config import PENETRACION_KPIS


def render():
    st.header("Penetración de telefonía fija")

    df = load_dataset("penetracion")

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tel_pen")

    df_range = df[
        (df["anio"] >= anio_desde) &
        (df["anio"] <= anio_hasta)
    ].copy()

    datasets = {"penetracion": df_range}

    kpis = build_kpis(
        PENETRACION_KPIS,
        datasets,
        default_dataset="penetracion",
    )

    # KPI (máximo histórico)
    max_val = df_range["accesos_100_hab"].max()
    periodo_max = df_range.loc[
        df_range["accesos_100_hab"].idxmax(), "periodo"
    ]

    kpis.append({
        "label": f"Máx. histórico c/100 habitantes ({periodo_max})",
        "value": max_val,
        "format": "{:.2f}",
    })

    show_kpis(kpis)

    st.divider()

    # gráfico dual axis
    st.subheader("📊 Evolución de penetración")

    DUAL_AXIS_CONFIG = {
        "title": "c/100 hogares vs c/100 habitantes",

        "left_axis": {
            "label": "c/100 hogares",
            "suffix": "",
            "series": [
                {
                    "column": "accesos_100_hog",
                    "name": "c/100 hogares",
                    "color": "#00B5E5",
                    "mode": "lines+markers",
                },
            ],
        },

        "right_axis": {
            "label": "c/100 habitantes",
            "suffix": "",
            "series": [
                {
                    "column": "accesos_100_hab",
                    "name": "c/100 habitantes",
                    "color": "#EEAE42",
                    "mode": "lines+markers",
                },
            ],
        },
    }

    fig = dual_axis_chart(DUAL_AXIS_CONFIG, df_range)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # YoY reutilizable
    # st.subheader("Variación interanual — c/100 habitantes")

    # df_yoy = compute_yoy(df_range, "accesos_100_hab")

    # fig_yoy = go.Figure(go.Bar(
    #     x=df_yoy["periodo"],
    #     y=df_yoy["yoy"].round(2),
    #     marker_color=[
    #         "#00B5E5" if v >= 0 else "#E74242"
    #         for v in df_yoy["yoy"]
    #     ],
    # ))

    # fig_yoy.update_layout(
    #     yaxis={"ticksuffix": "%"},
    #     margin={"t": 20, "b": 40, "l": 40, "r": 20},
    #     showlegend=False,
    # )

    # st.plotly_chart(fig_yoy, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range[
                ["anio", "trimestre", "periodo",
                 "accesos_100_hab", "accesos_100_hog"]
            ],
            use_container_width=True,
        )