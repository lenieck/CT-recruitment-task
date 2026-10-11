import re
import unicodedata

import pandas as pd

INPUT_FILE = "data/brands_raw.csv"
OUTPUT_FILE = "data/brands_cleaned.csv"


def clean(text):
    text = str(text).lower()
    for sign in ["’", "‘", "′", "`", "´"]:
        text = text.replace(sign, "'")
    text = re.sub(r"\(.*?\)", " ", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    text = " ".join(text.split())
    return text


df = pd.read_csv(INPUT_FILE)
df["brand"] = df["brand"].apply(clean)
df = df[df["brand"] != ""]
df = df.drop_duplicates(subset=["brand"])
df = df[["brand"]]

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")