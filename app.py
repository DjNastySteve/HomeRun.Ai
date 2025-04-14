
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pybaseball import statcast, cache
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import time

cache.enable()

st.set_page_config(page_title="BetEdge A.I. - MLB + NBA", layout="wide")
st.title("🎯 BetEdge A.I. – Dual-Sport Live Dashboard")

sport = st.sidebar.radio("Choose Sport", ["⚾ MLB", "🏀 NBA"])

# Only pull stats for selected players
player_names = [
    "Gunnar Henderson", "Brendan Donovan", "Pete Alonso", "Yordan Alvarez",
    "Francisco Lindor", "Logan O'Hoppe", "Jonathan Aranda",
    "Michael Harris II", "Rafael Devers", "Marcell Ozuna"
]

if sport == "⚾ MLB":
    st.header("⚾ Home Run Predictor")

    today = datetime.now().strftime('%Y-%m-%d')
    start_date = "2024-03-28"

    barrel_rates = []
    avg_velos = []
    hard_hit_rates = []
    hr_fb_rates = []

    st.info("Statcast now using pybaseball.statcast with filtered players and caching.")

    with st.spinner("Loading player stats... please wait ⏳"):
        try:
            statcast_df = statcast(start_dt=start_date, end_dt=today)

            for player_name in player_names:
                player_stats = statcast_df[statcast_df['player_name'] == player_name]
                if player_stats.empty:
                    barrel, velo, hard_hit, hr_fb = 0, 0, 0, 0
                else:
                    barrel = player_stats['barrel_rate'].mean()
                    velo = player_stats['launch_speed'].mean()
                    hard_hit = player_stats['hard_hit_percent'].mean()
                    hr_fb = player_stats['hr'].sum() / player_stats['balls_in_play'].sum() * 100 if player_stats['balls_in_play'].sum() > 0 else 0
                barrel_rates.append(round(barrel, 2))
                avg_velos.append(round(velo, 2))
                hard_hit_rates.append(round(hard_hit, 2))
                hr_fb_rates.append(round(hr_fb, 2))

            df = pd.DataFrame({
                "Player": player_names,
                "Barrel %": barrel_rates,
                "Exit Velo": avg_velos,
                "Hard Hit %": hard_hit_rates,
                "HR/FB %": hr_fb_rates
            })

            df["A.I. Rating"] = (
                df["Barrel %"] * 0.4 +
                df["Exit Velo"] * 0.2 +
                df["Hard Hit %"] * 0.2 +
                df["HR/FB %"] * 0.2
            ) / 10

            df = df.sort_values(by="A.I. Rating", ascending=False)
            st.dataframe(df)

            st.subheader("Top A.I. HR Hitters")
            fig, ax = plt.subplots()
            ax.barh(df["Player"].head(10)[::-1], df["A.I. Rating"].head(10)[::-1], color='green')
            ax.set_xlabel("A.I. Rating")
            st.pyplot(fig)

        except Exception as e:
            st.error(f"Statcast Load Error: {e}")

if sport == "🏀 NBA":
    st.header("🏀 Shot-Maker Index")

    all_players = players.get_players()
    player_name = st.selectbox("Select NBA Player", [p["full_name"] for p in all_players])
    player_obj = next((p for p in all_players if p["full_name"] == player_name), None)

    if player_obj:
        try:
            st.caption("Getting game logs...")
            logs = playergamelog.PlayerGameLog(player_id=player_obj["id"], season="2023").get_data_frames()[0]
            logs["A.I. Score"] = (logs["PTS"] + logs["FG3M"] * 2) / 10
            st.dataframe(logs[["GAME_DATE", "MATCHUP", "PTS", "FG3M", "A.I. Score"]].head(10))

            st.subheader("Recent Scoring Trend")
            fig2, ax2 = plt.subplots()
            ax2.plot(logs["GAME_DATE"].head(10)[::-1], logs["A.I. Score"].head(10)[::-1], marker='o')
            ax2.set_ylabel("A.I. Score")
            ax2.set_xlabel("Game Date")
            ax2.set_title("A.I. Scoring Trend")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

        except Exception as e:
            st.error(f"NBA Data Error: {e}")
