from config.endpoints import (
    InternetEndpoints,
    MovilEndpoints,
    TVEndpoints,
    FijaEndpoints,
    PostalEndpoints,
)

from config.theme import ENACOM

# ============================================================
# COLORES
# ============================================================

COLOR_SERVICIO = {
    "Internet fijo": ENACOM["cyan"],
    "Telefonía móvil": ENACOM["yellow"],
    "TV por suscripción": ENACOM["green"],
    "Telefonía fija": ENACOM["deep_blue"],
    "Mercado postal": ENACOM["navy"],
}

# ============================================================
# DATASETS
# ============================================================

DATASETS = {
    "internet_accesos": {
        "endpoint": InternetEndpoints.TECNOLOGIAS,
        "cols": [
            "anio",
            "trimestre",
            "total",
        ],
    },
    "internet_penetracion": {
        "endpoint": InternetEndpoints.PENETRACION,
        "cols": [
            "anio",
            "trimestre",
            "accesos_cada_100_hogares",
        ],
    },
    "internet_ingresos": {
        "endpoint": InternetEndpoints.INGRESOS,
        "cols": [
            "anio",
            "trimestre",
        ],
    },

    "movil_accesos": {
        "endpoint": MovilEndpoints.ACCESOS,
        "cols": [
            "anio",
            "trimestre",
        ],
    },
    "movil_penetracion": {
        "endpoint": MovilEndpoints.PENETRACION,
        "cols": [
            "anio",
            "trimestre",
            "accesos_100_hab",
        ],
    },
    "movil_ingresos": {
        "endpoint": MovilEndpoints.INGRESOS,
        "cols": [
            "anio",
            "trimestre",
        ],
    },

    "tv_accesos": {
        "endpoint": TVEndpoints.ACCESOS,
        "cols": [
            "anio",
            "trimestre",
            "tv_suscripcion",
            "tv_satelital",
        ],
    },
    "tv_penetracion": {
        "endpoint": TVEndpoints.PENETRACION,
        "cols": [
            "anio",
            "trimestre",
            "tv_suscripcion_100_hogares",
        ],
    },
    "tv_ingresos": {
        "endpoint": TVEndpoints.INGRESOS,
        "cols": [
            "anio",
            "trimestre",
            "tv_suscripcion",
            "tv_satelital",
        ],
    },

    "fija_accesos": {
        "endpoint": FijaEndpoints.FIJA_ACCESOS,
        "cols": [
            "anio",
            "trimestre",
            "total",
        ],
    },
    "fija_penetracion": {
        "endpoint": FijaEndpoints.FIJA_PENETRACION,
        "cols": [
            "anio",
            "trimestre",
            "accesos_100_hog",
        ],
    },
    "fija_ingresos": {
        "endpoint": FijaEndpoints.FIJA_INGRESOS,
        "cols": [
            "anio",
            "trimestre",
            "ingresos",
        ],
    },

    "postal_facturacion": {
        "endpoint": PostalEndpoints.FACTURACION,
        "cols": [
            "anio",
            "mes",
        ],
    },
}