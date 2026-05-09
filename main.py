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
    base_dir = Path(directory).resolve()

    type_files = {}
    for filepath in base_dir.rglob('*.types.[jt]s*'):
        if 'node_modules' in filepath.parts or 'dist' in filepath.parts:
            continue
        
        resolved_path = filepath.resolve()
        node_name = str(filepath.relative_to(base_dir)).replace('\\', '/')
        type_files[resolved_path] = node_name
        G.add_node(node_name)

    for filepath, file_node in type_files.items():
        imports = get_imports(filepath)
        for imp in imports:
            if imp.startswith('.'):
                raw_path = (filepath.parent / imp).resolve()
                
                candidates = [
                    raw_path,
                    raw_path.with_name(f"{raw_path.name}.types.ts"),
                    raw_path.with_name(f"{raw_path.name}.types.js"),
                    raw_path / "index.types.ts",
                    raw_path / f"{raw_path.name}.types.ts"
                ]
                
                target_node = None
                for candidate in candidates:
                    if candidate in type_files:
                        target_node = type_files[candidate]
                        break
                        
                if not target_node and raw_path.is_dir():
                    for known_path, known_node in type_files.items():
                        if known_path.parent == raw_path:
                            target_node = known_node
                            break
                            
                if target_node:
                    G.add_edge(file_node, target_node)

    return G

if __name__ == "__main__":
    target_directory = "D:\\JoshFile\\Github\\e-coop-client\\src\\modules"
    
    graph = build_graph(target_directory)
    
    net = Network(height="1000px", width="100%", directed=True, bgcolor="#222222", font_color="white")
    net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=200)
    net.from_nx(graph)
    net.show("dependency_graph.html", notebook=False)