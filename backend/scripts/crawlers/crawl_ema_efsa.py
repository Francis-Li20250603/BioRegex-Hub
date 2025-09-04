# backend/scripts/crawlers/crawl_ema_efsa.py
import requests, os
from bs4 import BeautifulSoup
import urllib.parse

os.makedirs("data", exist_ok=True)
EMA_OUT = os.path.join("data", "ema_human_medicines.xlsx")
EFSA_OUT = os.path.join("data", "efsa_openfoodtox.xlsx")

def crawl_ema():
    landing = "https://www.ema.europa.eu/en/medicines/download-medicine-data"
    r = requests.get(landing)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    link = soup.find("a", href=lambda href: href and href.endswith(".xlsx"))
    if not link:
        raise ValueError("Could not find EMA download link on landing page")
    url = urllib.parse.urljoin(landing, link["href"])
    resp = requests.get(url)
    resp.raise_for_status()
    with open(EMA_OUT, "wb") as f:
        f.write(resp.content)
    print(f"[EMA] Saved medicines dataset from {url} to {EMA_OUT}")

def crawl_efsa():
    # Correct stable link on Zenodo
    url = "https://zenodo.org/record/4274656/files/OpenFoodTox_v2.xlsx?download=1"
    r = requests.get(url)
    r.raise_for_status()
    with open(EFSA_OUT, "wb") as f:
        f.write(r.content)
    print(f"[EFSA] Saved OpenFoodTox dataset to {EFSA_OUT}")

if __name__ == "__main__":
    crawl_ema()
    crawl_efsa()
