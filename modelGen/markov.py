import networkx as nx
import matplotlib.pyplot as plt
import utils


def measure_markov_property(data, name, addr):
    G = nx.MultiDiGraph()
    edge_labels = {}
    for src in data.keys():
        for dst in data[src].keys():
            G.add_edge(str(src), str(dst), weight=data[src][dst], len=1000, label=str(data[src][dst]))
            edge_labels[(str(src), str(dst))] = str("{:.3f}".format(data[src][dst]))
    fig, ax = plt.subplots(figsize=(20, 20))
    pos = nx.spring_layout(G, seed=50)
    nx.draw_networkx_nodes(G, pos, node_size=2000, edgecolors='blue', node_color='blue')
    nx.draw_networkx_labels(G, pos)
    """arc_rad = 0.2
    edge_color = [1]*len(G.edges)
    nx.draw_networkx_edges(G, pos, ax=ax, connectionstyle=f'arc3, rad = {arc_rad}', width=2, edge_color=edge_color, arrowsize=20)"""
    nx.draw(G, pos, edge_color='black', width=2, linewidths=2, node_size=2000, alpha=0.9, labels={node: node for node in G.nodes()})
    nx.draw_networkx_edge_labels(G, pos=pos, ax=ax, edge_labels=edge_labels, font_color='red')
    plt.tight_layout()
    plt.savefig(addr + "_markov_" + name + ".jpg")
    plt.close()


def measure_markov_property_wrapper(items, name, addr):
    data = {}
    prev = 0
    for item in items:
        if item not in data.keys():
            data.setdefault(item, {})
            prev = item
        else:
            if item not in data[prev].keys():
                data[prev][item] = 1
            else:
                data[prev][item] += 1
            prev = item
    markov = {}
    for src in data.keys():
        pdf, _ = utils.generate_pdf_cdf(data[src])
        markov[src] = pdf
    measure_markov_property(markov, name, addr)