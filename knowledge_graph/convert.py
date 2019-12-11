"""
ConceptNet CSV Dump: https://github.com/commonsense/conceptnet5/wiki/Downloads
Source Code: https://github.com/tomkdickinson/conceptnet_neo4j
Import to Neo4j: https://neo4j.com/docs/operations-manual/current/tutorial/import-tool/

NOTE: Currently, URI is exported too which results in duplicate property entries.
If the terms without the prefix and suffix are unique, one could remove the uri and replace it with the name.

TODO: Node de/n/n is duplicate
TODO: Loops on one node possible as lang, name, pos not unique in conceptnet

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
from . import uri


lang_filter = ["de", "en"]

# POS tags
# n: NOUN
# v: VERB
# a: ADJECTIVE
# s: ADJECTIVE SATELLITE
# r: ADVERB


@dataclass(frozen=True)
class Node:
    prefix: str
    language: str
    name: str
    pos: str

    @classmethod
    def create(cls, uri: str) -> "Node":
        uri = uri.split("/")

        return cls(uri[1], uri[2], uri[3], uri[4] if len(uri) > 4 else None)

    @property
    def key(self):
        return "/".join(filter(None, (self.language, self.name, self.pos)))

    @property
    def label(self):
        return "Concept"


@dataclass(frozen=True)
class Source:
    contributor: str
    process: str


@dataclass(frozen=True)
class Relationship:
    prefix: str
    name: str
    start: Node
    end: Node
    dataset: str
    license: str
    weight: float
    # sources: List[Source]

    @classmethod
    def create(cls, uri: str, metadata: str, start: Node, end: Node) -> "Relationship":
        uri = uri.split("/")
        metadata = ast.literal_eval(metadata)

        return cls(
            uri[1],
            uri[2],
            start,
            end,
            metadata.get("dataset"),
            metadata.get("license"),
            float(metadata.get("weight", 1.0)),
        )

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
    nodes = dict()
    relationships = set()

    with gzip.open(conceptnet_csv, "rt") as f:
        rows = csv.reader(f, delimiter="\t")
        print(f"Reading {conceptnet_csv}")

        for i, row in enumerate(rows):
            start = Node.create(row[2])
            end = Node.create(row[3])
            rel = Relationship.create(row[1], row[4], start, end)

            if (
                start.prefix == "c"
                and end.prefix == "c"
                and rel.prefix == "r"
                and start.language in lang_filter
                and end.language in lang_filter
            ):
                if start.key not in nodes:
                    nodes[start.key] = start

                if end.key not in nodes:
                    nodes[end.key] = end

                relationships.add(rel)

                if start.pos:
                    start_general = nodes.get(start.key) or Node(
                        start.prefix, start.language, start.name, None
                    )
                    rel_start_general = Relationship.create(
                        row[1], row[4], start_general, end
                    )

                    nodes[start_general.key] = start_general
                    relationships.add(rel_start_general)

                if end.pos:
                    end_general = nodes.get(end.key) or Node(
                        end.prefix, end.language, end.name, None
                    )
                    rel_end_general = Relationship.create(
                        row[1], row[4], start, end_general
                    )

                    nodes[end_general] = end_general
                    relationships.add(rel_end_general)

                if start.pos and end.pos:
                    relationships.add(
                        Relationship.create(row[1], row[4], start_general, end_general)
                    )

    with open(nodes_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {nodes_csv}")
        writer.writerow(["key:ID", ":LABEL", "name", "language", "pos"])

        for n in nodes.values():
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
