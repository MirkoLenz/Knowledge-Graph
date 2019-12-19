import click
import subprocess
from shlex import split
from pathlib import Path


"""
NULL values in CSVs: https://github.com/neo4j/neo4j/issues/2521
"""


@click.command()
@click.argument("import_dir", default="/data/knowledge-graph/neo4j/import")
@click.argument(
    "database_path", default="/data/knowledge-graph/neo4j/data/databases/graph.db"
)
def run(import_dir, database_path):
    database_path = Path(database_path)
    import_dir = Path(import_dir)
    nodes_path = import_dir / "nodes.csv"
    relationships_path = import_dir / "relationships.csv"

    subprocess.run(split(f"sudo service neo4j stop"))
    subprocess.run(split(f"sudo rm -rf {database_path}"))
    subprocess.run(
        split(
            f"neo4j-admin import --database '{database_path}' --nodes '{nodes_path}' --relationships '{relationships_path}'"
        )
    )
    subprocess.run(split(f"sudo chown -R neo4j.neo4j {database_path}"))
    subprocess.run(split(f"sudo service neo4j start"))


if __name__ == "__main__":
    run()
