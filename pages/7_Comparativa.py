"""
7_Comparativa.py
────────────────
Vista transversal: compara métricas entre todos los servicios.

Secciones:
1. Ingresos por servicio  — Internet, Móvil, TV, Tel. fija, Postal
2. Accesos por servicio   — escala absoluta + índice base 100
3. Penetración comparada  — c/100 hogares (Internet, TV, Tel. fija) y c/100 hab. (Móvil)
4. Crecimiento relativo   — todos los accesos normalizados a base 100

Patrones de carga:
- TV ingresos/accesos: suma suscripción + satelital
- Postal: agrega mensual a trimestral, suma los 3 servicios
- Carga silenciosa (try_load): si un CSV no existe, la sección sigue con los disponibles
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from config.constants import (
    InternetCSV, MovilCSV, TVCSVs, TelefoniaCSV, PostalCSV,
)
from config.theme import ENACOM
from services.data_manager import DataManager, DataLoadError
from services.transformers import add_periodo_col, sort_by_periodo, last_period_delta
from components.page_setup import setup_page
from components.sidebar import render_sidebar
from components.kpi_cards import show_kpis
from components.charts import line_chart, bar_chart


st.set_page_config(page_title="Comparativa · ENACOM", page_icon="📊", layout="wide")
setup_page()

CATEGORIES = [
    "Accesos por servicio",
    "Penetración comparada",
    "Crecimiento relativo",
    "Ingresos por servicio",
]

# Colores fijos por servicio — consistentes en toda la página
COLOR_SERVICIO = {
    "Internet fijo": ENACOM["cyan"],
    "Telefonía móvil": ENACOM["yellow"],
    "TV por suscripción": ENACOM["green"],
    "Telefonía fija": ENACOM["deep_blue"],
    "Mercado postal": ENACOM["navy"],
}

categoria = render_sidebar(CATEGORIES, key="comp_categoria")
st.title("📊 Comparativa entre servicios")


# ── Helpers ───────────────────────────────────────────────────────────────────

def try_load(filename: str) -> pd.DataFrame | None:
    """Carga silenciosa: devuelve None si el archivo no existe."""
    try:
        return DataManager.load(filename)
    except DataLoadError:
        return None


def prep_trimestral(df: pd.DataFrame) -> pd.DataFrame:
    """Asegura columna periodo y orden cronológico estricto por anio+trimestre."""
    df = add_periodo_col(df)
    return df.sort_values(["anio", "trimestre"]).reset_index(drop=True)


def mensual_a_trimestral(df: pd.DataFrame, value_cols: list) -> pd.DataFrame:
    """Agrega datos mensuales (col 'mes') a trimestral sumando."""
    df = df.copy()
    df["trimestre"] = ((df["mes"] - 1) // 3) + 1
    return (
        df.groupby(["anio", "trimestre"])[value_cols]
        .sum()
        .reset_index()
        .pipe(prep_trimestral)
    )


def align_series(series_dict: dict) -> pd.DataFrame:
    """
    Une todas las series en un DataFrame largo con columnas:
    periodo, Servicio, valor.
    Solo incluye períodos comunes a todos los servicios.
    """
    frames = []
    for servicio, (df, col, label_col) in series_dict.items():
        df_s = df[["periodo", col]].copy()
        df_s = df_s.rename(columns={col: label_col})
        df_s["Servicio"] = servicio
        df_s = df_s.rename(columns={label_col: "valor"})
        frames.append(df_s)
    return pd.concat(frames, ignore_index=True)


def indice_base_100(df_long: pd.DataFrame, base_anio: int) -> pd.DataFrame:
    """
    Normaliza cada serie a base 100 en el primer trimestre del año base.
    Requiere columnas: periodo, Servicio, valor.
    """
    result = []
    for servicio, grupo in df_long.groupby("Servicio"):
        grupo = grupo.sort_values("periodo").copy()
        base_rows = grupo[grupo["periodo"].str.startswith(str(base_anio))]
        if base_rows.empty:
            continue
        base_val = base_rows["valor"].iloc[0]
        if base_val == 0:
            continue
        grupo["indice"] = (grupo["valor"] / base_val * 100).round(2)
        result.append(grupo)
    return pd.concat(result, ignore_index=True) if result else pd.DataFrame()


# ── 1. Ingresos por servicio ──────────────────────────────────────────────────

if categoria == "Ingresos por servicio":
    st.header("Ingresos por servicio")
    st.caption(
        "Valores en pesos corrientes (no ajustados por inflación). "
        "Internet, Móvil, TV y Telefonía fija en miles de pesos. "
        "Postal en pesos."
    )

    series = {}

    # Internet
    df = try_load(InternetCSV.INGRESOS)
    if df is not None:
        df = prep_trimestral(df)
        ing_col = next((c for c in df.columns if "ingreso" in c), None)
        if ing_col:
            series["Internet fijo"] = (df, ing_col, "Ingresos")

    # Móvil
    df = try_load(MovilCSV.INGRESOS)
    if df is not None:
        df = prep_trimestral(df)
        ing_col = next((c for c in df.columns if "ingreso" in c), None)
        if ing_col:
            series["Telefonía móvil"] = (df, ing_col, "Ingresos")

    # TV — suma suscripción + satelital
    df = try_load(TVCSVs.INGRESOS)
    if df is not None:
        df = prep_trimestral(df)
        if "tv_suscripcion" in df.columns and "tv_satelital" in df.columns:
            df["total_tv"] = df["tv_suscripcion"] + df["tv_satelital"]
            series["TV por suscripción"] = (df, "total_tv", "Ingresos")

    # Telefonía fija
    df = try_load(TelefoniaCSV.FIJA_INGRESOS)
    if df is not None:
        df = prep_trimestral(df)
        if "ingresos" in df.columns:
            series["Telefonía fija"] = (df, "ingresos", "Ingresos")

    # Postal — mensual → trimestral, suma los 3 servicios
    df = try_load(PostalCSV.FACTURACION)
    if df is not None and "mes" in df.columns:
        cols = [c for c in ["postales", "telegraficas", "monetarios"] if c in df.columns]
        df_t = mensual_a_trimestral(df, cols)
        df_t["total_postal"] = df_t[cols].sum(axis=1)
        series["Mercado postal"] = (df_t, "total_postal", "Ingresos")

    if not series:
        st.warning("No se encontraron archivos de ingresos.", icon="⚠️")
        st.stop()

    # KPIs
    kpis = []
    for servicio, (df_s, col, _) in series.items():
        val, delta = last_period_delta(df_s, col)
        kpis.append({"label": servicio, "value": val, "delta": delta, "format": "{:,.0f}"})
    show_kpis(kpis)

    st.divider()

    # Gráfico — cada servicio como traza separada
    fig = go.Figure()
    for servicio, (df_s, col, _) in series.items():
        fig.add_trace(go.Scatter(
            x=df_s["periodo"], y=df_s[col],
            name=servicio, mode="lines",
            line={"color": COLOR_SERVICIO.get(servicio, "#888"), "width": 2},
        ))
    todos_periodos_ing = sorted(set(
        p for df_s, col, _ in series.values()
        for p in df_s["periodo"].tolist()
    ))
    fig.update_layout(
        title="Ingresos por servicio — evolución histórica",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        hovermode="x unified",
        separators=",.",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
        xaxis={"categoryorder": "array", "categoryarray": todos_periodos_ing},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Las escalas difieren entre servicios (Internet y Móvil en miles de $, "
        "Postal en $ nominales). Usá la leyenda para mostrar/ocultar series.",
        icon="ℹ️",
    )

    with st.expander("Ver tabla de datos"):
        rows = []
        for servicio, (df_s, col, _) in series.items():
            tmp = df_s[["periodo", col]].copy()
            tmp["Servicio"] = servicio
            tmp = tmp.rename(columns={col: "Ingresos"})
            rows.append(tmp)
        st.dataframe(pd.concat(rows), use_container_width=True)


# ── 2. Accesos por servicio ───────────────────────────────────────────────────

elif categoria == "Accesos por servicio":
    st.header("Accesos por servicio")

    series = {}

    # Internet — total
    df = try_load(InternetCSV.TECNOLOGIAS)
    if df is not None:
        df = prep_trimestral(df)
        if "total" in df.columns:
            series["Internet fijo"] = (df, "total")

    # Móvil — operativos
    df = try_load(MovilCSV.ACCESOS)
    if df is not None:
        df = prep_trimestral(df)
        acc_col = next((c for c in df.columns if "operativo" in c or "total" in c), None)
        if acc_col:
            series["Telefonía móvil"] = (df, acc_col)

    # TV — suma suscripción + satelital
    df = try_load(TVCSVs.ACCESOS)
    if df is not None:
        df = prep_trimestral(df)
        if "tv_suscripcion" in df.columns and "tv_satelital" in df.columns:
            df["total_tv"] = df["tv_suscripcion"] + df["tv_satelital"]
            series["TV por suscripción"] = (df, "total_tv")

    # Telefonía fija — total
    df = try_load(TelefoniaCSV.FIJA_ACCESOS)
    if df is not None:
        df = prep_trimestral(df)
        if "total" in df.columns:
            series["Telefonía fija"] = (df, "total")

    if not series:
        st.warning("No se encontraron archivos de accesos.", icon="⚠️")
        st.stop()

    # KPIs
    kpis = []
    for servicio, (df_s, col) in series.items():
        val, delta = last_period_delta(df_s, col)
        kpis.append({"label": servicio, "value": val, "delta": delta, "format": "{:,.0f}"})
    show_kpis(kpis)

    st.divider()

    # Selector: escala real vs índice base 100
    modo = st.radio(
        "Escala",
        ["Valores absolutos", "Índice base 100"],
        horizontal=True, key="comp_acc_modo",
        help="Base 100 normaliza todas las series al mismo punto de partida "
             "para comparar tasas de crecimiento independientemente del volumen.",
    )

    if modo == "Valores absolutos":
        st.info(
            "Móvil tiene una escala 3–5x mayor que los demás. "
            "Usá la leyenda para comparar pares de servicios.",
            icon="ℹ️",
        )
        fig = go.Figure()
        for servicio, (df_s, col) in series.items():
            fig.add_trace(go.Scatter(
                x=df_s["periodo"], y=df_s[col],
                name=servicio, mode="lines",
                line={"color": COLOR_SERVICIO.get(servicio, "#888"), "width": 2},
            ))
        # Construir eje X ordenado cronológicamente con todos los períodos disponibles
        todos_periodos = sorted(set(
            p for df_s, col in series.values()
            for p in df_s["periodo"].tolist()
        ))

        fig.update_layout(
            title="Accesos por servicio — evolución histórica",
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font={"family": "Inter, Arial, sans-serif", "size": 13},
            margin={"t": 48, "b": 40, "l": 48, "r": 20},
            hovermode="x unified",
        separators=",.",
            legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
            yaxis={"tickformat": ",.0f", "gridcolor": "#E8E8E8"},
            xaxis={"categoryorder": "array", "categoryarray": todos_periodos},
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        anios_disponibles = sorted(set(
            int(df_s["anio"].min())
            for df_s, _ in series.values()
        ))
        base_anio = st.select_slider(
            "Año base (= 100)", options=anios_disponibles,
            value=max(anios_disponibles[0], 2014),
            key="comp_base_anio",
        )

        # Construir DataFrame largo para normalizar
        frames = []
        for servicio, (df_s, col) in series.items():
            tmp = df_s[["anio", "periodo", col]].copy()
            tmp["Servicio"] = servicio
            tmp = tmp.rename(columns={col: "valor"})
            frames.append(tmp)
        df_long = pd.concat(frames, ignore_index=True)
        df_idx = indice_base_100(df_long, base_anio)

        if df_idx.empty:
            st.warning("No hay datos disponibles para el año base seleccionado.")
        else:
            fig = go.Figure()
            fig.add_hline(y=100, line_dash="dot", line_color="#C6C6C6",
                          line_width=1, annotation_text=f"Base = {base_anio}")
            for servicio in df_idx["Servicio"].unique():
                sub = df_idx[df_idx["Servicio"] == servicio]
                fig.add_trace(go.Scatter(
                    x=sub["periodo"], y=sub["indice"],
                    name=servicio, mode="lines",
                    line={"color": COLOR_SERVICIO.get(servicio, "#888"), "width": 2},
                ))
            fig.update_layout(
                title=f"Crecimiento relativo de accesos — índice base 100 = {base_anio}",
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter, Arial, sans-serif", "size": 13},
                margin={"t": 48, "b": 40, "l": 48, "r": 20},
                hovermode="x unified",
        separators=",.",
                legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
                yaxis={"ticksuffix": "", "gridcolor": "#E8E8E8",
                       "title": "Índice (base = 100)"},
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                f"Un valor de 150 significa que el servicio tiene 50% más accesos "
                f"que en el primer trimestre de {base_anio}."
            )


# ── 3. Penetración comparada ──────────────────────────────────────────────────

elif categoria == "Penetración comparada":
    st.header("Penetración comparada entre servicios")
    st.caption(
        "Servicios fijos en accesos cada 100 hogares (eje izquierdo). "
        "Telefonía móvil en accesos cada 100 habitantes (eje derecho, escala distinta)."
    )

    series_hog = {}   # c/100 hogares
    series_hab = {}   # c/100 habitantes (móvil)

    # Internet — c/100 hogares
    df = try_load(InternetCSV.PENETRACION)
    if df is not None:
        df = prep_trimestral(df)
        if "accesos_cada_100_hogares" in df.columns:
            series_hog["Internet fijo"] = (df, "accesos_cada_100_hogares")

    # TV — c/100 hogares (suscripción)
    df = try_load(TVCSVs.PENETRACION)
    if df is not None:
        df = prep_trimestral(df)
        if "tv_suscripcion_100_hogares" in df.columns:
            series_hog["TV por suscripción"] = (df, "tv_suscripcion_100_hogares")

    # Telefonía fija — c/100 hogares
    df = try_load(TelefoniaCSV.FIJA_PENETRACION)
    if df is not None:
        df = prep_trimestral(df)
        if "accesos_100_hog" in df.columns:
            series_hog["Telefonía fija"] = (df, "accesos_100_hog")

    # Móvil — c/100 habitantes (eje derecho)
    df = try_load(MovilCSV.PENETRACION)
    if df is not None:
        df = prep_trimestral(df)
        if "accesos_100_hab" in df.columns:
            series_hab["Telefonía móvil"] = (df, "accesos_100_hab")

    # KPIs — último valor de cada serie
    kpis = []
    for servicio, (df_s, col) in {**series_hog, **series_hab}.items():
        val, delta = last_period_delta(df_s, col)
        unit = "c/100 hog." if servicio != "Telefonía móvil" else "c/100 hab."
        kpis.append({
            "label": f"{servicio} ({unit})",
            "value": val, "delta": delta, "format": "{:.2f}",
        })
    show_kpis(kpis)

    st.divider()

    fig = go.Figure()

    # Servicios fijos → eje izquierdo
    for servicio, (df_s, col) in series_hog.items():
        fig.add_trace(go.Scatter(
            x=df_s["periodo"], y=df_s[col],
            name=f"{servicio} (c/100 hog.)", mode="lines",
            line={"color": COLOR_SERVICIO.get(servicio, "#888"), "width": 2},
            yaxis="y1",
        ))

    # Móvil → eje derecho
    for servicio, (df_s, col) in series_hab.items():
        fig.add_trace(go.Scatter(
            x=df_s["periodo"], y=df_s[col],
            name=f"{servicio} (c/100 hab.)", mode="lines",
            line={"color": COLOR_SERVICIO.get(servicio, "#888"),
                  "width": 2, "dash": "dot"},
            yaxis="y2",
        ))

    todos_periodos_pen = sorted(set(
        p for df_s, col in {**series_hog, **series_hab}.values()
        for p in df_s["periodo"].tolist()
    ))
    fig.update_layout(
        title="Penetración por servicio",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 80},
        hovermode="x unified",
        separators=",.",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        xaxis={"categoryorder": "array", "categoryarray": todos_periodos_pen},
        yaxis=dict(
            title=dict(text="Accesos c/100 hogares", font={"color": ENACOM["primary"]}),
            gridcolor="#E8E8E8",
        ),
        yaxis2=dict(
            title=dict(text="Accesos c/100 hab. (móvil)",
                       font={"color": ENACOM["yellow"]}),
            tickfont={"color": ENACOM["yellow"]},
            overlaying="y", side="right", showgrid=False,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Tabla comparativa del último período disponible
    st.subheader("Último período disponible por servicio")
    rows = []
    for servicio, (df_s, col) in series_hog.items():
        ultimo = df_s.dropna(subset=[col]).iloc[-1]
        rows.append({
            "Servicio": servicio,
            "Período": ultimo["periodo"],
            "Penetración": round(float(ultimo[col]), 2),
            "Unidad": "c/100 hogares",
        })
    for servicio, (df_s, col) in series_hab.items():
        ultimo = df_s.dropna(subset=[col]).iloc[-1]
        rows.append({
            "Servicio": servicio,
            "Período": ultimo["periodo"],
            "Penetración": round(float(ultimo[col]), 2),
            "Unidad": "c/100 habitantes",
        })

    df_tabla = pd.DataFrame(rows).sort_values("Penetración", ascending=False)
    st.dataframe(df_tabla, use_container_width=True, hide_index=True)


# ── 4. Crecimiento relativo ───────────────────────────────────────────────────

elif categoria == "Crecimiento relativo":
    st.header("Crecimiento relativo de accesos")
    st.caption(
        "Todos los servicios normalizados a base 100 en el año seleccionado. "
        "Permite comparar tasas de crecimiento eliminando las diferencias de escala."
    )

    series = {}

    df = try_load(InternetCSV.TECNOLOGIAS)
    if df is not None:
        df = prep_trimestral(df)
        if "total" in df.columns:
            series["Internet fijo"] = (df, "total")

    df = try_load(MovilCSV.ACCESOS)
    if df is not None:
        df = prep_trimestral(df)
        acc_col = next((c for c in df.columns if "operativo" in c or "total" in c), None)
        if acc_col:
            series["Telefonía móvil"] = (df, acc_col)

    df = try_load(TVCSVs.ACCESOS)
    if df is not None:
        df = prep_trimestral(df)
        if "tv_suscripcion" in df.columns and "tv_satelital" in df.columns:
            df["total_tv"] = df["tv_suscripcion"] + df["tv_satelital"]
            series["TV por suscripción"] = (df, "total_tv")

    df = try_load(TelefoniaCSV.FIJA_ACCESOS)
    if df is not None:
        df = prep_trimestral(df)
        if "total" in df.columns:
            series["Telefonía fija"] = (df, "total")

    if not series:
        st.warning("No se encontraron archivos de accesos.", icon="⚠️")
        st.stop()

    # Filtros
    col1, col2, _ = st.columns([1, 1, 3])
    with col1:
        anios = sorted(set(int(df_s["anio"].min()) for df_s, _ in series.values()))
        base_anio = st.selectbox("Año base (= 100)", anios,
                                 index=anios.index(max(anios[0], 2014)),
                                 key="crec_base")
    with col2:
        servicios_sel = st.multiselect(
            "Servicios", list(series.keys()),
            default=list(series.keys()),
            key="crec_sel",
        )

    if not servicios_sel:
        st.warning("Seleccioná al menos un servicio.", icon="⚠️")
        st.stop()

    frames = []
    for servicio in servicios_sel:
        df_s, col = series[servicio]
        tmp = df_s[["anio", "periodo", col]].copy()
        tmp["Servicio"] = servicio
        tmp = tmp.rename(columns={col: "valor"})
        frames.append(tmp)

    df_long = pd.concat(frames, ignore_index=True)
    df_idx  = indice_base_100(df_long, base_anio)

    if df_idx.empty:
        st.warning("No hay datos para el año base seleccionado.")
        st.stop()

    # KPIs — variación total desde el año base
    st.subheader(f"Variación acumulada desde {base_anio}")
    kpis = []
    for servicio in servicios_sel:
        sub = df_idx[df_idx["Servicio"] == servicio]
        if sub.empty:
            continue
        ultimo_idx = sub["indice"].iloc[-1]
        kpis.append({
            "label": servicio,
            "value": ultimo_idx - 100,
            "format": "{:+.1f}%",
            "help": f"Variación acumulada de accesos desde {base_anio} al último período",
        })
    show_kpis(kpis)

    st.divider()

    fig = go.Figure()
    fig.add_hline(y=100, line_dash="dot", line_color="#C6C6C6",
                  line_width=1, annotation_text=f"Base = {base_anio}")
    for servicio in servicios_sel:
        sub = df_idx[df_idx["Servicio"] == servicio]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["periodo"], y=sub["indice"],
            name=servicio, mode="lines",
            line={"color": COLOR_SERVICIO.get(servicio, "#888"), "width": 2},
        ))
    todos_periodos_crec = sorted(df_idx["periodo"].unique())
    fig.update_layout(
        title=f"Índice de crecimiento de accesos (base 100 = T1 {base_anio})",
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "size": 13},
        margin={"t": 48, "b": 40, "l": 48, "r": 20},
        hovermode="x unified",
        separators=",.",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0},
        xaxis={"categoryorder": "array", "categoryarray": todos_periodos_crec},
        yaxis={"gridcolor": "#E8E8E8",
               "title": f"Índice (base 100 = T1 {base_anio})"},
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Fibra óptica impulsó el crecimiento de Internet fijo. "
        "Telefonía fija y TV muestran tendencias declinantes en los últimos años. "
        "Móvil creció fuertemente hasta 2016 y se estabilizó."
    )

    with st.expander("Ver tabla del índice"):
        pivot = df_idx.pivot_table(
            index="periodo", columns="Servicio", values="indice"
        ).round(1)
        st.dataframe(pivot, use_container_width=True)