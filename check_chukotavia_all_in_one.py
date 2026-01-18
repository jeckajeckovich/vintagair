import requests
import csv
from datetime import datetime, timedelta
import time

API_URL = "https://booking.chukotavia.com/websky/json/company-search-variants"

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://booking.chukotavia.com",
    "Referer": "https://booking.chukotavia.com/websky/",
    "User-Agent": "Mozilla/5.0"
}

START_DATE = datetime(2026, 1, 19)
END_DATE   = datetime(2026, 2, 18)

OUTPUT = "chukotavia_api_results.csv"

# =====================================================
# ВСЕ МАРШРУТЫ — ЗДЕСЬ, КАК ТЫ ИХ ДАЛ
# =====================================================

ROUTES = [
    ("DYR","БНГ"),("DYR","ВГИ"),("DYR","ЗЛА"),("DYR","KPW"),("DYR","KVM"),
    ("DYR","PWE"),("DYR","PVS"),("DYR","ЭГТ"),

    ("БНГ","АЙО"),("БНГ","DYR"),("БНГ","АЮЙ"),("БНГ","БНГ"),("БНГ","БИЛ"),
    ("БНГ","БРЧ"),("БНГ","ВГИ"),("БНГ","ВРЧ"),("БНГ","ЗЛА"),("БНГ","ИЛИ"),
    ("БНГ","ИНЧ"),("БНГ","КЭТ"),("БНГ","KPW"),("БНГ","КОИ"),("БНГ","ЛМТ"),
    ("БНГ","GDX"),("БНГ","KVM"),("БНГ","МШД"),("БНГ","НЕШ"),("БНГ","НУГ"),
    ("БНГ","НУТ"),("БНГ","ООЛ"),("БНГ","ОСГ"),("БНГ","PWE"),("БНГ","PVS"),
    ("БНГ","УЧН"),("БНГ","СИК"),("БНГ","УЭН"),("БНГ","УЭЛ"),("БНГ","KHV"),
    ("БНГ","ЧУВ"),("БНГ","ЭГТ"),("БНГ","ЭНМ"),("БНГ","ЭНР"),("БНГ","ЯНА"),

    ("БИЛ","МШД"),

    ("БРЧ","КЭТ"),("БРЧ","KPW"),("БРЧ","ООЛ"),

    ("ВГИ","DYR"),("ВГИ","KVM"),

    ("ВРЧ","НУТ"),

    ("ЗЛА","DYR"),("ЗЛА","ИНЧ"),("ЗЛА","НЕШ"),("ЗЛА","PVS"),
    ("ЗЛА","СИК"),("ЗЛА","УЭН"),("ЗЛА","KHV"),("ЗЛА","ЭГТ"),
    ("ЗЛА","ЭНР"),("ЗЛА","ЯНА"),

    ("КЭТ","БРЧ"),("КЭТ","KPW"),("КЭТ","ООЛ"),

    ("KPW","DYR"),("KPW","АЮЙ"),("KPW","БРЧ"),("KPW","ИЛИ"),
    ("KPW","КЭТ"),("KPW","KPW"),("KPW","ООЛ"),("KPW","ОСГ"),
    ("KPW","PWE"),("KPW","KHV"),

    ("КОИ","УЭЛ"),

    ("GDX","DYR"),("GDX","БРЧ"),("GDX","КЭТ"),("GDX","ООЛ"),("GDX","PWE"),

    ("KVM","DYR"),("KVM","ВГИ"),("KVM","ЛМТ"),("KVM","KHV"),("KVM","ЧУВ"),

    ("НЕШ","ЗЛА"),("НЕШ","ЭНР"),

    ("НУГ","PVS"),("НУГ","ЭГТ"),("НУГ","ЭНМ"),

    ("НУТ","ВРЧ"),

    ("ООЛ","БРЧ"),("ООЛ","КЭТ"),("ООЛ","KPW"),("ООЛ","GDX"),

    ("PWE","АЙО"),("PWE","DYR"),("PWE","БИЛ"),("PWE","KPW"),
    ("PWE","GDX"),("PWE","МШД"),("PWE","УЧН"),("PWE","KHV"),

    ("PVS","DYR"),("PVS","ЗЛА"),("PVS","НУГ"),("PVS","СИК"),
    ("PVS","ЭГТ"),("PVS","ЭНМ"),("PVS","ЯНА"),

    ("СИК","ЗЛА"),("СИК","PVS"),("СИК","ЯНА"),

    ("УЭН","ИНЧ"),

    ("УЭЛ","КОИ"),

    ("KHV","АЙО"),("KHV","DYR"),("KHV","АЮЙ"),("KHV","БНГ"),
    ("KHV","БИЛ"),("KHV","БРЧ"),("KHV","ВГИ"),("KHV","ВРЧ"),
    ("KHV","ЗЛА"),("KHV","ИЛИ"),("KHV","ИНЧ"),("KHV","КЭТ"),
    ("KHV","KPW"),("KHV","КОИ"),("KHV","ЛМТ"),("KHV","GDX"),
    ("KHV","KVM"),("KHV","МШД"),("KHV","НЕШ"),("KHV","НУГ"),
    ("KHV","ООЛ"),("KHV","PWE"),("KHV","PVS"),("KHV","УЧН"),
    ("KHV","СИК"),("KHV","УЭН"),("KHV","УЭЛ"),("KHV","ЧУВ"),
    ("KHV","ЭГТ"),("KHV","ЭНМ"),("KHV","ЭНР"),("KHV","ЯНА"),

    ("ЧУВ","ЛМТ"),

    ("ЭГТ","DYR"),("ЭГТ","ВРЧ"),("ЭГТ","ЗЛА"),("ЭГТ","КОИ"),
    ("ЭГТ","МШД"),("ЭГТ","НЕШ"),("ЭГТ","НУГ"),("ЭГТ","НУТ"),
    ("ЭГТ","PVS"),("ЭГТ","УЭЛ"),("ЭГТ","KHV"),("ЭГТ","ЭГТ"),
    ("ЭГТ","ЭНМ"),("ЭГТ","ЭНР"),

    ("ЭНМ","НУГ"),("ЭНМ","PVS"),("ЭНМ","ЭГТ"),("ЭНМ","ЭНМ"),

    ("ЭНР","ЗЛА"),("ЭНР","НЕШ"),

    ("ЯНА","ЗЛА"),("ЯНА","PVS"),("ЯНА","СИК"),("ЯНА","ЯНА"),
]

