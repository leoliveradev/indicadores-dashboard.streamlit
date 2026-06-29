from config.endpoints import TVEndpoints

DATASETS = {
    "accesos": {
        "endpoint": TVEndpoints.ACCESOS,
        "cols": ["anio", "trimestre", "tv_suscripcion", "tv_satelital"],
    },
    "accesos_provincia": {
        "endpoint": TVEndpoints.ACCESOS_PROVINCIA,
        "cols": ["anio", "trimestre", "provincia", "tv_suscripcion"],
    },
    "ingresos": {
        "endpoint": TVEndpoints.INGRESOS,
        "cols": ["anio", "trimestre", "tv_suscripcion", "tv_satelital"],
    },
    "penetracion": {
        "endpoint": TVEndpoints.PENETRACION,
        "cols": [
            "anio", "trimestre",
            "tv_suscripcion_100_hogares",
            "tv_satelital_100_hogares",
        ],
    },
}

RESUMEN_KPIS = [
    {
        "label": "Accesos totales",
        "dataset": "accesos",
        "type": "sum",
        "columns": ["tv_suscripcion", "tv_satelital"],
        "format": "{:,.0f}",
    },
    {
        "label": "Ingresos totales (miles $)",
        "dataset": "ingresos",
        "type": "sum",
        "columns": ["tv_suscripcion", "tv_satelital"],
        "format": "{:,.0f}",
    },
    {
        "label": "Penetración total (c/100 hogares)",
        "dataset": "penetracion",
        "type": "sum",
        "columns": [
            "tv_suscripcion_100_hogares",
            "tv_satelital_100_hogares",
        ],
        "format": "{:.2f}",
    },
]

TV_COLOR_MAP = {
    "TV suscripción": "#00B5E5",
    "TV satelital": "#EEAE42",
}

ACCESOS_KPIS = [
    {
        "label": "Accesos totales",
        "type": "sum",
        "columns": ["tv_suscripcion", "tv_satelital"],
        "format": "{:,.0f}",
    },
    {
        "label": "TV suscripción",
        "column": "tv_suscripcion",
        "format": "{:,.0f}",
    },
    {
        "label": "TV satelital",
        "column": "tv_satelital",
        "format": "{:,.0f}",
    },
    {
        "label": "% Suscripción",
        "type": "ratio",
        "num": "tv_suscripcion",
        "den": ["tv_suscripcion", "tv_satelital"],
        "format": "{:.1f}%",
    },
]

def build_kpis_agg(kpi_config, df):
    kpis = []

    for cfg in kpi_config:
        col = cfg["column"]

        if cfg["agg"] == "sum":
            val = df[col].sum()

        elif cfg["agg"] == "mean":
            val = df[col].mean()

        else:
            raise ValueError(f"agg no soportado: {cfg['agg']}")

        kpis.append({
            "label": cfg["label"],
            "value": val,
            "format": cfg["format"],
        })

    return kpis

ACCESOS_PROV_KPIS = [
    {
        "label": "Total nacional",
        "column": "tv_suscripcion",
        "agg": "sum",
        "format": "{:,.0f}",
    },
    {
        "label": "Promedio por provincia",
        "column": "tv_suscripcion",
        "agg": "mean",
        "format": "{:,.0f}",
    },
]