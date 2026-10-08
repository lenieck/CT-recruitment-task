import requests
from bs4 import BeautifulSoup
import pandas as pd

page_number = 1
brands_list = list()

while True:
    url = f'https://boozesip.com/brands/page/{page_number}/'
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html.parser')

    content = soup.find_all('div', class_='brand-card')
    if not content:
            break

    for card in content:
        if card:
            brand_name = card.find('h3')
            if brand_name:
                brands_list.append(brand_name.text.strip()) 
    page_number += 1

df = pd.DataFrame(brands_list, columns=["brand"])
df.to_csv('data/brands_raw.csv', index=False, encoding='utf-8')
