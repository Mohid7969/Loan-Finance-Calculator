# scraper.py
import requests, re, json
from bs4 import BeautifulSoup
from datetime import datetime

KIBOR_URL = "https://www.sbp.org.pk/ecodata/kibor_index.asp"
ECODATA_INDEX = "https://www.sbp.org.pk/ecodata/index2.asp"

def fetch_policy_rate():
    try:
        r = requests.get(ECODATA_INDEX, timeout=15)
        text = r.text
        # Try a few patterns
        m = re.search(r'Policy\s*Rate[^0-9\n\r]*([\d.]+)', text, re.I)
        if m:
            return float(m.group(1))
        m2 = re.search(r'SBP\s*Policy\s*Rate[^0-9\n\r]*([\d.]+)', text, re.I)
        if m2:
            return float(m2.group(1))
    except Exception as e:
        print("policy fetch error:", e)
    return None

def fetch_kibor():
    kibor3 = None
    kibor6 = None
    try:
        r = requests.get(KIBOR_URL, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")

        # 1) Table scan approach (preferred)
        for tr in soup.find_all("tr"):
            cols = [td.get_text(" ", strip=True) for td in tr.find_all(["td","th"])]
            if not cols: 
                continue
            first = cols[0].lower()
            # Normalize text to catch different labels
            if re.search(r'\b3[-\s]?m(?:onth)?\b', first, re.I) and len(cols) >= 2:
                # find numeric values in the rest of the row
                nums = re.findall(r'[\d.]+', " ".join(cols[1:]))
                if nums:
                    bid = float(nums[0])
                    offer = float(nums[1]) if len(nums) > 1 else bid
                    kibor3 = (bid + offer) / 2.0
            if re.search(r'\b6[-\s]?m(?:onth)?\b', first, re.I) and len(cols) >= 2:
                nums = re.findall(r'[\d.]+', " ".join(cols[1:]))
                if nums:
                    bid = float(nums[0])
                    offer = float(nums[1]) if len(nums) > 1 else bid
                    kibor6 = (bid + offer) / 2.0
            if kibor3 is not None and kibor6 is not None:
                break

        # 2) Fallback: regex on whole page
        if kibor3 is None or kibor6 is None:
            text = soup.get_text(" ", strip=True)
            m3 = re.search(r'3-?M(?:onth)?[^\d\n\r]*([\d.]+)[^\d\n\r]*([\d.]+)', text, re.I)
            m6 = re.search(r'6-?M(?:onth)?[^\d\n\r]*([\d.]+)[^\d\n\r]*([\d.]+)', text, re.I)
            if m3 and kibor3 is None:
                kibor3 = (float(m3.group(1)) + float(m3.group(2))) / 2.0
            if m6 and kibor6 is None:
                kibor6 = (float(m6.group(1)) + float(m6.group(2))) / 2.0
    except Exception as e:
        print("kibor fetch error:", e)

    return kibor3, kibor6

def main():
    sbp = fetch_policy_rate() or 20.5
    k3, k6 = fetch_kibor()
    k3 = k3 if k3 is not None else 21.9
    k6 = k6 if k6 is not None else 22.1

    # Murabaha rule: KIBOR 6M + 2% margin (adjustable)
    murabaha = round(k6 + 2.0, 2) if k6 is not None else 19.0

    data = {
        "sbpRate": round(float(sbp), 2),
        "kibor3m": round(float(k3), 2),
        "kibor6m": round(float(k6), 2),
        "murabahaRate": murabaha,
        "lastUpdated": datetime.utcnow().isoformat() + "Z"
    }

    with open("rates.json", "w") as f:
        json.dump(data, f, indent=2)

    print("Updated rates.json:", data)

if __name__ == "__main__":
    main()
