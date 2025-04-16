# app/routes.py
from datetime import datetime
import networkx as nx

def find_shortest_route(G, start, end, time_str, optimize):
    start_time = datetime.strptime(time_str, '%H:%M').time()
    start_nodes = [n for n in G.nodes if n[0] == start and n[1] >= start_time]
    if not start_nodes:
        return None

    best_path = None
    best_duration = float('inf')

    for start_node in start_nodes:
        try:
            end_candidates = [n for n in G.nodes if n[0] == end]
            for end_node in end_candidates:
                path = nx.dijkstra_path(G, source=start_node, target=end_node)
                duration = sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
                if duration < best_duration:
                    best_path = path
                    best_duration = duration
        except:
            continue

    if best_path:
        readable_path = [{'stop': node[0], 'time': node[1].strftime('%H:%M')} for node in best_path]
        return {'path': readable_path, 'duration': best_duration}
    return None
