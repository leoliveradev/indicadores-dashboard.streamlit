import streamlit as st

from components.kpi_cards import show_kpis
from components.charts import line_chart, bar_chart, area_chart

from pages.telefonia_movil.utils import load_dataset
from services.modality_helpers import melt_modalidad

from services.kpi_builder import build_kpis

from pages.telefonia_movil.config import RESUMEN_KPIS, MODALIDAD_COLOR_MAP


def render():
    st.header("Resumen general")

    datasets = {
        "accesos": load_dataset("accesos"),
        "ingresos": load_dataset("ingresos"),
        "minutos": load_dataset("minutos"),
        "penetracion": load_dataset("penetracion"),
    }

    # KPIs
    kpis = build_kpis(RESUMEN_KPIS, datasets)
    show_kpis(kpis)

    st.divider()

    st.subheader("📊 Evolución de métricas clave")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Líneas", "Área", "Barras"],
        horizontal=True,
        label_visibility="collapsed",
        key="mov_resumen_chart",
    )

    chart_fn = {
        "Líneas": line_chart,
        "Área": area_chart,
        "Barras": bar_chart,
    }[chart_type]

    col1, col2 = st.columns(2)

    with col1:
        fig = chart_fn(
            datasets["accesos"],
            "periodo",
            "total",
            title="Líneas operativas",
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = chart_fn(
            datasets["ingresos"],
            "periodo",
            "ingresos",
            title="Ingresos (miles $)",
        )
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        df_min_long = melt_modalidad(datasets["minutos"], "Minutos")

        fig = area_chart(
            df_min_long,
            "periodo",
            "Minutos",
            "Modalidad",
            title="Minutos de voz — modalidades",
            color_map=MODALIDAD_COLOR_MAP,
        )
        st.plotly_chart(fig, width="stretch")

    with col4:
        fig = line_chart(
            datasets["penetracion"],
            "periodo",
            "accesos_100_hab",
            title="Penetración (c/100 hab.)",
            markers=False,
        )
        st.plotly_chart(fig, width="stretch")