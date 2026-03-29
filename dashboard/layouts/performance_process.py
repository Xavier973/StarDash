"""
StarDash — Section 4 : Performance process
- Puissance estimée dans le temps
- Corrélation temp_delta / pannes thermiques
- Table des derniers événements critiques
"""
from dash import html, dcc
import plotly.graph_objects as go

from data import load_fait_capteurs

PLOTLY_THEME = dict(
    paper_bgcolor="#1a1f2e",
    plot_bgcolor="#1a1f2e",
    font=dict(color="#a0aec0", size=12),
    margin=dict(l=50, r=20, t=30, b=50),
)

# ---------------------------------------------------------------------------
# Graphiques
# ---------------------------------------------------------------------------

def _fig_puissance_temps(df) -> go.Figure:
    """Courbe puissance estimée + marqueurs pannes sur l'axe temporel."""
    sample   = df.iloc[::10].copy()
    pannes   = df[df["machine_failure"]].copy()

    fig = go.Figure([
        go.Scatter(
            x=sample["timestamp"],
            y=sample["puissance_estimee"],
            name="Puissance estimée (W)",
            mode="lines",
            line=dict(color="#b794f4", width=1.5),
            hovertemplate="%{x|%d/%m %H:%M}<br>Puissance : %{y:.0f} W<extra></extra>",
        ),
        go.Scatter(
            x=pannes["timestamp"],
            y=pannes["puissance_estimee"],
            name="Panne",
            mode="markers",
            marker=dict(color="#fc8181", size=6, symbol="x"),
            hovertemplate="%{x|%d/%m %H:%M}<br>Panne — %{y:.0f} W<extra></extra>",
        ),
    ])
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(title="Temps", gridcolor="#2d3748"),
        yaxis=dict(title="Puissance (W)", gridcolor="#2d3748"),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color="#a0aec0")),
        hovermode="x unified",
    )
    return fig


def _fig_correlation_temp_delta(df) -> go.Figure:
    """Scatter temp_delta vs panne thermique (HDF) — densité par couleur."""
    df = df.copy()
    df["panne_label"] = df["panne_dissipation_thermique"].map({True: "Panne thermique", False: "Normal"})

    colors = {"Normal": "#63b3ed", "Panne thermique": "#fc8181"}

    fig = go.Figure([
        go.Scatter(
            x=df[df["panne_label"] == label]["temp_delta"],
            y=df[df["panne_label"] == label]["puissance_estimee"],
            name=label,
            mode="markers",
            marker=dict(
                color=colors[label],
                size=4,
                opacity=0.5 if label == "Normal" else 0.85,
            ),
            hovertemplate="ΔT : %{x:.2f} K<br>Puissance : %{y:.0f} W<extra></extra>",
        )
        for label in ["Normal", "Panne thermique"]
    ])
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(title="Δ Température (process − air) [K]", gridcolor="#2d3748"),
        yaxis=dict(title="Puissance estimée (W)", gridcolor="#2d3748"),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color="#a0aec0")),
    )
    return fig


def _build_table_evenements(df) -> html.Div:
    """50 derniers événements avec machine_failure=True."""
    evenements = (
        df[df["machine_failure"]]
        .sort_values("timestamp", ascending=False)
        .head(50)
        [["timestamp", "product_id", "qualite", "usure_outil",
          "puissance_estimee", "temp_delta", "statut_usure"]]
    )

    if evenements.empty:
        return html.Div("Aucun événement critique.", style={"color": "#68d391", "padding": "1rem"})

    def statut_color(s):
        return {"critique": "#fc8181", "attention": "#f6ad55", "normal": "#68d391"}.get(s, "#a0aec0")

    rows = [
        html.Tr([
            html.Td(row["timestamp"].strftime("%d/%m %H:%M"), style={"color": "#a0aec0"}),
            html.Td(row["product_id"],                        style={"color": "#e2e8f0"}),
            html.Td(row["qualite"],                           style={"color": "#a0aec0"}),
            html.Td(f"{row['usure_outil']} min",              style={"color": statut_color(row["statut_usure"])}),
            html.Td(f"{row['puissance_estimee']:.0f} W",      style={"color": "#b794f4"}),
            html.Td(f"{row['temp_delta']:.2f} K",             style={"color": "#63b3ed"}),
            html.Td(row["statut_usure"].upper(),              style={"color": statut_color(row["statut_usure"]), "fontWeight": "bold"}),
        ])
        for _, row in evenements.iterrows()
    ]

    th_style = {"color": "#718096", "textAlign": "left",
                "paddingBottom": "0.5rem", "paddingRight": "1.5rem",
                "fontSize": "0.75rem", "textTransform": "uppercase"}

    return html.Div(
        style={"overflowY": "auto", "maxHeight": "360px"},
        children=[
            html.Table(
                style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.82rem"},
                children=[
                    html.Thead(html.Tr([
                        html.Th("Horodatage",  style=th_style),
                        html.Th("Machine",     style=th_style),
                        html.Th("Qualité",     style=th_style),
                        html.Th("Usure",       style=th_style),
                        html.Th("Puissance",   style=th_style),
                        html.Th("Δ Temp.",     style=th_style),
                        html.Th("Statut",      style=th_style),
                    ])),
                    html.Tbody(rows),
                ],
            )
        ],
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def _build_layout():
    df = load_fait_capteurs()

    # KPIs process
    puissance_moy  = round(df["puissance_estimee"].mean(), 1)
    puissance_max  = round(df["puissance_estimee"].max(), 1)
    temp_delta_moy = round(df["temp_delta"].mean(), 2)
    nb_thermiques  = int(df["panne_dissipation_thermique"].sum())

    return html.Div([

        # --- KPIs process ---
        html.Div(className="kpi-grid", style={"marginBottom": "1.5rem"}, children=[
            html.Div(className="kpi-card", children=[
                html.Div("Puissance moyenne", className="kpi-label"),
                html.Div(f"{puissance_moy:,} W", className="kpi-value"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Puissance max", className="kpi-label"),
                html.Div(f"{puissance_max:,} W", className="kpi-value kpi-value--warning"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Δ Temp. moyen", className="kpi-label"),
                html.Div(f"{temp_delta_moy} K", className="kpi-value"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Pannes thermiques", className="kpi-label"),
                html.Div(f"{nb_thermiques}", className="kpi-value kpi-value--danger"),
            ]),
        ]),

        # --- Puissance dans le temps (pleine largeur) ---
        html.Div(className="chart-card", style={"marginBottom": "1.5rem"}, children=[
            html.Div("Puissance estimée dans le temps — événements de panne", className="chart-title"),
            dcc.Graph(
                figure=_fig_puissance_temps(df),
                config={"displayModeBar": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
                style={"height": "320px"},
            ),
        ]),

        # --- Scatter corrélation + Table événements ---
        html.Div(className="charts-grid", children=[

            html.Div(className="chart-card", children=[
                html.Div("Corrélation Δ Température / Pannes thermiques", className="chart-title"),
                dcc.Graph(
                    figure=_fig_correlation_temp_delta(df),
                    config={"displayModeBar": False},
                    style={"height": "360px"},
                ),
            ]),

            html.Div(className="chart-card", children=[
                html.Div("50 derniers événements critiques", className="chart-title"),
                _build_table_evenements(df),
            ]),

        ]),

    ])


layout = _build_layout()
