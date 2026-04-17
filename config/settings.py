from pathlib import Path

# ── Rutas ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# ── Lectura de CSVs ────────────────────────────────────────────────────────
CSV_ENCODING = "utf-8"
CSV_SEPARATOR = ","

# ── App ────────────────────────────────────────────────────────────────────
APP_TITLE = "ENACOM - Indicadores"
APP_ICON = "📡"
APP_LAYOUT = "wide"
APP_VERSION = "1.0.0"