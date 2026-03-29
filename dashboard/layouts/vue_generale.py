"""
StarDash — Section 1 : Vue générale
- KPIs globaux : total cycles, taux de panne, disponibilité
- Répartition pannes par type (camembert)
- Distribution qualité produit L / M / H
"""
from dash import html, dcc
import plotly.graph_objects as go
import plotly.express as px

from data import load_fait_capteurs, load_kpis

# ---------------------------------------------------------------------------
# Helpers graphiques
# ---------------------------------------------------------------------------

PLOTLY_THEME = dict(
    paper_bgcolor="#1a1f2e",
    plot_bgcolor="#1a1f2e",
    font=dict(color="#a0aec0", size=12),
    margin=dict(l=40, r=20, t=30, b=40),
)


def _fig_pannes_par_type(df) -> go.Figure:
    types = {
        "Usure outil":        df["panne_usure_outil"].sum(),
        "Dissip. thermique":  df["panne_dissipation_thermique"].sum(),
        "Surpuissance":       df["panne_surpuissance"].sum(),
        "Surcharge":          df["panne_surcharge"].sum(),
        "Aléatoire":          df["panne_aleatoire"].sum(),
    }
    labels = list(types.keys())
    values = list(types.values())

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.45,
        textinfo="label+percent",
        textfont=dict(size=12, color="#e2e8f0"),
        marker=dict(colors=["#63b3ed", "#f6ad55", "#fc8181", "#68d391", "#b794f4"],
                    line=dict(color="#0f1117", width=2)),
        hovertemplate="<b>%{label}</b><br>%{value} pannes<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        showlegend=True,
        legend=dict(orientation="v", x=1.02, y=0.5,
                    font=dict(color="#a0aec0", size=11)),
    )
    return fig


def _fig_distribution_qualite(df) -> go.Figure:
    counts = df["qualite"].value_counts().reindex(["L", "M", "H"]).fillna(0)
    colors = {"L": "#fc8181", "M": "#f6ad55", "H": "#68d391"}

    fig = go.Figure(go.Bar(
        x=counts.index.tolist(),
        y=counts.values.tolist(),
        marker_color=[colors[q] for q in counts.index],
        text=counts.values.tolist(),
        textposition="outside",
        textfont=dict(color="#e2e8f0"),
        hovertemplate="<b>Qualité %{x}</b><br>%{y} cycles<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(title="Segment qualité", gridcolor="#2d3748"),
        yaxis=dict(title="Nombre de cycles", gridcolor="#2d3748"),
    )
    return fig


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def _build_layout():
    df   = load_fait_capteurs()
    kpis = load_kpis()

    taux_class = "kpi-value--danger" if kpis["taux_panne"] > 5 else "kpi-value--warning" if kpis["taux_panne"] > 2 else "kpi-value--ok"
    dispo_class = "kpi-value--ok"    if kpis["taux_dispo"] > 97 else "kpi-value--warning"

    return html.Div([

        # --- KPIs ---
        html.Div(className="kpi-grid", children=[
            html.Div(className="kpi-card", children=[
                html.Div("Cycles analysés", className="kpi-label"),
                html.Div(f"{kpis['total_cycles']:,}", className="kpi-value"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Pannes détectées", className="kpi-label"),
                html.Div(f"{kpis['nb_pannes']:,}", className=f"kpi-value {taux_class}"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Taux de panne", className="kpi-label"),
                html.Div(f"{kpis['taux_panne']} %", className=f"kpi-value {taux_class}"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Disponibilité machine", className="kpi-label"),
                html.Div(f"{kpis['taux_dispo']} %", className=f"kpi-value {dispo_class}"),
            ]),
        ]),

        # --- Graphiques ---
        html.Div(className="charts-grid", children=[

            html.Div(className="chart-card", children=[
                html.Div("Répartition des pannes par type", className="chart-title"),
                dcc.Graph(
                    figure=_fig_pannes_par_type(df),
                    config={"displayModeBar": False},
                    style={"height": "360px"},
                ),
            ]),

            html.Div(className="chart-card", children=[
                html.Div("Distribution qualité produit (L / M / H)", className="chart-title"),
                dcc.Graph(
                    figure=_fig_distribution_qualite(df),
                    config={"displayModeBar": False},
                    style={"height": "360px"},
                ),
            ]),

        ]),

    ])


layout = _build_layout()
