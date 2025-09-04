import os
import csv
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "bioregex_kg")

os.makedirs(OUTPUT_DIR, exist_ok=True)

NODES_FILE = os.path.join(OUTPUT_DIR, "nodes.csv")
EDGES_FILE = os.path.join(OUTPUT_DIR, "edges.csv")
GRAPH_FILE = os.path.join(OUTPUT_DIR, "graph.json")


def build_regex_from_values(values, max_samples=20):
    """Make a regex from sample values."""
    cleaned = [re.escape(v.strip()) for v in values if v and len(v.strip()) > 2]
    if not cleaned:
        return None
    return r"\b(" + "|".join(cleaned[:max_samples]) + r")\b"


def read_csv_column(file_path, possible_columns):
    """Try to extract values from one of the possible column names."""
    if not os.path.exists(file_path):
        return []

    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        headers = [h.lower() for h in reader.fieldnames]

        # Find matching column
        match = None
        for candidate in possible_columns:
            if candidate.lower() in headers:
                match = candidate
                break

        if not match:
            print(f"[WARN] {file_path}: No matching column found in {headers}")
            return []

        return [row.get(match, "").strip() for row in reader if row.get(match)]


def export_knowledge_graph():
    nodes, edges = [], []
    nodes.append({"id": "DataSource", "label": "Regulatory Data"})

    rule_counter = 1

    # === FDA ===
    fda_values = read_csv_column(
        os.path.join(DATA_DIR, "fda_drugs.csv"),
        ["drug_name", "Drug Name", "Product Name"]
    )
    if fda_values:
        regex = build_regex_from_values(fda_values)
        if regex:
            rule_id = f"rule:{rule_counter}"; rule_counter += 1
            nodes += [
                {"id": rule_id, "label": "Drug Name Rule"},
                {"id": "dtype:drug_name", "label": "Drug Name"},
                {"id": "region:FDA", "label": "FDA"},
                {"id": f"regex:{rule_id}", "label": regex}
            ]
            edges += [
                {"source": rule_id, "target": "dtype:drug_name", "relation": "TYPED_AS"},
                {"source": rule_id, "target": "region:FDA", "relation": "BELONGS_TO"},
                {"source": rule_id, "target": f"regex:{rule_id}", "relation": "USES_REGEX"}
            ]

    # === HIPAA ===
    hipaa_values = read_csv_column(
        os.path.join(DATA_DIR, "hipaa_breaches.csv"),
        ["breach_type", "Type of Breach", "Type"]
    )
    if hipaa_values:
        regex = build_regex_from_values(hipaa_values)
        if regex:
            rule_id = f"rule:{rule_counter}"; rule_counter += 1
            nodes += [
                {"id": rule_id, "label": "HIPAA Breach Rule"},
                {"id": "dtype:breach_type", "label": "Breach Type"},
                {"id": "region:HIPAA", "label": "HIPAA"},
                {"id": f"regex:{rule_id}", "label": regex}
            ]
            edges += [
                {"source": rule_id, "target": "dtype:breach_type", "relation": "TYPED_AS"},
                {"source": rule_id, "target": "region:HIPAA", "relation": "BELONGS_TO"},
                {"source": rule_id, "target": f"regex:{rule_id}", "relation": "USES_REGEX"}
            ]

    # === CMS ===
    cms_values = read_csv_column(
        os.path.join(DATA_DIR, "cms_hospitals.csv"),
        ["hospital_name", "Facility Name", "Hospital Name"]
    )
    if cms_values:
        regex = build_regex_from_values(cms_values)
        if regex:
            rule_id = f"rule:{rule_counter}"; rule_counter += 1
            nodes += [
                {"id": rule_id, "label": "Hospital Rule"},
                {"id": "dtype:hospital_name", "label": "Hospital Name"},
                {"id": "region:CMS", "label": "CMS"},
                {"id": f"regex:{rule_id}", "label": regex}
            ]
            edges += [
                {"source": rule_id, "target": "dtype:hospital_name", "relation": "TYPED_AS"},
                {"source": rule_id, "target": "region:CMS", "relation": "BELONGS_TO"},
                {"source": rule_id, "target": f"regex:{rule_id}", "relation": "USES_REGEX"}
            ]

    # === Deduplicate ===
    nodes = list({n["id"]: n for n in nodes}.values())

    # Write files
    with open(NODES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "label"])
        writer.writeheader(); writer.writerows(nodes)

    with open(EDGES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "relation"])
        writer.writeheader(); writer.writerows(edges)

    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

    print(f"[KG Export] ✅ {len(nodes)} nodes, {len(edges)} edges")


if __name__ == "__main__":
    export_knowledge_graph()

