import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from config.endpoints import PortabilidadEndpoints
from services.data_manager import DataManager, DataLoadError
from services.data_validator import DataValidator
from services.transformers import add_periodo_col, sort_by_periodo, last_period_delta
from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.charts import line_chart, bar_chart


st.set_page_config(page_title="Portabilidad · ENACOM", page_icon="🔄", layout="wide")
setup_page()

CATEGORIES = [
    "Resumen general",
    "Telefonía móvil",
    # "Telefonía fija",  ← descomentar cuando estén los datos
]

categoria = render_sidebar(CATEGORIES, key="port_categoria")
st.title("🔄 Portabilidad numérica")


def load(filename: str):
    try:
        return DataManager.load(filename)
    except DataLoadError as e:
        st.error(str(e), icon="🚨")
        st.stop()


def mensual_a_trimestral(df):
    """Suma portaciones por trimestre."""
    df = df.copy()
    df["trimestre"] = ((df["mes"] - 1) // 3) + 1
    return (
        df.groupby(["anio", "trimestre"])["total"]
        .sum()
        .reset_index()
        .pipe(lambda d: sort_by_periodo(add_periodo_col(d)))
    )


def mensual_a_anual(df):
    """Suma portaciones por año."""
    return (
        df.groupby("anio")["total"]
        .sum()
        .reset_index()
        .sort_values("anio")
    )


def add_mes_col(df):
    """Agrega columna periodo mensual tipo '2024-03'."""
    df = df.copy()
    df["periodo"] = df["anio"].astype(str) + "-" + df["mes"].astype(str).str.zfill(2)
    return df


# ── Resumen general ───────────────────────────────────────────────────────────

if categoria == "Resumen general":
    st.header("Resumen general")

    df = load(PortabilidadEndpoints.MOVIL)
    DataValidator.validate(df, ["anio", "mes", "total"])

    df_t  = mensual_a_trimestral(df)
    df_a  = mensual_a_anual(df)

    val_ult, delta_ult = last_period_delta(df_t, "total")
    total_acum = df["total"].sum()
    prom_mensual = df["total"].mean()
    idx_max = df["total"].idxmax()
    mes_pico = f"{df.loc[idx_max,'anio']}-{df.loc[idx_max,'mes']:02d}"

    show_kpis([
        {"label": "Portaciones (último trim.)", "value": val_ult,
         "delta": delta_ult, "format": "{:,.0f}"},
        {"label": "Total acumulado (2012–hoy)", "value": total_acum,
         "format": "{:,.0f}"},
        {"label": "Promedio mensual histórico", "value": prom_mensual,
         "format": "{:,.0f}"},
        {"label": f"Pico histórico ({mes_pico})", "value": df["total"].max(),
         "format": "{:,.0f}"},
    ])

    st.divider()

    col1, col2 = st.columns([3, 2])

    with col1:
        # Evolución trimestral
        fig = go.Figure(go.Scatter(
            x=df_t["periodo"], y=df_t["total"],
            mode="lines", fill="tozeroy",
            line={"color": "#00B5E5", "width": 2},
            fillcolor="rgba(0,181,229,0.08)",
        ))
        fig.update_layout(
            title="Portaciones móviles por trimestre",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Arial, sans-serif", "size": 13},
            margin={"t": 48, "b": 40, "l": 48, "r": 20},
            yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
            hovermode="x unified", showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Total anual como barras
        fig2 = go.Figure(go.Bar(
            x=df_a["anio"].astype(str), y=df_a["total"],
            marker_color="#00B5E5",
        ))
        fig2.update_layout(
            title="Total anual de portaciones",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Arial, sans-serif", "size": 13},
            margin={"t": 48, "b": 40, "l": 48, "r": 20},
            yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
            showlegend=False,
        )
        st.plotly_chart(fig2, use_container_width=True)


# ── Telefonía móvil ───────────────────────────────────────────────────────────

elif categoria == "Telefonía móvil":
    st.header("Portabilidad — telefonía móvil")

    df = load(PortabilidadEndpoints.MOVIL)
    DataValidator.validate(df, ["anio", "mes", "total"])
    df = add_mes_col(df)

    # Filtro de rango de años
    anios = sorted(df["anio"].unique())
    col_f1, col_f2, col_f3 = st.columns([1, 1, 4])
    with col_f1:
        anio_desde = st.selectbox("Desde", anios, index=0, key="port_desde")
    with col_f2:
        anio_hasta = st.selectbox("Hasta", anios,
                                  index=len(anios) - 1, key="port_hasta")

    df_range = df[(df["anio"] >= anio_desde) & (df["anio"] <= anio_hasta)].copy()
    df_t     = mensual_a_trimestral(df_range)
    df_a     = mensual_a_anual(df_range)

    val_ult, delta_ult = last_period_delta(df_t, "total")
    total_rango = df_range["total"].sum()
    prom_mens   = df_range["total"].mean()
    idx_max     = df_range["total"].idxmax()
    mes_pico    = df_range.loc[idx_max, "periodo"]

    show_kpis([
        {"label": "Portaciones (último trim.)", "value": val_ult,
         "delta": delta_ult, "format": "{:,.0f}"},
        {"label": f"Total {anio_desde}–{anio_hasta}", "value": total_rango,
         "format": "{:,.0f}"},
        {"label": "Promedio mensual", "value": prom_mens,
         "format": "{:,.0f}"},
        {"label": f"Pico del período ({mes_pico})", "value": df_range["total"].max(),
         "format": "{:,.0f}"},
    ])

    st.divider()

    # ── Vista mensual / trimestral / anual ────────────────────────────────────
    st.subheader("Evolución histórica")
    granularidad = st.radio(
        "Granularidad", ["Mensual", "Trimestral", "Anual"],
        horizontal=True, key="port_gran",
    )

    if granularidad == "Mensual":
        fig = go.Figure(go.Scatter(
            x=df_range["periodo"], y=df_range["total"],
            mode="lines", line={"color": "#00B5E5", "width": 1.5},
            fill="tozeroy", fillcolor="rgba(0,181,229,0.06)",
        ))
        fig.update_layout(
            title="Portaciones mensuales",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Arial, sans-serif", "size": 13},
            margin={"t": 48, "b": 40, "l": 48, "r": 20},
            yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
            xaxis={"tickangle": -45},
            hovermode="x unified", showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    elif granularidad == "Trimestral":
        fig = go.Figure(go.Scatter(
            x=df_t["periodo"], y=df_t["total"],
            mode="lines+markers", line={"color": "#00B5E5", "width": 2},
            fill="tozeroy", fillcolor="rgba(0,181,229,0.08)",
            marker={"size": 5},
        ))
        fig.update_layout(
            title="Portaciones trimestrales",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Arial, sans-serif", "size": 13},
            margin={"t": 48, "b": 40, "l": 48, "r": 20},
            yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
            hovermode="x unified", showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    else:  # Anual
        fig = go.Figure(go.Bar(
            x=df_a["anio"].astype(str), y=df_a["total"],
            marker_color="#00B5E5",
            text=df_a["total"].apply(lambda v: f"{v:,.0f}"),
            textposition="outside",
        ))
        fig.update_layout(
            title="Portaciones anuales",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Arial, sans-serif", "size": 13},
            margin={"t": 48, "b": 40, "l": 48, "r": 60},
            yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Estacionalidad mensual ────────────────────────────────────────────────
    st.subheader("Estacionalidad — promedio por mes del año")
    st.caption("Identifica qué meses concentran históricamente más portaciones.")

    MESES = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
             7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

    df_estac = (
        df_range.groupby("mes")["total"]
        .mean()
        .reset_index()
        .sort_values("mes")
    )
    df_estac["mes_label"] = df_estac["mes"].map(MESES)
    promedio_global = df_estac["total"].mean()

    fig_est = go.Figure(go.Bar(
        x=df_estac["mes_label"],
        y=df_estac["total"].round(0),
        marker_color=[
            "#00B5E5" if v >= promedio_global else "#BCE4F4"
            for v in df_estac["total"]
        ],
        text=df_estac["total"].apply(lambda v: f"{v:,.0f}"),
        textposition="outside",
    ))
    fig_est.add_hline(
        y=promedio_global, line_dash="dot",
        line_color="#C6C6C6", line_width=1,
        annotation_text=f"Promedio: {promedio_global:,.0f}",
        annotation_position="top right",
    )
    fig_est.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
        showlegend=False,
    )
    st.plotly_chart(fig_est, use_container_width=True)

    st.divider()

    # ── Variación interanual ──────────────────────────────────────────────────
    st.subheader("Variación interanual — promedio mensual por año")

    df_a_prom = df_range.groupby("anio")["total"].mean().reset_index()
    df_a_prom["yoy"] = df_a_prom["total"].pct_change() * 100

    fig_yoy = go.Figure(go.Bar(
        x=df_a_prom["anio"].astype(str),
        y=df_a_prom["yoy"].round(1),
        marker_color=[
            "#00B5E5" if v >= 0 else "#E74242"
            for v in df_a_prom["yoy"].fillna(0)
        ],
        text=df_a_prom["yoy"].apply(
            lambda v: f"{v:+.1f}%" if pd.notna(v) else ""
        ),
        textposition="outside",
    ))
    fig_yoy.update_layout(
        title="Variación % del promedio mensual respecto al año anterior",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        yaxis={"ticksuffix": "%", "gridcolor": "#E8E8E8"},
        showlegend=False,
    )
    st.plotly_chart(fig_yoy, use_container_width=True)

    with st.expander("Ver datos completos"):
        st.dataframe(
            df_range[["anio", "mes", "periodo", "total"]]
            .rename(columns={"total": "portaciones"}),
            use_container_width=True,
        )