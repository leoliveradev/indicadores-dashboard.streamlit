from config.endpoints import InternetEndpoints

from config.constants import (
    TECNOLOGIAS_COLS,
    TECNOLOGIAS_LABELS,
    VELOCIDAD_RANGOS_COLS,
    VELOCIDAD_RANGOS_LABELS,
)

DATASETS = {
    "tecnologias": {
        "endpoint": InternetEndpoints.TECNOLOGIAS,
        "cols": [
            "anio",
            "trimestre",
            "total",
        ]
        + TECNOLOGIAS_COLS,
    },
    "penetracion": {
        "endpoint": InternetEndpoints.PENETRACION,
        "cols": [
            "anio",
            "trimestre",
            "accesos_cada_100_hogares",
            "accesos_cada_100_habitantes",
        ],
    },
    "velocidad_media": {
        "endpoint": InternetEndpoints.VELOCIDAD_MEDIA,
        "cols": [
            "anio",
            "trimestre",
            "mbps",
        ],
    },
    "velocidad_rangos": {
        "endpoint": InternetEndpoints.VELOCIDAD_RANGOS,
        "cols": [
            "anio",
            "trimestre",
        ]
        + VELOCIDAD_RANGOS_COLS,
    },
    "ingresos": {
        "endpoint": InternetEndpoints.INGRESOS,
        "cols": [
            "anio",
            "trimestre",
        ],
    },
    "baf": {
        "endpoint": InternetEndpoints.BAF,
        "cols": [
            "anio",
            "trimestre",
            "banda_ancha_fija",
            "dial_up",
            "total",
        ],
    },
}


RESUMEN_KPIS = [
    {
        "label": "Accesos totales",
        "dataset": "tecnologias",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Penetración c/100 hogares",
        "dataset": "penetracion",
        "column": "accesos_cada_100_hogares",
        "format": "{:.2f}",
    },
    {
        "label": "Penetración c/100 habitantes",
        "dataset": "penetracion",
        "column": "accesos_cada_100_habitantes",
        "format": "{:.2f}",
    },
    {
        "label": "Velocidad media actual",
        "dataset": "vmd",
        "column": "mbps",
        "format": "{:.2f} Mbps",
    },
]

VELOCIDAD_MEDIA_KPIS = [
    {
        "label": "Velocidad media actual",
        "column": "mbps",
        "format": "{:.2f} Mbps",
    },
]

TECNOLOGIA_KPIS = [
    {
        "label": "Total",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Fibra óptica",
        "column": "fibra_optica",
        "format": "{:,.0f}",
    },
    {
        "label": "Cablemodem",
        "column": "cablemodem",
        "format": "{:,.0f}",
    },
    {
        "label": "ADSL",
        "column": "adsl",
        "format": "{:,.0f}",
    },
]

BAF_KPIS = [
    {
        "label": "Banda ancha fija",
        "column": "banda_ancha_fija",
        "format": "{:,.0f}",
    },
    {
        "label": "Dial-up",
        "column": "dial_up",
        "format": "{:,.0f}",
    },
    {
        "label": "Total",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "% Banda ancha",
        "type": "ratio",
        "num": "banda_ancha_fija",
        "den": ["total"],
        "format": "{:.2f}%",
    },
]