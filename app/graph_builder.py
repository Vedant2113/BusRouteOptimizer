import networkx as nx
from datetime import datetime, timedelta

def build_graph(df):
    G = nx.DiGraph()
    df = df[df['Time'].notnull()].sort_values(by=['Stop Location', 'Time'])

    for route in df['Route'].unique():
        route_df = df[df['Route'] == route].copy()
        if route == '68':
            if route_df[route_df['Stop Location'] == 'Canton-Potsdam Hospital']['Time'].empty:
                route_df = route_df[route_df['Stop Location'] != 'Canton-Potsdam Hospital']
        route_df = route_df.sort_values(by='Time')
        for i in range(len(route_df) - 1):
            row_a = route_df.iloc[i]
            row_b = route_df.iloc[i + 1]
            time_a = row_a['Time']
            time_b = row_b['Time']
            dt_a = datetime.combine(datetime.today(), time_a)
            dt_b = datetime.combine(datetime.today(), time_b)
            if dt_b < dt_a:
                dt_b += timedelta(days=1)
            duration = (dt_b - dt_a).total_seconds() / 60.0
            if duration >= 0:
                G.add_edge((row_a['Stop Location'], time_a), (row_b['Stop Location'], time_b), weight=duration, route=route, town=row_a['Town'])
    return G

def add_transfers(G, df):
    for stop, group in df.groupby('Stop Location'):
        times = sorted(group['Time'].dropna().unique())
        for i in range(len(times) - 1):
            t1 = times[i]
            t2 = times[i + 1]
            dt1 = datetime.combine(datetime.today(), t1)
            dt2 = datetime.combine(datetime.today(), t2)
            if dt2 < dt1:
                dt2 += timedelta(days=1)
            wait = (dt2 - dt1).total_seconds() / 60.0
            if wait > 0:
                G.add_edge((stop, t1), (stop, t2), weight=wait, route='Transfer', town=group.iloc[0]['Town'])
