import networkx as nx
import numpy as np
import pandas as pd
from dash import html

from network import PlayerNode


def _detect_anomalies(graph) -> pd.DataFrame:
    """Detect anomalies in the graph based on edge weight."""
    anomalies = []

    weight_threshold = np.percentile(
        [data.get("weight", 1) for _, _, data in graph.edges(data=True)], 99
    )

    for edge in graph.edges(data=True):
        weight = edge[-1].get("weight", 1)
        if weight > weight_threshold:
            anomalies.append(
                {
                    "Source": f"{edge[0]} - {edge[1]}",
                    "Type": "Rating Difference",
                    "Value": weight,
                }
            )

    return pd.DataFrame(anomalies)


def _detect_probability_anomalies(graph) -> pd.DataFrame:
    """Detect anomalies in the graph based on Probability of Win vs Actual Win."""

    def calculate_win_probability(rating_a: int, rating_b: int) -> float:
        """Calculate the win probability of player A against player B."""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def get_player_result(player: dict) -> float:
        if player.get("result") == "win":
            return 1
        elif player.get("result") == "stalemate":
            return 0.5
        return 0

    player_games: dict = {}
    anomalies = []
    for edge in graph.edges(data=True):
        if not edge[-1].get("data"):
            print("No data - skipping")
            continue
        games = edge[-1].get("data", 0)
        for game in games:
            player_a = game.get("white", {})
            player_b = game.get("black", {})

            player_a_probability = calculate_win_probability(
                player_a.get("rating"), player_b.get("rating")
            )
            player_b_probability = calculate_win_probability(
                player_b.get("rating"), player_a.get("rating")
            )

            player_a_result = get_player_result(player_a) - player_a_probability
            player_b_result = get_player_result(player_b) - player_b_probability

            player_games[player_a["username"]] = (
                player_games.get(player_a["username"], 0) + player_a_result
            )
            player_games[player_b["username"]] = (
                player_games.get(player_b["username"], 0) + player_b_result
            )

    percentile = np.percentile(list(player_games.values()), 98)
    for player, result in player_games.items():
        if result > percentile:
            anomalies.append(
                {"Source": player, "Type": "Win Probability", "Value": result}
            )

    return pd.DataFrame(anomalies)


def _page_rank_scores(graph) -> pd.DataFrame:
    """Calculate the PageRank scores for the graph."""
    scores = nx.pagerank(graph)
    scores_df = pd.DataFrame(
        [(node, "PageRank", score) for node, score in scores.items()],
        columns=["Source", "Type", "Value"],
    )

    percentile = np.percentile(scores_df["Value"], 98)
    return scores_df[scores_df["Value"] > percentile]


def create_anomaly_stats(graph):
    """Create the content for the Anomaly Detection tab."""
    anomalies = _detect_anomalies(graph)
    probability_anomalies = _detect_probability_anomalies(graph)
    page_rank_anomalies = _page_rank_scores(graph)
    anomalies = pd.concat([anomalies, probability_anomalies, page_rank_anomalies])

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
