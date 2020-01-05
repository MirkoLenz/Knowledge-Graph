# ReCAP Knowledge Graph

The idea of importing the CSV dump is based on a script by [Tom Dickinson](https://github.com/tomkdickinson/conceptnet_neo4j).

## Requirements

- Docker and docker-compose.
- Poetry package manager.
- Python 3.7 or higher (e.g. using pyenv).

## Setup

- Download [ConceptNet](https://github.com/commonsense/conceptnet5/wiki/Downloads) and save it to `./data`
- Copy `env-example` to `.env` and adjust to your preferences.
- Run `docker-compose up` to start the services.
