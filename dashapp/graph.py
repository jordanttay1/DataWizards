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


def _add_opponents(graph: nx.Graph, username: str) -> nx.Graph:
    """Add opponents to the graph."""
    if (player := get_player_data(username)) is None:
        raise ValueError(
            f"Player {username} not found. Is this a valid chess.com username?"
        )
    for opponent in get_opponents_by_month(username):
        if node := get_player_data(opponent):
            graph = add_edge(graph, player, node)


def add_opponents_with_depth(graph: nx.Graph, username: str, depth: int) -> nx.Graph:
    """Recursively add opponents to the graph up to a specified depth."""

    def recursive_add(username: str, current_depth: int):
        if current_depth > depth:
            return

        _add_opponents(graph, username)

        opponents = get_opponents_by_month(username)
        for opponent in opponents:
            if get_player_data(opponent):
                recursive_add(opponent, current_depth + 1)

    recursive_add(username, 1)
    return graph


def initialize_graph(username: str = "fabianocaruana", depth: int = 1) -> nx.Graph:
    """_summary_

    Args:
        username (str, optional): Player to intialize with. Defaults to "fabianocaruana".
        depth (int, optional): Depth of the graph. Defaults to 1.

    Returns:
        nx.Graph: NetworkX graph object.
    """
    graph = nx.Graph()
    player = get_player_data(username)
    graph = add_node(graph, player)
    add_opponents_with_depth(graph, username, depth)
    return graph


@app.callback(
    Output("network-graph", "figure"),
    Output("graph-data", "data"),
    Output("graph-error", "displayed"),
    Output("graph-error", "message"),
    Input("init-button", "n_clicks"),
    Input("network-graph", "clickData"),
    State("username-input", "value"),
    State("depth-input", "value"),
    State("graph-data", "data"),
)
def initialize_and_update_graph(n_clicks, clickData, username, depth, graph_data):
    """Initialize and update the graph when the initialize button is clicked."""
    graph = None

    try:
        if graph_data is None or username is not None:
            depth_value = int(depth) if depth else 1
            graph = initialize_graph(username or "fabianocaruana", depth_value)
            return create_figure(graph), graph_to_data(graph), False, ""
        if graph is None and graph_data is not None:
            graph = data_to_graph(graph_data)

        if clickData is not None:
            clicked_node = clickData["points"][0]["text"]
            print(f"Clicked node: {clicked_node}")
            _add_opponents(graph, clicked_node)
    except ValueError as e:
        print(e)
        fig = create_figure(graph) if graph is not None else {}
        data = graph_to_data(graph) if graph is not None else None
        return fig, data, True, str(e)

    return create_figure(graph), graph_to_data(graph), False, ""
