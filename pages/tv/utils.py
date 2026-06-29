from services.data_manager import DataManager
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
    last_period_delta,
)
import streamlit as st

import plotly.graph_objects as go
from services.transformers import add_periodo_col, sort_by_periodo, melt_tecnologias

from pages.tv.config import DATASETS

@st.cache_data
def load_dataset(dataset_key):
    if dataset_key not in DATASETS:
        raise ValueError(f"Dataset '{dataset_key}' no está definido en config")

    cfg = DATASETS[dataset_key]

    df = DataManager.load(cfg["endpoint"])
    DataValidator.validate(df, cfg["cols"])

    return sort_by_periodo(add_periodo_col(df))


def apply_operation(df, cfg):
    """Aplica operación declarativa (ej: sum)."""
    df = df.copy()

    if cfg["type"] == "sum":
        df["_metric"] = sum(df[col] for col in cfg["columns"])

    return df, "_metric"


def build_kpis(kpi_config, datasets, default_dataset=None):
    kpis = []

    for cfg in kpi_config:
        dataset_key = cfg.get("dataset", default_dataset)

        if dataset_key is None:
            raise ValueError("KPI sin dataset definido")

        df = datasets[dataset_key]

        df_calc, col = apply_operation(df, cfg)

        val, delta = last_period_delta(df_calc, col)

        kpis.append({
            "label": cfg["label"],
            "value": val,
            "delta": delta,
            "format": cfg["format"],
        })

    return kpis


def apply_operation(df, cfg):
    df = df.copy()

    # suma
    if cfg.get("type") == "sum":
        df["_metric"] = sum(df[col] for col in cfg["columns"])

    # ratio (%)
    elif cfg.get("type") == "ratio":
        total = sum(df[col] for col in cfg["den"])
        df["_metric"] = (df[cfg["num"]] / total) * 100

    # default (col directa)
    else:
        df["_metric"] = df[cfg["column"]]

    return df, "_metric"

def build_kpis_agg(kpi_config, df):
    kpis = []

    for cfg in kpi_config:
        col = cfg["column"]

        if cfg["agg"] == "sum":
            val = df[col].sum()

        elif cfg["agg"] == "mean":
            val = df[col].mean()

        else:
            raise ValueError(f"agg no soportado: {cfg['agg']}")

        kpis.append({
            "label": cfg["label"],
            "value": val,
            "format": cfg["format"],
        })

    return kpis

def get_top_bottom(df, col, label_col="provincia", fmt="{:,.0f}"):
    top = df.nlargest(1, col).iloc[0]
    low = df.nsmallest(1, col).iloc[0]

    return [
        {
            "label": f"Mayor ({top[label_col]})",
            "value": top[col],
            "format": fmt,
        },
        {
            "label": f"Menor ({low[label_col]})",
            "value": low[col],
            "format": fmt,
        },
    ]

def compute_yoy(df, col, periods=4):
    df = df.copy()
    df["yoy"] = df[col].pct_change(periods) * 100
    return df.dropna(subset=["yoy"])


def dual_axis_chart(config, df, x="periodo"):
    fig = go.Figure()

    for s in config["left_axis"]["series"]:
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[s["column"]],
            name=s["name"],
            mode=s.get("mode", "lines"),
            line={
                "color": s["color"],
                "width": 2,
                "dash": s.get("dash", None),
            },
            marker={"size": 4} if "markers" in s.get("mode", "") else None,
            yaxis="y1",
        ))

    for s in config["right_axis"]["series"]:
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[s["column"]],
            name=s["name"],
            mode=s.get("mode", "lines"),
            line={
                "color": s["color"],
                "width": 1.5,
                "dash": s.get("dash", None),
            },
            opacity=s.get("opacity", 0.7),
            yaxis="y2",
        ))

    fig.update_layout(
        title=config.get("title", ""),
        hovermode="x unified",
        margin={"t": 48, "b": 40, "l": 48, "r": 60},
        legend={"orientation": "h", "y": 1.02, "x": 0},

        yaxis=dict(
            title=config["left_axis"].get("label", ""),
            ticksuffix=config["left_axis"].get("suffix", ""),
            gridcolor="#E8E8E8",
        ),
        yaxis2=dict(
            title=config["right_axis"].get("label", ""),
            ticksuffix=config["right_axis"].get("suffix", ""),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )

    return fig


def compare_vs_national(
    df,
    group_col,
    value_col,
    selected,
    period_cols=("anio", "trimestre"),
    title=None,
    y_suffix=None
):
    """
    Genera gráfico comparando una serie (ej: provincia)
    contra el promedio nacional.
    """

    # serie del grupo seleccionado
    df_sel = df[df[group_col] == selected].copy()
    df_sel = sort_by_periodo(add_periodo_col(df_sel))

    # promedio nacional
    df_nac = (
        df.groupby(list(period_cols))[value_col]
        .mean()
        .reset_index()
    )
    df_nac = sort_by_periodo(add_periodo_col(df_nac))

    # gráfico
    fig = go.Figure()

    # serie seleccionada
    fig.add_trace(go.Scatter(
        x=df_sel["periodo"],
        y=df_sel[value_col],
        name=selected,
        mode="lines+markers",
        line={"width": 2},
    ))

    # promedio nacional
    fig.add_trace(go.Scatter(
        x=df_nac["periodo"],
        y=df_nac[value_col].round(2),
        name="Promedio nacional",
        mode="lines",
        line={"dash": "dot"},
    ))

    fig.update_layout(
        title=title,
        yaxis={"ticksuffix": y_suffix or ""},
        hovermode="x unified",
        margin={"t": 40, "b": 40, "l": 40, "r": 20},
        legend={"orientation": "h", "y": 1.02},
    )

    return fig



def split_tipo(df, value_name, label_map=None):
    df_long = melt_tecnologias(
        df,
        ["tv_suscripcion", "tv_satelital"],
        id_col="periodo",
        var_name="Tipo",
        value_name=value_name,
    )

    df_long["Tipo"] = df_long["Tipo"].map({
        "tv_suscripcion": "TV suscripción",
        "tv_satelital": "TV satelital",
    })

    if label_map is None:
        label_map = {
            "tv_suscripcion": "TV suscripción",
            "tv_satelital": "TV satelital",
        }

    return df_long