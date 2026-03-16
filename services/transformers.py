"""
transformers.py
───────────────
Transformaciones de pandas reutilizables entre páginas.

Reglas:
- Funciones puras: reciben DataFrame, devuelven DataFrame. Sin side effects.
- Sin imports de Streamlit acá. Esta capa no sabe nada de la UI.
- Cada función tiene una responsabilidad única y un nombre descriptivo.
"""

import pandas as pd


# ── Tiempo ────────────────────────────────────────────────────────────────────

def add_periodo_col(df: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega columna `periodo` combinando año y trimestre.
    Resultado: "2022-T1", "2022-T2", etc.

    Requiere columnas: `anio`, `trimestre`.
    """
    df = df.copy()
    df["periodo"] = df["anio"].astype(str) + "-T" + df["trimestre"].astype(str)
    return df


def sort_by_periodo(df: pd.DataFrame) -> pd.DataFrame:
    """Ordena el DataFrame cronológicamente por `anio` y `trimestre`."""
    return df.sort_values(["anio", "trimestre"]).reset_index(drop=True)


# ── Filtros ───────────────────────────────────────────────────────────────────

def filter_by_period(
    df: pd.DataFrame,
    anio: int,
    trimestre: int,
) -> pd.DataFrame:
    """Filtra filas para un año y trimestre específico."""
    return df[(df["anio"] == anio) & (df["trimestre"] == trimestre)].copy()


def filter_by_provincia(df: pd.DataFrame, provincia: str) -> pd.DataFrame:
    """Filtra por provincia. Si provincia es 'Todas', devuelve el DataFrame completo."""
    if provincia == "Todas":
        return df.copy()
    return df[df["provincia"] == provincia].copy()


# ── Formato largo (para gráficos de líneas con múltiples series) ──────────────

def melt_tecnologias(
    df: pd.DataFrame,
    value_cols: list[str],
    id_col: str = "periodo",
    var_name: str = "Tecnología",
    value_name: str = "Accesos",
) -> pd.DataFrame:
    """
    Convierte columnas de tecnologías a formato largo para Plotly.

    Parameters
    ----------
    df         : DataFrame con columna `periodo` y columnas de tecnología.
    value_cols : Lista de columnas a "derretir", ej. ["adsl","fibra_optica"].
    id_col     : Columna que identifica cada fila en el resultado.
    var_name   : Nombre de la columna variable en el resultado.
    value_name : Nombre de la columna de valores en el resultado.
    """
    return df.melt(
        id_vars=id_col,
        value_vars=value_cols,
        var_name=var_name,
        value_name=value_name,
    )


# ── Agregados ─────────────────────────────────────────────────────────────────

def aggregate_by_periodo(
    df: pd.DataFrame,
    value_cols: list[str],
    agg_func: str = "sum",
) -> pd.DataFrame:
    """
    Agrupa por `anio` + `trimestre`, aplica la función de agregación
    y devuelve con columna `periodo`.

    Útil cuando el CSV tiene filas por provincia y necesitás el total nacional.
    """
    grouped = (
        df.groupby(["anio", "trimestre"])[value_cols]
        .agg(agg_func)
        .reset_index()
    )
    return add_periodo_col(grouped)


def last_period_delta(
    df: pd.DataFrame,
    value_col: str,
) -> tuple[float, float]:
    """
    Calcula el valor del último período y la variación porcentual vs el anterior.

    Returns
    -------
    (valor_actual, delta_pct)
        delta_pct es positivo si creció, negativo si bajó, None si no hay período anterior.
    """
    df = sort_by_periodo(df.copy())

    # Forzar conversión numérica — la columna puede llegar como string
    # si la normalización del DataManager no la detectó (ej. puntos de miles mezclados)
    col = pd.to_numeric(
        df[value_col]
          .astype(str)
          .str.replace(".", "", regex=False)
          .str.replace(",", ".", regex=False),
        errors="coerce",
    )
    df[value_col] = col

    df = df.dropna(subset=[value_col])

    if len(df) < 1:
        return 0.0, None

    last_val = float(df[value_col].iloc[-1])

    if len(df) < 2:
        return last_val, None

    prev_val = float(df[value_col].iloc[-2])
    if prev_val == 0:
        return last_val, None

    delta_pct = (last_val - prev_val) / prev_val * 100
    return last_val, delta_pct