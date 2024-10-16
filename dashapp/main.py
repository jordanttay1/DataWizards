from dash import dcc, html

from dashapp.graph import create_figure, graph_to_data, initialize_graph

from . import app


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
