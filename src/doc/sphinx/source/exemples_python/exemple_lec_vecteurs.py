#!/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple de code lecture des vecteurs et de 
rangement dans un DataFrame Pandas

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

liste_param= ['flx_le_kh20_pal_0', 'flx_le_Vlicor_pal_0']

liste_acqid=['as160018', ]

# lecture des donnees et rangeme,nt dans un DataFrame
data = pd.DataFrame()

for acqid in liste_acqid :
    data_temp = pd.DataFrame()
    for p in liste_param : 
        x, time, hdr = AIDA.read_data(acqid, p)
        data_temp[p]= pd.Series ( x, index = time )

    data = data.append(data_temp)

# trace des series temporelles pour voir

plt.figure()
plt.plot (data['flx_le_kh20_pal_0'], label='flx_le_kh20_pal_0') 
plt.plot (data['flx_le_Vlicor_pal_0'], label='flx_le_Vlicor_pal_0') 
plt.legend()
plt.show()



    

