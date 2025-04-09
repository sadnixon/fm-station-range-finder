#!/usr/bin/env python
# coding: utf-8

# In[105]:


import requests
import re
import pandas as pd
import numpy as np

import shapely
import geopandas as gpd
from fiona.drvsupport import supported_drivers
from io import StringIO
supported_drivers['KML'] = 'rw'


# In[5]:


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}



all_stations = pd.read_csv("all_stations.csv")[['sign','freq','city','format','state']]


# In[264]:


all_stations_grouped = all_stations.groupby('sign').first().reset_index()
all_stations_grouped


# In[82]:


response = requests.get("https://transition.fcc.gov/fcc-bin/fmq?call=WYYD#tabs-10000-2",headers=headers)


page_text = response.text


# In[266]:


all_stations_grouped


# In[277]:


polygons = []

for row in range(len(all_stations_grouped)):
    
    call_sign = all_stations_grouped.iloc[row,0]
    freq = round(all_stations_grouped.iloc[row,1],1)

    response = requests.get("https://transition.fcc.gov/fcc-bin/fmq?call="+call_sign+"&freq="+str(freq)+"&fre2="+str(freq)+"#tabs-10000-2",headers=headers)
    page_text = response.text

    print(response)
    print(page_text)

    appid = re.findall("c_application_id = '(\d*)';",page_text)
    lmsid = re.findall("lms_appid = '([a-z0-9]*)';",page_text)
    call = re.findall("c_callsign = '([^']*)';",page_text)

    city = re.findall('c_comm_city_app = "([^"]*)";',page_text)
    state = re.findall("c_comm_state_app = '([^']*)';",page_text)
    fileno = re.findall("c_filenumber = '([^']*)';",page_text)
    
    shape_list = []
    
    #freq = round(all_stations.loc[all_stations['sign']==call_sign].iloc[0,1],1)

    for i in range(len(appid)):
        comp_url = 'https://transition.fcc.gov/fcc-bin/contourplot.kml?appid='+appid[i]+'&lmsid='+lmsid[i]+'&call='+call[i]+'&freq='+str(round(freq,1))+'&contour=60&city='+city[i]+'&state='+state[i]+'&fileno='+fileno[i]+'&.txt'
        response = requests.get(comp_url,headers=headers)

        print(response)
        print(page_text)

        try:
            kml_string = response.text
            kml_file = StringIO(kml_string)
            gdf = gpd.read_file(kml_file, driver='KML')
        except:
            pass

        # Plot the data
        #gdf.iloc[3:].plot()
        try:
            shape_list.append(shapely.geometry.Polygon(gdf.iloc[3,2]))
        except:
            pass


    s = gpd.GeoSeries(shape_list)
    combined_shape = s.unary_union
    
    polygons.append(combined_shape)
    
    if row%50==0:
        print(row)
    
all_stations_grouped['geometry'] = polygons

all_stations_grouped.to_csv('allstationspolygons.csv')




