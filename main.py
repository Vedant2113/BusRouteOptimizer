import streamlit as st
import pandas as pd
from app.data_loader import load_data
from app.graph_builder import build_graph
from app.routes import find_shortest_route

st.set_page_config(page_title="Bus Route Optimizer", layout="wide")
st.title("🚌 Bus Route Optimizer")

@st.cache_data
def initialize():
    df = load_data("merged_data.xlsx")
    G = build_graph(df)
    stops = sorted(df['Stop Location'].dropna().unique())
    return df, G, stops

df, G, all_stops = initialize()

start = st.selectbox("Select Start Stop", all_stops)
end = st.selectbox("Select Destination Stop", [stop for stop in all_stops if stop != start])
time_input = st.time_input("Preferred Departure Time")
day = st.selectbox("Operating Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])

if st.button("🔍 Find Shortest Route"):
    result = find_shortest_route(G, start, end, time_input.strftime("%H:%M"), optimize="shortest")

    if result:
        st.success(f"Trip Duration: {result['duration']} minutes")
        for step in result['path']:
            st.markdown(f"📍 `{step['stop']}` at `{step['time']}`")
    else:
        st.error("No valid route found. Check stop names and time.")
