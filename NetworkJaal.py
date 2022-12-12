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
from pyvis.network import Network
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

df_onus = pd.concat([df_edge.loc[df_edge['Orig.Bank']=='on-us']['Orig'],
                    df_edge.loc[df_edge['Dest.Bank']=='on-us']['Dest']],
                    axis=0).drop_duplicates().rename('name').to_frame().reset_index()

df_offus = pd.concat([df_edge.loc[df_edge['Orig.Bank']!='on-us']['Orig'],
                    df_edge.loc[df_edge['Dest.Bank']!='on-us']['Dest']],
                    axis=0).drop_duplicates().rename('name').to_frame().reset_index()

st.title('Transaction Data')
st.write(df_edge)

#Define show first layer only, or second layer as well
#nlayer = st.radio("Number of layer",
#                 ('first layer only', 'with second layer'))

#Define list of selection options
acct_list = df_node['name']
onus_list = df_onus['name']
offus_list = df_offus['name']

#Implement multiselect dropdown menu for option selection (returns a list)
#selected_acct = st.multiselect('Select acct(s) to visualize', acct_list)
selected_onus_acct = st.multiselect('Select on-us acct(s) to visualize', onus_list, ['A001'])
selected_offus_acct = st.multiselect('Select off-us acct(s) to visualize', offus_list, ['V001'])

#Amount threshold slider
threshold_amt = st.slider(label='Transaction amount minimum threshold (inclusive >=)', 
                          min_value=0, 
                          max_value=100000,
                          value=1,
                         step=100)
df_edge = df_edge.loc[df_edge['Amount']>=threshold_amt]

#Task Radio button
taskRadio = st.radio(label='Area of interest',
                    options = ['1. Transaction(s) involved selected subject(s) only',
                                '2. Direct Transaction(s) with selected subject(s)',
                                '3. Indirect Transaction(s) with selected subject(s) - first layer expand'])

if (len(selected_onus_acct)==0 and len(selected_offus_acct)==0):
  st.text('Choose at least 1 onus/offus account to get started.')
