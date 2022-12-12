#20221212 - streamlit with network visualization using Dash
#Ref: https://community.plotly.com/t/dash-networkx-digraph-highlight-descendants-and-ancestors-paths-on-existing-graph/68660
#Ref: https://towardsdatascience.com/python-interactive-network-visualization-using-networkx-plotly-and-dash-e44749161ed7

#import required library
import streamlit as st
import streamlit.components.v1 as components
import os, sys
import pandas as pd
import numpy as np
from jaal import Jaal
import networkx as nx
from addEdge import addEdge
import dash
from dash import Dash, html, dcc, Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
#import networkx as nx
#from pyvis.network import Network
import matplotlib.pyplot as plt
import math

#initialization of session state
if 'indEnd' not in st.session_state:
  st.session_state['ind0'] = False
  
# Add a title and intro text
st.title('Fund Flow Network Visualization using streamlit')
st.text('This is the first attempt to use Jaal package to perform interactive network visualization in streamlit platform')

#Import template file
file_temp = 'Network1.xlsx'
df_node_temp = pd.read_excel(file_temp, 'node')
df_edge_temp = pd.read_excel(file_temp, 'edge')

df_node = df_node_temp
df_edge = df_edge_temp

df_edge['weight'] = df_edge.apply (lambda row: len(str(row.Amount)), axis=1)
df_edge['title'] = df_edge.apply (lambda row: row.Orig + ' transferred HK$' + str(row.Amount) + ' to ' + row.Dest, axis=1)

G = nx.from_pandas_edgelist(df=df_edge, source='Orig', target='Dest', edge_attr=['weight', 'title'], create_using=nx.DiGraph())

pos = nx.layout.spring_layout(G)
for node in G.nodes:
    G.nodes[node]['pos'] = list(pos[node])
    
# Make list of nodes for plotly
node_x = []
node_y = []
text = []
for node in G.nodes():
    x, y = G.nodes[node]['pos']
    node_x.append(x)
    node_y.append(y)
    text.append(node)
    
edge_x = []
edge_y = []
for edge in G.edges():
    start = G.nodes[edge[0]]['pos']
    end = G.nodes[edge[1]]['pos']
    edge_x, edge_y = add_edge(start, end)
    
edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=lineWidth, color=lineColor), hoverinfo='none', mode='lines', text=text)
node_trace = go.Scatter(x=node_x, y=node_y, text=text,mode='markers+text', hoverinfo='text', marker=dict(showscale=False, color = nodeColor, size=nodeSize))

fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                )
             
# Note: if you don't use fixed ratio axes, the arrows won't be symmetrical
fig.update_layout(yaxis = dict(scaleanchor = "x", scaleratio = 1), plot_bgcolor='rgb(255,255,255)')
    
app = dash.Dash()
app.layout = html.Div([
    html.Div([
        html.H1(children='Hello Dash'),

        html.Div(children='''
        Directed Water and Orange Juice Graph.
         '''),
        html.Div(  children=[

            dcc.Dropdown([{'label': 'Connected', 'value': 'con'},{'label': 'Ascending', 'value': 'asc'},{'label': 'Descending', 'value': 'desc'}], '', id='typ-dropdown'),
            html.Div(id='dd-typ-container'),
            html.Div(html.Br()),
            dcc.Dropdown([{'label': 'Node A', 'value': 0},{'label': 'Node B', 'value': 1},{'label': 'Node C', 'value': 2},{'label': 'Node D', 'value': 3},{'label': 'Node A1', 'value': 4},{'label': 'Node B1', 'value': 5},{'label': 'Node C1', 'value': 6}], '', id='node-dropdown'),
            html.Div(id='dd-out-container')
            
            ]),

        html.Div([
            html.H3('Water Network'),

            dcc.Graph(id='example-graph1', figure=fig),
                        # dcc.Graph(id='example-graph', figure=fig)

        ], className="six columns"),

        html.Div([
            

            # dcc.Graph(id='example-graph2', figure=fig)
        ], className="six columns"),
    ], className="row")
])


# @app.callback(
#     Output('dd-out-container', 'children'),
#     Input('fig-dropdown', 'value')
# )
# def update_output(value):
#     return f'you have selected {value}'

@app.callback(
    Output('example-graph1', 'children'),
    Input('typ-dropdown', 'value'),
    Input('node-dropdown', 'value')
)

def connected_graph(contyp, value):
    desc = nx.descendants(G,value)
    anc = nx.ancestors(G,value)
    if contyp == 'desc':
        paths = [path for p in desc for path in nx.all_simple_paths(G,value,p)]
    elif contyp == 'anc':
        paths = [path for p in anc for path in nx.all_simple_paths(G,value,p)]
    elif contyp == 'con_':
        paths = [path for p in desc for path in nx.all_simple_paths(G,value,p)]
        paths.extend([path for p in anc for path in nx.all_simple_paths(G,p,value)])

    Q = nx.DiGraph()
    for p in paths:
        nx.add_path(Q,p)

    return Q


app.run_server(debug=True)

#End of Script  
