import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from textblob import TextBlob
import pandas as pd
import numpy as np
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from forecast import get_forecast

# ---------------- AUTO REFRESH ----------------
st_autorefresh(interval=60000, key="refresh")

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Global Conflict Risk Monitor",
    layout="wide"
)

# ---------------- UI STYLE ----------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(180deg,#0b1a2a,#09121c,#060b12);
    color:white;
    font-family: 'Segoe UI', sans-serif;
}

.main-title {
    text-align:center;
    font-size:48px;
    font-weight:700;
}

.sub-title {
    text-align:center;
    color:#9aa4af;
    margin-bottom:30px;
}

.panel {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(14px);
    border-radius:15px;
    padding:20px;
    border:1px solid rgba(255,255,255,0.08);
    box-shadow:0 0 20px rgba(0,0,0,0.4);
}

.news-box {
    background:#162433;
    padding:12px;
    margin-bottom:10px;
    border-radius:10px;
}

.sentiment {
    text-align:center;
    padding:30px;
    border-radius:15px;
    font-weight:bold;
    color:white;
}

.pos { background: linear-gradient(135deg,#1f7a45,#2ecc71); }
.neu { background: linear-gradient(135deg,#a67c00,#f1c40f); }
.neg { background: linear-gradient(135deg,#7a1f1f,#e74c3c); }

.emoji { font-size:60px; }

.risk-high {
    background: linear-gradient(135deg,#5a0000,#ff2e2e);
    padding:40px;
    border-radius:18px;
    text-align:center;
    font-size:32px;
    font-weight:bold;
    box-shadow:0 0 25px red;
}

.risk-medium {
    background: linear-gradient(135deg,#7a5a00,#ffb300);
    padding:40px;
    border-radius:18px;
    text-align:center;
    font-size:32px;
    font-weight:bold;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown("<div class='main-title'>🌍 Global Conflict Risk Monitor</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Real-Time News • Sentiment Analysis • Conflict Forecast</div>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
if os.path.exists("data/news_data.csv"):
    news = pd.read_csv("data/news_data.csv")
else:
    news = pd.DataFrame(columns=["title","description","source"])

if os.path.exists("data/timeseries.csv"):
    ts = pd.read_csv("data/timeseries.csv")
else:
    ts = pd.DataFrame({"negative_percent":[10,20,30,45,60]})

# ---------------- COUNTRY DETECTION ----------------
countries = [
    "Iran","Israel","Ukraine","Russia","China",
    "USA","India","Pakistan","Syria","Lebanon",
    "Turkey","North Korea","Gaza"
]

def detect_country(text):
    for c in countries:
        if c.lower() in str(text).lower():
            return c
    return None

news["country"] = news["title"].apply(detect_country)

map_data = news.dropna(subset=["country"])

country_risk = map_data["country"].value_counts().reset_index()
country_risk.columns = ["country","risk"]

# ---------------- HISTORY ----------------
history = ts["negative_percent"].tolist()

impact = 0
future = []

# ---------------- SENTIMENT MOCK ----------------
positive = np.random.randint(15,25)
neutral = np.random.randint(20,30)
negative = 100 - positive - neutral

# ---------------- LAYOUT ----------------
col1, col2, col3 = st.columns([1.2,2.2,1.2])

# ---------------- NEWS PANEL ----------------
with col1:

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Latest News Updates")

    if len(news) > 0:

        latest_news = news.dropna(subset=["title"]).tail(8)[::-1]

        selected = st.selectbox(
            "Select News",
            latest_news["title"]
        )

        analysis = TextBlob(selected)
        score = analysis.sentiment.polarity

        if score < -0.3:
            impact = 12
        elif score < -0.1:
            impact = 6
        elif score > 0.3:
            impact = -8
        elif score > 0.1:
            impact = -4
        else:
            impact = 0

        row = latest_news[latest_news["title"] == selected].iloc[0]

        st.markdown(
            f"<div class='news-box'>{selected}</div>",
            unsafe_allow_html=True
        )

        st.write(row.get("description","No description"))
        st.caption(f"Source: {row.get('source','Unknown')}")

    else:
        st.write("No news available")

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- APPLY SENTIMENT IMPACT ----------------
if len(history) > 0:
    history[-1] = max(0, min(100, history[-1] + impact))

# ---------------- FORECAST ----------------
future = get_forecast(history)

# ---------------- SENTIMENT PANEL ----------------
with col2:

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Sentiment Analysis")

    c1,c2,c3 = st.columns(3)

    c1.markdown(
        f"""
        <div class='sentiment pos'>
        <div class='emoji'>😊</div>
        Positive<br><h1>{positive}%</h1>
        </div>
        """,
        unsafe_allow_html=True)

    c2.markdown(
        f"""
        <div class='sentiment neu'>
        <div class='emoji'>😐</div>
        Neutral<br><h1>{neutral}%</h1>
        </div>
        """,
        unsafe_allow_html=True)

    c3.markdown(
        f"""
        <div class='sentiment neg'>
        <div class='emoji'>😟</div>
        Negative<br><h1>{negative}%</h1>
        </div>
        """,
        unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- RISK PANEL ----------------
with col3:

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.subheader("Current Risk Level")

    current_risk = history[-1]

    if current_risk > 60:
        box = "risk-high"
        text = "⚠️ HIGH RISK"
    else:
        box = "risk-medium"
        text = "🟠 MEDIUM RISK"

    st.markdown(
        f"<div class='{box}'>{text}<br><small>Conflict Escalation Likely</small></div>",
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- GLOBAL CONFLICT MAP ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='panel'>", unsafe_allow_html=True)

st.subheader("🌍 Global Conflict Map")

if len(country_risk) > 0:

    fig_map = px.scatter_geo(
        country_risk,
        locations="country",
        locationmode="country names",
        size="risk",
        color="risk",
        projection="natural earth",
        color_continuous_scale="Reds"
    )

    fig_map.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig_map, use_container_width=True)

else:
    st.write("No geographic conflict data available")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- TREND GRAPH ----------------
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='panel'>", unsafe_allow_html=True)

st.subheader("📈 Risk Trend Prediction — Forecast")

forecast_start = len(history)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        y=history,
        mode='lines+markers',
        name="Past Risk",
        line=dict(color='#1f77ff', width=4)
    )
)

fig.add_trace(
    go.Scatter(
        x=list(range(forecast_start, forecast_start + len(future))),
        y=future,
        mode='lines+markers',
        name="Forecast",
        line=dict(color='#ff4b4b', width=4, dash='dash')
    )
)

fig.update_layout(
    template="plotly_dark",
    height=420,
    xaxis_title="Time Steps",
    yaxis_title="Risk Level (%)"
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.caption(
    f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)