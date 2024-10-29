import json
from typing import Dict, Tuple

import networkx as nx
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, State, callback_context
from matplotlib import pyplot as plt

from dashapp import app
from extraction import get_opponents_and_games_by_month, get_player_data
from network import PlayerNode, add_edge, add_node


def create_figure(graph: nx.Graph):
    """Create a Plotly figure from a NetworkX graph."""
    pos = nx.fruchterman_reingold_layout(graph)  # May alter if needed

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
    data = {
        "nodes": list(graph.nodes(data=True)),
        "edges": list(graph.edges(data=True)),
    }

    with open("graph_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    return data


def data_to_graph(graph_data):
    """Convert stored data back to a graph."""
    graph = nx.Graph()
    graph.add_nodes_from(graph_data["nodes"])
    graph.add_edges_from(graph_data["edges"])
    return graph


def _add_opponents(
    graph: nx.Graph, username: str, player: PlayerNode | None = None
) -> Tuple[nx.Graph, Dict[str, PlayerNode | None]]:
    """Add opponents to the graph."""
    if player is None and (player := get_player_data(username)) is None:
        raise ValueError(
            f"Player {username} not found. Is this a valid chess.com username?"
        )
    opponents_and_games = get_opponents_and_games_by_month(username)
    opponents_node = {}
    for opponent, games in opponents_and_games.items():
        opponents_node[opponent] = get_player_data(opponent)
        if opponents_node[opponent] is not None:
            graph = add_edge(graph, player, opponents_node[opponent], games)

    return (graph, opponents_node)


def add_opponents_with_depth(
    graph: nx.Graph, username: str, depth: int, player: PlayerNode | None = None
) -> nx.Graph:
    """Recursively add opponents to the graph up to a specified depth."""

    def recursive_add(username: str, current_depth: int, player: PlayerNode | None):
        if current_depth > depth:
            return

        _, opponents_node = _add_opponents(graph, username, player=player)

        for opponent, node in opponents_node.items():
            if node:
                recursive_add(opponent, current_depth + 1, player=node)

    recursive_add(username, 1, player)
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
    add_opponents_with_depth(graph, username, depth, player=player)
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

    def initialize_new_graph(username, depth):
        """Initializes a new graph with given username and depth."""
        depth_value = int(depth) if depth else 1
        user = username or "fabianocaruana"
        graph = initialize_graph(user, depth_value)
        print(f"Initialized graph with {username}.")
        return graph

    def update_graph_from_click(graph, clickData):
        """Updates the graph with additional data based on clicked node."""
        clicked_node = clickData["points"][0]["text"]
        print(f"Clicked node: {clicked_node}")
        player = PlayerNode(**dict(graph.nodes(data=True)).get(clicked_node))
        graph, _ = _add_opponents(graph, clicked_node, player=player)

    def get_default_response(graph):
        """Creates default responses when no error occurs."""
        return create_figure(graph), graph_to_data(graph), False, ""

    try:
        ctx = callback_context
        if graph_data is None or (
            ctx.triggered and ctx.triggered[0]["prop_id"] == "init-button.n_clicks"
        ):
            graph = initialize_new_graph(username, depth)
            return get_default_response(graph)

        graph = data_to_graph(graph_data)

        if clickData is not None:
            update_graph_from_click(graph, clickData)

        return get_default_response(graph)

    except ValueError as e:
        print(e)
        figure = create_figure(graph) if graph else {}
        data = graph_to_data(graph) if graph else None
        return figure, data, True, str(e)
