import streamlit as st
import build_graph
import streamlit.components.v1 as components

def load_UI():
    st.title('Graph Visualization of Career Paths')

@st.cache_data
def construct_graph(query):
    net = build_graph.pyvis_graph(query)
    return net

def query_preprocessing(query):
    query = query.lower()
    query.replace("  ", " ")
    return query

def load_search(query, net):
    _, relevant_people, highlighted_in_nodes, higlighted_out_nodes = build_graph.find_relevant_nodes(query)
    all_nodes = set(net.get_nodes())
    if query != "":
        if query in all_nodes:
            st.subheader(f"Career paths containing {query}: {len(relevant_people)}")
            st.write("In-paths in red. Out-paths in blue.")
            net = build_graph.color_nodes(net,  query, highlighted_in_nodes, higlighted_out_nodes, in_network=True)
            html = net.save_graph("career_graph.html")
        else:
            st.write(f"No results found. Try a different search.")
            net = build_graph.color_nodes(net,  query, highlighted_in_nodes, higlighted_out_nodes)
            html = net.save_graph("career_graph.html")

        with open('career_graph.html', 'r') as HtmlFile:
            components.html(HtmlFile.read(), height=435)

        if len(relevant_people) != 0:
            st.subheader(f"Most notable people at {query}:")
            for p in relevant_people:
                st.markdown("- " + p)

if __name__ == '__main__':
    load_UI()
    query = st.text_input('Search by univerity or company name')
    query = query_preprocessing(query)
    net = construct_graph(query)
    load_search(query,net)