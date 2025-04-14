
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime

st.set_page_config(page_title="Home Run A.I. - Starters Only", layout="wide")
st.title("🏟️ Home Run A.I. (LIVE - Starters Only)")
st.markdown("Powered by MLB StatsAPI — only real starting hitters included.")

def get_todays_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    res = requests.get(url).json()
    games = []
    for date in res.get("dates", []):
        for game in date.get("games", []):
            game_id = game.get("gamePk")
            home = game["teams"]["home"]["team"]["name"]
            away = game["teams"]["away"]["team"]["name"]
            game_time = game.get("gameDate", "")[11:16]
            games.append({"GamePk": game_id, "Home": home, "Away": away, "Time": game_time})
    return pd.DataFrame(games)

def get_starting_hitters(game_pk):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    res = requests.get(url).json()
    hitters = []
    for side in ['home', 'away']:
        players = res['teams'][side]['players']
        for pid, data in players.items():
            pos = data.get("position", {}).get("code", "")
            if pos and pos != "P":  # Not a pitcher
                batting_order = data.get("battingOrder")
                if batting_order and int(batting_order) <= 900:
                    name = data["person"]["fullName"]
                    team = res['teams'][side]['team']['name']
                    hitters.append((name, team))
    return hitters

def simulate_power_metrics(player):
    return {
        "Barrel %": np.random.uniform(8, 18),
        "Exit Velo": np.random.uniform(86, 94),
        "Hard Hit %": np.random.uniform(30, 50),
        "HR/FB %": np.random.uniform(10, 22)
    }

# Load today's games
games_df = get_todays_games()

if games_df.empty:
    st.warning("No MLB games found for today.")
else:
    all_hitters = []

    for _, row in games_df.iterrows():
        game_hitters = get_starting_hitters(row["GamePk"])
        for player, team in game_hitters:
            metrics = simulate_power_metrics(player)
            ai_rating = (
                metrics["Barrel %"] * 0.4 +
                metrics["Exit Velo"] * 0.2 +
                metrics["Hard Hit %"] * 0.2 +
                metrics["HR/FB %"] * 0.2
            ) / 10
            all_hitters.append({
                "Player": player,
                "Team": team,
                "GameTime": row["Time"],
                **metrics,
                "A.I. Rating": round(ai_rating, 2)
            })

    if all_hitters:
        df = pd.DataFrame(all_hitters).sort_values(by="A.I. Rating", ascending=False)
        st.subheader("🎯 A.I. Picks: Real Starting Hitters Only")
        st.dataframe(df)

        st.subheader("🔝 Top 10 A.I. Picks")
        fig, ax = plt.subplots()
        ax.barh(df["Player"].head(10)[::-1], df["A.I. Rating"].head(10)[::-1], color='green')
        ax.set_xlabel("A.I. Rating")
        st.pyplot(fig)
    else:
        st.warning("Lineups may not be posted yet. Try again later.")
