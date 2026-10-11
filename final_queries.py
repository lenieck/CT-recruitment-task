import csv
import json

QUERIES_FILE = "data/queries.json"
REVIEW_FILE = "data/review_urls.csv"
OUTPUT_FILE = "data/kleniec.json"


def load_good_brands():
    good_brands = set()
    with open(REVIEW_FILE, encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            if row["decision"].strip() == "":
                good_brands.add(row["brand"])
    return good_brands


def main():
    good_brands = load_good_brands()

    with open(QUERIES_FILE, encoding="utf-8") as file:
        queries = json.load(file)["results"]

    filtered_queries = []
    for query in queries:
        if query["id"] in good_brands:
            filtered_queries.append(query)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump({"results": filtered_queries}, file, ensure_ascii=False)

    print(f"Saved {len(filtered_queries)} of {len(queries)} queries")


if __name__ == "__main__":
    main()