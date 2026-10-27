import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.title("🥧 Pie Chart from a CSV")

st.markdown(
    """
    This page reads `data/pie_demo.csv` and shows how I spend a typical week (hours).
    Use the widgets to choose which categories to include.
    """
)

# Find the CSV relative to this file so it works no matter where the app is launched from
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pie_demo.csv"


@st.cache_data
def load_data(path):
    return pd.read_csv(path)


if not DATA_PATH.exists():
    st.error(f"Could not find {DATA_PATH}. Make sure `data/pie_demo.csv` exists.")
    st.stop()

df = load_data(DATA_PATH)

st.markdown("#### Raw data")
st.dataframe(df, use_container_width=True, hide_index=True)

# ----------------- Widgets -----------------
categories = df["Activity"].tolist()
chosen = st.multiselect("Activities to include", options=categories, default=categories)
donut = st.checkbox("Show as donut chart", value=False)

view = df[df["Activity"].isin(chosen)]

# ----------------- Chart -----------------
st.markdown("#### Weekly hours by activity")
if view.empty:
    st.warning("Select at least one activity.")
else:
    fig = px.pie(
        view,
        names="Activity",
        values="Hours",
        hole=0.4 if donut else 0,
        title=f"Total: {view['Hours'].sum()} hours / week",
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)

with st.expander("How to read this chart"):
    st.write(
        """
        - Each slice is one activity; its size is that activity's share of the total hours.
        - Removing an activity recalculates the percentages for the ones left.
        """
    )

st.divider()
st.caption("Edit `data/pie_demo.csv` to change the data on this page.")
