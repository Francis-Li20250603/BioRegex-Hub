import os
import csv
import json
import sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "bioregex_kg")

os.makedirs(OUTPUT_DIR, exist_ok=True)

NODES_FILE = os.path.join(OUTPUT_DIR, "nodes.csv")
EDGES_FILE = os.path.join(OUTPUT_DIR, "edges.csv")
GRAPH_FILE = os.path.join(OUTPUT_DIR, "graph.json")

print(f"[DEBUG] BASE_DIR = {BASE_DIR}")
print(f"[DEBUG] DATA_DIR = {DATA_DIR}")
print(f"[DEBUG] OUTPUT_DIR = {OUTPUT_DIR}")


def export_nodes_and_edges():
    nodes = []
    edges = []

    if not os.path.exists(DATA_DIR):
        print(f"[KG Export] ❌ Data directory not found: {DATA_DIR}")
        sys.exit(1)

    files = os.listdir(DATA_DIR)
    if not files:
        print(f"[KG Export] ❌ No files found in {DATA_DIR}")
        sys.exit(1)

    # === Always central node ===
    nodes.append({"id": "DataSource", "label": "Regulatory Data"})

    # === Dataset nodes ===
    for fname in files:
        dataset_id = fname.split(".")[0]
        nodes.append({"id": dataset_id, "label": fname})
        edges.append({"source": "DataSource", "target": dataset_id, "relation": "contains"})

        # === Special case: FDA drugs ===
        if dataset_id == "fda_drugs":
            fpath = os.path.join(DATA_DIR, fname)
            try:
                with open(fpath, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        drug_name = row.get("drug_name") or row.get("Drug Name") or None
                        manufacturer = row.get("manufacturer") or row.get("Manufacturer") or None
                        if not drug_name:
                            continue

                        drug_id = f"drug:{drug_name.strip().replace(' ', '_')}"
                        nodes.append({"id": drug_id, "label": drug_name.strip()})
                        edges.append({"source": dataset_id, "target": drug_id, "relation": "contains"})

                        if manufacturer:
                            m_id = f"org:{manufacturer.strip().replace(' ', '_')}"
                            nodes.append({"id": m_id, "label": manufacturer.strip()})
                            edges.append({"source": drug_id, "target": m_id, "relation": "produced_by"})
            except Exception as e:
                print(f"[KG Export] ⚠️ Failed parsing FDA dataset: {e}")

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
    export_nodes_and_edges()




