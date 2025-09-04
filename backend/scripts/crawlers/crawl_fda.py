import requests, csv, os

OUT = os.path.join("data", "fda_drugs.csv")
os.makedirs("data", exist_ok=True)

def crawl_fda(limit=50):
    url = f"https://api.fda.gov/drug/label.json?limit={limit}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json().get("results", [])

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "brand_name", "generic_name", "purpose"])
        writer.writeheader()
        for d in data:
            writer.writerow({
                "id": d.get("id"),
                "brand_name": ",".join(d.get("openfda", {}).get("brand_name", [])),
                "generic_name": ",".join(d.get("openfda", {}).get("generic_name", [])),
                "purpose": ",".join(d.get("purpose", [])) if "purpose" in d else ""
            })
    print(f"[FDA] Saved {len(data)} records to {OUT}")

if __name__ == "__main__":
    crawl_fda()
