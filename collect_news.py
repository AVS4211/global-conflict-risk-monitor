import requests
import pandas as pd
from datetime import datetime
import os

API_KEY = "092d0f246afc464789fdc4d0ff3149a7"

url = "https://newsapi.org/v2/everything"

params = {
    "q": "war OR conflict OR military OR geopolitics",
    "language": "en",
    "sortBy": "publishedAt",
    "pageSize": 20,
    "apiKey": API_KEY
}

response = requests.get(url, params=params)
data = response.json()

articles_list = []

for article in data["articles"]:
    articles_list.append({
        "time_collected": datetime.now(),
        "title": article["title"],
        "description": article["description"],
        "source": article["source"]["name"]
    })

df = pd.DataFrame(articles_list)

# create data folder if not exists
os.makedirs("data", exist_ok=True)

file_path = "data/news_data.csv"

# append data
if os.path.exists(file_path):
    df.to_csv(file_path, mode="a", index=False, header=False)
else:
    df.to_csv(file_path, index=False)

print("✅ News collected and saved successfully!")
import time

while True:
    print("Collecting news...")
    response = requests.get(url, params=params)
    data = response.json()

    articles_list = []

    for article in data["articles"]:
        articles_list.append({
            "time_collected": datetime.now(),
            "title": article["title"],
            "description": article["description"],
            "source": article["source"]["name"]
        })

    df = pd.DataFrame(articles_list)
    df.to_csv(file_path, mode="a", index=False, header=False)

    print("✅ Updated!")
    time.sleep(10)  # every 10 minutes