elif (len(selected_onus_acct)>0 or len(selected_offus_acct)>0):
  #Transactions only involve between two selected subjects
  fraudlayer_acct = selected_onus_acct + selected_offus_acct
  df_edge_fraud = df_edge.loc[df_edge['Orig'].isin(fraudlayer_acct) & df_edge['Dest'].isin(fraudlayer_acct)]
  onusN_1 = len(selected_onus_acct)
  offusN_1 = len(selected_offus_acct)
  amt_1 = df_edge_fraud['Amount'].sum()
  remarks_1 = str(onusN_1) + ' [' + ','.join(selected_onus_acct) + '] on-us customer(s) had payment(s) to/from ' + str(offusN_1) + ' [' + ','.join(selected_offus_acct) + '] off-us customer(s) amounting HK$' + str(amt_1)
  
  #Expand 1 layer
  firstlayer_acct = fraudlayer_acct
  df_edge_firstlayer = df_edge.loc[df_edge['Orig'].isin(firstlayer_acct) | df_edge['Dest'].isin(firstlayer_acct)]
  firstlayer_onus_acct = pd.concat([df_edge_firstlayer.loc[df_edge_firstlayer['Orig.Bank']=='on-us']['Orig'].drop_duplicates(),
                         df_edge_firstlayer.loc[df_edge_firstlayer['Dest.Bank']=='on-us']['Dest'].drop_duplicates()], axis=0).drop_duplicates().rename('name')
  firstlayer_onus_acct = firstlayer_onus_acct.tolist()
  firstlayer_new_onus_acct = list(set(firstlayer_onus_acct)-set(fraudlayer_acct))
  newonusN_2 = len(firstlayer_new_onus_acct)
  remarks2 = str(newonusN_2) + ' additional customer(s) were identified [' + ','.join(firstlayer_new_onus_acct) + ']'

  #Expand 1 further layer
  secondlayer_acct = pd.concat([df_edge_firstlayer['Orig'], df_edge_firstlayer['Dest']], ignore_index=True, axis=0).drop_duplicates().rename('name')
  df_edge_secondlayer = df_edge.loc[df_edge['Orig'].isin(secondlayer_acct) | df_edge['Dest'].isin(secondlayer_acct)]
  secondlayer_onus_acct = pd.concat([df_edge_secondlayer.loc[df_edge_secondlayer['Orig.Bank']=='on-us']['Orig'].drop_duplicates(),
                         df_edge_secondlayer.loc[df_edge_secondlayer['Dest.Bank']=='on-us']['Dest'].drop_duplicates()], axis=0).drop_duplicates().rename('name')
  secondlayer_onus_acct = secondlayer_onus_acct.tolist()
  secondlayer_new_onus_acct = list(set(secondlayer_onus_acct)-set(firstlayer_onus_acct))
  newonusN_3 = len(secondlayer_new_onus_acct)
  remarks3 = str(newonusN_3) + ' additional customer(s) were identified [' + ','.join(secondlayer_new_onus_acct) + ']'
  
  if taskRadio == '1. Transaction(s) involved selected subject(s) only':
    st.title('1. Fraudulent transaction(s) involved selected on-us and off-us account(s)')
    st.write(remarks_1)
    st.write(df_edge_fraud)
    G1 = nx.from_pandas_edgelist(df=df_edge_fraud, source='Orig', target='Dest', edge_attr=['weight', 'title'], create_using=nx.DiGraph())
    net1 = Network(height='465px', bgcolor='#222222', font_color='white', directed=True)
    # Take Networkx graph and translate it to a PyVis graph format
    net1.from_nx(G1)
    net1.save_graph(f'pyvis_graph.html')
    HtmlFile1 = open(f'pyvis_graph.html', 'r', encoding='utf-8')
    components.html(HtmlFile1.read(), height=435)
  elif taskRadio == '2. Direct Transaction(s) with selected subject(s)':
    st.title('2. Direct Transaction(s) with selected subject(s)')
    st.write(remarks2)
    st.write(df_edge_firstlayer)
    G2 = nx.from_pandas_edgelist(df_edge_firstlayer, source='Orig', target='Dest', edge_attr=['weight', 'title'], create_using=nx.DiGraph())
    #nx.set_node_attributes(G2, dict(G2.degree), 'size')
    nx.set_node_attributes(G2, pd.Series(['blue','red','red','orange','blue','blue','orange']).to_dict(), 'color')
    net2 = Network(height='465px', bgcolor='#222222', font_color='white', directed=True)
    net2.from_nx(G2)
    net2.save_graph(f'pyvis_graph.html')
    HtmlFile2 = open(f'pyvis_graph.html', 'r', encoding='utf-8')
    components.html(HtmlFile2.read(), height=435)
  elif taskRadio == '3. Indirect Transaction(s) with selected subject(s) - first layer expand':
    st.title('2. Indirect Transaction(s) with selected subject(s)')
    st.write(remarks3)
    st.write(df_edge_secondlayer)
    G3 = nx.from_pandas_edgelist(df_edge_secondlayer, source='Orig', target='Dest', edge_attr=['weight', 'title'], create_using=nx.DiGraph())
    #nx.set_node_attributes(G2, dict(G2.degree), 'size')
    nx.set_node_attributes(G3, pd.Series(['blue','red','red','orange','blue','blue','orange']).to_dict(), 'color')
    net3 = Network(height='465px', bgcolor='#222222', font_color='white', directed=True)
    net3.from_nx(G3)
    net3.save_graph(f'pyvis_graph.html')
    HtmlFile3 = open(f'pyvis_graph.html', 'r', encoding='utf-8')
    components.html(HtmlFile3.read(), height=435)
  else:
    pass
    
  #Transactions only involve third layer subjects
  thirdlayer_acct = pd.concat([df_edge_secondlayer['Orig'], df_edge_secondlayer['Dest']], ignore_index=True, axis=0).drop_duplicates().rename('name')
  df_edge_thirdlayer = df_edge.loc[df_edge['Orig'].isin(thirdlayer_acct) | df_edge['Dest'].isin(thirdlayer_acct)]
  
else:
  pass
   
#End of Script  
