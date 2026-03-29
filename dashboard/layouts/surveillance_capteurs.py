"""
StarDash — Section 2 : Surveillance capteurs
- Courbe temporelle température air vs process
- Distribution vitesse de rotation par segment qualité
- Heatmap couple × usure outil (zones de risque)
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

def _fig_temperatures(df) -> go.Figure:
    """Courbe temporelle temp_air vs temp_process (échantillon pour perf)."""
    # 1 point sur 10 pour éviter 10 000 points dans le browser
    sample = df.iloc[::10].copy()

    fig = go.Figure([
        go.Scatter(
            x=sample["timestamp"],
            y=sample["temp_air"],
            name="Temp. air (K)",
            mode="lines",
            line=dict(color="#63b3ed", width=1.5),
            hovertemplate="%{x|%H:%M}<br>Air : %{y:.1f} K<extra></extra>",
        ),
        go.Scatter(
            x=sample["timestamp"],
            y=sample["temp_process"],
            name="Temp. process (K)",
            mode="lines",
            line=dict(color="#fc8181", width=1.5),
            hovertemplate="%{x|%H:%M}<br>Process : %{y:.1f} K<extra></extra>",
        ),
    ])
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(title="Temps", gridcolor="#2d3748", showgrid=True),
        yaxis=dict(title="Température (K)", gridcolor="#2d3748"),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color="#a0aec0")),
        hovermode="x unified",
    )
    return fig


def _fig_distribution_vitesse(df) -> go.Figure:
    """Box plot vitesse de rotation par segment qualité."""
    colors = {"L": "#fc8181", "M": "#f6ad55", "H": "#68d391"}

    fig = go.Figure([
        go.Box(
            y=df[df["qualite"] == q]["vitesse_rotation"],
            name=f"Qualité {q}",
            marker_color=colors[q],
            boxmean="sd",
            hovertemplate="<b>Qualité %{x}</b><br>%{y:.0f} rpm<extra></extra>",
        )
        for q in ["L", "M", "H"]
    ])
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(title="Segment qualité", gridcolor="#2d3748"),
        yaxis=dict(title="Vitesse de rotation (rpm)", gridcolor="#2d3748"),
        showlegend=False,
    )
    return fig


def _fig_heatmap_couple_usure(df) -> go.Figure:
    """Heatmap couple × usure outil — taux de panne moyen par cellule."""
    import numpy as np

    # Discrétisation en bins
    df = df.copy()
    df["bin_couple"] = (df["couple"] // 5 * 5).astype(int)
    df["bin_usure"]  = (df["usure_outil"] // 25 * 25).astype(int)

    pivot = (
        df.groupby(["bin_usure", "bin_couple"])["machine_failure"]
        .mean()
        .unstack(fill_value=0)
    )

    fig = go.Figure(go.Heatmap(
        z=pivot.values * 100,          # en %
        x=[f"{c} Nm" for c in pivot.columns],
        y=[f"{u} min" for u in pivot.index],
        colorscale=[
            [0.0, "#1a2744"],
            [0.3, "#2b4c8c"],
            [0.6, "#f6ad55"],
            [1.0, "#fc8181"],
        ],
        colorbar=dict(
            title=dict(text="Taux panne (%)", font=dict(color="#a0aec0")),
            tickfont=dict(color="#a0aec0"),
        ),
        hovertemplate="Usure : %{y}<br>Couple : %{x}<br>Taux panne : %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(title="Couple (Nm)", tickangle=-45),
        yaxis=dict(title="Usure outil (min)"),
    )
    return fig


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def _build_layout():
    df = load_fait_capteurs()

    return html.Div([

        # --- Courbe températures (pleine largeur) ---
        html.Div(className="chart-card", style={"marginBottom": "1.5rem"}, children=[
            html.Div("Températures air vs process dans le temps", className="chart-title"),
            dcc.Graph(
                figure=_fig_temperatures(df),
                config={"displayModeBar": True, "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
                style={"height": "320px"},
            ),
        ]),

        # --- Box plot + Heatmap ---
        html.Div(className="charts-grid", children=[

            html.Div(className="chart-card", children=[
                html.Div("Distribution vitesse de rotation par qualité", className="chart-title"),
                dcc.Graph(
                    figure=_fig_distribution_vitesse(df),
                    config={"displayModeBar": False},
                    style={"height": "360px"},
                ),
            ]),

            html.Div(className="chart-card", children=[
                html.Div("Zones de risque — Couple × Usure outil", className="chart-title"),
                dcc.Graph(
                    figure=_fig_heatmap_couple_usure(df),
                    config={"displayModeBar": False},
                    style={"height": "360px"},
                ),
            ]),

        ]),

    ])


layout = _build_layout()
