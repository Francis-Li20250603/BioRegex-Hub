# backend/scripts/crawlers/crawl_ema_efsa.py
import requests, os

os.makedirs("data", exist_ok=True)
EMA_OUT = os.path.join("data", "ema_human_medicines.xlsx")
EFSA_OUT = os.path.join("data", "efsa_openfoodtox.xlsx")

def crawl_ema():
    url = "https://www.ema.europa.eu/en/documents/other/human-medicines-authorised.xlsx"
    r = requests.get(url)
    r.raise_for_status()
    with open(EMA_OUT, "wb") as f:
        f.write(r.content)
    print(f"[EMA] Saved medicines dataset to {EMA_OUT}")

def crawl_efsa():
    url = "https://zenodo.org/record/4274656/files/OpenFoodTox_v2.xlsx?download=1"
    r = requests.get(url)
    r.raise_for_status()
    with open(EFSA_OUT, "wb") as f:
        f.write(r.content)
    print(f"[EFSA] Saved OpenFoodTox dataset to {EFSA_OUT}")

if __name__ == "__main__":
    crawl_ema()
    crawl_efsa()

