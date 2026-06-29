from config.endpoints import TVEndpoints

DATASETS = {
    "accesos": {
        "endpoint": TVEndpoints.ACCESOS,
        "cols": ["anio", "trimestre", "tv_suscripcion", "tv_satelital"],
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
