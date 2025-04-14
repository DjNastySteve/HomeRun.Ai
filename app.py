
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pybaseball import statcast_batter, cache
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog

cache.enable()

st.set_page_config(page_title="BetEdge A.I. - MLB + NBA", layout="wide")
st.title("🎯 BetEdge A.I. – Dual-Sport Live Dashboard")

sport = st.sidebar.radio("Choose Sport", ["⚾ MLB", "🏀 NBA"])

# Predefined MLBAM player IDs
player_ids = {
    "Gunnar Henderson": 683002,
    "Brendan Donovan": 680777,
    "Pete Alonso": 624413,
    "Yordan Alvarez": 670541,
    "Francisco Lindor": 596019,
    "Logan O'Hoppe": 681351,
    "Jonathan Aranda": 660546,
    "Michael Harris II": 683076,
    "Rafael Devers": 646240,
    "Marcell Ozuna": 542303
}

if sport == "⚾ MLB":
    st.header("⚾ Home Run Predictor (Fixed ID Mode)")

    today = datetime.now().strftime('%Y-%m-%d')
    start_date = "2024-03-28"

    barrel_rates = []
    avg_velos = []
    hard_hit_rates = []
    hr_fb_rates = []
    confirmed_names = []

    with st.spinner("Loading data for selected players..."):
        for name, pid in player_ids.items():
            try:
                data = statcast_batter(start_dt=start_date, end_dt=today, player_id=pid)
                if data.empty:
                    barrel, velo, hard_hit, hr_fb = 0, 0, 0, 0
                else:
                    barrel = data['barrel_rate'].mean()
                    velo = data['launch_speed'].mean()
                    hard_hit = data['hard_hit_percent'].mean()
                    hr_fb = data['hr'].sum() / data['balls_in_play'].sum() * 100 if data['balls_in_play'].sum() > 0 else 0

                barrel_rates.append(round(barrel, 2))
                avg_velos.append(round(velo, 2))
                hard_hit_rates.append(round(hard_hit, 2))
                hr_fb_rates.append(round(hr_fb, 2))
                confirmed_names.append(name)

            except Exception as e:
                print(f"⚠️ Error loading data for {name}: {e}")

    if confirmed_names:
        df = pd.DataFrame({
            "Player": confirmed_names,
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
    else:
        st.warning("No player data was found.")

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
