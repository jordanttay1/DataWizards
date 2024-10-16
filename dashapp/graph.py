import networkx as nx
import numpy as np
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from matplotlib import pyplot as plt

from extraction import get_opponents_by_month, get_player_data
from network import add_edge, add_node

from . import app


def create_figure(graph: nx.Graph):
    """Create a Plotly figure from a NetworkX graph."""
    pos = nx.spring_layout(graph)  # May alter if needed

    min_weight = 0
    max_weight = max(
        (data.get("weight", 1) for _, _, data in graph.edges(data=True)), default=1
    )
    cmap = plt.get_cmap("plasma")

    edges = []
    for edge in graph.edges(data=True):
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]

        weight = edge[-1].get("weight", 1)

        if max_weight > min_weight:
            normalized_weight = (weight - min_weight) / (max_weight - min_weight)
        else:
            normalized_weight = 0
        color = cmap(normalized_weight)
        r, g, b = (int(c * 255) for c in color[:3])
        edge_trace = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            line=dict(
                width=2,
                color=f"rgba({r}, {g}, {b}, 1)",
            ),
            mode="lines",
            showlegend=False,
            hoverinfo="none",
        )
        edges.append(edge_trace)

    fig = go.Figure(data=edges)

    node_x = [pos[node][0] for node in graph.nodes()]
    node_y = [pos[node][1] for node in graph.nodes()]
    node_text = [str(node) for node in graph.nodes()]
    ratings = [graph.nodes[node].get("rating", 0) for node in graph.nodes()]
    norm_ratings = (ratings - np.min(ratings)) / (np.max(ratings) - np.min(ratings))
    node_colors = cmap(norm_ratings)

    nodes = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,
        marker=dict(
            size=15,
            color=[
                f"rgba({int(c[0]*255)}, {int(c[1]*255)}, {int(c[2]*255)}, 1)"
                for c in node_colors
            ],
        ),
        showlegend=False,
    )

    fig.add_trace(nodes)

    fig.update_layout(
        showlegend=False,
        hovermode="closest",
        margin=dict(b=0, l=0, r=0, t=0),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=False, zeroline=False, visible=False),
        width=None,
        height=None,
    )

    return fig


def graph_to_data(graph: nx.Graph):
    """Convert the graph to store both nodes and edges."""
    return {
        "nodes": list(graph.nodes(data=True)),
        "edges": list(graph.edges(data=True)),
    }


def data_to_graph(graph_data):
    """Convert stored data back to a graph."""
    graph = nx.Graph()
    graph.add_nodes_from(graph_data["nodes"])
    graph.add_edges_from(graph_data["edges"])
    return graph


@app.callback(
    Output("network-graph", "figure"),
    Output("graph-data", "data"),
    Input("network-graph", "clickData"),
    State("graph-data", "data"),
)
def update_graph(clickData, graph_data):
    """Update the graph when a node is clicked."""
    if clickData is None:
        return create_figure(data_to_graph(graph_data)), graph_data

    clicked_node = clickData["points"][0]["text"]
    print(f"Clicked node: {clicked_node}")

    graph = data_to_graph(graph_data)
    _add_opponents(graph, clicked_node)

    return create_figure(graph), graph_to_data(graph)


def _add_opponents(graph: nx.Graph, username: str) -> nx.Graph:
    """Add opponents to the graph."""
    if (player := get_player_data(username)) is None:
        raise ValueError(f"Player {username} not found. This is unexpected.")
    for opponent in get_opponents_by_month(username):
        if node := get_player_data(opponent):
            graph = add_edge(graph, player, node)


def initialize_graph(username: str = "fabianocaruana") -> nx.Graph:
    """_summary_

    Args:
        username (str, optional): Player to intialize with. Defaults to "fabianocaruana".

    Returns:
        nx.Graph: NetworkX graph object.
    """
    graph = nx.Graph()
    player = get_player_data(username)
    graph = add_node(graph, player)
    _add_opponents(graph, username)
    return graph
