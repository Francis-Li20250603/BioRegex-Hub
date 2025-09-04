# backend/scripts/export_kg.py
import os
import csv
import json
import pandas as pd

DATA_DIR = "backend/data"
OUT_DIR = "backend/bioregex_kg"
os.makedirs(OUT_DIR, exist_ok=True)

def safe_read_csv(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"[WARN] Could not read {path}: {e}")
        return pd.DataFrame()

def safe_read_excel(path):
    try:
        return pd.read_excel(path)
    except Exception as e:
        print(f"[WARN] Could not read {path}: {e}")
        return pd.DataFrame()

def build_kg():
    nodes, edges = [], []

    # ✅ FDA
    fda_path = os.path.join(DATA_DIR, "fda_drugs.csv")
    if os.path.exists(fda_path):
        df = safe_read_csv(fda_path)
        for _, row in df.iterrows():
            brand = row.get("brand_name")
            generic = row.get("generic_name")
            if pd.notna(brand):
                nodes.append({"id": f"drug:{brand}", "label": brand, "type": "Drug"})
            if pd.notna(generic):
                nodes.append({"id": f"drug:{generic}", "label": generic, "type": "Drug"})
            if pd.notna(brand) and pd.notna(generic):
                edges.append({"source": f"drug:{brand}", "target": f"drug:{generic}", "relation": "HAS_GENERIC"})

    # ✅ HIPAA
    hipaa_path = os.path.join(DATA_DIR, "hipaa_breaches.csv")
    if os.path.exists(hipaa_path):
        df = safe_read_csv(hipaa_path)
        if not df.empty:
            for _, row in df.iterrows():
                breach_id = row.get("id") or row.get("BreachID") or _
                breach_type = row.get("Type of Breach") or row.get("breach_type")
                if pd.notna(breach_id):
                    nodes.append({"id": f"breach:{breach_id}", "label": "HIPAA Breach", "type": "Breach"})
                if pd.notna(breach_type):
                    nodes.append({"id": f"btype:{breach_type}", "label": breach_type, "type": "BreachType"})
                    edges.append({"source": f"breach:{breach_id}", "target": f"btype:{breach_type}", "relation": "CATEGORIZED_AS"})

    # ✅ CMS
    cms_path = os.path.join(DATA_DIR, "cms_hospitals.csv")
    if os.path.exists(cms_path):
        df = safe_read_csv(cms_path)
        if not df.empty:
            for _, row in df.iterrows():
                hosp = row.get("facility_name") or row.get("Hospital Name")
                city = row.get("city") or row.get("City")
                if pd.notna(hosp):
                    nodes.append({"id": f"hosp:{hosp}", "label": hosp, "type": "Hospital"})
                if pd.notna(city):
                    nodes.append({"id": f"city:{city}", "label": city, "type": "City"})
                    edges.append({"source": f"hosp:{hosp}", "target": f"city:{city}", "relation": "LOCATED_IN"})

    # ✅ EMA
    ema_path = os.path.join(DATA_DIR, "ema_human_medicines.xlsx")
    if os.path.exists(ema_path):
        df = safe_read_excel(ema_path)
        if not df.empty:
            for _, row in df.iterrows():
                med = row.get("name") or row.get("Medicinal product name")
                active = row.get("active_substance") or row.get("Active substance")
                if pd.notna(med):
                    nodes.append({"id": f"med:{med}", "label": med, "type": "Medicine"})
                if pd.notna(active):
                    nodes.append({"id": f"sub:{active}", "label": active, "type": "Substance"})
                if pd.notna(med) and pd.notna(active):
                    edges.append({"source": f"med:{med}", "target": f"sub:{active}", "relation": "CONTAINS"})

    # Deduplicate nodes/edges
    unique_nodes = {n["id"]: n for n in nodes}.values()
    unique_edges = {f'{e["source"]}-{e["target"]}-{e["relation"]}': e for e in edges}.values()

    # Save CSVs
    with open(os.path.join(OUT_DIR, "nodes.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "label", "type"])
        writer.writeheader()
        writer.writerows(unique_nodes)

    with open(os.path.join(OUT_DIR, "edges.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["source", "target", "relation"])
        writer.writeheader()
        writer.writerows(unique_edges)

    # Save JSON
    with open(os.path.join(OUT_DIR, "graph.json"), "w", encoding="utf-8") as f:
        json.dump({"nodes": list(unique_nodes), "edges": list(unique_edges)}, f, indent=2)

    print(f"[KG] Exported {len(unique_nodes)} nodes and {len(unique_edges)} edges to {OUT_DIR}")

if __name__ == "__main__":
    build_kg()
