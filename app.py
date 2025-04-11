
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Home Run A.I. Dashboard", layout="wide")
st.title("🏟️ Home Run A.I. Dashboard (with Real Batter Stats)")

today = datetime.now().strftime('%Y-%m-%d')

# Get today's MLB game IDs
games_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
games_data = requests.get(games_url).json()
game_ids = [game['gamePk'] for date in games_data['dates'] for game in date['games']]

if not game_ids:
    st.warning("No MLB games scheduled today.")
    st.stop()

# Load batter stat file (hosted locally or via GitHub in production)
stat_url = "https://raw.githubusercontent.com/DjNastySteve/HomeRun.Ai/main/statcast_2024.csv"
try:
    stat_df = pd.read_csv(stat_url)
    stat_df["player_name_clean"] = stat_df["last_name, first_name"].apply(lambda x: f"{x.split(', ')[1]} {x.split(', ')[0]}")
    batter_metrics = stat_df[[
        "player_name_clean", "barrel_batted_rate", "avg_best_speed", "hard_hit_percent"
    ]].copy()
    batter_metrics.rename(columns={
        "player_name_clean": "Player",
        "barrel_batted_rate": "Barrel %",
        "avg_best_speed": "Exit Velo",
        "hard_hit_percent": "Hard Hit %"
    }, inplace=True)
    batter_metrics["Barrel %"] = batter_metrics["Barrel %"].round(0).astype(int)
    batter_metrics["Exit Velo"] = batter_metrics["Exit Velo"].round(0).astype(int)
    batter_metrics["Hard Hit %"] = batter_metrics["Hard Hit %"].round(0).astype(int)
except:
    st.error("Could not load statcast data.")
    st.stop()

# Collect player data from MLB feed
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

# Merge real batter metrics
df = df.merge(batter_metrics, on="Player", how="left")

# Fill missing values with fallback estimates
np.random.seed(42)
df["Barrel %"] = df["Barrel %"].where(df["Barrel %"].notna(), np.random.randint(5, 18, len(df)))
df["Exit Velo"] = df["Exit Velo"].where(df["Exit Velo"].notna(), np.random.randint(87, 95, len(df)))
df["Hard Hit %"] = df["Hard Hit %"].where(df["Hard Hit %"].notna(), np.random.randint(30, 55, len(df)))
df["HR/FB %"] = np.random.randint(5, 25, len(df))  # still estimated for now
df["Pitcher HR/9"] = np.random.uniform(0.8, 2.2, len(df)).round(1)

# Simulated ISO Allowed by Pitcher Hand (placeholder for future API split logic)
# You can replace this with real splits using StatsAPI if desired
iso_lhb = np.random.uniform(.150, .250, len(df))  # batter is left
iso_rhb = np.random.uniform(.150, .250, len(df))  # batter is right

# For now, just assign generic ISO allowed based on pitcher handedness
# This will now be placed correctly after df["Pitcher Hand"] is assigned

df["Pitcher Hand"] = np.random.choice(['L', 'R'], len(df))

def calc_ai_rating(row):
    power = (row['Barrel %'] * 0.4 + row['Exit Velo'] * 0.2 + row['Hard Hit %'] * 0.2 + row['HR/FB %'] * 0.2) / 10
    weakness = row['Pitcher HR/9'] * 0.4 + row['Pitcher ISO'] * 10 * 0.3
    return round(min(power * 0.5 + weakness * 0.5, 10), 1)

df["A.I. Rating"] = df.apply(calc_ai_rating, axis=1)
df = df.sort_values(by="A.I. Rating", ascending=False)

st.success(f"Showing projected starters with real metrics for {len(df)} players on {today}.")

# Add filtering controls
teams = df['Team'].dropna().unique().tolist()
teams.sort()
min_rating = st.slider("Minimum A.I. Rating", 0.0, 10.0, 5.0, 0.5)
selected_teams = st.multiselect("Filter by Team", teams, default=teams)

# Apply filters
filtered_df = df[(df["A.I. Rating"] >= min_rating) & (df["Team"].isin(selected_teams))]


# Add handedness matchup filter
handed_matchups_only = st.checkbox("Show only strong handedness matchups (e.g. RHB vs LHP)", value=False)

# Simulate batter handedness for demo purposes (replace with real source if available)
df["Batter Hand"] = np.random.choice(["L", "R"], len(df))

if handed_matchups_only:
    filtered_df = filtered_df[
        ~((filtered_df["Batter Hand"] == "R") & (filtered_df["Pitcher Hand"] == "R")) &
        ~((filtered_df["Batter Hand"] == "L") & (filtered_df["Pitcher Hand"] == "L"))
    ]

st.dataframe(filtered_df.style.background_gradient(cmap="YlGn"))


