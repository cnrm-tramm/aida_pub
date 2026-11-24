#!/usr/bin/env python3

import sys
import numpy as np
import warnings
import datetime 
import math
import xarray as xr

def check_duplicates(array):
    """
    Renvoie les indices des éléments uniques
    Si éléments dupliqués, seul l'indice de la 1e apparition est gardé 
    """
    u, c = np.unique(array, return_index=True)
    return np.array(c, dtype = int)
    
def fct_Ech_tps_impos (X_data,time_in_data,ecart_max,time_out_data) :

    """
    Echantillonne une variable "X_data" daté par le vecteur "time_in_data" sur 
    une autre base de temps "time_out_data".
    
    Input :
        X_data        : variable de départ à échantillonner
        time_in_data  : base de temps de départ
        ecart_max     : écart maximum toléré
        time_out_data : base de temps d'arrivée
        
    Output :
        var_out : variable "X_data" échantillonnée sur la base de temps "time_out_data"

    """

    #Code retour
    cod_ret = 0

    # Initialisation du tableau de retour
    if (X_data.ndim == 1):
        var_out = np.ones((len(time_out_data)), dtype="f")*np.nan
    else :
        var_out = np.ones((len(time_out_data),X_data.shape[1]), dtype="f")*np.nan   

    ###
    # Passage sur une base de temps régulière 
    ###
    
    # # Parfois deux lignes ont la même dates exactement --> on supprime les doublons
    X_data_unique = X_data[check_duplicates(time_in_data)]
    time_in_data_unique = time_in_data[check_duplicates(time_in_data)]

    # Création d'un xarray avec les dates en index de ligne
    coords = {'time': time_in_data_unique}
    dims = ['time']

    if X_data.ndim > 1:
        for d in range(1,X_data.ndim) :

            coords['variable'+str(d)] = range(X_data_unique.shape[d])
            dims.append('variable'+str(d))

    var_in_xr = xr.DataArray(X_data_unique, coords=coords, dims=dims)


    # On réindexe au plus proche avec les dates de sorties régulières
    var_out = var_in_xr.reindex(time=time_out_data, method = "nearest", tolerance = ecart_max)
    var_out = var_out.to_numpy()

    return var_out,cod_ret
