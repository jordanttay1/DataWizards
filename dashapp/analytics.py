import numpy as np
import pandas as pd
from dash import html

from network import PlayerNode


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
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()
    average_rating = (
        np.mean([data["rating"] for _, data in graph.nodes(data=True)])
        if graph.number_of_nodes() > 0
        else 0
    )
    highest_rating = (
        max([data["rating"] for _, data in graph.nodes(data=True)], default=0),
    )
    lowest_rating = (
        min([data["rating"] for _, data in graph.nodes(data=True)], default=0),
    )
    return html.Div(
        [
            html.H3("Graph Summary"),
            html.P(f"Number of nodes: {num_nodes}"),
            html.P(f"Number of edges: {num_edges}"),
            html.P(f"Average player rating: {average_rating:.2f}"),
            html.P(f"Highest player rating: {highest_rating[0]}"),
            html.P(f"Lowest player rating: {lowest_rating[0]}"),
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
