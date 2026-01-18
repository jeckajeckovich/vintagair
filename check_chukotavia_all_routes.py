import csv
import requests
import time
from datetime import datetime, timedelta

API_URL = "https://booking.chukotavia.com/websky/json/company-search-variants"

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

START_DATE = datetime(2026, 1, 19)
END_DATE = datetime(2026, 2, 18)

ROUTES = {
    "DYR": ["BNG", "VGI", "ZLA", "KPW", "KVM", "PWE", "PVS", "EGT"],
    "BNG": ["DYR", "PWE", "PVS"],
    "PVS": ["DYR", "ZLA", "EGT"],
    "KPW": ["DYR", "PWE"],
    "PWE": ["DYR", "KPW"],
    "ZLA": ["DYR", "PVS"],
    "EGT": ["DYR", "PVS"]
}

def load_cities():
    cities = {}
    with open("cities_map.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cities[row["code"].strip()] = row["city_id"].strip()
    return cities

def daterange(start, end):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)

def check_route(date, origin, destination):
    payload = {
        "searchGroupId": "standard",
        "segmentsCount": "1",
        "date[0]": date.strftime("%d.%m.%Y"),
        "origin-city-code[0]": origin,
        "destination-city-code[0]": destination,
        "adultsCount": "1",
        "childrenCount": "0",
        "infantsWithSeatCount": "0",
        "infantsWithoutSeatCount": "0",
    }

    r = requests.post(API_URL, headers=HEADERS, data=payload, timeout=20)
    if r.status_code != 200:
        return []

    data = r.json()
    results = []

    for chain in data.get("flights", []):
        for f in chain.get("flights", []):
            price = None
            avail = None

            for p in data.get("prices", []):
                for d in p.get("flight_variants", []):
                    for dir in d.get("direction", []):
                        if str(f["id"]) in dir.get("flights", []):
                            price = p.get("price")
                            avail = dir.get("available")

            results.append({
                "date": date.strftime("%d.%m.%Y"),
                "flight_number": f.get("racenumber"),
                "origin": f.get("origincity"),
                "destination": f.get("destinationcity"),
                "departure": f.get("departuretime"),
                "arrival": f.get("arrivaltime"),
                "aircraft": f.get("airplaneName"),
                "price": price,
                "available": avail
            })

    return results

def main():
    print("▶ Загрузка городов...")
    cities = load_cities()

    out = []
    total_checks = 0

    for origin, dests in ROUTES.items():
        for dest in dests:
            if origin not in cities or dest not in cities:
                continue

            for date in daterange(START_DATE, END_DATE):
                total_checks += 1
                print(f"Проверка {origin} → {dest} {date.strftime('%d.%m.%Y')}")
                try:
                    res = check_route(date, origin, dest)
                    out.extend(res)
                    time.sleep(1.2)  # анти-бан
                except Exception as e:
                    print("Ошибка:", e)

    print(f"\n✔ Проверок: {total_checks}")
    print(f"✔ Найдено рейсов: {len(out)}")

    if out:
        with open("chukotavia_api_results.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=out[0].keys())
            writer.writeheader()
            writer.writerows(out)

        print("💾 Сохранено: chukotavia_api_results.csv")
    else:
        print("❗ Ничего не найдено")

if __name__ == "__main__":
    main()
