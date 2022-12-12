#20221209 - streamlit with network visualization
#Ref: https://medium.com/towards-data-science/how-to-deploy-interactive-pyvis-network-graphs-on-streamlit-6c401d4c99db

#import required library
import streamlit as st
import streamlit.components.v1 as components
import os, sys
import pandas as pd
import numpy as np
from jaal import Jaal
import dash
import dash_core_components as dcc
import dash_html_components as html
#import networkx as nx
#from pyvis.network import Network
import matplotlib.pyplot as plt
import math

def get_unused_port():
    """
    Get an empty port for the Pyro nameservr by opening a socket on random port,
    getting port number, and closing it [not atomic, so race condition is possible...]
    Might be better to open with port 0 (random) and then figure out what port it used.
    """
    so = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    so.bind(('localhost', 0))
    _, port = so.getsockname()
    so.close()
    return port 

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
#df_edge['title'] = df_edge.apply (lambda row: row.from + ' transferred HK$' + str(row.Amount) + ' to ' + row.to, axis=1)

st.write(df_edge)
st.write(df_node)

port=get_unused_port()
while True:
    try:
        Jaal(edge_df, node_df).plot(port=port)
    except:
        port+=1
        st.write(port)
#app = Jaal(df_edge, df_node).plot()
#server = app.server
   
#End of Script  
