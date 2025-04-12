
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="BetEdge A.I.", layout="wide")
st.title("🎯 BetEdge A.I. – Multi-Sport Predictive Dashboard")
st.markdown("#### 📅 Date: " + datetime.now().strftime('%A, %B %d, %Y'))

tabs = st.sidebar.radio("📊 Choose a sport", ["🏇 Horses", "🏒 NHL", "⚽ Soccer", "🏀 NBA", "🏈 NFL", "⚾ MLB"])

if tabs == "🏇 Horses":
    st.header("🏇 Track Whisperer")
    simulate = st.checkbox("🧪 Simulate Racecard (Dev Mode)")

    if simulate:
        df = pd.DataFrame({
            "Horse": ["Thunderbolt", "Silver Flame", "Dark Horizon", "Golden Stride", "Midnight Dancer"],
            "Jockey": ["R. Ortiz", "F. Prat", "I. Ortiz", "J. Rosario", "L. Saez"],
            "Speed Rating": np.random.randint(85, 110, 5),
            "Jockey Win %": np.random.uniform(12, 24, 5).round(1),
            "Track Condition Boost": np.random.uniform(-0.5, 1.2, 5).round(2),
            "Last 3 Races Avg Finish": np.random.uniform(1.8, 4.5, 5).round(2)
        })
    else:
        st.warning("Live race data not yet connected. Use Dev Mode.")
        st.stop()

    def calc_racing_index(row):
        score = (
            row["Speed Rating"] * 0.4 +
            row["Jockey Win %"] * 1.5 +
            (5 - row["Last 3 Races Avg Finish"]) * 2.0 +
            row["Track Condition Boost"] * 10
        )
        return round(min(max(score / 10, 0), 10), 2)

    df["Racing Index"] = df.apply(calc_racing_index, axis=1)

    st.subheader("🔥 Top 5 Win/Place/Show Picks")
    top5 = df.sort_values("Racing Index", ascending=False).head(5)
    for _, row in top5.iterrows():
        st.markdown(f"**{row['Horse']} – Jockey: {row['Jockey']}**")
        st.markdown(f"- Racing Index: `{row['Racing Index']}`")
        st.markdown(f"- Speed Rating: `{row['Speed Rating']}`, Jockey Win %: `{row['Jockey Win %']}%`")
        st.markdown(f"- Track Boost: `{row['Track Condition Boost']}`, Avg Finish (L3): `{row['Last 3 Races Avg Finish']}`")
        st.code(f"🏇 {row['Horse']} – Racing Index: {row['Racing Index']}/10", language="text")
        st.markdown("---")

    if st.checkbox("📊 Show Race Charts"):
        fig, ax = plt.subplots()
        ax.barh(top5["Horse"], top5["Racing Index"], color="purple")
        ax.invert_yaxis()
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        ax2.scatter(df["Speed Rating"], 5 - df["Last 3 Races Avg Finish"], alpha=0.7)
        ax2.set_xlabel("Speed Rating")
        ax2.set_ylabel("Win Tendency (Lower = Better Finish)")
        st.pyplot(fig2)

    st.download_button("📥 Download CSV", df.to_csv(index=False), "track_whisperer.csv", "text/csv")

else:
    st.info("Return to other modules to view NHL, Soccer, NBA, NFL, or MLB.")
