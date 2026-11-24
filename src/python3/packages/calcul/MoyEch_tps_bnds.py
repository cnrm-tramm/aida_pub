#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import warnings
import datetime 
#import util_bnds

def fct_MoyEch_tps_bnds (data_var_in, data_time_in, tolerance_mnq, data_time_out, time_bnds) :

    """
    Effectue le calcul de la fonction "fonction" aux temps "time_out" sur
    des intervalles définis par "time_bnds".

    Input :
        var_in : variable d'entrée sur laquelle on opère le calcul
        time in : variable temps associé à var_in
        tolerance_mnq : nombre de valeurs manquantes au-dela duquel on ne fera pas le calcul
        time_out  : variable temps de sortie
        time_bnds : intervalles de temps sur lesquels on applique le calcul

    Output :
        var_out : variable calculée
        cod_ret :  tableau de 1 float : code retour
        tab_stat : tableau de diagnostics

        
    Auteur :  CNRM/GMEI/TRAMM décembre 2020         
    """

    #
    # Copie des variables dans des structures numpy
    #
    cod_ret = np.array([0],dtype=np.float) 
        
    #
    # Pré-diagnostics
    #

    if data_var_in.ndim == 1 :
        var_out = np.ones(len(data_time_out), dtype=float)*np.nan
        tab_stat = np.array([1,2,3],dtype=np.int)
        nb_moy = np.zeros(1,dtype=np.int)
        nb_zero = np.zeros(1,dtype=np.int)
        nb_inf = np.zeros(1,dtype=np.int)
    else :
        var_out = np.ones((len(data_time_out), data_var_in.shape[1]),dtype = float)*np.nan
        tab_stat = np.ones((3,data_var_in.shape[1]),dtype=np.int)
        nb_moy = np.zeros(data_var_in.shape[1],dtype=np.int)
        nb_zero = np.zeros(data_var_in.shape[1],dtype=np.int)
        nb_inf = np.zeros(data_var_in.shape[1],dtype=np.int)
  
    pre_diag = 0

    
    if data_time_in[-1] < time_bnds[0][0] :
        pre_diag = -1
        nb_zero = len(data_time_out)
    if time_bnds[-1][1] < data_time_in[0] :
        pre_diag = -2
        nb_zero = len(data_time_out)
    if pre_diag != 0 :
        tab_stat[0] = nb_moy
        tab_stat[1] = nb_zero
        tab_stat[2] = nb_inf
        cod_ret[0] = pre_diag
        return var_out, cod_ret, tab_stat

    time_bnds_indexes = time_bnds_to_indexes(data_time_in, time_bnds)

    for i in range(len(time_bnds_indexes)) :
    #for i in range(872,874) :
        if time_bnds_indexes[i][0] == -1 :
            var_out[i] = np.nan
            nb_zero += 1
        elif time_bnds_indexes[i][0] > time_bnds_indexes[i][1] :
            var_out[i] = np.nan
            nb_zero +=  1
        else :
            # Appel de la fonction
            result, nb_ok = calcule_moy(data_var_in[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1])

            # Par défaut on met le résultat
            var_out[i] = result
            nb_moy = nb_moy+1

            if True in (nb_ok == 0) :
                # Si y a aucune valeur ok
                index_0 = np.where(nb_ok == 0)[0]

                if var_out.ndim == 1 :
                    var_out[i] = np.nan
                    nb_zero = nb_zero+1
                    nb_moy = nb_moy-1
                else :
                    var_out[i,index_0] = np.nan

                    nb_zero[index_0] = nb_zero[index_0]+1
                    nb_moy[index_0] = nb_moy[index_0]-1

            
            if True in (nb_ok <= tolerance_mnq) and True in (nb_ok > 0):
                #Si le nombre de valeurs moyennées est inférieur au nombre minimum requis
                
                #On cherche l'indice quand le nb de valeurs moyennées est inférieur au seuil 
                index_in_tolmnq = np.where(nb_ok <= tolerance_mnq)[0]
                index_non0 = np.where(nb_ok != 0)[0]

                index_non0_tolmnq = np.intersect1d(index_in_tolmnq,index_non0)
                
                if var_out.ndim == 1 :
                    var_out[i] = np.nan
                    nb_inf = nb_inf+1
                    nb_moy = nb_moy-1
                else :
                    var_out[i,index_non0_tolmnq] = np.nan
                
                    nb_inf[index_non0_tolmnq] = nb_inf[index_non0_tolmnq]+1
                    nb_moy[index_non0_tolmnq] = nb_moy[index_non0_tolmnq]-1
                

    tab_stat[0] = nb_moy
    tab_stat[1] = nb_zero
    tab_stat[2] = nb_inf

    return np.array(var_out, dtype=np.float), cod_ret, tab_stat

def time_bnds_to_indexes(time_in, time_bnds) :
    """
        Calcule les indices de time_in correspondant au time_bnds.
        Suppose que time_in et time_bnds sont ordonnés chronologiquement
    """
    index_bnds = np.zeros((len(time_bnds),2), dtype=np.int)
    i=0
    for j in range(len(time_bnds)) :
        if time_in[0] > time_bnds[j][1] :
            index_bnds[j] = [-1, -1]
            continue
        if time_in[-1] < time_bnds[j][0] :
            index_bnds[j] = [-1, -1]
            continue
        while i <len(time_in) and time_in[i]<time_bnds[j][0] :
            i=i+1
        index_bnds[j][0] = i
        while i <len(time_in) and time_in[i]<=time_bnds[j][1] :
            i=i+1
        index_bnds[j][1] = i-1
    return index_bnds
            
def calcule_moy(echantillon) :
    """
        Calcule la moyenne sur un echantillon 1D ou 2D.
    """
    if echantillon.ndim == 1 :
        nb_ok = np.array([0])
    else :
        nb_ok = np.zeros(echantillon.shape[1])

    result = np.nanmean(echantillon,axis = 0)   

    #Nombre de données ok
    if echantillon.ndim == 1 :
        nb_ok[0] = len(echantillon) - np.count_nonzero(np.isnan(echantillon))
    else :
        nb_ok = np.ones(echantillon.shape[1])*echantillon.shape[0] - np.count_nonzero(np.isnan(echantillon),axis = 0)

    return result, nb_ok

