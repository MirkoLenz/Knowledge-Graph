import subprocess
import typing as t
from pathlib import Path

import click


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

    subprocess.run(["sudo", "docker-compose", "stop", "neo4j"])
    subprocess.run(["sudo", "rm", "-rf", "data/neo4j/data"])
    subprocess.run(["sudo", "mkdir", "data/neo4j/data"])
    subprocess.run(
        [
            "sudo",
            "docker-compose",
            "run",
            "--rm",
            "neo4j",
            "bin/neo4j-admin",
            "import",
        ]
        + node_imports
        + relationship_imports
    )
    subprocess.run(["sudo", "docker-compose", "start", "neo4j"])


if __name__ == "__main__":
    main()
