# app/routes.py
from datetime import datetime
import networkx as nx

def find_shortest_routes(G, start, end, time_str, optimize="shortest", show_multiple=False):
    start_time = datetime.strptime(time_str, '%H:%M').time()
    all_times = sorted(set(n[1] for n in G.nodes if n[0] == start))

    # Prefer times >= start_time first, then fallback to earlier times if needed
    candidate_times = [t for t in all_times if t >= start_time] + [t for t in all_times if t < start_time]

    results = []
    seen_paths = set()

    for t in candidate_times:
        start_nodes = [n for n in G.nodes if n[0] == start and n[1] == t]
        for start_node in start_nodes:
            for end_node in [n for n in G.nodes if n[0] == end]:
                try:
                    path = nx.dijkstra_path(G, source=start_node, target=end_node, weight='weight')
                    duration = sum(G[u][v]['weight'] for u, v in zip(path[:-1], path[1:]))
                    path_signature = tuple((p[0], p[1]) for p in path)

                    if path_signature in seen_paths:
                        continue
                    seen_paths.add(path_signature)

                    transfers = []
                    previous_route = None
                    for u, v in zip(path[:-1], path[1:]):
                        current_route = G[u][v].get('route')
                        if current_route != previous_route:
                            transfers.append({
                                'from_stop': u[0],
                                'to_stop': v[0],
                                'time': u[1].strftime('%H:%M'),
                                'route': current_route
                            })
                        previous_route = current_route

                    readable_path = [{'stop': node[0], 'time': node[1].strftime('%H:%M')} for node in path]
                    results.append({
                        'path': readable_path,
                        'duration': duration,
                        'transfers': transfers
                    })
                except nx.NetworkXNoPath:
                    continue

        if results and not show_multiple:
            break

    return sorted(results, key=lambda x: x['duration'])
