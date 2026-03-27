"""
2_Movil.py
──────────
Vista de Comunicaciones Móviles.
"""

import streamlit as st
import plotly.graph_objects as go

from config.constants import MovilCSV
from services.data_manager import DataManager, DataLoadError
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col, sort_by_periodo, filter_by_period,
    melt_tecnologias, last_period_delta,
)
from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.filters import render_header_with_range_filter, render_range_filter, render_period_filters
from components.charts import line_chart, bar_chart, area_chart


st.set_page_config(page_title="Móvil · ENACOM", page_icon="📱", layout="wide")
setup_page()

CATEGORIES = [
    "Resumen general",
    "Accesos",
    "Llamadas",
    "Minutos de voz",
    "SMS",
    "Penetración",
    "Ingresos",
]

categoria = render_sidebar(CATEGORIES, key="movil_categoria")
st.title("📱 Comunicaciones móviles")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


def split_prepago_pospago(df, value_name="Valor"):
    """Convierte pospago/prepago a formato largo para gráficos de series."""
    df_long = melt_tecnologias(
        df, ["pospago", "prepago"],
        id_col="periodo", var_name="Modalidad", value_name=value_name,
    )
    df_long["Modalidad"] = df_long["Modalidad"].map({
        "pospago": "Pospago",
        "prepago": "Prepago",
    })
    return df_long


# ── Resumen general ───────────────────────────────────────────────────────────

