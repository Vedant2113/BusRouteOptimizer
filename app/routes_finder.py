from datetime import datetime
import networkx as nx

def find_transfer_path(start, end, start_time, G, df):
    candidates = [(s, t) for s, t in G.nodes if s == start and t >= start_time]
    targets = [(s, t) for s, t in G.nodes if s == end]
    shortest_path = None
    shortest_cost = float('inf')
    best_start_time = None

    for start_node in candidates:
        for end_node in targets:
            try:
                path = nx.dijkstra_path(G, start_node, end_node, weight='weight')
                cost = sum(G[path[i]][path[i + 1]]['weight'] for i in range(len(path) - 1))
                if cost < shortest_cost:
                    shortest_cost = cost
                    shortest_path = path
                    best_start_time = start_node[1]
            except nx.NetworkXNoPath:
                continue

    if not shortest_path:
        return "No path found"

    result = []
    for i in range(len(shortest_path) - 1):
        stop, t = shortest_path[i]
        next_stop, t2 = shortest_path[i + 1]
        edge = G[shortest_path[i]][shortest_path[i + 1]]
        result.append({
            'stop': stop,
            'town': edge['town'],
            'route': edge['route'],
            'time': t.strftime("%H:%M"),
            'transfer': edge['route'] == 'Transfer'
        })

    final_stop, final_time = shortest_path[-1]
    final_town = df[df['Stop Location'] == final_stop]['Town'].iloc[0] if not df[df['Stop Location'] == final_stop].empty else '-'
    result.append({
        'stop': final_stop,
        'town': final_town,
        'route': result[-1]['route'] if result else '-',
        'time': final_time.strftime("%H:%M"),
        'transfer': False
    })

    return result, int(shortest_cost), best_start_time
