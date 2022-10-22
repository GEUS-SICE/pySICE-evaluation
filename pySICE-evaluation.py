# -*- coding: utf-8 -*-
"""
@author: bav@geus.dk

tip list:
    %matplotlib inline
    %matplotlib qt
    import pdb; pdb.set_trace()
"""

import numpy as np
import pandas as pd
import os
import errno
from pathlib import Path
import bav_lib as bl
import matplotlib.pyplot as plt

#%%  PROMICE evaluation
# first file
data_org = pd.read_csv('data/PROMICE_jason_all.csv')
data_org['cloud'] = data_org.PROMICE_cloud_index
data_org['station'] = data_org.site
data_org['PROMICE_alb'] = data_org.albedo_PROMICE
data_org[data_org==-999] = np.nan
path_to_file_1 = 'data/PROMICE_jason_all_out.csv'
name_1='pySICEv2.1'
isnow_label = {
    1: "clean snow",
    2: "polluted snow",
    3: "mixed pixel",
    100: "SZA > 75",
    102: "TOA(21) < 0.1",
    103: "TOA(1) < 0.2",
    104: "grain_diameter < 0.1",
    105: "solver crashed",
    999: "no input",
}
data_out = pd.read_csv(path_to_file_1)

for var in data_org.columns[29:]:
    print(var)
    if var not in data_out.columns:
        data_out[var] = data_org.loc[data_out.xy.values, var] 
# Removing cloudy measurements
cloud_thd = 0.8
data_cloud = data_out[data_out['PROMICE_cloud_index']>cloud_thd]
data_out=data_out[data_out['PROMICE_cloud_index']<=cloud_thd]
print('\nRemoving '+str(data_cloud.shape[0]) +'/'+
      str(data_cloud.shape[0]+data_out.shape[0]) + ' due to clouds')

data_out.loc[data_out.grain_diameter<0.07,'albedo_bb_planar_sw'] = np.nan
data_out.loc[data_out.albedo_bb_planar_sw>1,'albedo_bb_planar_sw'] = np.nan

import matplotlib
f1, ax = plt.subplots(1,1)
msk=data_out[['albedo_bb_planar_sw', 'albedo_PROMICE']].notnull().all(1)
x = data_out.loc[msk, 'albedo_PROMICE']
y = data_out.loc[msk, 'albedo_bb_planar_sw']

hb = plt.hist2d(x,y,bins=(100,100), cmap = 'magma_r',
                norm=matplotlib.colors.LogNorm())
plt.plot([0.2, 1], [0.2, 1],'k')
cbar = plt.colorbar()
cbar.set_label('Number of observations in bin')
plt.xlabel('PROMICE albedo')
plt.ylabel('pySICEv2.1 albedo')
bl.stat_title(data_out['albedo_bb_planar_sw'], data_out['PROMICE_alb'],ax)
ax.set_xlim([0.2, 1])    
ax.set_ylim([0.2, 1])   
f1.savefig('figures/scatter.png')

#  Plot for each station
data_out['date'] = pd.to_datetime(data_out[['year','month','day','hour','minute','second']])
data_out = data_out.set_index(['station','date'], drop=False)
from matplotlib.patches import Rectangle
def multi_plot(data_out,
               sites = ['KAN_M', 'KAN_U'],
               sp1 = 4, sp2 = 2,
               title = '', OutputFolder='figures/',
               filename_out = 'plot',
               name='pySICE'
               ):

    f1, ax = plt.subplots(sp1,sp2,figsize=(13, 10))
    ax = ax.flatten()
    f1.subplots_adjust(hspace=0.2, wspace=0.1,
                       left = 0.06 , right = 0.95 ,
                       bottom = 0.15 , top = 0.94)
    count = -1
    for i, site in enumerate(sites):
        data_out.loc[site].PROMICE_alb.plot(ax=ax[i], 
                                        label='PROMICE',
                                        marker='o', 
                                        linestyle='None', 
                                        )
        data_out.loc[site].albedo_bb_planar_sw.plot(ax=ax[i], 
                                                label=name,
                                                marker='o',
                                                linestyle='None', 
                                                )
        data_out.loc[site].loc[data_out.loc[site].diagnostic_retrieval==3,
                           'albedo_bb_planar_sw'].plot(ax=ax[i],
                                                       color='k',
                                                       label='mixed',
                                                       marker='+',
                                                       linestyle='None',
                                                       )
        ax[i].fill_between([data_out.date.min(), data_out.date.max()], 
                           [0.564, 0.564],
                           color='lightgray')
        ax[i].grid(True)
        ax[i].set_title(site)
        ax[i].set_xlim([data_out.date.min(), data_out.date.max()])    
        ax[i].set_ylim(0.2,1)    
        ax[i].set_xlabel("")
            
        if i<len(sites)-2:
            ax[i].set_xticklabels("")
    ax[0].add_patch(
            Rectangle(xy=(np.nan, np.nan), width=np.nan,
                      height=np.nan, facecolor='lightgray',
                      label='bare ice albedo')
        )
    handles, labels = ax[0].get_legend_handles_labels()
    f1.legend(handles, labels, ncol=4, loc='upper center')
    f1.text(0.02, 0.5, title, va='center', rotation='vertical', size = 14)
    f1.savefig(OutputFolder+filename_out+'.png')
    
