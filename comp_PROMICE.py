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

# plt.close('all')
# first file
path_to_file_1 = '../pySICE/data/PROMICE/out_pol.csv'
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

data_org = pd.read_csv('../pySICE/data/PROMICE/S3_PROMICE_out.csv')
# data_org['x'] = data_org.index.values
# data_org['y'] = data_org.index.values*0
# input_f = data_org[['x','y','latitude','longitude', 'sza', 'saa', 
#                     'vza', 'vaa', 'Oa01_reflectance',
#                     'Oa02_reflectance', 'Oa03_reflectance', 'Oa04_reflectance',
#                     'Oa05_reflectance', 'Oa06_reflectance', 'Oa07_reflectance',
#                     'Oa08_reflectance', 'Oa09_reflectance', 'Oa10_reflectance',
#                     'Oa11_reflectance', 'Oa12_reflectance', 'Oa13_reflectance',
#                     'Oa14_reflectance', 'Oa15_reflectance', 'Oa16_reflectance',
#                     'Oa17_reflectance', 'Oa18_reflectance', 'Oa19_reflectance',
#                     'Oa20_reflectance', 'Oa21_reflectance',
#                     'altitude', 'total_ozone']]
# input_f.set_index('x').loc[input_f.sza.notnull(), :].to_csv('input.dat',sep=' ', header='None',float_format = '%0.4f')
data_out = pd.read_csv(path_to_file_1)

# data_fortran = pd.read_csv('fortran_output_promice/snow_parameters.dat',delim_whitespace=True, header=None)
# data_fortran.columns = ['j', 'alat', 'alon', 'diagnostic_retrieval', 'factor', 'grain_diameter', 'ssa', 'dlina', 'r0', 
#       'aload1', 'powe', 'polut', 'deff', 'absor1', 'absef660', 'absor1000', 'albedo_bb_planar_sw', 
#       'rvis', 'rnir', ' rsws', ' rviss', 'rnirs', ' andbi', 'andsi', 'ratka', 
#       'NPOLE', ' NBARE', ' NSNOW', ' sza', 'vza', 'raa', 'toa(1)', 'toa(21)', 
#       'tocos', 'akozon', 'difka', 'cv1', 'cv2']
# data_out = data_fortran
# name_1='fortran'
# data_org = data_org.iloc[data_out.j, :].reset_index()
# data_org[['x','y','longitude', 'latitude','altitude']]
# plt.figure()
# data_org.longitude.plot()
# data_fortran.alat.plot()

for var in ['station', 'year', 'month', 'day', 'hour', 'minute','second',
      'altitude', 'humidity', 'latitude', 'longitude',
       'sea_level_pressure', 'total_columnar_water_vapour', 'total_ozone',
       'slope','cloud', 'PROMICE_alb',
       'latitude N', 'longitude W', 'elevation', 'tilt', 'BBA_emp']:
    if var in data_out.columns:
        print(var)
        print(wtf)
    else:
        data_out[var] = data_org[var]
# Removing cloudy measurements
cloud_thd = 0.1
data_cloud = data_out[data_out['cloud']>cloud_thd]
data_out=data_out[data_out['cloud']<=cloud_thd]
print('\nRemoving '+str(data_cloud.shape[0]) +'/'+
      str(data_cloud.shape[0]+data_out.shape[0]) + ' due to clouds')

# second file
path_to_file_2 = '../pySICEv1.6/data/PROMICE/out.csv'
name_2='pySICEv1.6'
isnow_label_2 = {
    0: "clean snow",
    1: "polluted snow",
    2: "mixed pixel",
    6: 'polluted snow for which r0 was parametrized',
    7: 'reprocessed as clean snow',
    100: "SZA > 75",
    102: "TOA(21) < 0.1",
    103: "TOA(1) < 0.2",
    104: "grain_diameter < 0.1",
    999: "solver crashed",
}

