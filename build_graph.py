import json
import pyvis
from pyvis.network import Network
import networkx as nx
from collections import Counter

data = json.load(open("./network_data_standard.json"))

def networkx_graph():
    """
    Create graph with whole data. No positions specified.
    """

    # data ={
    #     "Mart\u00edn Abadi": [("Stanford University", "PhD student"), ("Google", "Core Developer for Tensorflow"), ("Coll\u00e8ge de France", "Temporary Professor for Computer Security"),("University of Oxford", "Rhodes Scholar")],
    #     "Charlie Ayers": [("Johnson & Wales University", "student"), ("Hilton Hotels", "Meadowlands and Parsippany locations in New Jersey"), ("Stoddard's Brewhouse", "Sunnyvale"), ("Left at Albuquerque", "unknown")],
    #     "Shona Brown": [("University of Oxford", "Rhodes Scholar"), ("Stanford University", "Ph.D student and postdoctoral work"), ("Google", "Senior Vice President"), ("Atlassian"," Board Member")]
    # }

    G = nx.DiGraph()
    connection_counter = Counter()
    all_nodes = []

    for person, info in data.items():
        place_nodes = [e[0].lower() for e in info]
        G.add_nodes_from(place_nodes)

        all_nodes.extend(place_nodes)

        for i in range(len(place_nodes)-1):
            connection = (place_nodes[i], place_nodes[i + 1])
            connection_counter[connection] += 1
            G.add_edge(place_nodes[i], place_nodes[i + 1], color=('red', 'blue'))

    all_nodes = set(all_nodes)

    return G, all_nodes, connection_counter

def find_relevant_nodes(query):
    """
    Find all nodes that are connected to the query node.
    """
    relevant_people = []
    highlighted_out_nodes = []
    highlighted_in_nodes = []
    for person, info in data.items():
        place_nodes = [e[0].lower() for e in info]

        if query != "" and query in place_nodes:
            split_index = place_nodes.index(query)
            relevant_people.append(person)
            highlighted_in_nodes.extend(place_nodes[:split_index])
            highlighted_out_nodes.extend(place_nodes[split_index+1:])
    
    highlighted_in_nodes = set(highlighted_in_nodes)
    highlighted_out_nodes = set(highlighted_out_nodes)
    return relevant_people, highlighted_in_nodes, highlighted_out_nodes


def color_nodes(net, query, highlighted_in_nodes, highlighted_out_nodes, in_network=False):
    if in_network:
        # highlighting relevant nodes
        for node in net.nodes:
            if node['id'] == query:
                node['shape'] = 'star'
                node['color'] = 'red'
                node['size'] = 50
            if node['id'] in highlighted_in_nodes:
                node['color'] = 'red'
            elif node['id'] in highlighted_out_nodes:
                node['color'] = 'blue'
            else:
                node['color'] = "#ddddff"
    else:
        for node in net.nodes:
            node['color'] = "#ddddff"

    return net


def pyvis_graph():
    # Take Networkx graph and translate it to a PyVis graph format

    G, _, connection_counter = networkx_graph()

    net = Network(directed=True, height='600px', width="800px", bgcolor='#222222', font_color='white')
    net.from_nx(G)
    net.repulsion(node_distance=420, central_gravity=0.5,
                  spring_length=110, spring_strength=0.10,
                  damping=0.95)

    # adding edge thickness and labels based on number of people with connection
    for edge in net.edges:
        source_id = edge['from']
        target_id = edge['to']
        weight = connection_counter[(source_id, target_id)]
        edge['value'] = weight
        edge['width'] = weight
        edge['title'] = f"{source_id} to {target_id}: {weight} people"

    return net