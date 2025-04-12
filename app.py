
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="BetEdge A.I.", layout="wide")
st.title("🎯 BetEdge A.I. – Multi-Sport Predictive Dashboard")
st.markdown("#### 📅 Date: " + datetime.now().strftime('%A, %B %d, %Y'))

tabs = st.sidebar.radio("📊 Choose a sport", ["🏒 NHL", "⚽ Soccer", "🏀 NBA", "🏈 NFL", "⚾ MLB", "🏇 Horses"])

if tabs == "🏒 NHL":
    st.header("🏒 Slapshot Surge")
    simulate = st.checkbox("🧪 Simulate Skater Data (Dev Mode)")

    if simulate:
        df = pd.DataFrame({
            "Player": ["Connor McDavid", "Auston Matthews", "David Pastrnak", "Leon Draisaitl", "Kirill Kaprizov"],
            "Team": ["Oilers", "Maple Leafs", "Bruins", "Oilers", "Wild"],
            "SOG/Game": np.random.uniform(3.0, 5.5, 5).round(1),
            "Power Play TOI": np.random.uniform(2.5, 5.0, 5).round(2),
            "Opponent Save %": np.random.uniform(0.885, 0.920, 5).round(3),
            "Ice Time": np.random.uniform(17, 23, 5).round(1),
            "Last 5 Goals": np.random.randint(0, 6, 5)
        })
    else:
        st.warning("Live NHL data not yet connected. Use Dev Mode.")
        st.stop()

    def calc_slapshot_rating(row):
        score = (
            row["SOG/Game"] * 2.0 +
            row["Power Play TOI"] * 1.5 +
            (1.0 - row["Opponent Save %"]) * 100 * 0.5 +
            row["Ice Time"] * 0.5 +
            row["Last 5 Goals"] * 1.0
        )
        return round(min(score / 2, 10), 2)

    df["Slapshot Index"] = df.apply(calc_slapshot_rating, axis=1)

    st.subheader("🔥 Top 5 Goal Threats")
    top5 = df.sort_values("Slapshot Index", ascending=False).head(5)
    for _, row in top5.iterrows():
        st.markdown(f"**{row['Player']} – {row['Team']}**")
        st.markdown(f"- Slapshot Index: `{row['Slapshot Index']}`")
        st.markdown(f"- SOG/Game: `{row['SOG/Game']}`, Power Play TOI: `{row['Power Play TOI']}`")
        st.markdown(f"- Ice Time: `{row['Ice Time']}`, Opp Save %: `{row['Opponent Save %']}`")
        st.markdown(f"- Goals (L5): `{row['Last 5 Goals']}`")
        st.code(f"🏒 {row['Player']} ({row['Team']}) | Slapshot Index: {row['Slapshot Index']}/10", language="text")
        st.markdown("---")

    if st.checkbox("📊 Show Charts"):
        fig, ax = plt.subplots()
        ax.barh(top5["Player"], top5["Slapshot Index"], color="dodgerblue")
        ax.invert_yaxis()
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        ax2.scatter(df["SOG/Game"], df["Last 5 Goals"], alpha=0.7)
        ax2.set_xlabel("SOG/Game")
        ax2.set_ylabel("Goals in Last 5")
        st.pyplot(fig2)

    st.download_button("📥 Download CSV", df.to_csv(index=False), "nhl_slapshot_surge.csv", "text/csv")

else:
    st.info("Return to other modules to view Soccer, NBA, NFL, or MLB.")
