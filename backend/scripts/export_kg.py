import os
import csv
import json
import sys

# === Directories ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "bioregex_kg")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Output files ===
NODES_FILE = os.path.join(OUTPUT_DIR, "nodes.csv")
EDGES_FILE = os.path.join(OUTPUT_DIR, "edges.csv")
GRAPH_FILE = os.path.join(OUTPUT_DIR, "graph.json")

print(f"[DEBUG] BASE_DIR = {BASE_DIR}")
print(f"[DEBUG] DATA_DIR = {DATA_DIR}")
print(f"[DEBUG] OUTPUT_DIR = {OUTPUT_DIR}")
print(f"[DEBUG] Files in DATA_DIR: {os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else '❌ Not found'}")


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

    # Build graph from filenames
    for fname in files:
        node_id = fname.split(".")[0]
        nodes.append({"id": node_id, "label": fname})
        edges.append({"source": "DataSource", "target": node_id, "relation": "contains"})

    # Always include central node
    nodes.append({"id": "DataSource", "label": "Regulatory Data"})

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



