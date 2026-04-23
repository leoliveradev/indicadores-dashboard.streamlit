import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config.endpoints import TVEndpoints
from services.data_manager import DataManager, DataLoadError
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col, sort_by_periodo, filter_by_period,
    melt_tecnologias, last_period_delta,
)
from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.filters import render_range_filter, render_period_filters
from components.charts import line_chart, bar_chart, area_chart


st.set_page_config(page_title="TV Paga · ENACOM", page_icon="📺", layout="wide")
setup_page()

CATEGORIES = [
    "Resumen general",
    "Accesos",
    "Accesos - provincia",
    "Penetración",
    "Penetración - provincia",
    "Ingresos",
]

categoria = render_sidebar(CATEGORIES, key="tv_categoria")
st.title("📺 Televisión por suscripción")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


def split_tipo(df, value_name="Valor"):
    """Convierte tv_suscripcion / tv_satelital a formato largo."""
    df_long = melt_tecnologias(
        df, ["tv_suscripcion", "tv_satelital"],
        id_col="periodo", var_name="Tipo", value_name=value_name,
    )
    df_long["Tipo"] = df_long["Tipo"].map({
        "tv_suscripcion": "TV suscripción",
        "tv_satelital":   "TV satelital",
    })
    return df_long


# ── Resumen general ───────────────────────────────────────────────────────────

