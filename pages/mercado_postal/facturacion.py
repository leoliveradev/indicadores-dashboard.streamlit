import streamlit as st
import plotly.express as px

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    area_chart,
    line_chart,
    bar_chart,
)

from services.chart_helpers import composition_pie_chart
from services.kpi_builder import build_kpis
from services.aggregation_helpers import mensual_a_trimestral

from pages.mercado_postal.utils import (
    load_dataset,
    melt_servicios,
)

from pages.mercado_postal.config import (
    FACTURACION_KPIS,
    SERVICIOS_COLS,
    SERVICIOS_LABELS,
)


def render():

    st.header("Facturación del mercado postal")

    st.caption(
        "Datos mensuales agregados a trimestral."
    )

    # dataset
    df = load_dataset("facturacion")

    df_t = mensual_a_trimestral(
        df,
        SERVICIOS_COLS,
    )

    # filtro
    anio_desde, anio_hasta = render_range_filter(
        df_t,
        key_prefix="pos_fac",
    )

    df_range = df_t[
        (df_t["anio"] >= anio_desde)
        & (df_t["anio"] <= anio_hasta)
    ].copy()

    # KPIs
    kpis = build_kpis(
        FACTURACION_KPIS,
        {"facturacion": df_range},
        default_dataset="facturacion",
    )

    show_kpis(kpis)

    st.divider()

    # formato largo
    df_long = melt_servicios(
        df_range,
        "Facturación",
    )

    st.subheader("📊 Evolución por servicio")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Área", "Líneas", "Barras"],
        horizontal=True,
        key="postal_fac_chart",
    )

    chart_fn = {
        "Área": area_chart,
        "Líneas": line_chart,
        "Barras": bar_chart,
    }[chart_type]

    fig = chart_fn(
        df_long,
        "periodo",
        "Facturación",
        "Servicio",
        title="Facturación por tipo de servicio ($)",
    )

    if chart_type == "Barras":
        fig.update_layout(
            barmode="stack"
        )

    st.plotly_chart(
        fig,
        width="stretch",
        key=f"postal_facturacion_{chart_type}",
    )

    st.divider()

    st.subheader(
        f"Composición — {df_range['periodo'].iloc[-1]}"
    )

    fig_pie = composition_pie_chart(
        df_range,
        columns=SERVICIOS_COLS,
        labels=SERVICIOS_LABELS,
        title=f"Composición — {df_range['periodo'].iloc[-1]}",
    )

    st.plotly_chart(
        fig_pie,
        width="stretch",
        key="postal_facturacion_pie",
    )

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range,
            width="stretch",
        )