import json
import csv
from datetime import datetime

import requests
import boto3

BUCKET = "nbu-rates-sema-lab2"
API_URL = "https://bank.gov.ua/NBU_Exchange/exchange_site"
START, END = "20220101", "20221231"
CURRENCIES = ["usd", "eur"]

s3 = boto3.client("s3")

for cur in CURRENCIES:
    # 1. Отримання даних з API НБУ у форматі JSON
    url = (f"{API_URL}?start={START}&end={END}&valcode={cur}"
           f"&sort=exchangedate&order=asc&json")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    json_file = f"nbu_{cur}_2022.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 2. Конвертація JSON у CSV
    csv_file = f"nbu_{cur}_2022.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "currency", "rate"])
        for row in data:
            date = datetime.strptime(row["exchangedate"], "%d.%m.%Y").date()
            writer.writerow([date.isoformat(), row["cc"], row["rate_per_unit"]])

    # 3. Вивантаження CSV на S3
    s3.upload_file(csv_file, BUCKET, f"data/{csv_file}")
    print(f"{cur.upper()}: {len(data)} записів -> s3://{BUCKET}/data/{csv_file}")
