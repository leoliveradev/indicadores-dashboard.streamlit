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

    if dataset_key == "accesos":

        for col in df.columns:
            col_lower = col.lower()

            if "operativo" in col_lower or "total" in col_lower:
                df["total"] = df[col]

            if "prepago" in col_lower:
                df["prepago"] = df[col]

            if "pospago" in col_lower:
                df["pospago"] = df[col]

    elif dataset_key == "sms":

        for col in df.columns:
            col_lower = col.lower()

            if (
                "sms" in col_lower
                or "mensaje" in col_lower
                or "total" in col_lower
            ):
                df["total"] = df[col]
                break

    elif dataset_key == "ingresos":

        for col in df.columns:
            col_lower = col.lower()

            if "ingreso" in col_lower or "miles" in col_lower:
                df["ingresos"] = df[col]
                
    return df

