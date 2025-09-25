import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_sbp_policy_rate():
    """Fetch SBP base rate (Policy Rate)"""
    url = "https://www.sbp.org.pk/statistics/policy-rate"
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")
    
    # Example: Look for first number in table
    rate_text = soup.find("td").get_text(strip=True)
    return float(rate_text.replace("%", "").strip())

def fetch_kibor_rates():
    """Fetch KIBOR 3M and 6M rates"""
    url = "https://www.sbp.org.pk/statistics/kibor"
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.find_all("tr")
    kibor3m, kibor6m = None, None

    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) >= 3:
            if "3-Month" in cols[0]:
                kibor3m = float(cols[1].replace("%", ""))
            elif "6-Month" in cols[0]:
                kibor6m = float(cols[1].replace("%", ""))

    return kibor3m, kibor6m

def fetch_murabaha_rate():
    """Placeholder until SBP publishes Islamic Murabaha dataset"""
    # You can later replace this with actual SBP link for Islamic profit rates
    return 19.0

if __name__ == "__main__":
    try:
        sbp_rate = fetch_sbp_policy_rate()
    except Exception as e:
        print("Failed to fetch SBP rate:", e)
        sbp_rate = 20.5  # fallback default

    try:
        kibor3m, kibor6m = fetch_kibor_rates()
    except Exception as e:
        print("Failed to fetch KIBOR:", e)
        kibor3m, kibor6m = 21.9, 22.1  # fallback default

    try:
        murabaha_rate = fetch_murabaha_rate()
    except Exception as e:
        print("Failed to fetch Murabaha:", e)
        murabaha_rate = 19.0  # fallback default

    data = {
        "sbpRate": sbp_rate,
        "kibor3m": kibor3m,
        "kibor6m": kibor6m,
        "murabahaRate": murabaha_rate,
        "lastUpdated": datetime.utcnow().isoformat() + "Z"
    }

    with open("rates.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ rates.json updated:", data)
