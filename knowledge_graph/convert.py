"""
ConceptNet CSV Dump: https://github.com/commonsense/conceptnet5/wiki/Downloads
Source Code: https://github.com/tomkdickinson/conceptnet_neo4j
Import to Neo4j: https://neo4j.com/docs/operations-manual/current/tutorial/import-tool/

NOTE: Currently, URI is exported too which results in duplicate property entries.
If the terms without the prefix and suffix are unique, one could remove the uri and replace it with the name.

>>> neo4j-admin import --database="concept.db" --nodes "nodes.csv" --relationships "relationships.csv"
"""
import csv
from pathlib import Path
from neo4j import GraphDatabase
from dataclasses import dataclass, field
from typing import List, Dict
import gzip
import ast
import click


@dataclass(frozen=True)
class Node:
    uri: str
    name: str
    language: str


@dataclass(frozen=True)
class Source:
    contributor: str
    process: str


@dataclass(frozen=True)
class Relationship:
    uri: str
    start: Node
    end: Node
    rel_type: str
    dataset: str
    license: str
    weight: float
    # sources: List[Source]


@click.command()
@click.argument("conceptnet_csv", default="data/conceptnet-assertions-5.7.0.csv.gz")
@click.argument("nodes_csv", default="/var/lib/neo4j/import/nodes.csv")
@click.argument("relationships_csv", default="/var/lib/neo4j/import/relationships.csv")
# @click.option("break_after", default=0)
def run(conceptnet_csv: str, nodes_csv: str, relationships_csv: str) -> None:
    nodes = set()
    relationships = list()

    with gzip.open(conceptnet_csv, "rt") as f:
        rows = csv.reader(f, delimiter="\t")
        print(f"Reading {conceptnet_csv}")

        for i, row in enumerate(rows):
            rel_uri = row[1]
            start_uri = row[2]
            end_uri = row[3]
            metadata = ast.literal_eval(row[4])

            rel_prefix, rel_type = rel_uri.split("/")[1:3]
            start_prefix, start_lang, start_name = start_uri.split("/")[1:4]
            end_prefix, end_lang, end_name = end_uri.split("/")[1:4]

            if start_prefix == "c" and end_prefix == "c" and rel_prefix == "r":
                start_node = Node(uri=start_uri, name=start_name, language=start_lang)
                end_node = Node(uri=end_uri, name=end_name, language=end_lang)

                nodes.add(start_node)
                nodes.add(end_node)

                relationships.append(
                    Relationship(
                        uri=rel_uri,
                        start=start_node,
                        end=end_node,
                        rel_type=rel_type,
                        dataset=metadata.get("dataset", ""),
                        license=metadata.get("license", ""),
                        weight=float(metadata.get("weight", 1.0)),
                        # sources=[
                        #     Source(source.get("contributor", ""), source.get("process", ""))
                        #     for source in metadata["sources"]
                        # ],
                    )
                )

            # if break_after > 0 and i >= break_after:
            #     break

    with open(nodes_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {nodes_csv}")
        writer.writerow(["uri:ID", ":LABEL", "name", "language"])

        for n in nodes:
            writer.writerow((n.uri, "Concept", n.name, n.language))

    with open(relationships_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {relationships_csv}")
        writer.writerow(
            [
                ":START_ID",
                ":END_ID",
                ":TYPE",
                "uri",
                "dataset",
                "license",
                "weight:float",
            ]
        )

        for r in relationships:
            writer.writerow(
                (
                    r.start.uri,
                    r.end.uri,
                    r.rel_type,
                    r.uri,
                    r.dataset,
                    r.license,
                    r.weight,
                )
            )


if __name__ == "__main__":
    run()
