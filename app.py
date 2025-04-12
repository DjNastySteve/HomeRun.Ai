
# BetEdge A.I. Full – Now with NBA Shot-Maker Index
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="BetEdge A.I.", layout="wide")
st.title("🎯 BetEdge A.I. – Multi-Sport Predictive Dashboard")
st.markdown("#### 📅 Date: " + datetime.now().strftime('%A, %B %d, %Y'))

tabs = st.sidebar.radio("📊 Choose a sport", ["⚾ MLB", "🏈 NFL", "🏀 NBA", "⚽ Soccer", "🏒 NHL", "🏇 Horses"])

# NBA Shot-Maker Index
if tabs == "🏀 NBA":
    st.header("🏀 Shot-Maker Index")
    simulate = st.checkbox("🧪 Simulate Player Data (Dev Mode)")

    if simulate:
        df = pd.DataFrame({
            "Player": ["Luka Doncic", "Stephen Curry", "Jayson Tatum", "Kevin Durant", "Donovan Mitchell"],
            "Team": ["Mavericks", "Warriors", "Celtics", "Suns", "Cavaliers"],
            "Usage %": np.random.uniform(28, 36, 5).round(1),
            "Opponent Def Rating": np.random.randint(105, 120, 5),
            "Last 3 Games PPG": np.random.randint(20, 42, 5),
            "Minutes": np.random.randint(28, 39, 5),
            "3PM per Game": np.random.uniform(2.0, 5.0, 5).round(1),
            "FGA per Game": np.random.uniform(15, 25, 5).round(1)
        })
    else:
        st.warning("Live NBA player prop data not connected. Use Dev Mode.")
        st.stop()

    def calc_shot_rating(row):
        base = (
            row['Usage %'] * 0.3 +
            (130 - row['Opponent Def Rating']) * 0.2 +
            row['Last 3 Games PPG'] * 0.2 +
            row['Minutes'] * 0.1 +
            row['3PM per Game'] * 0.2
        )
        return round(min(base / 10, 10), 2)

    df["Shot-Maker Index"] = df.apply(calc_shot_rating, axis=1)

    st.subheader("🔥 Top 5 Scoring Picks")
    top5 = df.sort_values("Shot-Maker Index", ascending=False).head(5)
    for _, row in top5.iterrows():
        st.markdown(f"**{row['Player']} – {row['Team']}**")
        st.markdown(f"- Shot-Maker Index: `{row['Shot-Maker Index']}`")
        st.markdown(f"- Usage: `{row['Usage %']}%`, PPG (L3): `{row['Last 3 Games PPG']}`, Minutes: `{row['Minutes']}`")
        st.markdown(f"- Opp Def Rating: `{row['Opponent Def Rating']}`, 3PM: `{row['3PM per Game']}`")
        st.code(f"🔥 {row['Player']} ({row['Team']}) | Shot Index: {row['Shot-Maker Index']}/10", language="text")
        st.markdown("---")

    if st.checkbox("📊 Show Shot Charts"):
        fig, ax = plt.subplots()
        ax.barh(top5["Player"], top5["Shot-Maker Index"], color="orange")
        ax.invert_yaxis()
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        ax2.scatter(df["3PM per Game"], df["Last 3 Games PPG"], alpha=0.7)
        ax2.set_xlabel("3PM/Game")
        ax2.set_ylabel("PPG (Last 3)")
        st.pyplot(fig2)

    st.download_button("📥 Download CSV", df.to_csv(index=False), "nba_shot_maker_index.csv", "text/csv")

# Placeholder tabs (already built MLB + NFL go here)
elif tabs == "⚾ MLB":
    st.header("⚾ Home Run A.I. (Already Active)")
    st.info("This module is already active. Return to previous app build for full features.")

elif tabs == "🏈 NFL":
    st.header("🏈 Touchdown Threat Tracker (Already Active)")
    st.info("This module is already active. Return to previous app build for full features.")

elif tabs == "⚽ Soccer":
    st.header("⚽ Goal Machine (Coming Soon)")
    st.info("Goal probability forecasts using xG, match tempo, and defensive form.")

elif tabs == "🏒 NHL":
    st.header("🏒 Slapshot Surge (Coming Soon)")
    st.info("Shot on Goal + 1st Goal scorer prediction tools based on goalie matchups.")

elif tabs == "🏇 Horses":
    st.header("🏇 Track Whisperer (Coming Soon)")
    st.info("Horse + jockey synergy rating, track condition effects, and AI race edge insight.")
