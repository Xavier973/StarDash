"""
StarDash — Section 3 : Maintenance prédictive (section principale)
- Taux de disponibilité machine par segment qualité
- Jauge d'usure outil : normal / attention / critique
- Alertes actives : machines en zone rouge
- Top 5 des causes de panne
"""
from dash import html, dcc
import plotly.graph_objects as go

from data import load_fait_capteurs, load_kpis

PLOTLY_THEME = dict(
    paper_bgcolor="#1a1f2e",
    plot_bgcolor="#1a1f2e",
    font=dict(color="#a0aec0", size=12),
    margin=dict(l=40, r=20, t=30, b=40),
)

# ---------------------------------------------------------------------------
# Graphiques
# ---------------------------------------------------------------------------

def _fig_disponibilite_par_qualite(df) -> go.Figure:
    """Bar chart horizontal : taux de disponibilité par segment qualité."""
    result = []
    for q in ["L", "M", "H"]:
        sub = df[df["qualite"] == q]
        taux_dispo = round((1 - sub["machine_failure"].mean()) * 100, 2)
        result.append({"qualite": f"Qualité {q}", "dispo": taux_dispo})

    labels = [r["qualite"] for r in result]
    values = [r["dispo"] for r in result]
    colors = ["#68d391" if v >= 97 else "#f6ad55" if v >= 94 else "#fc8181" for v in values]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v} %" for v in values],
        textposition="inside",
        textfont=dict(color="#0f1117", size=13, weight="bold"),
        hovertemplate="<b>%{y}</b><br>Disponibilité : %{x:.2f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(title="Disponibilité (%)", range=[90, 100], gridcolor="#2d3748"),
        yaxis=dict(gridcolor="#2d3748"),
        shapes=[dict(
            type="line", x0=97, x1=97, y0=-0.5, y1=2.5,
            line=dict(color="#fc8181", width=1.5, dash="dot"),
        )],
        annotations=[dict(
            x=97, y=2.6, text="Seuil 97%", showarrow=False,
            font=dict(color="#fc8181", size=10),
        )],
    )
    return fig


def _fig_jauge_usure(df) -> go.Figure:
    """Jauge d'usure outil : répartition normal / attention / critique."""
    counts = df["statut_usure"].value_counts()
    total  = len(df)

    normal    = counts.get("normal", 0)
    attention = counts.get("attention", 0)
    critique  = counts.get("critique", 0)
    pct_critique = round(critique / total * 100, 1)

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=pct_critique,
        number=dict(suffix=" %", font=dict(color="#e2e8f0", size=36)),
        delta=dict(reference=5, increasing=dict(color="#fc8181"), decreasing=dict(color="#68d391")),
        gauge=dict(
            axis=dict(range=[0, 20], tickcolor="#a0aec0", tickfont=dict(color="#a0aec0")),
            bar=dict(color="#fc8181"),
            bgcolor="#2d3748",
            steps=[
                dict(range=[0, 5],   color="#1a3a2a"),
                dict(range=[5, 10],  color="#3d3010"),
                dict(range=[10, 20], color="#3d1010"),
            ],
            threshold=dict(
                line=dict(color="#f6ad55", width=3),
                thickness=0.75,
                value=10,
            ),
        ),
        title=dict(text="Cycles en zone critique (%)", font=dict(color="#a0aec0", size=13)),
    ))
    theme = {**PLOTLY_THEME, "margin": dict(l=30, r=30, t=60, b=20)}
    fig.update_layout(
        **theme,
        annotations=[
            dict(x=0.15, y=0.12, text=f"Normal<br><b>{normal:,}</b>",
                 showarrow=False, font=dict(color="#68d391", size=12), xref="paper", yref="paper"),
            dict(x=0.5,  y=0.12, text=f"Attention<br><b>{attention:,}</b>",
                 showarrow=False, font=dict(color="#f6ad55", size=12), xref="paper", yref="paper"),
            dict(x=0.85, y=0.12, text=f"Critique<br><b>{critique:,}</b>",
                 showarrow=False, font=dict(color="#fc8181", size=12), xref="paper", yref="paper"),
        ],
    )
    return fig


def _fig_top5_causes(df) -> go.Figure:
    """Bar chart horizontal : top 5 causes de panne."""
    causes = {
        "Usure outil":          df["panne_usure_outil"].sum(),
        "Dissip. thermique":    df["panne_dissipation_thermique"].sum(),
        "Surpuissance":         df["panne_surpuissance"].sum(),
        "Surcharge":            df["panne_surcharge"].sum(),
        "Aléatoire":            df["panne_aleatoire"].sum(),
    }
    sorted_causes = sorted(causes.items(), key=lambda x: x[1], reverse=True)
    labels = [c[0] for c in sorted_causes]
    values = [c[1] for c in sorted_causes]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(
            color=values,
            colorscale=[[0, "#2b4c8c"], [0.5, "#f6ad55"], [1, "#fc8181"]],
            showscale=False,
        ),
        text=values,
        textposition="outside",
        textfont=dict(color="#e2e8f0"),
        hovertemplate="<b>%{y}</b><br>%{x} occurrences<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_THEME,
        xaxis=dict(title="Nombre d'occurrences", gridcolor="#2d3748"),
        yaxis=dict(gridcolor="#2d3748", autorange="reversed"),
    )
    return fig


