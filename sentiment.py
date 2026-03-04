import pandas as pd
from textblob import TextBlob
from datetime import datetime
import os

# ---------------- LOAD NEWS DATA ----------------

file_path = "data/news_data.csv"

if not os.path.exists(file_path):
    print("❌ No news data found")
    exit()

df = pd.read_csv(file_path)

# ---------------- CLEAN TEXT ----------------

df["title"] = df["title"].fillna("")
df["description"] = df["description"].fillna("")

df["text"] = df["title"] + " " + df["description"]

# ---------------- SENTIMENT FUNCTION ----------------

def get_sentiment(text):

    analysis = TextBlob(str(text))
    score = analysis.sentiment.polarity

    if score > 0.1:
        return "Positive", score
    elif score < -0.1:
        return "Negative", score
    else:
        return "Neutral", score

# ---------------- APPLY SENTIMENT ----------------

results = df["text"].apply(get_sentiment)

df["sentiment"] = results.apply(lambda x: x[0])
df["score"] = results.apply(lambda x: x[1])

# ---------------- SAVE SENTIMENT FILE ----------------

sentiment_file = "data/news_with_sentiment.csv"

os.makedirs("data", exist_ok=True)

df.to_csv(sentiment_file, index=False)

print("✅ Sentiment analysis completed!")

# ---------------- CALCULATE SENTIMENT PERCENTAGES ----------------

sentiment_counts = df["sentiment"].value_counts(normalize=True) * 100

positive_percent = sentiment_counts.get("Positive", 0)
neutral_percent = sentiment_counts.get("Neutral", 0)
negative_percent = sentiment_counts.get("Negative", 0)

print(f"Positive: {positive_percent:.2f}%")
print(f"Neutral: {neutral_percent:.2f}%")
print(f"Negative: {negative_percent:.2f}%")

# ---------------- RISK LEVEL ----------------

if negative_percent > 70:
    risk = "HIGH ⚠️"
elif negative_percent > 40:
    risk = "MEDIUM 🟡"
else:
    risk = "LOW 🟢"

print(f"Current Risk Level: {risk}")

# ---------------- SAVE TIME SERIES ----------------

history_file = "data/timeseries.csv"

history_row = pd.DataFrame([{
    "time": datetime.now(),
    "negative_percent": negative_percent
}])

# Append safely
if os.path.exists(history_file):

    existing = pd.read_csv(history_file)

    # prevent too many duplicate rows in same minute
    if len(existing) == 0 or abs(existing.iloc[-1]["negative_percent"] - negative_percent) > 0.1:

        history_row.to_csv(
            history_file,
            mode="a",
            index=False,
            header=False
        )

else:

    history_row.to_csv(
        history_file,
        index=False
    )

print("✅ Time-series data updated!")