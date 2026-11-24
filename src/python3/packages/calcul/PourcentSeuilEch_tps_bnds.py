#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import warnings
import datetime 

def fct_PourcentSeuilEch_tps_bnds (data_var_in, data_time_in, tolerance_mnq, data_time_out, time_bnds,sargsup) :
    """
    Effectue le calcul de la fonction "fonction" aux temps "time_out" sur
    des intervalles définis par "time_bnds".

    Input :
        data_var_in : variable d'entrée sur laquelle on opère le calcul
        time in : variable temps associé à data_var_in
        tolerance_mnq : nombre de valeurs manquantes au-dela duquel on ne fera pas le calcul
        time_out  : variable temps de sortie
        time_bnds : intervalles de temps sur lesquels on applique le calcul
        argsup: arguments de la fonction

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

    #
    # Pré-diagnostics
    #
    var_out = np.ones(len(data_time_out), dtype=float)*np.nan
    pre_diag = 0
    nb_moy = 0
    nb_zero = 0
    nb_inf = 0
    
    if data_time_in[-1] < time_bnds[0][0] :
        pre_diag = -1
        nb_zero = len(time_out)
    if time_bnds[-1][1] < data_time_in[0] :
        pre_diag = -2
        nb_zero = len(time_out)
    if pre_diag != 0 :
        tab_stat[0] = nb_moy;
        tab_stat[1] = nb_zero;
        tab_stat[2] = nb_inf;
        cod_ret[0] = pre_diag;
        return var_out, cod_ret, tab_stat;

    time_bnds_indexes = time_bnds_to_indexes(data_time_in, time_bnds)

    for i in range(len(time_bnds_indexes)) :
        if time_bnds_indexes[i][0] == -1 :
            var_out[i] = np.nan
            nb_zero += 1
        else :
            # Appel de la fonction
            result, nb_ok = calcule_pourcentseuil(data_var_in[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1],sargsup)
            if nb_ok == 0 :
                var_out[i] = np.nan
                nb_zero += 1
            elif nb_ok <= tolerance_mnq :
                var_out[i] = np.nan
                nb_inf += 1
            else :
                var_out[i] = result
                nb_moy += 1
    tab_stat[0] = float(nb_moy);
    tab_stat[1] = float(nb_zero);
    tab_stat[2] = float(nb_inf);

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
            
def calcule_pourcentseuil(echantillon, sarg_sup) :
    """
        Calcule le pourcentage de valeurs inférieures au seuil sur un echantillon.
        le pourcentseuil q est un seuil maxi 
        on a pris comme argsup un seuil en float : le champ entrant est de la forme param1:param2:...param
        
    """
    loc_som = 0.0
    nb_ok = 0
    
    with warnings.catch_warnings():
        warnings.filterwarnings('error') 
        try :
            # on prend le premier caractere qui est le seuil 
            q=float(sarg_sup.split(':')[0])
            for ech in echantillon:
                if ech <= q:
                    loc_som=loc_som+1
            result = (loc_som)*100/echantillon.size 
            nb_ok=nb_ok+1
        except RuntimeWarning :
            result = np.nan
    nb_ok = echantillon.size - np.count_nonzero(np.isnan(echantillon))
    
    return result, nb_ok

