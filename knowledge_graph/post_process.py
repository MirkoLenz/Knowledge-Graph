"""
Delete all nodes and edges:
```
MATCH (n)
OPTIONAL MATCH (n)-[r]-()
DELETE n,r
```
"""

import click
from neo4j import GraphDatabase


@click.command("post-process")
@click.argument("neo4j_url", default="bolt://localhost:7687")
def main(neo4j_url: str):
    driver = GraphDatabase.driver(neo4j_url)  # auth=("username", "password")

    with driver.session() as session:
        session.run("CREATE INDEX FOR (n:Concept) ON (n.name)")
        session.run("CREATE INDEX FOR (n:Concept) ON (n.uri)")
        session.run("CREATE INDEX FOR (n:Concept) ON (n.language)")


if __name__ == "__main__":
    main()
