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


def add_node(graph: nx.Graph, node: PlayerNode) -> nx.Graph:
    """Add a node to the graph if it doesn't already exist."""
    if node.uid not in graph:
        graph.add_node(node.uid, **asdict(node))
    return graph


def add_edge(graph: nx.Graph, node1: PlayerNode, node2: PlayerNode) -> nx.Graph:
    """Add an edge between two nodes if it doesn't already exist."""
    graph = add_node(graph, node1)
    graph = add_node(graph, node2)
    if not graph.has_edge(node1.uid, node2.uid):
        graph.add_edge(node1.uid, node2.uid)
    return graph
