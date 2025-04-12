
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Home Run A.I. Pro", layout="wide")
today_label = datetime.now().strftime('%A, %B %d, %Y')

st.markdown("""
    <style>
    body { background-color: #111111; color: #FFFFFF; }
    .main .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #39B1FF; }
    .stDataFrame { background-color: #1c1c1c; }
    </style>
""", unsafe_allow_html=True)

st.title("⚾ Home Run A.I. Pro Dashboard")
st.markdown(f"#### 📅 Date: {today_label}")

simulate = st.checkbox("🧪 Simulate Lineups (Dev Mode)")

if simulate:
    players = ["Mookie Betts", "Aaron Judge", "Juan Soto", "Shohei Ohtani", "Ronald Acuña Jr."]
    teams = ["Dodgers", "Yankees", "Padres", "Angels", "Braves"]
    df = pd.DataFrame({
        "Player": players,
        "Team": teams,
        "Barrel %": np.random.randint(5, 18, 5),
        "Exit Velo": np.random.randint(87, 95, 5),
        "Hard Hit %": np.random.randint(30, 55, 5),
        "HR/FB %": np.random.randint(5, 25, 5),
        "Pitcher HR/9": np.random.uniform(0.8, 2.2, 5),
        "Pitcher ISO": np.random.uniform(0.160, 0.230, 5),
        "Ballpark HR Factor": np.random.uniform(0.90, 1.20, 5),
        "Wind Boost": np.random.uniform(-0.3, 0.4, 5)
    })
else:
    st.warning("❌ No live data detected. Use Dev Mode.")
    st.stop()

df["Weather Boost"] = df["Ballpark HR Factor"] * 0.5 + df["Wind Boost"] * 0.5
def calc_ai_rating(row):
    power = (row['Barrel %']*0.4 + row['Exit Velo']*0.2 + row['Hard Hit %']*0.2 + row['HR/FB %']*0.2) / 10
    weakness = row['Pitcher HR/9']*0.4 + row['Pitcher ISO']*10*0.3
    return round(min(power*0.5 + weakness*0.5, 10), 2)
df["A.I. Rating"] = df.apply(calc_ai_rating, axis=1) + df["Weather Boost"]
df["A.I. Rating"] = df["A.I. Rating"].clip(upper=10).round(2)

if st.checkbox("📊 Show Charts"):
    st.subheader("Top 5 A.I. Ratings")
    top5 = df.sort_values("A.I. Rating", ascending=False).head(5)
    fig, ax = plt.subplots()
    ax.barh(top5["Player"], top5["A.I. Rating"], color="skyblue")
    ax.invert_yaxis()
    st.pyplot(fig)

    st.subheader("Barrel % vs Exit Velo")
    fig2, ax2 = plt.subplots()
    ax2.scatter(df["Exit Velo"], df["Barrel %"], alpha=0.7)
    ax2.set_xlabel("Exit Velo")
    ax2.set_ylabel("Barrel %")
    st.pyplot(fig2)

st.subheader("🔥 Top 5 Projected Picks")
top5 = df.sort_values("A.I. Rating", ascending=False).head(5)
for _, row in top5.iterrows():
    st.markdown(f"**{row['Player']} – {row['Team']}**")
    st.markdown(f"- A.I. Rating: `{row['A.I. Rating']}`")
    st.markdown(f"- Barrel %: `{row['Barrel %']}`, Exit Velo: `{row['Exit Velo']}`, HR/FB: `{row['HR/FB %']}`")
    st.markdown(f"- Weather Boost: `{row['Weather Boost']:.2f}`")
    st.code(f"🔥 {row['Player']} – {row['Team']} | A.I. {row['A.I. Rating']}/10", language="text")
    st.markdown("---")

st.download_button("📥 Download Full CSV", df.to_csv(index=False), "home_run_ai.csv", "text/csv")
