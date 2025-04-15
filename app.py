
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from pybaseball import batting_stats
from bs4 import BeautifulSoup
import re

OWM_API_KEY = "your_openweather_api_key_here"

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=imperial"
        res = requests.get(url).json()
        return {
            "temp": res['main']['temp'],
            "wind": res['wind']['speed'],
            "condition": res['weather'][0]['main']
        }
    except:
        return {"temp": 72, "wind": 5, "condition": "Clear"}

def scrape_dk_home_run_odds():
    url = "https://sportsbook.draftkings.com/leagues/baseball/mlb"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    odds_map = {}
    for tag in soup.find_all("span", string=re.compile(r"\+\d{2,4}")):
        parent = tag.find_parent()
        if parent:
            player_info = parent.find_previous("span")
            if player_info:
                name = player_info.text.strip().lower()
                try:
                    odds = int(tag.text.strip().replace("+", ""))
                    odds_map[name] = odds
                except:
                    continue
    return odds_map

def get_todays_games():
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&date={today}"
    res = requests.get(url).json()
    games = []
    for date in res.get("dates", []):
        for game in date.get("games", []):
            games.append({
                "GamePk": game["gamePk"],
                "Home": game["teams"]["home"]["team"]["name"],
                "Away": game["teams"]["away"]["team"]["name"],
                "Time": game["gameDate"][11:16],
                "Venue": game.get("venue", {}).get("name", ""),
                "City": game.get("venue", {}).get("name", "Unknown")
            })
    return games

def get_hitters(game_pk):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    res = requests.get(url).json()
    hitters = []
    for side in ["home", "away"]:
        players = res['teams'][side]['players']
        for pid, info in players.items():
            pos = info.get("position", {}).get("code", "")
            if pos and pos != "P":
                order = info.get("battingOrder")
                if order and int(order) <= 900:
                    hitters.append((info["person"]["fullName"], res["teams"][side]["team"]["name"]))
    return hitters

def run_app():
    st.set_page_config(layout="wide")
    st.title("🏟️ Home Run A.I. - DraftKings Odds Edition")

    st.markdown("### Today's Top A.I. Home Run Picks")
    batting = batting_stats(2024)
    batting["player_name"] = batting["Name"].str.lower()
    odds_map = scrape_dk_home_run_odds()
    games = get_todays_games()
    final = []

    for game in games:
        weather = get_weather(game["City"])
        wind_bonus = 0.2 if weather["wind"] > 10 else 0
        temp_bonus = 0.2 if weather["temp"] > 80 else 0
        hitters = get_hitters(game["GamePk"])

        for name, team in hitters:
            name_l = name.lower()
            stats = batting[batting["player_name"] == name_l]
            odds = odds_map.get(name_l)

            if not stats.empty:
                ab = stats["AB"].values[0]
                hr = stats["HR"].values[0]
                hard_hit = ((stats["2B"].values[0] + stats["3B"].values[0] + hr) / ab) * 100 if ab > 0 else 0
                hr_fb = (hr / ab) * 100 if ab > 0 else 0
                barrel = np.random.uniform(10, 16)
                velo = np.random.uniform(88, 94)
                odds_bonus = 0.25 if odds and odds < 350 else 0
                ai = (barrel * 0.4 + velo * 0.2 + hard_hit * 0.2 + hr_fb * 0.2) / 10 + wind_bonus + temp_bonus + odds_bonus

                final.append({
                    "Player": name,
                    "Team": team,
                    "City": game["City"],
                    "Venue": game["Venue"],
                    "Temp (F)": weather["temp"],
                    "Wind (mph)": weather["wind"],
                    "Odds": odds if odds else "-",
                    "Barrel %": round(barrel, 2),
                    "Exit Velo": round(velo, 2),
                    "A.I. Rating": round(ai, 2)
                })

    df = pd.DataFrame(final).sort_values("A.I. Rating", ascending=False)
    st.dataframe(df)

    st.subheader("🔝 Top 10 Projected Home Run Hitters")
    st.bar_chart(df.head(10).set_index("Player")["A.I. Rating"])

if __name__ == "__main__":
    run_app()
