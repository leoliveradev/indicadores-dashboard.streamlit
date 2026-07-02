from services.data_manager import DataManager
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col,
    sort_by_periodo
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