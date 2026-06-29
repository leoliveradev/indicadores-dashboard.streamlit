import streamlit as st
from components.kpi_cards import show_kpis
from components.charts import area_chart
from services.transformers import melt_tecnologias

from pages.tv.config import RESUMEN_KPIS, TV_COLOR_MAP
from pages.tv.utils import load_dataset, build_kpis


def split_tipo(df, value_name):
    df_long = melt_tecnologias(
        df,
        ["tv_suscripcion", "tv_satelital"],
        id_col="periodo",
        var_name="Tipo",
        value_name=value_name,
    )
    df_long["Tipo"] = df_long["Tipo"].map({
        "tv_suscripcion": "TV suscripción",
        "tv_satelital": "TV satelital",
    })
    return df_long


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