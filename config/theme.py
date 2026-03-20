# ── Paleta institucional ENACOM ───────────────────────────────────────────────
# Fuente: sitio oficial de ENACOM (área de institucionales)

ENACOM = {
    # Principal
    "primary":      "#0B1742",   # Azul marino oscuro — fondo, headers
    "white":        "#FFFFFF",
    "light_gray":   "#C6C6C6",

    # Acentos
    "yellow":       "#EEAE42",   # Llamadas a la acción, alertas
    "red":          "#E74242",   # Caídas, variaciones negativas
    "green":        "#ACAE22",   # Crecimiento, variaciones positivas

    # Secundarios
    "light_yellow": "#FFF3D8",   # Fondos suaves de advertencia
    "light_blue":   "#BCE4F4",   # Fondos suaves informativos
    "cyan":         "#00B5E5",   # Highlights, links, series principales
    "blue":         "#0074A6",   # Series secundarias
    "deep_blue":    "#005297",   # Series terciarias
    "navy":         "#003667",   # Series cuaternarias / bordes
}

# ── Mapeo de tecnologías de internet ─────────────────────────────────────────
COLORS = {
    # Tecnologías — del más al menos relevante por adopción actual
    "fibra_optica": ENACOM["cyan"],       # protagonista
    "cablemodem":   ENACOM["blue"],
    "wireless":     ENACOM["deep_blue"],
    "adsl":         ENACOM["light_gray"], # en declive
    "otros":        ENACOM["navy"],
    "total":        ENACOM["primary"],

    # Modalidades móviles
    "prepago":      ENACOM["yellow"],
    "pospago":      ENACOM["cyan"],

    # Semánticos — usados en KPIs y deltas
    "positive":     ENACOM["green"],
    "negative":     ENACOM["red"],
    "neutral":      ENACOM["light_gray"],
    "primary":      ENACOM["primary"],
    "secondary":    ENACOM["blue"],
}

# Secuencia por defecto para gráficos multi-serie sin mapeo explícito
COLOR_SEQUENCE = [
    ENACOM["cyan"],
    ENACOM["blue"],
    ENACOM["deep_blue"],
    ENACOM["navy"],
    ENACOM["yellow"],
    ENACOM["green"],
    ENACOM["red"],
    ENACOM["light_gray"],
]

# ── Layout base Plotly ────────────────────────────────────────────────────────
PLOTLY_BASE_LAYOUT = {
    "font": {
        "family": "Inter, Arial, sans-serif",
        "size":   13,
        "color":  ENACOM["primary"],
    },
    "plot_bgcolor":  "rgba(0,0,0,0)",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "margin": {"t": 48, "b": 80, "l": 48, "r": 20},
    "colorway": COLOR_SEQUENCE,
    "xaxis": {
        "showgrid":    True,
        "gridcolor":   "#E8E8E8",
        "linecolor":   ENACOM["light_gray"],
        "tickfont":    {"color": ENACOM["primary"]},
        "title_font":  {"color": ENACOM["primary"]},
    },
    "yaxis": {
        "showgrid":            True,
        "gridcolor":           "#E8E8E8",
        "linecolor":           ENACOM["light_gray"],
        "tickformat":          ",.0f",
        "separatethousands":   True,
        "tickfont":            {"color": ENACOM["primary"]},
        "title_font":          {"color": ENACOM["primary"]},
    },
    "legend": {
        "orientation": "h",
        "yanchor":     "top",
        "y":           -0.30,
        "xanchor":     "left",
        "x":           0,
        "font":        {"color": ENACOM["primary"]},
        "bgcolor":     "rgba(0,0,0,0)",
    },
    "title": {
        "font": {"color": ENACOM["primary"], "size": 15},
        "x": 0,
        "xanchor": "left",
        "pad": {"b": 8},
    },
    "hovermode": "x unified",
    "hoverlabel": {
        "bgcolor":    ENACOM["primary"],
        "font_color": ENACOM["white"],
        "bordercolor": ENACOM["navy"],
    },
}

# ── CSS inyectable en Streamlit ───────────────────────────────────────────────
# Llamar con: st.markdown(STREAMLIT_CSS, unsafe_allow_html=True)
# Recomendado en app.py para aplicarlo globalmente.

STREAMLIT_CSS = f"""
<style>
    /* Sidebar — fondo general */
    [data-testid="stSidebar"] {{
        background-color: {ENACOM['primary']};
    }}
    [data-testid="stSidebar"] * {{
        color: {ENACOM['white']} !important;
    }}
    [data-testid="stSidebar"] hr {{
        border-color: {ENACOM['navy']} !important;
    }}

    /* Selectbox dentro del sidebar — fondo del campo */
    [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {{
        background-color: {ENACOM['navy']} !important;
        border-color: {ENACOM['deep_blue']} !important;
        border-radius: 6px !important;
    }}
    /* Texto del valor seleccionado */
    [data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-baseweb="select"] div {{
        color: {ENACOM['white']} !important;
    }}
    /* Ícono de flecha del desplegable */
    [data-testid="stSidebar"] [data-baseweb="select"] svg {{
        fill: {ENACOM['light_gray']} !important;
    }}
    /* Hover sobre el campo */
    [data-testid="stSidebar"] [data-baseweb="select"] > div:first-child:hover {{
        border-color: {ENACOM['cyan']} !important;
    }}
    /* Lista desplegable (el popover sale fuera del sidebar) */
    [data-baseweb="popover"] [data-baseweb="menu"] {{
        background-color: {ENACOM['navy']} !important;
        border: 1px solid {ENACOM['deep_blue']} !important;
        border-radius: 6px !important;
    }}
    [data-baseweb="popover"] [role="option"] {{
        background-color: {ENACOM['navy']} !important;
        color: {ENACOM['white']} !important;
    }}
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [aria-selected="true"] {{
        background-color: {ENACOM['deep_blue']} !important;
        color: {ENACOM['white']} !important;
    }}

    /* Métricas (KPI cards) */
    [data-testid="stMetric"] {{
        background-color: {ENACOM['light_blue']};
        border-left: 4px solid {ENACOM['cyan']};
        border-radius: 6px;
        padding: 12px 16px;
    }}
    [data-testid="stMetricLabel"] {{
        color: {ENACOM['deep_blue']} !important;
        font-size: 12px !important;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    [data-testid="stMetricValue"] {{
        color: {ENACOM['primary']} !important;
        font-weight: 700;
    }}
    [data-testid="stMetricDelta"] svg {{
        fill: currentColor;
    }}

    /* Tabs */
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        color: {ENACOM['cyan']} !important;
        border-bottom-color: {ENACOM['cyan']} !important;
        font-weight: 600;
    }}

    /* Divider */
    hr {{
        border-color: {ENACOM['light_gray']};
        opacity: 0.4;
    }}

    /* Títulos */
    h1, h2, h3 {{
        color: {ENACOM['primary']} !important;
    }}

    /* Info / warning boxes */
    [data-testid="stAlert"] {{
        border-radius: 6px;
    }}
</style>
"""