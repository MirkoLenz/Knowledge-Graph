#!/usr/bin/env bash

export NEO4J_HOME=/data/knowledge-graph/neo4j
sudo docker run --name recap-neo4j --rm -v $NEO4J_HOME/data:/data -v $NEO4J_HOME/logs:/logs -v $NEO4J_HOME/import:/import neo4j bin/neo4j-admin import --nodes "import/conceptnet-nodes.csv" --relationships "import/conceptnet-relationships.csv"
sudo docker run --name recap-neo4j --rm -p7474:7474 -p7687:7687 -d -v $NEO4J_HOME/data:/data -v $NEO4J_HOME/logs:/logs -v $NEO4J_HOME/import:/import -v $NEO4J_HOME/plugins:/plugins --env NEO4J_AUTH=none --env NEO4J_dbms_connector_bolt_advertised__address=136.199.130.136:7687 neo4j
