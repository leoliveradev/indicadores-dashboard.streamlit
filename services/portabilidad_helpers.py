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