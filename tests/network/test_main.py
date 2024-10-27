import networkx as nx
import pytest

from network import GameEdge, PlayerNode, add_edge, add_node


@pytest.fixture
def setup_graph():
    """Fixture to create an empty graph for testing."""
    return nx.Graph()


@pytest.fixture
def player_nodes():
    """Fixture to create mock player nodes for testing."""
    return (
        PlayerNode(uid=1, name="", username="player1", country="USA", rating=2000),
        PlayerNode(uid=2, name="", username="player2", country="USA", rating=2000),
        PlayerNode(uid=3, name="", username="player3", country="USA", rating=2000),
    )


@pytest.fixture
def edge_data():
    """Fixture to create mock edge data for testing."""
    return [
        GameEdge(
            pgn="",
            time_control="",
            time_class="",
            rules="",
            accuracies={},
            eco_code="",
            white=None,
            black=None,
            start_time=0,
            end_time=0,
        )
    ]


def test_add_node(setup_graph, player_nodes):
    """Test adding a new node to the graph."""
    graph = setup_graph
    node = player_nodes[0]

    graph = add_node(graph, node)

    assert graph.has_node(node.username)


def test_add_edge_new_nodes(setup_graph, player_nodes, edge_data):
    """Test adding an edge between two new nodes."""
    graph = setup_graph
    node1, node2 = player_nodes[0], player_nodes[1]

    graph = add_edge(graph, node1, node2, edge_data=edge_data)

    assert graph.has_node(node1.username)
    assert graph.has_node(node2.username)
    assert graph.has_edge(node1.username, node2.username)


def test_add_edge_existing_node(setup_graph, player_nodes, edge_data):
    """Test adding an edge between an existing node and a new node."""
    graph = setup_graph
    existing_node = player_nodes[0]
    new_node = player_nodes[1]

    # First, add the existing node
    graph = add_node(graph, existing_node)

    # Now add an edge to the new node
    graph = add_edge(graph, existing_node, new_node, edge_data=edge_data)

    assert graph.has_node(existing_node.username)
    assert graph.has_node(new_node.username)
    assert graph.has_edge(existing_node.username, new_node.username)


def test_no_duplicate_edges(setup_graph, player_nodes, edge_data):
    """Test that adding the same edge twice does not create duplicates."""
    graph = setup_graph
    node1, node2 = player_nodes[0], player_nodes[1]

    graph = add_edge(graph, node1, node2, edge_data=edge_data)
    initial_edge_count = graph.number_of_edges()

    # Try adding the same edge again
    graph = add_edge(graph, node1, node2, edge_data=edge_data)

    assert graph.number_of_edges() == initial_edge_count  # Edge count should not change
