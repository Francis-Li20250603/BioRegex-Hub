import requests, os

os.makedirs("data", exist_ok=True)
EMA_OUT = os.path.join("data", "ema_medicines.csv")
EFSA_OUT = os.path.join("data", "efsa_openfoodtox.xlsx")

def crawl_ema():
    # EMA medicine datasets are downloadable CSVs
    url = "https://www.ema.europa.eu/documents/other/medicines-data.csv"
    r = requests.get(url)
    r.raise_for_status()
    with open(EMA_OUT, "wb") as f:
        f.write(r.content)
    print(f"[EMA] Saved medicine dataset to {EMA_OUT}")

def crawl_efsa():
    url = "https://zenodo.org/record/4274656/files/OpenFoodTox_v2.xlsx"  # EFSA public toxicology
    r = requests.get(url)
    r.raise_for_status()
    with open(EFSA_OUT, "wb") as f:
        f.write(r.content)
    print(f"[EFSA] Saved OpenFoodTox to {EFSA_OUT}")

if __name__ == "__main__":
    crawl_ema()
    crawl_efsa()
