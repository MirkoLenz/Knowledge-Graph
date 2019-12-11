"""
ConceptNet CSV Dump: https://github.com/commonsense/conceptnet5/wiki/Downloads
Source Code: https://github.com/tomkdickinson/conceptnet_neo4j
Import to Neo4j: https://neo4j.com/docs/operations-manual/current/tutorial/import-tool/

>>> neo4j-admin import --database "concept.db" --nodes "nodes.csv" --relationships "relationships.csv"
"""

import csv
from pathlib import Path
from neo4j import GraphDatabase
from dataclasses import dataclass, field
from typing import List, Dict
import gzip
import ast
import click
from .uri import split_uri, concept_uri, is_concept, is_relation


lang_filter = ["de", "en"]

# POS tags
# n: NOUN
# v: VERB
# a: ADJECTIVE
# s: ADJECTIVE SATELLITE
# r: ADVERB


@dataclass(frozen=True)
class Node:
    language: str
    name: str

    @classmethod
    def from_uri(cls, uri: str) -> "Node":
        uri = split_uri(uri)

        return cls(uri[1], uri[2])

    @property
    def key(self):
        return concept_uri(self.language, self.name)

    @property
    def label(self):
        return "Conceptnet"


@dataclass(frozen=True)
class Relationship:
    name: str
    start: Node
    end: Node
    dataset: str
    license: str
    weight: float

    @classmethod
    def from_uri(
        cls, uri: str, metadata: str, start: Node, end: Node
    ) -> "Relationship":
        uri = split_uri(uri)
        metadata = ast.literal_eval(metadata)

        return cls(
            uri[1],
            start,
            end,
            metadata.get("dataset"),
            metadata.get("license"),
            float(metadata.get("weight", 1.0)),
        )


@click.command()
@click.argument("conceptnet_csv", default="data/conceptnet-assertions-5.7.0.csv.gz")
@click.argument("nodes_csv", default="/var/lib/neo4j/import/nodes.csv")
@click.argument("relationships_csv", default="/var/lib/neo4j/import/relationships.csv")
# @click.option("break_after", default=0)
def run(conceptnet_csv: str, nodes_csv: str, relationships_csv: str) -> None:
    nodes = set()
    relationships = set()

    with gzip.open(conceptnet_csv, "rt") as f:
        rows = csv.reader(f, delimiter="\t")
        print(f"Reading {conceptnet_csv}")

        for i, row in enumerate(rows):
            rel_uri = row[1]
            start_uri = row[2]
            end_uri = row[3]

            if is_concept(start_uri) and is_concept(end_uri) and is_relation(rel_uri):
                start = Node.from_uri(start_uri)
                end = Node.from_uri(end_uri)

                if (
                    start.language in lang_filter
                    and end.language in lang_filter
                    and start != end
                ):
                    relationship = Relationship.from_uri(rel_uri, row[4], start, end)
                    nodes.add(start)
                    nodes.add(end)
                    relationships.add(relationship)

    with open(nodes_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {nodes_csv}")
        writer.writerow(["key:ID", ":LABEL", "name", "language"])

        for n in nodes.values():
            writer.writerow((n.key, n.label, n.name, n.language))

    with open(relationships_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {relationships_csv}")
        writer.writerow(
            [":START_ID", ":END_ID", ":TYPE", "dataset", "license", "weight:float",]
        )

        for r in relationships:
            writer.writerow(
                (r.start.key, r.end.key, r.name, r.dataset, r.license, r.weight)
            )


if __name__ == "__main__":
    run()
