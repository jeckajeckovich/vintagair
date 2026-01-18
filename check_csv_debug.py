import csv

with open("cities_map.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    print("Заголовки:", reader.fieldnames)
    for i, row in enumerate(reader):
        print(row)
        if i == 2:
            break
