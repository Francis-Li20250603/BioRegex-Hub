# backend/scripts/crawlers/crawl_hipaa.py

import requests
import os
import csv

def crawl_hipaa():
    api_url = "https://healthdata.gov/resource/2fwp-4ekt.json"
    os.makedirs("backend/data", exist_ok=True)
    out_csv = "backend/data/hipaa_breaches.csv"

    print(f"[HIPAA] Fetching breach data from {api_url}")
    r = requests.get(api_url, timeout=60)
    r.raise_for_status()

    data = r.json()
    if not data:
        raise RuntimeError("[HIPAA] No data received from API.")

    # Write CSV
    keys = sorted({k for item in data for k in item.keys()})
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in data:
            writer.writerow({k: row.get(k, "") for k in keys})

    print(f"[HIPAA] Saved {len(data)} records to {out_csv}")

if __name__ == "__main__":
    crawl_hipaa()



