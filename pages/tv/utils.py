from services.data_manager import DataManager
from services.data_validator import DataValidator
from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
    last_period_delta,
)
import streamlit as st

from pages.tv.config import DATASETS

@st.cache_data
def load_dataset(dataset_key):
    cfg = DATASETS[dataset_key]

    df = DataManager.load(cfg["endpoint"])
    DataValidator.validate(df, cfg["cols"])

    return sort_by_periodo(add_periodo_col(df))


# ✅ helpers seguros
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
