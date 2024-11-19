import asyncio
from typing import Dict, Optional, Tuple

import networkx as nx
import numpy as np
import plotly.graph_objs as go
from dash import Input, Output, State, callback_context
from matplotlib import pyplot as plt

from dashapp import app
from extraction import (
    fetch_player_data,
    get_opponents_and_games_by_month,
    get_player_data,
)
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
    norm_ratings = (ratings - np.min(ratings)) / max(
        1, (np.max(ratings) - np.min(ratings))
    )
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

    return data


def data_to_graph(graph_data):
    """Convert stored data back to a graph."""
    graph = nx.Graph()
    graph.add_nodes_from(graph_data["nodes"])
    graph.add_edges_from(graph_data["edges"])
    return graph


async def _add_opponents_async(
    graph: nx.Graph,
    username: str,
    year: Optional[int],
    month: Optional[int],
    player: Optional[PlayerNode] = None,
) -> Tuple[nx.Graph, Dict[str, Optional[PlayerNode]]]:
    """Add opponents to the graph."""
    if player is None and (player := get_player_data(username)) is None:
        raise ValueError(
            f"Player {username} not found. Is this a valid chess.com username?"
        )
    opponents_node: dict = {}

    # Add filters to reduce data
    # if not is_within_rated_range(player):
    #     return (graph, opponents_node)
    # if not is_within_country(player):
    #     return (graph, opponents_node)

    opponents_and_games = get_opponents_and_games_by_month(username, year, month)

    fetch_tasks = [fetch_player_data(opponent) for opponent in opponents_and_games]
    fetched_nodes = await asyncio.gather(*fetch_tasks)

    for opponent, node in zip(opponents_and_games.keys(), fetched_nodes):
        if node is None:
            continue
        # if not is_within_rated_range(node):
        #     continue
        # if not is_within_country(node):
        #     continue

        opponents_node[opponent] = node
        graph = add_edge(graph, player, node, opponents_and_games[opponent])

    return (graph, opponents_node)


def _add_opponents(
    graph: nx.Graph,
    username: str,
    year: Optional[int],
    month: Optional[int],
    player: Optional[PlayerNode] = None,
) -> Tuple[nx.Graph, Dict[str, Optional[PlayerNode]]]:
    """Synchronous wrapper for the asynchronous _add_opponents_async."""
    return asyncio.run(_add_opponents_async(graph, username, year, month, player))


def add_opponents_with_depth(
    graph: nx.Graph,
    username: str,
    year: Optional[int],
    month: Optional[int],
    depth: int,
    player: Optional[PlayerNode] = None,
) -> nx.Graph:
    """Recursively add opponents to the graph up to a specified depth."""

    async def recursive_add(
        graph: nx.Graph, username: str, current_depth: int, player: Optional[PlayerNode]
    ):
        if current_depth > depth:
            return

        _, opponents_node = await _add_opponents_async(
            graph, username, year, month, player
        )

        for opponent, node in opponents_node.items():
            if node:
                await recursive_add(graph, opponent, current_depth + 1, node)

    asyncio.run(recursive_add(graph, username, 1, player))

    return graph


def initialize_graph(
    username: str = "fabianocaruana",
    year: Optional[int] = None,
    month: Optional[int] = None,
    depth: int = 1,
) -> nx.Graph:
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
    graph = add_opponents_with_depth(graph, username, year, month, depth, player=player)
    return graph


@app.callback(
    [
        Output("network-graph", "figure"),
        Output("graph-data", "data"),
        Output("graph-error", "displayed"),
        Output("graph-error", "message"),
    ],
    [
        Input("init-button", "n_clicks"),
        Input("network-graph", "clickData"),
    ],
    [
        State("username-input", "value"),
        State("year-input", "value"),
        State("month-input", "value"),
        State("depth-input", "value"),
        State("graph-data", "data"),
    ],
)
def initialize_and_update_graph(
    n_clicks, click_data, username, year, month, depth, graph_data
):
    """Initialize and update the graph when the initialize button is clicked."""

    def initialize_new_graph(username, depth):
        """Initializes a new graph with given username and depth."""
        user = username or "fabianocaruana"
        graph = initialize_graph(user, year, month, depth)
        print(f"Initialized graph with {username}.")
        return graph

    def update_graph_from_click(
        graph: nx.Graph, click_data: dict, year: Optional[int], month: Optional[int]
    ):
        """Updates the graph with additional data based on clicked node."""
        clicked_node = click_data["points"][0]["text"]
        print(f"Clicked node: {clicked_node}")
        player = PlayerNode(**dict(graph.nodes(data=True)).get(clicked_node) or {})
        graph, _ = _add_opponents(graph, clicked_node, year, month, player=player)

    def get_default_response(graph):
        """Creates default responses when no error occurs."""
        return create_figure(graph), graph_to_data(graph), False, ""

    def init_button_clicked():
        ctx = callback_context
        return ctx.triggered and ctx.triggered[0]["prop_id"] == "init-button.n_clicks"

    try:
        if graph_data is None or (init_button_clicked()):
            try:
                graph = initialize_new_graph(username, depth)
            except ValueError:
                graph = initialize_new_graph(username, 0)
            return get_default_response(graph)

        graph = data_to_graph(graph_data)

        if click_data is not None:
            update_graph_from_click(graph, click_data, year, month)

        return get_default_response(graph)

    except ValueError as e:
        print(e)
        figure = create_figure(graph) if graph else {}
        data = graph_to_data(graph) if graph else None
        return figure, data, True, str(e)
