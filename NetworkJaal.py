#20221209 - streamlit with network visualization
#Ref: https://medium.com/towards-data-science/how-to-deploy-interactive-pyvis-network-graphs-on-streamlit-6c401d4c99db

#import required library
import streamlit as st
import streamlit.components.v1 as components
import os, sys
import pandas as pd
import numpy as np
from jaal import Jaal
import networkx as nx
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

G1 = nx.from_pandas_edgelist(df=df_edge_fraud, source='Orig', target='Dest', edge_attr=['weight', 'title'], create_using=nx.DiGraph())

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
    edge_x, edge_y = addEdge(start, end, edge_x, edge_y, .8, 'end', .04, 30, nodeSize)
    

edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=lineWidth, color=lineColor), hoverinfo='none', mode='lines', text=text)


node_trace = go.Scatter(x=node_x, y=node_y, text=text,mode='markers+text', hoverinfo='text', marker=dict(showscale=False, color = nodeColor, size=nodeSize))



#End of Script  
