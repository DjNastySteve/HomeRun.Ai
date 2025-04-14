
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime

st.set_page_config(page_title="Home Run A.I. - Free & Live", layout="wide")
st.title("🏟️ Home Run A.I. (LIVE - StatsAPI)")
st.markdown("Fully automated, powered by free MLB StatsAPI + simulated metrics")

def get_todays_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    res = requests.get(url).json()
    games = []
    for date in res.get("dates", []):
        for game in date.get("games", []):
            home = game["teams"]["home"]["team"]["name"]
            away = game["teams"]["away"]["team"]["name"]
            game_time = game.get("gameDate", "")[11:16]
            games.append({"Home": home, "Away": away, "Time": game_time})
    return pd.DataFrame(games)

def simulate_power_metrics(player):
    # Simulate statcast-style power data for demo purposes
    return {
        "Barrel %": np.random.uniform(8, 18),
        "Exit Velo": np.random.uniform(86, 94),
        "Hard Hit %": np.random.uniform(30, 50),
        "HR/FB %": np.random.uniform(10, 22)
    }

# Load games
games_df = get_todays_games()

if games_df.empty:
    st.warning("No MLB games found for today.")
else:
    st.success(f"Games found: {len(games_df)}")
    st.dataframe(games_df)

    # Simulate top HR candidates per game
    st.subheader("📊 Simulated A.I. Home Run Picks")
    simulated_data = []

    for _, row in games_df.iterrows():
        for team in [row["Home"], row["Away"]]:
            # Create 1 random slugger per team
            player_name = f"{team} Slugger"
            metrics = simulate_power_metrics(player_name)
            ai_rating = (
                metrics["Barrel %"] * 0.4 +
                metrics["Exit Velo"] * 0.2 +
                metrics["Hard Hit %"] * 0.2 +
                metrics["HR/FB %"] * 0.2
            ) / 10
            simulated_data.append({
                "Player": player_name,
                "Team": team,
                "GameTime": row["Time"],
                **metrics,
                "A.I. Rating": round(ai_rating, 2)
            })

    df = pd.DataFrame(simulated_data).sort_values(by="A.I. Rating", ascending=False)
    st.dataframe(df)

    # Bar chart
    st.subheader("🔥 Top A.I. Rated HR Picks")
    fig, ax = plt.subplots()
    ax.barh(df["Player"].head(10)[::-1], df["A.I. Rating"].head(10)[::-1], color='green')
    ax.set_xlabel("A.I. Rating")
    st.pyplot(fig)
