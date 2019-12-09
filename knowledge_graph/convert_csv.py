"""
ConceptNet CSV Dump: https://github.com/commonsense/conceptnet5/wiki/Downloads
Source Code: https://github.com/tomkdickinson/conceptnet_neo4j
Import to Neo4j: https://neo4j.com/docs/operations-manual/current/tutorial/import-tool/

>>> neo4j-admin import --database="concept.db" --nodes "nodes.csv" --relationships "relationships.csv"
"""
import csv
from pathlib import Path

# Path to ConceptNets extracted folder (which contains assertions)
conceptnet_location = Path("in/assertions.csv")
# Location for the output nodes.csv file
nodes_location = Path("out/nodes.csv")
# Location of the relationships.csv file
relationship_location = Path("out/relationships.csv")

nodes = set()
relationships = []

with conceptnet_location.open() as f:
    rows = csv.reader(f, delimiter="\t")
    print(f"Reading {conceptnet_location}")

    for i, row in enumerate(rows):
        rel = row[1]
        start = row[2]
        end = row[3]

        if start.startswith("/c/") and end.startswith("/c/") and rel.startswith("/r/"):
            dataset = row[4]["dataset"]
            license = row[4]["license"]
            weight = row[4]["weight"]
            contributor = row[4]["sources"][0]["contributor"]
            process = row[4]["sources"][0]["process"]

            nodes.add(start)
            nodes.add(end)
            relationships.append(
                [start, end, rel, dataset, license, weight, contributor, process]
            )

with nodes_location.open("w") as f:
    writer = csv.writer(f)
    print(f"Writing {nodes_location}")
    writer.writerow(["uri:ID", ":LABEL"])

    for n in nodes:
        writer.writerow([n, "Concept"])

with relationship_location.open("w") as f:
    writer = csv.writer(f)
    print(f"Writing {relationship_location}")
    writer.writerow(
        [
            ":START_ID",
            ":END_ID",
            ":TYPE",
            "dataset",
            "license",
            "weight",
            "contributor",
            "process",
        ]
    )

    for r in relationships:
        writer.writerow(r)
