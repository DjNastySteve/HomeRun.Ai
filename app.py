
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Home Run A.I. Pro Dashboard", layout="wide")

st.markdown("""
    <style>
    body { background-color: #111111; color: #FFFFFF; }
    .main .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #39B1FF; }
    .st-cf, .st-cb { background-color: #111111; color: #FFFFFF; }
    .stDataFrame { background-color: #1c1c1c; }
    </style>
""", unsafe_allow_html=True)

st.title("⚾ Home Run A.I. Pro Dashboard")
st.markdown("#### 📅 Date: Saturday, April 12, 2025")

simulate = st.checkbox("🧪 Simulate Lineups (Dev Mode)")

today = datetime.now().strftime('%Y-%m-%d')
lineup_data = []

if simulate:
    lineup_data = [{"Player": "Mookie Betts", "Team": "Dodgers", "GameID": 9999, "PitcherID": "P100"},{"Player": "Aaron Judge", "Team": "Yankees", "GameID": 9999, "PitcherID": "P101"},{"Player": "Juan Soto", "Team": "Padres", "GameID": 9999, "PitcherID": "P102"},{"Player": "Shohei Ohtani", "Team": "Angels", "GameID": 9999, "PitcherID": "P103"},{"Player": "Ronald Acuña Jr.", "Team": "Braves", "GameID": 9999, "PitcherID": "P104"}]
else:
    games_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    games_data = requests.get(games_url).json()
    game_ids = [game['gamePk'] for date in games_data['dates'] for game in date['games']]
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
            players = box.get("teams", {}).get("players", {})
            pitcher_list = box.get("teams", {}).get("pitchers", [])
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
    st.warning("❌ No player lineup data was retrieved and Dev Mode is off.")
    st.stop()

# Simulate stat data
df["Barrel %"] = np.random.randint(5, 18, len(df))
df["Exit Velo"] = np.random.randint(87, 95, len(df))
df["Hard Hit %"] = np.random.randint(30, 55, len(df))
df["HR/FB %"] = np.random.randint(5, 25, len(df))

df["Pitcher HR/9"] = np.random.uniform(0.8, 2.2, len(df))
df["Pitcher ISO"] = np.random.uniform(0.160, 0.230, len(df))
df["Pitcher Hand"] = np.random.choice(["L", "R"], len(df))
df["Batter Hand"] = np.random.choice(["L", "R"], len(df))

df["Ballpark HR Factor"] = np.random.uniform(0.90, 1.20, len(df)).round(2)
df["Wind Boost"] = np.random.uniform(-0.3, 0.4, len(df)).round(2)
df["Weather Boost"] = df["Ballpark HR Factor"] * 0.5 + df["Wind Boost"] * 0.5

def calc_ai_rating(row):
    power = (row['Barrel %'] * 0.4 + row['Exit Velo'] * 0.2 + row['Hard Hit %'] * 0.2 + row['HR/FB %'] * 0.2) / 10
    weakness = row['Pitcher HR/9'] * 0.4 + row['Pitcher ISO'] * 10 * 0.3
    return round(min(power * 0.5 + weakness * 0.5, 10), 2)

df["A.I. Rating"] = df.apply(calc_ai_rating, axis=1) + df["Weather Boost"]
df["A.I. Rating"] = df["A.I. Rating"].clip(upper=10).round(2)

teams = df['Team'].dropna().unique().tolist()
teams.sort()
min_rating = st.slider("Minimum A.I. Rating", 0.0, 10.0, 5.0, 0.5)
selected_teams = st.multiselect("Filter by Team", teams, default=teams)
handed_matchups_only = st.checkbox("Show only strong handedness matchups", value=False)
if handed_matchups_only:
    df = df[~((df["Batter Hand"] == "R") & (df["Pitcher Hand"] == "R")) & ~((df["Batter Hand"] == "L") & (df["Pitcher Hand"] == "L"))]
filtered_df = df[(df["A.I. Rating"] >= min_rating) & (df["Team"].isin(selected_teams))]

st.subheader("🔥 Top 5 Projected Home Run Picks")
top5 = filtered_df.sort_values(by="A.I. Rating", ascending=False).head(5)[["Player", "Team", "A.I. Rating", "Barrel %", "Exit Velo", "Weather Boost"]]
st.table(top5.reset_index(drop=True))

st.dataframe(filtered_df.style.background_gradient(cmap="YlGn"))
st.download_button("📥 Download as CSV", filtered_df.to_csv(index=False), "home_run_ai_filtered.csv", "text/csv")
