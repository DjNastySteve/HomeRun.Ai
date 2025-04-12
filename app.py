
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Home Run A.I. Dashboard", layout="wide")
st.title("🏟️ Home Run A.I. Dashboard (Debugging Merge Error)")

today = datetime.now().strftime('%Y-%m-%d')

# Get games
games_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
games_data = requests.get(games_url).json()
game_ids = [game['gamePk'] for date in games_data['dates'] for game in date['games']]
if not game_ids:
    st.warning("No games today.")
    st.stop()

# Load batter stats
stat_url = "https://raw.githubusercontent.com/DjNastySteve/HomeRun.Ai/main/statcast_2024.csv"
stat_df = pd.read_csv(stat_url)
stat_df["player_name_clean"] = stat_df["last_name, first_name"].apply(lambda x: f"{x.split(', ')[1]} {x.split(', ')[0]}")

batter_metrics = stat_df[[
    "player_name_clean", "barrel_batted_rate", "avg_best_speed", "hard_hit_percent"
]].copy()


st.write("🧪 Batter Metrics Columns BEFORE rename:", batter_metrics.columns.tolist())
if "player_name_clean" in batter_metrics.columns:
    batter_metrics.rename(columns={

    "player_name_clean": "Player",
    "barrel_batted_rate": "Barrel %",
    "avg_best_speed": "Exit Velo",
    "hard_hit_percent": "Hard Hit %"
}, inplace=True)
else:
    st.error("❌ 'player_name_clean' column not found in batter_metrics")

lineup_data = []
for game_id in game_ids:
    feed_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
    r = requests.get(feed_url)
    if r.status_code != 200:
        continue
    data = r.json()
    box = data.get("liveData", {}).get("boxscore", {})
    for side in ["home", "away"]:
        team_name = box.get("teams", {}).get(side, {}).get("team", {}).get("name", "")
        lineup = box.get("teams", {}).get(side, {}).get("battingOrder", [])[:9]
        players = box.get("teams", {}).get(side, {}).get("players", {})
        pitcher_list = box.get("teams", {}).get(side, {}).get("pitchers", [])
        pitcher_id = pitcher_list[0] if pitcher_list else None
        for pid in lineup:
            player = players.get(f"ID{pid}", {})
            name = player.get("person", {}).get("fullName", "")
            lineup_data.append({
                "Player": name,
                "Team": team_name,
                "GameID": game_id,
                "PitcherID": pitcher_id
            })

df = pd.DataFrame(lineup_data).drop_duplicates(subset=["Player", "Team", "GameID"])
if df.empty:
    st.error("❌ No player lineup data was retrieved. Check game feed or if any games have started.")
    st.stop()

# Debug logs before merge
st.write("⚠️ df columns before merge:", df.columns.tolist())
st.write("⚠️ batter_metrics columns:", batter_metrics.columns.tolist())

# Merge
df = df.merge(batter_metrics, on="Player", how="left")

st.success("Merge completed successfully!")
st.dataframe(df.head())
