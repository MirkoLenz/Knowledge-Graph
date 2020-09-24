import ast
import csv
import gzip
import os
import subprocess
import sys
from dataclasses import dataclass, field
from os import chown
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

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

pos_replacements = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "s": "adjective",  # satellite
    "r": "adverb",
}

pos_default = "other"


@dataclass(frozen=True)
class Node:
    language: str
    name: str
    pos: Optional[str]

    @classmethod
    def from_uri(cls, uri: str) -> "Node":
        uri_parts = split_uri(uri)
        pos = pos_default

        if len(uri_parts) > 3:
            pos = pos_replacements.get(uri_parts[3], pos_default)

        return cls(uri_parts[1], uri_parts[2], pos)

    @property
    def uri(self):
        if self.pos:
            return concept_uri(self.language, self.name, self.pos)

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
@click.argument("neo4j_import_dir", default="data/neo4j/import/")
@click.argument("conceptnet_csv", default="data/conceptnet-assertions-5.7.0.csv.gz")
@click.argument("nodes_csv", default="conceptnet-nodes.csv")
@click.argument(
    "relationships_csv",
    default="conceptnet-relationships.csv",
)
@click.option("--debug", is_flag=True)
def main(
    neo4j_import_dir: str,
    conceptnet_csv: str,
    nodes_csv: str,
    relationships_csv: str,
    debug: bool,
) -> None:
    nodes_path = Path(neo4j_import_dir, nodes_csv)
    relationships_path = Path(neo4j_import_dir, relationships_csv)

    _check_access(neo4j_import_dir, os.W_OK)

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

            if debug and len(nodes) >= 10000:
                break

    with nodes_path.open("w") as f:
        writer = csv.writer(f)
        print(f"Writing {nodes_csv}")
        writer.writerow(("uri:ID", ":LABEL", "name", "language", "pos", "source"))

        for n in nodes:
            writer.writerow((n.uri, n.label, n.name, n.language, n.pos, n.source))

    with relationships_path.open("w") as f:
        writer = csv.writer(f)
        print(f"Writing {relationships_csv}")
        writer.writerow(
            (
                ":START_ID",
                ":END_ID",
                ":TYPE",
                "uri",
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
                    r.uri,
                    # r.dataset,
                    r.weight,
                    r.source,
                )
            )


def _check_access(dir: str, mode: int) -> None:
    if not os.access(dir, mode):
        chown_cmd = [
            "sudo",
            "chown",
            "-R",
            f"{os.getenv('USER')}.{os.getenv('USER')}",
            dir,
        ]

        click.echo(f"The target directory {dir} is not writable.")
        click.echo(f"Fix it by executing '{' '.join(chown_cmd)}'? [yn] ", nl=False)
        char = click.getchar()
        click.echo()

        if char == "y":
            subprocess.run(chown_cmd)
        else:
            click.echo("The target directory is not writable.")
            sys.exit()


if __name__ == "__main__":
    main()
