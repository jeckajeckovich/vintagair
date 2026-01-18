import csv

INPUT_FILE = "chukotavia_flights_clean.csv"
OUTPUT_FILE = "chukotavia_routes_clean.csv"

def is_valid_time(t):
    if not t:
        return False
    if ":" not in t:
        return False
    h, m = t.split(":")
    return h.isdigit() and m.isdigit() and 0 <= int(h) <= 23

routes = []

with open(INPUT_FILE, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        flight = row.get("flight_number", "").strip()
        from_city = row.get("from", "").strip()
        to_city = row.get("to", "").strip()

        if not flight or not from_city or not to_city:
            continue

        dep = row.get("departure", "").strip()
        arr = row.get("arrival", "").strip()

        if not flight or not from_city or not to_city:
            continue

        routes.append({
            "airline": row.get("airline", "ЧукотАВИА"),
            "flight_number": flight,
            "aircraft_type": row.get("aircraft_type", ""),
            "from_city": from_city,
            "to_city": to_city,
            "departure_time": dep,
            "arrival_time": arr,
            "months": row.get("raw", ""),
            "days_raw": row.get("raw", ""),
            "source": "official_schedule"
        })

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "airline",
            "flight_number",
            "aircraft_type",
            "from_city",
            "to_city",
            "departure_time",
            "arrival_time",
            "months",
            "days_raw",
            "source"
        ]
    )
    writer.writeheader()
    writer.writerows(routes)

print(f"Готово. Сохранено маршрутов: {len(routes)}")
print(f"Файл: {OUTPUT_FILE}")
