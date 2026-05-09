import os
import re
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from pyvis.network import Network

def get_imports(filepath):
    imports = []
    pattern = re.compile(r'import\s+(?:.*?\s+from\s+)?[\'"](.*?)[\'"]')
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                imports.append(match.group(1))
    return imports

def build_graph(directory):
    G = nx.DiGraph()
    base_dir = Path(directory)

    for filepath in base_dir.rglob('*.types.[jt]s*'):
        if 'node_modules' in filepath.parts or 'dist' in filepath.parts:
            continue

        file_node = str(filepath.relative_to(base_dir))
        G.add_node(file_node)

        imports = get_imports(filepath)
        for imp in imports:
            if imp.startswith('.'):
                resolved_path = (filepath.parent / imp).resolve()
                try:
                    target_node = str(resolved_path.relative_to(base_dir.resolve()))
                    G.add_edge(file_node, target_node)
                except ValueError:
                    pass

    return G

def visualize_graph(G):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=4, iterations=20)
    
    nx.draw(
        G, pos, 
        with_labels=True, 
        node_size=10, 
        font_size=6, 
        edge_color='gray', 
        node_color='skyblue', 
        alpha=0.4,
        arrows=True,
        arrowsize=5
    )
    
    plt.title("Dependency Graph")
    plt.show()

if __name__ == "__main__":
    target_directory = "D:\\JoshFile\\Github\\e-coop-client\\src\\modules"
    graph = build_graph(target_directory)
    
    # cycles = list(nx.simple_cycles(graph))
    # if cycles:
    #     print(f"Found {len(cycles)} circular dependencies:")
    #     for cycle in cycles:
    #         print(" -> ".join(cycle) + " -> " + cycle[0])
            
    # visualize_graph(graph)

    graph = build_graph(target_directory)
    
    # Create an interactive web network
    net = Network(height="1000px", width="100%", directed=True, bgcolor="#222222", font_color="white")
    
    # Pyvis has a built-in solver for network layouts
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=200)
    
    # Load the NetworkX graph into Pyvis
    net.from_nx(graph)
    
    # Generate and open the HTML file
    net.show("dependency_graph.html", notebook=False)