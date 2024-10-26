import numpy as np
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output

from dashapp import app
from dashapp.analytics import (
    create_anomaly_stats,
    create_graph_summary,
    create_player_stats,
)
from dashapp.graph import create_figure, data_to_graph, graph_to_data, initialize_graph


def main():
    """Run the Dash app."""
    graph = initialize_graph()

    app.layout = html.Div(
        style={"flexDirection": "column"},
        children=[
            html.H1(
                "Chess.com Player Network Analysis by Data Wizards",
                style={"textAlign": "center"},
            ),
            html.P(
                "Click on a node to explore the player network.",
                style={"textAlign": "center"},
            ),
            html.Div(
                children=[
                    dcc.Store(id="graph-data", data=graph_to_data(graph)),
                    dcc.Loading(
                        id="loading",
                        type="default",
                        children=[
                            dcc.Graph(
                                id="network-graph",
                                figure=create_figure(graph),
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
    )

    @app.callback(
        Output("analytics-content", "children"),
        Input("analytics-tabs", "value"),
        Input("graph-data", "data"),
    )
    def render_analytics(tab, graph_data):
        graph = data_to_graph(graph_data)
        if tab == "summary-tab":
            return create_graph_summary(graph)
        elif tab == "stats-tab":
            return create_player_stats(graph)
        elif tab == "anomaly-tab":
            return create_anomaly_stats(graph)

    app.run_server(debug=True)


if __name__ == "__main__":
    main()
