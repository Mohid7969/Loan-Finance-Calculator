import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# --- Fetch SBP Policy Rate ---
def fetch_sbp_rate():
    url = "https://www.sbp.org.pk/statistics/policy-rate.asp"
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    # Look for a table cell with % sign
    for td in soup.find_all("td"):
        text = td.get_text(strip=True).replace("%", "")
        try:
            val = float(text)
            if 5 < val < 30:  # sanity check range
                return val
        except:
            continue
    return None

# --- Fetch KIBOR 3M & 6M ---
def fetch_kibor_rates():
    url = "https://www.sbp.org.pk/reports/kibor.asp"
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    kibor3m, kibor6m = None, None

    # Search all rows for 3-Month and 6-Month values
    for row in soup.find_all("tr"):
        cols = [c.get_text(strip=True).replace("%", "") for c in row.find_all("td")]
        if not cols:
            continue

        if "3" in row.get_text():
            for c in cols:
                try:
                    val = float(c)
                    if 5 < val < 30:
                        kibor3m = val
                        break
                except:
                    continue

        if "6" in row.get_text():
            for c in cols:
                try:
                    val = float(c)
                    if 5 < val < 30:
                        kibor6m = val
                        break
                except:
                    continue

    return kibor3m, kibor6m

# --- Fetch Murabaha Rate (derived for now) ---
def fetch_murabaha_rate(sbp_rate, kibor3m, kibor6m):
    """
    Since SBP doesn’t publish a single Murabaha rate,
    we approximate:
    - Use KIBOR 3M if available, else KIBOR 6M
    - Add a 0.5% Islamic financing margin
    """
    base = kibor3m or kibor6m or sbp_rate
    if base:
        return round(base + 0.5, 2)
    return None

if __name__ == "__main__":
    sbp_rate = fetch_sbp_rate()
    kibor3m, kibor6m = fetch_kibor_rates()
    murabaha_rate = fetch_murabaha_rate(sbp_rate, kibor3m, kibor6m)

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

    with open("rates.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Rates updated:", data)
