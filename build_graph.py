import json
import pyvis
from pyvis.network import Network
import networkx as nx
from collections import Counter

data = json.load(open("./network_data_standard.json"))

# data = {
#     "Martn Abadi": [("Stanford University", "PhD student"), ("Google", "Core Developer for Tensorflow"),
#                           ("College de France", "Temporary Professor for Computer Security"),
#                           ("University of Oxford", "Rhodes Scholar")],
#     "Charlie Ayers": [("Johnson & Wales University", "student"),
#                       ("Hilton Hotels", "Meadowlands and Parsippany locations in New Jersey"),
#                       ("Stoddard's Brewhouse", "Sunnyvale"), ("Left at Albuquerque", "unknown")],
#     "Shona Brown": [("University of Oxford", "Rhodes Scholar"),
#                     ("Stanford University", "Ph.D student and postdoctoral work"), ("Google", "Senior Vice President"),
#                     ("Atlassian", " Board Member")]
# }


def networkx_graph():
    """
    Create graph with whole data. No positions specified.
    """

    G = nx.DiGraph()
    connection_counter = Counter()
    node_counter = Counter()
    all_nodes = []

    for person, info in data.items():
        place_nodes = [e[0].lower() for e in info]
        G.add_nodes_from(place_nodes)

        all_nodes.extend(place_nodes)

        for i in range(len(place_nodes)-1):
            connection = (place_nodes[i], place_nodes[i + 1])
            connection_counter[connection] += 1
            node_counter[place_nodes[i]] += 1
            G.add_edge(place_nodes[i], place_nodes[i + 1])
        node_counter[place_nodes[-1]] += 1

    all_nodes = set(all_nodes)
    return G, all_nodes, connection_counter, node_counter

def find_relevant_nodes(query):
    """
    Find all nodes that are connected to the query node.
    """
    relevant_people = []
    highlighted_out_nodes = []
    highlighted_in_nodes = []
    for person, info in data.items():
        place_nodes = [e[0].lower() for e in info]
        concat_places = " ".join(place_nodes)
        if query != "" and query in concat_places:

            # search for index of query in place_nodes
            for count, node in enumerate(place_nodes):
                if query in node:
                    split_index = count
                    relevant_people.append(person)
                    highlighted_in_nodes.extend(place_nodes[:split_index])
                    highlighted_out_nodes.extend(place_nodes[split_index+1:])
                    break
            
    highlighted_in_nodes = set(highlighted_in_nodes)
    highlighted_out_nodes = set(highlighted_out_nodes)

    return query, relevant_people, highlighted_in_nodes, highlighted_out_nodes


def color_nodes_edges(net, query, highlighted_in_nodes, highlighted_out_nodes, in_network=False):
    print("coloring nodes....")
    print("query: ", query)
    if in_network:
        # highlighting relevant nodes
        for node in net.nodes:
            if query in node['id']:
                node['color'] = 'yellow'
                node['shape'] = 'star'
                node['size'] = 50

            elif node['id'] in highlighted_in_nodes:
                node['color'] = 'red'
                node['shape'] = 'dot'
                node['size'] = 1 # HANNA ATTN

            elif node['id'] in highlighted_out_nodes:
                node['color'] = 'blue'
                node['shape'] = 'dot'
                node['size'] = 1 # HANNA ATTN

            else:
                node['color'] = "#ddddff"
                node['shape'] = 'dot'
                node['size'] = 1 # HANNA ATTN
        
        # highlighting relevant edges
        for edge in net.edges:
            source_id = edge['from']
            if source_id in highlighted_in_nodes:
                edge['color'] = 'red'
            elif source_id in highlighted_out_nodes:
                edge['color'] = 'blue'
            else:
                edge['color'] = "#ddddff"

    else:
        for node in net.nodes:
            node['color'] = "#ddddff"
            node['shape'] = 'dot'
            node['size'] = 1

    return net

def most_common_path(net, query, node_counter, connection_counter):
    adj_list = net.get_adj_list()
    most_common_post = 0
    most_common_pre = 0
    most_common_pre_node = ""
    most_common_post_node = ""
    queried_node = ""
    for node in net.nodes:
        if query in node['id']:
            queried_node = node['id']
            break
    for adj_node in adj_list[queried_node]:
        edge_val = connection_counter[(queried_node, adj_node)]
        for edge in net.edges:
            if edge['from'] == queried_node and edge['to'] == adj_node:
                if edge_val > most_common_post:
                    most_common_post = edge_val
                    most_common_post_node = adj_node
            elif edge['to'] == queried_node and edge['from'] == adj_node:
                if edge_val > most_common_pre:
                    most_common_pre = edge_val
                    most_common_pre_node = adj_node
    percent_post = most_common_post / node_counter[queried_node]
    percent_pre = most_common_pre / node_counter[queried_node]
    return most_common_pre_node, most_common_post_node, most_common_pre, most_common_post, percent_pre, percent_post

def pyvis_graph():
    # Take Networkx graph and translate it to a PyVis graph format

    G, _, connection_counter, node_counter = networkx_graph()

    net = Network(directed=True, height='600px', width="800px", bgcolor='#222222', font_color='white')
    net.from_nx(G)
    net.repulsion(node_distance=420, central_gravity=0.5,
                  spring_length=110, spring_strength=0.10,
                  damping=0.95)

    # set smooth edges to avoid re-rendering
    net.set_edge_smooth("Dynamic")

    # adding node size and labels based on number of people with connection
    for edge in net.edges:
        source_id = edge['from']
        target_id = edge['to']
        weight = connection_counter[(source_id, target_id)]
        edge['title'] = f"{source_id} to {target_id}: {weight} people"

    for node in net.nodes:
        num_people = node_counter[node['id']]
        # node['size'] = num_people * 0.5 + 1 # set node size, HANNA ATTN
        node['title'] = f"People at {node['id']}: {num_people}"
        
    return net, node_counter, connection_counter