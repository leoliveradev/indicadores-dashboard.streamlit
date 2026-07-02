
# ─────────────────────────────────────────────
# MELT MODALIDADES 
# ─────────────────────────────────────────────

from services.transformers import melt_tecnologias


def melt_modalidad(df, value_name):
    df_long = melt_tecnologias(
        df,
        ["pospago", "prepago"],
        id_col="periodo",
        var_name="Modalidad",
        value_name=value_name,
    )

    df_long["Modalidad"] = df_long["Modalidad"].map({
        "pospago": "Pospago",
        "prepago": "Prepago",
    })

    return df_long


def melt_segmentos(df, segmentos_cols, labels, id_col="periodo"):

    if id_col not in df.columns:
        raise ValueError(f"{id_col} no está en el dataframe")

    df_long = melt_tecnologias(
        df,
        segmentos_cols,
        id_col=id_col,
        var_name="Segmento",
        value_name="Accesos",
    )

    df_long["Segmento"] = df_long["Segmento"].map(labels)

    return df_long

def split_tipo(df, value_name, label_map=None):
    df_long = melt_tecnologias(
        df,
        ["tv_suscripcion", "tv_satelital"],
        id_col="periodo",
        var_name="Tipo",
        value_name=value_name,
    )

    df_long["Tipo"] = df_long["Tipo"].map({
        "tv_suscripcion": "TV suscripción",
        "tv_satelital": "TV satelital",
    })

    if label_map is None:
        label_map = {
            "tv_suscripcion": "TV suscripción",
            "tv_satelital": "TV satelital",
        }

    return df_long