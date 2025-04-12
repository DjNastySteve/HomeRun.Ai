
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime

st.set_page_config(page_title="Home Run A.I. Pro", layout="wide")
today_label = datetime.now().strftime('%A, %B %d, %Y')

st.markdown("""
    <style>
    body { background-color: #111111; color: #FFFFFF; }
    .main .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #39B1FF; }
    .stDataFrame { background-color: #1c1c1c; }
    </style>
""", unsafe_allow_html=True)

st.title("⚾ Home Run A.I. Pro Dashboard")
st.markdown(f"#### 📅 Date: {today_label}")

simulate = st.checkbox("🧪 Simulate Lineups (Dev Mode)")

lineup_data = []

if simulate:
    players = ["Mookie Betts", "Aaron Judge", "Juan Soto", "Shohei Ohtani", "Ronald Acuña Jr."]
    teams = ["Dodgers", "Yankees", "Padres", "Angels", "Braves"]
    lineup_data = [{"Player": p, "Team": t, "PitcherID": f"PID{i}", "GameID": 9999} for i, (p, t) in enumerate(zip(players, teams))]
else:
    st.info("🔄 Checking for MLB lineup feed...")
    today = datetime.now().strftime('%Y-%m-%d')
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
            lineup = box.get("teams", {}).get(side, {}).get("battingOrder", [])
            players = box.get("teams", {}).get("players", {})
            pitcher_list = box.get("teams", {}).get("pitchers", [])
            pitcher_id = pitcher_list[0] if pitcher_list else None
            for pid in lineup:
                player = players.get(f"ID{pid}", {})
                name = player.get("person", {}).get("fullName", "")
                if name:
                    lineup_data.append({"Player": name, "Team": team_name, "GameID": game_id, "PitcherID": pitcher_id})

    if not lineup_data:
        st.warning("❌ No live MLB lineups found. Enable Dev Mode to test.")
        st.stop()
    else:
        st.success("✅ Live MLB lineups detected. Loading real data...")

df = pd.DataFrame(lineup_data)
if df.empty:
    st.warning("❌ No data available.")
    st.stop()

# Simulated player stats
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
    power = (row['Barrel %']*0.4 + row['Exit Velo']*0.2 + row['Hard Hit %']*0.2 + row['HR/FB %']*0.2) / 10
    weakness = row['Pitcher HR/9']*0.4 + row['Pitcher ISO']*10*0.3
    return round(min(power*0.5 + weakness*0.5, 10), 2)

df["A.I. Rating"] = df.apply(calc_ai_rating, axis=1) + df["Weather Boost"]
df["A.I. Rating"] = df["A.I. Rating"].clip(upper=10).round(2)

# Filters
teams = df["Team"].dropna().unique().tolist()
teams.sort()
selected_teams = st.multiselect("Filter by Team", teams, default=teams)
min_rating = st.slider("Minimum A.I. Rating", 0.0, 10.0, 5.0, 0.5)
handed_matchups_only = st.checkbox("Only show favorable handedness matchups", value=False)

if handed_matchups_only:
    df = df[~((df["Batter Hand"] == "R") & (df["Pitcher Hand"] == "R")) & ~((df["Batter Hand"] == "L") & (df["Pitcher Hand"] == "L"))]

df_filtered = df[(df["A.I. Rating"] >= min_rating) & (df["Team"].isin(selected_teams))]

# Charts
if st.checkbox("📊 Show Charts"):
    st.subheader("Top 10 A.I. Ratings")
    top10 = df_filtered.sort_values("A.I. Rating", ascending=False).head(10)
    fig, ax = plt.subplots()
    ax.barh(top10["Player"], top10["A.I. Rating"], color="skyblue")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.subheader("Barrel % vs Exit Velo")
    fig2, ax2 = plt.subplots()
    ax2.scatter(df["Exit Velo"], df["Barrel %"], alpha=0.7)
    ax2.set_xlabel("Exit Velo")
    ax2.set_ylabel("Barrel %")
    st.pyplot(fig2)

# Cards
st.subheader("🔥 Top 5 Picks")
top5 = df_filtered.sort_values("A.I. Rating", ascending=False).head(5)
for _, row in top5.iterrows():
    st.markdown(f"**{row['Player']} – {row['Team']}**")
    st.markdown(f"- A.I. Rating: `{row['A.I. Rating']}`")
    st.markdown(f"- Barrel %: `{row['Barrel %']}`, Exit Velo: `{row['Exit Velo']}`, HR/FB: `{row['HR/FB %']}`")
    st.markdown(f"- Weather Boost: `{row['Weather Boost']:.2f}`")
    st.code(f"🔥 {row['Player']} – {row['Team']} | A.I. {row['A.I. Rating']}/10", language="text")
    st.markdown("---")

# Full Table
st.subheader("📋 Full Leaderboard")
st.dataframe(df_filtered.style.background_gradient(cmap="YlGn"))

st.download_button("📥 Download CSV", df_filtered.to_csv(index=False), "home_run_ai.csv", "text/csv")
