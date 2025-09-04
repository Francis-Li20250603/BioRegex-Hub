# backend/scripts/crawlers/crawl_cms.py
import requests
import os

def crawl_cms():
    url = "https://data.cms.gov/provider-data/api/1/datastore/query/xubh-q36u/0/download?format=csv"
    os.makedirs("backend/data", exist_ok=True)
    out_path = "backend/data/cms_hospitals.csv"

    print(f"[CMS] Downloading hospital dataset from {url}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()

    with open(out_path, "wb") as f:
        f.write(r.content)

    print(f"[CMS] Saved dataset to {out_path}")

if __name__ == "__main__":
    crawl_cms()

