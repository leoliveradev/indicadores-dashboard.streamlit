from services.data_manager import DataManager
from services.data_validator import DataValidator

from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
)

from pages.internet.config import DATASETS


def load_dataset(dataset_key):

    cfg = DATASETS[dataset_key]

    df = DataManager.load(
        cfg["endpoint"]
    )

    DataValidator.validate(
        df,
        cfg["cols"],
    )

    if (
        "anio" in df.columns
        and "trimestre" in df.columns
    ):
        df = sort_by_periodo(
            add_periodo_col(df)
        )

    return normalize_columns(
        df,
        dataset_key,
    )


def normalize_columns(
    df,
    dataset_key,
):
    df = df.copy()

    if dataset_key == "ingresos":

        for col in df.columns:

            col_lower = col.lower()

            if (
                "ingreso" in col_lower
                or "miles" in col_lower
                or "monto" in col_lower
            ):
                df["ingresos"] = df[col]
                break

    return df