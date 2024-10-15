import networkx as nx
import plotly.graph_objs as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State

from extraction import get_opponents_by_month, get_player_data
from network import add_edge, add_node

app = Dash("Network Graph")


def create_figure(graph: nx.Graph):
    pos = nx.spring_layout(graph)  # May alter if needed

    edge_x = []
    edge_y = []
    for edge in graph.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    edges = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1, color="#888"),
        hoverinfo="none",
        mode="lines",
        showlegend=False,
    )

    node_x = [pos[node][0] for node in graph.nodes()]
    node_y = [pos[node][1] for node in graph.nodes()]
    node_text = [str(node) for node in graph.nodes()]

    nodes = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers",
        hoverinfo="text",
        text=node_text,
        marker=dict(
            size=20,
            color="red",
        ),
        showlegend=False,
    )

    fig = go.Figure(data=[edges, nodes])
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
        "nodes": list(graph.nodes()),
        "edges": list(graph.edges()),
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
    player = get_player_data(username)
    for opponent in get_opponents_by_month(username):
        node = get_player_data(opponent)
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


def main():
    """Run the Dash app."""
    graph = initialize_graph()
    app.layout = html.Div(
        [
            dcc.Store(id="graph-data", data=graph_to_data(graph)),
            dcc.Loading(
                id="loading",
                type="default",
                children=[
                    dcc.Graph(
                        id="network-graph",
                        figure=create_figure(graph),
                        style={"height": "100vh"},
                    ),
                ],
            ),
        ]
    )
    app.run_server(debug=True)


if __name__ == "__main__":
    main()
