import requests
import csv
import time
from datetime import datetime, timedelta

API_URL = "https://booking.chukotavia.com/websky/json/company-search-variants"

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0"
}

START_DATE = datetime(2026, 1, 18)
END_DATE = datetime(2026, 2, 18)

SLEEP_BETWEEN_REQUESTS = 2.5  # защита от бана

def daterange(start, end):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)

def check_route(origin, destination, date_str):
    payload = {
        "searchGroupId": "standard",
        "segmentsCount": 1,
        "date[0]": date_str,
        "origin-city-code[0]": origin,
        "destination-city-code[0]": destination,
        "adultsCount": 1,
        "childrenCount": 0,
        "infantsWithSeatCount": 0,
        "infantsWithoutSeatCount": 0
    }

    try:
        r = requests.post(API_URL, data=payload, headers=HEADERS, timeout=15)
        if r.status_code != 200:
            return None

        data = r.json()
        if data.get("result") != "ok":
            return None

        flights = data.get("flights", [])
        prices = data.get("prices", [])

        if not flights or not prices:
            return None

        f = flights[0]["flights"][0]
        p = prices[0]

        return {
            "date": date_str,
            "flight_number": f["racenumber"],
            "origin": f["origincityName"],
            "destination": f["destinationcityName"],
            "departure": f["departuretime"],
            "arrival": f["arrivaltime"],
            "aircraft": f["airplaneName"],
            "price": p["price"],
            "available": p["flight_variants"][0]["direction"][0]["available"]
        }

    except Exception as e:
        print("Ошибка:", e)
        return None

def main():
    results = []

    with open("routes_known.csv", encoding="utf-8") as f:
        routes = list(csv.DictReader(f))

    for route in routes:
        print(f"\n▶ {route['origin_name']} → {route['destination_name']}")

        # для деревень проверяем ТОЛЬКО ближайшие 7 дней
        dates = list(daterange(START_DATE, END_DATE))
        if route["aircraft_group"] == "MI8":
            dates = dates[:7]

        for d in dates:
            date_str = d.strftime("%d.%m.%Y")
            print(f"  ⏳ {date_str}")

            result = check_route(
                route["origin_code"],
                route["destination_code"],
                date_str
            )

            if result:
                print("    ✔ НАЙДЕН")
                results.append(result)

            time.sleep(SLEEP_BETWEEN_REQUESTS)

    if results:
        with open("chukotavia_api_results.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=results[0].keys()
            )
            writer.writeheader()
            writer.writerows(results)

        print("\n✅ Готово: chukotavia_api_results.csv")
    else:
        print("\n❌ Рейсы не найдены")

if __name__ == "__main__":
    main()
