import os
import csv
import json

# === Ensure output directory exists ===
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "bioregex_kg")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === Output file paths ===
NODES_FILE = os.path.join(OUTPUT_DIR, "nodes.csv")
EDGES_FILE = os.path.join(OUTPUT_DIR, "edges.csv")
GRAPH_FILE = os.path.join(OUTPUT_DIR, "graph.json")


def export_nodes_and_edges():
    """
    Example export function:
    Reads from backend/data/* and builds a simple knowledge graph.
    """
    nodes = []
    edges = []

    # Collect nodes from all available datasets
    if os.path.exists(DATA_DIR):
        for fname in os.listdir(DATA_DIR):
            fpath = os.path.join(DATA_DIR, fname)
            node_id = fname.split(".")[0]

            nodes.append({"id": node_id, "label": fname})

            # Example: link dataset node to a central "DataSource"
            edges.append({"source": "DataSource", "target": node_id, "relation": "contains"})

    else:
        print(f"[KG Export] ⚠️ Data directory not found: {DATA_DIR}")

    # Add central node
    if nodes:
        nodes.append({"id": "DataSource", "label": "Regulatory Data"})

    # === Write CSV files ===
    with open(NODES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "label"])
        writer.writeheader()
        writer.writerows(nodes)

    with open(EDGES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "relation"])
        writer.writeheader()
        writer.writerows(edges)

    # === Write JSON file ===
    graph = {"nodes": nodes, "edges": edges}
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"[KG Export] ✅ Nodes written to {NODES_FILE}")
    print(f"[KG Export] ✅ Edges written to {EDGES_FILE}")
    print(f"[KG Export] ✅ Graph written to {GRAPH_FILE}")


if __name__ == "__main__":
    export_nodes_and_edges()


