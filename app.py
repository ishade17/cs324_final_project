import streamlit as st
import build_graph
import streamlit.components.v1 as components


st.title('Network Graph Visualization of Career Paths')
query = st.text_input('Search by univerity or company name')

G, all_nodes, highlighted_nodes, relevant_people, connection_counter = build_graph.networkx_graph(query)

net = None
net = build_graph.pyvis_graph(query)
if query != "":
    if query in all_nodes:
        st.write(f"Career paths containing {query}: {len(relevant_people)}. Relevant paths in red.")
        net = build_graph.color_nodes(net,  query, highlighted_nodes, in_network=True)
        html = net.save_graph("career_graph.html")
    else:
        st.write(f"No results found. Try a different search.")
        net = build_graph.color_nodes(net,  query, highlighted_nodes)
        html = net.save_graph("career_graph.html")

    with open('career_graph.html', 'r') as HtmlFile:
        components.html(HtmlFile.read(), height=435)

    if len(relevant_people) != 0:
        st.write("Most notable people at ", query, ":")
        for p in relevant_people:
            st.markdown("- " + p)
