from services.transformers import (
    add_periodo_col,
    sort_by_periodo,
)


def mensual_a_trimestral(df):
    """
    Convierte una serie mensual en trimestral
    sumando las portaciones por trimestre.
    """

    df = df.copy()

    df["trimestre"] = (
        (df["mes"] - 1) // 3
    ) + 1

    return (
        df.groupby(
            ["anio", "trimestre"]
        )["total"]
        .sum()
        .reset_index()
        .pipe(
            lambda d: sort_by_periodo(
                add_periodo_col(d)
            )
        )
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


def add_mes_col(df):
    """
    Agrega periodo mensual YYYY-MM.
    """

    df = df.copy()

    df["periodo"] = (
        df["anio"].astype(str)
        + "-"
        + df["mes"].astype(str).str.zfill(2)
    )

    return df