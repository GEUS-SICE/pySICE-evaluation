# -*- coding: utf-8 -*-
"""

"""
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr
import val_lib as vl
import geopandas as gpd

# Loading data
# In situ observations
(data_cook, metadata, WL) = vl.load_cook_data()

# OLCI input
# https://scihub.copernicus.eu/dhus/odata/v1/Products('04c630f9-0382-4689-b606-e91d44eab67e')/$value
# https://scihub.copernicus.eu/dhus/odata/v1/Products('65239852-8cb5-4aa7-9291-30b185a61e57')/$value
# https://scihub.copernicus.eu/dhus/odata/v1/Products('dd696088-0b60-48b7-ad13-78ad0ae1bb38')/$value
# https://scihub.copernicus.eu/dhus/odata/v1/Products('493d7678-9853-429f-978e-749186f77b93')/$value
# https://scihub.copernicus.eu/dhus/odata/v1/Products('7c299c71-f121-476d-bbfe-290c0f1ea687')/$value

path_to_folder = 'data/Cook_data/SEN3/OLCI_proc/'
folderlist = [dI for dI in os.listdir(path_to_folder)
              if os.path.isdir(os.path.join(path_to_folder, dI))]

site_coord = pd.read_csv('data/Cook_data/lat_lon.csv', header=None,
                         names=['site', 'lat', 'lon'])
gdf = gpd.GeoDataFrame(site_coord,
                       geometry=gpd.points_from_xy(site_coord['lon'], site_coord['lat']),
                       crs='EPSG:4326').to_crs("epsg:3413")

site_coord['x'] = gdf.geometry.x
site_coord['y'] = gdf.geometry.y
site_coord = site_coord.set_index('site').drop(columns='geometry')

df = pd.DataFrame()
print('loading OLCI data')
for foldername in folderlist:
    folderpath = path_to_folder + foldername
    print(folderpath)
    filelist = ['height.tif', 'O3.tif', 'O3_SICE.tif', 'OAA.tif',
                    'OZA.tif', 'r_TOA_01.tif', 'r_TOA_02.tif', 'r_TOA_03.tif', 
                    'r_TOA_04.tif', 'r_TOA_05.tif', 'r_TOA_06.tif', 'r_TOA_07.tif', 
                    'r_TOA_08.tif', 'r_TOA_09.tif', 'r_TOA_10.tif', 'r_TOA_11.tif',
                    'r_TOA_12.tif', 'r_TOA_13.tif', 'r_TOA_14.tif', 'r_TOA_15.tif',
                    'r_TOA_16.tif', 'r_TOA_17.tif', 'r_TOA_18.tif', 'r_TOA_19.tif',
                    'r_TOA_20.tif', 'r_TOA_21.tif', 'SAA.tif', 'SZA.tif']

    data_pySICE = pd.DataFrame()
    da = xr.Dataset()
    for file in filelist: 
        da[file[:-4]] = xr.open_dataarray(folderpath + '/' +  file)
    plt.figure()
    da['r_TOA_21'].plot()
    gdf.plot(ax=plt.gca(),color='tab:red')
    plt.title(foldername)
    for site in site_coord.index:
        tmp = da.interp(x=site_coord.loc[site, 'x'], 
                        y=site_coord.loc[site, 'y'],
                        method='nearest').to_dataframe()
        tmp['site'] = site
        tmp['date'] = pd.to_datetime(foldername)
        df = df.append(tmp)
df = df.reset_index().drop(columns=['spatial_ref','band'])
for i in range(22):
    df = df.rename(columns={'r_TOA_'+str(i).zfill(2): 'Oa'+str(i).zfill(2)+'_reflectance'})

df = df.rename(columns={'SZA': 'sza',
                         'SAA': 'saa',
                         'OZA': 'vza',
                         'OAA': 'vaa',
                         'O3': 'total_ozone',
                         'height': 'elevation'})
 
df.to_csv('../pySICE/data/PROMICE/Cook_OLCI_input.csv')

df_out = pd.read_csv('../pySICE/data/PROMICE/out/Cook_OLCI_out.csv')
df_out = pd.concat((df_out,df),axis=1)
df_out = df_out.set_index(['site', 'date'])
#%%
# %matplotlib inline
# %matplotlib qt
alb_sph_lab = ['albedo_spectral_planar_01', 'albedo_spectral_planar_02',
       'albedo_spectral_planar_03', 'albedo_spectral_planar_04',
       'albedo_spectral_planar_05', 'albedo_spectral_planar_06',
       'albedo_spectral_planar_07', 'albedo_spectral_planar_08',
       'albedo_spectral_planar_09', 'albedo_spectral_planar_10',
       'albedo_spectral_planar_11', 'albedo_spectral_planar_16',
       'albedo_spectral_planar_17', 'albedo_spectral_planar_18',
       'albedo_spectral_planar_19', 'albedo_spectral_planar_20',
       'albedo_spectral_planar_21']

central_wavelengths= np.array([400, 412.5 ,442.5 ,490 ,510 ,560 ,620 ,665, 
                               673.75 ,681.25 ,708.75 ,753.75, 761.25 ,
                               764.375 ,767.5 ,778.75 ,865 ,885 ,900 ,940 ,1020])
fig, ax = plt.subplots(3,6, sharex='col', sharey='row',figsize=(15, 15))
ax = ax.flatten()
fig.subplots_adjust(hspace=0, wspace=0)
for k, sample in enumerate(metadata.index.values):

    print(sample)
    ax[k].scatter(WL,data_cook.loc[sample])
    date = '20'+sample.split('_')[3]+'-'+sample.split('_')[2].zfill(2)+'-'+sample.split('_')[1]
    try:
        tmp = df_out.loc['S6_GRL', date]
        if len(tmp) >0:
            plt.plot(central_wavelengths, df_out[[alb_sph_lab]].values,
                     marker='o', linestyle='o')
        print('????')
    except:
        pass
    # ax[i].text(0.2, 0.93, 
    #   str(metadata['Cells/mL in upper 2cm'][k]) + ' cells/mL',
    #   fontsize=14,
    #   color='black',
    #   fontweight='bold',
    #   horizontalalignment='left',
    #   verticalalignment='top',
    #   bbox=dict(boxstyle="square", ec='lightskyblue', alpha=0.8))    
fig.text(0.5, 0.05, 'Wavelength (nm)', ha='center', size = 20)
fig.text(0.05, 0.5, 'Albedo', va='center', rotation='vertical', size = 20)
        
#%% 

central_wavelengths = [central_wavelengths[int(x[-2:])-1] for x in alb_sph_lab]
for scene in np.unique(data_pySICE_all.index.values):
    plt.figure()
    tmp = data_pySICE_all.loc[scene,alb_sph_lab]
    for i in range(tmp.shape[0]):
        plt.plot(central_wavelengths, tmp.iloc[i,:])
    plt.title(scene+' Nbr pixels = ' + str(tmp.shape[0]))
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Albedo (-)')
    
