# Contributing

The following provides a detailed explanation on how to contribute to this project.

## Setup

This project leverages [poetry](http://python-poetry.org) as its package & environment management.  
To get started, simply run `poetry install --with dev` to setup and install the necessary dependencies.

For further information on installing & using poetry, visit [poetry](http://python-poetry.org).

## Test

This project leverages various tests, formatters, linters, and more. To facilitate the execution of these tests, the following makefile target was made: `make tests`

Execute `make tests` to ensure the project was cloned successfully, and leverage it often to test contributions.

## Serve

This project leverages Plotly Dash to serve a web app.

Execute `make serve` to start running a local server of the app for testing.

## Deploy

This project is deployed on GCP. Once `gcloud` is installed locally, execute `make deploy` to deploy the app on GCP.
