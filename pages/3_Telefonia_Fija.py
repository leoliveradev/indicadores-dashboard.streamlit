import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config.endpoints import FijaEndpoints
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


st.set_page_config(page_title="Telefonía Fija · ENACOM", page_icon="☎️", layout="wide")
setup_page()

CATEGORIES = [
    "Resumen general",
    "Accesos",
    "Accesos - provincia",
    "Penetración",
    "Penetración - provincia",
    "Ingresos",
]

# Columnas de segmento y sus etiquetas
SEGMENTOS_COLS   = ["hogares", "comercial", "gobierno", "otros"]
SEGMENTOS_LABELS = {
    "hogares":   "Hogares",
    "comercial": "Comercial",
    "gobierno":  "Gobierno",
    "otros":     "Otros",
}

categoria = render_sidebar(CATEGORIES, key="tel_categoria")
st.title("☎️ Telefonía fija")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


# ── Resumen general ───────────────────────────────────────────────────────────

if categoria == "Resumen general":
    st.header("Resumen general")

    df_acc = load(FijaEndpoints.FIJA_ACCESOS)
    df_ing = load(FijaEndpoints.FIJA_INGRESOS)
    df_pen = load(FijaEndpoints.FIJA_PENETRACION)

    for df, cols in [
        (df_acc, ["anio", "trimestre"] + SEGMENTOS_COLS + ["total"]),
        (df_ing, ["anio", "trimestre", "ingresos"]),
        (df_pen, ["anio", "trimestre", "accesos_100_hab", "accesos_100_hog"]),
    ]:
        DataValidator.validate(df, cols)

    df_acc = sort_by_periodo(add_periodo_col(df_acc))
    df_ing = sort_by_periodo(add_periodo_col(df_ing))
    df_pen = sort_by_periodo(add_periodo_col(df_pen))

    val_tot, delta_tot = last_period_delta(df_acc, "total")
    val_hog, delta_hog = last_period_delta(df_acc, "hogares")
    val_ing, delta_ing = last_period_delta(df_ing, "ingresos")
    val_pen, delta_pen = last_period_delta(df_pen, "accesos_100_hog")

    show_kpis([
        {"label": "Accesos totales",      "value": val_tot, "delta": delta_tot,
         "format": "{:,.0f}"},
        {"label": "Hogares",              "value": val_hog, "delta": delta_hog,
         "format": "{:,.0f}"},
        {"label": "Ingresos (miles $)",   "value": val_ing, "delta": delta_ing,
         "format": "{:,.0f}"},
        {"label": "Penetración c/100 hog","value": val_pen, "delta": delta_pen,
         "format": "{:.2f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        df_long = melt_tecnologias(df_acc, SEGMENTOS_COLS,
                                   id_col="periodo", var_name="Segmento", value_name="Accesos")
        df_long["Segmento"] = df_long["Segmento"].map(SEGMENTOS_LABELS)
        fig = area_chart(df_long, "periodo", "Accesos", "Segmento",
                         title="Accesos por segmento — evolución")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = bar_chart(df_ing, "periodo", "ingresos",
                        title="Ingresos por trimestre (miles $)")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        fig = line_chart(df_pen, "periodo", "accesos_100_hog",
                         title="Penetración c/100 hogares",
                         labels={"accesos_100_hog": "c/100 hogares"}, markers=False)
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        # Último período: composición por segmento
        ultimo = df_acc.iloc[-1]
        df_pie = (
            df_acc[SEGMENTOS_COLS].iloc[-1]
            .rename(SEGMENTOS_LABELS)
            .reset_index()
        )
        df_pie.columns = ["Segmento", "Accesos"]
        fig_pie = px.pie(df_pie, names="Segmento", values="Accesos",
                         title=f"Composición — {df_acc['periodo'].iloc[-1]}",
                         hole=0.45)
        fig_pie.update_layout(margin={"t": 50, "b": 0, "l": 0, "r": 0})
        st.plotly_chart(fig_pie, use_container_width=True)


# ── Accesos ───────────────────────────────────────────────────────────────────

elif categoria == "Accesos":
    st.header("Accesos de telefonía fija")

    df = load(FijaEndpoints.FIJA_ACCESOS)
    DataValidator.validate(df, ["anio", "trimestre"] + SEGMENTOS_COLS + ["total"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tel_acc")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    val_tot, delta_tot = last_period_delta(df_range, "total")
    val_hog, delta_hog = last_period_delta(df_range, "hogares")
    val_com, delta_com = last_period_delta(df_range, "comercial")
    val_gob, delta_gob = last_period_delta(df_range, "gobierno")

    show_kpis([
        {"label": "Total",      "value": val_tot, "delta": delta_tot, "format": "{:,.0f}"},
        {"label": "Hogares",    "value": val_hog, "delta": delta_hog, "format": "{:,.0f}"},
        {"label": "Comercial",  "value": val_com, "delta": delta_com, "format": "{:,.0f}"},
        {"label": "Gobierno",   "value": val_gob, "delta": delta_gob, "format": "{:,.0f}"},
    ])

    st.divider()

    df_long = melt_tecnologias(df_range, SEGMENTOS_COLS,
                               id_col="periodo", var_name="Segmento", value_name="Accesos")
    df_long["Segmento"] = df_long["Segmento"].map(SEGMENTOS_LABELS)

    tab1, tab2, tab3 = st.tabs(["Área apilada", "Líneas", "Barras"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Accesos", "Segmento",
                         title="Accesos por segmento — evolución")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_long, "periodo", "Accesos", "Segmento",
                         title="Evolución por segmento")
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = bar_chart(df_long, "periodo", "Accesos", "Segmento",
                        title="Accesos por trimestre", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Participación hogares sobre el total")
    df_range["pct_hogares"] = (df_range["hogares"] / df_range["total"] * 100).round(2)
    fig_pct = go.Figure(go.Scatter(
        x=df_range["periodo"], y=df_range["pct_hogares"],
        mode="lines+markers", fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
        marker={"size": 4},
    ))
    fig_pct.update_layout(
        title="% accesos hogares sobre el total",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
        hovermode="x unified",
    )
    st.plotly_chart(fig_pct, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(df_range, use_container_width=True)



# ── Accesos - provincia ───────────────────────────────────────────────────────

elif categoria == "Accesos - provincia":
    st.header("Accesos telefonía fija — por provincia")

    df = load(FijaEndpoints.FIJA_ACCESOS_PROVINCIA)

    # Typo en el CSV original: "hogres" → "hogares"
    df = df.rename(columns={"hogres": "hogares"})

    DataValidator.validate(df, ["anio", "trimestre", "provincia",
                                "hogares", "comercial", "gobierno", "otros", "total"])
    df = sort_by_periodo(add_periodo_col(df))

    anio, trimestre = render_period_filters(df, key_prefix="tel_prov_acc")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()

    top = df_periodo.nlargest(1, "total").iloc[0]
    low = df_periodo.nsmallest(1, "total").iloc[0]

    show_kpis([
        {"label": "Total nacional",         "value": df_periodo["total"].sum(),
         "format": "{:,.0f}"},
        {"label": f"Mayor ({top['provincia']})", "value": top["total"],
         "format": "{:,.0f}"},
        {"label": f"Menor ({low['provincia']})", "value": low["total"],
         "format": "{:,.0f}"},
        {"label": "Promedio por provincia", "value": df_periodo["total"].mean(),
         "format": "{:,.0f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ranking por accesos totales")
        df_rank = df_periodo[["provincia","total"]].sort_values("total", ascending=True)
        fig = bar_chart(df_rank, x="total", y="provincia",
                        title=f"Accesos por provincia — {anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"},
                          xaxis={"tickformat": ",.0f"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Composición por segmento")
        df_long = melt_tecnologias(
            df_periodo, SEGMENTOS_COLS,
            id_col="provincia", var_name="Segmento", value_name="Accesos",
        )
        df_long["Segmento"] = df_long["Segmento"].map(SEGMENTOS_LABELS)
        df_long = df_long.merge(
            df_periodo[["provincia","total"]], on="provincia"
        ).sort_values("total", ascending=False)

        fig = bar_chart(df_long, x="Accesos", y="provincia",
                        color="Segmento", barmode="stack",
                        title=f"Composición por segmento — {anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"},
                          xaxis={"tickformat": ",.0f"})
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Comparar evolución entre provincias")
    provincias = sorted(df["provincia"].unique())
    prov_multi = st.multiselect(
        "Seleccionar provincias", provincias,
        default=["Buenos Aires", "CABA", "Córdoba", "Santa Fe"],
        key="tel_prov_multi",
    )
    if prov_multi:
        df_multi = sort_by_periodo(add_periodo_col(
            df[df["provincia"].isin(prov_multi)].copy()
        ))
        fig = line_chart(df_multi, "periodo", "total", "provincia",
                         title="Accesos totales — comparativa provincial",
                         labels={"total": "Accesos"})
        st.plotly_chart(fig, use_container_width=True)


# ── Penetración ───────────────────────────────────────────────────────────────

elif categoria == "Penetración":
    st.header("Penetración de telefonía fija")

    df = load(FijaEndpoints.FIJA_PENETRACION)
    DataValidator.validate(df, ["anio", "trimestre", "accesos_100_hab", "accesos_100_hog"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tel_pen")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    hab_val, delta_hab = last_period_delta(df_range, "accesos_100_hab")
    hog_val, delta_hog = last_period_delta(df_range, "accesos_100_hog")
    hab_max   = df_range["accesos_100_hab"].max()
    periodo_max = df_range.loc[df_range["accesos_100_hab"].idxmax(), "periodo"]

    show_kpis([
        {"label": "Accesos c/100 hab. (último)", "value": hab_val,
         "delta": delta_hab, "format": "{:.2f}"},
        {"label": "Accesos c/100 hogares",       "value": hog_val,
         "delta": delta_hog, "format": "{:.2f}"},
        {"label": f"Máx. histórico hab. ({periodo_max})", "value": hab_max,
         "format": "{:.2f}"},
    ])

    st.divider()

    # Doble eje Y: hogares vs habitantes
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_range["periodo"], y=df_range["accesos_100_hog"],
        name="c/100 hogares", mode="lines+markers",
        line={"color": "#00B5E5", "width": 2}, marker={"size": 4},
        fill="tozeroy", fillcolor="rgba(0,181,229,0.06)",
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=df_range["periodo"], y=df_range["accesos_100_hab"],
        name="c/100 habitantes", mode="lines+markers",
        line={"color": "#EEAE42", "width": 2}, marker={"size": 4},
        fill="tozeroy", fillcolor="rgba(238,174,66,0.06)",
        yaxis="y2",
    ))
    fig.update_layout(
        title="Penetración — c/100 hogares vs c/100 habitantes",
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
            title=dict(text="c/100 habitantes", font={"color": "#EEAE42"}),
            tickfont={"color": "#EEAE42"},
            overlaying="y", side="right", showgrid=False,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Variación interanual — c/100 habitantes")
    df_yoy = df_range.copy()
    df_yoy["yoy"] = df_yoy["accesos_100_hab"].pct_change(4) * 100
    df_yoy = df_yoy.dropna(subset=["yoy"])

    fig_yoy = go.Figure(go.Bar(
        x=df_yoy["periodo"], y=df_yoy["yoy"].round(2),
        marker_color=["#00B5E5" if v >= 0 else "#E74242" for v in df_yoy["yoy"]],
    ))
    fig_yoy.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"size": 12}, margin={"t": 20, "b": 40, "l": 40, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
        showlegend=False,
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(df_range[["anio","trimestre","periodo",
                                "accesos_100_hab","accesos_100_hog"]],
                     use_container_width=True)



# ── Penetración - provincia ───────────────────────────────────────────────────────

elif categoria == "Penetración - provincia":
    st.header("Penetración telefonía fija — por provincia")

    df = load(FijaEndpoints.FIJA_PENETRACION_PROVINCIA)
    DataValidator.validate(df, ["anio", "trimestre", "provincia",
                                "accesos_100_hab", "accesos_100_hog"])
    df = sort_by_periodo(add_periodo_col(df))

    anio, trimestre = render_period_filters(df, key_prefix="tel_prov_pen")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()

    top_hog = df_periodo.nlargest(1, "accesos_100_hog").iloc[0]
    low_hog = df_periodo.nsmallest(1, "accesos_100_hog").iloc[0]

    show_kpis([
        {"label": f"Mayor penetración hogares ({top_hog['provincia']})",
         "value": top_hog["accesos_100_hog"], "format": "{:.2f}"},
        {"label": f"Menor penetración hogares ({low_hog['provincia']})",
         "value": low_hog["accesos_100_hog"], "format": "{:.2f}"},
        {"label": "Promedio nacional (hogares)",
         "value": df_periodo["accesos_100_hog"].mean(), "format": "{:.2f}"},
        {"label": "Promedio nacional (hab.)",
         "value": df_periodo["accesos_100_hab"].mean(), "format": "{:.2f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ranking — c/100 hogares")
        df_hog = df_periodo[["provincia","accesos_100_hog"]].sort_values(
            "accesos_100_hog", ascending=True
        )
        fig = bar_chart(df_hog, x="accesos_100_hog", y="provincia",
                        title=f"{anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Ranking — c/100 habitantes")
        df_hab = df_periodo[["provincia","accesos_100_hab"]].sort_values(
            "accesos_100_hab", ascending=True
        )
        fig = bar_chart(df_hab, x="accesos_100_hab", y="provincia",
                        title=f"{anio} T{trimestre}")
        fig.update_layout(height=650, yaxis={"categoryorder": "total ascending"})
        fig.update_traces(marker_color="#EEAE42", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Evolución provincia vs promedio nacional")
    provincias = sorted(df["provincia"].unique())
    prov_sel = st.selectbox("Seleccionar provincia", provincias, key="tel_prov_pen_evol")

    df_prov = sort_by_periodo(add_periodo_col(
        df[df["provincia"] == prov_sel].copy()
    ))
    df_nac = sort_by_periodo(add_periodo_col(
        df.groupby(["anio","trimestre"])["accesos_100_hog"].mean().reset_index()
    ))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_prov["periodo"], y=df_prov["accesos_100_hog"],
        name=prov_sel, mode="lines+markers",
        line={"color": "#00B5E5", "width": 2}, marker={"size": 4},
    ))
    fig.add_trace(go.Scatter(
        x=df_nac["periodo"], y=df_nac["accesos_100_hog"].round(2),
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

    df = load(FijaEndpoints.FIJA_INGRESOS)
    DataValidator.validate(df, ["anio", "trimestre", "ingresos"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="tel_ing")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    val, delta = last_period_delta(df_range, "ingresos")
    val_inicio = df_range["ingresos"].iloc[0]
    crec_acum = (val - val_inicio) / val_inicio * 100 if val_inicio else None

    show_kpis([
        {"label": "Ingresos (miles $)", "value": val, "delta": delta,
         "format": "{:,.0f}"},
        {"label": "Crecimiento acumulado", "value": crec_acum or 0,
         "format": "{:+.1f}%",
         "help": f"Variación desde {anio_desde} hasta {anio_hasta}"},
    ])

    st.divider()

    tab1, tab2 = st.tabs(["Barras", "Línea"])
    with tab1:
        fig = bar_chart(df_range, "periodo", "ingresos",
                        title="Ingresos por trimestre (miles $)")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_range, "periodo", "ingresos",
                         title="Ingresos — evolución", markers=False)
        st.plotly_chart(fig, use_container_width=True)
