from config.endpoints import FijaEndpoints

SEGMENTOS_COLS = ["hogares", "comercial", "gobierno", "otros"]

SEGMENTOS_LABELS = {
    "hogares": "Hogares",
    "comercial": "Comercial",
    "gobierno": "Gobierno",
    "otros": "Otros",
}

DATASETS = {
    "accesos": {
        "endpoint": FijaEndpoints.FIJA_ACCESOS,
        "cols": ["anio", "trimestre"] + SEGMENTOS_COLS + ["total"],
    },
    "ingresos": {
        "endpoint": FijaEndpoints.FIJA_INGRESOS,
        "cols": ["anio", "trimestre", "ingresos"],
    },
    "penetracion": {
        "endpoint": FijaEndpoints.FIJA_PENETRACION,
        "cols": ["anio", "trimestre", "accesos_100_hab", "accesos_100_hog"],
    },
    "accesos_provincia": {
        "endpoint": FijaEndpoints.FIJA_ACCESOS_PROVINCIA,
        "cols": [
            "anio", "trimestre", "provincia",
            "hogares", "comercial", "gobierno", "otros", "total"
        ],
    },
    "penetracion_provincia": {
        "endpoint": FijaEndpoints.FIJA_PENETRACION_PROVINCIA,
        "cols": [
            "anio", "trimestre", "provincia",
            "accesos_100_hab", "accesos_100_hog"
        ],
    },
}

RESUMEN_KPIS = [
    {
        "label": "Accesos totales",
        "dataset": "accesos",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Accesos Hogares",
        "dataset": "accesos",
        "column": "hogares",
        "format": "{:,.0f}",
    },
    {
        "label": "Ingresos (miles $)",
        "dataset": "ingresos",
        "column": "ingresos",
        "format": "{:,.0f}",
    },
    {
        "label": "Accesos c/100 hogares",
        "dataset": "penetracion",
        "column": "accesos_100_hog",
        "format": "{:.2f}",
    },
]

ACCESOS_KPIS = [
    {
        "label": "Total",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Hogares",
        "column": "hogares",
        "format": "{:,.0f}",
    },
    {
        "label": "Comercial",
        "column": "comercial",
        "format": "{:,.0f}",
    },
    {
        "label": "Gobierno",
        "column": "gobierno",
        "format": "{:,.0f}",
    },
    {
        "label": "% Hogares",
        "type": "ratio",
        "num": "hogares",
        "den": ["hogares", "comercial", "gobierno", "otros"],
        "format": "{:.1f}%",
    },
]

ACCESOS_PROV_KPIS = [
    {
        "label": "Total nacional",
        "column": "total",
        "agg": "sum",
        "format": "{:,.0f}",
    },
    {
        "label": "Penetración por provincia",
        "column": "total",
        "agg": "mean",
        "format": "{:,.0f}",
    },
]

PENETRACION_KPIS = [
    {
        "label": "Accesos c/100 habitantes",
        "column": "accesos_100_hab",
        "format": "{:.2f}",
    },
    {
        "label": "Accesos c/100 hogares",
        "column": "accesos_100_hog",
        "format": "{:.2f}",
    },
]

PENETRACION_PROV_KPIS = [
    {
        "label": "Nacional (hogares)",
        "column": "accesos_100_hog",
        "agg": "mean",
        "format": "{:.2f}",
    },
    {
        "label": "Nacional (habitantes)",
        "column": "accesos_100_hab",
        "agg": "mean",
        "format": "{:.2f}",
    },
]

INGRESOS_KPIS = [
    {
        "label": "Ingresos (miles $)",
        "column": "ingresos",
        "format": "{:,.0f}",
    },
]