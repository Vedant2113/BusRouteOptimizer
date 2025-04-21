# main.py
import streamlit as st
import pandas as pd
from app.data_loader import load_data
from app.graph_builder import build_graph
from app.routes import find_shortest_routes

st.set_page_config(page_title="Bus Route Optimizer", layout="wide")
st.title("🚌 Bus Route Optimizer")

@st.cache_data
def initialize():
    df = load_data("merged_data.xlsx")
    df['Stop_Town'] = df.apply(lambda row: f"{row['Stop Location']} ({row['Town']})" if pd.notna(row['Town']) else row['Stop Location'], axis=1)
    town_map = df.set_index('Stop_Town')['Stop Location'].to_dict()
    towns = df.set_index('Stop Location')['Town'].to_dict() if 'Town' in df.columns else {}
    stops = sorted(df['Stop_Town'].dropna().unique())
    G = build_graph(df)
    return df, G, stops, town_map, towns

# Load data and mappings
df, G, all_stops_display, display_to_stop_map, towns_dict = initialize()

# Safely get defaults
default_start = all_stops_display[0]
default_end = all_stops_display[1] if len(all_stops_display) > 1 else all_stops_display[0]

start_display = st.session_state.get("start", default_start)
end_display = st.session_state.get("end", default_end)

if start_display not in all_stops_display:
    start_display = default_start
if end_display not in all_stops_display:
    end_display = default_end

cols = st.columns([4, 1, 4])
with cols[0]:
    new_start_display = st.selectbox("Select Start Stop", all_stops_display, index=all_stops_display.index(start_display), key="start_select")
with cols[1]:
    if st.button("🔁 Swap Stops"):
        start_display, end_display = end_display, start_display
        st.session_state["start"] = start_display
        st.session_state["end"] = end_display
        st.experimental_rerun()
with cols[2]:
    available_ends = [s for s in all_stops_display if s != new_start_display]
    if end_display not in available_ends:
        end_display = available_ends[0]
    new_end_display = st.selectbox("Select Destination Stop", available_ends, index=available_ends.index(end_display), key="end_select")

# Store in session
st.session_state["start"] = new_start_display
st.session_state["end"] = new_end_display

# Convert display names back to stop names
start = display_to_stop_map[new_start_display]
end = display_to_stop_map[new_end_display]

time_input = st.time_input("Preferred Departure Time")
day = st.selectbox("Operating Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
show_alternatives = st.checkbox("Show next available routes if none found")

if st.button("🔍 Find Shortest Route"):
    results = find_shortest_routes(G, start, end, time_input.strftime("%H:%M"), optimize="shortest", show_multiple=show_alternatives)

    if results:
        for i, result in enumerate(results):
            if show_alternatives and i > 0:
                st.markdown("---")
                st.info(f"Alternative Route #{i+1} - Duration: {result['duration']} minutes")
            else:
                st.success(f"Trip Duration: {result['duration']} minutes")

            for step in result['path']:
                town = towns_dict.get(step['stop'], "")
                display_name = f"{step['stop']} ({town})" if town else step['stop']
                st.markdown(f"📍 `{display_name}` at `{step['time']}`")
    else:
        st.error("No valid or alternate routes found. Please try adjusting the time or check for service availability.")
