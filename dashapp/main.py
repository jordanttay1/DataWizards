import numpy as np
import pandas as pd
from dash import dcc, html
from dash.dependencies import Input, Output

from dashapp.graph import create_figure, data_to_graph, graph_to_data, initialize_graph
from network import PlayerNode

from . import app


def _detect_anomalies(graph) -> pd.DataFrame:
    """Detect anomalies in the graph based on edge weight."""
    anomalies = []

    weight_threshold = np.percentile(
        [data.get("weight", 1) for _, _, data in graph.edges(data=True)], 90
    )

    for edge in graph.edges(data=True):
        weight = edge[-1].get("weight", 1)
        if weight > weight_threshold:
            anomalies.append(
                {"Source": f"{edge[0]} - {edge[1]}", "Type": "Weight", "Value": weight}
            )

    return pd.DataFrame(anomalies)


def create_anomaly_stats(graph):
    """Create the content for the Anomaly Detection tab."""
    anomalies = _detect_anomalies(graph)

    if anomalies.empty:
        return html.Div([html.H3("No anomalies detected in the graph.")])

    anomaly_table = html.Table(
        [
            html.Thead(
                html.Tr(
                    [
                        html.Th(col, style={"textAlign": "left"})
                        for col in anomalies.columns
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(row["Source"]),
                            html.Td(row["Type"]),
                            html.Td(row["Value"]),
                        ],
                    )
                    for _, row in anomalies.iterrows()
                ],
            ),
        ],
        style={"width": "100%"},
    )

    return html.Div(
        [
            html.H3("Anomaly Detection Results"),
            anomaly_table,
        ]
    )


def create_graph_summary(graph):
    """Create a summary of the graph."""
    num_nodes = len(graph.nodes)
    num_edges = len(graph.edges)
    return html.Div(
        [
            html.H3("Graph Summary"),
            html.P(f"Number of nodes: {num_nodes}"),
            html.P(f"Number of edges: {num_edges}"),
        ]
    )


def create_player_stats(graph):
    """Create player statistics."""
    nodes = graph.nodes(data=True)
    headers = [field for field in PlayerNode.__dataclass_fields__]

    return html.Div(
        [
            html.H3("Player Statistics"),
            html.Table(
                [
                    html.Tr(
                        [html.Th(field) for field in headers],
                        style={"textAlign": "left"},
                    )
                ]
                + [
                    html.Tr([html.Td(node[-1].get(field)) for field in headers])
                    for node in nodes
                ]
            ),
        ]
    )


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
