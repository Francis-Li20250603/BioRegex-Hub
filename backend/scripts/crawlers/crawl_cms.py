# backend/scripts/crawlers/crawl_cms.py
import requests, csv, os

OUT = os.path.join("data", "cms_hospitals.csv")
os.makedirs("data", exist_ok=True)

def crawl_cms(limit=50):
    url = f"https://data.cms.gov/resource/xubh-q36u.json?$limit={limit}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()

    if not data:
        raise ValueError("No data returned from CMS API")

    fieldnames = sorted(data[0].keys())

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"[CMS] Saved {len(data)} hospital records to {OUT}")

if __name__ == "__main__":
    crawl_cms()

