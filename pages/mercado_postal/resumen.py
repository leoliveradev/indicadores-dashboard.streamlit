import streamlit as st

from components.kpi_cards import show_kpis
from components.charts import (
    area_chart,
    line_chart,
)

from services.aggregation_helpers import mensual_a_trimestral

from pages.mercado_postal.utils import (
    load_dataset,
    melt_servicios,
)

from pages.mercado_postal.config import (
    RESUMEN_KPIS,
    SERVICIOS_COLS,
)

from services.kpi_builder import build_kpis


def render():

    st.header("Resumen general")

    # datasets
    df_facturation = load_dataset("facturacion")
    df_production = load_dataset("produccion")
    df_personal = load_dataset("personal")

    # agregación trimestral
    df_fac_t = mensual_a_trimestral(
        df_facturation,
        SERVICIOS_COLS,
    )

    df_pro_t = mensual_a_trimestral(
        df_production,
        SERVICIOS_COLS,
    )

    datasets = {
        "facturacion": df_fac_t,
        "produccion": df_pro_t,
        "personal": df_personal,
    }

    # kpis
    kpis = build_kpis(
        RESUMEN_KPIS,
        datasets,
    )

    show_kpis(kpis)

    st.divider()

    # Facturación
    df_fac_long = melt_servicios(
        df_fac_t,
        "Facturación",
    )

    fig = area_chart(
        df_fac_long,
        "periodo",
        "Facturación",
        "Servicio",
        title="Facturación por tipo de servicio ($)",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    # Producción
    df_pro_long = melt_servicios(
        df_pro_t,
        "Producción",
    )

    fig = area_chart(
        df_pro_long,
        "periodo",
        "Producción",
        "Servicio",
        title="Producción por tipo de servicio (unidades)",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    # Personal ocupado
    fig = line_chart(
        df_personal,
        "periodo",
        "personal_ocupado",
        title="Personal ocupado — evolución",
        labels={
            "personal_ocupado": "Personas",
        },
        markers=False,
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )
