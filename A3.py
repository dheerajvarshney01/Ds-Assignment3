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

gdf_ais.plot()
plt.show()

## read shape file into GeoDataFrame object (that contains GeoSeries objects):
gdf_shapes=gpd.read_file(
    r'D:\Studies\DalhousieUniversity\Summer2019\DataScience\A3\Nima_Ports\assignment3shapefile.shp')
gdf_shapes = gdf_shapes.set_index('port_name')
##nimaPortsGDF.plot()
##plt.show()
gdf_shapes['centroidPoint'] = gdf_shapes.geometry.apply(lambda x: x.centroid)

ax = gdf_shapes.plot()
centroidPoints = [point for point in gdf_shapes['centroidPoint']]
gpd.GeoSeries(centroidPoints).plot(ax=ax,color='yellow',markersize=10)
plt.show()

pointsClosestToCentroids = []
for cp in centroidPoints:
    pointsClosestToCentroids.append(
        gdf_ais.loc[gdf_ais.distance(cp)==gdf_ais.distance(cp).min(),:])

ax = gdf_shapes.plot()
##gpd.GeoSeries(centroidPoints).plot(ax=ax,color='yellow',markersize=10)

pointClosestTocentroids = []
for points in pointsClosestToCentroids:
    pointClosestTocentroids.append(points.iloc[0,:].geometry.buffer(0.003))

gpd.GeoSeries(pointClosestTocentroids).plot(ax=ax,color='pink',markersize=10)

gdf_ais.plot(ax=ax,color='g',alpha=0.2)

for point in pointClosestTocentroids:
    gdf_ais.loc[gdf_ais.within(point),:].plot(ax=ax,color='k')

plt.show()


