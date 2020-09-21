import ast
import csv
import gzip
from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Any, Dict, List, Mapping

import click

from .uri import (
    assertion_uri,
    concept_uri,
    is_concept,
    is_relation,
    join_uri,
    split_uri,
)

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
    def uri(self):
        return concept_uri(self.language, self.name)

    @property
    def label(self):
        return "Concept"

    @property
    def source(self):
        return "conceptnet"


@dataclass(frozen=True)
class Relationship:
    category: str
    start: Node
    end: Node
    weight: float

    @classmethod
    def from_uri(
        cls, uri: str, start: Node, end: Node, weight: float
    ) -> "Relationship":
        return cls(
            uri[3 : len(uri)],
            start,
            end,
            weight,
        )

    @property
    def uri(self) -> str:
        rel_uri = join_uri("r", self.category)
        return assertion_uri(rel_uri, self.start.uri, self.end.uri)

    @property
    def source(self):
        return "conceptnet"


@click.command("convert")
@click.argument("conceptnet_csv", default="data/conceptnet-assertions-5.7.0.csv.gz")
@click.argument("nodes_csv", default="data/neo4j/import/conceptnet-nodes.csv")
@click.argument(
    "relationships_csv",
    default="data/neo4j/import/conceptnet-relationships.csv",
)
@click.option("--debug", is_flag=True)
def main(
    conceptnet_csv: str, nodes_csv: str, relationships_csv: str, debug: bool
) -> None:
    if not os.access(nodes_csv, os.W_OK) and not os.access(relationships_csv, os.W_OK):
        raise RuntimeError("The target directory is not writable.")

    nodes = set()
    relationships: Dict[str, Relationship] = {}

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
                    nodes.add(start)
                    nodes.add(end)

                    rel_metadata: Mapping[str, str] = ast.literal_eval(row[4])
                    weight = float(rel_metadata.get("weight", 1.0))
                    rel = Relationship.from_uri(rel_uri, start, end, weight)

                    # Relationships can occur more then once,
                    # if two different datasets yield in the same relationsip.
                    # We are going to merge them in the following.
                    if rel.uri in relationships.keys():
                        merged_weight = relationships[rel.uri].weight + rel.weight
                        rel = Relationship.from_uri(rel_uri, start, end, merged_weight)

                    relationships[rel.uri] = rel

            if debug and len(nodes) >= 1000:
                break

    with open(nodes_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {nodes_csv}")
        writer.writerow((":ID", ":LABEL", "name", "language", "source"))

        for n in nodes:
            writer.writerow((n.uri, n.label, n.name, n.language, n.source))

    with open(relationships_csv, "w") as f:
        writer = csv.writer(f)
        print(f"Writing {relationships_csv}")
        writer.writerow(
            (
                ":START_ID",
                ":END_ID",
                ":TYPE",
                # "uri",
                # "dataset",
                "weight:float",
                "source",
            )
        )

        for r in relationships.values():
            writer.writerow(
                (
                    r.start.uri,
                    r.end.uri,
                    r.category,
                    # r.uri,
                    # r.dataset,
                    r.weight,
                    r.source,
                )
            )


if __name__ == "__main__":
    main()