if categoria == "Resumen general":
    st.header("Resumen general")

    df_acc = load(MovilCSV.ACCESOS)
    df_ing = load(MovilCSV.INGRESOS)
    df_min = load(MovilCSV.MINUTOS)
    df_pen = load(MovilCSV.PENETRACION)

    for df, cols in [
        (df_acc, ["anio", "trimestre"]),
        (df_ing, ["anio", "trimestre"]),
        (df_min, ["anio", "trimestre"]),
        (df_pen, ["anio", "trimestre", "accesos_100_hab"]),
    ]:
        DataValidator.validate(df, cols)

    df_acc = sort_by_periodo(add_periodo_col(df_acc))
    df_ing = sort_by_periodo(add_periodo_col(df_ing))
    df_min = sort_by_periodo(add_periodo_col(df_min))
    df_pen = sort_by_periodo(add_periodo_col(df_pen))

    acc_col = next((c for c in df_acc.columns if "operativo" in c or "total" in c), df_acc.columns[-1])
    ing_col = next((c for c in df_ing.columns if "ingreso" in c or "miles" in c), df_ing.columns[-1])

    val_acc, delta_acc = last_period_delta(df_acc, acc_col)
    val_ing, delta_ing = last_period_delta(df_ing, ing_col)
    val_min, delta_min = last_period_delta(df_min, "total")
    val_pen, delta_pen = last_period_delta(df_pen, "accesos_100_hab")

    show_kpis([
        {"label": "Líneas operativas",   "value": val_acc, "delta": delta_acc,
         "format": "{:,.0f}"},
        {"label": "Ingresos (miles $)",  "value": val_ing, "delta": delta_ing,
         "format": "{:,.0f}"},
        {"label": "Minutos de voz",      "value": val_min, "delta": delta_min,
         "format": "{:,.0f}"},
        {"label": "Accesos c/100 hab.",  "value": val_pen, "delta": delta_pen,
         "format": "{:.2f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        fig = line_chart(df_acc, "periodo", acc_col,
                         title="Líneas operativas — evolución", markers=False)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = bar_chart(df_ing, "periodo", ing_col,
                        title="Ingresos por trimestre")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        df_min_long = split_prepago_pospago(df_min, "Minutos")
        fig = area_chart(df_min_long, "periodo", "Minutos", "Modalidad",
                         title="Minutos de voz — pospago vs prepago",
                         color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        fig = line_chart(df_pen, "periodo", "accesos_100_hab",
                         title="Penetración — accesos c/100 hab.", markers=False)
        st.plotly_chart(fig, use_container_width=True)


# ── Accesos ───────────────────────────────────────────────────────────────────

elif categoria == "Accesos":
    # st.header("Líneas móviles activas")

    df = load(MovilCSV.ACCESOS)
    DataValidator.validate(df, ["anio", "trimestre"])
    df = sort_by_periodo(add_periodo_col(df))

    # anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_acc")
    anio_desde, anio_hasta = render_header_with_range_filter("Líneas móviles activas", df, key_prefix="mov_acc")

    st.divider()
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    acc_col = next((c for c in df.columns if "operativo" in c or "total" in c), df.columns[-1])
    pre_col = next((c for c in df.columns if "prepago" in c), None)
    pos_col = next((c for c in df.columns if "pospago" in c), None)

    val_tot, delta_tot = last_period_delta(df_range, acc_col)

    kpis = [{"label": "Líneas operativas", "value": val_tot,
              "delta": delta_tot, "format": "{:,.0f}"}]
    if pos_col:
        val_pos, delta_pos = last_period_delta(df_range, pos_col)
        kpis.append({"label": "Pospago", "value": val_pos,
                     "delta": delta_pos, "format": "{:,.0f}"})
    if pre_col:
        val_pre, delta_pre = last_period_delta(df_range, pre_col)
        kpis.append({"label": "Prepago", "value": val_pre,
                     "delta": delta_pre, "format": "{:,.0f}"})

    show_kpis(kpis)
    st.divider()

    if pre_col and pos_col:
        df_long = split_prepago_pospago(df_range, "Líneas")
        tab1, tab2 = st.tabs(["Área apilada", "Líneas"])
        with tab1:
            fig = area_chart(df_long, "periodo", "Líneas", "Modalidad",
                             title="Líneas — pospago vs prepago",
                             color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            fig = line_chart(df_long, "periodo", "Líneas", "Modalidad",
                             title="Evolución pospago vs prepago",
                             color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
            st.plotly_chart(fig, use_container_width=True)
    else:
        fig = line_chart(df_range, "periodo", acc_col,
                         title="Líneas operativas — evolución", markers=True)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver datos"):
        st.dataframe(df_range, use_container_width=True)


# ── Llamadas ──────────────────────────────────────────────────────────────────

elif categoria == "Llamadas":
    st.header("Llamadas cursadas")

    df = load(MovilCSV.LLAMADAS)
    DataValidator.validate(df, ["anio", "trimestre", "pospago", "prepago", "total"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_llam")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    val_tot, delta_tot = last_period_delta(df_range, "total")
    val_pos, delta_pos = last_period_delta(df_range, "pospago")
    val_pre, delta_pre = last_period_delta(df_range, "prepago")
    pct_pos = val_pos / val_tot * 100 if val_tot else 0

    show_kpis([
        {"label": "Total llamadas",  "value": val_tot, "delta": delta_tot,
         "format": "{:,.0f}"},
        {"label": "Pospago",         "value": val_pos, "delta": delta_pos,
         "format": "{:,.0f}"},
        {"label": "Prepago",         "value": val_pre, "delta": delta_pre,
         "format": "{:,.0f}"},
        {"label": "% Pospago",       "value": pct_pos,
         "format": "{:.1f}%"},
    ])

    st.divider()

    df_long = split_prepago_pospago(df_range, "Llamadas")

    tab1, tab2, tab3 = st.tabs(["Área apilada", "Líneas", "Barras"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Llamadas", "Modalidad",
                         title="Llamadas — pospago vs prepago",
                         color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_long, "periodo", "Llamadas", "Modalidad",
                         title="Evolución de llamadas por modalidad",
                         color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = bar_chart(df_long, "periodo", "Llamadas", "Modalidad",
                        title="Llamadas por trimestre", barmode="stack",
                        color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Participación pospago sobre el total")
    df_range["pct_pospago"] = (df_range["pospago"] / df_range["total"] * 100).round(2)
    fig_pct = go.Figure(go.Scatter(
        x=df_range["periodo"], y=df_range["pct_pospago"],
        mode="lines+markers", fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
        marker={"size": 4},
    ))
    fig_pct.update_layout(
        title="% llamadas pospago sobre total",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
        hovermode="x unified",
    )
    st.plotly_chart(fig_pct, use_container_width=True)


# ── Minutos de voz ────────────────────────────────────────────────────────────

elif categoria == "Minutos de voz":
    st.header("Minutos de voz cursados")

    df = load(MovilCSV.MINUTOS)
    DataValidator.validate(df, ["anio", "trimestre", "pospago", "prepago", "total"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_min")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    val_tot, delta_tot = last_period_delta(df_range, "total")
    val_pos, delta_pos = last_period_delta(df_range, "pospago")
    val_pre, delta_pre = last_period_delta(df_range, "prepago")
    pct_pos = val_pos / val_tot * 100 if val_tot else 0

    show_kpis([
        {"label": "Total minutos",  "value": val_tot, "delta": delta_tot,
         "format": "{:,.0f}"},
        {"label": "Pospago",        "value": val_pos, "delta": delta_pos,
         "format": "{:,.0f}"},
        {"label": "Prepago",        "value": val_pre, "delta": delta_pre,
         "format": "{:,.0f}"},
        {"label": "% Pospago",      "value": pct_pos,
         "format": "{:.1f}%"},
    ])

    st.divider()

    df_long = split_prepago_pospago(df_range, "Minutos")

    tab1, tab2, tab3 = st.tabs(["Área apilada", "Líneas", "Barras"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Minutos", "Modalidad",
                         title="Minutos de voz — pospago vs prepago",
                         color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_long, "periodo", "Minutos", "Modalidad",
                         title="Evolución minutos por modalidad",
                         color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = bar_chart(df_long, "periodo", "Minutos", "Modalidad",
                        title="Minutos por trimestre", barmode="stack",
                        color_map={"Pospago": "#00B5E5", "Prepago": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Participación pospago sobre el total")
    df_range["pct_pospago"] = (df_range["pospago"] / df_range["total"] * 100).round(2)
    fig_pct = go.Figure(go.Scatter(
        x=df_range["periodo"], y=df_range["pct_pospago"],
        mode="lines+markers", fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
        marker={"size": 4},
    ))
    fig_pct.update_layout(
        title="% minutos pospago sobre total",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
        hovermode="x unified",
    )
    st.plotly_chart(fig_pct, use_container_width=True)


# ── SMS ───────────────────────────────────────────────────────────────────────

elif categoria == "SMS":
    st.header("Mensajes de texto (SMS)")

    df = load(MovilCSV.SMS)
    DataValidator.validate(df, ["anio", "trimestre"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_sms")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    sms_col = next((c for c in df.columns if "sms" in c or "mensaje" in c or "total" in c),
                   df.columns[-1])
    val, delta = last_period_delta(df_range, sms_col)

    show_kpis([{"label": "SMS enviados (miles)", "value": val,
                "delta": delta, "format": "{:,.0f}"}])
    st.divider()

    tab1, tab2 = st.tabs(["Línea", "Barras"])
    with tab1:
        fig = line_chart(df_range, "periodo", sms_col,
                         title="SMS — evolución histórica", markers=False)
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = bar_chart(df_range, "periodo", sms_col, title="SMS por trimestre")
        st.plotly_chart(fig, use_container_width=True)


# ── Penetración ───────────────────────────────────────────────────────────────

elif categoria == "Penetración":
    st.header("Penetración de telefonía móvil")

    df = load(MovilCSV.PENETRACION)
    DataValidator.validate(df, ["anio", "trimestre", "accesos_100_hab"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_pen")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    val, delta    = last_period_delta(df_range, "accesos_100_hab")
    val_max       = df_range["accesos_100_hab"].max()
    periodo_max   = df_range.loc[df_range["accesos_100_hab"].idxmax(), "periodo"]
    val_inicio    = df_range["accesos_100_hab"].iloc[0]
    variacion_acum = (val - val_inicio) / val_inicio * 100 if val_inicio else None

    show_kpis([
        {"label": "Accesos c/100 hab. (último)",
         "value": val, "delta": delta, "format": "{:.2f}"},
        {"label": f"Máximo histórico ({periodo_max})",
         "value": val_max, "format": "{:.2f}"},
        {"label": "Variación acumulada",
         "value": variacion_acum or 0, "format": "{:+.1f}%",
         "help": f"Variación desde {anio_desde} hasta {anio_hasta}"},
    ])

    st.divider()
    st.caption("Valores superiores a 100 indican múltiples SIMs por persona.")

    fig = go.Figure()
    fig.add_hline(y=100, line_dash="dot", line_color="#C6C6C6", line_width=1,
                  annotation_text="100 accesos/100 hab.", annotation_position="top right")
    fig.add_trace(go.Scatter(
        x=df_range["periodo"], y=df_range["accesos_100_hab"],
        mode="lines+markers", fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
        marker={"size": 4},
        name="Accesos c/100 hab.",
    ))
    fig.update_layout(
        title="Penetración de telefonía móvil (accesos cada 100 habitantes)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"gridcolor": "#E8E8E8"},
        hovermode="x unified",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Variación interanual")
    df_yoy = df_range.copy()
    df_yoy["yoy"] = df_yoy["accesos_100_hab"].pct_change(4) * 100
    df_yoy = df_yoy.dropna(subset=["yoy"])

    fig_yoy = go.Figure(go.Bar(
        x=df_yoy["periodo"],
        y=df_yoy["yoy"].round(2),
        marker_color=["#00B5E5" if v >= 0 else "#E74242" for v in df_yoy["yoy"]],
    ))
    fig_yoy.update_layout(
        title="Variación interanual (%)",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"size": 12},
        margin={"t": 40, "b": 40, "l": 40, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
        showlegend=False,
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(df_range[["anio", "trimestre", "periodo", "accesos_100_hab"]],
                     use_container_width=True)
        

# ── Ingresos ──────────────────────────────────────────────────────────────────

elif categoria == "Ingresos":
    st.header("Ingresos del sector móvil")

    df = load(MovilCSV.INGRESOS)
    DataValidator.validate(df, ["anio", "trimestre"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="mov_ing")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    ing_col = next((c for c in df.columns if "ingreso" in c or "miles" in c), df.columns[-1])
    val, delta = last_period_delta(df_range, ing_col)

    show_kpis([{"label": "Ingresos (miles $)", "value": val,
                "delta": delta, "format": "{:,.0f}"}])
    st.divider()

    tab1, tab2 = st.tabs(["Barras", "Línea"])
    with tab1:
        fig = bar_chart(df_range, "periodo", ing_col, title="Ingresos por trimestre")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_range, "periodo", ing_col,
                         title="Ingresos — evolución", markers=False)
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver datos"):
        st.dataframe(df_range, use_container_width=True)