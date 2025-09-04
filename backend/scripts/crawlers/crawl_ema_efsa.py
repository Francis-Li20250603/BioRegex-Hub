# backend/scripts/crawlers/crawl_ema_efsa.py
import requests, os, time
from bs4 import BeautifulSoup
import urllib.parse

os.makedirs("data", exist_ok=True)
EMA_OUT = os.path.join("data", "ema_human_medicines.xlsx")
EFSA_OUT = os.path.join("data", "efsa_openfoodtox.xlsx")

HEADERS = {"User-Agent": "BioRegex-Hub/1.0 (contact: example@example.com)"}

def polite_request(url, retries=3, backoff=10):
    """Make polite requests with retries for 429 errors."""
    for i in range(retries):
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 429:
            wait = backoff * (i + 1)
            print(f"[WARN] 429 Too Many Requests for {url}, retrying in {wait}s...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r
    raise RuntimeError(f"Failed to fetch {url} after {retries} retries")

def crawl_ema():
    landing = "https://www.ema.europa.eu/en/medicines/download-medicine-data"
    print(f"[EMA] Visiting landing page: {landing}")
    r = polite_request(landing)
    soup = BeautifulSoup(r.text, "html.parser")
    link = soup.find("a", href=lambda href: href and href.endswith(".xlsx"))
    if not link:
        raise ValueError("Could not find EMA .xlsx link")
    url = urllib.parse.urljoin(landing, link["href"])
    print(f"[EMA] Attempting download from: {url}")
    resp = polite_request(url)
    with open(EMA_OUT, "wb") as f:
        f.write(resp.content)
    print(f"[EMA] Saved dataset to {EMA_OUT}")

def crawl_efsa():
    # Corrected EFSA link (note: /record/ not /records/)
    url = "https://zenodo.org/record/4274656/files/OpenFoodTox_v2.xlsx?download=1"
    print(f"[EFSA] Attempting download from: {url}")
    resp = polite_request(url)
    with open(EFSA_OUT, "wb") as f:
        f.write(resp.content)
    print(f"[EFSA] Saved dataset to {EFSA_OUT}")

if __name__ == "__main__":
    try:
        crawl_ema()
    except Exception as e:
        print(f"[EMA] Skipped due to error: {e}")
    try:
        crawl_efsa()
    except Exception as e:
        print(f"[EFSA] Skipped due to error: {e}")
