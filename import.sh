#!/usr/bin/env bash

export NEO4J_ROOT=/data/knowledge-graph/neo4j
export NEO4J_HOME=/var/lib/neo4j

docker stop recap-neo4j
rm -rf $NEO4J_ROOT/data/databases
docker run --name recap-neo4j --rm -v $NEO4J_ROOT/data:/data -v $NEO4J_ROOT/logs:/logs -v $NEO4J_ROOT/import:$NEO4J_HOME/import neo4j bin/neo4j-admin import --nodes "import/conceptnet-nodes.csv" --relationships "import/conceptnet-relationships.csv"
docker run --name recap-neo4j --rm -p 7474:7474 -p 7687:7687 -d -v $NEO4J_ROOT/data:/data -v $NEO4J_ROOT/logs:/logs -v $NEO4J_ROOT/import:$NEO4J_HOME/import -v $NEO4J_ROOT/plugins:/plugins --env NEO4J_AUTH=none --env NEO4J_dbms_connector_bolt_advertised__address=136.199.130.136:7687 neo4j

# DEBUG
# docker run --name recap-neo4j --rm -it -v $NEO4J_ROOT/data:/data -v $NEO4J_ROOT/logs:/logs -v $NEO4J_ROOT/import:$NEO4J_HOME/import -v $NEO4J_ROOT/plugins:/plugins neo4j bash
