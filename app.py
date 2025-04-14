
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pybaseball import statcast
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import time

st.set_page_config(page_title="BetEdge A.I. - Dual Sport", layout="wide")
st.title("🏟️ BetEdge A.I. – MLB + NBA Smart Dashboard")

# Select mode
mode = st.sidebar.radio("Choose Sport", ["MLB", "NBA"])

if mode == "MLB":
    st.subheader("⚾ MLB Home Run Predictor")

    today = datetime.now().strftime('%Y-%m-%d')
    with st.spinner("Fetching Statcast data..."):
        try:
            data = statcast(start_dt="2024-03-28", end_dt=today)
            top_hitters = data.groupby("player_name").agg({
                "barrel_rate": "mean",
                "launch_speed": "mean",
                "hard_hit_percent": "mean",
                "events": "count"
            }).reset_index()
            top_hitters = top_hitters[top_hitters["events"] > 20].dropna()
            top_hitters["A.I. Rating"] = (
                top_hitters["barrel_rate"] * 0.4 +
                top_hitters["launch_speed"] * 0.3 +
                top_hitters["hard_hit_percent"] * 0.3
            ) / 10
            top_hitters = top_hitters.sort_values("A.I. Rating", ascending=False)
            st.dataframe(top_hitters.head(20))
        except Exception as e:
            st.error(f"Failed to load MLB data: {e}")

elif mode == "NBA":
    st.subheader("🏀 NBA Shot-Maker Index")

    nba_players = players.get_players()
    player_name = st.selectbox("Select NBA Player", [p["full_name"] for p in nba_players])
    selected = next((p for p in nba_players if p["full_name"] == player_name), None)

    if selected:
        with st.spinner("Fetching NBA game log..."):
            try:
                log = playergamelog.PlayerGameLog(player_id=selected["id"], season="2023").get_data_frames()[0]
                log["A.I. Score"] = (log["PTS"] + log["FG3M"]*1.5 + log["AST"]*0.5 - log["TOV"]) / 10
                st.dataframe(log[["GAME_DATE", "MATCHUP", "PTS", "FG3M", "AST", "TOV", "A.I. Score"]].head(10))
            except Exception as e:
                st.error(f"NBA data error: {e}")
