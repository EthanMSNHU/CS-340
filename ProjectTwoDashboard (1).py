#!/usr/bin/env python
# coding: utf-8

# In[4]:


from jupyter_plotly_dash import JupyterDash
import dash
from dash import dcc, html  
import dash_leaflet as dl
import plotly.express as px
import dash_table as dt
from dash.dependencies import Input, Output, State
import os
import numpy as np
import pandas as pd
from pymongo import MongoClient
from bson.json_util import dumps
import re  # needed for regex pattern matching
import base64  # needed for images
from CRUD import AnimalShelter

###########################
# Data Manipulation / Model
###########################
username = "aacuser"
password = "Password"
shelter = AnimalShelter(username, password)  

# Create the default dataframe
df = pd.DataFrame.from_records(shelter.getRecordCriteria({}))

#########################
# Dashboard Layout / View
#########################
app = JupyterDash(__name__)  

# Add the customer's branding
image_filename = 'Grazioso Salvare Logo.png'
try:
    with open(image_filename, 'rb') as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode() 
except FileNotFoundError:
    encoded_image = None  

app.layout = html.Div([
    html.A([
        html.Center(html.Img(src=f'data:image/png;base64,{encoded_image}', height=250, width=251))
    ], href='https://www.snhu.edu', target="_blank"),

    html.Center(html.B(html.H1('Ethan Mills SNHU CS-340 Dashboard'))),
    html.Hr(),

    dcc.RadioItems(
        id='filter-type',
        options=[
            {'label': 'All', 'value': 'All'},
            {'label': 'Water Rescue', 'value': 'Water'},
            {'label': 'Mountain or Wilderness Rescue', 'value': 'Mountain'},
            {'label': 'Disaster Rescue or Individual Tracking', 'value': 'Disaster'},
        ],
        value='All'
    ),

    html.Hr(),

    dt.DataTable(
        id='datatable-id',
        columns=[{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns],
        data=df.to_dict('records'),
        editable=True,
        row_selectable="single",
        selected_rows=[],  
        filter_action="native",
        sort_action="native",
        page_action="native",
        page_current=0,
        page_size=10,
    ),

    html.Br(),
    html.Hr(),

    html.Div(className='row', style={'display': 'flex', 'justify-content': 'center'}, children=[
        html.Div(id='graph-id', className='col s12 m6'),
        html.Div(id='map-id', className='col s12 m6')
    ])
])

#############################################
# Interaction Between Components / Controller
#############################################

@app.callback(
    [Output('datatable-id', 'data'), Output('datatable-id', 'columns')],
    [Input('filter-type', 'value')]
)
def update_dashboard(filter_type):
    global df  

    if filter_type == 'All':
        df = pd.DataFrame.from_records(shelter.getRecordCriteria({}))
    elif filter_type == 'Water':
        labRegex = re.compile(".*lab.*", re.IGNORECASE)
        chesaRegex = re.compile(".*chesa.*", re.IGNORECASE)
        newRegex = re.compile(".*newf.*", re.IGNORECASE)
        df = pd.DataFrame.from_records(shelter.getRecordCriteria({
            '$or': [
                {"breed": {'$regex': newRegex}},
                {"breed": {'$regex': chesaRegex}},
                {"breed": {'$regex': labRegex}},
            ],
            "sex_upon_outcome": "Intact Female",
            "age_upon_outcome_in_weeks": {"$gte": 26.0, "$lte": 156.0}
        }))
    elif filter_type == 'Mountain':
        germanRegex = re.compile(".*german.*", re.IGNORECASE)
        alaskanRegex = re.compile(".*mala.*", re.IGNORECASE)
        oldRegex = re.compile(".*old english.*", re.IGNORECASE)  
        huskyRegex = re.compile(".*husk.*", re.IGNORECASE)
        rottRegex = re.compile(".*rott.*", re.IGNORECASE)
        df = pd.DataFrame.from_records(shelter.getRecordCriteria({
            '$or': [
                {"breed": {'$regex': germanRegex}},
                {"breed": {'$regex': alaskanRegex}},
                {"breed": {'$regex': oldRegex}},
                {"breed": {'$regex': huskyRegex}},
                {"breed": {'$regex': rottRegex}},
            ],
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {"$gte": 26.0, "$lte": 156.0}
        }))
    elif filter_type == 'Disaster':
        df = pd.DataFrame.from_records(shelter.getRecordCriteria({
            '$or': [
                {"breed": {'$regex': re.compile(".*german.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*golden.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*blood.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*dober.*", re.IGNORECASE)}},
                {"breed": {'$regex': re.compile(".*rott.*", re.IGNORECASE)}},
            ],
            "sex_upon_outcome": "Intact Male",
            "age_upon_outcome_in_weeks": {"$gte": 20.0, "$lte": 300.0}
        }))
    else:
        raise Exception("Unknown filter")

    return df.to_dict('records'), [{"name": i, "id": i, "deletable": False, "selectable": True} for i in df.columns]

@app.callback(
    Output('map-id', "children"),
    [Input('datatable-id', "derived_virtual_selected_rows")]
)
def update_map(virtualRows):
    global df  
    if not virtualRows:
        markerArray = (30.75, -97.48)
        toolTip = "Austin Animal Center"
        popUpHeading = "Austin Animal Center"
        popUpParagraph = "Shelter Home Location"
    else:
        dff = df.iloc[virtualRows]  
        coordLat = float(dff.iloc[0]['location_lat'])
        coordLong = float(dff.iloc[0]['location_long'])
        markerArray = (coordLat, coordLong)
        toolTip = dff.iloc[0]['breed']
        popUpHeading = "Animal Name"
        popUpParagraph = dff.iloc[0]['name']

    return [
        dl.Map(style={'width': '700px', 'height': '450px'}, center=markerArray, zoom=10, children=[
            dl.TileLayer(id="base-layer-id"),
            dl.Marker(position=markerArray, children=[
                dl.Tooltip(toolTip),
                dl.Popup([
                    html.H1(popUpHeading),
                    html.P(popUpParagraph)
                ])
            ])
        ])
    ]

app.run_server(mode="inline")  


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CURD


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[ ]:


import os
os.getcwd()


# In[ ]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[ ]:


import CRUD


# In[1]:


import os
os.getcwd()


# In[2]:


os.chdir('/home/ethanmills_snhu/Desktop')


# In[3]:


import CRUD


# In[ ]:




