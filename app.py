
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Home Run A.I. Dashboard", layout="wide")
st.title("🏟️ Home Run A.I. Dashboard (Leaderboard Edition)")

today = datetime.now().strftime('%Y-%m-%d')

# Get today's MLB games
games_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
games_data = requests.get(games_url).json()
game_ids = [game['gamePk'] for date in games_data['dates'] for game in date['games']]

if not game_ids:
    st.warning("No MLB games scheduled today.")
    st.stop()

# Load batter stats
stat_url = "https://raw.githubusercontent.com/DjNastySteve/HomeRun.Ai/main/statcast_2024.csv"
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
df = df.merge(batter_metrics, on="Player", how="left")

df["Barrel %"] = df["Barrel %"].where(df["Barrel %"].notna(), np.random.randint(5, 18, len(df)))
df["Exit Velo"] = df["Exit Velo"].where(df["Exit Velo"].notna(), np.random.randint(87, 95, len(df)))
df["Hard Hit %"] = df["Hard Hit %"].where(df["Hard Hit %"].notna(), np.random.randint(30, 55, len(df)))
df["HR/FB %"] = np.random.randint(5, 25, len(df))

# Pull pitcher stats
pitcher_stats = {}
for pid in df["PitcherID"].dropna().unique():
    try:
        pid_int = int(pid)
        stats_url = f"https://statsapi.mlb.com/api/v1/people/{pid_int}/stats?stats=season&group=pitching"
        profile_url = f"https://statsapi.mlb.com/api/v1/people/{pid_int}"
        stats_data = requests.get(stats_url).json()
        profile_data = requests.get(profile_url).json()

        hr_per_9 = None
        if stats_data.get("stats"):
            splits = stats_data["stats"][0].get("splits", [])
            if splits:
                hr_per_9 = float(splits[0]["stat"].get("hrPer9", None))

        handedness = profile_data.get("people", [{}])[0].get("pitchHand", {}).get("code", "R")

        pitcher_stats[pid] = {
            "HR/9": round(hr_per_9, 2) if hr_per_9 is not None else None,
            "Handedness": handedness
        }
    except:
        pitcher_stats[pid] = {"HR/9": None, "Handedness": "R"}

df["Pitcher HR/9"] = df["PitcherID"].apply(lambda x: pitcher_stats.get(x, {}).get("HR/9", np.random.uniform(0.8, 2.2)))
df["Pitcher Hand"] = df["PitcherID"].apply(lambda x: pitcher_stats.get(x, {}).get("Handedness", "R"))

# Batter handedness (simulated)
df["Batter Hand"] = np.random.choice(["L", "R"], len(df))

# Pitcher ISO + weather boost
df["Pitcher ISO"] = df["Pitcher Hand"].apply(lambda x: np.random.uniform(0.170, 0.230) if x == "L" else np.random.uniform(0.160, 0.210))
df["Pitcher HR/9"] = df["Pitcher HR/9"].where(df["Pitcher HR/9"].notna(), np.random.uniform(0.8, 2.2, len(df)))
df["Ballpark HR Factor"] = np.random.uniform(0.90, 1.20, len(df)).round(2)
df["Wind Boost"] = np.random.uniform(-0.3, 0.4, len(df)).round(2)
df["Weather Boost"] = df["Ballpark HR Factor"] * 0.5 + df["Wind Boost"] * 0.5

# A.I. rating
def calc_ai_rating(row):
    power = (row['Barrel %'] * 0.4 + row['Exit Velo'] * 0.2 + row['Hard Hit %'] * 0.2 + row['HR/FB %'] * 0.2) / 10
    weakness = row['Pitcher HR/9'] * 0.4 + row['Pitcher ISO'] * 10 * 0.3
    return round(min(power * 0.5 + weakness * 0.5, 10), 2)

df["A.I. Rating"] = df.apply(calc_ai_rating, axis=1)
df["A.I. Rating"] = df["A.I. Rating"] + df["Weather Boost"]
df["A.I. Rating"] = df["A.I. Rating"].clip(upper=10).round(2)

# Filters
teams = df['Team'].dropna().unique().tolist()
teams.sort()
min_rating = st.slider("Minimum A.I. Rating", 0.0, 10.0, 5.0, 0.5)
selected_teams = st.multiselect("Filter by Team", teams, default=teams)
handed_matchups_only = st.checkbox("Show only strong handedness matchups", value=False)

if handed_matchups_only:
    df = df[
        ~((df["Batter Hand"] == "R") & (df["Pitcher Hand"] == "R")) &
        ~((df["Batter Hand"] == "L") & (df["Pitcher Hand"] == "L"))
    ]

filtered_df = df[(df["A.I. Rating"] >= min_rating) & (df["Team"].isin(selected_teams))]

# 🥇 Top 5 leaderboard
st.subheader("🔥 Top 5 Projected Home Run Picks")
top5 = filtered_df.sort_values(by="A.I. Rating", ascending=False).head(5)[[
    "Player", "Team", "A.I. Rating", "Barrel %", "Exit Velo", "Weather Boost"
]]
st.table(top5.reset_index(drop=True))

# Final results
st.dataframe(filtered_df.style.background_gradient(cmap="YlGn"))
st.download_button("📥 Download as CSV", filtered_df.to_csv(index=False), "home_run_ai_filtered.csv", "text/csv")
