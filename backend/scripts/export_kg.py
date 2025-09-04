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

def load_csv_terms(path, column):
    """Safely load a column from a CSV if file exists."""
    if not os.path.exists(path):
        print(f"[WARN] CSV not found: {path}")
        return []
    try:
        df = pd.read_csv(path)
        if column in df.columns:
            terms = df[column].dropna().astype(str).unique().tolist()
            return [t.strip() for t in terms if t.strip()]
        else:
            print(f"[WARN] Column {column} not found in {path}")
            return []
    except Exception as e:
        print(f"[ERROR] Could not read {path}: {e}")
        return []

def load_xlsx_terms(path, column):
    """Safely load a column from an XLSX if file exists."""
    if not os.path.exists(path):
        print(f"[WARN] XLSX not found: {path}")
        return []
    try:
        df = pd.read_excel(path)
        if column in df.columns:
            terms = df[column].dropna().astype(str).unique().tolist()
            return [t.strip() for t in terms if t.strip()]
        else:
            print(f"[WARN] Column {column} not found in {path}")
            return []
    except Exception as e:
        print(f"[ERROR] Could not read {path}: {e}")
        return []

# --- FDA: Drug names ---
fda_file = os.path.join(DATA_DIR, "fda_drugs.csv")
fda_terms = load_csv_terms(fda_file, "brand_name")
if fda_terms:
    add_node("DataSource", "Regulatory Data")
    add_node("region:FDA", "FDA")
    for i, term in enumerate(fda_terms[:200]):  # limit to avoid overgrowth
        rule_id = f"fda_rule:{i+1}"
        add_node(rule_id, "FDA Drug Rule")
        add_node(f"regex:{rule_id}", rf"\b{term}\b")
        add_edge("DataSource", rule_id, "contains")
        add_edge(rule_id, f"regex:{rule_id}", "uses")
        add_edge(rule_id, "region:FDA", "applies_to")
else:
    print("[WARN] No terms for fda_drug_names; no regex nodes created.")

# --- EMA: Human medicines ---
ema_file = os.path.join(DATA_DIR, "ema_human_medicines.xlsx")
ema_terms = load_xlsx_terms(ema_file, "Name of medicine")
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
    print("[WARN] No terms for ema_medicine_names; no regex nodes created.")

# --- CMS: Hospital names ---
cms_file = os.path.join(DATA_DIR, "cms_hospitals.csv")
cms_terms = load_csv_terms(cms_file, "hospital_name")
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
    print("[WARN] No terms for cms_hospital_names; no regex nodes created.")

# --- HIPAA: Breach types ---
hipaa_file = os.path.join(DATA_DIR, "hipaa_breaches.csv")
hipaa_terms = load_csv_terms(hipaa_file, "Breach Submission Type")
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
    print("[WARN] No terms for hipaa_breach_types; no regex nodes created.")

# --- Save outputs ---
nodes_file = os.path.join(OUT_DIR, "nodes.csv")
edges_file = os.path.join(OUT_DIR, "edges.csv")
graph_file = os.path.join(OUT_DIR, "graph.json")

pd.DataFrame(nodes).to_csv(nodes_file, index=False)
pd.DataFrame(edges).to_csv(edges_file, index=False)
with open(graph_file, "w") as f:
    json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

print(f"[DONE] Wrote {nodes_file}, {edges_file}, {graph_file}")

