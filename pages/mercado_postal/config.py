from config.endpoints import PostalEndpoints

SERVICIOS_COLS = [
    "postales",
    "telegraficas",
    "monetarios",
]

SERVICIOS_LABELS = {
    "postales": "Servicios postales",
    "telegraficas": "Servicios telegráficos",
    "monetarios": "Servicios monetarios",
}

DATASETS = {
    "facturacion": {
        "endpoint": PostalEndpoints.FACTURACION,
        "cols": ["anio", "mes"] + SERVICIOS_COLS,
    },
    "produccion": {
        "endpoint": PostalEndpoints.PRODUCCION,
        "cols": ["anio", "mes"] + SERVICIOS_COLS,
    },
    "personal": {
        "endpoint": PostalEndpoints.PERSONAL_OCUPADO,
        "cols": [
            "anio",
            "trimestre",
            "personal_ocupado",
        ],
    },
    "provincia": {
        "endpoint": PostalEndpoints.PROV_FACTURACION,
        "cols": [
            "anio",
            "trimestre",
            "provincia",
            "pesos",
            "unidades",
        ],
    },
}

RESUMEN_KPIS = [
    {
        "label": "Facturación postales ($)",
        "dataset": "facturacion",
        "column": "postales",
        "format": "{:,.0f}",
    },
    {
        "label": "Producción postales (unid.)",
        "dataset": "produccion",
        "column": "postales",
        "format": "{:,.0f}",
    },
    {
        "label": "Personal ocupado",
        "dataset": "personal",
        "column": "personal_ocupado",
        "format": "{:,.0f}",
    },
    {
        "label": "Facturación total ($)",
        "dataset": "facturacion",
        "type": "sum",
        "columns": [
            "postales",
            "telegraficas",
            "monetarios",
        ],
        "format": "{:,.0f}",
    },
]

FACTURACION_KPIS = [
    {
        "label": "Postales ($)",
        "column": "postales",
        "format": "{:,.0f}",
    },
    {
        "label": "Telegráficos ($)",
        "column": "telegraficas",
        "format": "{:,.0f}",
    },
    {
        "label": "Monetarios ($)",
        "column": "monetarios",
        "format": "{:,.0f}",
    },
    {
        "label": "Total ($)",
        "type": "sum",
        "columns": [
            "postales",
            "telegraficas",
            "monetarios",
        ],
        "format": "{:,.0f}",
    },
]