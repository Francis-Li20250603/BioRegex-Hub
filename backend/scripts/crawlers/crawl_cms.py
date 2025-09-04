# backend/scripts/crawlers/crawl_cms.py
import requests, csv, os

OUT = os.path.join("data", "cms_hospitals.csv")
os.makedirs("data", exist_ok=True)

def crawl_cms(limit=50):
    # Hospital General Information dataset
    url = f"https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0?limit={limit}"
    r = requests.get(url)
    r.raise_for_status()
    json_data = r.json()

    # Try different possible keys
    data = json_data.get("records") or json_data.get("data") or []
    if not data:
        raise ValueError("Unexpected CMS API response format")

    # Normalize keys
    fieldnames = data[0].keys()

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"[CMS] Saved {len(data)} hospital records to {OUT}")

if __name__ == "__main__":
    crawl_cms()

