import pandas as pd
import unicodedata

df = pd.read_csv("data/brands_raw.csv")

df.rename(columns={"brand": "original"}, inplace=True)

def clean(text):
    text = str(text).lower()
    text_norm = unicodedata.normalize('NFKD', text)  
    text_uni = ''.join([c for c in text_norm if not unicodedata.combining(c)])  
    return text_uni

df['brand_clean'] = df['original'].apply(clean)
df.to_csv('data/brands_cleaned.csv', index=False, encoding='utf-8')