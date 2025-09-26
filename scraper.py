import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

KIBOR_URL = "https://www.sbp.org.pk/ecodata/kibor_index.asp"
ECODATA_KIBOR = KIBOR_URL
ECODATA_INDEX = "https://www.sbp.org.pk/ecodata/kibor_index.asp"  # SBP shows base policy rate on same page

def fetch_sbp_policy_rate(soup):
    # The Policy Rate text appears near top of the page, e.g. “SBP Policy Rate 11.00% p.a.”
    # Search for “SBP Policy Rate” in text
    text = soup.get_text(" ", strip=True)
    m = re.search(r"SBP\s*Policy\s*Rate\s*([\d.]+)\s*%?", text, re.IGNORECASE)
    if m:
        try:
            return float(m.group(1))
        except:
            pass
    return None

def fetch_kibor_rates(soup):
    # Find rows with "3-M" or "3-M" and "6-M"
    kibor3 = None
    kibor6 = None

    # Find the table containing “KIBOR” labels
    table = None
    # Basic find: find any <table> element that has "3-M" or "3-M" in its text
    for tbl in soup.find_all("table"):
        if "3-M" in tbl.get_text() or "3-M" in tbl.get_text():
            table = tbl
            break

    if table:
        for tr in table.find_all("tr"):
            cols = [td.get_text(" ", strip=True) for td in tr.find_all("td")]
            if len(cols) >= 3:
                # The first column is the tenor
                tenor = cols[0].strip().lower()
                if re.match(r"3[-\u2011-]?m", tenor):  # matches "3-M", "3-M"
                    try:
                        bid = float(cols[1])
                        offer = float(cols[2])
                        kibor3 = (bid + offer) / 2.0
                    except:
                        pass
                elif re.match(r"6[-\u2011-]?m", tenor):
                    try:
                        bid = float(cols[1])
                        offer = float(cols[2])
                        kibor6 = (bid + offer) / 2.0
                    except:
                        pass

    return kibor3, kibor6

def main():
    try:
        resp = requests.get(ECODATA_KIBOR, timeout=15)
        resp.raise_for_status()
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")

        sbp_rate = fetch_sbp_policy_rate(soup)
        kibor3m, kibor6m = fetch_kibor_rates(soup)

    except Exception as e:
        print("Error fetching KIBOR page:", e)
        sbp_rate, kibor3m, kibor6m = None, None, None

    # Fallback defaults
    if sbp_rate is None:
        sbp_rate = 20.5
    if kibor3m is None:
        kibor3m = 21.9
    if kibor6m is None:
        kibor6m = 22.1

    # Murabaha: you can make Murabaha = sbp_rate + margin (e.g. +1%)
    margin = 1.0  # change margin if you want
    murabaha_rate = round(sbp_rate + margin, 2)

    data = {
        "sbpRate": sbp_rate,
        "kibor3m": round(kibor3m, 2),
        "kibor6m": round(kibor6m, 2),
        "murabahaRate": murabaha_rate,
        "lastUpdated": datetime.utcnow().isoformat() + "Z"
    }

    with open("rates.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Updated rates:", data)

if __name__ == "__main__":
    main()

    with open("rates.json", "w") as f:
        json.dump(data, f, indent=2)

    print("✅ Rates updated:", data)
