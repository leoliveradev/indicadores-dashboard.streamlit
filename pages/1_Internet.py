"""
1_Internet.py
─────────────
Vista de Internet Fijo.
"""

import streamlit as st
import plotly.express as px

from config.constants import InternetCSV, TECNOLOGIAS_COLS, TECNOLOGIAS_LABELS
from config.theme import COLORS

from services.data_manager import DataManager, DataLoadError
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
    filter_by_period,
    aggregate_by_periodo,
    melt_tecnologias,
    last_period_delta,
)

from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.filters import render_period_filters, render_range_filter   # ← nuevo
from components.charts import line_chart, bar_chart, area_chart


st.set_page_config(page_title="Internet · ENACOM", page_icon="🌐", layout="wide")
setup_page()

CATEGORIES = [
    "Resumen general",
    "Tecnología",
    "Velocidad media",
    "Rangos de velocidad",
    "Banda ancha vs Dial-up",
    "Penetración",
    "Ingresos",
]

categoria = render_sidebar(CATEGORIES, key="internet_categoria")
st.title("🌐 Internet fijo")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


# ── Resumen general ───────────────────────────────────────────────────────────

if categoria == "Resumen general":
    st.header("Resumen general")

    df = load(InternetCSV.TECNOLOGIAS)
    DataValidator.validate(df, ["anio", "trimestre", "total", "fibra_optica", "adsl"])

    df = sort_by_periodo(add_periodo_col(df))
    df_nat = aggregate_by_periodo(df, TECNOLOGIAS_COLS + ["total"])

    total, delta_total = last_period_delta(df_nat, "total")
    fibra, delta_fibra = last_period_delta(df_nat, "fibra_optica")
    adsl,  delta_adsl  = last_period_delta(df_nat, "adsl")
    cable, delta_cable = last_period_delta(df_nat, "cablemodem")

    show_kpis([
        {"label": "Accesos totales", "value": total, "delta": delta_total, "format": "{:,.0f}"},
        {"label": "Fibra óptica",    "value": fibra, "delta": delta_fibra, "format": "{:,.0f}"},
        {"label": "Cablemodem",      "value": cable, "delta": delta_cable, "format": "{:,.0f}"},
        {"label": "ADSL",            "value": adsl,  "delta": delta_adsl,  "format": "{:,.0f}"},
    ])

    st.divider()

    df_long = melt_tecnologias(df_nat, value_cols=TECNOLOGIAS_COLS,
                               var_name="Tecnología", value_name="Accesos")
    df_long["Tecnología"] = df_long["Tecnología"].map(TECNOLOGIAS_LABELS)

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = line_chart(df_long, x="periodo", y="Accesos", color="Tecnología",
                         title="Accesos por tecnología — evolución")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        df_pie = df_nat[TECNOLOGIAS_COLS].iloc[-1].rename(TECNOLOGIAS_LABELS).reset_index()
        df_pie.columns = ["Tecnología", "Accesos"]
        fig2 = px.pie(df_pie, names="Tecnología", values="Accesos",
                      title=f"Composición — {df_nat['periodo'].iloc[-1]}", hole=0.45)
        fig2.update_layout(margin={"t": 50, "b": 0, "l": 0, "r": 0})
        st.plotly_chart(fig2, use_container_width=True)


# ── Tecnología ────────────────────────────────────────────────────────────────

