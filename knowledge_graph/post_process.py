"""
Delete all nodes and edges:
```
MATCH (n)
OPTIONAL MATCH (n)-[r]-()
DELETE n,r
```
"""

import click
import os
from dotenv import load_dotenv

load_dotenv()
from neo4j import GraphDatabase


@click.command("post-process")
@click.argument("neo4j_url", default="bolt://localhost:7687")
def main(neo4j_url: str):
    neo4j_auth = os.getenv("NEO4J_AUTH").split("/", 1)
    driver = GraphDatabase.driver(neo4j_url, auth=neo4j_auth)

    with driver.session() as session:
        session.run("CREATE INDEX FOR (n:Concept) ON (n.name)")
        session.run("CREATE INDEX FOR (n:Concept) ON (n.uri)")
        session.run("CREATE INDEX FOR (n:Concept) ON (n.language)")


if __name__ == "__main__":
    main()
