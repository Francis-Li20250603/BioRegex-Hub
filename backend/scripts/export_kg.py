import os
import csv
import json
import pandas as pd

DATA_DIR = "backend/data"
OUT_DIR = "backend/bioregex_kg"
os.makedirs(OUT_DIR, exist_ok=True)

nodes = []
edges = []

def add_node(node_id, label):
    nodes.append({"id": node_id, "label": label})

def add_edge(source, target, relation):
    edges.append({"source": source, "target": target, "relation": relation})

def make_regex_rule(prefix, idx, terms, region):
    """Create regex rules for a dataset column"""
    rule_id = f"{prefix}_rule:{idx}"
    regex_id = f"regex:{prefix}_rule:{idx}"

    # escape regex meta chars in terms
    pattern = r"\b(" + "|".join([str(t).replace("(", "\(").replace(")", "\)").replace(".", "\.") 
                                for t in terms if isinstance(t, str)]) + r")\b"

    add_node(rule_id, f"{region} Rule {idx}")
    add_node(regex_id, pattern)
    add_edge("DataSource", rule_id, "contains")
    add_edge(rule_id, regex_id, "uses")
    add_edge(rule_id, f"region:{region}", "applies_to")

# Base DataSource node
add_node("DataSource", "Regulatory Data")

# Regions
for region in ["FDA", "EMA", "CMS", "HIPAA"]:
    add_node(f"region:{region}", region)

# --- FDA ---
fda_file = os.path.join(DATA_DIR, "fda_drugs.csv")
if os.path.exists(fda_file):
    df = pd.read_csv(fda_file)
    if "brand_name" in df.columns:
        make_regex_rule("fda", 1, df["brand_name"].dropna().unique(), "FDA")
    if "generic_name" in df.columns:
        make_regex_rule("fda", 2, df["generic_name"].dropna().unique(), "FDA")
else:
    print("[WARN] FDA file missing")

# --- EMA ---
ema_file = os.path.join(DATA_DIR, "ema_human_medicines.xlsx")
if os.path.exists(ema_file):
    df = pd.read_excel(ema_file)
    # EMA sheet often has "Name" or "Medicine name"
    for col in df.columns:
        if "Name" in col:
            make_regex_rule("ema", 1, df[col].dropna().unique(), "EMA")
else:
    print("[WARN] EMA file missing")

# --- CMS ---
cms_file = os.path.join(DATA_DIR, "cms_hospitals.csv")
if os.path.exists(cms_file):
    df = pd.read_csv(cms_file)
    if "Facility Name" in df.columns:
        make_regex_rule("cms", 1, df["Facility Name"].dropna().unique(), "CMS")
else:
    print("[WARN] CMS file missing")

# --- HIPAA ---
hipaa_file = os.path.join(DATA_DIR, "hipaa_breaches.csv")
if os.path.exists(hipaa_file):
    df = pd.read_csv(hipaa_file)
    if "Name of Covered Entity" in df.columns:
        make_regex_rule("hipaa", 1, df["Name of Covered Entity"].dropna().unique(), "HIPAA")
    if "Covered Entity Type" in df.columns:
        make_regex_rule("hipaa", 2, df["Covered Entity Type"].dropna().unique(), "HIPAA")
else:
    print("[WARN] HIPAA file missing")

# --- Save outputs ---
nodes_file = os.path.join(OUT_DIR, "nodes.csv")
edges_file = os.path.join(OUT_DIR, "edges.csv")
graph_file = os.path.join(OUT_DIR, "graph.json")

pd.DataFrame(nodes).to_csv(nodes_file, index=False)
pd.DataFrame(edges).to_csv(edges_file, index=False)
with open(graph_file, "w") as f:
    json.dump({"nodes": nodes, "edges": edges}, f, indent=2)

print(f"[DONE] Wrote {nodes_file}, {edges_file}, {graph_file}")

