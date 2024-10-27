from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional

import networkx as nx


@dataclass
class PlayerNode:
    """Dataclass to represent a player node in the graph."""

    uid: int
    name: str
    username: str
    country: str
    rating: int


@dataclass
class PlayerDetails:
    """Dataclass representing details about a player in a match."""

    uid: int
    username: str
    rating: int
    result: str


@dataclass
class GameEdge:
    """Dataclass representing an edge between two players."""

    pgn: str
    time_control: str
    time_class: str
    rules: str
    accuracies: Dict[str, float]
    eco_code: str

    white: PlayerDetails
    black: PlayerDetails

    start_time: int
    end_time: int
    duration: Optional[int] = field(init=False)

    def __post_init__(self):
        self.duration = self.end_time - self.start_time


def add_node(graph: nx.Graph, node: PlayerNode | None) -> nx.Graph:
    """Add a node to the graph if it doesn't already exist."""
    if node is not None and node.username not in graph:
        graph.add_node(node.username, **asdict(node))
    return graph


def add_edge(
    graph: nx.Graph,
    node1: PlayerNode | None,
    node2: PlayerNode | None,
    edge_data: List[GameEdge] | None = None,
) -> nx.Graph:
    """Add an edge between two nodes if it doesn't already exist."""
    if node1 is None or node2 is None or edge_data is None:
        print("Cannot add edge with missing nodes or edge data.")
        return graph
    if node1.username not in graph:
        graph = add_node(graph, node1)
    if node2.username not in graph:
        graph = add_node(graph, node2)
    if not graph.has_edge(node1.username, node2.username):
        weight = abs(node1.rating - node2.rating)
        graph.add_edge(
            node1.username,
            node2.username,
            weight=weight,
            data=[asdict(edge) for edge in edge_data],
        )
    return graph
