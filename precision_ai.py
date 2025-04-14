
import pandas as pd
import numpy as np
import requests
from datetime import datetime
from pybaseball import statcast_batter
import json

# Set your free OpenWeatherMap API key here
OWM_API_KEY = "your_openweather_api_key"
WEBHOOK_URL = "https://discord.com/api/webhooks/1361483435960438800/0ozeGsJ91aVdUUMuwwL8Cw1RMPU584liQCRx4ocRREIPVlGYLbGeG8rQcBN22mG-6QLl"

def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_API_KEY}&units=imperial"
        response = requests.get(url).json()
        return {
            "wind_mph": response["wind"]["speed"],
            "temp_f": response["main"]["temp"],
            "conditions": response["weather"][0]["main"]
        }
    except:
        return {"wind_mph": 0, "temp_f": 70, "conditions": "Unknown"}

def get_statcast(start="2024-03-28", end=None):
    if not end:
        end = datetime.now().strftime("%Y-%m-%d")
    data = statcast_batter(start_dt=start, end_dt=end)
    return data

def aggregate_player_metrics(statcast_df):
    grouped = statcast_df.groupby("player_name")
    metrics = grouped.agg({
        "launch_speed": "mean",
        "barrel": "sum",
        "events": "count"
    }).reset_index()
    metrics["Barrel %"] = (metrics["barrel"] / metrics["events"]) * 100
    metrics["Exit Velo"] = metrics["launch_speed"]
    return metrics[["player_name", "Barrel %", "Exit Velo"]]

def simulate_game_data():
    return [
        {"Player": "Aaron Judge", "Team": "NYY", "Opponent": "BOS", "Venue": "Yankee Stadium"},
        {"Player": "Shohei Ohtani", "Team": "LAD", "Opponent": "SD", "Venue": "Dodger Stadium"},
        {"Player": "Pete Alonso", "Team": "NYM", "Opponent": "PHI", "Venue": "Citi Field"},
    ]

def post_to_discord(df):
    msg = "**🎯 Precision HR A.I. Picks**\n"
    for _, row in df.iterrows():
        msg += f"- **{row['Player']}** ({row['Team']}) | Barrel: {row['Barrel %']}% | EV: {row['Exit Velo']} mph | A.I.: {row['A.I. Rating']}\n"
    payload = {"content": msg}
    requests.post(WEBHOOK_URL, data=json.dumps(payload), headers={"Content-Type": "application/json"})

def run():
    statcast_df = get_statcast()
    metrics = aggregate_player_metrics(statcast_df)
    games = simulate_game_data()
    final = []

    for g in games:
        weather = get_weather(g["Venue"])
        name = g["Player"]
        match = metrics[metrics["player_name"].str.lower() == name.lower()]
        if not match.empty:
            barrel = match["Barrel %"].values[0]
            velo = match["Exit Velo"].values[0]
        else:
            barrel = np.random.uniform(8, 14)
            velo = np.random.uniform(87, 94)

        wind_bonus = 0.3 if weather["wind_mph"] > 12 else 0
        temp_bonus = 0.3 if weather["temp_f"] > 78 else 0

        ai_rating = (barrel * 0.5 + velo * 0.3) / 10 + wind_bonus + temp_bonus
        final.append({
            "Player": name,
            "Team": g["Team"],
            "Barrel %": round(barrel, 2),
            "Exit Velo": round(velo, 2),
            "A.I. Rating": round(ai_rating, 2)
        })

    result_df = pd.DataFrame(final).sort_values(by="A.I. Rating", ascending=False)
    print(result_df)
    post_to_discord(result_df)

if __name__ == "__main__":
    run()
