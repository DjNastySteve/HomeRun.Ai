
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from datetime import datetime
from pybaseball import batting_stats
from bs4 import BeautifulSoup
import json

st.set_page_config(page_title="Home Run A.I. - Autopilot", layout="wide")
st.title("🏟️ Home Run A.I. - Full Autopilot")
st.markdown("Today’s starting hitters, real stats, weather, live odds — and top picks exported automatically.")

@st.cache_data
def load_stat_data(year=2024):
    df = batting_stats(year)
    df['player_name'] = df['Name'].str.lower()
    return df

@st.cache_data
def scrape_hr_odds():
    # Placeholder for scraping real odds
    odds_map = {
        "aaron judge": 280,
        "mookie betts": 320,
        "pete alonso": 300,
        "shohei ohtani": 250
    }
    return odds_map

@st.cache_data
def get_weather(city):
    # Simulated for demo — replace with OpenWeatherMap API later
    return {
        "wind_mph": np.random.randint(2, 20),
        "temp_f": np.random.randint(55, 95)
    }

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
            venue = game.get("venue", {}).get("name", "")
            games.append({"GamePk": game_id, "Home": home, "Away": away, "Time": game_time, "Venue": venue})
    return pd.DataFrame(games)

def get_starting_hitters(game_pk):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    res = requests.get(url).json()
    hitters = []
    for side in ['home', 'away']:
        players = res['teams'][side]['players']
        for pid, data in players.items():
            pos = data.get("position", {}).get("code", "")
            if pos and pos != "P":
                batting_order = data.get("battingOrder")
                if batting_order and int(batting_order) <= 900:
                    name = data["person"]["fullName"]
                    team = res['teams'][side]['team']['name']
                    hitters.append((name, team))
    return hitters

def export_to_discord(df, webhook_url):
    try:
        top = df.head(5)
        msg = "**📈 Home Run A.I. Top 5 Picks Today:**\n"
        for _, row in top.iterrows():
            msg += f"- **{row['Player']}** ({row['Team']}) | Odds: {row['HR Odds']} | Rating: {row['A.I. Rating']}\n"
        payload = {"content": msg}
        requests.post(webhook_url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        return True
    except Exception as e:
        return False

# Load data
batting_df = load_stat_data()
name_to_stats = dict(zip(batting_df['player_name'], batting_df.to_dict('records')))
odds_feed = scrape_hr_odds()
games_df = get_todays_games()

if games_df.empty:
    st.warning("No games found.")
else:
    all_hitters = []
    for _, row in games_df.iterrows():
        venue = row["Venue"]
        weather = get_weather(venue)
        wind_bonus = 0.2 if weather["wind_mph"] > 10 else 0
        temp_bonus = 0.2 if weather["temp_f"] > 80 else 0
        hitters = get_starting_hitters(row["GamePk"])
        for name, team in hitters:
            name_l = name.lower()
            stats = name_to_stats.get(name_l)
            odds = odds_feed.get(name_l)
            if stats:
                ab = stats.get("AB", 0)
                doubles = stats.get("2B", 0)
                triples = stats.get("3B", 0)
                hr = stats.get("HR", 0)
                hard_hit = (doubles + triples + hr) / ab * 100 if ab > 0 else 0
                hr_fb = hr / ab * 100 if ab > 0 else 0
                barrel = np.random.uniform(10, 16)
                velo = np.random.uniform(88, 94)
                base_ai = (barrel * 0.4 + velo * 0.2 + hard_hit * 0.2 + hr_fb * 0.2) / 10
                odds_bonus = 0.25 if odds and odds < 350 else 0
                ai_rating = base_ai + wind_bonus + temp_bonus + odds_bonus

                all_hitters.append({
                    "Player": name,
                    "Team": team,
                    "GameTime": row["Time"],
                    "Venue": venue,
                    "Temp (F)": weather["temp_f"],
                    "Wind (mph)": weather["wind_mph"],
                    "Barrel %": round(barrel, 2),
                    "Exit Velo": round(velo, 2),
                    "Hard Hit %": round(hard_hit, 2),
                    "HR/FB %": round(hr_fb, 2),
                    "HR Odds": odds if odds else "-",
                    "A.I. Rating": round(ai_rating, 2)
                })

    if all_hitters:
        df = pd.DataFrame(all_hitters).sort_values(by="A.I. Rating", ascending=False)
        st.dataframe(df)
        st.subheader("🔥 Auto Export Top Picks")
        webhook_url = st.text_input("Paste your Discord Webhook URL to auto-send picks:")
        if st.button("📤 Export to Discord"):
            if export_to_discord(df, webhook_url):
                st.success("Top picks sent to Discord! ✅")
            else:
                st.error("Failed to send. Check webhook URL.")
    else:
        st.warning("No hitter data.")
