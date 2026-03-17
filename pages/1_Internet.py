"""
1_Internet.py
─────────────
Vista de Internet Fijo.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.constants import (
    InternetCSV, TECNOLOGIAS_COLS, TECNOLOGIAS_LABELS,
    VELOCIDAD_RANGOS_COLS, VELOCIDAD_RANGOS_LABELS,
)
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
from components.filters import render_period_filters, render_range_filter, render_period_and_provincia_filters   # ← nuevo
from components.charts import line_chart, bar_chart, area_chart


st.set_page_config(page_title="Internet · ENACOM", page_icon="🌐", layout="wide")
setup_page()

CATEGORIES = [
    "Resumen general",
    "Tecnología",
    "Tecnología - provincia",
    "Velocidad media",
    "Velocidad media - provincia",
    "Rangos de velocidad",
    "Rangos de velocidad - provincia",
    "Banda ancha vs Dial-up",
    "Banda ancha - provincia",
    "Penetración",
    "Penetración - provincia",
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


# ── Banda ancha vs Dial-up ───────────────────────────────────────────────────
 
elif categoria == "Banda ancha vs Dial-up":
    st.header("Banda ancha fija vs Dial-up")
 
    df = load(InternetCSV.BANDA_ANCHA_DIALUP)
    DataValidator.validate(df, ["anio", "trimestre", "banda_ancha_fija", "dial_up", "total"])
    df = sort_by_periodo(add_periodo_col(df))
 
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="baf")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()
 
    baf_actual, delta_baf   = last_period_delta(df_range, "banda_ancha_fija")
    dup_actual, delta_dup   = last_period_delta(df_range, "dial_up")
    tot_actual, delta_tot   = last_period_delta(df_range, "total")
    pct_baf = baf_actual / tot_actual * 100 if tot_actual else 0
 
    show_kpis([
        {"label": "Banda ancha fija",  "value": baf_actual, "delta": delta_baf,
         "format": "{:,.0f}"},
        {"label": "Dial-up",           "value": dup_actual, "delta": delta_dup,
         "format": "{:,.0f}"},
        {"label": "Total",             "value": tot_actual, "delta": delta_tot,
         "format": "{:,.0f}"},
        {"label": "% Banda ancha",     "value": pct_baf,
         "format": "{:.2f}%",
         "help": "Proporción de banda ancha sobre el total de accesos"},
    ])
 
    st.divider()
 
    df_long = melt_tecnologias(
        df_range, ["banda_ancha_fija", "dial_up"],
        id_col="periodo", var_name="Tipo", value_name="Accesos",
    )
    df_long["Tipo"] = df_long["Tipo"].map({
        "banda_ancha_fija": "Banda ancha fija",
        "dial_up": "Dial-up",
    })
 
    tab1, tab2, tab3 = st.tabs(["Área apilada", "Líneas", "Barras"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Accesos", "Tipo",
                         title="Evolución banda ancha vs dial-up",
                         color_map={"Banda ancha fija": "#00B5E5", "Dial-up": "#C6C6C6"})
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_long, "periodo", "Accesos", "Tipo",
                         title="Evolución banda ancha vs dial-up",
                         color_map={"Banda ancha fija": "#00B5E5", "Dial-up": "#C6C6C6"})
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = bar_chart(df_long, "periodo", "Accesos", "Tipo",
                        title="Banda ancha vs dial-up por trimestre",
                        barmode="stack",
                        color_map={"Banda ancha fija": "#00B5E5", "Dial-up": "#C6C6C6"})
        st.plotly_chart(fig, use_container_width=True)
 
    # Evolución del porcentaje BA
    st.subheader("Participación de banda ancha sobre el total")
    df_range["pct_baf"] = (df_range["banda_ancha_fija"] / df_range["total"] * 100).round(2)

    fig_pct = go.Figure(go.Scatter(
        x=df_range["periodo"], y=df_range["pct_baf"],
        mode="lines+markers", fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
        marker={"size": 4},
    ))
    fig_pct.update_layout(
        title="% Banda ancha sobre total de accesos",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8", "range": [95, 101]},
        hovermode="x unified",
    )
    st.plotly_chart(fig_pct, use_container_width=True)
 

# ── Rangos de velocidad ───────────────────────────────────────────────────────
 
elif categoria == "Rangos de velocidad":
    st.header("Accesos por rangos de velocidad")
 
    df = load(InternetCSV.VELOCIDAD_RANGOS)
    DataValidator.validate(df, ["anio", "trimestre"] + VELOCIDAD_RANGOS_COLS)
    df = sort_by_periodo(add_periodo_col(df))
 
    anio_desde, anio_hasta = render_range_filter(df, key_prefix="vrang")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()
 
    # KPIs: último período
    ultimo = df_range.iloc[-1]
    total_acc  = ultimo["total"] if "total" in df_range.columns else df_range[VELOCIDAD_RANGOS_COLS].iloc[-1].sum()
    alta_vel   = ultimo["mayor_30mbps"]
    baja_vel   = ultimo["hasta_512_kbps"] + ultimo.get("entre_512_1mbps", 0)
    pct_alta   = alta_vel / total_acc * 100 if total_acc else 0
 
    show_kpis([
        {"label": "Total accesos",    "value": total_acc, "format": "{:,.0f}"},
        {"label": "+30 Mbps",         "value": alta_vel,  "format": "{:,.0f}"},
        {"label": "% sobre +30 Mbps", "value": pct_alta,  "format": "{:.1f}%",
         "help": "Proporción de accesos con velocidad mayor a 30 Mbps"},
        {"label": "Hasta 1 Mbps",     "value": baja_vel,  "format": "{:,.0f}"},
    ])
 
    st.divider()
 
    df_long = melt_tecnologias(
        df_range, VELOCIDAD_RANGOS_COLS,
        id_col="periodo", var_name="Rango", value_name="Accesos",
    )
    df_long["Rango"] = df_long["Rango"].map(VELOCIDAD_RANGOS_LABELS)
 
    # Orden de menor a mayor velocidad
    orden_rangos = list(VELOCIDAD_RANGOS_LABELS.values())
    df_long["Rango"] = pd.Categorical(df_long["Rango"], categories=orden_rangos, ordered=True)
    df_long = df_long.sort_values(["periodo", "Rango"])  # cronológico primero, rango segundo
 
    tab1, tab2, tab3 = st.tabs(["Área apilada", "Barras", "Líneas"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Accesos", "Rango",
                         title="Evolución por rangos de velocidad")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = bar_chart(df_long, "periodo", "Accesos", "Rango",
                        title="Accesos por rango de velocidad", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = line_chart(df_long, "periodo", "Accesos", "Rango",
                         title="Evolución por rango de velocidad")
        st.plotly_chart(fig, use_container_width=True)
 
    # Distribución en el último período (torta)
    st.subheader(f"Distribución — {df_range['periodo'].iloc[-1]}")
    ultimo_dist = df_range[VELOCIDAD_RANGOS_COLS].iloc[-1].rename(VELOCIDAD_RANGOS_LABELS)
    df_pie = ultimo_dist.reset_index()
    df_pie.columns = ["Rango", "Accesos"]
    df_pie = df_pie[df_pie["Accesos"] > 0]
 
    fig_pie = px.pie(df_pie, names="Rango", values="Accesos",
                            hole=0.4, title=f"Composición por rango — {df_range['periodo'].iloc[-1]}")
    fig_pie.update_layout(margin={"t": 50, "b": 0, "l": 0, "r": 0})
    st.plotly_chart(fig_pie, use_container_width=True)
 

# ── Penetración ───────────────────────────────────────────────────────────────

elif categoria == "Penetración":
    st.header("Penetración de Internet fijo")

    df = load(InternetCSV.PENETRACION)
    DataValidator.validate(df, ["anio", "trimestre",
                                "accesos_cada_100_hogares",
                                "accesos_cada_100_habitantes"])

    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="pen")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    hog_actual, delta_hog = last_period_delta(df_range, "accesos_cada_100_hogares")
    hab_actual, delta_hab = last_period_delta(df_range, "accesos_cada_100_habitantes")

    hog_inicio = df_range["accesos_cada_100_hogares"].iloc[0]
    hab_inicio = df_range["accesos_cada_100_habitantes"].iloc[0]
    crec_hog = (hog_actual - hog_inicio) / hog_inicio * 100 if hog_inicio else None
    crec_hab = (hab_actual - hab_inicio) / hab_inicio * 100 if hab_inicio else None

    show_kpis([
        {"label": "Accesos c/100 hogares",    "value": hog_actual,
         "delta": delta_hog, "format": "{:.2f}",
         "help": "Accesos a internet fijo cada 100 hogares"},
        {"label": "Accesos c/100 habitantes", "value": hab_actual,
         "delta": delta_hab, "format": "{:.2f}",
         "help": "Accesos a internet fijo cada 100 habitantes"},
        {"label": "Crecimiento hogares",      "value": crec_hog or 0,
         "format": "{:+.1f}%",
         "help": f"Variación acumulada en el rango {anio_desde}–{anio_hasta}"},
        {"label": "Crecimiento hab.",         "value": crec_hab or 0,
         "format": "{:+.1f}%",
         "help": f"Variación acumulada en el rango {anio_desde}–{anio_hasta}"},
    ])

    st.divider()

    # ── Gráfico doble eje Y ───────────────────────────────────────────────────
    st.subheader("Evolución histórica")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_range["periodo"],
        y=df_range["accesos_cada_100_hogares"],
        name="c/100 hogares",
        mode="lines+markers",
        marker={"size": 4},
        line={"color": "#00B5E5", "width": 2},
        fill="tozeroy",
        fillcolor="rgba(0,181,229,0.06)",
        yaxis="y1",
    ))

    fig.add_trace(go.Scatter(
        x=df_range["periodo"],
        y=df_range["accesos_cada_100_habitantes"],
        name="c/100 habitantes",
        mode="lines+markers",
        marker={"size": 4},
        line={"color": "#EEAE42", "width": 2},
        fill="tozeroy",
        fillcolor="rgba(238,174,66,0.06)",
        yaxis="y2",
    ))

    fig.update_layout(
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin={"t": 40, "b": 40, "l": 48, "r": 60},
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        yaxis=dict(
            title=dict(text="c/100 hogares", font={"color": "#00B5E5"}),
            tickfont={"color": "#00B5E5"},
            showgrid=True,
            gridcolor="#E8E8E8",
        ),
        yaxis2=dict(
            title=dict(text="c/100 habitantes", font={"color": "#EEAE42"}),
            tickfont={"color": "#EEAE42"},
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Crecimiento interanual ────────────────────────────────────────────────
    st.subheader("Variación interanual")

    df_yoy = df_range.copy()
    df_yoy["hog_yoy"] = df_yoy["accesos_cada_100_hogares"].pct_change(4) * 100
    df_yoy["hab_yoy"] = df_yoy["accesos_cada_100_habitantes"].pct_change(4) * 100
    df_yoy = df_yoy.dropna(subset=["hog_yoy"])

    col1, col2 = st.columns(2)
    with col1:
        fig_yoy1 = go.Figure(go.Bar(
            x=df_yoy["periodo"],
            y=df_yoy["hog_yoy"].round(2),
            marker_color=[
                "#00B5E5" if v >= 0 else "#E74242"
                for v in df_yoy["hog_yoy"]
            ],
            name="c/100 hogares",
        ))
        fig_yoy1.update_layout(
            title="Var. interanual — hogares (%)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font={"size": 12},
            margin={"t": 40, "b": 40, "l": 40, "r": 20},
            yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
            showlegend=False,
        )
        st.plotly_chart(fig_yoy1, use_container_width=True)

    with col2:
        fig_yoy2 = go.Figure(go.Bar(
            x=df_yoy["periodo"],
            y=df_yoy["hab_yoy"].round(2),
            marker_color=[
                "#EEAE42" if v >= 0 else "#E74242"
                for v in df_yoy["hab_yoy"]
            ],
            name="c/100 habitantes",
        ))
        fig_yoy2.update_layout(
            title="Var. interanual — habitantes (%)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font={"size": 12},
            margin={"t": 40, "b": 40, "l": 40, "r": 20},
            yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
            showlegend=False,
        )
        st.plotly_chart(fig_yoy2, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range[["anio", "trimestre", "periodo",
                       "accesos_cada_100_hogares",
                       "accesos_cada_100_habitantes"]],
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


# ── Separador de sección (no es una categoría seleccionable) ──────────────────

elif categoria == "── Por provincia ──":
    st.info("Seleccioná una sección provincial en el menú lateral.", icon="👈")


# ═══════════════════════════════════════════════════════════════════════════════
# SECCIONES POR PROVINCIA
# ═══════════════════════════════════════════════════════════════════════════════

elif categoria == "Tecnología - provincia":
    st.header("Accesos por tecnología — por provincia")

    df = load(InternetCSV.TECNOLOGIAS_PROVINCIA)
    DataValidator.validate(df, ["anio", "trimestre", "provincia"] + TECNOLOGIAS_COLS + ["total"])

    anio, trimestre = render_period_filters(df, key_prefix="prov_tec")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()

    # ── KPIs del período ──────────────────────────────────────────────────────
    total_nac = df_periodo["total"].sum()
    fibra_nac = df_periodo["fibra_optica"].sum()
    cable_nac = df_periodo["cablemodem"].sum()
    adsl_nac  = df_periodo["adsl"].sum()

    show_kpis([
        {"label": "Total nacional",  "value": total_nac, "format": "{:,.0f}"},
        {"label": "Fibra óptica",    "value": fibra_nac, "format": "{:,.0f}"},
        {"label": "Cablemodem",      "value": cable_nac, "format": "{:,.0f}"},
        {"label": "ADSL",            "value": adsl_nac,  "format": "{:,.0f}"},
    ])

    st.divider()

    # ── Ranking de provincias por total ───────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Ranking por accesos totales")
        df_rank = df_periodo[["provincia", "total"]].sort_values("total", ascending=True)
        fig_rank = bar_chart(
            df_rank, x="total", y="provincia",
            title=f"Accesos totales por provincia — {anio} T{trimestre}",
        )
        fig_rank.update_layout(
            height=650,
            yaxis={"categoryorder": "total ascending"},
            xaxis={"tickformat": ",.0f"},
        )
        fig_rank.update_traces(marker_color="#00B5E5", orientation="h")
        st.plotly_chart(fig_rank, use_container_width=True)

    with col2:
        st.subheader("Composición por tecnología")
        df_long = melt_tecnologias(
            df_periodo, TECNOLOGIAS_COLS,
            id_col="provincia", var_name="Tecnología", value_name="Accesos",
        )
        df_long["Tecnología"] = df_long["Tecnología"].map(TECNOLOGIAS_LABELS)
        df_long = df_long.merge(
            df_periodo[["provincia","total"]], on="provincia"
        ).sort_values("total", ascending=False)

        fig_comp = bar_chart(
            df_long, x="Accesos", y="provincia",
            color="Tecnología", barmode="stack",
            title=f"Composición por tecnología — {anio} T{trimestre}",
        )
        from config.theme import COLORS
        fig_comp.update_layout(
            height=650,
            yaxis={"categoryorder": "total ascending"},
            xaxis={"tickformat": ",.0f"},
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    st.divider()

    # ── Evolución de una provincia ────────────────────────────────────────────
    st.subheader("Evolución histórica por provincia")

    provincias = sorted(df["provincia"].unique())
    prov_sel = st.selectbox("Seleccionar provincia", provincias, key="prov_tec_evol")

    df_prov = df[df["provincia"] == prov_sel].copy()
    df_prov = sort_by_periodo(add_periodo_col(df_prov))
    df_long_evol = melt_tecnologias(df_prov, TECNOLOGIAS_COLS)
    df_long_evol["Tecnología"] = df_long_evol["Tecnología"].map(TECNOLOGIAS_LABELS)

    tab1, tab2 = st.tabs(["Líneas", "Área apilada"])
    with tab1:
        st.plotly_chart(
            line_chart(df_long_evol, "periodo", "Accesos", "Tecnología",
                       title=f"{prov_sel} — evolución por tecnología"),
            use_container_width=True,
        )
    with tab2:
        st.plotly_chart(
            area_chart(df_long_evol, "periodo", "Accesos", "Tecnología",
                       title=f"{prov_sel} — composición en el tiempo"),
            use_container_width=True,
        )


# ── Velocidad media - provincia ───────────────────────────────────────────────────

elif categoria == "Velocidad media - provincia":
    st.header("Velocidad media de descarga — por provincia")

    df = load(InternetCSV.VELOCIDAD_MEDIA_PROVINCIA)
    DataValidator.validate(df, ["anio", "trimestre", "provincia", "mbps"])

    anio, trimestre = render_period_filters(df, key_prefix="prov_vel")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()

    top = df_periodo.nlargest(1, "mbps").iloc[0]
    low = df_periodo.nsmallest(1, "mbps").iloc[0]

    show_kpis([
        {"label": f"Mayor velocidad ({top['provincia']})",
         "value": top["mbps"], "format": "{:.1f} Mbps"},
        {"label": f"Menor velocidad ({low['provincia']})",
         "value": low["mbps"], "format": "{:.1f} Mbps"},
        {"label": "Promedio nacional",
         "value": df_periodo["mbps"].mean(), "format": "{:.1f} Mbps"},
        {"label": "Diferencia máx–mín",
         "value": top["mbps"] - low["mbps"], "format": "{:.1f} Mbps"},
    ])

    st.divider()

    st.subheader("Ranking por velocidad media")
    df_rank = df_periodo[["provincia","mbps"]].sort_values("mbps", ascending=True)
    fig = bar_chart(df_rank, x="mbps", y="provincia",
                    title=f"Velocidad media por provincia — {anio} T{trimestre}")
    fig.update_layout(
        height=650,
        yaxis={"categoryorder": "total ascending"},
        xaxis={"ticksuffix": " Mbps"},
    )
    fig.update_traces(marker_color="#00B5E5", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Evolución multi-provincia ─────────────────────────────────────────────
    st.subheader("Comparar evolución entre provincias")

    provincias = sorted(df["provincia"].unique())
    prov_multi = st.multiselect(
        "Seleccionar provincias",
        provincias,
        default=["Buenos Aires", "CABA", "Córdoba", "Santa Fe"],
        key="prov_vel_multi",
    )

    if prov_multi:
        df_multi = df[df["provincia"].isin(prov_multi)].copy()
        df_multi = sort_by_periodo(add_periodo_col(df_multi))
        fig = line_chart(
            df_multi, x="periodo", y="mbps", color="provincia",
            title="Velocidad media — comparativa entre provincias",
            labels={"mbps": "Mbps"},
        )
        st.plotly_chart(fig, use_container_width=True)


# ── Banda ancha - provincia ───────────────────────────────────────────────────────

elif categoria == "Banda ancha - provincia":
    st.header("Banda ancha fija vs Dial-up — por provincia")

    df = load(InternetCSV.BAF_PROVINCIA)
    DataValidator.validate(df, ["anio", "trimestre", "provincia",
                                "banda_ancha_fija", "dial_up", "total"])

    anio, trimestre = render_period_filters(df, key_prefix="prov_baf")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()
    df_periodo["pct_banda_ancha"] = (
        df_periodo["banda_ancha_fija"] / df_periodo["total"] * 100
    ).round(2)

    top_baf = df_periodo.nlargest(1, "pct_banda_ancha").iloc[0]
    low_baf = df_periodo.nsmallest(1, "pct_banda_ancha").iloc[0]

    show_kpis([
        {"label": "Banda ancha total",  "value": df_periodo["banda_ancha_fija"].sum(),
         "format": "{:,.0f}"},
        {"label": "Dial-up total",      "value": df_periodo["dial_up"].sum(),
         "format": "{:,.0f}"},
        {"label": f"Mayor % BA ({top_baf['provincia']})",
         "value": top_baf["pct_banda_ancha"], "format": "{:.1f}%"},
        {"label": f"Menor % BA ({low_baf['provincia']})",
         "value": low_baf["pct_banda_ancha"], "format": "{:.1f}%"},
    ])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Banda ancha por provincia")
        df_rank = df_periodo[["provincia","banda_ancha_fija"]].sort_values(
            "banda_ancha_fija", ascending=True
        )
        fig = bar_chart(df_rank, x="banda_ancha_fija", y="provincia",
                        title=f"Accesos banda ancha — {anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"},
                          xaxis={"tickformat": ",.0f"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("% Banda ancha sobre total")
        df_pct = df_periodo[["provincia","pct_banda_ancha"]].sort_values(
            "pct_banda_ancha", ascending=True
        )
        fig = bar_chart(df_pct, x="pct_banda_ancha", y="provincia",
                        title=f"Proporción banda ancha — {anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"},
                          xaxis={"ticksuffix": "%"})
        fig.update_traces(marker_color="#ACAE22", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Evolución de una provincia ────────────────────────────────────────────
    st.subheader("Evolución banda ancha vs dial-up")

    provincias = sorted(df["provincia"].unique())
    prov_sel = st.selectbox("Seleccionar provincia", provincias, key="prov_baf_evol")

    df_prov = sort_by_periodo(add_periodo_col(
        df[df["provincia"] == prov_sel].copy()
    ))
    df_long = melt_tecnologias(
        df_prov, ["banda_ancha_fija", "dial_up"],
        id_col="periodo", var_name="Tipo", value_name="Accesos",
    )
    df_long["Tipo"] = df_long["Tipo"].map({
        "banda_ancha_fija": "Banda ancha fija",
        "dial_up": "Dial-up",
    })
    fig = area_chart(df_long, "periodo", "Accesos", "Tipo",
                     title=f"{prov_sel} — evolución banda ancha vs dial-up",
                     color_map={"Banda ancha fija": "#00B5E5", "Dial-up": "#C6C6C6"})
    st.plotly_chart(fig, use_container_width=True)


# ── Rangos de velocidad - provincia ──────────────────────────────────────────

elif categoria == "Rangos de velocidad - provincia":
    st.header("Rangos de velocidad — por provincia")

    df = load(InternetCSV.VELOCIDAD_RANGOS_PROVINCIA)
    df = sort_by_periodo(add_periodo_col(df))

    # El CSV provincial usa "hasta_512kbps" (sin guión), el nacional "hasta_512_kbps"
    # Lo normalizamos para que coincida con VELOCIDAD_RANGOS_COLS y VELOCIDAD_RANGOS_LABELS
    df = df.rename(columns={"hasta_512kbps": "hasta_512_kbps"})

    DataValidator.validate(df, ["anio", "trimestre", "provincia"] + VELOCIDAD_RANGOS_COLS)

    anio, trimestre = render_period_filters(df, key_prefix="prov_vrang")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()
    df_periodo["pct_alta_vel"] = (
        df_periodo["mayor_30mbps"] / df_periodo["total"] * 100
    ).round(2)

    # ── KPIs ─────────────────────────────────────────────────────────────────
    top = df_periodo.nlargest(1, "pct_alta_vel").iloc[0]
    low = df_periodo.nsmallest(1, "pct_alta_vel").iloc[0]

    show_kpis([
        {"label": f"Mayor % +30 Mbps ({top['provincia']})",
         "value": top["pct_alta_vel"], "format": "{:.1f}%"},
        {"label": f"Menor % +30 Mbps ({low['provincia']})",
         "value": low["pct_alta_vel"], "format": "{:.1f}%"},
        {"label": "Promedio nacional +30 Mbps",
         "value": df_periodo["pct_alta_vel"].mean(), "format": "{:.1f}%"},
        {"label": "Total accesos nacionales",
         "value": df_periodo["total"].sum(), "format": "{:,.0f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("% accesos +30 Mbps por provincia")
        df_rank = df_periodo[["provincia", "pct_alta_vel"]].sort_values(
            "pct_alta_vel", ascending=True
        )
        fig = bar_chart(df_rank, x="pct_alta_vel", y="provincia",
                        title=f"% accesos >30 Mbps — {anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"},
                          xaxis={"ticksuffix": "%"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Composición de rangos por provincia")
        df_long = melt_tecnologias(
            df_periodo, VELOCIDAD_RANGOS_COLS,
            id_col="provincia", var_name="Rango", value_name="Accesos",
        )
        df_long["Rango"] = df_long["Rango"].map(VELOCIDAD_RANGOS_LABELS)
        df_long = df_long.merge(
            df_periodo[["provincia", "total"]], on="provincia"
        ).sort_values("total", ascending=False)

        fig = bar_chart(df_long, x="Accesos", y="provincia",
                        color="Rango", barmode="stack",
                        title=f"Distribución por rango — {anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"},
                          xaxis={"tickformat": ",.0f"})
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Evolución histórica de una provincia ─────────────────────────────────
    st.subheader("Evolución histórica por provincia")

    provincias = sorted(df["provincia"].unique())
    prov_sel = st.selectbox("Seleccionar provincia", provincias, key="prov_vrang_evol")

    df_prov = sort_by_periodo(add_periodo_col(
        df[df["provincia"] == prov_sel].copy()
    ))
    df_long_evol = melt_tecnologias(
        df_prov, VELOCIDAD_RANGOS_COLS,
        id_col="periodo", var_name="Rango", value_name="Accesos",
    )
    df_long_evol["Rango"] = df_long_evol["Rango"].map(VELOCIDAD_RANGOS_LABELS)
    orden_rangos = list(VELOCIDAD_RANGOS_LABELS.values())
    df_long_evol["Rango"] = pd.Categorical(
        df_long_evol["Rango"], categories=orden_rangos, ordered=True
    )
    df_long_evol = df_long_evol.sort_values(["periodo", "Rango"])

    tab1, tab2 = st.tabs(["Área apilada", "Barras"])
    with tab1:
        fig = area_chart(df_long_evol, "periodo", "Accesos", "Rango",
                         title=f"{prov_sel} — evolución por rangos de velocidad")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = bar_chart(df_long_evol, "periodo", "Accesos", "Rango",
                        title=f"{prov_sel} — rangos de velocidad", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)


# ── Penetración - provincia ───────────────────────────────────────────────────────

elif categoria == "Penetración - provincia":
    st.header("Penetración de Internet — por provincia")

    df = load(InternetCSV.PENETRACION_PROVINCIA)
    DataValidator.validate(df, ["anio", "trimestre", "provincia",
                                "accesos_cada_100_hogares",
                                "accesos_cada_100_habitantes"])

    anio, trimestre = render_period_filters(df, key_prefix="prov_pen")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()

    # ── KPIs: líderes ─────────────────────────────────────────────────────────
    top_hog = df_periodo.nlargest(1, "accesos_cada_100_hogares").iloc[0]
    top_hab = df_periodo.nlargest(1, "accesos_cada_100_habitantes").iloc[0]
    low_hog = df_periodo.nsmallest(1, "accesos_cada_100_hogares").iloc[0]

    show_kpis([
        {"label": f"Mayor penetración hogares ({top_hog['provincia']})",
         "value": top_hog["accesos_cada_100_hogares"], "format": "{:.2f}"},
        {"label": f"Mayor penetración hab. ({top_hab['provincia']})",
         "value": top_hab["accesos_cada_100_habitantes"], "format": "{:.2f}"},
        {"label": f"Menor penetración hogares ({low_hog['provincia']})",
         "value": low_hog["accesos_cada_100_hogares"], "format": "{:.2f}"},
        {"label": "Promedio nacional (hogares)",
         "value": df_periodo["accesos_cada_100_hogares"].mean(), "format": "{:.2f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ranking — c/100 hogares")
        df_hog = df_periodo[["provincia","accesos_cada_100_hogares"]].sort_values(
            "accesos_cada_100_hogares", ascending=True
        )
        fig = bar_chart(df_hog, x="accesos_cada_100_hogares", y="provincia",
                        title=f"{anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Ranking — c/100 habitantes")
        df_hab = df_periodo[["provincia","accesos_cada_100_habitantes"]].sort_values(
            "accesos_cada_100_habitantes", ascending=True
        )
        fig = bar_chart(df_hab, x="accesos_cada_100_habitantes", y="provincia",
                        title=f"{anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#EEAE42", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Evolución de provincia vs nacional ────────────────────────────────────
    st.subheader("Evolución provincia vs promedio nacional")

    provincias = sorted(df["provincia"].unique())
    prov_sel = st.selectbox("Seleccionar provincia", provincias, key="prov_pen_evol")

    df_prov = sort_by_periodo(add_periodo_col(
        df[df["provincia"] == prov_sel].copy()
    ))
    df_nac = sort_by_periodo(add_periodo_col(
        df.groupby(["anio","trimestre"])["accesos_cada_100_hogares"].mean().reset_index()
    ))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_prov["periodo"], y=df_prov["accesos_cada_100_hogares"],
        name=prov_sel, mode="lines+markers",
        line={"color": "#00B5E5", "width": 2}, marker={"size": 4},
    ))
    fig.add_trace(go.Scatter(
        x=df_nac["periodo"], y=df_nac["accesos_cada_100_hogares"].round(2),
        name="Promedio nacional", mode="lines",
        line={"color": "#C6C6C6", "width": 1.5, "dash": "dot"},
    ))
    fig.update_layout(
        title=f"{prov_sel} vs promedio nacional — accesos c/100 hogares",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.02},
        yaxis={"gridcolor": "#E8E8E8"},
    )
    st.plotly_chart(fig, use_container_width=True)


# ── En desarrollo ─────────────────────────────────────────────────────────────

else:
    st.info(f"La sección **{categoria}** está en desarrollo.", icon="🔧")