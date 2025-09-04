import requests, csv, os

OUT = os.path.join("data", "cms_providers.csv")
os.makedirs("data", exist_ok=True)

def crawl_cms():
    url = "https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0"  # Hospital General Info
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()["records"]

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"[CMS] Saved {len(data)} provider records to {OUT}")

if __name__ == "__main__":
    crawl_cms()
