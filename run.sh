#!/usr/bin/env bash

export NEO4J_HOME=/data/knowledge-graph/neo4j
# docker run --name recap-neo4j -rm -it -v $NEO4J_HOME/data:/data -v $NEO4J_HOME/logs:/logs -v $NEO4J_HOME/import:/var/lib/neo4j/import neo4j -c /bin/bash
# neo4j-admin import --nodes "conceptnet-nodes.csv" --relationships "conceptnet-relationships.csv"
docker run --name recap-neo4j -rm -v $NEO4J_HOME/data:/data -v $NEO4J_HOME/logs:/logs -v $NEO4J_HOME/import:/var/lib/neo4j/import neo4j -c neo4j-admin import --nodes "conceptnet-nodes.csv" --relationships "conceptnet-relationships.csv"
docker run --name recap-neo4j -rm -p7474:7474 -p7687:7687 -d -v $NEO4J_HOME/data:/data -v $NEO4J_HOME/logs:/logs -v $NEO4J_HOME/import:/var/lib/neo4j/import -v $NEO4J_HOME/plugins:/plugins --env NEO4J_AUTH=none neo4j
