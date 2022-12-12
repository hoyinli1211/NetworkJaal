#20221209 - streamlit with network visualization
#Ref: https://medium.com/towards-data-science/how-to-deploy-interactive-pyvis-network-graphs-on-streamlit-6c401d4c99db

#import required library
import streamlit as st
import streamlit.components.v1 as components
import os, sys
import pandas as pd
import numpy as np
from jaal import Jaal
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

st.write(df_edge)

df_edge['weight'] = df_edge.apply (lambda row: len(str(row.Amount)), axis=1)
df_edge['title'] = df_edge.apply (lambda row: row.from + ' transferred HK$' + str(row.Amount) + ' to ' + row.to, axis=1)

Jaal(df_edge, df_node).plot()

   
#End of Script  
