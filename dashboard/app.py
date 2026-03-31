"""
StarDash — Application Dash principale
Pipeline data industriel — AI4I 2020 Predictive Maintenance
"""
import dash
from dash import dcc, html, Input, Output

from layouts import (
    vue_generale,
    surveillance_capteurs,
    maintenance_predictive,
    performance_process,
)

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    title="StarDash — Maintenance Prédictive",
    assets_folder="assets",
    suppress_callback_exceptions=True,
)
server = app.server  # exposé pour Gunicorn / Docker

# ---------------------------------------------------------------------------
# Layout principal
# ---------------------------------------------------------------------------

TABS = [
    {"label": "Vue générale",          "value": "vue-generale"},
    {"label": "Surveillance capteurs", "value": "surveillance-capteurs"},
    {"label": "Maintenance prédictive","value": "maintenance-predictive"},
    {"label": "Performance process",   "value": "performance-process"},
]

app.layout = html.Div(
    id="app-container",
    children=[

        # --- En-tête ---
        html.Header(
            className="header",
            children=[
                html.Div(className="header-left", children=[
                    html.Div(className="header-brand", children=[
                        html.H1("StarDash", className="header-title"),
                        html.Span(className="header-live", children=[
                            html.Span(className="live-dot"),
                            html.Span("Live", className="live-label"),
                        ]),
                    ]),
                    html.Span("Maintenance Prédictive Industrielle", className="header-subtitle"),
                ]),
                html.Div(className="header-right", children=[
                    html.Div(className="header-meta", children=[
                        html.Span("Dataset", className="meta-label"),
                        html.Span("AI4I 2020", className="meta-value"),
                    ]),
                    html.Div(className="header-meta", children=[
                        html.Span("Cycles", className="meta-label"),
                        html.Span("10 000", className="meta-value"),
                    ]),
                ]),
            ],
        ),

        # --- Navigation par onglets ---
        dcc.Tabs(
            id="tabs",
            value="vue-generale",
            className="tabs-container",
            children=[
                dcc.Tab(label=t["label"], value=t["value"], className="tab", selected_className="tab--selected")
                for t in TABS
            ],
        ),

        # --- Contenu dynamique ---
        html.Main(id="tab-content", className="tab-content"),

        # --- Footer ---
        html.Footer(className="footer", children=[
            html.Div(className="footer-inner", children=[
                html.Div(className="footer-left", children=[
                    html.Span("StarDash - 2026", className="footer-brand"),
                    html.Span("Maintenance Prédictive Industrielle — AI4I 2020", className="footer-desc"),
                ]),
                html.Div(className="footer-links", children=[
                    html.A(
                        href="https://github.com/Xavier973/StarDash",
                        target="_blank", rel="noopener noreferrer",
                        className="footer-link",
                        children=[
                            html.Span("⌥", className="footer-icon"),
                            "GitHub",
                        ],
                    ),
                    html.A(
                        href="https://www.linkedin.com/in/xavier-cuniberti-528aa84b/",
                        target="_blank", rel="noopener noreferrer",
                        className="footer-link",
                        children=[
                            html.Span("in", className="footer-icon footer-icon--li"),
                            "LinkedIn",
                        ],
                    ),
                    html.A(
                        href="mailto:x.cuniberti@gmail.com",
                        className="footer-link",
                        children=[
                            html.Span("@", className="footer-icon"),
                            "x.cuniberti@gmail.com",
                        ],
                    ),
                    html.A(
                        href="https://data-service.fr",
                        target="_blank", rel="noopener noreferrer",
                        className="footer-link",
                        children=[
                            html.Span("◈", className="footer-icon"),
                            "data-service.fr",
                        ],
                    ),
                ]),
            ]),
        ]),

    ],
)

# ---------------------------------------------------------------------------
# Callback navigation
# ---------------------------------------------------------------------------

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "value"),
)
def render_tab(tab: str):
    mapping = {
        "vue-generale":           vue_generale,
        "surveillance-capteurs":  surveillance_capteurs,
        "maintenance-predictive": maintenance_predictive,
        "performance-process":    performance_process,
    }
    return mapping.get(tab, html.Div("Onglet introuvable"))


# ---------------------------------------------------------------------------
# Lancement
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
