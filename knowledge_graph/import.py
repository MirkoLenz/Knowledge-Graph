import click
import subprocess


@click.command()
@click.argument("nodes", default="/var/lib/neo4j/import/nodes.csv")
@click.argument("relationships", default="/var/lib/neo4j/import/relationships.csv")
@click.argument("database", default="concept.db")
def run(nodes, relationships, database):
    subprocess.run(
        f"neo4j-admin import --database='{database}' --nodes '{nodes}' --relationships '{relationships}'"
    )


if __name__ == "__main__":
    run()
