import plotly.graph_objects as go
import plotly.express as px

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


def participation_chart(
    df,
    numerator,
    denominator,
    title,
    x="periodo",
    y_suffix="%",
    color="#00B5E5",
):
    """
    Genera un gráfico de participación porcentual.

    Ejemplo:
        pospago / total * 100
        hogares / total * 100
    """

    df_plot = df.copy()

    df_plot["_pct"] = (
        df_plot[numerator]
        / df_plot[denominator]
        * 100
    ).round(2)

    fig = go.Figure(
        go.Scatter(
            x=df_plot[x],
            y=df_plot["_pct"],
            mode="lines+markers",
            fill="tozeroy",
            line={
                "color": color,
                "width": 2,
            },
            fillcolor="rgba(0,181,229,0.08)",
            marker={"size": 4},
        )
    )

    fig.update_layout(
        title=title,
        hovermode="x unified",
        margin={
            "t": 40,
            "b": 40,
            "l": 40,
            "r": 20,
        },
        yaxis={
            "ticksuffix": y_suffix,
            "gridcolor": "#E8E8E8",
        },
    )

    return fig


def seasonality_chart(
    df,
    value_col,
    month_col,
    month_labels,
    title=None,
):
    """
    Genera gráfico de estacionalidad
    mostrando el promedio histórico mensual.
    """

    df_estac = (
        df.groupby(month_col)[value_col]
        .mean()
        .reset_index()
        .sort_values(month_col)
    )

    df_estac["mes_label"] = (
        df_estac[month_col]
        .map(month_labels)
    )

    promedio_global = (
        df_estac[value_col]
        .mean()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=df_estac["mes_label"],
            y=df_estac[value_col],
            marker_color=[
                "#00B5E5"
                if v >= promedio_global
                else "#BCE4F4"
                for v in df_estac[value_col]
            ],
            text=df_estac[value_col].apply(
                lambda v: f"{v:,.0f}"
            ),
            textposition="outside",
        )
    )

    fig.add_hline(
        y=promedio_global,
        line_dash="dot",
        line_color="#C6C6C6",
        line_width=1,
        annotation_text=f"Promedio: {promedio_global:,.0f}",
        annotation_position="top right",
    )

    fig.update_layout(
        title=title,
        yaxis={"tickformat": ",.0f"},
        showlegend=False,
    )

    return fig

def composition_pie_chart(
    df,
    columns,
    labels=None,
    title=None,
    hole=0.45,
    color_map=None,
):

    serie = df[columns].iloc[-1]

    if labels:
        serie = serie.rename(labels)

    df_pie = serie.reset_index()

    df_pie.columns = [
        "Categoria",
        "Valor",
    ]

    df_pie = df_pie[
        df_pie["Valor"] > 0
    ]

    fig = px.pie(
        df_pie,
        names="Categoria",
        values="Valor",
        hole=hole,
        title=title,
        color="Categoria",
        color_discrete_map=color_map,
    )

    fig.update_layout(
        margin={
            "t": 50,
            "b": 0,
            "l": 0,
            "r": 0,
        }
    )

    return fig

def province_ranking_chart(
    df,
    value_col,
    title,
    color="#00B5E5",
    height=650,
    tickformat=",.0f",
):
    from components.charts import bar_chart

    df_rank = (
        df[
            ["provincia", value_col]
        ]
        .sort_values(
            value_col,
            ascending=True,
        )
    )

    fig = bar_chart(
        df_rank,
        x=value_col,
        y="provincia",
        title=title,
    )

    fig.update_layout(
        height=height,
        yaxis={
            "categoryorder": "total ascending",
        },
        xaxis={
            "tickformat": tickformat,
        },
    )

    fig.update_traces(
        marker_color=color,
        orientation="h",
    )

    return fig