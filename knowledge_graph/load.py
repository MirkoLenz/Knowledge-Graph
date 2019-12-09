from neo4j import GraphDatabase
from pathlib import Path
import csv
from dataclasses import dataclass, field
from typing import List, Dict
import gzip
import ast


@dataclass
class Node:
    name: str
    language: str

    @property
    def props(self) -> str:
        return {
            "name": self.name,
            "language": self.language,
        }


@dataclass
class Relationship:
    start: Node
    end: Node
    rel_type: str
    dataset: str
    license: str
    weight: float
    sources: List[Dict[str, str]]

    @property
    def props(self) -> str:
        return {
            "dataset": self.dataset,
            "license": self.license,
            "weight": self.weight,
            # "sources": self.sources,
        }


path = Path("data/conceptnet-assertions-5.7.0.csv.gz")
relationships = []

with gzip.open(path, "rt") as f:
    rows = csv.reader(f, delimiter="\t")

    for row in rows:
        rel = row[1]
        start = row[2]
        end = row[3]
        metadata = ast.literal_eval(row[4])

        rel_prefix, rel_type = rel.split("/")[1:3]
        start_prefix, start_lang, start_name = start.split("/")[1:4]
        end_prefix, end_lang, end_name = end.split("/")[1:4]

        if start_prefix == "c" and end_prefix == "c" and rel_prefix == "r":
            relationships.append(
                Relationship(
                    start=Node(name=start_name, language=start_lang),
                    end=Node(name=end_name, language=end_lang),
                    rel_type=rel_type,
                    dataset=metadata["dataset"],
                    license=metadata["license"],
                    weight=float(metadata["weight"]),
                    sources=metadata["sources"],
                )
            )

        break


def create_relationship(tx, rel):
    start = rel.start
    end = rel.end

    return tx.run(
        f"CREATE p = (start:Concept $start_props) -[:{rel.rel_type} $rel_props]->(end:Concept $end_props)",
        start_props=start.props,
        end_props=end.props,
        rel_props=rel.props,
    )


# uri = "bolt://localhost:7687"
uri = "bolt://136.199.130.136:7687"
driver = GraphDatabase.driver(uri)  # auth=("username", "password")

with driver.session() as session:
    for relationship in relationships:
        session.write_transaction(create_relationship, relationship)
