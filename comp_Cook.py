# -*- coding: utf-8 -*-
"""

"""
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sice import pySICE
import rasterio as rio
import xarray as xr
import val_lib as vl
# https://scihub.copernicus.eu/dhus/odata/v1/Products('04c630f9-0382-4689-b606-e91d44eab67e')/$value
# https://scihub.copernicus.eu/dhus/odata/v1/Products('65239852-8cb5-4aa7-9291-30b185a61e57')/$value
# https://scihub.copernicus.eu/dhus/odata/v1/Products('dd696088-0b60-48b7-ad13-78ad0ae1bb38')/$value
# https://scihub.copernicus.eu/dhus/odata/v1/Products('493d7678-9853-429f-978e-749186f77b93')/$value
# https://scihub.copernicus.eu/dhus/odata/v1/Products('7c299c71-f121-476d-bbfe-290c0f1ea687')/$value
#%% Running SICE
path_to_folder = 'validation/data/Cook_data/SEN3/OLCI_proc/'
folderlist = [dI for dI in os.listdir(path_to_folder) 
              if os.path.isdir(os.path.join(path_to_folder,dI))]
 
for foldername in folderlist:
    folderpath = path_to_folder + foldername
    print(folderpath)
    pySICE(folderpath)
    vl.plot_sice_output(folderpath+'/')

#%% Loading data
import val_lib as vl
(data_cook, metadata, WL) = vl.load_cook_data()

#%%
print('loading pySICE output') 
from bav_lib import haversine
from rasterio.warp import transform
import cartopy.crs as ccrs

site_coord = pd.read_csv('validation/data/Cook_data/lat_lon.csv',header=None)
(lat_obs, lon_obs) = site_coord.iloc[0,1:3]

data_pySICE_all = pd.DataFrame()

for foldername in folderlist:
    folderpath = path_to_folder + foldername
    print(folderpath)
    filelist = os.listdir(folderpath)
    data_pySICE = pd.DataFrame()
    for i in range(len(filelist)): 
        if filelist[i][-3:]=='xml':
            continue
        # print(filelist[i][:-4])
        data = rio.open(folderpath + '/' +  filelist[i])
        
        # Read the data
        da = xr.open_rasterio(folderpath + '/' +  filelist[i])
        
        val = da.values[0]
        if i == 0:
            # Compute the lon/lat coordinates with rasterio.warp.transform
            ny, nx = len(da['y']), len(da['x'])
            x, y = np.meshgrid(da['x'], da['y'])
            lon, lat = transform(da.crs, {'init': 'EPSG:4326'},
                                 x.flatten(), y.flatten())
            lon = np.asarray(lon).reshape((ny, nx))
            lat = np.asarray(lat).reshape((ny, nx))
            dist = haversine(lat.flatten(), lon.flatten(), 
                             lat_obs.repeat(len(lat.flatten())), 
                             lon_obs.repeat(len(lat.flatten())))
            ind = dist<2
            data_pySICE['lon'] = lon.flatten()[ind]
            data_pySICE['lat'] = lat.flatten()[ind]
        data_pySICE[filelist[i][:-4]] = val.flatten()[ind]
        
        if filelist[i][:-4] == 'albedo_bb_planar_sw':
            min_lon = -50
            min_lat = 66
            max_lon = -47
            max_lat = 68
            da.coords['lon'] = (('y', 'x'), lon)
            da.coords['lat'] = (('y', 'x'), lat)
            mask_lon = (da.lon >= min_lon) & (da.lon <= max_lon)
            mask_lat = (da.lat >= min_lat) & (da.lat <= max_lat)       
            da = da.where(mask_lon & mask_lat, drop=True)
    
            # Compute a greyscale out of the rgb image
            greyscale = da.mean(dim='band')
    
            # Plot on a map
            plt.figure(figsize=(20, 15))
            ax = plt.subplot(projection=ccrs.NorthPolarStereo())
            greyscale.plot(ax=ax, x='lon', y='lat', transform=ccrs.NorthPolarStereo(),
                            cmap='Greys_r', add_colorbar=True, vmin=0, vmax=1)
            ax.scatter(lon_obs, lat_obs, s=20)
            ax.scatter(data_pySICE['lon'],data_pySICE['lat'], s=15)
            plt.title(foldername)
            plt.tight_layout()
        
    data_pySICE['scene'] = foldername
    data_pySICE_all = data_pySICE_all.append(data_pySICE)
    
data_pySICE_all=data_pySICE_all.set_index('scene')   


#%%
# %matplotlib inline
# %matplotlib qt
   
fig, ax = plt.subplots(4,4, sharex='col', sharey='row',figsize=(15, 15))
fig.subplots_adjust(hspace=0, wspace=0)
for k, sample in enumerate(metadata.index.values):
    i,j = np.unravel_index(k, ax.shape)
    print(sample)
    ax[i, j].scatter(WL,data_cook.loc[sample])
    ax[i, j].scatter(WL,data_cook.loc[sample])
    ax[i, j].text(0.2, 0.93, 
      str(metadata['Cells/mL in upper 2cm'][k]) + ' cells/mL',
      fontsize=14,
      color='black',
      fontweight='bold',
      horizontalalignment='left',
      verticalalignment='top',
      bbox=dict(boxstyle="square", ec='lightskyblue', alpha=0.8))    
fig.text(0.5, 0.05, 'Bottom of atmosphere OLCI reflectance', ha='center', size = 20)
fig.text(0.05, 0.5, 'PROMICE albedo', va='center', rotation='vertical', size = 20)
        
#%% 
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
central_wavelengths = [central_wavelengths[int(x[-2:])-1] for x in alb_sph_lab]
for scene in np.unique(data_pySICE_all.index.values):
    plt.figure()
    tmp = data_pySICE_all.loc[scene,alb_sph_lab]
    for i in range(tmp.shape[0]):
        plt.plot(central_wavelengths, tmp.iloc[i,:])
    plt.title(scene+' Nbr pixels = ' + str(tmp.shape[0]))
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Albedo (-)')
    
