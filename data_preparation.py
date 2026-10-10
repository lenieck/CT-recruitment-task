import re
import unicodedata
import pandas as pd

df = pd.read_csv("data/brands_raw.csv")
df = df.rename(columns={"brand": "original"})


def clean(text):
    text = str(text).lower()
    for sign in ["’", "‘", "′", "`", "´"]:
        text = text.replace(sign, "'")
    text = re.sub(r"\(.*?\)", " ", text)
    text = unicodedata.normalize("NFKD", text)
    text = "".join([c for c in text if not unicodedata.combining(c)])
    text = " ".join(text.split())
    return text


df["brand_clean"] = df["original"].apply(clean)
df = df[df["brand_clean"] != ""]
df = df.drop_duplicates(subset=["brand_clean"])

df.to_csv("data/brands_cleaned.csv", index=False, encoding="utf-8")
