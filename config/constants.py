# ── Nombres de archivos CSV por servicio ─────────────────────────────────────
# Centralizar acá evita strings dispersos por todo el código.
# Si renombrás un archivo, lo cambiás en un solo lugar.

class InternetCSV:
    TECNOLOGIAS         = "internet_accesos_tecnologias.csv"
    VELOCIDAD_RANGOS    = "internet_accesos_velocidad_rangos.csv"
    VELOCIDAD_MEDIA     = "internet_velocidad_media_descarga.csv"
    BANDA_ANCHA_DIALUP  = "internet_banda_ancha_dialup.csv"
    PENETRACION         = "internet_accesos_penetracion.csv"
    INGRESOS            = "internet_ingresos.csv"
    ACCESOS_PROVINCIA   = "internet_accesos_provincia.csv"
    ACCESOS_LOCALIDAD   = "internet_accesos_localidad.csv"
    VELOCIDAD_PROVINCIA = "internet_velocidad_provincia.csv"

    TECNOLOGIAS_PROVINCIA     = "internet_accesos_tecnologias_provincias.csv"
    PENETRACION_PROVINCIA     = "internet_accesos_penetracion_provincias.csv"
    VELOCIDAD_MEDIA_PROVINCIA = "internet_velocidad_media_descarga_provincias.csv"
    VELOCIDAD_RANGOS_PROVINCIA= "internet_accesos_velocidad_rangos_provincias.csv"
    BAF_PROVINCIA             = "internet_accesos_baf_provincias.csv"


class MovilCSV:
    ACCESOS  = "comunicaciones_moviles_accesos.csv"
    INGRESOS = "comunicaciones_moviles_ingresos.csv"
    MINUTOS  = "comunicaciones_moviles_minutos.csv"
    SMS      = "comunicaciones_moviles_sms.csv"


class TVCSVs:
    ACCESOS  = "tv_accesos.csv"
    INGRESOS = "tv_ingresos.csv"


class TelefoniaCSV:
    FIJA_ACCESOS  = "telefonia_fija_accesos.csv"
    FIJA_INGRESOS = "telefonia_fija_ingresos.csv"
    FIJA_PENETRACION  = "telefonia_fija_penetracion.csv"
    FIJA_PENETRACION_PROVINCIAS  = "telefonia_fija_penetracion_provincias.csv"


class PostalCSV:
    FACTURACION   = "mercado_postal_facturacion.csv"
    PRODUCCION = "mercado_postal_produccion.csv"
    PERSONAL_OCUPADO = "mercado_postal_personal_ocupado.csv"


# ── Columnas estándar esperadas en todos los CSVs temporales ─────────────────
COL_ANIO      = "anio"
COL_TRIMESTRE = "trimestre"
COL_PROVINCIA = "provincia"

# ── Columnas de internet / tecnología ────────────────────────────────────────
TECNOLOGIAS_COLS = ["adsl", "cablemodem", "fibra_optica", "wireless", "otros"]
TECNOLOGIAS_LABELS = {
    "adsl":        "ADSL",
    "cablemodem":  "Cablemodem",
    "fibra_optica":"Fibra óptica",
    "wireless":    "Wireless",
    "otros":       "Otros",
    "total":       "Total",
}

# ── Provincias (para ordenar y filtrar consistentemente) ─────────────────────
PROVINCIAS_ARG = [
    "Buenos Aires", "CABA", "Catamarca", "Chaco", "Chubut", "Córdoba",
    "Corrientes", "Entre Ríos", "Formosa", "Jujuy", "La Pampa", "La Rioja",
    "Mendoza", "Misiones", "Neuquén", "Río Negro", "Salta", "San Juan",
    "San Luis", "Santa Cruz", "Santa Fe", "Santiago del Estero",
    "Tierra del Fuego", "Tucumán",
]

# ── Rangos de velocidad ───────────────────────────────────────────────────────
VELOCIDAD_RANGOS_COLS = [
    "hasta_512kbps", "entre_512_1mbps", "entre_1mbps_6mbps",
    "entre_6mbps_10mbps", "entre_10mbps_20mbps",
    "entre_20mbps_30mbps", "mayor_30mbps",
]
VELOCIDAD_RANGOS_LABELS = {
    "hasta_512kbps":      "Hasta 512 Kbps",
    "entre_512_1mbps":    "512 Kbps–1 Mbps",
    "entre_1mbps_6mbps":  "1–6 Mbps",
    "entre_6mbps_10mbps": "6–10 Mbps",
    "entre_10mbps_20mbps":"10–20 Mbps",
    "entre_20mbps_30mbps":"20–30 Mbps",
    "mayor_30mbps":       "+30 Mbps",
}