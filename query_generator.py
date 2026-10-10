import csv
import json
import re
import unicodedata

INPUT_FILE = "data/brands_cleaned.csv"
OUTPUT_FILE = "kleniec.json"
OPTIONAL_THRESHOLD = 1

ALCOHOL_WORDS = [
    "vodka", "vodkas",
    "whisky", "whiskies",
    "whiskey", "whiskeys",
    "tequila", "tequilas",
    "mezcal", "mezcals",
    "cognac", "cognacs",
    "brandy", "brandies",
    "bourbon", "bourbons",
    "liqueur", "liqueurs",
    "vermouth", "vermouths",
    "champagne", "champagnes",
    "prosecco", "proseccos",
    "absinthe", "absinthes",
    "schnapps",
    "rum", "rums",
    "gin", "gins",
    "wine", "wines",
    "beer", "beers",
    "lager", "lagers",
    "liquor", "liquors",
    "cocktail", "cocktails",
    "alcohol", "alcoholic",
    "distillery", "distilleries",
    "distilled", "distilling",
]

OPTIONAL = [{"keyword": word, "mode": "m"} for word in ALCOHOL_WORDS]


def build_required(name):
    required = []
    phrase = []
    for word in re.findall(r"[a-z0-9']+", name):
        if word.endswith("'s"):
            phrase.append(word[:-2].replace("'", ""))
            required.append({"keyword": "-".join(phrase), "mode": "c"})
            phrase = []
        else:
            cleaned = word.replace("'", "")
            if cleaned:
                phrase.append(cleaned)
    if phrase:
        required.append({"keyword": "-".join(phrase), "mode": "m"})
    return required


def main():
    results = []
    seen = set()
    with open(INPUT_FILE, encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            required = build_required(row["brand_clean"])
            if not required:
                continue
            key = json.dumps(required)
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "id": row["original"],
                "required": required,
                "optional": OPTIONAL,
                "optionalThreshold": OPTIONAL_THRESHOLD,
            })
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump({"results": results}, file, ensure_ascii=False)

if __name__ == "__main__":
    main()