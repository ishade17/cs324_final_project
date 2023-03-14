import streamlit as st
import build_graph
import streamlit.components.v1 as components
import openai

openai.api_key = "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"

def load_UI():
    st.title('Graph Visualization of Career Paths')

@st.cache_resource
def construct_graph():
    net, node_counter, connection_counter = build_graph.pyvis_graph()
    return net, node_counter, connection_counter

def query_preprocessing(query):
    query = query.lower()
    query.replace("  ", " ")
    return query

def call_chatgpt(prompt):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content

def load_search(query, net, node_counter, connection_counter):
    _, relevant_people, highlighted_in_nodes, higlighted_out_nodes = build_graph.find_relevant_nodes(query)
    all_nodes = set(net.get_nodes())
    if query != "":
        if query in " ".join(all_nodes):
            st.subheader(f"Career paths containing {query}: {len(relevant_people)}")
            st.write("In-paths in red. Out-paths in blue.")
            net = build_graph.color_nodes_edges(net,  query, highlighted_in_nodes, higlighted_out_nodes, in_network=True)
            html = net.save_graph("career_graph.html")
        else:
            st.write(f"No results found. Try a different search.")
            net = build_graph.color_nodes_edges(net,  query, highlighted_in_nodes, higlighted_out_nodes)
            html = net.save_graph("career_graph.html")

        with open('career_graph.html', 'r') as HtmlFile:
            components.html(HtmlFile.read(), height=500)

        # find most common before & after nodes
        most_common_pre_node, most_common_post_node, _, _, percent_pre, percent_post = build_graph.most_common_path(net, query, node_counter, connection_counter)

        query = query.capitalize()
        prompt = f"Give 3 bullet points of advice on how to get to {query}, given that the most common working experience before this is {most_common_pre_node}."
        generation = call_chatgpt(prompt)
        st.subheader(f"Advice on getting to {query}:")
        st.write(f"The most common experience before {query} is {most_common_pre_node.capitalize()}, with {round(percent_pre, 3)*100}% of {query} coming from {most_common_pre_node.capitalize()} directly. After {query}, {round(percent_post, 3)*100}% go to {most_common_post_node.capitalize()}.")
        st.write(f"\nHere's some advice for getting to {query}:\n")
        st.write(generation)

        if len(relevant_people) != 0:
            st.subheader(f"Notable people at {query}:")
            for p in relevant_people:
                st.markdown("- " + p)
        

if __name__ == '__main__':
    load_UI()
    query = st.text_input('Search by univerity or company name')
    query = query_preprocessing(query)
    net, node_counter, connection_counter = construct_graph()
    load_search(query,net, node_counter, connection_counter)