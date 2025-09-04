# backend/scripts/export_kg.py
"""
Builds a regex-ready knowledge graph from the raw datasets in backend/data/.
Outputs:
  - backend/bioregex_kg/nodes.csv   (id,label)
  - backend/bioregex_kg/edges.csv   (source,target,relation)
  - backend/bioregex_kg/graph.json  ({nodes:[...], edges:[...]})

Design:
  - Regions: FDA, EMA, CMS, HIPAA
  - Types:   drug_name, medicine_name, hospital_name, breach_type
  - Rules:   one rule per region/type (split into multiple regex chunks if long)
  - Regex:   case-insensitive, word-boundary anchored, whitespace-tolerant
Robustness:
  - Skips files that are actually HTML (failed downloads pasted as CSV)
  - Finds columns by fuzzy name match
  - Splits huge alternation lists into chunks to keep regex size reasonable
"""

from __future__ import annotations
import csv
import json
import os
import re
from typing import Iterable, List, Optional, Tuple

import pandas as pd


DATA_DIR = "backend/data"
OUT_DIR = "backend/bioregex_kg"

# ---------------------------------------
# Helpers
# ---------------------------------------

def ensure_out_dir():
    os.makedirs(OUT_DIR, exist_ok=True)
    # Overwrite (no append). We’ll simply rewrite files later.


def looks_like_html(path: str) -> bool:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(1024).lstrip()
            return head.startswith("<!DOCTYPE") or head.startswith("<html")
    except Exception:
        return False


def safe_read_csv(path: str) -> Optional[pd.DataFrame]:
    if not os.path.exists(path):
        print(f"[WARN] CSV not found: {path}")
        return None
    if looks_like_html(path):
        print(f"[WARN] CSV is actually HTML, skipping: {path}")
        return None
    try:
        df = pd.read_csv(path, dtype=str, low_memory=False)
        return df.fillna("")
    except Exception as e:
        print(f"[WARN] Failed reading CSV {path}: {e}")
        return None


