import pandas as pd
import streamlit as st

from components.kpi_cards import show_kpis
from components.filters import render_period_filters
from components.charts import (
    line_chart,
)

from services.chart_helpers import (
    province_ranking_chart,
)

from services.transformers import (
    filter_by_period,
)

from pages.internet.utils import (
    load_dataset,
)


def render():

    # st.header("Penetración — por provincia")
    st.caption(
        "Evolución de la penetración de Internet — por provincia."
    )

    # ── Dataset ──────────────────────────────────────────

    df = load_dataset("penetracion_provincia")
    df_nacional = load_dataset("penetracion")

    # ── Filtro ───────────────────────────────────────────

    anio, trimestre = render_period_filters(
        df,
        key_prefix="prov_pen",
    )

    df_periodo = filter_by_period(
        df,
        anio,
        trimestre,
    ).copy()

    # ── KPIs ─────────────────────────────────────────────

    top_hog = df_periodo.nlargest(
        1,
        "accesos_cada_100_hogares",
    ).iloc[0]

    top_hab = df_periodo.nlargest(
        1,
        "accesos_cada_100_habitantes",
    ).iloc[0]

    low_hog = df_periodo.nsmallest(
        1,
        "accesos_cada_100_hogares",
    ).iloc[0]

    show_kpis(
        [
            {
                "label": (f"Mayor penetración hogares " f"({top_hog['provincia']})"),
                "value": top_hog["accesos_cada_100_hogares"],
                "format": "{:.2f}",
            },
            {
                "label": (f"Mayor penetración hab. " f"({top_hab['provincia']})"),
                "value": top_hab["accesos_cada_100_habitantes"],
                "format": "{:.2f}",
            },
            {
                "label": (f"Menor penetración hogares " f"({low_hog['provincia']})"),
                "value": low_hog["accesos_cada_100_hogares"],
                "format": "{:.2f}",
            },
            {
                "label": "Promedio nacional (hogares)",
                "value": (df_periodo["accesos_cada_100_hogares"].mean()),
                "format": "{:.2f}",
            },
        ]
    )

    st.divider()

    # ── Rankings ─────────────────────────────────────────

    col1, col2 = st.columns(2)

    with col1:

        st.subheader("Ranking — c/100 hogares")

        fig = province_ranking_chart(
            df_periodo,
            value_col="accesos_cada_100_hogares",
            title=f"{anio} T{trimestre}",
            tickformat=",.2f",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    with col2:

        st.subheader("Ranking — c/100 habitantes")

        fig = province_ranking_chart(
            df_periodo,
            value_col="accesos_cada_100_habitantes",
            title=f"{anio} T{trimestre}",
            tickformat=",.2f",
            color="#EEAE42",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )

    st.divider()

    # ── Evolución histórica ──────────────────────────────

    st.subheader("Provincia vs penetración nacional")

    provincias = sorted(df["provincia"].unique())

    provincia = st.selectbox(
        "Provincia",
        provincias,
        key="internet_pen_prov",
    )

    df_prov = df[df["provincia"] == provincia].copy()

    df_nac = df_nacional[
        [
            "periodo",
            "accesos_cada_100_hogares",
        ]
    ].copy()

    df_nac["provincia"] = "Penetración nacional"

    df_compare = pd.concat(
        [
            df_prov,
            df_nac,
        ],
        ignore_index=True,
    )

    fig = line_chart(
        df_compare,
        x="periodo",
        y="accesos_cada_100_hogares",
        color="provincia",
        y_tickformat=",.2f",
        title=(f"{provincia} vs penetración nacional"),
    )

    st.plotly_chart(
        fig,
        width="stretch",
    )

    # ── Tabla ────────────────────────────────────────────

    with st.expander("Ver datos completos"):

        st.dataframe(
            df_periodo,
            width="stretch",
        )
