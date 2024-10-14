from dataclasses import asdict, dataclass

import networkx as nx


@dataclass
class PlayerNode:
    """Dataclass to represent a player node in the graph."""

    uid: int
    name: str
    username: str
    country: str
    rating: int


def add_node(graph: nx.Graph, node: PlayerNode | None) -> nx.Graph:
    """Add a node to the graph if it doesn't already exist."""
    if node is not None and node.username not in graph:
        graph.add_node(node.username, **asdict(node))
    return graph


def add_edge(
    graph: nx.Graph, node1: PlayerNode | None, node2: PlayerNode | None
) -> nx.Graph:
    """Add an edge between two nodes if it doesn't already exist."""
    if node1 is None or node2 is None:
        print("Cannot add edge with missing nodes.")
        return graph
    if node1.username not in graph:
        graph = add_node(graph, node1)
    if node2.username not in graph:
        graph = add_node(graph, node2)
    if not graph.has_edge(node1.username, node2.username):
        graph.add_edge(node1.username, node2.username)
    return graph
