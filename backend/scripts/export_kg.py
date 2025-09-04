# backend/scripts/export_kg.py
import os
import json
import uuid
import shutil
from typing import Dict, Any, List, Optional

import pandas as pd

# --- Paths ---------------------------------------------------
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA_DIR = os.path.join(REPO_ROOT, "data")
KG_DIR = os.path.join(REPO_ROOT, "bioregex_kg")

# Always wipe the KG folder before rebuilding
if os.path.exists(KG_DIR):
    shutil.rmtree(KG_DIR)
os.makedirs(KG_DIR, exist_ok=True)

NODES_CSV = os.path.join(KG_DIR, "nodes.csv")
EDGES_CSV = os.path.join(KG_DIR, "edges.csv")
GRAPH_JSON = os.path.join(KG_DIR, "graph.json")

# --- Helpers -------------------------------------------------
def uuid5_for(*parts: str) -> str:
    """Deterministic UUIDv5 from strings."""
    base = "||".join([p if p is not None else "" for p in parts])
    return str(uuid.uuid5(uuid.NAMESPACE_URL, base))

def safe_label(row: Dict[str, Any], fallbacks: List[str], default_prefix: str) -> str:
    for k in fallbacks:
        v = row.get(k)
        if v and isinstance(v, str) and v.strip():
            return v.strip()
    for v in row.values():
        if isinstance(v, str) and v.strip():
            return v.strip()
    return f"{default_prefix}:{uuid.uuid4().hex[:8]}"

def load_csv(path: str) -> Optional[pd.DataFrame]:
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception:
            return pd.read_csv(path, encoding="ISO-8859-1")
    return None

def load_xlsx(path: str) -> Optional[pd.DataFrame]:
    if os.path.exists(path):
        try:
            return pd.read_excel(path, engine="openpyxl")
        except Exception:
            return pd.read_excel(path)
    return None

def rows_to_nodes(rows: List[Dict[str, Any]], type_name: str, source_key: str) -> List[Dict[str, Any]]:
    nodes = []
    for r in rows:
        label = safe_label(
            r,
            fallbacks=[
                "brand_name", "generic_name", "drug_name", "product_name", "proprietary_name",
                "Name", "name", "medicinal_product", "medicinal_product_name",
                "facility_name", "hospital_name", "provider_name",
                "entity_name", "covered_entity_name", "Name of Covered Entity",
                "title"
            ],
            default_prefix=type_name
        )
        id_basis = [type_name, source_key, label]
        for key in ("application_number", "product_ndc", "ndc", "id", "ID", "eudract_number"):
            if r.get(key):
                id_basis.append(str(r.get(key)))
        node_id = uuid5_for(*id_basis)
        nodes.append({
            "id": node_id,
            "label": label,
            "type": type_name,
            "source": source_key,
            "props": json.dumps(r, ensure_ascii=False)
        })
    return nodes

def df_to_rows(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df is None or df.empty:
        return []
    return [
        {k: (None if pd.isna(v) else v) for k, v in row.items()}
        for row in df.to_dict(orient="records")
    ]

# --- Source “root” nodes ------------------------------------
SOURCE_ROOTS = [
    {"id": uuid5_for("SOURCE", "FDA"),   "label": "FDA",   "type": "Source", "source": "SYSTEM", "props": json.dumps({"url": "https://www.fda.gov"})},
    {"id": uuid5_for("SOURCE", "HIPAA"), "label": "HIPAA", "type": "Source", "source": "SYSTEM", "props": json.dumps({"url": "https://www.hhs.gov/hipaa"})},
    {"id": uuid5_for("SOURCE", "CMS"),   "label": "CMS",   "type": "Source", "source": "SYSTEM", "props": json.dumps({"url": "https://data.cms.gov"})},
    {"id": uuid5_for("SOURCE", "EMA"),   "label": "EMA",   "type": "Source", "source": "SYSTEM", "props": json.dumps({"url": "https://www.ema.europa.eu"})},
    {"id": uuid5_for("SOURCE", "EFSA"),  "label": "EFSA",  "type": "Source", "source": "SYSTEM", "props": json.dumps({"url": "https://www.efsa.europa.eu"})},
]

# --- Main build ---------------------------------------------
def main():
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, str]] = []

    # add source roots
    nodes.extend(SOURCE_ROOTS)
    src_ids = {n["label"]: n["id"] for n in SOURCE_ROOTS}

    # FDA
    fda_df = load_csv(os.path.join(DATA_DIR, "fda_drugs.csv"))
    fda_nodes = rows_to_nodes(df_to_rows(fda_df), "Drug", "FDA")
    nodes.extend(fda_nodes)
    edges.extend([{"source": src_ids["FDA"], "target": n["id"], "type": "CONTAINS_RECORD"} for n in fda_nodes])

    # HIPAA
    hipaa_df = load_csv(os.path.join(DATA_DIR, "hipaa_breaches.csv"))
    hipaa_nodes = rows_to_nodes(df_to_rows(hipaa_df), "Breach", "HIPAA")
    nodes.extend(hipaa_nodes)
    edges.extend([{"source": src_ids["HIPAA"], "target": n["id"], "type": "CONTAINS_RECORD"} for n in hipaa_nodes])

    # CMS
    cms_df = load_csv(os.path.join(DATA_DIR, "cms_hospitals.csv"))
    cms_nodes = rows_to_nodes(df_to_rows(cms_df), "Provider", "CMS")
    nodes.extend(cms_nodes)
    edges.extend([{"source": src_ids["CMS"], "target": n["id"], "type": "CONTAINS_RECORD"} for n in cms_nodes])

    # EMA
    ema_df = load_xlsx(os.path.join(DATA_DIR, "ema_human_medicines.xlsx"))
    ema_nodes = rows_to_nodes(df_to_rows(ema_df), "Medicine", "EMA")
    nodes.extend(ema_nodes)
    edges.extend([{"source": src_ids["EMA"], "target": n["id"], "type": "CONTAINS_RECORD"} for n in ema_nodes])

    # EFSA
    efsa_xlsx = os.path.join(DATA_DIR, "efsa_openfoodtox.xlsx")
    if os.path.exists(efsa_xlsx):
        efsa_df = load_xlsx(efsa_xlsx)
        efsa_nodes = rows_to_nodes(df_to_rows(efsa_df), "Substance", "EFSA")
        nodes.extend(efsa_nodes)
        edges.extend([{"source": src_ids["EFSA"], "target": n["id"], "type": "CONTAINS_RECORD"} for n in efsa_nodes])

    # Deduplicate
    seen = set()
    unique_nodes = []
    for n in nodes:
        if n["id"] not in seen:
            unique_nodes.append(n)
            seen.add(n["id"])

    # Write outputs
    pd.DataFrame(unique_nodes).to_csv(NODES_CSV, index=False)
    pd.DataFrame(edges).to_csv(EDGES_CSV, index=False)
    with open(GRAPH_JSON, "w", encoding="utf-8") as f:
        json.dump({"nodes": unique_nodes, "edges": edges}, f, ensure_ascii=False, indent=2)

    print(f"[KG] Wrote {len(unique_nodes)} nodes and {len(edges)} edges to {KG_DIR}")

if __name__ == "__main__":
    main()

