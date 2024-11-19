# Big Chess Analysis by team DataWizards

## DESCRIPTION

The following project is a Big Chess Analysis using the chess.com [API](https://chesscom.readthedocs.io/en/latest/) and [API Wrapper](https://github.com/sarartur/chess.com).

This project is open-source on [Github](https://github.com/jordanttay1/DataWizards), with published docs at [Documentation](https://jordanttay1.github.io/DataWizards/).
Looking to contribute? Visit [CONTRIBUTING](CONTRIBUTING.md) for more details.

## INTRODUCTION

Learn more about the community of players you or your opponent's are part of in Chess.com! Deep-dive into the chess.com network and identify & report unusual anomalies in games or players!

This project enables an interactive graph of chess.com players, pulling player and game data along the way to analyze and identify anomalies.

Deep dive analysis approaches can be found in `notebooks/`.

## INSTALLATION

No installation required! Simply visit our [site](https://cse6242-439117.wl.r.appspot.com) and start exploring.

If local install is preferred:

- `poetry` is highly recommended. Follow [Poetry Installation](https://python-poetry.org/docs/) for installation.
- `poetry install` to install & create a local virtual environment for the project.
  - Alternatively, a `requirements.txt` is generated for `pip`.

## EXECUTION

Execution not required! Simply visit our [site](https://cse6242-439117.wl.r.appspot.com) and start exploring.

If local execution is preferred:

- `poetry` is highly recommended to enable `poetry run`.
  - Alternatively, leverage `requirements.txt` & `python -m venv`.
- `make serve_dev` to launch the webapp on localhost (using Dash)
  -- Alternatively `poetry run python dashapp/main.py`
  -- Alternatively `make serve` to launch with gunicorn on 127.0.0.1:8080

### Exploration

Visit our [site](https://cse6242-439117.wl.r.appspot.com) to get started. There you will be greeted with inputs: Username, Date, and Depth. Please input a chess.com username to begin (modify date and depth to your preference).

_Easter-Egg: You can skip the inputs and simply generate the graph right away!_

Once the graph is loaded, you're welcome to click on graph'ed nodes, and explore the space further.

### Analytics

Analytics of the graph is generated live as the graph adapts. Review the analytics, and consider reporting anomalies to chess.com!

More in-depth approaches can be found in `notebooks`.
