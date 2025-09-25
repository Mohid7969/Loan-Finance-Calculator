import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

# SBP website for policy rate (base rate)
SBP_URL = "https://www.sbp.org.pk"

def fetch_rates():
    # Fetch SBP policy rate (base rate)
    policy_rate = 20.5  # fallback
    kibor_3m = 21.9     # fallback
    kibor_6m = 22.1     # fallback
    murabaha = 19.0     # fallback

    try:
        # Example scraping (needs real endpoint on SBP site)
        resp = requests.get("https://www.sbp.org.pk/ecodata/PolicyRate.asp")
        soup = BeautifulSoup(resp.text, "html.parser")
        # Assume policy rate appears in first <td>
        rate_text = soup.find("td").text.strip()
        policy_rate = float(rate_text)
    except Exception as e:
        print("Error fetching SBP Policy Rate:", e)

    # Create JSON data
    data = {
        "sbpRate": policy_rate,
        "kibor3m": kibor_3m,
        "kibor6m": kibor_6m,
        "murabahaRate": murabaha,
        "lastUpdated": datetime.utcnow().isoformat()
    }

    # Save to rates.json
    with open("rates.json", "w") as f:
        json.dump(data, f, indent=2)

    print("rates.json updated:", data)

if __name__ == "__main__":
    fetch_rates()
