# ReCAP Knowledge Graph

The idea of importing the CSV dump is based on a script by [Tom Dickinson](https://github.com/tomkdickinson/conceptnet_neo4j).

## Requirements

-   Docker and docker-compose.
-   Poetry package manager.
-   Python 3.7 or higher (e.g., using pyenv).

## Setup

-   Create the folder `data` with the subfolders `neo4j` and `postgres`.
-   Download the [ConceptNet assertions](https://github.com/commonsense/conceptnet5/wiki/Downloads) and save to `./data`.
-   Copy `env-example` to `.env` and adjust to your preferences.
-   Run `poetry install` to create the virtual environment and install the dependencies.
-   Run `poetry run python -m knowledge_graph convert` to transform the assertions into a format that Neo4j can understand.
-   Run `poetry run python -m knowledge_graph import` to import the nodes and relationships into Neo4j.
-   Run `poetry run python -m knowledge_graph post-process` to create indices for the most important attributes.
-   Run `docker-compose up` to start the services.
