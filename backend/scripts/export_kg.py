import os
import csv
import json
import pandas as pd

# --- Directories ---
REPO_ROOT = os.path.dirname(os.path.dirname(__file__))  # repo root
DATA_DIR = os.path.join(REPO_ROOT, "backend", "data")
OUT_DIR = os.path.join(REPO_ROOT, "backend", "bioregex_kg")
os.makedirs(OUT_DIR, exist_ok=True)

# --- Files ---
FDA_FILE = os.path.join(DATA_DIR, "fda_drugs.csv")
EMA_FILE = os.path.join(DATA_DIR, "ema_human_medicines.xlsx")
CMS_FILE = os.path.join(DATA_DIR, "cms_hospitals.csv")
HIPAA_FILE = os.path.join(DATA_DIR, "hipaa_breaches.csv")

# --- Output ---
NODES_FILE = os.path.join(OUT_DIR, "nodes.csv")
EDGES_FILE = os.path.join(OUT_DIR, "edges.csv")
GRAPH_FILE = os.path.join(OUT_DIR, "graph.json")


def safe_regex(term: str) -> str:
    """Escape a term into a safe regex fragment."""
    return r"\b" + str(term).replace("(", r"\(").replace(")", r"\)") + r"\b"


def build_nodes_edges():
    nodes, edges = [], []

    # --- FDA ---
    if os.path.exists(FDA_FILE):
        df = pd.read_csv(FDA_FILE)
        if "brand_name" in df.columns:
            for i, name in enumerate(df["brand_name"].dropna().unique()[:200]):  # cap 200
                node_id = f"fda_rule:{i+1}"
                regex_id = f"regex:fda_rule:{i+1}"
                nodes.extend([
                    {"id": node_id, "label": f"FDA Drug Rule {i+1}"},
                    {"id": regex_id, "label": safe_regex(name)},
                    {"id": "region:FDA", "label": "FDA"},
                ])
                edges.extend([
                    {"source": "DataSource", "target": node_id, "relation": "contains"},
                    {"source": node_id, "target": regex_id, "relation": "uses"},
                    {"source": node_id, "target": "region:FDA", "relation": "applies_to"},
                ])
    else:
        print("[WARN] FDA file missing")

    # --- EMA ---
    if os.path.exists(EMA_FILE):
        df = pd.read_excel(EMA_FILE)
        col = None
        for candidate in ["name", "Medicine Name", "INN"]:  # guess column
            if candidate in df.columns:
                col = candidate
                break
        if col:
            for i, name in enumerate(df[col].dropna().unique()[:200]):
                node_id = f"ema_rule:{i+1}"
                regex_id = f"regex:ema_rule:{i+1}"
                nodes.extend([
                    {"id": node_id, "label": f"EMA Medicine Rule {i+1}"},
                    {"id": regex_id, "label": safe_regex(name)},
                    {"id": "region:EMA", "label": "EMA"},
                ])
                edges.extend([
                    {"source": "DataSource", "target": node_id, "relation": "contains"},
                    {"source": node_id, "target": regex_id, "relation": "uses"},
                    {"source": node_id, "target": "region:EMA", "relation": "applies_to"},
                ])
        else:
            print("[WARN] No usable column in EMA file")
    else:
        print("[WARN] EMA file missing")

    # --- CMS ---
    if os.path.exists(CMS_FILE):
        df = pd.read_csv(CMS_FILE, low_memory=False)
        if "Facility Name" in df.columns:
            for i, hosp in enumerate(df["Facility Name"].dropna().unique()[:200]):
                node_id = f"cms_rule:{i+1}"
                regex_id = f"regex:cms_rule:{i+1}"
                nodes.extend([
                    {"id": node_id, "label": f"CMS Hospital Rule {i+1}"},
                    {"id": regex_id, "label": safe_regex(hosp)},
                    {"id": "region:CMS", "label": "CMS"},
                ])
                edges.extend([
                    {"source": "DataSource", "target": node_id, "relation": "contains"},
                    {"source": node_id, "target": regex_id, "relation": "uses"},
                    {"source": node_id, "target": "region:CMS", "relation": "applies_to"},
                ])
        else:
            print("[WARN] Column 'Facility Name' not found in CMS file")
    else:
        print("[WARN] CMS file missing")

    # --- HIPAA ---
    if os.path.exists(HIPAA_FILE):
        df = pd.read_csv(HIPAA_FILE)
        if "Name of Covered Entity" in df.columns:
            for i, entity in enumerate(df["Name of Covered Entity"].dropna().unique()[:200]):
                node_id = f"hipaa_rule:{i+1}"
                regex_id = f"regex:hipaa_rule:{i+1}"
                nodes.extend([
                    {"id": node_id, "label": f"HIPAA Entity Rule {i+1}"},
                    {"id": regex_id, "label": safe_regex(entity)},
                    {"id": "region:HIPAA", "label": "HIPAA"},
                ])
                edges.extend([
                    {"source": "DataSource", "target": node_id, "relation": "contains"},
                    {"source": node_id, "target": regex_id, "relation": "uses"},
                    {"source": node_id, "target": "region:HIPAA", "relation": "applies_to"},
                ])
        else:
            print("[WARN] Column 'Name of Covered Entity' not found in HIPAA file")
    else:
        print("[WARN] HIPAA file missing")

    return nodes, edges


def main():
    nodes, edges = build_nodes_edges()

    # Save nodes
    with open(NODES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "label"])
        writer.writeheader()
        writer.writerows(nodes)

    # Save edges
    with open(EDGES_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "relation"])
        writer.writeheader()
        writer.writerows(edges)

    # Save JSON
    graph = {"nodes": nodes, "edges": edges}
    with open(GRAPH_FILE, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)

    print(f"[DONE] Wrote {NODES_FILE}, {EDGES_FILE}, {GRAPH_FILE}")


if __name__ == "__main__":
    main()

