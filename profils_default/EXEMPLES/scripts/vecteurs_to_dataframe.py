#!/bin/env python3
# -*- coding: utf-8 -*-
"""
Lecture de vecteurs et rangement dans un DataFrame Pandas
"""

import os
import sys
import datetime as dt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA

# dictionnaire decrivant les variables du DataFrame et le nom des
# vecteurs correspondants
dict_param= {'RGD':'ray_rgd_cnr1_c2_cal_%60', 'RGM':'ray_rgm_cnr1_c2_cal_%60'}

# acquisitions à lire
acqid_deb='ts210213'
acqid_fin='ts210213'

# lecture des donnees et rangement dans un DataFrame
data = pd.DataFrame()
for p in dict_param.keys() :
    x, time, hdr = AIDA.read_datas(acqid_deb, dict_param[p], acqid_fin)
    data[p] =  pd.Series ( x, index = time )

# trace des series temporelles pour voir

plt.figure()
plt.plot (data['RGM'], label='RGM')
plt.plot (data['RGD'], label='RGD')
plt.legend()
plt.show()