data_org = pd.read_csv('../pySICE/data/PROMICE/S3_PROMICE_out.csv')
data_out_2 = pd.read_csv(path_to_file_2)
for var in ['station', 'year', 'month', 'day', 'hour', 'minute','second',
      'altitude', 'humidity', 'latitude', 'longitude',
       'sea_level_pressure', 'total_columnar_water_vapour', 'total_ozone',
       'sza', 'vza', 'saa', 'vaa', 'slope','cloud', 'PROMICE_alb',
       'latitude N', 'longitude W', 'elevation', 'tilt', 'BBA_emp']:
    if var in data_out_2.columns:
        print(wtf)
    else:
        data_out_2[var] = data_org[var]
# Removing cloudy measurements
data_cloud = data_out_2[data_out_2['cloud']>cloud_thd]
data_out_2=data_out_2[data_out_2['cloud']<=cloud_thd]
print('\nRemoving '+str(data_cloud.shape[0]) +'/'+
      str(data_cloud.shape[0]+data_out.shape[0]) + ' due to clouds')

# % Plot results ##
fs = 15
ss=5
f1, ax = plt.subplots(1,2,figsize=(16, 8))
# ax=[ax]
f1.subplots_adjust(hspace=0.2, wspace=0.1,
                   left = 0.08 , right = 0.95 ,
                   bottom = 0.2 , top = 0.9)
    
for isnow in data_out['diagnostic_retrieval'].unique():
    ax[0].plot(data_out.loc[data_out['diagnostic_retrieval']==isnow, 'albedo_bb_planar_sw'],
                  data_out.loc[data_out['diagnostic_retrieval']==isnow, 'PROMICE_alb'],
                  label = isnow_label[isnow],
                  marker='o',linestyle='None')
ax[0].plot([0, 1], [0,1], 'k')
bl.stat_title(data_out['albedo_bb_planar_sw'], data_out['PROMICE_alb'],ax[0])
ax[0].set_xlabel("Albedo from "+name_1+" (-)",fontsize=fs)
ax[0].set_ylabel("PROMICE albedo (-)",fontsize=fs)
ax[0].set_xlim([0, 1])    
ax[0].set_ylim([0, 1])   
ax[0].legend() 

tmp = data_out_2['diagnostic_retrieval']
tmp[data_out_2['diagnostic_retrieval']<0] = 999
for isnow in tmp.unique():
    if isnow < 0:
        isnow=999
    ax[1].plot(data_out_2.loc[data_out_2['diagnostic_retrieval']==isnow, 'albedo_bb_planar_sw'],
                  data_out_2.loc[data_out_2['diagnostic_retrieval']==isnow, 'PROMICE_alb'],
                  label = isnow_label_2[isnow],
                  marker='o',linestyle='None')
ax[1].plot([0, 1], [0,1], 'k')
bl.stat_title(data_out_2['albedo_bb_planar_sw'], data_out_2['PROMICE_alb'],ax[1])
ax[1].set_xlabel("Albedo from "+name_2+" (-)",fontsize=fs)
ax[1].set_ylabel("PROMICE albedo (-)",fontsize=fs)
ax[1].set_xlim([0, 1])    
ax[1].set_ylim([0, 1])   
ax[1].legend() 

f1.savefig('figures/scatter.png')

data_out['date'] = pd.to_datetime(data_out[['year','month','day','hour','minute','second']])
data_out = data_out.set_index(['station','date'], drop=False)
# data_out=data_out.groupby(pd.Grouper(freq='H', level=0)).first()

bl.multi_plot(data_out, title = 'Albedo (-)',
              sites =['KAN_L','KAN_M','KAN_U','KPC_L','KPC_U','SCO_L','SCO_U','EGP'],
              OutputFolder = 'figures/', filename_out='PROMICE_comp_1', name='pySICEv2.1', marker='o',linestyle='None')
bl.multi_plot(data_out, title='Albedo (-)',
              sites =['QAS_L','QAS_U','TAS_L','TAS_A','THU_L','THU_U','UPE_L','UPE_U'],
              OutputFolder = 'figures/', filename_out='PROMICE_comp_2', name='pySICEv2.1', marker='o',linestyle='None')
plt.figure()
plt.plot(data_out.loc['KPC_L'].cloud,
         data_out.loc['KPC_L'].albedo_bb_planar_sw - data_out.loc['KPC_L'].PROMICE_alb,
         marker = 'o', linestyle='None')
