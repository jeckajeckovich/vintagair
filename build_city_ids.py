import requests
import csv
import time

API_AUTOCOMPLETE = "https://booking.chukotavia.com/api/autocomplete"

CODES = set()

# берем коды из routes_master.csv
with open("routes_master.csv", encoding="utf-8") as f:
    for line in f:
        if "→" in line:
            a, b = line.strip().split("→")
            CODES.add(a.strip())
            CODES.add(b.strip())

def get_city_id(code):
    r = requests.get(API_AUTOCOMPLETE, params={"term": code}, verify=False, timeout=10)
    r.raise_for_status()
    data = r.json()
    for item in data:
        if item.get("code") == code:
            return item["id"], item["name"]
    return None, None

rows = []

for code in sorted(CODES):
    try:
        city_id, name = get_city_id(code)
        print(code, "→", city_id)
        if city_id:
            rows.append({
                "code": code,
                "city_id": city_id,
                "name": name
            })
        time.sleep(0.3)
    except Exception as e:
        print("ERROR", code, e)

with open("cities_map.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["code", "city_id", "name"])
    writer.writeheader()
    writer.writerows(rows)

print("ГОТОВО → cities_map.csv")
