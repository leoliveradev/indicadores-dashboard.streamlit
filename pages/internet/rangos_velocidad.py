import streamlit as st
import pandas as pd

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import (
    line_chart,
    area_chart,
    bar_chart,
)

from services.kpi_builder import build_kpis

from services.chart_helpers import (
    composition_pie_chart,
)

from services.transformers import (
    melt_tecnologias,
)

from pages.internet.utils import (
    load_dataset,
)

from pages.internet.config import (
    RANGOS_KPIS,
    VELOCIDAD_RANGOS_COLS,
    VELOCIDAD_RANGOS_LABELS,
)


def render():

    # st.header("Rangos de velocidad")
    st.caption("Evolución de los rangos de velocidad de Internet.")

    df = load_dataset("velocidad_rangos")

    # ── Filtro ───────────────────────────────────────────

    anio_desde, anio_hasta = render_range_filter(
        df,
        key_prefix="vrang",
    )

    df_range = df[
        (df["anio"] >= anio_desde)
        & (df["anio"] <= anio_hasta)
    ].copy()

    # ── KPIs ─────────────────────────────────────────────

    kpis = build_kpis(
        RANGOS_KPIS,
        {"rangos": df_range},
        default_dataset="rangos",
    )

    show_kpis(kpis)

    st.divider()

    # ── Composición actual ───────────────────────────────

    st.subheader(
        f"Composición — {df_range['periodo'].iloc[-1]}"
    )

    fig_pie = composition_pie_chart(
        df_range,
        columns=VELOCIDAD_RANGOS_COLS,
        labels=VELOCIDAD_RANGOS_LABELS,
        title=(
            f"Distribución por rango "
            f"— {df_range['periodo'].iloc[-1]}"
        ),
    )

    st.plotly_chart(
        fig_pie,
        width="stretch",
    )

    st.divider()

    # ── Evolución histórica ──────────────────────────────

    df_long = melt_tecnologias(
        df_range,
        VELOCIDAD_RANGOS_COLS,
        id_col="periodo",
        var_name="Rango",
        value_name="Accesos",
    )

    df_long["Rango"] = (
        df_long["Rango"]
        .map(VELOCIDAD_RANGOS_LABELS)
    )

    orden_rangos = list(
        VELOCIDAD_RANGOS_LABELS.values()
    )

    df_long["Rango"] = pd.Categorical(
        df_long["Rango"],
        categories=orden_rangos,
        ordered=True,
    )

    df_long = df_long.sort_values(
        ["periodo", "Rango"]
    )

    st.subheader(
        "📊 Evolución por rangos"
    )

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Área", "Barras", "Líneas"],
        horizontal=True,
        label_visibility="collapsed",
        key="rangos_chart_type",
    )

    if chart_type == "Área":

        fig = area_chart(
            df_long,
            "periodo",
            "Accesos",
            "Rango",
            title="Evolución por rangos de velocidad",
        )

    elif chart_type == "Barras":

        fig = bar_chart(
            df_long,
            "periodo",
            "Accesos",
            "Rango",
            title="Accesos por rango de velocidad",
            barmode="stack",
        )

    else:

        fig = line_chart(
            df_long,
            "periodo",
            "Accesos",
            "Rango",
            title="Evolución por rango de velocidad",
        )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    # ── Tabla ────────────────────────────────────────────

    with st.expander("Ver datos completos"):

        st.dataframe(
            df_range,
            width="stretch",
        )