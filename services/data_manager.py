"""
data_manager.py
───────────────
Única responsabilidad: cargar CSVs desde disco y cachearlos en memoria.

Reglas:
- Todo acceso a disco pasa por acá. Las páginas NUNCA hacen pd.read_csv directamente.
- El cache de Streamlit vive acá y en ningún otro lado.
- Si un archivo no existe o falla la lectura, lanza DataLoadError con mensaje claro.
"""

import pandas as pd
import streamlit as st

from config.settings import DATA_DIR, CSV_ENCODING, CSV_SEPARATOR


class DataLoadError(Exception):
    """Error controlado al cargar un CSV."""
    pass


class DataManager:

    @staticmethod
    @st.cache_data(show_spinner=False)
    def load(filename: str) -> pd.DataFrame:
        """
        Carga y cachea un CSV del directorio data/.

        Parameters
        ----------
        filename : str
            Nombre del archivo, ej. "internet_accesos_tecnologias.csv".
            Usar las constantes de config/constants.py, nunca strings literales.

        Returns
        -------
        pd.DataFrame
            DataFrame con columnas en minúsculas y strings sin espacios.

        Raises
        ------
        DataLoadError
            Si el archivo no existe o no puede parsearse.
        """
        filepath = DATA_DIR / filename

        if not filepath.exists():
            raise DataLoadError(
                f"Archivo no encontrado: `{filepath}`\n"
                f"Verificá que el archivo esté en `{DATA_DIR}`."
            )

        try:
            df = pd.read_csv(
                filepath,
                sep=CSV_SEPARATOR,
                encoding=CSV_ENCODING,
            )
        except Exception as exc:
            raise DataLoadError(
                f"Error al parsear `{filename}`: {exc}"
            ) from exc

        df = DataManager._normalize_dataframe(df)
        return df

    @staticmethod
    def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalización estándar aplicada a todos los DataFrames:
        - Columnas a minúsculas y sin espacios.
        - Strings sin espacios en blanco al inicio/fin.
        - Columnas numéricas que llegaron como string (puntos de miles).
        """
        # Columnas: minúsculas, sin espacios, sin caracteres raros
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(r"[^\w]", "_", regex=True)
        )

        # Strip de strings en columnas object
        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda c: c.str.strip())

        # Columnas numéricas que vienen con puntos de miles (ej. "1.234.567")
        for col in df.columns:
            if df[col].dtype == object:
                cleaned = df[col].str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
                try:
                    df[col] = pd.to_numeric(cleaned)
                except (ValueError, AttributeError):
                    pass  # No era numérica, se deja como está

        return df

    @staticmethod
    def clear_cache() -> None:
        """Limpia el cache de Streamlit. Útil en desarrollo."""
        st.cache_data.clear()