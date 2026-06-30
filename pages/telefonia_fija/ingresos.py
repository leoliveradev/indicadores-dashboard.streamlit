import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_range_filter
from components.charts import line_chart, bar_chart, area_chart

from pages.telefonia_fija.utils import load_dataset, build_kpis
from pages.telefonia_fija.config import INGRESOS_KPIS


def render():
    st.header("Ingresos del sector")

    df = load_dataset("ingresos")

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tel_ing")

    df_range = df[
        (df["anio"] >= anio_desde) &
        (df["anio"] <= anio_hasta)
    ].copy()

    # KPIs dinámicos
    datasets = {"ingresos": df_range}

    kpis = build_kpis(
        INGRESOS_KPIS,
        datasets,
        default_dataset="ingresos",
    )

    # KPI adicional: crecimiento acumulado
    val_inicio = df_range["ingresos"].iloc[0]
    val_actual = df_range["ingresos"].iloc[-1]

    crec_acum = (
        (val_actual - val_inicio) / val_inicio * 100
        if val_inicio
        else None
    )

    kpis.append({
        "label": "Crecimiento acumulado",
        "value": crec_acum,
        "format": "{:+.1f}%",
        "help": f"Variación desde {anio_desde} hasta {anio_hasta}",
    })

    show_kpis(kpis)

    st.divider()

    # selector único (consistente con todo el dashboard)
    st.subheader("📊 Evolución de ingresos")

    chart_type = st.radio(
        "Tipo de gráfico",
        ["Barras", "Líneas", "Área"],
        horizontal=True,
        key="tel_ing_chart",
    )

    chart_fn = {
        "Barras": bar_chart,
        "Líneas": line_chart,
        "Área": area_chart,
    }[chart_type]

    fig = chart_fn(
        df_range,
        "periodo",
        "ingresos",
        title="Ingresos por trimestre (miles $)",
    )

    st.plotly_chart(fig, use_container_width=True)

    # tabla opcional
    with st.expander("Ver datos completos"):
        st.dataframe(df_range, use_container_width=True)