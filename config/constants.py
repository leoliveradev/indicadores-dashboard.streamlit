# ── Columnas estándar esperadas ─────────────────
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
    "hasta_512_kbps", "entre_512_1mbps", "entre_1mbps_6mbps",
    "entre_6mbps_10mbps", "entre_10mbps_20mbps",
    "entre_20mbps_30mbps", "mayor_30mbps",
]
VELOCIDAD_RANGOS_LABELS = {
    "hasta_512_kbps":     "Hasta 512 Kbps",
    "entre_512_1mbps":    "512 Kbps–1 Mbps",
    "entre_1mbps_6mbps":  "1–6 Mbps",
    "entre_6mbps_10mbps": "6–10 Mbps",
    "entre_10mbps_20mbps":"10–20 Mbps",
    "entre_20mbps_30mbps":"20–30 Mbps",
    "mayor_30mbps":       "+30 Mbps",
}