
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="BetEdge A.I.", layout="wide")
st.title("🎯 BetEdge A.I. – Multi-Sport Predictive Dashboard")
st.markdown("#### 📅 Date: " + datetime.now().strftime('%A, %B %d, %Y'))

tabs = st.sidebar.radio("📊 Choose a sport", ["⚽ Soccer", "⚾ MLB", "🏈 NFL", "🏀 NBA", "🏒 NHL", "🏇 Horses"])

if tabs == "⚽ Soccer":
    st.header("⚽ Goal Machine")
    simulate = st.checkbox("🧪 Simulate Striker Data (Dev Mode)")

    if simulate:
        df = pd.DataFrame({
            "Player": ["Erling Haaland", "Kylian Mbappé", "Harry Kane", "Robert Lewandowski", "Darwin Núñez"],
            "Team": ["Man City", "PSG", "Bayern", "Barcelona", "Liverpool"],
            "xG": np.random.uniform(0.45, 1.10, 5).round(2),
            "Last 5 Goals": np.random.randint(1, 6, 5),
            "Minutes": np.random.randint(70, 95, 5),
            "Opponent GA/game": np.random.uniform(0.8, 2.2, 5).round(2),
            "Team Form (last 5)": np.random.randint(2, 5, 5)
        })
    else:
        st.warning("Live EPL/UCL data not connected. Use Dev Mode.")
        st.stop()

    def calc_goal_index(row):
        base = (
            row["xG"] * 0.4 +
            row["Last 5 Goals"] * 0.2 +
            (100 - (row["Opponent GA/game"] * 50)) * 0.1 +
            row["Minutes"] * 0.1 +
            row["Team Form (last 5)"] * 0.2
        )
        return round(min(base / 2, 10), 2)

    df["Goal Index"] = df.apply(calc_goal_index, axis=1)

    st.subheader("🔥 Top 5 Goal Scorers")
    top5 = df.sort_values("Goal Index", ascending=False).head(5)
    for _, row in top5.iterrows():
        st.markdown(f"**{row['Player']} – {row['Team']}**")
        st.markdown(f"- Goal Index: `{row['Goal Index']}`")
        st.markdown(f"- xG: `{row['xG']}`, Goals (L5): `{row['Last 5 Goals']}`, Minutes: `{row['Minutes']}`")
        st.markdown(f"- Opp GA/Game: `{row['Opponent GA/game']}`, Team Form: `{row['Team Form (last 5)']}`")
        st.code(f"⚽ {row['Player']} ({row['Team']}) | Goal Index: {row['Goal Index']}/10", language="text")
        st.markdown("---")

    if st.checkbox("📊 Show Goal Scoring Charts"):
        fig, ax = plt.subplots()
        ax.barh(top5["Player"], top5["Goal Index"], color="green")
        ax.invert_yaxis()
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        ax2.scatter(df["xG"], df["Last 5 Goals"], alpha=0.7)
        ax2.set_xlabel("xG")
        ax2.set_ylabel("Goals in Last 5 Matches")
        st.pyplot(fig2)

    st.download_button("📥 Download CSV", df.to_csv(index=False), "soccer_goal_machine.csv", "text/csv")

else:
    st.info("Return to previous modules for MLB, NFL, and NBA.")
