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
    """
    Create a simple regex that matches any of the given values.
    Used for demo purposes (in production, more advanced NLP/regex generation needed).
    """
    cleaned = [re.escape(v.strip()) for v in values if v and len(v.strip()) > 1]
    if not cleaned:
        return None
    sample = cleaned[:max_samples]
    return r"\b(" + "|".join(sample) + r")\b"


def export_knowledge_graph():
    nodes = []
    edges = []

    # === Core node types ===
    nodes.append({"id": "DataSource", "label": "Regulatory Data"})

    # === Regex rule index ===
    rule_counter = 1

    # === FDA dataset: drug names ===
    fda_file = os.path.join(DATA_DIR, "fda_drugs.csv")
    if os.path.exists(fda_file):
        with open(fda_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            drug_names = [row.get("drug_name") or row.get("Drug Name") for row in reader if row.get("drug_name") or row.get("Drug Name")]
            regex_pattern = build_regex_from_values(drug_names)
            if regex_pattern:
                rule_id = f"rule:{rule_counter}"
                rule_counter += 1
                nodes.append({"id": rule_id, "label": "Drug Name Rule"})
                nodes.append({"id": "dtype:drug_name", "label": "Drug Name"})
                nodes.append({"id": "region:FDA", "label": "FDA"})
                nodes.append({"id": f"regex:{rule_id}", "label": regex_pattern})

                edges.append({"source": rule_id, "target": "dtype:drug_name", "relation": "TYPED_AS"})
                edges.append({"source": rule_id, "target": "region:FDA", "relation": "BELONGS_TO"})
                edges.append({"source": rule_id, "target": f"regex:{rule_id}", "relation": "USES_REGEX"})

    # === HIPAA dataset: breach types ===
    hipaa_file = os.path.join(DATA_DIR, "hipaa_breaches.csv")
    if os.path.exists(hipaa_file):
        with open(hipaa_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            breach_types = [row.get("breach_type") or row.get("Type") for row in reader if row.get("breach_type") or row.get("Type")]
            regex_pattern = build_regex_from_values(breach_types)
            if regex_pattern:
                rule_id = f"rule:{rule_counter}"
                rule_counter += 1
                nodes.append({"id": rule_id, "label": "Breach Type Rule"})
                nodes.append({"id": "dtype:breach_type", "label": "Breach Type"})
                nodes.append({"id": "region:HIPAA", "label": "HIPAA"})
                nodes.append({"id": f"regex:{rule_id}", "label": regex_pattern})

                edges.append({"source": rule_id, "target": "dtype:breach_type", "relation": "TYPED_AS"})
                edges.append({"source": rule_id, "target": "region:HIPAA", "relation": "BELONGS_TO"})
                edges.append({"source": rule_id, "target": f"regex:{rule_id}", "relation": "USES_REGEX"})

    # === CMS dataset: hospital names ===
    cms_file = os.path.join(DATA_DIR, "cms_hospitals.csv")
    if os.path.exists(cms_file):
        with open(cms_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            hospital_names = [row.get("hospital_name") or row.get("Hospital Name") for row in reader if row.get("hospital_name") or row.get("Hospital Name")]
            regex_pattern = build_regex_from_values(hospital_names)
            if regex_pattern:
                rule_id = f"rule:{rule_counter}"
                rule_counter += 1
                nodes.append({"id": rule_id, "label": "Hospital Name Rule"})
                nodes.append({"id": "dtype:hospital_name", "label": "Hospital Name"})
                nodes.append({"id": "region:CMS", "label": "CMS"})
                nodes.append({"id": f"regex:{rule_id}", "label": regex_pattern})

                edges.append({"source": rule_id, "target": "dtype:hospital_name", "relation": "TYPED_AS"})
                edges.append({"source": rule_id, "target": "region:CMS", "relation": "BELONGS_TO"})
                edges.append({"source": rule_id, "target": f"regex:{rule_id}", "relation": "USES_REGEX"})

    # === Deduplicate nodes ===
    unique_nodes = {n["id"]: n for n in nodes}
    nodes = list(unique_nodes.values())

    # === Write CSVs ===
    with open(NODES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "label"])
        writer.writeheader()
        writer.writerows(nodes)

    with open(EDGES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "relation"])
        writer.writeheader()
        writer.writerows(edges)

    # === Write JSON ===
    graph = {"nodes": nodes, "edges": edges}
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"[KG Export] ✅ Wrote {len(nodes)} nodes and {len(edges)} edges")
    print(f"[KG Export] ✅ Files saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    export_knowledge_graph()





