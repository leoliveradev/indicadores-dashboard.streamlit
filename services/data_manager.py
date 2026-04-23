import pandas as pd
import streamlit as st
import requests
from config.settings import API_BASE_URL, TIMEOUT_CONEXION

class DataLoadError(Exception):
    """Error controlado al cargar datos desde la API."""
    pass

class DataManager:

    @staticmethod
    @st.cache_data(show_spinner="Conectando con la API de ENACOM...", ttl=3600)
    def load(endpoint: str) -> pd.DataFrame:

        url = f"{API_BASE_URL}/{endpoint}"
        
        try:
            response = requests.get(url, timeout=TIMEOUT_CONEXION)
            response.raise_for_status() # Lanza error si no es 200 OK
            
            json_response = response.json()
        
            if isinstance(json_response, dict) and "data" in json_response:
                raw_data = json_response["data"]
            else:
                raw_data = json_response

            df = pd.DataFrame(raw_data)

            if df.empty:
                raise DataLoadError(f"Sin datos para: `{endpoint}`")

        except Exception as exc:
            raise DataLoadError(f"Error al procesar `{endpoint}`: {exc}")

        return DataManager._normalize_dataframe(df)

    @staticmethod
    def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:

        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace(r"[^\w]", "_", regex=True)
            .str.strip("_")
        )

        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda c: c.str.strip() if hasattr(c, 'str') else c)

        for col in df.columns:
            if df[col].dtype == object:
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, AttributeError):
                    pass
        return df

    @staticmethod
    def clear_cache() -> None:
        st.cache_data.clear()