from services.data_manager import DataManager
from services.data_validator import DataValidator

from pages.mercado_postal.config import (
    DATASETS,
    SERVICIOS_LABELS,
)

from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
    melt_tecnologias,
)

def load_dataset(dataset_key):

    cfg = DATASETS[dataset_key]

    df = DataManager.load(
        cfg["endpoint"]
    )

    DataValidator.validate(
        df,
        cfg["cols"],
    )

    if "trimestre" in df.columns:
        df = sort_by_periodo(
            add_periodo_col(df)
        )

    return df

def limpiar_provincias(df):

    df = df.copy()

    df["provincia"] = (
        df["provincia"]
        .str.strip()
        .replace({
            "Rio Negro": "Río Negro",
        })
    )

    return df



def melt_servicios(
    df,
    value_name,
):
    df_long = melt_tecnologias(
        df,
        ["postales", "telegraficas", "monetarios"],
        id_col="periodo",
        var_name="Servicio",
        value_name=value_name,
    )

    df_long["Servicio"] = (
        df_long["Servicio"]
        .map(SERVICIOS_LABELS)
    )

    return df_long