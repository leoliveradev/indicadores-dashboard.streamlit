import streamlit as st
from services.data_manager import DataManager
from services.data_validator import DataValidator
from services.transformers import (
  add_periodo_col, 
  sort_by_periodo,  
  melt_tecnologias
)
from pages.telefonia_fija.config import DATASETS


@st.cache_data
def load_dataset(dataset_key):
    if dataset_key not in DATASETS:
        raise ValueError(f"Dataset '{dataset_key}' no definido")

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

def get_last_period_composition(df, cols, labels):
    df_pie = df[cols].iloc[-1].rename(labels).reset_index()
    df_pie.columns = ["Segmento", "Valor"]
    return df_pie


def compute_yoy(df, col, periods=4):
    df = df.copy()
    df["yoy"] = df[col].pct_change(periods) * 100
    return df.dropna(subset=["yoy"])