# =====================================================

def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def check_route(date, origin, dest):
    payload = {
        "searchGroupId": "standard",
        "segmentsCount": "1",
        "date[0]": date,
        "origin-city-code[0]": origin,
        "destination-city-code[0]": dest,
        "adultsCount": "1",
        "childrenCount": "0",
        "infantsWithSeatCount": "0",
        "infantsWithoutSeatCount": "0"
    }

    r = requests.post(API_URL, headers=HEADERS, data=payload, timeout=20)
    if r.status_code != 200:
        return []

    data = r.json()
    flights = data.get("flights", [])
    prices = data.get("prices", [])

    price_map = {}
    for p in prices:
        for v in p.get("flight_variants", []):
            for d in v.get("direction", []):
                for fid in d.get("flights", []):
                    price_map[str(fid)] = {
                        "price": p.get("price"),
                        "available": d.get("available")
                    }

    results = []
    for chain in flights:
        for f in chain.get("flights", []):
            fid = str(f.get("id"))
            info = price_map.get(fid, {})
            results.append({
                "date": date,
                "origin": origin,
                "destination": dest,
                "flight_number": f.get("racenumber"),
                "departure": f.get("departuretime"),
                "arrival": f.get("arrivaltime"),
                "aircraft": f.get("airplaneName"),
                "price": info.get("price"),
                "available": info.get("available")
            })
    return results


def main():
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date","origin","destination",
                "flight_number","departure","arrival",
                "aircraft","price","available"
            ]
        )
        writer.writeheader()

        for origin, dest in ROUTES:
            print(f"▶ {origin} → {dest}")
            for d in daterange(START_DATE, END_DATE):
                date_str = d.strftime("%d.%m.%Y")
                rows = check_route(date_str, origin, dest)
                for r in rows:
                    writer.writerow(r)
                time.sleep(0.6)

    print("✅ ГОТОВО:", OUTPUT)


if __name__ == "__main__":
    main()
