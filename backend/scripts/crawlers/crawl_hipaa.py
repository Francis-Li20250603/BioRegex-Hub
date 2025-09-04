# backend/scripts/crawlers/crawl_hipaa.py

import requests
import os

def crawl_hipaa():
    url = "https://ocrportal.hhs.gov/ocr/breach/download?format=csv"
    os.makedirs("backend/data", exist_ok=True)
    out_path = "backend/data/hipaa_breaches.csv"

    print(f"[HIPAA] Attempting to download HIPAA breaches via portal: {url}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()

    ct = r.headers.get("Content-Type", "")
    if "text/csv" not in ct:
        raise RuntimeError(f"[HIPAA] Unexpected content type: {ct}")

    with open(out_path, "wb") as f:
        f.write(r.content)

    print(f"[HIPAA] Saved data to {out_path}")

if __name__ == '__main__':
    crawl_hipaa()
