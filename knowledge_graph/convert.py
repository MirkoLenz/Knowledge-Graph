"""
ConceptNet CSV Dump: https://github.com/commonsense/conceptnet5/wiki/Downloads
Source Code: https://github.com/tomkdickinson/conceptnet_neo4j
Import to Neo4j: https://neo4j.com/docs/operations-manual/current/tutorial/import-tool/

NOTE: Currently, URI is exported too which results in duplicate property entries.
If the terms without the prefix and suffix are unique, one could remove the uri and replace it with the name.

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


lang_filter = ["de", "en"]

# POS tags
# n: NOUN
# v: VERB
# a: ADJECTIVE
# s: ADJECTIVE SATELLITE
# r: ADVERB


@dataclass(unsafe_hash=True)
class Node:
    prefix: str
    name: str
    language: str
    pos: str

    def __init__(self, uri: str):
        uri = uri.split("/")

        self.prefix = uri[1]
        self.language = uri[2]
        self.name = uri[3]
        self.pos = uri[4] if len(uri) > 4 else None

    @property
    def key(self):
        return "/".join([self.language, self.name, self.pos])

    @property
    def label(self):
        return "Concept"


@dataclass(unsafe_hash=True)
class Source:
    contributor: str
    process: str


@dataclass(unsafe_hash=True)
class Relationship:
    prefix: str
    start: Node
    end: Node
    name: str
    dataset: str
    license: str
    weight: float
    # sources: List[Source]

    def __init__(self, uri: str, metadata: str, start: Node, end: Node) -> None:
        uri = uri.split("/")

        self.prefix = uri[1]
        self.name = uri[2]
        self.start = start
        self.end = end

        metadata = ast.literal_eval(metadata)
        self.dataset = metadata.get("dataset")
        self.license = metadata.get("license")
        self.weight = float(metadata.get("weight", 1.0))

        # self.sources=[
        #     Source(source.get("contributor", ""), source.get("process", ""))
        #     for source in metadata["sources"]
        # ],


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
            start = Node(row[2])
            end = Node(row[3])
            rel = Relationship(row[1], row[4], start, end)

            if (
                start.prefix == "c"
                and end.prefix == "c"
                and rel.prefix == "r"
                and start.language in lang_filter
                and end.language in lang_filter
            ):
                nodes.add(start)
                nodes.add(end)
                relationships.append(rel)

    with open(nodes_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {nodes_csv}")
        writer.writerow([":ID", ":LABEL", "name", "language", "pos"])

        for n in nodes:
            writer.writerow((n.key, n.label, n.name, n.language, n.pos))

    with open(relationships_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {relationships_csv}")
        writer.writerow(
            [":START_ID", ":END_ID", ":TYPE", "dataset", "license", "weight:float",]
        )

        for r in relationships:
            writer.writerow(
                (r.start.key, r.end.key, r.name, r.dataset, r.license, r.weight,)
            )


if __name__ == "__main__":
    run()
