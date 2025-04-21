import streamlit as st
import pandas as pd
from app.data_loader import load_data
from app.graph_builder import build_graph
from app.routes import find_shortest_route

st.set_page_config(page_title="Bus Route Optimizer", layout="wide")
st.title("🚌 Bus Route Optimizer")
# User Input
start = st.text_input("Enter Start Stop")
end = st.text_input("Enter Destination Stop")
time_input = st.time_input("Preferred Departure Time")
day = st.selectbox("Operating Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])


    if st.button("🔍 Find Shortest Route"):
    st.info("📌 Backend logic not connected — this is a frontend-only mockup.")

    if result:
        st.success(f"Trip Duration: {result['duration']} minutes")
        for step in result['path']:
            st.markdown(f"📍 `{step['stop']}` at `{step['time']}`")
    else:
        st.error("No valid route found. Check stop names and time.")
