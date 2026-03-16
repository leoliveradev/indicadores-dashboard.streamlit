from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ── Lectura de CSVs ────────────────────────────────────────────────────────
CSV_ENCODING = "cp1252"
CSV_SEPARATOR = ","

# ── App ────────────────────────────────────────────────────────────────────
APP_TITLE = "Indicadores - ENACOM"
APP_ICON = "📡"
APP_LAYOUT = "wide"
APP_VERSION = "1.0.0"