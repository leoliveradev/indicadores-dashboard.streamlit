import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    line_chart,
    area_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis
from services.kpi_helpers import (
    build_max_kpi,
    build_growth_kpi,
)

from pages.mercado_postal.utils import load_dataset
from pages.mercado_postal.config import PERSONAL_KPIS


def render():

    st.header("Personal ocupado en el mercado postal")

    # Dataset
    df = load_dataset("personal")

    # Filtro
    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="postal_per",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs base
    kpis = build_kpis(
        PERSONAL_KPIS,
        {"personal": df_range},
        default_dataset="personal",
    )

    # mínimo histórico
    idx_min = df_range["personal_ocupado"].idxmin()

    kpis.append({
        "label": f"Mínimo histórico ({df_range.loc[idx_min, 'periodo']})",
        "value": df_range.loc[idx_min, "personal_ocupado"],
        "format": "{:,.0f}",
    })

    # máximo histórico
    kpis.append(
        build_max_kpi(
            df_range,
            "personal_ocupado",
            fmt="{:,.0f}",
        )
    )

    # crecimiento acumulado
    kpis.append(
        build_growth_kpi(
            df_range,
            "personal_ocupado",
            help_text=f"Variación desde {anio_desde} hasta {anio_hasta}",
        )
    )

    show_kpis(kpis)

    st.divider()

    st.subheader("📊 Evolución del empleo")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Líneas", "Área", "Barras"],
        horizontal=True,
        key="postal_personal_chart",
    )

    chart_fn = {
        "Líneas": line_chart,
        "Área": area_chart,
        "Barras": bar_chart,
    }[chart_type]

    fig = chart_fn(
        df_range,
        "periodo",
        "personal_ocupado",
        title="Personal ocupado — evolución histórica",
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    with st.expander("Ver datos completos"):

        st.dataframe(
            df_range[
                [
                    "anio",
                    "trimestre",
                    "periodo",
                    "personal_ocupado",
                ]
            ],
            width="stretch",
        )