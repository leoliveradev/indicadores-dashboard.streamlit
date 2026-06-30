import plotly.graph_objects as go
from services.transformers import add_periodo_col, sort_by_periodo

def dual_axis_chart(config, df, x="periodo"):
    fig = go.Figure()

    for s in config["left_axis"]["series"]:
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[s["column"]],
            name=s["name"],
            mode=s.get("mode", "lines"),
            line={
                "color": s["color"],
                "width": 2,
                "dash": s.get("dash", None),
            },
            marker={"size": 4} if "markers" in s.get("mode", "") else None,
            yaxis="y1",
        ))

    for s in config["right_axis"]["series"]:
        fig.add_trace(go.Scatter(
            x=df[x],
            y=df[s["column"]],
            name=s["name"],
            mode=s.get("mode", "lines"),
            line={
                "color": s["color"],
                "width": 1.5,
                "dash": s.get("dash", None),
            },
            opacity=s.get("opacity", 0.7),
            yaxis="y2",
        ))

    fig.update_layout(
        title=config.get("title", ""),
        hovermode="x unified",
        margin={"t": 48, "b": 40, "l": 48, "r": 60},
        legend={"orientation": "h", "y": 1.02, "x": 0},

        yaxis=dict(
            title=config["left_axis"].get("label", ""),
            ticksuffix=config["left_axis"].get("suffix", ""),
            gridcolor="#E8E8E8",
        ),

        yaxis2=dict(
            title=config["right_axis"].get("label", ""),
            ticksuffix=config["right_axis"].get("suffix", ""),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
    )

    return fig


def compare_vs_national(
    df,
    group_col,
    value_col,
    selected,
    period_cols=("anio", "trimestre"),
    title=None,
    y_suffix=None
):
    """
    Genera gráfico comparando una serie (ej: provincia)
    contra el nacional.
    """

    # serie del grupo seleccionado
    df_sel = df[df[group_col] == selected].copy()
    df_sel = sort_by_periodo(add_periodo_col(df_sel))

    # nacional
    df_nac = (
        df.groupby(list(period_cols))[value_col]
        .mean()
        .reset_index()
    )
    df_nac = sort_by_periodo(add_periodo_col(df_nac))

    fig = go.Figure()

    # serie seleccionada
    fig.add_trace(go.Scatter(
        x=df_sel["periodo"],
        y=df_sel[value_col],
        name=selected,
        mode="lines+markers",
        line={"width": 2},
    ))

    # nacional
    fig.add_trace(go.Scatter(
        x=df_nac["periodo"],
        y=df_nac[value_col].round(2),
        name="Nacional",
        mode="lines",
        line={"dash": "dot"},
    ))

    fig.update_layout(
        title=title,
        yaxis={"ticksuffix": y_suffix or ""},
        hovermode="x unified",
        margin={"t": 40, "b": 40, "l": 40, "r": 20},
        legend={"orientation": "h", "y": 1.02},
    )

    return fig