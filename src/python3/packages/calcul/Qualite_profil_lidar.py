#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Qualislope.py : Check quality of rcs slope % molecular slope around reference
                altitude
                Cette fonction est appelée par un opérateur Aida écrit en
                langage C.

   Input arguments
   ---------------
  
        - pr2: the Pr2 signal from the LIDAR remote sensing
        - pr2_mol: the Pr2 signal from the molecular model
        - z: altitude above the ground level (in meters)
        - zref: reference altitude for molecular signal 
  
   Output argument
   ---------------
  
        - qualindex: quality index for each profiles
  
   Auteur 
   ------
        - CNRM/GMEI/TRAMM  P. Richard Fevrier 2018 a partir d'un script
          scilab ecrit par le LOA.

"""

import os
import sys
import numpy as np
from scipy import stats

PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))
import AIDA

def Qualite_profil_lidar(pr2,pr2_mol,z,zref) :

# initialization
    qualindex=np.zeros(len(pr2))
    pr2_lidc = np.empty(0)

    H_step = 1500.

    for i in np.arange(len(pr2)) :

        pr2_lid = pr2[i, :]
        zi= z[i,:] 
        pr2_moli = pr2_mol[i, :]

        if np.all(np.isnan(pr2_lid)) or np.isnan(zref[i]) or np.all(np.isnan(pr2_moli))   :  # no data in the pr2 profile
            qualindex[i] = np.nan
            continue

        pr2_lid[pr2_lid == 0] = 1e-10


# reference altitude
        d_zref = abs(zi-zref[i])
        iref = np.argmin(d_zref)

# parameter : step for calculation of slope
        step = H_step/(zi[2]- zi[1])

        if ((iref -step/2) < 0 ) or ((iref + step/2) > len(zi) ) :
            qualindex[i] = np.nan
            continue


# remove power
        power = np.floor(float(np.log10(np.nanmean(pr2_lid[20:30]))))
        pr2_lidb = pr2_lid * 10**(-power)



# calibration factors
        iref_grd = np.argmin(d_zref)

        mean_mol = np.mean(pr2_moli[iref_grd - 5 : iref_grd + 6])
        mean_lid = np.mean(pr2_lidb[iref_grd - 5 : iref_grd + 6])
# ajout valeur aboslue pour ne pas changer le signe de la pente 
# du signal lidar
        k_grd = abs ( mean_mol / mean_lid )

        pr2_lidc =  k_grd * (pr2_lidb)

# Mise en commentaire de cette partie car cela n'est pas très 
# adapté dans le cas d'un signal très bruité
# On peut changer le signe de tout le profil si une seule valeur est
# négative (W. Maurel, 24/10/2019)
#
# if pr2 negative in the reference zone, the whole profile is reversed
#        if pr2_lidc[1] < 0 :
#            pr2_lidc = -pr2_lidc + 2 * mean_mol

        imax = len(zi)
        i_trace = 222
# slope under
        area=np.max( (int(iref - step), 0 ))
        area1=np.min( (int(iref + 1), imax ))
        (a1, b1,rho,_,_) = stats.linregress(zi[area : area1],pr2_lidc[area:area1])
        [amol1, bmol1, rho1,_,_] = stats.linregress(zi[area:area1], pr2_moli[area:area1])

# slope between
        area =np.max( ( int(iref - (step / 2)), 0) ) 
        area1 =np.min( (int(iref + (step / 2)) + 1, imax) ) 
        (a2, b2,rho,_,_) = stats.linregress(zi[area:area1],pr2_lidc[area:area1])
        [amol2, bmol2, rho2,_,_] = stats.linregress(zi[area:area1], pr2_moli[area:area1])

# slope above
        area = np.max( ( int(iref), 0))
        area1 = np.min( (int(iref + step + 1), imax) )
        (a3, b3,rho,_,_) = stats.linregress(zi[area:area1],pr2_lidc[area:area1])
        [amol3, bmol3, rho3,_,_] = stats.linregress(zi[area:area1], pr2_moli[area:area1])

# the ratio has to be > 0 and not far from 1
#slopes = [a1 / amol1, a2 / amol2, a3 / amol2]
        slopes = np.array([a1 / amol1, a2 / amol2, a3 / amol3])
        best = np.argmin(abs(slopes-1.))

        qualindex[i]=slopes[best]

    return np.array(qualindex)

