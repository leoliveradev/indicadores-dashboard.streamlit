"""
Valida que un DataFrame tenga la forma esperada antes de que llegue a la UI.

Usar en cada página justo después de cargar el CSV:
    df = DataManager.load(InternetEndpoints.TECNOLOGIAS)
    DataValidator.validate(df, required_cols=["anio", "trimestre", "total"])
"""

import pandas as pd
import streamlit as st

class ValidationError(Exception):
    pass

class DataValidator:

    @staticmethod
    def validate(
        df: pd.DataFrame, 
        required_cols: list[str],
        context: str = ""
    ) -> None:
        """
        Varifica columnas requeridas y muestra un error en la UI si fallan.
        
        Parameters
        ----------
        :df:                DataFrame a validar
        :required_cols :    Lista de columnas que deben estar presentes en el DataFrame
        :context :          Nombre del CSV o sección (para el mensaje de error)

        Raises
        ------
        ValidationError si faltan columnas requeridas

        """
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            label = f" en `{context}`" if context else ""
            msg = (
                f"Columnas faltantes: `{missing_cols}`\n\n "
                f"Columnas disponibles: `{list(df.columns)}`"
            )
            st.error(msg, icon="❌")
            raise ValidationError(msg)
        
    @staticmethod
    def has_data(df: pd.DataFrame, filters: dict) -> bool:
        """
        Verifica que aplicar `filters` sobre `df` resulte en al menos una fila.
        Muestra advertencia en la UI si el resultado está vacío.

        Parameters
        ----------
        :df:        DataFrame ya cargado
        :filters:   Dict col -> valor, ej. {"anio": 2023, "trimestre": 1}

        Returns
        -------
        bool - True si hay datos, False si no.
        """

        mask = pd.Series([True] * len(df), index=df.index)
        for col, val in filters.items():
            if col in df.columns:
                mask &= (df[col] == val)

        if mask.sum() == 0:
            st.warning(
                f"No hay datos para los filtros seleccionados: {filters}",
                icon="⚠️"
            )
            return False

        return True