from datetime import datetime

from dash import Input, Output, dcc, html

from dashapp import app
from dashapp.analytics import (
    create_anomaly_stats,
    create_graph_summary,
    create_player_stats,
)
from dashapp.graph import data_to_graph

app.layout = html.Div(
    id="app-container",
    style={
        "maxWidth": "1400px",
        "margin": "auto",
        "padding": "20px",
        "borderRadius": "10px",
        "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
        "position": "relative",
    },
    children=[
        html.Div(
            style={"flexDirection": "column"},
            children=[
                html.H1(
                    "Chess.com Player Network Analysis by Data Wizards",
                    style={"textAlign": "center"},
                ),
                html.P(
                    [
                        "Enter a username to begin exploring!",
                        html.Br(),
                        "Click on a node to explore the player network, or increase the depth counter to explore further.",
                    ],
                    style={"textAlign": "center"},
                ),
                # Username input, Date input, depth counter
                html.Div(
                    style={
                        "textAlign": "center",
                        "display": "flex",
                        "justifyContent": "center",
                    },
                    children=[
                        html.Div(
                            children=[
                                html.P("Chess.com Username:", className="input-label"),
                                dcc.Input(
                                    id="username-input",
                                    type="text",
                                    placeholder="Enter Username",
                                    className="input-field",
                                    style={"margin": "0 5px"},
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                html.P("Year:", className="input-label"),
                                dcc.Input(
                                    id="year-input",
                                    type="number",
                                    value=datetime.now().year,
                                    min=2008,
                                    max=datetime.now().year,
                                    className="input-field",
                                    style={"width": "80px", "margin": "0 5px"},
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                html.P("Month:", className="input-label"),
                                dcc.Input(
                                    id="month-input",
                                    type="number",
                                    value=datetime.now().month,
                                    min=1,
                                    max=12,
                                    className="input-field",
                                    style={"width": "80px", "margin": "0 5px"},
                                ),
                            ],
                        ),
                        html.Div(
                            children=[
                                html.P("Depth:", className="input-label"),
                                dcc.Input(
                                    id="depth-input",
                                    type="number",
                                    value=1,
                                    min=1,
                                    max=5,
                                    className="input-field depth-input",
                                ),
                            ],
                        ),
                    ],
                ),
                # Button to Graph
                html.Div(
                    style={"textAlign": "center"},
                    children=[
                        html.Button(
                            "Graph",
                            id="init-button",
                            n_clicks=0,
                            style={
                                "margin": "10px",
                                "width": "150px",
                                "height": "40px",
                                "fontSize": "16px",
                                "fontWeight": "bold",
                                "color": "white",
                                "backgroundColor": "#007bff",
                                "border": "none",
                                "borderRadius": "5px",
                            },
                        )
                    ],
                ),
                html.Div(
                    children=[
                        dcc.Store(id="graph-data", data=None),
                        dcc.Loading(
                            id="loading",
                            type="default",
                            overlay_style={
                                "visibility": "visible",
                                "filter": "blur(2px)",
                            },
                            children=[
                                dcc.Graph(
                                    id="network-graph",
                                    className="blur",
                                    figure={},
                                ),
                                dcc.ConfirmDialog(
                                    id="graph-error",
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    style={
                        "flexDirection": "row",
                        "padding": "10px",
                    },
                    children=[
                        dcc.Tabs(
                            id="analytics-tabs",
                            value="summary-tab",
                            children=[
                                dcc.Tab(label="Summary", value="summary-tab"),
                                dcc.Tab(label="Player Stats", value="stats-tab"),
                                dcc.Tab(label="Anomalies", value="anomaly-tab"),
                            ],
                        ),
                        html.Div(id="analytics-content"),
                    ],
                ),
            ],
        ),
    ],
)


@app.callback(
    Output("network-graph", "className"),
    Input("init-button", "n_clicks"),
)
def remove_blur(n_clicks):
    """Remove blur effect when the initialize button is clicked."""
    if n_clicks > 0:
        return "no-blur"
    return "blur"


@app.callback(
    Output("analytics-content", "children"),
    Input("analytics-tabs", "value"),
    Input("graph-data", "data"),
)
def render_analytics(tab, graph_data):
    """Render the content for the selected tab."""
    if not graph_data:
        return html.Div([html.H3("No graph data available.")])
    graph = data_to_graph(graph_data)
    if tab == "summary-tab":
        return create_graph_summary(graph)
    elif tab == "stats-tab":
        return create_player_stats(graph)
    elif tab == "anomaly-tab":
        return create_anomaly_stats(graph)


def main():
    """Run the Dash app."""
    app.run_server(debug=True)


if __name__ == "__main__":
    main()

# Expose server for gunicorn
server = app.server
