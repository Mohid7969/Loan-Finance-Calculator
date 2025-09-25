import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

KIBOR_URL = "https://www.sbp.org.pk/ecodata/kibor_index.asp"
ECODATA_INDEX = "https://www.sbp.org.pk/ecodata/index2.asp"

def fetch_sbp_policy_rate():
    """Fetch SBP policy / base rate from SBP econ-data pages."""
    try:
        resp = requests.get(ECODATA_INDEX, timeout=15)
        text = resp.text
        soup = BeautifulSoup(text, "html.parser")
        plain_text = soup.get_text(" ", strip=True)
        m = re.search(r"Policy\s*Rate\s*([\d.]+)", plain_text, re.IGNORECASE)
        if m:
            return float(m.group(1))
    except Exception as e:
        print("Error fetching SBP rate:", e)
    return None

def fetch_kibor_rates():
    """Fetch KIBOR 3M & 6M (average of bid/offer)."""
    kb3 = kb6 = None
    try:
        resp = requests.get(KIBOR_URL, timeout=15)
        html = resp.text
        match3 = re.search(r"3-?M\s+([\d.]+)\s+([\d.]+)", html, re.IGNORECASE)
        match6 = re.search(r"6-?M\s+([\d.]+)\s+([\d.]+)", html, re.IGNORECASE)
        if match3:
            bid = float(match3.group(1))
            offer = float(match3.group(2))
            kb3 = (bid + offer) / 2.0
        if match6:
            bid = float(match6.group(1))
            offer = float(match6.group(2))
            kb6 = (bid + offer) / 2.0
    except Exception as e:
        print("Error fetching KIBOR:", e)
    return kb3, kb6

def main():
    sbp_rate = fetch_sbp_policy_rate() or 20.5
    kibor3m, kibor6m = fetch_kibor_rates()
    if kibor3m is None: kibor3m = 21.9
    if kibor6m is None: kibor6m = 22.1

    # Islamic Murabaha rate = KIBOR (6M) + 2% margin
    murabaha_rate = kibor6m + 2.0

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

if __name__ == "__main__":
    main()
