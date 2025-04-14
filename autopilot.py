
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from pybaseball import batting_stats
import json

WEBHOOK_URL = "https://discord.com/api/webhooks/1361483435960438800/0ozeGsJ91aVdUUMuwwL8Cw1RMPU584liQCRx4ocRREIPVlGYLbGeG8rQcBN22mG-6QLl"

def get_stat_data():
    df = batting_stats(2024)
    df['player_name'] = df['Name'].str.lower()
    return df

def simulate_weather():
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
            games.append({
                "GamePk": game.get("gamePk"),
                "Venue": game.get("venue", {}).get("name", ""),
                "Time": game.get("gameDate", "")[11:16]
            })
    return games

def get_hitters(game_pk):
    url = f"https://statsapi.mlb.com/api/v1/game/{game_pk}/boxscore"
    res = requests.get(url).json()
    hitters = []
    for side in ['home', 'away']:
        players = res['teams'][side]['players']
        for pid, data in players.items():
            pos = data.get("position", {}).get("code", "")
            if pos and pos != "P":
                order = data.get("battingOrder")
                if order and int(order) <= 900:
                    hitters.append((data["person"]["fullName"], res['teams'][side]['team']['name']))
    return hitters

def calculate_ai(df, odds_map):
    stats_map = dict(zip(df['player_name'], df.to_dict('records')))
    final = []

    for game in get_todays_games():
        venue = game['Venue']
        weather = simulate_weather()
        hitters = get_hitters(game["GamePk"])
        for name, team in hitters:
            name_l = name.lower()
            stats = stats_map.get(name_l)
            odds = odds_map.get(name_l)
            if stats:
                ab = stats.get("AB", 0)
                doubles = stats.get("2B", 0)
                triples = stats.get("3B", 0)
                hr = stats.get("HR", 0)
                hard_hit = (doubles + triples + hr) / ab * 100 if ab > 0 else 0
                hr_fb = hr / ab * 100 if ab > 0 else 0
                barrel = np.random.uniform(10, 16)
                velo = np.random.uniform(88, 94)
                wind_bonus = 0.2 if weather["wind_mph"] > 10 else 0
                temp_bonus = 0.2 if weather["temp_f"] > 80 else 0
                odds_bonus = 0.25 if odds and odds < 350 else 0
                ai = (barrel * 0.4 + velo * 0.2 + hard_hit * 0.2 + hr_fb * 0.2) / 10 + wind_bonus + temp_bonus + odds_bonus
                final.append({
                    "Player": name,
                    "Team": team,
                    "Odds": odds,
                    "Rating": round(ai, 2)
                })

    return sorted(final, key=lambda x: x['Rating'], reverse=True)[:5]

def post_to_discord(top):
    content = "**📈 Home Run A.I. Daily Picks (Auto Export)**\n"
    for row in top:
        content += f"- **{row['Player']}** ({row['Team']}) | Odds: {row['Odds']} | A.I. Rating: {row['Rating']}\n"
    payload = {"content": content}
    requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})

def run():
    odds_sample = {
        "aaron judge": 280,
        "mookie betts": 320,
        "pete alonso": 300,
        "shohei ohtani": 250
    }
    df = get_stat_data()
    top = calculate_ai(df, odds_sample)
    post_to_discord(top)

if __name__ == "__main__":
    run()
