import pandas as pd

from services.aggregation_helpers import mensual_a_trimestral
from services.data_manager import DataManager
from services.data_validator import DataValidator

from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
)

from pages.comparativa.config import DATASETS


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

    # =====================================================
    # INGRESOS INTERNET / MOVIL
    # =====================================================

    if dataset_key in [
        "internet_ingresos",
        "movil_ingresos",
        "fija_ingresos",
    ]:
        if "ingresos" in df.columns:
            return df

        for col in df.columns:

            col_lower = col.lower()

            if (
                "ingreso" in col_lower
                or "ingresos" in col_lower
                or "miles" in col_lower
                or "monto" in col_lower
            ):
                df["ingresos"] = df[col]
                break

    # =====================================================
    # TV ACCESOS
    # =====================================================

    elif dataset_key == "tv_accesos":

        if (
            "tv_suscripcion" in df.columns
            and "tv_satelital" in df.columns
        ):

            df["total"] = (
                df["tv_suscripcion"]
                + df["tv_satelital"]
            )

    # =====================================================
    # TV INGRESOS
    # =====================================================

    elif dataset_key == "tv_ingresos":

        if (
            "tv_suscripcion" in df.columns
            and "tv_satelital" in df.columns
        ):

            df["ingresos"] = (
                df["tv_suscripcion"]
                + df["tv_satelital"]
            )
    # =====================================================
    # ACCESOS MOVIL
    # =====================================================
    elif dataset_key == "movil_accesos":

        for col in df.columns:

            col_lower = col.lower()

            if (
                "operativos" in col_lower
                or "total" in col_lower
            ):
                df["total"] = df[col]
                break

    # =====================================================
    # POSTAL
    # =====================================================

    elif dataset_key == "postal_facturacion":

      cols = [
          c
          for c in [
              "postales",
              "telegraficas",
              "monetarios",
          ]
          if c in df.columns
      ]

      if "mes" in df.columns:

          df = mensual_a_trimestral(
              df,
              cols,
          )

      df["ingresos"] = df[cols].sum(axis=1)
      df["total"] = df["ingresos"]

    return df


def indice_base_100(
    df_long: pd.DataFrame,
    base_anio: int,
) -> pd.DataFrame:
    """
    Normaliza cada serie a base 100 usando el primer período
    disponible del año seleccionado.

    Requiere columnas:
        - periodo
        - Servicio
        - valor
    """

    result = []

    for servicio, grupo in df_long.groupby("Servicio"):

        grupo = (
            grupo
            .sort_values("periodo")
            .copy()
        )

        base_rows = grupo[
            grupo["periodo"].str.startswith(
                str(base_anio)
            )
        ]

        if base_rows.empty:
            continue

        base_val = base_rows["valor"].iloc[0]

        if base_val == 0:
            continue

        grupo["indice"] = (
            grupo["valor"]
            / base_val
            * 100
        ).round(2)

        result.append(grupo)

    if not result:
        return pd.DataFrame()

    return pd.concat(
        result,
        ignore_index=True,
    )