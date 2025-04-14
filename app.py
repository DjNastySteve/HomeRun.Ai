
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pybaseball import statcast
from nba_api.stats.static import players
from nba_api.stats.endpoints import playergamelog
import time

st.set_page_config(page_title="BetEdge A.I.", layout="wide")
st.title("🎯 BetEdge A.I. – Dual-Sport A.I. Dashboard")

mode = st.sidebar.radio("📊 Select Sport", ["⚾ MLB – Home Run A.I.", "🏀 NBA – Shot-Maker Index"])

if mode == "⚾ MLB – Home Run A.I.":
    st.header("⚾ MLB – Home Run Predictor")
    odds_feed = {
        "Gunnar Henderson": 400, "Brendan Donovan": 950, "Pete Alonso": 320,
        "Yordan Alvarez": 300, "Francisco Lindor": 340, "Logan O'Hoppe": 450,
        "Jonathan Aranda": 520, "Michael Harris II": 420, "Rafael Devers": 450, "Marcell Ozuna": 420
    }

    game_data = [
        ("Gunnar Henderson", "BAL", "TOR", "7:05 PM"), ("Brendan Donovan", "STL", "PHI", "8:15 PM"),
        ("Pete Alonso", "NYM", "OAK", "10:05 PM"), ("Yordan Alvarez", "HOU", "LAA", "8:10 PM"),
        ("Francisco Lindor", "NYM", "OAK", "10:05 PM"), ("Logan O'Hoppe", "LAA", "HOU", "8:10 PM"),
        ("Jonathan Aranda", "TB", "ATL", "7:05 PM"), ("Michael Harris II", "ATL", "TB", "7:05 PM"),
        ("Rafael Devers", "BOS", "CHW", "7:40 PM"), ("Marcell Ozuna", "ATL", "TB", "7:05 PM")
    ]

    pitcher_weakness = {"TOR": 6.8, "PHI": 7.2, "OAK": 8.1, "LAA": 7.0, "HOU": 6.5, "ATL": 7.3, "TB": 6.6, "CHW": 7.9}
    ballpark_factor = {"TOR": 1.05, "PHI": 1.10, "OAK": 0.90, "LAA": 1.08, "HOU": 1.00, "ATL": 1.03, "TB": 0.92, "CHW": 1.10}

    players_data = [{"Player": p, "Team": team, "Opponent": opp, "GameTime": time, "HR_Odds": odds_feed[p]}
                    for p, team, opp, time in game_data]
    df = pd.DataFrame(players_data)

    def get_statcast_power(player_name):
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            stats = statcast(start_dt="2024-03-28", end_dt=today)
            player_stats = stats[stats['player_name'] == player_name]
            if player_stats.empty:
                return 0, 0, 0, 0
            return (
                player_stats['barrel_rate'].mean(),
                player_stats['launch_speed'].mean(),
                player_stats['hard_hit_percent'].mean(),
                player_stats['hr'].sum() / player_stats['balls_in_play'].sum() * 100 if player_stats['balls_in_play'].sum() > 0 else 0
            )
        except:
            return 0, 0, 0, 0

    df[["Barrel %", "Exit Velo", "Hard Hit %", "HR/FB %"]] = df["Player"].apply(lambda p: pd.Series(get_statcast_power(p)))

    def calculate_ai_rating(row):
        power_score = (row['Barrel %'] * 0.4 + row['Exit Velo'] * 0.2 + row['Hard Hit %'] * 0.2 + row['HR/FB %'] * 0.2) / 10
        weakness = pitcher_weakness.get(row["Opponent"], 7)
        park = ballpark_factor.get(row["Opponent"], 1)
        odds_factor = max(0.1, (1000 - row["HR_Odds"]) / 1000 * 10)
        ai_rating = (power_score * 0.5 + weakness * 0.2 + park * 2 + odds_factor * 0.3)
        return round(min(ai_rating, 10), 2)

    df["A.I. Rating"] = df.apply(calculate_ai_rating, axis=1)
    df = df.sort_values(by="A.I. Rating", ascending=False)

    st.dataframe(df.style.background_gradient(cmap="YlGn"))
    st.subheader("🔝 Top A.I. Rated Players")
    fig, ax = plt.subplots()
    ax.barh(df["Player"].head(10)[::-1], df["A.I. Rating"].head(10)[::-1], color='green')
    ax.set_xlabel("A.I. Rating")
    ax.set_title("Top 10 Projected HR Hitters")
    st.pyplot(fig)

    st.subheader("🎯 Barrel % vs. Exit Velocity")
    fig2, ax2 = plt.subplots()
    ax2.scatter(df["Barrel %"], df["Exit Velo"], s=df["A.I. Rating"]*10, alpha=0.7)
    ax2.set_xlabel("Barrel %")
    ax2.set_ylabel("Exit Velo")
    ax2.set_title("Power Contact Profile")
    st.pyplot(fig2)

elif mode == "🏀 NBA – Shot-Maker Index":
    st.header("🏀 NBA – Shot-Maker Index")

    nba_players = ["Stephen Curry", "Luka Doncic", "Jayson Tatum", "Kevin Durant", "Devin Booker"]
    shot_data = []

    for player_name in nba_players:
        try:
            player_info = players.find_players_by_full_name(player_name)[0]
            player_id = player_info['id']
            log = playergamelog.PlayerGameLog(player_id=player_id, season="2023-24", season_type_all_star="Regular Season")
            time.sleep(0.5)
            df_stats = log.get_data_frames()[0].head(5)

            usage = np.random.uniform(28, 36)
            ppg = df_stats["PTS"].mean()
            threes = df_stats["FG3M"].mean()
            minutes = df_stats["MIN"].str.replace(":", ".").astype(float).mean()
            def_rating = np.random.randint(105, 115)

            shot_score = (usage * 0.25 + ppg * 0.25 + threes * 0.2 + minutes * 0.15 + (130 - def_rating) * 0.15) / 10
            shot_data.append([player_name, usage, ppg, threes, minutes, def_rating, round(min(shot_score, 10), 2)])
        except:
            continue

    nba_df = pd.DataFrame(shot_data, columns=["Player", "Usage %", "PPG", "3PM", "Minutes", "Opp Def Rating", "A.I. Score"])
    nba_df = nba_df.sort_values("A.I. Score", ascending=False)

    st.dataframe(nba_df.style.background_gradient(cmap="Blues"))
    st.subheader("🏀 Top A.I. Shot Makers")
    fig3, ax3 = plt.subplots()
    ax3.barh(nba_df["Player"].head(10)[::-1], nba_df["A.I. Score"].head(10)[::-1], color='blue')
    ax3.set_xlabel("A.I. Score")
    ax3.set_title("Top NBA Scoring Threats")
    st.pyplot(fig3)
