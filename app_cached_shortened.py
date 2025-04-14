
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pybaseball import statcast_batter_daily, cache
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import time

# Enable caching to speed up repeated Statcast queries
cache.enable()

st.set_page_config(page_title="BetEdge A.I. - MLB + NBA", layout="wide")
st.title("🎯 BetEdge A.I. – Dual-Sport Live Dashboard")

sport = st.sidebar.radio("Choose Sport", ["⚾ MLB", "🏀 NBA"])

if sport == "⚾ MLB":
    st.header("⚾ Home Run Predictor")

    try:
        today = datetime.today()
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')

        with st.spinner("Loading 7 days of Statcast data..."):
            data = statcast_batter_daily(start_dt=start_date, end_dt=end_date)

        player_stats = data.groupby("player_name").agg({
            "launch_speed": "mean",
            "events": "count"
        }).reset_index()

        player_stats = player_stats[player_stats["events"] > 15]
        player_stats["A.I. Rating"] = player_stats["launch_speed"] / 2
        top_hitters = player_stats.sort_values("A.I. Rating", ascending=False).head(15)

        st.dataframe(top_hitters[["player_name", "launch_speed", "A.I. Rating"]])

        st.subheader("Top 10 A.I. Hitters")
        fig, ax = plt.subplots()
        ax.barh(top_hitters["player_name"].head(10)[::-1], top_hitters["A.I. Rating"].head(10)[::-1], color='green')
        ax.set_xlabel("A.I. Rating")
        ax.set_title("Top 10 HR Hitters")
        st.pyplot(fig)

    except Exception as e:
        st.error(f"MLB Data Load Error: {e}")

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
