
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pybaseball import statcast_batter_daily
from nba_api.stats.endpoints import leaguedashplayerstats
from datetime import datetime

st.set_page_config(page_title="BetEdge A.I. - Dual Sport", layout="wide")
st.title("🎯 BetEdge A.I. - MLB & NBA Live Dashboard")

# Sidebar for sport selection
sport = st.sidebar.selectbox("Choose Sport", ["MLB", "NBA"])

if sport == "MLB":
    st.header("⚾ Home Run Predictor")
    players = ["Aaron Judge", "Shohei Ohtani", "Mookie Betts", "Matt Olson", "Yordan Alvarez"]
    today = datetime.now().strftime('%Y-%m-%d')
    stats = statcast_batter_daily(start_dt="2024-03-28", end_dt=today)
    df = stats[stats['player_name'].isin(players)].groupby("player_name").agg({
        'barrel_rate': 'mean',
        'avg_hit_speed': 'mean',
        'hard_hit_percent': 'mean',
        'hr': 'sum',
        'balls_in_play': 'sum'
    }).reset_index()

    df["HR/FB %"] = df.apply(lambda r: (r["hr"]/r["balls_in_play"])*100 if r["balls_in_play"] > 0 else 0, axis=1)
    df.rename(columns={"player_name": "Player", "barrel_rate": "Barrel %", "avg_hit_speed": "Exit Velo", "hard_hit_percent": "Hard Hit %"}, inplace=True)

    df["A.I. Rating"] = df.apply(lambda r: round(min(((r["Barrel %"] * 0.4 + r["Exit Velo"] * 0.2 + r["Hard Hit %"] * 0.2 + r["HR/FB %"] * 0.2) / 10), 10), 2), axis=1)

    st.dataframe(df.sort_values("A.I. Rating", ascending=False))

    st.subheader("Top 5 Hitters")
    fig, ax = plt.subplots()
    top5 = df.sort_values("A.I. Rating", ascending=False).head(5)
    ax.barh(top5["Player"], top5["A.I. Rating"], color='green')
    st.pyplot(fig)

elif sport == "NBA":
    st.header("🏀 Shot-Maker Index")
    stats = leaguedashplayerstats.LeagueDashPlayerStats(season='2023-24').get_data_frames()[0]
    stats = stats[stats["GP"] > 10]
    top_players = stats.sort_values("PTS", ascending=False).head(20)

    df = pd.DataFrame({
        "Player": top_players["PLAYER_NAME"],
        "Usage %": top_players["USG_PCT"] * 100,
        "PPG": top_players["PTS"],
        "3PM": top_players["FG3M"],
        "Minutes": top_players["MIN"],
        "Opp Def Rank": np.random.randint(90, 110, len(top_players))  # Simulated for now
    })

    df["A.I. Rating"] = df.apply(lambda r: round(min(((r["Usage %"] * 0.3 + r["PPG"] * 0.3 + r["3PM"] * 0.2 + r["Minutes"] * 0.1 + (130 - r["Opp Def Rank"]) * 0.1) / 10), 10), 2), axis=1)

    st.dataframe(df.sort_values("A.I. Rating", ascending=False).head(10))

    st.subheader("Top Shot Makers")
    fig2, ax2 = plt.subplots()
    top10 = df.sort_values("A.I. Rating", ascending=False).head(10)
    ax2.barh(top10["Player"], top10["A.I. Rating"], color="purple")
    st.pyplot(fig2)
