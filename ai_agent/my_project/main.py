# 간단한 데이터 정리 스크립트
import csv
from utils import clean_text

INPUT_FILE = "data.csv"
OUTPUT_FILE = "output.csv"

def main():
    with open(INPUT_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]

    for row in rows:
        row["name"] = clean_text(row.get("name", ""))
        row["memo"] = clean_text(row.get("memo", ""))

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"완료: {len(rows)}개 행 처리됨")

if __name__ == "__main__":
    main()
