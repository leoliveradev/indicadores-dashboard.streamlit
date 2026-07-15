import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    area_chart,
    line_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis
from services.aggregation_helpers import mensual_a_trimestral
from services.chart_helpers import dual_axis_chart

from pages.mercado_postal.utils import (
    load_dataset,
    melt_servicios,
)

from pages.mercado_postal.config import (
    PRODUCCION_KPIS,
    SERVICIOS_COLS,
)


def render():

    st.header("Producción del mercado postal")

    st.caption(
        "Datos mensuales agregados a trimestral. "
        "Unidades físicas despachadas."
    )

    # Dataset
    df = load_dataset("produccion")

    df_t = mensual_a_trimestral(
        df,
        SERVICIOS_COLS,
    )

    # Filtro
    anio_desde, anio_hasta = render_range_filter(
        df_t,
        key_prefix="pos_pro",
    )

    df_range = df_t[
        (df_t["anio"] >= anio_desde)
        & (df_t["anio"] <= anio_hasta)
    ].copy()

    # KPIs
    kpis = build_kpis(
        PRODUCCION_KPIS,
        {"produccion": df_range},
        default_dataset="produccion",
    )

    show_kpis(kpis)

    st.divider()

    # Evolución
    df_long = melt_servicios(
        df_range,
        "Producción",
    )

    st.subheader("📊 Evolución por servicio")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Área", "Líneas", "Barras"],
        horizontal=True,
        key="postal_pro_chart",
    )

    chart_fn = {
        "Área": area_chart,
        "Líneas": line_chart,
        "Barras": bar_chart,
    }[chart_type]

    fig = chart_fn(
        df_long,
        "periodo",
        "Producción",
        "Servicio",
        title="Producción por tipo de servicio (unidades)",
    )

    if chart_type == "Barras":
        fig.update_layout(
            barmode="stack"
        )

    st.plotly_chart(
        fig,
        width="stretch",
        key=f"postal_produccion_{chart_type}",
    )

    st.divider()

    st.subheader(
        "Producción vs facturación — servicios postales"
    )

    df_fac = load_dataset("facturacion")

    df_fac_t = mensual_a_trimestral(
        df_fac,
        SERVICIOS_COLS,
    )

    df_fac_r = df_fac_t[
        (df_fac_t["anio"] >= anio_desde)
        & (df_fac_t["anio"] <= anio_hasta)
    ].copy()

    config = {
        "title": "Producción vs facturación — servicios postales",
        "left_axis": {
            "label": "Unidades",
            "series": [
                {
                    "column": "postales",
                    "name": "Producción postales",
                    "color": "#00B5E5",
                }
            ],
        },
        "right_axis": {
            "label": "Pesos ($)",
            "series": [
                {
                    "column": "postales",
                    "name": "Facturación postales",
                    "color": "#EEAE42",
                    "dash": "dot",
                }
            ],
        },
    }

    # usamos el mismo período para ambos
    df_compare = df_range[
        ["periodo", "postales"]
    ].rename(
        columns={
            "postales": "produccion_postales",
        }
    )

    df_compare["facturacion_postales"] = (
        df_fac_r["postales"].values
    )

    config = {
        "title": "Producción vs facturación — servicios postales",
        "left_axis": {
            "label": "Unidades",
            "series": [
                {
                    "column": "produccion_postales",
                    "name": "Producción postales",
                    "color": "#00B5E5",
                }
            ],
        },
        "right_axis": {
            "label": "Pesos ($)",
            "series": [
                {
                    "column": "facturacion_postales",
                    "name": "Facturación postales",
                    "color": "#EEAE42",
                    "dash": "dot",
                }
            ],
        },
    }

    fig = dual_axis_chart(
        config,
        df_compare,
    )

    st.plotly_chart(
        fig,
        width="stretch",
        key=f"produccion_vs_facturacion",

    )

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range,
            width="stretch",
        )