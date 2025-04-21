import streamlit as st
from route_finder import find_transfer_path

def display_all_routes(G, start, end, df):
    shown_paths = set()
    found_any = False
    all_times = sorted([t for s, t in G.nodes if s == start])

    for s_time in all_times:
        result = find_transfer_path(start, end, s_time, G, df)
        if isinstance(result, tuple):
            path, duration, correct_start_time = result
            path_signature = tuple((step['stop'], step['route'], step['time']) for step in path)
            if path_signature in shown_paths:
                continue
            shown_paths.add(path_signature)
            found_any = True
            st.write(f"🕒 **Start Time:** {correct_start_time.strftime('%H:%M')}")
            st.write(f"⏱️ **Trip Duration:** {duration} minutes")
            previous_route = None
            for i, step in enumerate(path):
                if step['transfer']:
                    next_route = path[i + 1]['route'] if i + 1 < len(path) else "Unknown"
                    st.markdown(f"<div style='background-color:#d4edda; color:#155724; padding:0.5rem; border-radius:6px; margin-bottom:0.5rem; font-weight:bold;'>🔁 Transfer at {step['stop']} ({step['town']}) from Route {previous_route} to Route {next_route} at {step['time']}</div>", unsafe_allow_html=True)
                else:
                    transfer_notice = f" (Transfer to Route {step['route']})" if previous_route and step['route'] != previous_route else ""
                    st.write(f"➡️ {step['stop']} ({step['town']}) via Route {step['route']}{transfer_notice} at {step['time']}")
                previous_route = step['route']
            st.markdown("---")

    if not found_any:
        st.warning("No available routes found from this stop to the destination.")

def display_shortest_route(G, start, end, user_time, df):
    result = find_transfer_path(start, end, user_time, G, df)
    if isinstance(result, str):
        st.error(result)
    else:
        route, duration, correct_start_time = result
        st.success(f"Trip time: {duration} minutes")
        st.write(f"🕒 **Start Time:** {correct_start_time.strftime('%H:%M')}")
        st.write("### Route Details:")
        previous_route = None
        for i, step in enumerate(route):
            if step['transfer']:
                next_route = route[i + 1]['route'] if i + 1 < len(route) else "Unknown"
                st.markdown(f"<div style='background-color:#d4edda; color:#155724; padding:0.5rem; border-radius:6px; margin-bottom:0.5rem; font-weight:bold;'>🔁 Transfer at {step['stop']} ({step['town']}) from Route {previous_route} to Route {next_route} at {step['time']}</div>", unsafe_allow_html=True)
            else:
                transfer_notice = f" (Transfer to Route {step['route']})" if previous_route and step['route'] != previous_route else ""
                st.write(f"➡️ {step['stop']} ({step['town']}) via Route {step['route']}{transfer_notice} at {step['time']}")
            previous_route = step['route']
