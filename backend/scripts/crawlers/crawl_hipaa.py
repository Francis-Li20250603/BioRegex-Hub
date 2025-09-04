import requests, csv, os
from bs4 import BeautifulSoup

OUT = os.path.join("data", "hipaa_breaches.csv")
os.makedirs("data", exist_ok=True)

def crawl_hipaa():
    url = "https://ocrportal.hhs.gov/ocr/breach/breach_report.jsf"
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Placeholder: HIPAA portal is JS-heavy; real scrape would need Selenium.
    # For demo, just output the HTML snapshot.
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        f.write(r.text)

    print(f"[HIPAA] Snapshot saved to {OUT}")

if __name__ == "__main__":
    crawl_hipaa()
