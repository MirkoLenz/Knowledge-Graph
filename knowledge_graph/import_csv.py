import click
import subprocess
from shlex import split
from pathlib import Path
import typing as t


"""
NULL values in CSVs: https://github.com/neo4j/neo4j/issues/2521
"""


def import_statement(key: str, files: t.Iterable[str]) -> t.List[str]:
    stmt = []
    for file in files:
        stmt.append(f"--{key}")
        stmt.append(f"import/{file}")

    return stmt


@click.command("import")
@click.option("--nodes", multiple=True, default=["conceptnet-nodes.csv"])
@click.option(
    "--relationships", multiple=True, default=["conceptnet-relationships.csv"]
)
def main(nodes, relationships):
    node_imports = import_statement("nodes", nodes)
    relationship_imports = import_statement("relationships", relationships)

    subprocess.run(split("sudo docker-compose stop neo4j"))
    subprocess.run(split("sudo rm -rf data/neo4j"))
    subprocess.run(split("sudo mkdir data/neo4j"))
    subprocess.run(
        ["docker-compose", "run", "neo4j", "--rm", "bin/neo4j-admin", "import",]
        + node_imports
        + relationship_imports
    )
    subprocess.run(split("docker-compose start neo4j"))


if __name__ == "__main__":
    main()
