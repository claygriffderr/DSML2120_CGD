# AI use note:
# Parts of this page were written with help from Claude Code, using the
# Claude Opus 5.5 model (claude-opus-5-5), on 2026-10-29 around 6:48 PM MDT.
# AI helped write the sample fallback data (SAMPLE_DF), the line chart, and
# the code that saves each reading to data/weather_history.csv so the chart
# shows historic data. I reviewed and tested the code myself.

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import time
from pathlib import Path


st.set_page_config(page_title="Live API Demo (Simple)", page_icon="📡", layout="wide")
# Disable fade/transition so charts don't blink between reruns
st.markdown("""
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

st.title("📡 Live Temperature Data Demo (Open-Meteo)")
st.caption("Live data visualization of weather in Denver, Co.")


lat, lon = 39.7392, -104.9903  # Denver
wurl = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m&timezone=America/Denver"

# Every reading gets saved here so the chart can show history
HISTORY_PATH = Path(__file__).resolve().parent.parent / "data" / "weather_history.csv"
COLUMNS = ["time", "temperature", "wind"]


def load_history():
    """Read the saved readings, or return an empty table if there are none yet."""
    if HISTORY_PATH.exists():
        return pd.read_csv(HISTORY_PATH, parse_dates=["time"])
    return pd.DataFrame(columns=COLUMNS)


def get_weather():
    """Fetch the current reading, add it to the CSV, and return (history_df, error)."""
    # Create the CSV with just a header row if it isn't there yet
    if not HISTORY_PATH.exists():
        HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=COLUMNS).to_csv(HISTORY_PATH, index=False)

    try:
        r = requests.get(wurl, timeout=10)
        r.raise_for_status()
        j = r.json()["current"]
    except (requests.RequestException, KeyError) as e:
        return load_history(), f"Could not reach Open-Meteo: {e}"

    new_row = pd.DataFrame([{"time": pd.to_datetime(j["time"]),
                             "temperature": j["temperature_2m"],
                             "wind": j["wind_speed_10m"]}])

    history = load_history()
    # Open-Meteo only updates "current" every 15 minutes, so skip a reading
    # whose timestamp is already saved (otherwise we'd store duplicates)
    if new_row["time"].iloc[0] not in set(history["time"]):
        new_row.to_csv(HISTORY_PATH, mode="a", header=False, index=False)
        history = pd.concat([history, new_row], ignore_index=True)

    return history.sort_values("time"), None


# Sample data in the same shape get_weather() returns, used if the API fails
# and there is no saved history yet (temperature in °C, wind in km/h)
SAMPLE_DF = pd.DataFrame([{"time": pd.to_datetime("2026-10-29T18:30"),
                           "temperature": 12.4,
                           "wind": 9.7}])


# --- Auto Refresh Controls ---
st.subheader("🔁 Auto Refresh Settings")

# Let user choose how often to refresh (in seconds)
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)

# Toggle to turn automatic refreshing on/off
auto_refresh = st.toggle("Enable auto-refresh", value=False)

# Show current refresh time
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")


st.subheader("Temperature history")
df, err = get_weather()

if err:
    st.warning(err)
if df.empty:
    st.info("No saved readings yet, so showing sample data.")
    df = SAMPLE_DF.copy()

st.dataframe(df, use_container_width=True, hide_index=True)

fig = px.line(df, x="time", y="temperature", markers=True,
              title="Temperature in Denver, CO over time",
              labels={"time": "Time", "temperature": "Temperature (°C)"})
st.plotly_chart(fig, use_container_width=True)
st.caption(f"{len(df)} readings saved in data/weather_history.csv")

# If auto-refresh is ON, wait and rerun the app
if auto_refresh:
    time.sleep(refresh_sec)
    st.rerun()
