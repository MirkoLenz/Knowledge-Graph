from neo4j import GraphDatabase
import click


"""
Delete all nodes and edges:
```
MATCH (n)
OPTIONAL MATCH (n)-[r]-()
DELETE n,r
```
"""


# def create_relationship(tx, rel):
#     start = rel.start
#     end = rel.end

#     return tx.run(
#         f"CREATE p = (start:Concept $start_props) -[:{rel.rel_type} $rel_props]->(end:Concept $end_props)",
#         start_props=start.props,
#         end_props=end.props,
#         rel_props=rel.props,
#     )


@click.command()
@click.argument("neo4j_url", default="bolt://localhost:7687")
def run(neo4j_url):
    driver = GraphDatabase.driver(neo4j_url)  # auth=("username", "password")

    with driver.session() as session:
        session.run("CREATE CONSTRAINT ON (n:Concept) ASSERT n.uri IS UNIQUE")
        session.run("CREATE INDEX ON :Concept(name)")
        session.run("CREATE INDEX ON :Concept(language)")


if __name__ == "__main__":
    run()