elif categoria == "Tecnología":
    st.header("Accesos por tecnología")

    df = load(InternetCSV.TECNOLOGIAS)
    DataValidator.validate(df, ["anio", "trimestre"] + TECNOLOGIAS_COLS + ["total"])

    # ← filtros inline, ya no en el sidebar
    anio, trimestre = render_period_filters(df, key_prefix="tec")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_filtered = filter_by_period(df, anio, trimestre)
    total, _ = last_period_delta(df_filtered, "total")
    fibra     = df_filtered["fibra_optica"].sum()
    adsl      = df_filtered["adsl"].sum()
    cable     = df_filtered["cablemodem"].sum()

    show_kpis([
        {"label": "Total",        "value": total, "format": "{:,.0f}"},
        {"label": "Fibra óptica", "value": fibra, "format": "{:,.0f}"},
        {"label": "Cablemodem",   "value": cable, "format": "{:,.0f}"},
        {"label": "ADSL",         "value": adsl,  "format": "{:,.0f}"},
    ])

    st.divider()

    df = sort_by_periodo(add_periodo_col(df))
    df_nat = aggregate_by_periodo(df, TECNOLOGIAS_COLS)
    df_long = melt_tecnologias(df_nat, TECNOLOGIAS_COLS)
    df_long["Tecnología"] = df_long["Tecnología"].map(TECNOLOGIAS_LABELS)

    tab_linea, tab_area, tab_barra = st.tabs(["Líneas", "Área", "Barras"])
    with tab_linea:
        st.plotly_chart(line_chart(df_long, "periodo", "Accesos", "Tecnología",
                                   title="Evolución por tecnología"),
                        use_container_width=True)
    with tab_area:
        st.plotly_chart(area_chart(df_long, "periodo", "Accesos", "Tecnología",
                                   title="Composición en el tiempo"),
                        use_container_width=True)
    with tab_barra:
        st.plotly_chart(bar_chart(df_long, "periodo", "Accesos", "Tecnología",
                                  title="Barras apiladas por tecnología", barmode="stack"),
                        use_container_width=True)


# ── Velocidad media ───────────────────────────────────────────────────────────

elif categoria == "Velocidad media":
    st.header("Velocidad media de descarga")

    df = load(InternetCSV.VELOCIDAD_MEDIA)
    DataValidator.validate(df, ["anio", "trimestre", "mbps"])

    # ← slider de rango inline, ya no en el sidebar
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="vel")

    df_range = sort_by_periodo(add_periodo_col(
        df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]
    ))

    vel_actual, delta_vel = last_period_delta(df_range, "mbps")
    show_kpis([
        {"label": "Vel. media actual", "value": vel_actual,
         "delta": delta_vel, "format": "{:.1f} Mbps"},
    ])

    st.divider()

    st.plotly_chart(
        line_chart(df_range, x="periodo", y="mbps",
                   title="Velocidad media de descarga (Mbps)",
                   labels={"mbps": "Mbps", "periodo": "Período"}, markers=True),
        use_container_width=True,
    )


# ── Penetración ───────────────────────────────────────────────────────────────

elif categoria == "Penetración":
    st.header("Penetración de Internet")

    df = load(InternetCSV.PENETRACION_HOGARES)
    DataValidator.validate(df, ["anio", "trimestre"])
    df = sort_by_periodo(add_periodo_col(df))

    value_col = next(
        (c for c in df.columns if "accesos" in c or "penetracion" in c or "hogares" in c), None
    )
    if value_col is None:
        st.warning("No se encontró columna de penetración. Columnas: " + str(list(df.columns)))
        st.stop()

    val, delta = last_period_delta(df, value_col)
    show_kpis([{"label": "Accesos c/100 hogares", "value": val,
                "delta": delta, "format": "{:.2f}"}])

    st.divider()
    st.plotly_chart(
        line_chart(df, x="periodo", y=value_col,
                   title="Penetración de Internet fijo (accesos cada 100 hogares)"),
        use_container_width=True,
    )


# ── Ingresos ──────────────────────────────────────────────────────────────────

elif categoria == "Ingresos":
    st.header("Ingresos del sector")

    df = load(InternetCSV.INGRESOS)
    DataValidator.validate(df, ["anio", "trimestre"])
    df = sort_by_periodo(add_periodo_col(df))

    value_col = next(
        (c for c in df.columns if "ingreso" in c or "miles" in c or "monto" in c), None
    )
    if value_col is None:
        st.warning("No se encontró columna de ingresos. Columnas: " + str(list(df.columns)))
        st.stop()

    val, delta = last_period_delta(df, value_col)
    show_kpis([{"label": "Ingresos (miles $)", "value": val,
                "delta": delta, "format": "{:,.0f}"}])

    st.divider()
    st.plotly_chart(
        bar_chart(df, x="periodo", y=value_col,
                  title="Ingresos por trimestre (miles de pesos)"),
        use_container_width=True,
    )


# ── En desarrollo ─────────────────────────────────────────────────────────────

else:
    st.info(f"La sección **{categoria}** está en desarrollo.", icon="🔧")