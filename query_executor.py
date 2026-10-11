import csv
import json
import re

import requests

INPUT_FILE = "data/queries.json"
REVIEW_FILE = "data/review_urls.csv"
NOT_FOUND_FILE = "data/urls_not_found.csv"
ESTIMATOR_URL = "https://urlkeywords.ctpl.dev/keywordURLs"
TIMEOUT_SECONDS = 60
SOURCE_NAMES = ["source1", "source2", "source3", "source4", "source5"]


def load_queries():
    with open(INPUT_FILE, encoding="utf-8") as file:
        return json.load(file)["results"]


def build_payload(query):
    return {key: value for key, value in query.items() if key != "id"}


def clean_url(url):
    match = re.match(r"^\[.*\]\((.*)\)$", url)
    if match:
        return match.group(1)
    return url


def get_url_key(url):
    return re.sub(r"^(https?://)?(www\.)?", "", url)


def extract_urls(response_json):
    unique_urls = {}
    for source in response_json["sources"].values():
        for url in source["urls"]:
            url = clean_url(url)
            unique_urls.setdefault(get_url_key(url), url)
    return list(unique_urls.values())


def extract_source_counts(response_json):
    source_counts = {}
    for name in SOURCE_NAMES:
        source = response_json["sources"].get(name, {})
        source_counts[name] = source.get("quantity", 0)
    return source_counts


def run_query(query):
    response = requests.post(
        ESTIMATOR_URL,
        data=json.dumps(build_payload(query)),
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    response_json = response.json()
    return extract_urls(response_json), extract_source_counts(response_json)


def write_csv(path, fieldnames, rows, encoding="utf-8"):
    with open(path, "w", encoding=encoding, newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    queries = load_queries()
    found = []
    not_found = []

    for number, query in enumerate(queries, start=1):
        brand = query["id"]
        try:
            urls, source_counts = run_query(query)
        except Exception as error:
            print(f"[{number}/{len(queries)}] {brand}: ERROR {error}")
            continue

        if urls:
            row = {
                "brand": brand,
                "count": len(urls),
                "urls": json.dumps(urls),
                "decision": "",
            }
            row.update(source_counts)
            found.append(row)
        else:
            not_found.append({"brand": brand})
        print(f"[{number}/{len(queries)}] {brand}: {len(urls)} urls")

    review_columns = ["brand", "count", "urls"] + SOURCE_NAMES + ["decision"]
    write_csv(REVIEW_FILE, review_columns, found, encoding="utf-8-sig")
    write_csv(NOT_FOUND_FILE, ["brand"], not_found)
    print(f"Found: {len(found)}, not found: {len(not_found)}")


if __name__ == "__main__":
    main()