from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
)

def mensual_a_trimestral(
    df,
    value_cols,
):

    if isinstance(value_cols, str):
        value_cols = [value_cols]

    df = df.copy()

    df["trimestre"] = (
        (df["mes"] - 1) // 3
    ) + 1

    grouped = (
        df.groupby(
            ["anio", "trimestre"]
        )[value_cols]
        .sum()
        .reset_index()
    )

    return sort_by_periodo(
        add_periodo_col(grouped)
    )

def mensual_a_anual(df):
    """
    Convierte una serie mensual en anual
    sumando las portaciones del año.
    """

    return (
        df.groupby("anio")["total"]
        .sum()
        .reset_index()
        .sort_values("anio")
    )