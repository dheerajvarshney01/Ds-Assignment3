import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
import shapely
import missingno as msn
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import os, sys

df_aisData=pd.read_csv(r'D:\Studies\DalhousieUniversity\Summer2019\DataScience\A3\AISData.csv')
## drop the column that is same as index in data frame:
df_aisData.drop('Unnamed: 0', axis=1, inplace=True)
## drop duplicates:
df_aisData.drop_duplicates(subset=None, keep='first', inplace=True)
## drop unused columns:
df_aisData.drop(['position_accuracy', 'sog', 'cog'], axis=1, inplace=True)

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

## Q1
print("******************************* Q1 *************************************")
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

## Only one vessle exists in the dataset, hence only one vessle found
print(allPoinsWithinEnvelopes.mmsi.unique())


## Q2:
print("******************************* Q2 *************************************")
import matplotlib.cm as cm
from matplotlib.colors import SymLogNorm
import matplotlib.pyplot as plt
cmap = cm.YlOrRd

def preparePlot(gdf_ais, gdf_shapes):
    norm = SymLogNorm(linthresh=0.03, linscale=1, vmin=1, vmax=gdf_ais.shape[0])
    fig, ax = plt.subplots(1, figsize=(15, 8))
    for port_name in set(gdf_shapes.port_name):
        port = gdf_shapes.loc[gdf_shapes.port_name==port_name,:]
        port_area = port.geometry
        signalsWithinPortArea = gdf_ais.loc[gdf_ais.within(port_area.values[0].envelope),:]
        numberOfSignals = signalsWithinPortArea.shape[0]
        port.plot(ax=ax,color = cmap(norm(numberOfSignals)))
        ax.axis('off')
        ax.set_title('Density of AIS port messages (log10 scale)', fontdict={'fontsize': '25', 'fontweight': '3'})
    plot_val = plt.cm.ScalarMappable(cmap='YlOrRd', norm=norm)
    plot_bar = fig.colorbar(plot_val)

preparePlot(gdf_ais, gdf_shapes)
plt.show()

## Q3:
print("******************************* Q3 *************************************")
# Sort records in gdf_ais by time:
gdf_ais.sort_values(by = ['time'], ascending=True, inplace=True, kind='quicksort', na_position='last')
# Reset and drop index:
gdf_ais.reset_index(drop=True, inplace=True)

gdf_ais['hour'] = gdf_ais['time'].apply(lambda x: x[:-11])
uniqueHours = list(gdf_ais['hour'].unique())

gdf_aisByHour = []
for hour in uniqueHours:
    gdf_aisByHour.append(gdf_ais.loc[gdf_ais['hour'] == hour])

# We create plots and save 10 first of them to the disk.
# We don't save all of them because they are 2529.
i=0
for gdf in gdf_aisByHour:
    if i > 10:
        break
    preparePlot(gdf, gdf_shapes)
    fileName = os.path.dirname(sys.argv[0]) + "\\Q3Figures\\" +str(i)
    plt.savefig(fileName + ".png")
    plt.close()
    i += 1



## Q4:
print("******************************* Q4 *************************************")
# port of interest - 'port7'/'southend container terminal'/'ind'/'auto_port'/'pointpolygon'
portOfInterest = 'port7'
port = gdf_shapes.loc[gdf_shapes.port_name==portOfInterest,:]
port_area = port.geometry
signalsWithinPortArea = gdf_ais.loc[gdf_ais.within(port_area.values[0].envelope),:]

gdf_aisByHourPortOfInterest = []
for hour in uniqueHours:
    gdf_aisByHourPortOfInterest.append(signalsWithinPortArea.loc[signalsWithinPortArea['hour'] == hour].shape[0])


hours = range(0, len(uniqueHours), 1)

plt.plot(hours, gdf_aisByHourPortOfInterest)
plt.show()


## Q5
print("******************************* Q5 *************************************")
## reference - lab 7
import numpy as np
from skmultiflow.drift_detection.adwin import ADWIN
adwin = ADWIN()

for i in hours:
    adwin.add_element(gdf_aisByHourPortOfInterest[i])
    if adwin.detected_change():
        print('Change detected in data: ' + str(gdf_aisByHourPortOfInterest[i]) + ' - at index: ' + str(i))


## Q6
print("******************************* Q6 *************************************")
# Clustering ports based on message density. We are using data from Q1 where
from sklearn.cluster import DBSCAN