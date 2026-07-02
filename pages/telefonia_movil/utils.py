import streamlit as st

from services.data_manager import DataManager
from services.data_validator import DataValidator
from services.transformers import add_periodo_col, sort_by_periodo

from pages.telefonia_movil.config import DATASETS


@st.cache_data
def load_dataset(dataset_key):
    if dataset_key not in DATASETS:
        raise ValueError(f"Dataset '{dataset_key}' no definido")

    cfg = DATASETS[dataset_key]

    df = DataManager.load(cfg["endpoint"])
    DataValidator.validate(df, cfg["cols"])

    df = sort_by_periodo(add_periodo_col(df))

    df = normalize_columns(df, dataset_key)

    return df


# ─────────────────────────────────────────────
# NORMALIZACIÓN
# ─────────────────────────────────────────────

def normalize_columns(df, dataset_key):
    df = df.copy()

    # accesos / ingresos → nombres variables
    if dataset_key in ["accesos", "ingresos"]:
        for col in df.columns:
            col_lower = col.lower()

            if "total" in col_lower or "operativo" in col_lower:
                df["total"] = df[col]

            if "ingreso" in col_lower or "miles" in col_lower:
                df["ingresos"] = df[col]

    return df


# ─────────────────────────────────────────────
# MELT MODALIDADES 
# ─────────────────────────────────────────────

from services.transformers import melt_tecnologias


def melt_modalidad(df, value_name):
    df_long = melt_tecnologias(
        df,
        ["pospago", "prepago"],
        id_col="periodo",
        var_name="Modalidad",
        value_name=value_name,
    )

    df_long["Modalidad"] = df_long["Modalidad"].map({
        "pospago": "Pospago",
        "prepago": "Prepago",
    })

    return df_long
