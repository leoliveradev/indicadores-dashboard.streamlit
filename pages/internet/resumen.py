import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from components.kpi_cards import show_kpis
from components.charts import line_chart

from services.kpi_builder import build_kpis
from services.transformers import (
    last_period_delta,
    aggregate_by_periodo,
    melt_tecnologias,
    filter_by_period,
)

from pages.internet.utils import load_dataset

from pages.internet.config import (
    RESUMEN_KPIS,
    TECNOLOGIAS_COLS,
    TECNOLOGIAS_LABELS,
    VELOCIDAD_RANGOS_COLS,
    VELOCIDAD_RANGOS_LABELS,
)


def render():

    st.header("Resumen general")

    # ── Datasets ──────────────────────────────────────────

    df_tec = load_dataset("tecnologias")
    df_pen = load_dataset("penetracion")
    df_ing = load_dataset("ingresos")
    df_rang = load_dataset("velocidad_rangos")
    df_vel = load_dataset("velocidad_media")

    datasets = {
        "tecnologias": df_tec,
        "penetracion": df_pen,
    }

    # ── KPIs base ─────────────────────────────────────────

    kpis = build_kpis(
        RESUMEN_KPIS,
        datasets,
    )

    # KPI ingresos

    val_ing, delta_ing = last_period_delta(
        df_ing,
        "ingresos",
    )

    kpis.append(
        {
            "label": "Ingresos (miles $)",
            "value": val_ing,
            "delta": delta_ing,
            "format": "{:,.0f}",
        }
    )

    # KPI participación fibra

    ultimo = df_tec.iloc[-1]
    anterior = df_tec.iloc[-2]

    pct_fibra = (
        ultimo["fibra_optica"]
        / ultimo["total"]
        * 100
    )

    pct_fibra_prev = (
        anterior["fibra_optica"]
        / anterior["total"]
        * 100
    )

    kpis.append(
        {
            "label": "% Fibra sobre total",
            "value": pct_fibra,
            "delta": pct_fibra - pct_fibra_prev,
            "format": "{:.1f}%",
            "help": (
                "Participación de fibra óptica "
                "sobre el total de accesos"
            ),
        }
    )

    # mismo layout que tenías

    show_kpis(kpis[:3])
    show_kpis(kpis[3:])

    st.divider()

    # ── Tecnología + Velocidad ────────────────────────────

    col1, col2 = st.columns(2)

    with col1:

        periodo_tec = df_tec["periodo"].iloc[-1]

        df_pie = (
            df_tec[TECNOLOGIAS_COLS]
            .iloc[-1]
            .rename(TECNOLOGIAS_LABELS)
            .reset_index()
        )

        df_pie.columns = [
            "Tecnología",
            "Accesos",
        ]

        fig_pie = px.pie(
            df_pie,
            names="Tecnología",
            values="Accesos",
            hole=0.45,
            title=f"Composición por tecnología — {periodo_tec}",
        )

        st.plotly_chart(
            fig_pie,
            width="stretch",
        )

    with col2:

        vel_actual, _ = last_period_delta(
            df_vel,
            "mbps",
        )

        st.metric(
            "Velocidad media nacional",
            f"{vel_actual:.1f} Mbps",
        )

        fig = line_chart(
            df_vel,
            "periodo",
            "mbps",
            title="Velocidad media de descarga",
            markers=True,
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    st.divider()

    # ── Fibra vs ADSL vs Cable ────────────────────────────

    df_comp = aggregate_by_periodo(
        df_tec,
        [
            "fibra_optica",
            "adsl",
            "cablemodem",
        ],
    )

    df_comp = melt_tecnologias(
        df_comp,
        [
            "fibra_optica",
            "adsl",
            "cablemodem",
        ],
        var_name="Tecnología",
        value_name="Accesos",
    )

    df_comp["Tecnología"] = (
        df_comp["Tecnología"]
        .map(TECNOLOGIAS_LABELS)
    )

    fig = line_chart(
        df_comp,
        "periodo",
        "Accesos",
        "Tecnología",
        title=(
            "Fibra vs ADSL vs Cablemodem "
            "— convergencia tecnológica"
        ),
        markers=False,
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    st.divider()

    # ── Rangos de velocidad ───────────────────────────────

    periodo_rango = df_rang["periodo"].iloc[-1]

    ultimo_rango = (
        df_rang[VELOCIDAD_RANGOS_COLS]
        .iloc[-1]
        .rename(VELOCIDAD_RANGOS_LABELS)
    )

    df_rango_pie = (
        ultimo_rango
        .reset_index()
    )

    df_rango_pie.columns = [
        "Rango",
        "Accesos",
    ]

    df_rango_pie = df_rango_pie[
        df_rango_pie["Accesos"] > 0
    ]

    fig_rango = px.pie(
        df_rango_pie,
        names="Rango",
        values="Accesos",
        hole=0.45,
        title=f"Rangos de velocidad — {periodo_rango}",
    )

    st.plotly_chart(
        fig_rango,
        width="stretch",
    )