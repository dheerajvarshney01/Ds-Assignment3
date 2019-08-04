import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
import shapely
import missingno as msn
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import os

df_aisData=pd.read_csv(r'D:\Studies\DalhousieUniversity\Summer2019\DataScience\A3\AISData.csv')
## drop the column that is same as index in data frame:
df_aisData = df_aisData.drop('Unnamed: 0', axis=1)

## rename columns:
columnsList = list(df_aisData.columns)
columnsList[0] = 'time'
columnsList[1] = 'x'
columnsList[2] = 'y'
df_aisData.columns = columnsList

gdf_ais = gpd.GeoDataFrame(df_aisData, crs={'init': 'epsg:4326'},
                        geometry=[shapely.geometry.Point(xy) for xy in zip(df_aisData.x, df_aisData.y)])


## read shape file into GeoDataFrame object (that contains GeoSeries objects):
gdf_shapes=gpd.read_file(
    r'D:\Studies\DalhousieUniversity\Summer2019\DataScience\A3\Nima_Ports\assignment3shapefile.shp')
##gdf_shapes = gdf_shapes.set_index('port_name')

## Q1
## Plot shapes of ports:
gdf_shapes.plot()
plt.show()

## Plot AIS data on the shapes of ports plot:
ax = gdf_shapes.plot()
gdf_ais.plot(ax=ax, facecolors='none', edgecolors='g')
plt.show()

## Plot AIS data that overlap shapes of ports - meaning ships entering ports
envelopes = []
for index, row in gdf_shapes.iterrows():
    envelopes.append(row.geometry.envelope)

ax = gdf_shapes.plot()
pointsWithinEnvelopes = []
for envelope in envelopes:
    pointsWithinEnvelope = gdf_ais.loc[gdf_ais.within(envelope),:]
    pointsWithinEnvelopes.append(pointsWithinEnvelope)
    pointsWithinEnvelope.plot(ax=ax,facecolors='none', edgecolors='g')

plt.show()


## Find all vessels visiting all th eports:
allPoinsWithinEnvelopes = pointsWithinEnvelopes[0]
for points in pointsWithinEnvelopes[1:]:
    allPoinsWithinEnvelopes.append(points)

## Only one vessle exists in the dataset, hence only one vessle foubd
print(allPoinsWithinEnvelopes.mmsi.unique())


## Q2:
import matplotlib.cm as cm
from matplotlib.colors import SymLogNorm
import matplotlib.pyplot as plt
cmap = cm.copper
norm = SymLogNorm(linthresh=0.03, linscale=1, vmin=1, vmax=gdf_ais.shape[0])
fig, ax = plt.subplots(1, figsize=(15, 8))
for port_name in set(gdf_shapes.port_name):
    port = gdf_shapes.loc[gdf_shapes.port_name==port_name,:]
    port_area = port.geometry
    signalsWithinPortArea = gdf_ais.loc[gdf_ais.within(port_area.values[0].envelope),:]
    numberOfSignals = signalsWithinPortArea.shape[0]
    port.plot(ax=ax,color = cmap(norm(numberOfSignals)))
    ax.axis('off')
    ax.set_title('Density of AIS port messages', fontdict={'fontsize': '25', 'fontweight': '3'})
plot_val = plt.cm.ScalarMappable(cmap='copper', norm=norm)
plot_bar = fig.colorbar(plot_val)
plt.show()



