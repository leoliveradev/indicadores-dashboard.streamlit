import streamlit as st

from services.data_manager import DataManager
from services.data_validator import DataValidator

from pages.portabilidad.config import DATASETS


def load_dataset(dataset_key):

    cfg = DATASETS[dataset_key]

    df = DataManager.load(cfg["endpoint"])

    DataValidator.validate(
        df,
        cfg["cols"],
    )

    return df

MESES = {
    1: "Ene",
    2: "Feb",
    3: "Mar",
    4: "Abr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dic",
}