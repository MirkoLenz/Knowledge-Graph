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
def main():
    neo4j_url = "neo4j://" + os.getenv("NEO4J_URL")
    neo4j_auth = os.getenv("NEO4J_AUTH").split("/", 1)
    driver = GraphDatabase.driver(
        neo4j_url,
        auth=tuple(neo4j_auth),
        encrypted=False,
    )

    with driver.session() as session:
        session.run("CREATE INDEX FOR (n:Concept) ON (n.name)")
        session.run("CREATE INDEX FOR (n:Concept) ON (n.language)")
        session.run("CREATE INDEX FOR (n:Concept) ON (n.pos)")


if __name__ == "__main__":
    main()
