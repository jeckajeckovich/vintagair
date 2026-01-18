import csv
import re

INPUT_FILE = "chukotavia_flights_raw.csv"
OUTPUT_FILE = "chukotavia_flights_clean.csv"


def parse_flight(raw):
    parts = raw.split("|")
    if len(parts) < 2:
        return None

    text = raw

    # номер рейса
    flight_number = None
    m = re.search(r"(АД\s*\d+)", text)
    if m:
        flight_number = m.group(1)

    # маршрут
    route_from = None
    route_to = None
    m = re.search(r"([А-ЯЁ\-]+)\s*-\s*([А-ЯЁ\-]+)", text)
    if m:
        route_from = m.group(1).title()
        route_to = m.group(2).title()

    # время
    dep = None
    arr = None
    m = re.search(r"(\d{3,4})\s+(\d{3,4})", text)
    if m:
        dep = m.group(1)
        arr = m.group(2)
        dep = dep[:-2] + ":" + dep[-2:]
        arr = arr[:-2] + ":" + arr[-2:]

    return {
        "flight_number": flight_number,
        "from": route_from,
        "to": route_to,
        "departure": dep,
        "arrival": arr,
        "raw": raw
    }


def main():
    cleaned = []

    with open(INPUT_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            parsed = parse_flight(row["raw_data"])
            if parsed:
                parsed["airline"] = row["airline"]
                parsed["aircraft_type"] = row["aircraft_type"]
                cleaned.append(parsed)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "airline",
                "aircraft_type",
                "flight_number",
                "from",
                "to",
                "departure",
                "arrival",
                "raw"
            ]
        )
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"Готово. Сохранено рейсов: {len(cleaned)}")
    print(f"Файл: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
