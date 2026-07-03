from config.endpoints import PortabilidadEndpoints

DATASETS = {
    "movil": {
        "endpoint": PortabilidadEndpoints.MOVIL,
        "cols": [
            "anio",
            "mes",
            "total",
        ],
    },
}


RESUMEN_KPIS = [
    {
        "label": "Portaciones (último trim.)",
        "dataset": "trimestral",
        "column": "total",
        "format": "{:,.0f}",
    },
]