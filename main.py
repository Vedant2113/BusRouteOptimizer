import streamlit as st
import pandas as pd
from app.data_loader import load_data
from app.graph_builder import build_graph
from app.routes import find_shortest_route

st.set_page_config(page_title="Bus Route Optimizer", layout="wide")
st.title("🚌 Bus Route Optimizer")
