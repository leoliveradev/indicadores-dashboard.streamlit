def build_max_kpi(
    df,
    column,
    label="Máximo histórico",
    fmt="{:,.0f}",
    period_col="periodo",
):
    """
    Genera un KPI con el valor máximo histórico y su período.
    """
    idx = df[column].idxmax()

    return {
        "label": f"{label} ({df.loc[idx, period_col]})",
        "value": df.loc[idx, column],
        "format": fmt,
    }


def build_growth_kpi(
    df,
    column,
    label="Variación acumulada",
    fmt="{:+.1f}%",
    help_text=None,
):
    """
    Calcula variación entre primer y último valor.
    """
    if len(df) < 2:
        growth = None
    else:
        first = df[column].iloc[0]
        last = df[column].iloc[-1]

        growth = (
            (last - first) / first * 100
            if first
            else None
        )

    return {
        "label": label,
        "value": growth,
        "format": fmt,
        "help": help_text,
    }