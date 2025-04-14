
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Replace with your real GitHub raw CSV URL
CSV_URL = "https://raw.githubusercontent.com/your_username/your_repo/main/today_data.csv"

st.set_page_config(page_title="Home Run A.I. - Live", layout="wide")
st.title("🏟️ Home Run A.I. Dashboard (LIVE)")
st.markdown("Powered by free GitHub automation and same-day data.")

try:
    df = pd.read_csv(CSV_URL)

    # Optional rounding
    for col in ["Barrel %", "Exit Velo", "Hard Hit %", "HR/FB %"]:
        if col in df.columns:
            df[col] = df[col].round(2)

    # A.I. Rating formula
    df["A.I. Rating"] = (
        df["Barrel %"] * 0.4 +
        df["Exit Velo"] * 0.2 +
        df["Hard Hit %"] * 0.2 +
        df["HR/FB %"] * 0.2
    ) / 10
    df["A.I. Rating"] = df["A.I. Rating"].round(2)
    df = df.sort_values(by="A.I. Rating", ascending=False)

    st.success(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    st.dataframe(df)

    st.subheader("🔝 Top A.I. Rated Players")
    fig, ax = plt.subplots()
    ax.barh(df["Player"].head(10)[::-1], df["A.I. Rating"].head(10)[::-1], color='green')
    ax.set_xlabel("A.I. Rating")
    ax.set_title("Top 10 Projected HR Hitters")
    st.pyplot(fig)

except Exception as e:
    st.error("❌ Failed to load data from GitHub. Make sure your CSV link is correct.")
    st.exception(e)
