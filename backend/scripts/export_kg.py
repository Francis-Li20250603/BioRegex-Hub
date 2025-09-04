# backend/scripts/export_kg.py

import os
import re
import json
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))

DATA_DIR = os.path.join(REPO_ROOT, "backend", "data")
OUT_DIR = os.path.join(REPO_ROOT, "backend", "bioregex_kg")

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------
# Helpers
# ---------------------------

def make_regex(term: str) -> str:
    """
    Create a safe regex pattern for a term.
    Escapes special chars and enforces case-insensitive whole word matching.
    """
    term = term.strip()
    if not term:
        return None
    safe = re.escape(term)
    return rf"(?i)\b{safe}\b"

def write_csv(path, rows, header):
    pd.DataFrame(rows, columns=header).to_csv(path, index=False)

# ---------------------------
# Data parsers
# ---------------------------

def parse_fda_terms(csv_file):
    if not os.path.exists(csv_file):
        print(f"[WARN] FDA file missing")
        return []
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"[WARN] Failed to read FDA file: {e}")
        return []

    col = next((c for c in df.columns if "generic_name" in c.lower() or "substance_name" in c.lower()), None)
    if not col:
        print(f"[WARN] No usable column in FDA file")
        return []

    return df[col].dropna().astype(str).unique().tolist()

def parse_ema_terms(xlsx_file):
    if not os.path.exists(xlsx_file):
        print(f"[WARN] EMA file not found: {xlsx_file}")
        return []

    try:
        df = pd.read_excel(xlsx_file, sheet_name="Medicine")
    except Exception as e:
        print(f"[WARN] Could not read EMA Excel file: {e}")
        return []

    col_candidates = ["Medicine", "Name of medicine"]
    col = next((c for c in col_candidates if c in df.columns), None)

    if not col:
        print(f"[WARN] No usable column in EMA file")
        return []

    return df[col].dropna().astype(str).unique().tolist()

def parse_cms_terms(csv_file):
    if not os.path.exists(csv_file):
        print(f"[WARN] CMS file missing")
        return []
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"[WARN] Failed to read CMS file: {e}")
        return []

    col = next((c for c in df.columns if "hospital" in c.lower()), None)
    if not col:
        print(f"[WARN] No usable column in CMS file")
        return []

    return df[col].dropna().astype(str).unique().tolist()

def parse_hipaa_terms(csv_file):
    if not os.path.exists(csv_file):
        print(f"[WARN] HIPAA file missing")
        return []
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"[WARN] Failed to read HIPAA file: {e}")
        return []

    col = next((c for c in df.columns if "breach" in c.lower()), None)
    if not col:
        print(f"[WARN] No usable column in HIPAA file")
        return []

    return df[col].dropna().astype(str).unique().tolist()

# ---------------------------
# Build KG
# ---------------------------

def build_kg():
    sources = {
        "fda_drug_names": parse_fda_terms(os.path.join(DATA_DIR, "fda_drugs.csv")),
        "ema_medicine_names": parse_ema_terms(os.path.join(DATA_DIR, "ema_human_medicines.xlsx")),
        "cms_hospital_names": parse_cms_terms(os.path.join(DATA_DIR, "cms_hospitals.csv")),
        "hipaa_breach_types": parse_hipaa_terms(os.path.join(DATA_DIR, "hipaa_breaches.csv")),
    }

    nodes, edges = [], []

    for src, terms in sources.items():
        if not terms:
            print(f"[WARN] No terms for {src}; no regex nodes created.")
            continue

        for t in terms:
            regex = make_regex(t)
            if not regex:
                continue
            node_id = f"{src}:{t}"
            nodes.append({"id": node_id, "label": t, "source": src, "regex": regex})
            edges.append({"source": src, "target": node_id, "relation": "HAS_TERM"})

    # Write CSVs
    write_csv(os.path.join(OUT_DIR, "nodes.csv"), nodes, ["id", "label", "source", "regex"])
    write_csv(os.path.join(OUT_DIR, "edges.csv"), edges, ["source", "target", "relation"])

    # JSON export
    graph = {"nodes": nodes, "edges": edges}
    with open(os.path.join(OUT_DIR, "graph.json"), "w") as f:
        json.dump(graph, f, indent=2)

    print(f"[DONE] Wrote {os.path.join(OUT_DIR, 'nodes.csv')}, {os.path.join(OUT_DIR, 'edges.csv')}, {os.path.join(OUT_DIR, 'graph.json')}")

if __name__ == "__main__":
    build_kg()
