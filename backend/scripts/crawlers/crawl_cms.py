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

    # Extract column names from metadata
    columns = [c["name"] for c in json_data["meta"]["view"]["columns"]]
    rows = json_data.get("data", [])

    # Save to CSV
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"[CMS] Saved {len(rows)} hospital records to {OUT}")

if __name__ == "__main__":
    crawl_cms()

