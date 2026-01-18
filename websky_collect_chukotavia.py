import requests
import csv
from datetime import datetime, timedelta
import time

# ================= НАСТРОЙКИ =================

BASE_URL = "https://booking.chukotavia.com/websky/json/company-search-variants"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Origin": "https://booking.chukotavia.com",
    "Referer": "https://booking.chukotavia.com/websky/",
    "User-Agent": "Mozilla/5.0",
}

OUTPUT_CSV = "chukotavia_websky_flights_until_18_02_2026.csv"

START_DATE = datetime.today()
END_DATE = datetime(2026, 2, 18)

REQUEST_DELAY = 1.2  # секунд между запросами

# ================= АЭРОПОРТЫ =================
# ВСЕ КОДЫ: IATA + локальные (как на сайте)

AIRPORT_CODES = {
    "Анадырь": "DYR",
    "Провидения": "PVS",
    "Певек": "PWE",
    "Кепервеем": "KPW",
    "Марково": "KVM",
    "Беринговский": "БНГ",
    "Ваеги": "ВГИ",
    "Биллингс": "БИЛ",
    "Бургachan": "БРЧ",
    "Ванкарем": "ВРЧ",
    "Залив Лаврентия": "ЗЛА",
    "Каэтын": "КЭТ",
    "Конергино": "КОИ",
    "Магадан": "GDX",
    "Нешкан": "НЭШ",
    "Нутепельмен": "НУТ",
    "Омолон": "ООЛ",
    "Сиреники": "СИК",
    "Уэлен": "УЭН",
    "Уэлькаль": "УЭЛ",
    "Хабаровск": "KHV",
    "Чуванское": "ЧУВ",
    "Эгвекинот Залив Креста": "ЭГТ",
    "Энмелен": "ЭНМ",
    "Энурмино": "ЭНР",
    "Янракыннот": "ЯНА",
}

# ================= ВСПОМОГАТЕЛЬНОЕ =================

def daterange(start, end):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)

def post_search(origin, destination, date_str):
    payload = {
        "searchGroupId": "standard",
        "segmentsCount": 1,
        "date[0]": date_str,
        "origin-city-code[0]": origin,
        "destination-city-code[0]": destination,
        "adultsCount": 1,
        "childrenCount": 0,
        "infantsWithSeatCount": 0,
        "infantsWithoutSeatCount": 0,
    }

    response = requests.post(
        BASE_URL,
        headers=HEADERS,
        data=payload,
        timeout=30,
        verify=False
    )

    if response.status_code != 200:
        return None

    return response.json()

# ================= ОСНОВНАЯ ЛОГИКА =================

def main():
    results = []
    seen = set()

    print("🚀 Старт сбора рейсов Чукотавиа")

    try:
        for date in daterange(START_DATE, END_DATE):
            date_str = date.strftime("%d.%m.%Y")
            print(f"\n📅 Дата: {date_str}")

            for origin_name, origin_code in AIRPORT_CODES.items():
                for dest_name, dest_code in AIRPORT_CODES.items():

                    if origin_code == dest_code:
                        continue

                    print(f"  ✈️ {origin_code} → {dest_code}")

                    data = post_search(origin_code, dest_code, date_str)
                    time.sleep(REQUEST_DELAY)

                    if not data or data.get("result") != "ok":
                        continue

                    flights = data.get("flights", [])
                    prices = data.get("prices", [])

                    if not flights or not prices:
                        continue

                    price_info = prices[0]
                    price = price_info.get("price")
                    currency = price_info.get("currency")

                    for chain in flights:
                        for f in chain.get("flights", []):

                            key = (
                                date_str,
                                f["racenumber"],
                                f["originport"],
                                f["destinationcity"],
                            )

                            if key in seen:
                                continue

                            seen.add(key)

                            results.append({
                                "date": date_str,
                                "flight_number": f["carrier"] + " " + f["racenumber"],
                                "origin": f["originport"],
                                "destination": f["destinationcity"],
                                "departure": f["departuretime"],
                                "arrival": f["arrivaltime"],
                                "aircraft": f["airplaneName"],
                                "price": price,
                                "currency": currency,
                                "available": price_info["flight_variants"][0]["direction"][0]["available"]
                            })

                            print("    ✅ НАЙДЕН РЕЙС")

    except KeyboardInterrupt:
        print("\n⛔ Остановлено пользователем")

    # ================= СОХРАНЕНИЕ =================

    if results:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=results[0].keys()
            )
            writer.writeheader()
            writer.writerows(results)

        print(f"\n💾 Сохранено рейсов: {len(results)}")
        print(f"📄 Файл: {OUTPUT_CSV}")
    else:
        print("\n😕 Рейсов не найдено")

# ================= ЗАПУСК =================

if __name__ == "__main__":
    main()
