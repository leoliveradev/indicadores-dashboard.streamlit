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
)

from services.chart_helpers import (
    composition_pie_chart,
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

    # st.header("Resumen general")
    st.caption("Resumen de los principales indicadores del sector de telecomunicaciones.")
    # ── Datasets ──────────────────────────────────────────

    df_tec = load_dataset("tecnologias")
    df_pen = load_dataset("penetracion")
    df_ing = load_dataset("ingresos")
    df_rang = load_dataset("velocidad_rangos")
    df_vel = load_dataset("velocidad_media")

    datasets = {
        "tecnologias": df_tec,
        "penetracion": df_pen,
        "vmd": df_vel,
    }

    # ── KPIs base ─────────────────────────────────────────

    kpis = build_kpis(
        RESUMEN_KPIS,
        datasets,
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

    # mismo layout que tenías

    show_kpis(kpis[:3])
    show_kpis(kpis[3:])

    st.divider()

    # ── Tecnología + Velocidad ────────────────────────────

    col1, col2 = st.columns(2)

    with col1:

        periodo_tec = df_tec["periodo"].iloc[-1]

        fig_pie = composition_pie_chart(
            df_tec,
            columns=TECNOLOGIAS_COLS,
            labels=TECNOLOGIAS_LABELS,
            title=f"Composición por tecnología — {periodo_tec}",
        )

        st.plotly_chart(
            fig_pie,
            width="stretch",
        )

    with col2:
        # ── Rangos de velocidad ───────────────────────────────

        fig_rango = composition_pie_chart(
            df_rang,
            columns=VELOCIDAD_RANGOS_COLS,
            labels=VELOCIDAD_RANGOS_LABELS,
            title=f"Composición por rango — {df_rang['periodo'].iloc[-1]}",
        )

        st.plotly_chart(
            fig_rango,
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


