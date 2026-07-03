import streamlit as st
import plotly.graph_objects as go

from components.kpi_cards import show_kpis
from components.filters import render_range_filter

from services.transformers import last_period_delta
from services.kpi_helpers import build_max_kpi
from services.portabilidad_helpers import (
  mensual_a_trimestral, 
  mensual_a_anual, 
  add_mes_col
)
from services.chart_helpers import seasonality_chart

from pages.portabilidad.utils import (
    load_dataset,
    MESES
)


def render():
    st.header("Portabilidad — telefonía móvil")

    df = load_dataset("movil")
    df = add_mes_col(df)

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="port_mov",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    df_t = mensual_a_trimestral(df_range)
    df_a = mensual_a_anual(df_range)

    # KPIs
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
            "label": f"Total {anio_desde}-{anio_hasta}",
            "value": df_range["total"].sum(),
            "format": "{:,.0f}",
        },
        {
            "label": "Promedio mensual",
            "value": df_range["total"].mean(),
            "format": "{:,.0f}",
        },
        build_max_kpi(
            df_range,
            "total",
            label="Pico del período",
            fmt="{:,.0f}",
        ),
    ]

    show_kpis(kpis)

    st.divider()

    # Evolución histórica
    st.subheader("📊 Evolución histórica")

    granularidad = st.radio(
        "Granularidad",
        ["Mensual", "Trimestral", "Anual"],
        horizontal=True,
        key="port_gran",
    )

    if granularidad == "Mensual":

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_range["periodo"],
            y=df_range["total"],
            mode="lines",
            line={"color": "#00B5E5", "width": 1.5},
            fill="tozeroy",
            fillcolor="rgba(0,181,229,0.06)",
        ))

        fig.update_layout(
            title="Portaciones mensuales",
            hovermode="x unified",
            yaxis={"tickformat": ",.0f"},
            showlegend=False,
        )

    elif granularidad == "Trimestral":

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_t["periodo"],
            y=df_t["total"],
            mode="lines+markers",
            line={"color": "#00B5E5", "width": 2},
            marker={"size": 5},
            fill="tozeroy",
            fillcolor="rgba(0,181,229,0.08)",
        ))

        fig.update_layout(
            title="Portaciones trimestrales",
            hovermode="x unified",
            yaxis={"tickformat": ",.0f"},
            showlegend=False,
        )

    else:

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_a["anio"].astype(str),
            y=df_a["total"],
            marker_color="#00B5E5",
            text=df_a["total"].apply(lambda v: f"{v:,.0f}"),
            textposition="outside",
        ))

        fig.update_layout(
            title="Portaciones anuales",
            yaxis={"tickformat": ",.0f"},
            showlegend=False,
        )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    # Estacionalidad
    st.subheader("📅 Estacionalidad")

    st.caption(
        "Promedio histórico de portaciones por mes."
    )



    fig_est = seasonality_chart(
        df_range,
        value_col="total",
        month_col="mes",
        month_labels=MESES,
        title="Estacionalidad de portaciones",
    )

    st.plotly_chart(
        fig_est,
        use_container_width=True,
    )

    # df_estac = (
    #     df_range.groupby("mes")["total"]
    #     .mean()
    #     .reset_index()
    #     .sort_values("mes")
    # )

    # df_estac["mes_label"] = (
    #     df_estac["mes"]
    #     .map(MESES)
    # )

    # promedio_global = (
    #     df_estac["total"]
    #     .mean()
    # )

    # fig_est = go.Figure()

    # fig_est.add_trace(go.Bar(
    #     x=df_estac["mes_label"],
    #     y=df_estac["total"],
    #     marker_color=[
    #         "#00B5E5"
    #         if v >= promedio_global
    #         else "#BCE4F4"
    #         for v in df_estac["total"]
    #     ],
    #     text=df_estac["total"].apply(
    #         lambda v: f"{v:,.0f}"
    #     ),
    #     textposition="outside",
    # ))

    # fig_est.add_hline(
    #     y=promedio_global,
    #     line_dash="dot",
    #     line_color="#C6C6C6",
    #     annotation_text=f"Promedio: {promedio_global:,.0f}",
    # )

    # fig_est.update_layout(
    #     yaxis={"tickformat": ",.0f"},
    #     showlegend=False,
    # )

    # st.plotly_chart(
    #     fig_est,
    #     use_container_width=True,
    # )

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range[
                [
                    "anio",
                    "mes",
                    "periodo",
                    "total",
                ]
            ].rename(
                columns={"total": "portaciones"}
            ),
            use_container_width=True,
        )