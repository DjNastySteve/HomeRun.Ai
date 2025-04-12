
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
    simulate = st.checkbox("🧪 Simulate Lineups (Dev Mode)")

    if simulate:
        df = pd.DataFrame({
            "Player": ["Mookie Betts", "Aaron Judge", "Juan Soto", "Shohei Ohtani", "Ronald Acuña Jr."],
            "Team": ["Dodgers", "Yankees", "Padres", "Angels", "Braves"],
            "Barrel %": np.random.randint(5, 18, 5),
            "Exit Velo": np.random.randint(87, 95, 5),
            "Hard Hit %": np.random.randint(30, 55, 5),
            "HR/FB %": np.random.randint(5, 25, 5),
            "Pitcher HR/9": np.random.uniform(0.8, 2.2, 5),
            "Pitcher ISO": np.random.uniform(0.160, 0.230, 5),
            "Ballpark HR Factor": np.random.uniform(0.90, 1.20, 5),
            "Wind Boost": np.random.uniform(-0.3, 0.4, 5),
        })
    else:
        st.warning("Live MLB data integration coming soon. Use Dev Mode to preview.")
        st.stop()

    df["Weather Boost"] = df["Ballpark HR Factor"] * 0.5 + df["Wind Boost"] * 0.5

    def calc_ai_rating(row):
        power = (row['Barrel %']*0.4 + row['Exit Velo']*0.2 + row['Hard Hit %']*0.2 + row['HR/FB %']*0.2) / 10
        weakness = row['Pitcher HR/9']*0.4 + row['Pitcher ISO']*10*0.3
        return round(min(power*0.5 + weakness*0.5, 10), 2)

    df["A.I. Rating"] = df.apply(calc_ai_rating, axis=1) + df["Weather Boost"]
    df["A.I. Rating"] = df["A.I. Rating"].clip(upper=10).round(2)

    st.subheader("🔥 Top 5 Home Run Picks")
    top5 = df.sort_values("A.I. Rating", ascending=False).head(5)
    for _, row in top5.iterrows():
        st.markdown(f"**{row['Player']} – {row['Team']}**")
        st.markdown(f"- A.I. Rating: `{row['A.I. Rating']}`")
        st.markdown(f"- Barrel %: `{row['Barrel %']}`, Exit Velo: `{row['Exit Velo']}`, HR/FB: `{row['HR/FB %']}`")
        st.markdown(f"- Weather Boost: `{row['Weather Boost']:.2f}`")
        st.code(f"🔥 {row['Player']} – {row['Team']} | A.I. {row['A.I. Rating']}/10", language="text")
        st.markdown("---")

    if st.checkbox("📊 Show Charts"):
        fig, ax = plt.subplots()
        ax.barh(top5["Player"], top5["A.I. Rating"], color="skyblue")
        ax.invert_yaxis()
        st.pyplot(fig)

        fig2, ax2 = plt.subplots()
        ax2.scatter(df["Exit Velo"], df["Barrel %"], alpha=0.7)
        ax2.set_xlabel("Exit Velo")
        ax2.set_ylabel("Barrel %")
        st.pyplot(fig2)

    st.download_button("📥 Download CSV", df.to_csv(index=False), "mlb_home_run_ai.csv", "text/csv")

elif tabs == "🏈 NFL":
    st.header("🏈 Touchdown Threat Tracker")
    simulate = st.checkbox("🧪 Simulate Red Zone Data (Dev Mode)")

    if simulate:
        df = pd.DataFrame({
            "Player": ["Christian McCaffrey", "Tyreek Hill", "Travis Kelce", "Stefon Diggs", "Austin Ekeler"],
            "Team": ["49ers", "Dolphins", "Chiefs", "Bills", "Chargers"],
            "Position": ["RB", "WR", "TE", "WR", "RB"],
            "Red Zone Touches": np.random.randint(3, 10, 5),
            "Target Share %": np.random.uniform(18, 34, 5).round(1),
            "Opp. Red Zone Rank": np.random.randint(1, 32, 5),
            "Snap %": np.random.uniform(65, 95, 5).round(1),
            "Weather Impact": np.random.uniform(-0.3, 0.2, 5).round(2)
        })
    else:
        st.warning("Live NFL red zone data not yet connected. Use Dev Mode.")
        st.stop()

    def calc_td_rating(row):
        score = (
            row['Red Zone Touches'] * 0.4 +
            row['Target Share %'] * 0.2 +
            (100 - row['Opp. Red Zone Rank']) * 0.2 +
            row['Snap %'] * 0.1 +
            row['Weather Impact'] * 10 * 0.1
        )
        return round(min(score / 10, 10), 2)

    df["TD Threat Score"] = df.apply(calc_td_rating, axis=1)

    st.subheader("🔥 Top 5 TD Threats")
    top5 = df.sort_values("TD Threat Score", ascending=False).head(5)
    for _, row in top5.iterrows():
        st.markdown(f"**{row['Player']} – {row['Team']} ({row['Position']})**")
        st.markdown(f"- TD Threat Score: `{row['TD Threat Score']}`")
        st.markdown(f"- Red Zone Touches: `{row['Red Zone Touches']}`, Target Share: `{row['Target Share %']}%`")
        st.markdown(f"- Snap %: `{row['Snap %']}%`, Opp. RZ Rank: `{row['Opp. Red Zone Rank']}`")
        st.code(f"🔥 {row['Player']} ({row['Team']}) | TD Score {row['TD Threat Score']}/10", language="text")
        st.markdown("---")

    if st.checkbox("📊 Show TD Threat Charts"):
        fig, ax = plt.subplots()
        ax.barh(top5["Player"], top5["TD Threat Score"], color="salmon")
        ax.invert_yaxis()
        st.pyplot(fig)

    st.download_button("📥 Download CSV", df.to_csv(index=False), "nfl_td_threats.csv", "text/csv")

elif tabs == "🏀 NBA":
    st.header("🏀 Shot-Maker Index (Coming Soon)")
    st.info("Projected scorers, 3PT threats, and matchup impact tools for prop and DFS analysis.")

elif tabs == "⚽ Soccer":
    st.header("⚽ Goal Machine (Coming Soon)")
    st.info("Goal probability forecasts using xG, match tempo, and defensive form.")

elif tabs == "🏒 NHL":
    st.header("🏒 Slapshot Surge (Coming Soon)")
    st.info("Shot on Goal + 1st Goal scorer prediction tools based on goalie matchups.")

elif tabs == "🏇 Horses":
    st.header("🏇 Track Whisperer (Coming Soon)")
    st.info("Horse + jockey synergy rating, track condition effects, and AI race edge insight.")
