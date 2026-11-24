#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
Synchroniser un parametre sur une autre base de temps
par interpolation par spline

IN :

    X       variable à interpoler
    time    temps de X
    time_dest temps destination
    decal   decalage temporel (s)
    unit_X    unite de X ("degres", "radian", ou "autre") 

OUT : 
    X_sync X synchronisé sur time_dest 


@Météo-France CNRM/GMEI/TRAMM
W. Maurel 
le 06/03/2020

"""

import numpy as np
from scipy.interpolate import UnivariateSpline

def traite_nan ( x, x_inter, time_x, toler, time_dest ):
    """
    remplace les valeurs par des nan dans la serie x_inter 
    qui étaient presents dans la serie x
    """

    idx_nan = np.where ( np.isnan(x) )[0]
    resu = np.copy(x_inter)

    if len(idx_nan) == 0 :
        return(resu)

    i_av = idx_nan[0]
    imin_av =  np.argmin(abs(time_x[i_av] - time_dest)) 
    nbval_hors_toler = 0
    for i in idx_nan :
        t = time_x[i]
        imin= np.argmin(abs(t - time_dest)) 
        #print ("t={}  time_dest={} toler ={}".format(t, time_dest[imin], toler))
        if ( np.abs(t - time_dest[imin])) < toler :
            resu[imin] = np.nan
            # traitement du cas ou il y a des sauts temporels > toler dans les valeurs manquantes
            # mais pas dans time_dest
            #print ( "i= {}, i_av={}, imin={}, imin_av={}".format(i, i_av, imin, imin_av ))
            if (i-i_av -1) == nbval_hors_toler and (imin - imin_av > 1 ) :
                #print ( "resu[{}:{}] = np.nan".format(imin_av+1,imin) )
                resu[imin_av+1:imin] = np.nan
            imin_av = imin
            i_av = i
            nbval_hors_toler = 0
        else :
            nbval_hors_toler = nbval_hors_toler +1

    return resu

def supprime_retour_ar (x, time_x) :
    """
    supprime les valeurs pour lesquelles le temps revient en arriere
    Il faudra peut-être le mettre dans un operateur independant ...
    """

    time_z = np.copy(time_x)
    z = np.copy(x)
    n_retour = 1
    while ( n_retour > 0 ) :
        dt = np.diff(time_z)
        idx = np.where( dt <=0. )[0]
        time_z = np.delete(time_z, idx+1)
        z = np.delete(z, idx+1)
        n_retour = len(idx)

    return ( z, time_z)

def Synchro_spline(x, time, time_dest, decal, unit=""):
    """ Cubic spline interpolation
    """

    cnvt_coef = { 'degres': np.pi/180.,
                  'radians': 1.0 }

    if ((unit == 'degres') or (unit == 'radians')) :
        typ = "angle"
        cnvt = cnvt_coef[unit]
    else: 
        typ = ""

    # suppression des retours arrière

    data, time_data = supprime_retour_ar (x, time) 

    sel = np.isfinite(data)

    if typ != "angle" :
        inter = UnivariateSpline( time_data[sel], data[sel], s=0)
    else:
        inter_cos = UnivariateSpline(time_data[sel], np.cos(data[sel]*cnvt), s=0)
        inter_sin = UnivariateSpline(time_data[sel], np.sin(data[sel]*cnvt), s=0)

    
    # calcul d'un seuil de tolerance pour le recalage des NaN 
    periode = np.median(np.diff(time_dest)) 
    p=10**(np.floor( np.log10(periode/2.)))
    seuil = p*np.ceil(periode/(2.*p))

    if typ != "angle":
        y = inter(time_dest + decal)
        data_sync = traite_nan ( data , y, time_data, seuil, time_dest )
    else:
        x_data = inter_cos(time_dest + decal)
        x_data = traite_nan ( data , x_data, time_data, seuil, time_dest )
        y_data = inter_sin(time_dest + decal)
        y_data = traite_nan ( data , y_data, time_data, seuil, time_dest )
        data_sync = np.arctan2(y_data, x_data) / cnvt

    return data_sync