def safe_read_xlsx(path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
    if not os.path.exists(path):
        print(f"[WARN] XLSX not found: {path}")
        return None
    try:
        df = pd.read_excel(path, dtype=str, sheet_name=sheet_name)  # openpyxl
        if isinstance(df, dict):  # if multiple sheets returned, concat
            df = pd.concat(df.values(), ignore_index=True)
        return df.fillna("")
    except Exception as e:
        print(f"[WARN] Failed reading XLSX {path}: {e}")
        return None


def pick_columns(df: pd.DataFrame, *needles: str) -> List[str]:
    """Return columns whose names contain ALL provided needles (case-insensitive)."""
    cols = []
    for c in df.columns:
        lc = c.lower()
        if all(n in lc for n in needles):
            cols.append(c)
    return cols


def gather_strings(df: pd.DataFrame, candidate_cols: Iterable[str]) -> List[str]:
    items = []
    for col in candidate_cols:
        ser = df[col].astype(str).str.strip()
        items.extend([x for x in ser.tolist() if x and x.lower() != "nan"])
    # de-duplicate, preserve rough ordering
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def normalize_for_regex(term: str) -> str:
    """Make space flexible and escape regex specials safely."""
    # Strip
    term = term.strip()
    # Escape first
    esc = re.escape(term)
    # Make spaces flexible
    esc = re.sub(r"\\ ", r"\\s+", esc)
    # Collapse multiple \s+ if they happen to arise
    esc = re.sub(r"(\\s\+)+", r"\\s+", esc)
    return esc


def chunk_regex(terms: List[str], chunk_size: int = 600) -> List[str]:
    """
    Build one or more regex patterns with word boundaries, case-insensitive intended.
    Each chunk avoids extremely long alternations which can be slow or rejected upstream.
    """
    patterns = []
    buf: List[str] = []

    for t in terms:
        esc = normalize_for_regex(t)
        if esc:
            buf.append(esc)
        if len(buf) >= chunk_size:
            patterns.append(r"\b(?:" + "|".join(buf) + r")\b")
            buf = []
    if buf:
        patterns.append(r"\b(?:" + "|".join(buf) + r")\b")
    return patterns


# ---------------------------------------
# Extract per source
# ---------------------------------------

def extract_fda_names() -> List[str]:
    path = os.path.join(DATA_DIR, "fda_drugs.csv")
    df = safe_read_csv(path)
    if df is None:
        return []
    cols = set()
    # common column name variants
    for probe in (
        ("brand", "name"),
        ("generic", "name"),
        ("proprietary", "name"),
        ("nonproprietary", "name"),
    ):
        cols.update(pick_columns(df, *probe))

    if not cols:
        # fallback: any column that literally equals id/brand_name/generic_name
        for c in ("brand_name", "generic_name", "proprietary_name", "nonproprietary_name"):
            if c in df.columns:
                cols.add(c)

    names = gather_strings(df, cols)
    print(f"[FDA] gathered {len(names)} names from columns: {sorted(cols)}")
    return names


def extract_ema_names() -> List[str]:
    path = os.path.join(DATA_DIR, "ema_human_medicines.xlsx")
    df = safe_read_xlsx(path)
    if df is None:
        return []
    cols = set()

    # Look for various "name" columns
    for c in df.columns:
        lc = c.lower()
        if "name" in lc:
            cols.add(c)

    names = gather_strings(df, cols)
    print(f"[EMA] gathered {len(names)} names from columns: {sorted(cols)}")
    return names


def extract_cms_hospital_names() -> List[str]:
    path = os.path.join(DATA_DIR, "cms_hospitals.csv")
    df = safe_read_csv(path)
    if df is None:
        return []
    cols = set()
    # common probes
    candidates = list(set(
        pick_columns(df, "hospital", "name")
        + pick_columns(df, "facility", "name")
        + [c for c in df.columns if c.lower().strip() in ("hospital_name", "provider_name")]
    ))
    cols.update(candidates)

    names = gather_strings(df, cols)
    print(f"[CMS] gathered {len(names)} hospital names from columns: {sorted(cols)}")
    return names


def extract_hipaa_breach_types() -> List[str]:
    path = os.path.join(DATA_DIR, "hipaa_breaches.csv")
    df = safe_read_csv(path)
    if df is None:
        return []
    # typical column names: "Type of Breach", "Breach Type", etc.
    cols = list(set(
        pick_columns(df, "type", "breach") +
        [c for c in df.columns if c.lower().strip() in ("type of breach", "breach type")]
    ))

    items = gather_strings(df, cols)
    # Normalize to title-case terms (optional)
    items = [re.sub(r"\s+", " ", x).strip() for x in items]
    print(f"[HIPAA] gathered {len(items)} breach types from columns: {sorted(cols)}")
    return items


# ---------------------------------------
# Graph assembly
# ---------------------------------------

def add_node(nodes: dict, node_id: str, label: str):
    if node_id not in nodes:
        nodes[node_id] = {"id": node_id, "label": label}


def add_edge(edges: list, source: str, target: str, relation: str):
    edges.append({"source": source, "target": target, "relation": relation})


def build_source_block(
    nodes: dict,
    edges: list,
    *,
    region_id: str,
    region_label: str,
    dtype_id: str,
    dtype_label: str,
    rule_slug: str,
    rule_label: str,
    terms: List[str],
):
    # Base nodes
    add_node(nodes, "DataSource", "Regulatory Data")
    add_node(nodes, region_id, region_label)
    add_node(nodes, dtype_id, dtype_label)

    # Rule node (logical rule grouping)
    rule_id = f"rule:{rule_slug}"
    add_node(nodes, rule_id, rule_label)

    # Edges: rule metadata
    add_edge(edges, rule_id, region_id, "BELONGS_TO")
    add_edge(edges, rule_id, dtype_id, "TYPED_AS")
    add_edge(edges, "DataSource", rule_id, "contains")

    # Regex chunks
    if not terms:
        print(f"[WARN] No terms for {rule_slug}; no regex nodes created.")
        return

    patterns = chunk_regex(terms, chunk_size=600)
    for i, pat in enumerate(patterns, start=1):
        regex_id = f"regex:{rule_slug}:{i}"
        add_node(nodes, regex_id, pat)
        add_edge(edges, rule_id, regex_id, "HAS_REGEX")


def main():
    ensure_out_dir()

    nodes: dict[str, dict] = {}
    edges: list[dict] = []

    # FDA
    fda_terms = extract_fda_names()
    build_source_block(
        nodes, edges,
        region_id="region:FDA", region_label="FDA",
        dtype_id="dtype:drug_name", dtype_label="Drug Name",
        rule_slug="fda_drug_names", rule_label="FDA Drug Names",
        terms=fda_terms
    )

    # EMA
    ema_terms = extract_ema_names()
    build_source_block(
        nodes, edges,
        region_id="region:EMA", region_label="EMA",
        dtype_id="dtype:medicine_name", dtype_label="Medicine Name",
        rule_slug="ema_medicine_names", rule_label="EMA Medicine Names",
        terms=ema_terms
    )

    # CMS
    cms_terms = extract_cms_hospital_names()
    build_source_block(
        nodes, edges,
        region_id="region:CMS", region_label="CMS",
        dtype_id="dtype:hospital_name", dtype_label="Hospital Name",
        rule_slug="cms_hospital_names", rule_label="CMS Hospital Names",
        terms=cms_terms
    )

    # HIPAA
    hipaa_terms = extract_hipaa_breach_types()
    build_source_block(
        nodes, edges,
        region_id="region:HIPAA", region_label="HIPAA",
        dtype_id="dtype:breach_type", dtype_label="Breach Type",
        rule_slug="hipaa_breach_types", rule_label="HIPAA Breach Types",
        terms=hipaa_terms
    )

    # ---- Write CSVs ----
    nodes_path = os.path.join(OUT_DIR, "nodes.csv")
    edges_path = os.path.join(OUT_DIR, "edges.csv")
    graph_path = os.path.join(OUT_DIR, "graph.json")

    # nodes.csv
    with open(nodes_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "label"])
        w.writeheader()
        for n in nodes.values():
            w.writerow(n)

    # edges.csv
    with open(edges_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source", "target", "relation"])
        w.writeheader()
        for e in edges:
            w.writerow(e)

    # graph.json
    graph = {"nodes": list(nodes.values()), "edges": edges}
    with open(graph_path, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    print(f"[DONE] Wrote {nodes_path}, {edges_path}, {graph_path}")


if __name__ == "__main__":
    main()
