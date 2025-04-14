
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="BetEdge A.I.", layout="wide")
st.title("🎯 BetEdge A.I. – Multi-Sport Predictive Dashboard")
st.markdown("#### 📅 Date: " + datetime.now().strftime('%A, %B %d, %Y'))

tabs = st.sidebar.radio("📊 Choose a sport", ["⚾ MLB", "🏈 NFL", "🏀 NBA", "⚽ Soccer", "🏒 NHL", "🏇 Horses"])

if tabs == "⚾ MLB":
    st.header("⚾ Home Run A.I.")
    if st.checkbox("🧪 Simulate MLB Data"):
        df = pd.DataFrame({
            "Player": ["Aaron Judge", "Shohei Ohtani", "Mookie Betts", "Matt Olson", "Yordan Alvarez"],
            "Team": ["Yankees", "Angels", "Dodgers", "Braves", "Astros"],
            "Barrel %": np.random.randint(5, 18, 5),
            "Exit Velo": np.random.randint(87, 95, 5),
            "Hard Hit %": np.random.randint(30, 55, 5),
            "HR/FB %": np.random.randint(5, 25, 5),
            "Pitcher HR/9": np.random.uniform(0.8, 2.2, 5),
            "Ballpark HR Factor": np.random.uniform(0.90, 1.20, 5),
            "Wind Boost": np.random.uniform(-0.3, 0.4, 5)
        })

        df["Pitcher Hand"] = np.random.choice(["L", "R"], len(df))
        df["Pitcher ISO"] = df["Pitcher Hand"].apply(
            lambda x: np.random.uniform(0.170, 0.230) if x == "L" else np.random.uniform(0.160, 0.210)
        )
        df["Weather Boost"] = df["Ballpark HR Factor"] * 0.5 + df["Wind Boost"] * 0.5

        def calc_ai_rating(row):
            power = (row['Barrel %'] * 0.4 + row['Exit Velo'] * 0.2 + row['Hard Hit %'] * 0.2 + row['HR/FB %'] * 0.2) / 10
            weakness = row['Pitcher HR/9'] * 0.4 + row['Pitcher ISO'] * 10 * 0.3
            return round(min(power * 0.5 + weakness * 0.5 + row["Weather Boost"], 10), 2)

        df["A.I. Rating"] = df.apply(calc_ai_rating, axis=1)

        st.subheader("Top 5 Home Run Picks")
        st.dataframe(df.sort_values("A.I. Rating", ascending=False).head(5))

elif tabs == "🏈 NFL":
    st.header("🏈 Touchdown Threat Tracker")
    if st.checkbox("🧪 Simulate NFL Data"):
        df = pd.DataFrame({
            "Player": ["Tyreek Hill", "Travis Kelce", "Christian McCaffrey", "Justin Jefferson", "Ja'Marr Chase"],
            "Team": ["Dolphins", "Chiefs", "49ers", "Vikings", "Bengals"],
            "Red Zone Touches": np.random.randint(3, 10, 5),
            "Target Share %": np.random.uniform(18, 34, 5).round(1),
            "Opp. Red Zone Rank": np.random.randint(1, 32, 5),
            "Snap %": np.random.uniform(65, 95, 5).round(1),
            "Weather Impact": np.random.uniform(-0.3, 0.2, 5).round(2)
        })
        df["TD Score"] = df.apply(lambda r: round(min((r['Red Zone Touches']*0.4 + r['Target Share %']*0.2 + (100 - r['Opp. Red Zone Rank'])*0.2 + r['Snap %']*0.1 + r['Weather Impact']*10*0.1)/10, 10), 2), axis=1)
        st.subheader("Top 5 TD Threats")
        st.dataframe(df.sort_values("TD Score", ascending=False).head(5))

elif tabs == "🏀 NBA":
    st.header("🏀 Shot-Maker Index")
    if st.checkbox("🧪 Simulate NBA Data"):
        df = pd.DataFrame({
            "Player": ["Stephen Curry", "Luka Doncic", "Jayson Tatum", "Kevin Durant", "Devin Booker"],
            "Team": ["Warriors", "Mavericks", "Celtics", "Suns", "Suns"],
            "Usage %": np.random.uniform(28, 36, 5).round(1),
            "Opponent Def Rating": np.random.randint(105, 120, 5),
            "Last 3 Games PPG": np.random.randint(20, 42, 5),
            "Minutes": np.random.randint(28, 39, 5),
            "3PM/Game": np.random.uniform(2.0, 5.0, 5).round(1)
        })
        df["Shot Index"] = df.apply(lambda r: round(min((r['Usage %']*0.3 + (130 - r['Opponent Def Rating'])*0.2 + r['Last 3 Games PPG']*0.2 + r['Minutes']*0.1 + r['3PM/Game']*0.2)/10, 10), 2), axis=1)
        st.dataframe(df.sort_values("Shot Index", ascending=False))

elif tabs == "⚽ Soccer":
    st.header("⚽ Goal Machine")
    if st.checkbox("🧪 Simulate Soccer Data"):
        df = pd.DataFrame({
            "Player": ["Erling Haaland", "Kylian Mbappe", "Harry Kane", "Robert Lewandowski", "Mohamed Salah"],
            "Team": ["Man City", "PSG", "Bayern", "Barcelona", "Liverpool"],
            "xG": np.random.uniform(0.45, 1.10, 5).round(2),
            "Last 5 Goals": np.random.randint(1, 6, 5),
            "Minutes": np.random.randint(70, 95, 5),
            "Opponent GA/game": np.random.uniform(0.8, 2.2, 5).round(2),
            "Team Form (last 5)": np.random.randint(2, 5, 5)
        })
        df["Goal Index"] = df.apply(lambda r: round(min((r["xG"]*0.4 + r["Last 5 Goals"]*0.2 + (100 - (r["Opponent GA/game"] * 50)) * 0.1 + r["Minutes"]*0.1 + r["Team Form (last 5)"]*0.2)/2, 10), 2), axis=1)
        st.dataframe(df.sort_values("Goal Index", ascending=False))

# Add others as needed...

