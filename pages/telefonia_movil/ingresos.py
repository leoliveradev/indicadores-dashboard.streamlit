import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    line_chart,
    area_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis
from services.kpi_helpers import build_growth_kpi

from pages.telefonia_movil.utils import load_dataset
from pages.telefonia_movil.config import INGRESOS_KPIS


def render():
    st.header("Ingresos del sector móvil")

    df = load_dataset("ingresos")

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="mov_ing",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs base
    kpis = build_kpis(
        INGRESOS_KPIS,
        {"ingresos": df_range},
        default_dataset="ingresos",
    )

    # crecimiento acumulado
    # val_inicio = df_range["ingresos"].iloc[0]
    # val_actual = df_range["ingresos"].iloc[-1]

    # crecimiento = (
    #     (val_actual - val_inicio)
    #     / val_inicio
    #     * 100
    #     if val_inicio
    #     else None
    # )

    # kpis.append(
    #     {
    #         "label": "Crecimiento acumulado",
    #         "value": crecimiento,
    #         "format": "{:+.1f}%",
    #         "help": (
    #             f"Variación desde "
    #             f"{anio_desde} hasta {anio_hasta}"
    #         ),
    #     }
    # )
    
    kpis.append(
        build_growth_kpi(
            df_range,
            "ingresos",
            help_text=f"Variación desde {anio_desde} hasta {anio_hasta}",
        )
    )


    show_kpis(kpis)

    st.divider()

    st.subheader("📊 Evolución de ingresos")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Barras", "Líneas", "Área"],
        horizontal=True,
        label_visibility="collapsed",
        key="mov_ing_chart",
    )

    chart_fn = {
        "Barras": bar_chart,
        "Líneas": line_chart,
        "Área": area_chart,
    }[chart_type]

    fig = chart_fn(
        df_range,
        "periodo",
        "ingresos",
        title="Ingresos del sector móvil (miles $)",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range,
            width="stretch",
        )