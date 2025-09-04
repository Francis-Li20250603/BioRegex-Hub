# backend/scripts/crawlers/crawl_cms.py
import requests, os

OUT = os.path.join("data", "cms_hospitals.csv")
os.makedirs("data", exist_ok=True)

def crawl_cms():
    # Stable dataset export for Hospital General Information
    url = "https://data.cms.gov/provider-data/dataset/xubh-q36u.csv"
    r = requests.get(url)
    r.raise_for_status()

    with open(OUT, "wb") as f:
        f.write(r.content)

    print(f"[CMS] Saved hospital dataset to {OUT}")

if __name__ == "__main__":
    crawl_cms()
