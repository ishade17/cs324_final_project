import json
import pyvis
from pyvis.network import Network
import networkx as nx
from collections import Counter


def query_preprocessing(query):
    query = query.lower()
    query.replace("  ", " ")
    return query

def networkx_graph(query):
    """
    Create graph with whole data. No positions specified.
    """
    data = json.load(open("./network_data_clean.json"))

    # data ={
    #     "Mart\u00edn Abadi": [("Stanford University", "PhD student"), ("Google", "Core Developer for Tensorflow"), ("Coll\u00e8ge de France", "Temporary Professor for Computer Security"),("University of Oxford", "Rhodes Scholar")],
    #     "Charlie Ayers": [("Johnson & Wales University", "student"), ("Hilton Hotels", "Meadowlands and Parsippany locations in New Jersey"), ("Stoddard's Brewhouse", "Sunnyvale"), ("Left at Albuquerque", "unknown")],
    #     "Shona Brown": [("University of Oxford", "Rhodes Scholar"), ("Stanford University", "Ph.D student and postdoctoral work"), ("Google", "Senior Vice President"), ("Atlassian"," Board Member")]
    # }

    query = query_preprocessing(query)
    G = nx.DiGraph()
    connection_counter = Counter()
    all_nodes = []
    highlighted_nodes = []
    relevant_people = []
    for person, info in data.items():
        place_nodes = [e[0].lower() for e in info]
        n = len(place_nodes)
        G.add_nodes_from(place_nodes)

        all_nodes.extend(place_nodes)
        if query != "" and query in place_nodes:
            relevant_people.append(person)
            highlighted_nodes.extend(place_nodes)

        for i in range(n - 1):
            connection = (place_nodes[i], place_nodes[i + 1])
            connection_counter[connection] += 1
            G.add_edge(place_nodes[i], place_nodes[i + 1])

        # for i in range(n - 1):

    all_nodes = set(all_nodes)
    highlighted_nodes = set(highlighted_nodes)
    print(highlighted_nodes)

    return G, all_nodes, highlighted_nodes, relevant_people, connection_counter

def color_nodes(net, query, highlighted_nodes, in_network=False):
    if in_network:
        # highlighting relevant nodes
        for node in net.nodes:
            if node['id'] == query:
                node['shape'] = 'star'
                node['color'] = 'red'
                node['size'] = 50
            if node['id'] in highlighted_nodes:
                node['color'] = 'red'
            else:
                node['color'] = "#ddddff"
    else:
        for node in net.nodes:
            node['color'] = "#ddddff"

    return net


def pyvis_graph(query):
    # Take Networkx graph and translate it to a PyVis graph format

    G, all_nodes, highlighted_nodes, relevant_people, connection_counter = networkx_graph(query)

    net = Network(directed=True, height='600px', width="800px", bgcolor='#222222', font_color='white')
    net.repulsion(node_distance=420, central_gravity=0.5,
                  spring_length=110, spring_strength=0.10,
                  damping=0.95)
    net.from_nx(G)

    # adding edge thickness and labels based on number of people with connection
    for edge in net.edges:
        source_id = edge['from']
        target_id = edge['to']
        weight = connection_counter[(source_id, target_id)]
        edge['value'] = weight
        edge['width'] = weight
        edge['title'] = f"{source_id} to {target_id}: {weight} people"

    return net

#
# def final_graph(query):

#
#     # query = "Stanford University"
#     G, all_nodes, highlighted_nodes, relevant_people, connection_counter = networkx_graph(query, data)
#     net = highlighted_graph(query, G, all_nodes, highlighted_nodes, connection_counter)
#     # net.show("my_network.html", notebook=False)
#
#     return net, relevant_people, all_nodes