if categoria == "Resumen general":
    st.header("Resumen general")

    df_acc = load(TVEndpoints.ACCESOS)
    df_ing = load(TVEndpoints.INGRESOS)
    df_pen = load(TVEndpoints.PENETRACION)

    for df, cols in [
        (df_acc, ["anio", "trimestre", "tv_suscripcion", "tv_satelital"]),
        (df_ing, ["anio", "trimestre", "tv_suscripcion", "tv_satelital"]),
        (df_pen, ["anio", "trimestre",
                  "tv_suscripcion_100_habitantes", "tv_suscripcion_100_hogares"]),
    ]:
        DataValidator.validate(df, cols)

    df_acc = sort_by_periodo(add_periodo_col(df_acc))
    df_ing = sort_by_periodo(add_periodo_col(df_ing))
    df_pen = sort_by_periodo(add_periodo_col(df_pen))

    val_sus, delta_sus = last_period_delta(df_acc, "tv_suscripcion")
    val_sat, delta_sat = last_period_delta(df_acc, "tv_satelital")
    ing_sus, delta_ing = last_period_delta(df_ing, "tv_suscripcion")
    pen_hog, delta_pen = last_period_delta(df_pen, "tv_suscripcion_100_hogares")

    show_kpis([
        {"label": "TV suscripción",      "value": val_sus, "delta": delta_sus,
         "format": "{:,.0f}"},
        {"label": "TV satelital",        "value": val_sat, "delta": delta_sat,
         "format": "{:,.0f}"},
        {"label": "Ingresos suscripción (miles $)", "value": ing_sus, "delta": delta_ing,
         "format": "{:,.0f}"},
        {"label": "Penetración c/100 hogares",      "value": pen_hog, "delta": delta_pen,
         "format": "{:.2f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        df_long = split_tipo(df_acc, "Accesos")
        fig = area_chart(df_long, "periodo", "Accesos", "Tipo",
                         title="Accesos — suscripción vs satelital",
                         color_map={"TV suscripción": "#00B5E5",
                                    "TV satelital": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        df_long_ing = split_tipo(df_ing, "Ingresos")
        fig = area_chart(df_long_ing, "periodo", "Ingresos", "Tipo",
                         title="Ingresos — suscripción vs satelital (miles $)",
                         color_map={"TV suscripción": "#00B5E5",
                                    "TV satelital": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = line_chart(df_pen, "periodo", "tv_suscripcion_100_hogares",
                         title="Penetración suscripción c/100 hogares",
                         labels={"tv_suscripcion_100_hogares": "c/100 hogares"},
                         markers=False)
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        fig = line_chart(df_pen, "periodo", "tv_satelital_100_hogares",
                         title="Penetración satelital c/100 hogares",
                         labels={"tv_satelital_100_hogares": "c/100 hogares"},
                         markers=False)
        st.plotly_chart(fig, use_container_width=True)


# ── Accesos ───────────────────────────────────────────────────────────────────

elif categoria == "Accesos":
    st.header("Accesos a TV por suscripción")

    df = load(TVEndpoints.ACCESOS)
    DataValidator.validate(df, ["anio", "trimestre", "tv_suscripcion", "tv_satelital"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tv_acc")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    val_sus, delta_sus = last_period_delta(df_range, "tv_suscripcion")
    val_sat, delta_sat = last_period_delta(df_range, "tv_satelital")
    val_tot = val_sus + val_sat
    pct_sus = val_sus / val_tot * 100 if val_tot else 0

    show_kpis([
        {"label": "TV suscripción",  "value": val_sus, "delta": delta_sus,
         "format": "{:,.0f}"},
        {"label": "TV satelital",    "value": val_sat, "delta": delta_sat,
         "format": "{:,.0f}"},
        {"label": "Total",           "value": val_tot,
         "format": "{:,.0f}"},
        {"label": "% Suscripción",   "value": pct_sus,
         "format": "{:.1f}%"},
    ])

    st.divider()

    df_long = split_tipo(df_range, "Accesos")

    tab1, tab2, tab3 = st.tabs(["Área apilada", "Líneas", "Barras"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Accesos", "Tipo",
                         title="Accesos — suscripción vs satelital",
                         color_map={"TV suscripción": "#00B5E5",
                                    "TV satelital": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_long, "periodo", "Accesos", "Tipo",
                         title="Evolución de accesos por tipo",
                         color_map={"TV suscripción": "#00B5E5",
                                    "TV satelital": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = bar_chart(df_long, "periodo", "Accesos", "Tipo",
                        title="Accesos por trimestre", barmode="stack",
                        color_map={"TV suscripción": "#00B5E5",
                                   "TV satelital": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Participación suscripción sobre el total")
    df_range["pct_sus"] = (
        df_range["tv_suscripcion"] /
        (df_range["tv_suscripcion"] + df_range["tv_satelital"]) * 100
    ).round(2)

    fig_pct = go.Figure(go.Scatter(
        x=df_range["periodo"], y=df_range["pct_sus"],
        mode="lines+markers", fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
        marker={"size": 4},
    ))
    fig_pct.update_layout(
        title="% TV suscripción sobre total de accesos",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
        hovermode="x unified",
    )
    st.plotly_chart(fig_pct, use_container_width=True)


# ── Accesos - provincia ───────────────────────────────────────────────────────────

elif categoria == "Accesos - provincia":
    st.header("Accesos TV suscripción — por provincia")

    df = load(TVEndpoints.ACCESOS_PROVINCIA)
    DataValidator.validate(df, ["anio", "trimestre", "provincia", "tv_suscripcion"])
    df = sort_by_periodo(add_periodo_col(df))

    anio, trimestre = render_period_filters(df, key_prefix="tv_prov_acc")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()

    top = df_periodo.nlargest(1, "tv_suscripcion").iloc[0]
    low = df_periodo.nsmallest(1, "tv_suscripcion").iloc[0]

    show_kpis([
        {"label": "Total nacional",
         "value": df_periodo["tv_suscripcion"].sum(), "format": "{:,.0f}"},
        {"label": f"Mayor ({top['provincia']})",
         "value": top["tv_suscripcion"], "format": "{:,.0f}"},
        {"label": f"Menor ({low['provincia']})",
         "value": low["tv_suscripcion"], "format": "{:,.0f}"},
        {"label": "Promedio por provincia",
         "value": df_periodo["tv_suscripcion"].mean(), "format": "{:,.0f}"},
    ])

    st.divider()

    st.subheader("Ranking por accesos")
    df_rank = df_periodo[["provincia", "tv_suscripcion"]].sort_values(
        "tv_suscripcion", ascending=True
    )
    fig = bar_chart(df_rank, x="tv_suscripcion", y="provincia",
                    title=f"Accesos TV suscripción por provincia — {anio} T{trimestre}")
    fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"},
                      xaxis={"tickformat": ",.0f"})
    fig.update_traces(marker_color="#00B5E5", orientation="h")
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Evolución multi-provincia
    st.subheader("Comparar evolución entre provincias")
    provincias = sorted(df["provincia"].unique())
    prov_multi = st.multiselect(
        "Seleccionar provincias",
        provincias,
        default=["Buenos Aires", "CABA", "Córdoba", "Santa Fe"],
        key="tv_prov_multi",
    )
    if prov_multi:
        df_multi = sort_by_periodo(add_periodo_col(
            df[df["provincia"].isin(prov_multi)].copy()
        ))
        fig = line_chart(df_multi, "periodo", "tv_suscripcion", "provincia",
                         title="Accesos TV suscripción — comparativa provincial",
                         labels={"tv_suscripcion": "Accesos"})
        st.plotly_chart(fig, use_container_width=True)


# ── Penetración ───────────────────────────────────────────────────────────────

elif categoria == "Penetración":
    st.header("Penetración de TV por suscripción")

    df = load(TVEndpoints.PENETRACION)
    DataValidator.validate(df, [
        "anio", "trimestre",
        "tv_suscripcion_100_habitantes", "tv_satelital_100_habitantes",
        "tv_suscripcion_100_hogares",    "tv_satelital_100_hogares",
    ])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tv_pen")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    sus_hog, delta_sus_hog = last_period_delta(df_range, "tv_suscripcion_100_hogares")
    sat_hog, delta_sat_hog = last_period_delta(df_range, "tv_satelital_100_hogares")
    sus_hab, delta_sus_hab = last_period_delta(df_range, "tv_suscripcion_100_habitantes")
    sat_hab, delta_sat_hab = last_period_delta(df_range, "tv_satelital_100_habitantes")

    show_kpis([
        {"label": "Suscripción c/100 hogares",   "value": sus_hog,
         "delta": delta_sus_hog, "format": "{:.2f}"},
        {"label": "Satelital c/100 hogares",     "value": sat_hog,
         "delta": delta_sat_hog, "format": "{:.2f}"},
        {"label": "Suscripción c/100 hab.",      "value": sus_hab,
         "delta": delta_sus_hab, "format": "{:.2f}"},
        {"label": "Satelital c/100 hab.",        "value": sat_hab,
         "delta": delta_sat_hab, "format": "{:.2f}"},
    ])

    st.divider()

    # Doble eje Y: hogares (eje izq) vs habitantes (eje der)
    st.subheader("Evolución — c/100 hogares vs c/100 habitantes")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_range["periodo"], y=df_range["tv_suscripcion_100_hogares"],
        name="Suscripción c/100 hogares", mode="lines+markers",
        line={"color": "#00B5E5", "width": 2}, marker={"size": 4},
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=df_range["periodo"], y=df_range["tv_satelital_100_hogares"],
        name="Satelital c/100 hogares", mode="lines+markers",
        line={"color": "#EEAE42", "width": 2, "dash": "dot"}, marker={"size": 4},
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=df_range["periodo"], y=df_range["tv_suscripcion_100_habitantes"],
        name="Suscripción c/100 hab.", mode="lines",
        line={"color": "#005297", "width": 1.5}, opacity=0.7,
        yaxis="y2",
    ))
    fig.add_trace(go.Scatter(
        x=df_range["periodo"], y=df_range["tv_satelital_100_habitantes"],
        name="Satelital c/100 hab.", mode="lines",
        line={"color": "#854F0B", "width": 1.5}, opacity=0.7,
        yaxis="y2",
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 60},
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        yaxis=dict(
            title=dict(text="c/100 hogares", font={"color": "#00B5E5"}),
            tickfont={"color": "#00B5E5"}, gridcolor="#E8E8E8",
        ),
        yaxis2=dict(
            title=dict(text="c/100 habitantes", font={"color": "#005297"}),
            tickfont={"color": "#005297"},
            overlaying="y", side="right", showgrid=False,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Variación interanual de penetración hogares
    st.subheader("Variación interanual — suscripción c/100 hogares")
    df_yoy = df_range.copy()
    df_yoy["yoy"] = df_yoy["tv_suscripcion_100_hogares"].pct_change(4) * 100
    df_yoy = df_yoy.dropna(subset=["yoy"])

    fig_yoy = go.Figure(go.Bar(
        x=df_yoy["periodo"], y=df_yoy["yoy"].round(2),
        marker_color=["#00B5E5" if v >= 0 else "#E74242" for v in df_yoy["yoy"]],
    ))
    fig_yoy.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"size": 12},
        margin={"t": 20, "b": 40, "l": 40, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
        showlegend=False,
    )
    st.plotly_chart(fig_yoy, use_container_width=True)


# ── Penetración - provincia ───────────────────────────────────────────────────────

elif categoria == "Penetración - provincia":
    st.header("Penetración TV suscripción — por provincia")

    df = load(TVEndpoints.PENETRACION_PROVINCIA)

    # Normalizar nombres de columnas (100habitantes vs 100_habitantes)
    df = df.rename(columns={
        "tv_suscripcion_100habitantes": "tv_suscripcion_100_habitantes",
        "tv_suscripcion_100hogares":    "tv_suscripcion_100_hogares",
    })

    DataValidator.validate(df, ["anio", "trimestre", "provincia",
                                "tv_suscripcion_100_habitantes",
                                "tv_suscripcion_100_hogares"])
    df = sort_by_periodo(add_periodo_col(df))

    anio, trimestre = render_period_filters(df, key_prefix="tv_prov_pen")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()

    top_hog = df_periodo.nlargest(1, "tv_suscripcion_100_hogares").iloc[0]
    low_hog = df_periodo.nsmallest(1, "tv_suscripcion_100_hogares").iloc[0]

    show_kpis([
        {"label": f"Mayor penetración hogares ({top_hog['provincia']})",
         "value": top_hog["tv_suscripcion_100_hogares"], "format": "{:.2f}"},
        {"label": f"Menor penetración hogares ({low_hog['provincia']})",
         "value": low_hog["tv_suscripcion_100_hogares"], "format": "{:.2f}"},
        {"label": "Promedio nacional (hogares)",
         "value": df_periodo["tv_suscripcion_100_hogares"].mean(), "format": "{:.2f}"},
        {"label": "Promedio nacional (hab.)",
         "value": df_periodo["tv_suscripcion_100_habitantes"].mean(), "format": "{:.2f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ranking — c/100 hogares")
        df_hog = df_periodo[["provincia", "tv_suscripcion_100_hogares"]].sort_values(
            "tv_suscripcion_100_hogares", ascending=True
        )
        fig = bar_chart(df_hog, x="tv_suscripcion_100_hogares", y="provincia",
                        title=f"{anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Ranking — c/100 habitantes")
        df_hab = df_periodo[["provincia", "tv_suscripcion_100_habitantes"]].sort_values(
            "tv_suscripcion_100_habitantes", ascending=True
        )
        fig = bar_chart(df_hab, x="tv_suscripcion_100_habitantes", y="provincia",
                        title=f"{anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#EEAE42", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Evolución provincia vs promedio nacional")
    provincias = sorted(df["provincia"].unique())
    prov_sel = st.selectbox("Seleccionar provincia", provincias, key="tv_prov_pen_evol")

    df_prov = sort_by_periodo(add_periodo_col(
        df[df["provincia"] == prov_sel].copy()
    ))
    df_nac = sort_by_periodo(add_periodo_col(
        df.groupby(["anio", "trimestre"])["tv_suscripcion_100_hogares"]
        .mean().reset_index()
    ))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_prov["periodo"], y=df_prov["tv_suscripcion_100_hogares"],
        name=prov_sel, mode="lines+markers",
        line={"color": "#00B5E5", "width": 2}, marker={"size": 4},
    ))
    fig.add_trace(go.Scatter(
        x=df_nac["periodo"], y=df_nac["tv_suscripcion_100_hogares"].round(2),
        name="Promedio nacional", mode="lines",
        line={"color": "#C6C6C6", "width": 1.5, "dash": "dot"},
    ))
    fig.update_layout(
        title=f"{prov_sel} vs promedio nacional — c/100 hogares",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.02},
        yaxis={"gridcolor": "#E8E8E8"},
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Ingresos ──────────────────────────────────────────────────────────────────

elif categoria == "Ingresos":
    st.header("Ingresos del sector")

    df = load(TVEndpoints.INGRESOS)
    DataValidator.validate(df, ["anio", "trimestre", "tv_suscripcion", "tv_satelital"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tv_ing")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()
    df_range["total"] = df_range["tv_suscripcion"] + df_range["tv_satelital"]

    val_sus, delta_sus = last_period_delta(df_range, "tv_suscripcion")
    val_sat, delta_sat = last_period_delta(df_range, "tv_satelital")
    val_tot, delta_tot = last_period_delta(df_range, "total")

    show_kpis([
        {"label": "Ingresos suscripción (miles $)", "value": val_sus,
         "delta": delta_sus, "format": "{:,.0f}"},
        {"label": "Ingresos satelital (miles $)",   "value": val_sat,
         "delta": delta_sat, "format": "{:,.0f}"},
        {"label": "Total (miles $)",                "value": val_tot,
         "delta": delta_tot, "format": "{:,.0f}"},
    ])

    st.divider()

    df_long = split_tipo(df_range, "Ingresos")

    tab1, tab2 = st.tabs(["Área apilada", "Barras"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Ingresos", "Tipo",
                         title="Ingresos — suscripción vs satelital (miles $)",
                         color_map={"TV suscripción": "#00B5E5",
                                    "TV satelital": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = bar_chart(df_long, "periodo", "Ingresos", "Tipo",
                        title="Ingresos por trimestre (miles $)", barmode="stack",
                        color_map={"TV suscripción": "#00B5E5",
                                   "TV satelital": "#EEAE42"})
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(df_range[["anio", "trimestre", "periodo",
                                "tv_suscripcion", "tv_satelital", "total"]],
                     use_container_width=True)
