import json, csv, os
from sqlmodel import Session, select
from app.database import get_engine
from app.models import Rule

OUT_DIR = os.environ.get("KG_OUT_DIR", "./bioregex_kg")
os.makedirs(OUT_DIR, exist_ok=True)

def main():
    engine = get_engine()
    with Session(engine) as s:
        rules = s.exec(select(Rule)).all()

    nodes, edges = [], []
    seen_regions, seen_dtypes = set(), set()

    for r in rules:
        rid = f"rule:{r.id}"
        nodes.append({
            "id": rid,
            "label": "Rule",
            "pattern": r.pattern,
            "region": r.region,
            "data_type": r.data_type
        })

        reg_id = f"region:{r.region}"
        if r.region not in seen_regions:
            nodes.append({"id": reg_id, "label": "Region", "name": r.region})
            seen_regions.add(r.region)
        edges.append({"source": rid, "target": reg_id, "type": "BELONGS_TO"})

        dt_id = f"dtype:{r.data_type}"
        if r.data_type not in seen_dtypes:
            nodes.append({"id": dt_id, "label": "DataType", "name": r.data_type})
            seen_dtypes.add(r.data_type)
        edges.append({"source": rid, "target": dt_id, "type": "TYPED_AS"})

    with open(os.path.join(OUT_DIR, "graph.json"), "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT_DIR, "nodes.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","label","pattern","region","data_type","name"])
        w.writeheader()
        for n in nodes:
            w.writerow({k: n.get(k,"") for k in w.fieldnames})

    with open(os.path.join(OUT_DIR, "edges.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["source","target","type"])
        w.writeheader()
        for e in edges:
            w.writerow(e)

if __name__ == "__main__":
    main()