multi_plot(data_out, title = 'Albedo (-)',
              sites =['KAN_L','KAN_M','KAN_U','KPC_L','KPC_U','SCO_L','SCO_U','EGP'],
              OutputFolder = 'figures/', 
              filename_out='PROMICE_comp_1',
              name='pySICEv2.1')

multi_plot(data_out, title='Albedo (-)',
              sites = ['QAS_L', 'QAS_U', 'TAS_L', 'TAS_A', 'THU_L', 'THU_U', 'UPE_L', 'UPE_U'],
              OutputFolder = 'figures/', 
              filename_out='PROMICE_comp_2',
              name='pySICEv2.1')

# %% SSA evaluation
import scipy.io
mat = scipy.io.loadmat('data/SSA EGP/SSA2017.mat')
SSA_obs = pd.DataFrame( {key: mat[key][:,0] for key in ['DOY','sample_num','SSA']})
SSA_obs['Year'] = 2017
mat = scipy.io.loadmat('data/SSA EGP/SSA2018.mat')
tmp = pd.DataFrame( {'DOY': mat['DOY_mat'].flatten(),
                     'sample_num': mat['Distance_mat'].flatten(),
                     'SSA': mat['SSA_mat'].flatten()})
tmp['Year'] = 2018
SSA_obs=SSA_obs.append(tmp)
tmp = pd.read_csv('data/SSA EGP/SSA2019.txt',sep="\t")
tmp['DOY'] = pd.to_datetime(tmp.date).dt.dayofyear.values
tmp['sample_num'] = np.nan
tmp['SSA'] = tmp['SSA_mean']
tmp = tmp.drop(columns = ['date','SSA_mean'])
tmp['Year'] = 2019
SSA_obs=SSA_obs.append(tmp)

SSA_obs['time'] = np.asarray((np.asarray(SSA_obs['Year'], dtype='datetime64[Y]')-1970)+(np.asarray(SSA_obs['DOY']*24, dtype='timedelta64[h]')), dtype='datetime64[s]')
SSA_obs=SSA_obs.set_index('time',drop=False)
SSA_obs=SSA_obs.sort_index()
#from pySICE:     SSA = 6./D /0.917 so D =  6 /SSA / 0.917
SSA_obs['gd_mm'] = 6 /SSA_obs['SSA'] / 0.917
SSA_obs_d = SSA_obs.groupby(level=0).mean()
SSA_obs_d['SSA_std'] = SSA_obs.groupby(level=0).std()['SSA']
SSA_obs_d['gd_std'] = SSA_obs.groupby(level=0).std()['gd_mm']
SSA_obs_d.loc['2019','gd_std'] = SSA_obs_d['gd_std'].mean()
SSA_obs_d.drop(['sample_num','Year','DOY'],axis=1)
SSA_obs_d = SSA_obs_d.reset_index()
SSA_obs_d.time = SSA_obs_d.time + pd.Timedelta('12 hours')
SSA_obs_d = SSA_obs_d.set_index('time')

df_EGP = data_out.loc['EGP'].copy()
df_EGP.loc[df_EGP.grain_diameter<0.07, ['grain_diameter', 'snow_specific_area']] = np.nan

fig, ax = plt.subplots(3,1,figsize=(10,15))
fig.subplots_adjust(hspace=0.3, wspace=0.1,
                   left = 0.08 , right = 0.99 ,
                   bottom = 0.06 , top = 0.96)
for i, yr in enumerate(range(2017,2020)):
    df_EGP.loc[str(yr)].snow_specific_area.plot(ax=ax[i], label='pySICEv2.1',
                                           marker='o', linestyle='None')
    
    SSA_obs_d.loc[str(yr)].SSA.plot(ax=ax[i], label='Observations',
                               marker='^', linestyle='None')
    ax[i].grid()
    ax[i].set_ylabel('SSA (m2 kg-1)')
    ax[i].set_xlabel('')
    ax[i].set_xlim(pd.to_datetime(str(yr)+'-05-01'), pd.to_datetime(str(yr)+'-08-15'))
handles, labels = ax[0].get_legend_handles_labels()
fig.legend(handles, labels, ncol=4, loc='upper right')
fig.suptitle('EastGRIP')
fig.savefig('figures/SSA_EGP.png')

fig, ax = plt.subplots(3,1,figsize=(10,15))
fig.subplots_adjust(hspace=0.3, wspace=0.1,
                   left = 0.08 , right = 0.99 ,
                   bottom = 0.06 , top = 0.96)
for i, yr in enumerate(range(2017,2020)):
    df_EGP.loc[str(yr)].grain_diameter.plot(ax=ax[i], label='pySICEv2.1',
                                           marker='o', linestyle='None')
    
    SSA_obs_d.loc[str(yr)].gd_mm.plot(ax=ax[i], label='Observations',
                               marker='^', linestyle='None')
    ax[i].grid()
    ax[i].set_ylabel('d_opt (mm)')
    ax[i].set_xlabel('')
    ax[i].set_xlim(pd.to_datetime(str(yr)+'-05-01'), pd.to_datetime(str(yr)+'-08-15'))
    # lab=[l.get_text()[5:] for l in ax[i].get_xticklabels()]
    # ax[i].set_xticks([l for l in ax[i].get_xticks()])
    # ax[i].set_xticklabels(lab)
    # ax[i].set_title(str(yr))
handles, labels = ax[0].get_legend_handles_labels()
fig.legend(handles, labels, ncol=4, loc='upper right')
fig.suptitle('EastGRIP')
fig.savefig('figures/GD_EGP.png')