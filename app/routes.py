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

                    # Build readable path with inline explanation and transfers
                    full_path = []
                    previous_route = None

                    for i, (u, v) in enumerate(zip(path[:-1], path[1:])):
                        current_route = G[u][v].get('route')
                        u_time = u[1].strftime('%H:%M')

                        if i == 0:
                            full_path.append({
                                'type': 'stop',
                                'stop': u[0],
                                'time': u_time,
                                'route': current_route,
                                'description': f"Start at {u[0]} via Route {current_route} at {u_time}"
                            })

                        if previous_route is not None and current_route != previous_route:
                            full_path.append({
                                'type': 'transfer',
                                'from_stop': u[0],
                                'to_stop': v[0],
                                'time': u_time,
                                'route': current_route,
                                'description': f"Transfer from Route {previous_route} to Route {current_route} at {u[0]}"
                            })

                        full_path.append({
                            'type': 'stop',
                            'stop': v[0],
                            'time': v[1].strftime('%H:%M'),
                            'route': current_route,
                            'description': f"Continue to {v[0]} via Route {current_route} at {v[1].strftime('%H:%M')}"
                        })

                        previous_route = current_route

                    results.append({
                        'path': full_path,
                        'duration': duration
                    })

                except nx.NetworkXNoPath:
                    continue

        if results and not show_multiple:
            break

    return sorted(results, key=lambda x: x['duration'])
