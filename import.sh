#!/usr/bin/env bash

docker-compose stop neo4j
rm -rf data/neo4j/data
mkdir data/neo4j/data
docker-compose run --rm neo4j bin/neo4j-admin import --nodes "import/conceptnet-nodes.csv" --relationships "import/conceptnet-relationships.csv"
docker-compose start neo4j

# DEBUG
# docker-compose run --rm neo4j bash
