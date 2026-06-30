import streamlit as st
from services.data_manager import DataManager
from services.data_validator import DataValidator
from services.transformers import add_periodo_col, sort_by_periodo, last_period_delta, melt_tecnologias

import plotly.graph_objects as go

from pages.telefonia_fija.config import DATASETS


@st.cache_data
def load_dataset(dataset_key):
    if dataset_key not in DATASETS:
        raise ValueError(f"Dataset '{dataset_key}' no definido")

    cfg = DATASETS[dataset_key]

    df = DataManager.load(cfg["endpoint"])
    DataValidator.validate(df, cfg["cols"])

    return sort_by_periodo(add_periodo_col(df))


def apply_operation(df, cfg):
    df = df.copy()

    if cfg.get("type") == "sum":
        df["_metric"] = sum(df[col] for col in cfg["columns"])

    elif cfg.get("type") == "ratio":
        total = sum(df[col] for col in cfg["den"])
        df["_metric"] = (df[cfg["num"]] / total) * 100

    else:
        df["_metric"] = df[cfg["column"]]

    return df, "_metric"


def build_kpis(kpi_config, datasets, default_dataset=None):
    kpis = []

    for cfg in kpi_config:
        dataset_key = cfg.get("dataset", default_dataset)

        if dataset_key is None:
            raise ValueError("KPI sin dataset")

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


def melt_segmentos(df, segmentos_cols, labels, id_col="periodo"):

    if id_col not in df.columns:
        raise ValueError(f"{id_col} no está en el dataframe")

    df_long = melt_tecnologias(
        df,
        segmentos_cols,
        id_col=id_col,
        var_name="Segmento",
        value_name="Accesos",
    )

    df_long["Segmento"] = df_long["Segmento"].map(labels)

    return df_long


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

def get_last_period_composition(df, cols, labels):
    df_pie = df[cols].iloc[-1].rename(labels).reset_index()
    df_pie.columns = ["Segmento", "Valor"]
    return df_pie


def compute_yoy(df, col, periods=4):
    df = df.copy()
    df["yoy"] = df[col].pct_change(periods) * 100
    return df.dropna(subset=["yoy"])

