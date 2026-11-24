#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import warnings
import datetime 
from scipy.stats import hmean

def fct_MoyInvEch_tps_bnds (var_in, 
                             time_in,
                             tolerance_mnq,
                             time_out, 
                             time_bnds,
                             val_inv,val_replac,tolerance_inv) :
    """
    Effectue le calcul aux temps "time_out" sur des intervalles définis par "time_bnds".

    Input :
        var_in : variable d'entrée sur laquelle on opère le calcul
        time in : variable temps associé à var_in
        tolerance_mnq : nombre de valeurs manquantes au-dela duquel on ne fera pas le calcul
        time_out  : variable temps de sortie
        time_bnds : intervalles de temps sur lesquels on applique le calcul
        val_inv : valeur invalide pour laquelle l'écart-type n'est pas calculé
        val_remplac : valeur de remplacement quand la valeur atteint val_inv avec une tolérance
        tolerance_inv : proportion de valeurs nécessaires pour que le calcul dde l'écart type soit valide

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
    tab_stat = np.array([1,2,3],dtype=np.float) 
    data_var_in = np.ones(len(var_in), dtype=float)
    data_var_in[:] = var_in
    data_time_in = np.ones(len(time_in), dtype=np.float64)
    data_time_in[:] = time_in
    data_tolerance_mnq = np.ones(1, dtype=np.int32)
    data_tolerance_mnq[:] = tolerance_mnq
    data_time_out = np.ones(len(time_out), dtype=np.float64)
    data_time_out[:] = time_out

    # c'est une chaine de caractere
    data_time_bnds = np.ones((len(time_bnds),2), dtype=np.float64)
    data_time_bnds[:] = time_bnds

    #
    # Pré-diagnostics
    #
    var_out = np.ones(len(time_out), dtype=float)*np.nan
    pre_diag = 0
    nb_moy = 0
    nb_zero = 0
    nb_inf = 0
    
    if data_time_in[-1] < data_time_bnds[0][0] :
        pre_diag = -1
        nb_zero = len(time_out)
    if data_time_bnds[-1][1] < data_time_in[0] :
        pre_diag = -2
        nb_zero = len(time_out)
    if pre_diag != 0 :
        tab_stat[0] = nb_moy
        tab_stat[1] = nb_zero
        tab_stat[2] = nb_inf
        cod_ret[0] = pre_diag
        return var_out, cod_ret, tab_stat

    time_bnds_indexes = time_bnds_to_indexes(data_time_in, data_time_bnds)

    for i in range(len(time_bnds_indexes)) :
        if time_bnds_indexes[i][0] == -1 :
            var_out[i] = np.nan
            nb_zero += 1
        else :
            # Appel de la fonction
            result, nb_ok = calcule_moyinv(var_in[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1], val_inv,val_replac,tolerance_inv)
            if nb_ok == 0 :
                var_out[i] = np.nan
                nb_zero += 1
            elif nb_ok <= data_tolerance_mnq[0] :
                var_out[i] = np.nan
                nb_inf += 1
            else :
                var_out[i] = result
                nb_moy += 1
    tab_stat[0] = float(nb_moy)
    tab_stat[1] = float(nb_zero)
    tab_stat[2] = float(nb_inf)

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
            #print("MIN:",j,i, time_in[i],time_bnds[j][0])
            i=i+1
        index_bnds[j][0] = i
        while i <len(time_in) and time_in[i]<=time_bnds[j][1] :
            #print("MAX:",j,i, time_in[i],time_bnds[j][1])
            i=i+1
        index_bnds[j][1] = i-1
        #print("{},{},[{},{}],[{},{}]".format(j,i, index_bnds[j][0], index_bnds[j][1], time_bnds[j][0], time_bnds[j][1]))
        #if i>50 :
        #    sys.exit(1)
    return index_bnds


def calcule_moyinv(echantillon,val_inv,val_replac,tolerance_inv) :
    """
        Calcule la moyenne sur un echantillon sauf pour les valeurs = val_inv .
        On fait le calcul sur la periode mais on remplace par val_replace si nb de valeur invalide > tolerance invalide  
        si la valeur est mise a val_inv on considere qu'elle est valide pour le calcul de la tolérance: augmentation de nb_Ok
    """
    nb_ok = 0
    
    with warnings.catch_warnings():
        warnings.filterwarnings('error') 
        try :
            epsilon=0.0001

            #annulation des Nans sinon on ne peut pas comparer aux val_inv
            mx2=np.ma.masked_array(echantillon,np.isnan(echantillon))
            mx2=mx2.compressed()
            #recherche de valeurs invalides dans l'échantillon
            mx=np.ma.masked_array(mx2,mx2>=val_inv)
            # on vérifie par rapport a la tolerance
            result=val_replac
            nb_inv=len(mx[~mx.mask])
            nb_total=len(mx)
            if nb_inv/nb_total  >= tolerance_inv:
                result=np.nanmean(mx)
        except RuntimeWarning as e:
            print("ERR:{}".format(e))
            result = np.nan
    nb_ok = echantillon.size - np.count_nonzero(np.isnan(echantillon))
    
    return result, nb_ok