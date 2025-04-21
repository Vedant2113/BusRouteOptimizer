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
    towns = df.set_index('Stop Location')['Town'].to_dict() if 'Town' in df.columns else {}
    return df, G, stops, towns

df, G, all_stops, towns_dict = initialize()

if "start" not in st.session_state:
    st.session_state.start = all_stops[0]
if "end" not in st.session_state:
    st.session_state.end = all_stops[1] if len(all_stops) > 1 else all_stops[0]

cols = st.columns([4, 1, 4])
with cols[0]:
    st.session_state.start = st.selectbox("Select Start Stop", all_stops, index=all_stops.index(st.session_state.start), key="start")
with cols[1]:
    swap = st.button("🔁 Swap Stops")
with cols[2]:
    st.session_state.end = st.selectbox("Select Destination Stop", [s for s in all_stops if s != st.session_state.start], index=0 if st.session_state.end == st.session_state.start else all_stops.index(st.session_state.end), key="end")

if swap:
    temp = st.session_state.start
    st.session_state.start = st.session_state.end
    st.session_state.end = temp
    st.experimental_set_query_params(start=st.session_state.start, end=st.session_state.end)

    # Re-render the form with swapped values
    st.experimental_rerun()

time_input = st.time_input("Preferred Departure Time")
day = st.selectbox("Operating Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
show_alternatives = st.checkbox("Show next available routes if none found")

if st.button("🔍 Find Shortest Route"):
    result = find_shortest_route(G, st.session_state.start, st.session_state.end, time_input.strftime("%H:%M"), optimize="shortest")

    if result:
        st.success(f"Trip Duration: {result['duration']} minutes")
        for step in result['path']:
            town = towns_dict.get(step['stop'], "")
            display_name = f"{step['stop']} ({town})" if town else step['stop']
            st.markdown(f"📍 `{display_name}` at `{step['time']}`")
    elif show_alternatives:
        st.warning("No direct route at selected time. Showing next available route...")
        next_result = find_shortest_route(G, st.session_state.start, st.session_state.end, time_input.strftime("%H:%M"), optimize="shortest", fallback=True)
        if next_result:
            st.success(f"Next Available Trip Duration: {next_result['duration']} minutes")
            for step in next_result['path']:
                town = towns_dict.get(step['stop'], "")
                display_name = f"{step['stop']} ({town})" if town else step['stop']
                st.markdown(f"📍 `{display_name}` at `{step['time']}`")
        else:
            st.error("No upcoming routes available.")
    else:
        st.error("No valid route found. Check stop names and time.")
