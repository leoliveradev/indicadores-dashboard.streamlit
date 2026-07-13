import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import (
    line_chart,
    area_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis

from services.transformers import (
    aggregate_by_periodo,
    filter_by_period,
    melt_tecnologias,
)

from pages.internet.utils import (
    load_dataset,
)

from pages.internet.config import (
    TECNOLOGIA_KPIS,
    TECNOLOGIAS_COLS,
    TECNOLOGIAS_LABELS,
)


def render():

    st.header("Accesos por tecnología")

    df = load_dataset("tecnologias")

    anio, trimestre = render_period_filters(
        df,
        key_prefix="tec",
    )

    df_periodo = filter_by_period(
        df,
        anio,
        trimestre,
    )

    kpis = build_kpis(
        TECNOLOGIA_KPIS,
        {"tec": df_periodo},
        default_dataset="tec",
    )

    show_kpis(kpis)

    st.divider()

    df_nat = aggregate_by_periodo(
        df,
        TECNOLOGIAS_COLS,
    )

    df_long = melt_tecnologias(
        df_nat,
        TECNOLOGIAS_COLS,
    )

    df_long["Tecnología"] = df_long["Tecnología"].map(TECNOLOGIAS_LABELS)

    st.subheader("📊 Evolución tecnológica")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Líneas", "Área", "Barras"],
        horizontal=True,
        key="internet_tec_chart",
    )

    if chart_type == "Líneas":

        fig = line_chart(
            df_long,
            "periodo",
            "Accesos",
            "Tecnología",
            title="Evolución por tecnología",
        )

    elif chart_type == "Área":

        fig = area_chart(
            df_long,
            "periodo",
            "Accesos",
            "Tecnología",
            title="Composición en el tiempo",
        )

    else:

        fig = bar_chart(
            df_long,
            "periodo",
            "Accesos",
            "Tecnología",
            title="Barras apiladas por tecnología",
            barmode="stack",
        )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.divider()

    st.subheader(f"Composición — {anio} T{trimestre}")

    periodo_actual = filter_by_period(
        df,
        anio,
        trimestre,
    )

    ultimo = (
        periodo_actual[TECNOLOGIAS_COLS].sum().rename(TECNOLOGIAS_LABELS).reset_index()
    )

    ultimo.columns = [
        "Tecnología",
        "Accesos",
    ]

    import plotly.express as px

    fig_pie = px.pie(
        ultimo,
        names="Tecnología",
        values="Accesos",
        hole=0.45,
    )

    st.plotly_chart(
        fig_pie,
        width="stretch",
    )

    with st.expander("Ver datos completos"):

        st.dataframe(
            periodo_actual,
            width="stretch",
        )
