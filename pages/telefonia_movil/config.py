from config.endpoints import MovilEndpoints

# ─────────────────────────────────────────────
# MODALIDADES
# ─────────────────────────────────────────────

MODALIDADES_COLS = ["pospago", "prepago"]

MODALIDADES_LABELS = {
    "pospago": "Pospago",
    "prepago": "Prepago",
}

MODALIDAD_COLOR_MAP = {
    "Pospago": "#00B5E5",
    "Prepago": "#EEAE42",
}

# ─────────────────────────────────────────────
# DATASETS
# ─────────────────────────────────────────────

DATASETS = {
    "accesos": {
        "endpoint": MovilEndpoints.ACCESOS,
        "cols": ["anio", "trimestre"],
    },
    "ingresos": {
        "endpoint": MovilEndpoints.INGRESOS,
        "cols": ["anio", "trimestre"],
    },
    "minutos": {
        "endpoint": MovilEndpoints.MINUTOS,
        "cols": ["anio", "trimestre", "pospago", "prepago", "total"],
    },
    "llamadas": {
        "endpoint": MovilEndpoints.LLAMADAS,
        "cols": ["anio", "trimestre", "pospago", "prepago", "total"],
    },
    "sms": {
        "endpoint": MovilEndpoints.SMS,
        "cols": ["anio", "trimestre"],
    },
    "penetracion": {
        "endpoint": MovilEndpoints.PENETRACION,
        "cols": ["anio", "trimestre", "accesos_100_hab"],
    },
}

# ─────────────────────────────────────────────
# KPIS
# ─────────────────────────────────────────────

RESUMEN_KPIS = [
    {
        "label": "Líneas operativas",
        "dataset": "accesos",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Ingresos (miles $)",
        "dataset": "ingresos",
        "column": "ingresos",
        "format": "{:,.0f}",
    },
    {
        "label": "Minutos de voz",
        "dataset": "minutos",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Accesos c/100 hab.",
        "dataset": "penetracion",
        "column": "accesos_100_hab",
        "format": "{:.2f}",
    },
]

ACCESOS_KPIS = [
    {
        "label": "Líneas operativas",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Pospago",
        "column": "pospago",
        "format": "{:,.0f}",
    },
    {
        "label": "Prepago",
        "column": "prepago",
        "format": "{:,.0f}",
    },
    {
        "label": "% Pospago",
        "type": "ratio",
        "num": "pospago",
        "den": ["pospago", "prepago"],
        "format": "{:.1f}%",
    },
]

LLAMADAS_KPIS = [
    {
        "label": "Total llamadas",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Pospago",
        "column": "pospago",
        "format": "{:,.0f}",
    },
    {
        "label": "Prepago",
        "column": "prepago",
        "format": "{:,.0f}",
    },
    {
        "label": "% Pospago",
        "type": "ratio",
        "num": "pospago",
        "den": ["pospago", "prepago"],
        "format": "{:.1f}%",
    },
]

MINUTOS_KPIS = [
    {
        "label": "Total minutos",
        "column": "total",
        "format": "{:,.0f}",
    },
    {
        "label": "Pospago",
        "column": "pospago",
        "format": "{:,.0f}",
    },
    {
        "label": "Prepago",
        "column": "prepago",
        "format": "{:,.0f}",
    },
    {
        "label": "% Pospago",
        "type": "ratio",
        "num": "pospago",
        "den": ["pospago", "prepago"],
        "format": "{:.1f}%",
    },
]

SMS_KPIS = [
    {
        "label": "SMS enviados (miles)",
        "column": "total",
        "format": "{:,.0f}",
    },
]