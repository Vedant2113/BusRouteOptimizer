# main.py
import streamlit as st
from app.data_loader import load_and_prepare_data
from app.graph_builder import build_graph, add_transfers
from app.route_finder import find_transfer_path
from app.route_display import display_all_routes, display_shortest_route
from app.ui_config import apply_custom_styles
from datetime import datetime, time

apply_custom_styles()

file_path = "merged_data.xlsx"
df, all_displays, stop_display_map, reverse_display_map = load_and_prepare_data(file_path)

# Select operating day
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
selected_day = st.selectbox("Select operating day", days_of_week, index=datetime.today().weekday())
df = df[df[selected_day] == 1]

# Time input
time_options = sorted(df['Time'].dropna().unique())
default_time = min(time_options) if time_options else time(6, 0)
user_time = st.time_input("Select earliest available departure time", value=default_time)

# Session state init
if 'start_display' not in st.session_state:
    st.session_state['start_display'] = all_displays[0]
if 'end_display' not in st.session_state:
    st.session_state['end_display'] = all_displays[1]

# Swap logic
col1, col2, col3 = st.columns([5, 1, 5])
with col2:
    if st.button("🔄", help="Switch start and destination"):
        st.session_state['start_display'], st.session_state['end_display'] = st.session_state['end_display'], st.session_state['start_display']

with col1:
    start_display = st.selectbox("Select starting stop", all_displays, index=all_displays.index(st.session_state['start_display']), key="start")
with col3:
    end_display = st.selectbox("Select destination stop", all_displays, index=all_displays.index(st.session_state['end_display']), key="end")

st.session_state['start_display'] = start_display
st.session_state['end_display'] = end_display

start = stop_display_map[start_display]
end = stop_display_map[end_display]
trip_type = st.radio("Trip type", options=["One-way"])
show_all = st.checkbox("Show all possible routes without selecting time")

G = build_graph(df)
add_transfers(G, df)

if show_all:
    display_all_routes(G, start, end, df)
elif st.button("Find Shortest Time"):
    display_shortest_route(G, start, end, user_time, df)
