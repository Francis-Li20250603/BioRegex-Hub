# backend/scripts/export_kg.py
"""
Export the current BioRegex Hub database content into a knowledge graph format.

Outputs:
  - bioregex_kg/graph.json  (nodes + edges in JSON)
  - bioregex_kg/nodes.csv   (tabular node list)
  - bioregex_kg/edges.csv   (tabular edge list)
"""

import os
import json
import csv
from sqlmodel import Session, select
from app.database import get_engine
from app.models import Rule

OUT_DIR = os.environ.get("KG_OUT_DIR", "bioregex_kg")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    engine = get_engine()
    with Session(engine) as session:
        rules = session.exec(select(Rule)).all()

    nodes, edges = [], []
    seen_regions, seen_dtypes = set(), set()

    for rule in rules:
        rid = f"rule:{rule.id}"
        nodes.append({
            "id": rid,
            "label": "Rule",
            "pattern": rule.pattern,
            "region": rule.region,
            "data_type": rule.data_type,
        })

        reg_id = f"region:{rule.region}"
        if rule.region not in seen_regions:
            nodes.append({
                "id": reg_id,
                "label": "Region",
                "name": rule.region
            })
            seen_regions.add(rule.region)
        edges.append({
            "source": rid,
            "target": reg_id,
            "type": "BELONGS_TO"
        })

        dt_id = f"dtype:{rule.data_type}"
        if rule.data_type not in seen_dtypes:
            nodes.append({
                "id": dt_id,
                "label": "DataType",
                "name": rule.data_type
            })
            seen_dtypes.add(rule.data_type)
        edges.append({
            "source": rid,
            "target": dt_id,
            "type": "TYPED_AS"
        })

    # JSON export
    with open(os.path.join(OUT_DIR, "graph.json"), "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=2)

    # CSV export
    with open(os.path.join(OUT_DIR, "nodes.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "label", "pattern", "region", "data_type", "name"])
        writer.writeheader()
        for n in nodes:
            writer.writerow({k: n.get(k, "") for k in writer.fieldnames})

    with open(os.path.join(OUT_DIR, "edges.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "type"])
        writer.writeheader()
        for e in edges:
            writer.writerow(e)

    print(f"Knowledge graph exported to {OUT_DIR}/")

if __name__ == "__main__":
    main()
