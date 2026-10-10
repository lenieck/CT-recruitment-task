import csv
import json
import re

import requests

INPUT_FILE = "kleniec.json"
RESULTS_FILE = "estimator_results.csv"
NOT_FOUND_FILE = "urls_not_found.csv"
NO_DICTIONARY_FILE = "urls_without_dictionary.csv"
COMMON_WORDS_FILE = "common_words.csv"
ESTIMATOR_URL = "https://urlkeywords.ctpl.dev/keywordURLs"
TIMEOUT_SECONDS = 60

RUN_WITH_DICTIONARY = False
RUN_WITHOUT_DICTIONARY = True
TOP_WORDS_TO_PRINT = 100
IGNORED_WORDS = {"www", "com", "http", "https", "html", "htm", "php", "net", "org", "amp"}


def load_queries():
    with open(INPUT_FILE, encoding="utf-8") as file:
        return json.load(file)["results"]


def build_payload(query):
    return {key: value for key, value in query.items() if key != "id"}


def extract_urls(response_json):
    urls = []
    for source in response_json["sources"].values():
        urls.extend(source["urls"])
    return urls


def run_query(query):
    response = requests.post(
        ESTIMATOR_URL,
        data=json.dumps(build_payload(query)),
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return extract_urls(response.json())


def write_csv(path, fieldnames, rows):
    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_brand_words(query):
    words = set()
    for item in query["required"]:
        words.update(re.findall(r"[a-z0-9]+", item["keyword"]))
    return words


def get_url_words(url):
    return set(re.findall(r"[a-z]{3,}", url.lower())) - IGNORED_WORDS


def load_not_found_brands():
    with open(NOT_FOUND_FILE, encoding="utf-8", newline="") as file:
        return {row["brand"] for row in csv.DictReader(file)}


def run_with_dictionary(queries):
    found = []
    not_found = []

    for number, query in enumerate(queries, start=1):
        brand = query["id"]
        try:
            urls = run_query(query)
        except Exception as error:
            print(f"[{number}/{len(queries)}] {brand}: ERROR {error}")
            continue

        if urls:
            found.append({"brand": brand, "count": len(urls), "urls": json.dumps(urls)})
        else:
            not_found.append({"brand": brand})
        print(f"[{number}/{len(queries)}] {brand}: {len(urls)} urls")

    write_csv(RESULTS_FILE, ["brand", "count", "urls"], found)
    write_csv(NOT_FOUND_FILE, ["brand"], not_found)
    print(f"Found: {len(found)}, not found: {len(not_found)}")


def run_without_dictionary(queries):
    not_found_brands = load_not_found_brands()
    selected_queries = [query for query in queries if query["id"] in not_found_brands]

    found = []
    url_counter = {}
    brand_counter = {}

    for number, query in enumerate(selected_queries, start=1):
        brand = query["id"]
        try:
            urls = run_query({"id": brand, "required": query["required"]})
        except Exception as error:
            print(f"[{number}/{len(selected_queries)}] {brand}: ERROR {error}")
            continue

        print(f"[{number}/{len(selected_queries)}] {brand}: {len(urls)} urls")
        if not urls:
            continue

        found.append({"brand": brand, "count": len(urls), "urls": json.dumps(urls)})

        brand_words = get_brand_words(query)
        words_in_brand_urls = set()
        for url in urls:
            words = get_url_words(url) - brand_words
            words_in_brand_urls.update(words)
            for word in words:
                url_counter[word] = url_counter.get(word, 0) + 1
        for word in words_in_brand_urls:
            brand_counter[word] = brand_counter.get(word, 0) + 1

    sorted_words = sorted(
        url_counter,
        key=lambda word: (brand_counter[word], url_counter[word]),
        reverse=True,
    )
    word_rows = [
        {"word": word, "brands": brand_counter[word], "urls": url_counter[word]}
        for word in sorted_words
    ]

    write_csv(NO_DICTIONARY_FILE, ["brand", "count", "urls"], found)
    write_csv(COMMON_WORDS_FILE, ["word", "brands", "urls"], word_rows)

    print(f"Brands with urls without dictionary: {len(found)} of {len(selected_queries)}")
    print("Most common words (word: brands, urls):")
    for row in word_rows[:TOP_WORDS_TO_PRINT]:
        print(f"  {row['word']}: {row['brands']}, {row['urls']}")


def main():
    queries = load_queries()
    if RUN_WITH_DICTIONARY:
        run_with_dictionary(queries)
    if RUN_WITHOUT_DICTIONARY:
        run_without_dictionary(queries)


if __name__ == "__main__":
    main()