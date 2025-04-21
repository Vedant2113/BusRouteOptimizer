# main.py
import streamlit as st
import pandas as pd
from utils.data_loader import load_and_prepare_data
from utils.graph_builder import build_graph, add_transfers
from utils.route_finder import find_transfer_path
from utils.route_display import display_all_routes, display_shortest_route
from utils.ui_config import apply_custom_styles


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

# Initialize data and mappings
df, G, all_stops_display, display_to_stop_map, towns_dict = initialize()

# Defaults
default_start = all_stops_display[0]
default_end = all_stops_display[1] if len(all_stops_display) > 1 else all_stops_display[0]

# Session state
if "start" not in st.session_state:
    st.session_state.start = default_start
if "end" not in st.session_state:
    st.session_state.end = default_end

cols = st.columns([4, 1, 4])
with cols[0]:
    start_selection = st.selectbox("Select Start Stop", all_stops_display, index=all_stops_display.index(st.session_state.start), key="start_select")
with cols[1]:
    swap_clicked = st.button("🔁 Swap Stops")
with cols[2]:
    available_ends = [s for s in all_stops_display if s != start_selection]
    if st.session_state.end not in available_ends:
        st.session_state.end = available_ends[0]
    end_selection = st.selectbox("Select Destination Stop", available_ends, index=available_ends.index(st.session_state.end), key="end_select")

if swap_clicked:
    st.session_state.start, st.session_state.end = st.session_state.end, st.session_state.start
    start_selection, end_selection = st.session_state.start, st.session_state.end

st.session_state.start = start_selection
st.session_state.end = end_selection

# Extract real stop names
start = display_to_stop_map[st.session_state.start]
end = display_to_stop_map[st.session_state.end]

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

            st.markdown("**📍 Route Details:**")
            for step in result['path']:
                town = towns_dict.get(step['stop'], "")
                display_name = f"{step['stop']} ({town})" if town else step['stop']
                st.markdown(f"- {display_name} at {step['time']}")

            if result.get('transfers'):
                st.markdown("**🔁 Transfers:**")
                for t in result['transfers']:
                    st.markdown(f"→ Transfer to **Route {t['route']}** at **{t['from_stop']}** → **{t['to_stop']}** (depart at {t['time']})")
    else:
        st.error("No valid or alternate routes found. Try adjusting the time or check service availability.")
