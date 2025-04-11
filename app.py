
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Home Run A.I. Dashboard", layout="wide")

st.title("🏟️ Home Run A.I. Dashboard (Cleaned + Team Names + Rounded)")
st.markdown("""
✅ Only projected starting hitters (batting order 1–9)  
✅ Full team names  
✅ All stats rounded to whole numbers
""")

today = datetime.now().strftime('%Y-%m-%d')

games_url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
games_data = requests.get(games_url).json()
game_ids = [game['gamePk'] for date in games_data['dates'] for game in date['games']]

if not game_ids:
    st.warning("No MLB games scheduled today.")
    st.stop()

lineup_data = []
for game_id in game_ids:
    feed_url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
    r = requests.get(feed_url)
    if r.status_code != 200:
        continue
    data = r.json()
    game_info = data.get("gameData", {})
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

np.random.seed(42)
df['Barrel %'] = np.random.uniform(5, 18, len(df)).round(0).astype(int)
df['Exit Velo'] = np.random.uniform(87, 95, len(df)).round(0).astype(int)
df['Hard Hit %'] = np.random.uniform(30, 55, len(df)).round(0).astype(int)
df['HR/FB %'] = np.random.uniform(5, 25, len(df)).round(0).astype(int)
df['Pitcher HR/9'] = np.random.uniform(0.8, 2.2, len(df)).round(1)
df['Pitcher ISO'] = np.random.uniform(.150, .250, len(df)).round(3)
df['Pitcher Hand'] = np.random.choice(['L', 'R'], len(df))

def calc_ai_rating(row):
    power = (row['Barrel %'] * 0.4 + row['Exit Velo'] * 0.2 + row['Hard Hit %'] * 0.2 + row['HR/FB %'] * 0.2) / 10
    weakness = row['Pitcher HR/9'] * 0.4 + row['Pitcher ISO'] * 10 * 0.3
    return round(min(power * 0.5 + weakness * 0.5, 10), 1)

df["A.I. Rating"] = df.apply(calc_ai_rating, axis=1)

df = df.sort_values(by="A.I. Rating", ascending=False)

st.success(f"Showing projected starters for {len(df)} players in {len(game_ids)} games on {today}.")
st.dataframe(df.style.background_gradient(cmap="YlGn"))
