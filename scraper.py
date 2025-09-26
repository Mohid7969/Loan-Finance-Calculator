import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_sbp_rate():
    # Example SBP page (adjust if SBP changes link)
    url = "https://www.sbp.org.pk/statistics/policy-rate.asp"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    # Look for the first number in the page (SBP policy rate)
    text = soup.get_text()
    for word in text.split():
        try:
            val = float(word.replace("%", ""))
            if 5 < val < 30:  # sanity check
                return val
        except:
            continue
    return None

def fetch_kibor_rates():
    url = "https://www.sbp.org.pk/reports/kibor.asp"  # Example page (replace with actual KIBOR source)
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    kibor3m, kibor6m = None, None

    # Try to find numbers in table text
    text = soup.get_text().split()
    for i, word in enumerate(text):
        try:
            val = float(word.replace("%", ""))
            if "3" in text[i-1]:
                kibor3m = val
            if "6" in text[i-1]:
                kibor6m = val
        except:
            continue

    return kibor3m, kibor6m

def fetch_murabaha_rate(sbp_rate):
    # For now, approximate Murabaha = SBP rate + 0.5%
    if sbp_rate:
        return round(sbp_rate + 0.5, 2)
    return None

if __name__ == "__main__":
    sbp_rate = fetch_sbp_rate()
    kibor3m, kibor6m = fetch_kibor_rates()
    murabaha_rate = fetch_murabaha_rate(sbp_rate)

    data = {
        "sbpRate": sbp_rate,
        "kibor3m": kibor3m,
        "kibor6m": kibor6m,
        "murabahaRate": murabaha_rate,
        "lastUpdated": datetime.utcnow().isoformat()
    }

    with open("rates.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Rates updated:", data)
