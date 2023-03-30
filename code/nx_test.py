import networkx as nx

# Create an undirected graph
G = nx.Graph()

# Add nodes and edges to the graph
G.add_edges_from([(1, 2), (2, 3), (3, 1), (4, 5), (5, 6)])

# Find connected components
connected_components = nx.connected_components(G)

# Print connected components
for idx, component in enumerate(connected_components, start=1):
    print(f"Connected Component {idx}: {component}")

