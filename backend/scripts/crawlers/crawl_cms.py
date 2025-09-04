# backend/scripts/crawlers/crawl_cms.py
import requests, os

OUT = os.path.join("data", "cms_hospitals.csv")
os.makedirs("data", exist_ok=True)

def crawl_cms():
    # Official CMS Hospital General Information CSV
    url = "https://data.cms.gov/provider-data/sites/default/files/resources/ea09f8a5-8176-4a49-8bb2-5a1e7c0bf0ce.csv"
    r = requests.get(url)
    r.raise_for_status()

    with open(OUT, "wb") as f:
        f.write(r.content)

    print(f"[CMS] Saved hospital dataset to {OUT}")

if __name__ == "__main__":
    crawl_cms()