def _build_alertes(df) -> html.Div:
    """Table des machines actuellement en zone critique."""
    critiques = df[df["statut_usure"] == "critique"].copy()

    if critiques.empty:
        return html.Div("Aucune alerte active.", style={"color": "#68d391", "padding": "1rem"})

    # Dernière mesure par machine
    derniere = (
        critiques.sort_values("timestamp")
        .groupby("product_id")
        .last()
        .reset_index()
        .head(10)
    )

    rows = []
    for _, row in derniere.iterrows():
        statut_color = "#fc8181"
        rows.append(html.Tr([
            html.Td(row["product_id"],            style={"color": "#e2e8f0"}),
            html.Td(row["qualite"],               style={"color": "#a0aec0"}),
            html.Td(f"{row['usure_outil']} min",  style={"color": statut_color, "fontWeight": "bold"}),
            html.Td(row["statut_usure"].upper(),  style={"color": statut_color, "fontWeight": "bold"}),
            html.Td("OUI" if row["machine_failure"] else "non",
                    style={"color": "#fc8181" if row["machine_failure"] else "#68d391"}),
        ]))

    return html.Table(
        style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.85rem"},
        children=[
            html.Thead(html.Tr([
                html.Th("Machine",    style={"color": "#718096", "textAlign": "left", "paddingBottom": "0.5rem"}),
                html.Th("Qualité",    style={"color": "#718096", "textAlign": "left"}),
                html.Th("Usure",      style={"color": "#718096", "textAlign": "left"}),
                html.Th("Statut",     style={"color": "#718096", "textAlign": "left"}),
                html.Th("En panne",   style={"color": "#718096", "textAlign": "left"}),
            ])),
            html.Tbody(rows),
        ],
    )


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def _build_layout():
    df   = load_fait_capteurs()
    kpis = load_kpis()

    nb_critiques = int((df["statut_usure"] == "critique").sum())
    badge_color  = "#fc8181" if nb_critiques > 100 else "#f6ad55"

    return html.Div([

        # --- KPI résumé maintenance ---
        html.Div(className="kpi-grid", style={"marginBottom": "1.5rem"}, children=[
            html.Div(className="kpi-card", children=[
                html.Div("Disponibilité globale", className="kpi-label"),
                html.Div(
                    f"{kpis['taux_dispo']} %",
                    className=f"kpi-value {'kpi-value--ok' if kpis['taux_dispo'] >= 97 else 'kpi-value--warning'}",
                ),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Cycles en zone critique", className="kpi-label"),
                html.Div(f"{nb_critiques:,}", className="kpi-value kpi-value--danger"),
            ]),
            html.Div(className="kpi-card", children=[
                html.Div("Pannes totales", className="kpi-label"),
                html.Div(f"{kpis['nb_pannes']:,}", className="kpi-value kpi-value--danger"),
            ]),
        ]),

        # --- Dispo par qualité + Jauge usure ---
        html.Div(className="charts-grid", style={"marginBottom": "1.5rem"}, children=[

            html.Div(className="chart-card", children=[
                html.Div("Disponibilité par segment qualité", className="chart-title"),
                dcc.Graph(
                    figure=_fig_disponibilite_par_qualite(df),
                    config={"displayModeBar": False},
                    style={"height": "300px"},
                ),
            ]),

            html.Div(className="chart-card", children=[
                html.Div("Jauge d'usure outil", className="chart-title"),
                dcc.Graph(
                    figure=_fig_jauge_usure(df),
                    config={"displayModeBar": False},
                    style={"height": "300px"},
                ),
            ]),

        ]),

        # --- Alertes actives + Top 5 causes ---
        html.Div(className="charts-grid", children=[

            html.Div(className="chart-card", children=[
                html.Div([
                    html.Span("Alertes actives — Machines en zone critique", className="chart-title",
                              style={"display": "inline"}),
                    html.Span(f" {nb_critiques}", style={
                        "marginLeft": "0.5rem", "background": badge_color, "color": "#0f1117",
                        "borderRadius": "999px", "padding": "0.1rem 0.5rem",
                        "fontSize": "0.75rem", "fontWeight": "bold",
                    }),
                ], style={"marginBottom": "1rem"}),
                _build_alertes(df),
            ]),

            html.Div(className="chart-card", children=[
                html.Div("Top 5 — Causes de panne", className="chart-title"),
                dcc.Graph(
                    figure=_fig_top5_causes(df),
                    config={"displayModeBar": False},
                    style={"height": "300px"},
                ),
            ]),

        ]),

    ])


layout = _build_layout()
