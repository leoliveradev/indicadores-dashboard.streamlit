"""
6_Mercado_Postal.py
───────────
Vista de Mercado Postal.

Particularidades:
- Facturación y producción son mensuales → se agregan a trimestral para
  consistencia visual con el resto del dashboard.
- Personal ocupado es trimestral.
- Provincias arranca en 2015.
- CSV provincial tiene typos en nombres de provincia (espacios, tildes).
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from config.constants import PostalCSV
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


st.set_page_config(page_title="Postal · ENACOM", page_icon="📦", layout="wide")
setup_page()

CATEGORIES = [
    "Resumen general",
    "Facturación",
    "Producción",
    "Facturación y producción - provincia",
    "Personal ocupado",
]

SERVICIOS_COLS = ["postales", "telegraficas", "monetarios"]
SERVICIOS_LABELS = {
    "postales":     "Servicios postales",
    "telegraficas": "Servicios telegráficos",
    "monetarios":   "Servicios monetarios",
}

categoria = render_sidebar(CATEGORIES, key="postal_categoria")
st.title("📦 Mercado postal")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


def mensual_a_trimestral(df, value_cols):
    """
    Agrega datos mensuales a trimestral sumando los 3 meses de cada trimestre.
    Requiere columnas: anio, mes.
    """
    df = df.copy()
    df["trimestre"] = ((df["mes"] - 1) // 3) + 1
    grouped = (
        df.groupby(["anio", "trimestre"])[value_cols]
        .sum()
        .reset_index()
    )
    return sort_by_periodo(add_periodo_col(grouped))


def limpiar_provincias(df):
    """Normaliza nombres de provincia con typos del CSV de ENACOM."""
    df = df.copy()
    df["provincia"] = (
        df["provincia"]
        .str.strip()
        .replace({"Rio Negro": "Río Negro"})
    )
    return df


# ── Resumen general ───────────────────────────────────────────────────────────

if categoria == "Resumen general":
    st.header("Resumen general")

    df_fac = load(PostalCSV.FACTURACION)
    df_pro = load(PostalCSV.PRODUCCION)
    df_per = load(PostalCSV.PERSONAL_OCUPADO)

    for df, cols in [
        (df_fac, ["anio", "mes"] + SERVICIOS_COLS),
        (df_pro, ["anio", "mes"] + SERVICIOS_COLS),
        (df_per, ["anio", "trimestre", "personal_ocupado"]),
    ]:
        DataValidator.validate(df, cols)

    df_fac_t = mensual_a_trimestral(df_fac, SERVICIOS_COLS)
    df_pro_t = mensual_a_trimestral(df_pro, SERVICIOS_COLS)
    df_per   = sort_by_periodo(add_periodo_col(df_per))

    fac_tot, delta_fac = last_period_delta(df_fac_t, "postales")
    pro_tot, delta_pro = last_period_delta(df_pro_t, "postales")
    per_val, delta_per = last_period_delta(df_per, "personal_ocupado")

    # Total facturación del último trimestre
    ultimo_fac = df_fac_t.iloc[-1]
    fac_total = ultimo_fac[SERVICIOS_COLS].sum()

    show_kpis([
        {"label": "Facturación postales ($)",    "value": fac_tot,  "delta": delta_fac,
         "format": "{:,.0f}"},
        {"label": "Producción postales (unid.)", "value": pro_tot,  "delta": delta_pro,
         "format": "{:,.0f}"},
        {"label": "Personal ocupado",            "value": per_val,  "delta": delta_per,
         "format": "{:,.0f}"},
        {"label": "Facturación total ($)",       "value": fac_total,
         "format": "{:,.0f}",
         "help": "Suma de postales + telegráficos + monetarios"},
    ])

    st.divider()

    # col1, col2 = st.columns(1)
    # with col1:
    #     df_long = melt_tecnologias(df_fac_t, SERVICIOS_COLS,
    #                                id_col="periodo", var_name="Servicio", value_name="Facturación")
    #     df_long["Servicio"] = df_long["Servicio"].map(SERVICIOS_LABELS)
    #     fig = area_chart(df_long, "periodo", "Facturación", "Servicio",
    #                      title="Facturación por tipo de servicio ($)")
    #     st.plotly_chart(fig, use_container_width=True)

    # with col2:
    #     df_long_p = melt_tecnologias(df_pro_t, SERVICIOS_COLS,
    #                                  id_col="periodo", var_name="Servicio", value_name="Producción")
    #     df_long_p["Servicio"] = df_long_p["Servicio"].map(SERVICIOS_LABELS)
    #     fig = area_chart(df_long_p, "periodo", "Producción", "Servicio",
    #                      title="Producción por tipo de servicio (unidades)")
    #     st.plotly_chart(fig, use_container_width=True)

    # col3, _ = st.columns([1, 1])
    # with col3:
    #     fig = line_chart(df_per, "periodo", "personal_ocupado",
    #                      title="Personal ocupado — evolución",
    #                      labels={"personal_ocupado": "Personas"}, markers=False)
    #     st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        df_long = melt_tecnologias(df_fac_t, SERVICIOS_COLS,
                                   id_col="periodo", var_name="Servicio", value_name="Facturación")
        df_long["Servicio"] = df_long["Servicio"].map(SERVICIOS_LABELS)
        fig = area_chart(df_long, "periodo", "Facturación", "Servicio",
                         title="Facturación por tipo de servicio ($)")
        st.plotly_chart(fig, use_container_width=True)

        df_long_p = melt_tecnologias(df_pro_t, SERVICIOS_COLS,
                                     id_col="periodo", var_name="Servicio", value_name="Producción")
        df_long_p["Servicio"] = df_long_p["Servicio"].map(SERVICIOS_LABELS)
        fig = area_chart(df_long_p, "periodo", "Producción", "Servicio",
                         title="Producción por tipo de servicio (unidades)")
        st.plotly_chart(fig, use_container_width=True)

        fig = line_chart(df_per, "periodo", "personal_ocupado",
                         title="Personal ocupado — evolución",
                         labels={"personal_ocupado": "Personas"}, markers=False)
        st.plotly_chart(fig, use_container_width=True)        

# ── Facturación ───────────────────────────────────────────────────────────────

elif categoria == "Facturación":
    st.header("Facturación del mercado postal")
    st.caption("Datos mensuales agregados a trimestral.")

    df = load(PostalCSV.FACTURACION)
    DataValidator.validate(df, ["anio", "mes"] + SERVICIOS_COLS)
    df_t = mensual_a_trimestral(df, SERVICIOS_COLS)

    anio_desde, anio_hasta = render_range_filter(df_t, key_prefix="pos_fac")
    df_range = df_t[(df_t["anio"] >= anio_desde) & (df_t["anio"] <= anio_hasta)].copy()

    fac_pos, delta_pos = last_period_delta(df_range, "postales")
    fac_tel, delta_tel = last_period_delta(df_range, "telegraficas")
    fac_mon, delta_mon = last_period_delta(df_range, "monetarios")
    fac_tot = fac_pos + fac_tel + fac_mon

    show_kpis([
        {"label": "Postales ($)",     "value": fac_pos, "delta": delta_pos, "format": "{:,.0f}"},
        {"label": "Telegráficos ($)", "value": fac_tel, "delta": delta_tel, "format": "{:,.0f}"},
        {"label": "Monetarios ($)",   "value": fac_mon, "delta": delta_mon, "format": "{:,.0f}"},
        {"label": "Total ($)",        "value": fac_tot,                     "format": "{:,.0f}"},
    ])

    st.divider()

    df_long = melt_tecnologias(df_range, SERVICIOS_COLS,
                               id_col="periodo", var_name="Servicio", value_name="Facturación")
    df_long["Servicio"] = df_long["Servicio"].map(SERVICIOS_LABELS)

    tab1, tab2, tab3 = st.tabs(["Área apilada", "Líneas", "Barras"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Facturación", "Servicio",
                         title="Facturación por tipo de servicio ($)")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_long, "periodo", "Facturación", "Servicio",
                         title="Evolución de facturación por servicio")
        st.plotly_chart(fig, use_container_width=True)
    with tab3:
        fig = bar_chart(df_long, "periodo", "Facturación", "Servicio",
                        title="Facturación por trimestre", barmode="stack")
        st.plotly_chart(fig, use_container_width=True)

    # Composición último trimestre
    st.subheader(f"Composición — {df_range['periodo'].iloc[-1]}")
    ultimo = df_range[SERVICIOS_COLS].iloc[-1].rename(SERVICIOS_LABELS).reset_index()
    ultimo.columns = ["Servicio", "Facturación"]
    fig_pie = px.pie(ultimo, names="Servicio", values="Facturación", hole=0.45)
    fig_pie.update_layout(margin={"t": 20, "b": 0, "l": 0, "r": 0})
    st.plotly_chart(fig_pie, use_container_width=True)


# ── Producción ────────────────────────────────────────────────────────────────

elif categoria == "Producción":
    st.header("Producción del mercado postal")
    st.caption("Datos mensuales agregados a trimestral. Unidades físicas despachadas.")

    df = load(PostalCSV.PRODUCCION)
    DataValidator.validate(df, ["anio", "mes"] + SERVICIOS_COLS)
    df_t = mensual_a_trimestral(df, SERVICIOS_COLS)

    anio_desde, anio_hasta = render_range_filter(df_t, key_prefix="pos_pro")
    df_range = df_t[(df_t["anio"] >= anio_desde) & (df_t["anio"] <= anio_hasta)].copy()

    pro_pos, delta_pos = last_period_delta(df_range, "postales")
    pro_tel, delta_tel = last_period_delta(df_range, "telegraficas")
    pro_mon, delta_mon = last_period_delta(df_range, "monetarios")
    pro_tot = pro_pos + pro_tel + pro_mon

    show_kpis([
        {"label": "Postales (unid.)",     "value": pro_pos, "delta": delta_pos,
         "format": "{:,.0f}"},
        {"label": "Telegráficos (unid.)", "value": pro_tel, "delta": delta_tel,
         "format": "{:,.0f}"},
        {"label": "Monetarios (unid.)",   "value": pro_mon, "delta": delta_mon,
         "format": "{:,.0f}"},
        {"label": "Total (unid.)",        "value": pro_tot,
         "format": "{:,.0f}"},
    ])

    st.divider()

    df_long = melt_tecnologias(df_range, SERVICIOS_COLS,
                               id_col="periodo", var_name="Servicio", value_name="Producción")
    df_long["Servicio"] = df_long["Servicio"].map(SERVICIOS_LABELS)

    tab1, tab2 = st.tabs(["Área apilada", "Líneas"])
    with tab1:
        fig = area_chart(df_long, "periodo", "Producción", "Servicio",
                         title="Producción por tipo de servicio (unidades)")
        st.plotly_chart(fig, use_container_width=True)
    with tab2:
        fig = line_chart(df_long, "periodo", "Producción", "Servicio",
                         title="Evolución de producción por servicio")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Facturación vs producción — ¿crecen juntos?")
    st.caption("Compara si la facturación y el volumen físico evolucionan en la misma dirección.")

    df_fac = load(PostalCSV.FACTURACION)
    df_fac_t = mensual_a_trimestral(df_fac, SERVICIOS_COLS)
    df_fac_r = df_fac_t[(df_fac_t["anio"] >= anio_desde) & (df_fac_t["anio"] <= anio_hasta)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_range["periodo"], y=df_range["postales"],
        name="Producción postales (unid.)", mode="lines",
        line={"color": "#00B5E5", "width": 2}, yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        x=df_fac_r["periodo"], y=df_fac_r["postales"],
        name="Facturación postales ($)", mode="lines",
        line={"color": "#EEAE42", "width": 2, "dash": "dot"}, yaxis="y2",
    ))
    fig.update_layout(
        title="Producción vs facturación — servicios postales",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 60},
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "top", "y": -0.20, "x": 0},
        yaxis=dict(
            title=dict(text="Unidades", font={"color": "#00B5E5"}),
            tickfont={"color": "#00B5E5"}, gridcolor="#E8E8E8",
        ),
        yaxis2=dict(
            title=dict(text="Pesos ($)", font={"color": "#EEAE42"}),
            tickfont={"color": "#EEAE42"},
            overlaying="y", side="right", showgrid=False,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Personal ocupado ──────────────────────────────────────────────────────────

elif categoria == "Personal ocupado":
    st.header("Personal ocupado en el mercado postal")

    df = load(PostalCSV.PERSONAL_OCUPADO)
    DataValidator.validate(df, ["anio", "trimestre", "personal_ocupado"])
    df = sort_by_periodo(add_periodo_col(df))

    anio_desde, anio_hasta = render_range_filter(df, key_prefix="pos_per")
    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()

    val, delta    = last_period_delta(df_range, "personal_ocupado")
    val_max       = df_range["personal_ocupado"].max()
    periodo_max   = df_range.loc[df_range["personal_ocupado"].idxmax(), "periodo"]
    val_min       = df_range["personal_ocupado"].min()
    periodo_min   = df_range.loc[df_range["personal_ocupado"].idxmin(), "periodo"]

    show_kpis([
        {"label": "Personal actual",         "value": val,     "delta": delta,
         "format": "{:,.0f}"},
        {"label": f"Máx. ({periodo_max})",   "value": val_max, "format": "{:,.0f}"},
        {"label": f"Mín. ({periodo_min})",   "value": val_min, "format": "{:,.0f}"},
        {"label": "Variación máx–mín",       "value": val_max - val_min,
         "format": "{:,.0f}"},
    ])

    st.divider()

    fig = go.Figure(go.Scatter(
        x=df_range["periodo"], y=df_range["personal_ocupado"],
        mode="lines+markers", fill="tozeroy",
        line={"color": "#00B5E5", "width": 2},
        fillcolor="rgba(0,181,229,0.08)",
        marker={"size": 4},
    ))
    fig.update_layout(
        title="Personal ocupado — evolución histórica",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Variación interanual")
    df_yoy = df_range.copy()
    df_yoy["yoy"] = df_yoy["personal_ocupado"].pct_change(4) * 100
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


# ── Facturación y producción - provincia ─────────────────────────────────────────

elif categoria == "Facturación y producción - provincia":
    st.header("Facturación y producción — por provincia")
    st.caption("Datos disponibles desde 2015. CABA y GBA aparecen agrupados en la fuente original.")

    df = load(PostalCSV.PROV_FACTURACION)
    df = limpiar_provincias(df)
    DataValidator.validate(df, ["anio", "trimestre", "provincia", "pesos", "unidades"])
    df = sort_by_periodo(add_periodo_col(df))

    anio, trimestre = render_period_filters(df, key_prefix="pos_prov")

    if not DataValidator.has_data(df, {"anio": anio, "trimestre": trimestre}):
        st.stop()

    df_periodo = filter_by_period(df, anio, trimestre).copy()

    top_pesos = df_periodo.nlargest(1, "pesos").iloc[0]
    top_unid  = df_periodo.nlargest(1, "unidades").iloc[0]

    show_kpis([
        {"label": "Facturación total ($)",
         "value": df_periodo["pesos"].sum(), "format": "{:,.0f}"},
        {"label": "Producción total (unid.)",
         "value": df_periodo["unidades"].sum(), "format": "{:,.0f}"},
        {"label": f"Mayor facturación ({top_pesos['provincia']})",
         "value": top_pesos["pesos"], "format": "{:,.0f}"},
        {"label": f"Mayor producción ({top_unid['provincia']})",
         "value": top_unid["unidades"], "format": "{:,.0f}"},
    ])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Ranking — facturación ($)")
        df_rank = df_periodo[["provincia", "pesos"]].sort_values("pesos", ascending=True)
        fig = bar_chart(df_rank, x="pesos", y="provincia",
                        title=f"Facturación por provincia — {anio} T{trimestre}")
        fig.update_layout(height=700, yaxis={"categoryorder": "total ascending"},
                          xaxis={"tickformat": ",.0f"})
        fig.update_traces(marker_color="#00B5E5", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Ranking — producción (unidades)")
        df_rank2 = df_periodo[["provincia", "unidades"]].sort_values("unidades", ascending=True)
        fig = bar_chart(df_rank2, x="unidades", y="provincia",
                        title=f"Producción por provincia — {anio} T{trimestre}")
        fig.update_layout(height=700, yaxis={"categoryorder": "total ascending"},
                          xaxis={"tickformat": ",.0f"})
        fig.update_traces(marker_color="#EEAE42", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Comparar evolución entre provincias")
    metric = st.radio("Métrica", ["Facturación ($)", "Producción (unidades)"],
                      horizontal=True, key="pos_prov_metric")
    val_col = "pesos" if metric == "Facturación ($)" else "unidades"

    provincias = sorted(df["provincia"].unique())
    prov_multi = st.multiselect(
        "Seleccionar provincias", provincias,
        default=["CABA y GBA", "Buenos Aires", "Córdoba", "Santa Fe"],
        key="pos_prov_multi",
    )
    if prov_multi:
        df_multi = sort_by_periodo(add_periodo_col(
            df[df["provincia"].isin(prov_multi)].copy()
        ))
        fig = line_chart(df_multi, "periodo", val_col, "provincia",
                         title=f"{metric} — comparativa provincial",
                         labels={val_col: metric})
        st.plotly_chart(fig, use_container_width=True)