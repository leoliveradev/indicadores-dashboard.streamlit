import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    area_chart,
    line_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis
from services.chart_helpers import participation_chart
from services.modality_helpers import melt_modalidad

from pages.telefonia_movil.utils import load_dataset
from pages.telefonia_movil.config import (
    MINUTOS_KPIS,
    MODALIDAD_COLOR_MAP,
)


def render():
    st.header("Minutos de voz cursados")

    df = load_dataset("minutos")

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="mov_min",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs
    kpis = build_kpis(
        MINUTOS_KPIS,
        {"minutos": df_range},
        default_dataset="minutos",
    )

    show_kpis(kpis)

    st.divider()

    # datos para gráficos
    df_long = melt_modalidad(
        df_range,
        "Minutos",
    )

    st.subheader("📊 Evolución por modalidad")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Área", "Líneas", "Barras"],
        horizontal=True,
        key="mov_min_chart",
    )

    chart_fn = {
        "Área": area_chart,
        "Líneas": line_chart,
        "Barras": bar_chart,
    }[chart_type]

    fig = chart_fn(
        df_long,
        "periodo",
        "Minutos",
        "Modalidad",
        title="Minutos de voz — pospago vs prepago",
        color_map=MODALIDAD_COLOR_MAP,
    )

    if chart_type == "Barras":
        fig.update_layout(barmode="stack")

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("% minutos pospago sobre el total")

    fig_pct = participation_chart(
        df_range,
        numerator="pospago",
        denominator="total",
        title="% minutos pospago sobre el total",
    )

    st.plotly_chart(
        fig_pct,
        use_container_width=True,
    )

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range,
            use_container_width=True,
        )