import networkx as nx
import pandas as pd

def build_graph(df):
    G = nx.DiGraph()
    valid_df = df[df['Time'].notnull()].sort_values(by=['Route', 'Time'])

    for route in valid_df['Route'].unique():
        route_df = valid_df[valid_df['Route'] == route]
        stops = list(route_df[['Stop Location', 'Time']].itertuples(index=False, name=None))

        for i in range(len(stops) - 1):
            stop_a, time_a = stops[i]
            stop_b, time_b = stops[i + 1]
            if time_b > time_a:
                time_diff = (pd.Timestamp.combine(pd.Timestamp.today(), time_b) - pd.Timestamp.combine(pd.Timestamp.today(), time_a)).seconds // 60
                G.add_edge((stop_a, time_a), (stop_b, time_b), weight=time_diff, route=route)

    return G
