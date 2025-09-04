# backend/scripts/export_kg.py

import os
import csv
import json
import pandas as pd

# --- Resolve paths relative to repo root ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

DATA_DIR = os.path.join(REPO_ROOT, "backend", "data")
OUT_DIR = os.path.join(REPO_ROOT, "backend", "bioregex_kg")
os.makedirs(OUT_DIR, exist_ok=True)

# --- Initialize containers ---
nodes = []
edges = []

# --- Helper functions ---
def add_node(node_id, label):
    if not any(n["id"] == node_id for n in nodes):
        nodes.append({"id": node_id, "label": label})

def add_edge(source, target, relation):
    edges.append({"source": source, "target": target, "relation": relation})

def load_terms(path, expected_column=None, filetype="csv"):
    """Load terms from CSV/XLSX, auto-detect column if expected is missing."""
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return []

    try:
        if filetype == "csv":
            df = pd.read_csv(path)
        else:
            df = pd.read_excel(path)

        # Choose column
        if expected_column and expected_column in df.columns:
            column = expected_column
        else:
            object_cols = df.select_dtypes(include=["object"]).columns
            if len(object_cols) == 0:
                print(f"[WARN] No string-like columns in {path}")
                return []
            column = object_cols[0]
            print(f"[INFO] Expected '{expected_column}' not found in {os.path.basename(path)}; using '{column}' instead.")

        # Clean values
        terms = df[column].dropna().astype(str).unique().tolist()
        return [t.strip() for t in terms if t.strip()]

    except Exception as e:
        print(f"[ERROR] Could not read {path}: {e}")
        return []

# --- FDA: Drug names ---
fda_terms = load_terms(os.path.join(DATA_DIR, "fda_drugs.csv"), "brand_name", "csv")
if fda_terms:
    add_node("DataSource", "Regulatory Data")
    add_node("region:FDA", "FDA")
    for i, term in enumerate(fda_terms[:200]):  # limit for performance
        rule_id = f"fda_rule:{i+1}"
        add_node(rule_id, "FDA Drug Rule")
        add_node(f"regex:{rule_id}", rf"\b{term}\b")
        add_edge("DataSource", rule_id, "contains")
        add_edge(rule_id, f"regex:{rule_id}", "uses")
        add_edge(rule_id, "region:FDA", "applies_to")
else:
    print("[WARN] No terms for fda_drugs; no regex nodes created.")

# --- EMA: Human medicines ---
ema_terms = load_terms(os.path.join(DATA_DIR, "ema_human_medicines.xlsx"), "Name of medicine", "xlsx")
if ema_terms:
    add_node("region:EMA", "EMA")
    for i, term in enumerate(ema_terms[:200]):
        rule_id = f"ema_rule:{i+1}"
        add_node(rule_id, "EMA Medicine Rule")
        add_node(f"regex:{rule_id}", rf"\b{term}\b")
        add_edge("DataSource", rule_id, "contains")
        add_edge(rule_id, f"regex:{rule_id}", "uses")
        add_edge(rule_id, "region:EMA", "applies_to")
else:
    print("[WARN] No terms for ema_human_medicines; no regex nodes created.")

# --- CMS: Hospitals ---
cms_terms = load_terms(os.path.join(DATA_DIR, "cms_hospitals.csv"), "hospital_name", "csv")
if cms_terms:
    add_node("region:CMS", "CMS")
    for i, term in enumerate(cms_terms[:200]):
        rule_id = f"cms_rule:{i+1}"
        add_node(rule_id, "CMS Hospital Rule")
        add_node(f"regex:{rule_id}", rf"\b{term}\b")
        add_edge("DataSource", rule_id, "contains")
        add_edge(rule_id, f"regex:{rule_id}", "uses")
        add_edge(rule_id, "region:CMS", "applies_to")
else:
    print("[WARN] No terms for cms_hospitals; no regex nodes created.")

# --- HIPAA: Breach types ---
hipaa_terms = load_terms(os.path.join(DATA_DIR, "hipaa_breaches.csv"), "Breach Submission Type", "csv")
if hipaa_terms:
    add_node("region:HIPAA", "HIPAA")
    for i, term in enumerate(hipaa_terms[:200]):
        rule_id = f"hipaa_rule:{i+1}"
        add_node(rule_id, "HIPAA Breach Rule")
        add_node(f"regex:{rule_id}", rf"\b{term}\b")
        add_edge("DataSource", rule_id, "contains")
        add_edge(rule_id, f"regex:{rule_id}", "uses")
        add_edge(rule_id, "region:HIPAA", "applies_to")
else:
    print("[WARN] No terms for hipaa_breaches; no regex nodes created.")

# --- Save outputs ---
nodes_file = os.path.join(OUT_DIR, "nodes.csv")
edges_file = os.path.join(OUT_DIR, "edges.csv")
graph_file = os.path.join(OUT_DIR, "graph.json")

pd.DataFrame(nodes).to_csv(nodes_file, index=False)
pd.DataFrame(edges).to_csv(edges_file, index=False)
with open(graph_file, "w") as f:
    json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

print(f"[DONE] Wrote {nodes_file}, {edges_file}, {graph_file}")
