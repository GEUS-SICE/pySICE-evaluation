# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 14:03:28 2019

@author: bav
"""

#%matplotlib qt  

import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable  
import pandas as pd
from scipy.stats import gaussian_kde
from sklearn import linear_model
from sklearn.metrics import mean_squared_error, r2_score
import datetime
import matplotlib.dates as mdates
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')

from math import radians, cos, sin, asin, sqrt
def haversine(lat1, lon1, lat2, lon2, to_radians=True, earth_radius=6371):
    """
    slightly modified version: of http://stackoverflow.com/a/29546836/2901002

    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees or in radians)

    All (lat, lon) coordinates must have numeric dtypes and be of equal length.

    """
    if to_radians:
        lat1, lon1, lat2, lon2 = np.radians([lat1, lon1, lat2, lon2])

    a = np.sin((lat2-lat1)/2.0)**2 + \
        np.cos(lat1) * np.cos(lat2) * np.sin((lon2-lon1)/2.0)**2

    return earth_radius * 2 * np.arcsin(np.sqrt(a))
    
def stat_title(x,y,ax):
    ind = np.logical_and(pd.notnull(x),pd.notnull(y))
    x = x[ind]
    y=y[ind]
    x = x.values.reshape(-1,1)
    y = y.values.reshape(-1,1)    

    lr = linear_model.LinearRegression()
    lr.fit(x,y)
    # print('Coefficients: \n', lr.coef_)    
    preds = lr.predict(x)
    ax.set_title('R2=%.3f\nRMSE=%.2f\nN=%.0f' % (r2_score(y,preds),
                                              mean_squared_error(y,preds), 
                                              len(x)))
    return ax


#%%
def OutlookRaster(var,title):
    l,b,r,t = var.bounds
    res = var.res
    x = np.arange(l,r, res[0])
    y = np.arange(t,b, -res[0])
    z=var.read(1)
    nan_col = ~np.all(np.isnan(z), axis=0)
    z=z[:,nan_col]
    x=x[nan_col]
    
    nan_row = ~np.all(np.isnan(z), axis=1)
    z=z[nan_row,:]
    y=y[nan_row]
     
    fig = go.Figure(
            data=go.Heatmap(x=x,
                            y=y,
                            z=z,
                            type = 'heatmap',
                            colorscale='Jet',
                            colorbar=dict(title=title),
                            showscale=True))
    fig.update_layout(
        autosize=False,
        width=500,
        height=500)    
    fig.show()
#    fig.write_image(title+".jpeg")
    return x,y,z

#%%
def heatmap(var, title='', col_lim=(np.nan, np.nan) ,cmap_in='gnuplot'):
    if np.isnan(col_lim[0]):
        col_lim=(np.nanmin(var), np.nanmax(var))
    z=var
    nan_col = ~np.all(np.isnan(z), axis=0)
    z=z[:,nan_col]
    
    nan_row = ~np.all(np.isnan(z), axis=1)
    z=z[nan_row,:]

    cmap = plt.get_cmap(cmap_in)
    cmap.set_bad(color='gray')

#    fig,ax = plt.subplots()
    im = plt.imshow(z, cmap=cmap, interpolation='nearest',vmin=col_lim[0], vmax=col_lim[1])
    cb= plt.colorbar(im)
    cb.ax.set_ylabel(title)
#    fig.show()
#    fig.write_image(title+".jpeg")
    return z
#%%
def heatmap_discrete(var, title='', col_lim=(np.nan, np.nan) ,cmap_in='gnuplot'):
    if np.isnan(col_lim[0]):
        col_lim=(np.nanmin(var), np.nanmax(var))
    z=var
    nan_col = ~np.all(np.isnan(z), axis=0)
    z=z[:,nan_col]
    
    nan_row = ~np.all(np.isnan(z), axis=1)
    z=z[nan_row,:]

    cmap = plt.get_cmap(cmap_in)
    cmap.set_bad(color='gray')
    
    bounds = np.unique(var)[np.logical_not(np.isnan(np.unique(var)))]
    bounds = np.append(bounds, bounds[len(bounds)-1]+1)
    norm = mpl.colors.BoundaryNorm(bounds, cmap.N+1)

    fig,ax = plt.subplots(figsize=(10,15))
    im = ax.imshow(z+1e-6, cmap=cmap, norm = norm, interpolation='Nearest')
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%" , pad= 0.1)
    cb = mpl.colorbar.ColorbarBase(ax=cax, cmap=cmap, norm=norm)
    
    tic_locs =bounds[0:len(bounds)-1] - (bounds[0:len(bounds)-1]-bounds[1:len(bounds)])/2
    cb.set_ticks(tic_locs)
    cb.ax.set_yticklabels(bounds[0:len(bounds)-1])
    cb.ax.set_ylabel(title)

    fig.show()
#    fig.write_image(title+".jpeg")
    return fig,ax
    


#%% Density scatter

def density_scatter(x,y,ax,ss):
    if isinstance(x, pd.core.series.Series)==False:
        x = pd.DataFrame(x)
        x = x[0]
    if isinstance(y, pd.core.series.Series)==False:
        y = pd.DataFrame(y)
        y=y[y.columns[0]]
        
    y=y[~np.isnan(x)]
    x=x[~np.isnan(x)]
    x=x[~np.isnan(y)]
    y=y[~np.isnan(y)]

    xy = np.vstack([x,y])
    z = gaussian_kde(xy)(xy)
    # Sort the points by density, so that the densest points are plotted last
    idx = z.argsort()
    x, y, z = x.iloc[idx], y.iloc[idx], z[idx]
    ax.scatter(x, y, c=z, s=ss)
    return ax
# =============================================================================
# 
# =============================================================================
    
#%% Plotting top of atmosphere refletance
#%matplotlib qt
#%matplotlib inline  
def mosaic_albedo_fit(df, Rad_in):
    fig, ax = plt.subplots(7,3, sharex='col', sharey='row',figsize=(15, 15))
    fig.subplots_adjust(hspace=0, wspace=0)
    if Rad_in=='Rt':
        fig.text(0.5, 0.05, 'Top of atmosphere OLCI reflectance', ha='center', size = 20)
    elif Rad_in=='Rb':
        fig.text(0.5, 0.05, 'Bottom of atmosphere OLCI reflectance', ha='center', size = 20)
    fig.text(0.05, 0.5, 'PROMICE albedo', va='center', rotation='vertical', size = 20)
    
    # axes are in a two-dimensional array, indexed by [row, col]
    count=0
    ss=5
    
    for i in range(7):
        for j in range(3):
            # Calculate the point density
            count = count+1
            R=df[Rad_in+str(count)]
            alb = df['PROMICE alb']
            alb=alb[~np.isnan(R)]
            R=R[~np.isnan(R)]
            alb = alb[~(R>1.1)]
            R = R[~(R>1.1)]
            
            input_name= Rad_in+str(count)
    
            density_scatter(R,alb,ax[i, j],ss)
            
            R=R.values
            alb=alb.values
            R=R.reshape(-1,1)
            alb=alb.reshape(-1,1)
            lr = linear_model.LinearRegression()
            lr.fit(R, alb)
            print(Rad_in+str(count))
            print('Coefficients: \n', lr.coef_)
            
            preds = lr.predict(R)
            
            tmp = np.array([np.min(R), np.max(R)])
            tmp = tmp.reshape(-1,1)
            ax[i, j].plot(tmp, lr.predict(tmp))
#            x_ticks  = np.linspace(0.25,1,4)
#            ax[i, j].set_xticklabels(x_ticks,fontsize=20)
#            ax[i, j].set_yticklabels(x_ticks,fontsize=20)
              
            ax[i, j].text(0.08, 0.93, 
              '%s' % input_name,
              fontsize=18,
              color='black',
              fontweight='bold',
              horizontalalignment='left',
              verticalalignment='top',
              bbox=dict(boxstyle="square",
                       ec='lightskyblue',
                       alpha=0.8))
            ax[i, j].text(0.7, 0.5, 
              'R2=%.3f\nRMSE=%.2f\nN=%.0f' % (r2_score(alb,preds), mean_squared_error(alb,preds),len(R)),
              fontsize=13,
              color='white',
              fontweight='bold',
              horizontalalignment='left',
              verticalalignment='top',
              bbox=dict(boxstyle="square",
                       ec='lightskyblue',
                       alpha=0.8))
            ax[i, j].set_xlim([0.01, 1.05])
            ax[i, j].set_ylim([0.01, 1.05])
            ax[i, j].grid(True)
    fig.savefig('./output/linear_'+Rad_in+'oa.png',bbox_inches='tight')


