import streamlit as st
from components.kpi_cards import show_kpis
from components.charts import area_chart

from pages.tv.config import RESUMEN_KPIS, TV_COLOR_MAP
from pages.tv.utils import load_dataset, build_kpis, split_tipo


def render():
    st.header("Resumen general")

    datasets = {
        "accesos": load_dataset("accesos"),
        "ingresos": load_dataset("ingresos"),
        "penetracion": load_dataset("penetracion"),
    }

    kpis = build_kpis(RESUMEN_KPIS, datasets)

    show_kpis(kpis)

    st.divider()

    with st.container():
        fig = area_chart(
            split_tipo(datasets["accesos"], "Accesos"),
            "periodo",
            "Accesos",
            "Tipo",
            title="Accesos — suscripción vs satelital",
            color_map=TV_COLOR_MAP,
        )
        st.plotly_chart(fig, use_container_width=True)

        fig = area_chart(
            split_tipo(datasets["ingresos"], "Ingresos"),
            "periodo",
            "Ingresos",
            "Tipo",
            title="Ingresos — suscripción vs satelital",
            color_map=TV_COLOR_MAP,
        )
        st.plotly_chart(fig, use_container_width=True)