
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime

st.set_page_config(page_title="Home Run A.I. - Real Players", layout="wide")
st.title("🏟️ Home Run A.I. (LIVE - Real Players)")
st.markdown("Pulled from MLB StatsAPI, simulating power metrics for real hitters.")

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

def get_team_roster(team_name):
    # Look up MLB team ID first
    teams = requests.get("https://statsapi.mlb.com/api/v1/teams?sportId=1").json()["teams"]
    team_id = next((t["id"] for t in teams if t["name"] == team_name), None)
    if not team_id:
        return []
    roster_url = f"https://statsapi.mlb.com/api/v1/teams/{team_id}/roster/Active"
    roster = requests.get(roster_url).json().get("roster", [])
    return [player["person"]["fullName"] for player in roster]

def simulate_power_metrics(player):
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
    st.success(f"Games today: {len(games_df)}")
    st.dataframe(games_df[["Home", "Away", "Time"]])

    all_players = []

    for _, row in games_df.iterrows():
        for team in [row["Home"], row["Away"]]:
            player_names = get_team_roster(team)
            top_hitters = player_names[:5]  # Limit to top 5 to keep performance high
            for player in top_hitters:
                metrics = simulate_power_metrics(player)
                ai_rating = (
                    metrics["Barrel %"] * 0.4 +
                    metrics["Exit Velo"] * 0.2 +
                    metrics["Hard Hit %"] * 0.2 +
                    metrics["HR/FB %"] * 0.2
                ) / 10
                all_players.append({
                    "Player": player,
                    "Team": team,
                    "GameTime": row["Time"],
                    **metrics,
                    "A.I. Rating": round(ai_rating, 2)
                })

    df = pd.DataFrame(all_players).sort_values(by="A.I. Rating", ascending=False)
    st.subheader("🎯 A.I. Top HR Candidates (Real Players)")
    st.dataframe(df)

    st.subheader("🔝 Top 10 A.I. Picks")
    fig, ax = plt.subplots()
    ax.barh(df["Player"].head(10)[::-1], df["A.I. Rating"].head(10)[::-1], color='green')
    ax.set_xlabel("A.I. Rating")
    st.pyplot(fig)
