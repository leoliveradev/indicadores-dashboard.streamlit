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
    "tecnologias_provincia": {
        "endpoint": InternetEndpoints.TECNOLOGIAS_PROVINCIA,
        "cols": [
            "anio",
            "trimestre",
            "provincia",
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
    "velocidad_media_provincia": {
        "endpoint": InternetEndpoints.VELOCIDAD_MEDIA_PROVINCIA,
        "cols": [
            "anio",
            "trimestre",
            "provincia",
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

TECNOLOGIA_PROVINCIA_KPIS = [
    {
        "label": "Total nacional",
        "column": "total",
        "agg": "sum",
        "format": "{:,.0f}",
    },
    {
        "label": "Fibra óptica",
        "column": "fibra_optica",
        "agg": "sum",
        "format": "{:,.0f}",
    },
    {
        "label": "Cablemodem",
        "column": "cablemodem",
        "agg": "sum",
        "format": "{:,.0f}",
    },
    {
        "label": "ADSL",
        "column": "adsl",
        "agg": "sum",
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

PENETRACION_KPIS = [
    {
        "label": "Accesos c/100 hogares",
        "column": "accesos_cada_100_hogares",
        "format": "{:.2f}",
    },
    {
        "label": "Accesos c/100 habitantes",
        "column": "accesos_cada_100_habitantes",
        "format": "{:.2f}",
    },
]

RANGOS_KPIS = [
    {
        "label": "Total accesos",
        "type": "sum",
        "columns": VELOCIDAD_RANGOS_COLS,
        "format": "{:,.0f}",
    },
    {
        "label": "+30 Mbps",
        "column": "mayor_30mbps",
        "format": "{:,.0f}",
    },
    {
        "label": "% +30 Mbps",
        "type": "ratio",
        "num": "mayor_30mbps",
        "den": VELOCIDAD_RANGOS_COLS,
        "format": "{:.2f}%",
    },
    {
        "label": "Hasta 1 Mbps",
        "type": "sum",
        "columns": [
            "hasta_512_kbps",
            "entre_512_1mbps",
        ],
        "format": "{:,.0f}",
    },
]
