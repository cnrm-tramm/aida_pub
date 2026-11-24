#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import warnings
import datetime 

def fct_Stationnarite_Covar_XY_tps_bnds (x, y, time_in, nsub, tolerance_mnq, time_out, time_bnds) :
    """
    Effectue le calcul de la stationnarité de la covariance de 2 paramètres
    aux temps "time_out" sur des intervalles définis par "time_bnds".
    x et y ont la même base de temps.
    Cette fonction calcule le rapport suivant :
        Rapport = [ moyenne(cov(x,y) sur T1) - cov(x,y) sur T2 ] / ( cov (x,y) sur T2 ) 
        avec T2=intervalle de temps de chaque time_bnds
             T1=T2/nsub
    Foken considère que si Rapport < 30 % les conditions sont stationnaires
    
    Input :
        x : première variable (masked array)
        y : deuxième variable (masked array)
        time_in : variable temps associé à x et y
        nsub : nombre de sous-intervales à utiliser pour le calcul
        tolerance_mnq : pourcentage de valeurs manquantes de l'intervale (ou sous-intervale) de calcul 
                        au-dela duquel on ne fera pas le calcul
        time_out  : variable temps de sortie
        time_bnds : intervales de temps sur lesquels on applique le calcul

    Output :
        var_out : variable calculée
        cod_ret :  int : code retour
        tab_stat : tableau de diagnostics

        
    Auteur :  CNRM/GMEI/TRAMM 
    """

    #
    # Initialisation des varaiables
    #
    cod_ret = 0 
    tab_stat = np.array([1,2,3],dtype=np.float)
    
    #
    # Pré-diagnostics
    #
    var_out = np.ones(len(time_out), dtype=float)*np.nan
    pre_diag = 0
    nb_stat_cov = 0
    nb_zero = 0
    nb_inf = 0
    
    if time_in[-1] < time_bnds[0][0] :
        pre_diag = -1
        nb_zero = len(time_out)
    if time_bnds[-1][1] < time_in[0] :
        pre_diag = -2
        nb_zero = len(time_out)
    if pre_diag != 0 :
        tab_stat[0] = nb_stat_cov;
        tab_stat[1] = nb_zero;
        tab_stat[2] = nb_inf;
        cod_ret = pre_diag;
        return var_out, cod_ret, tab_stat;

    time_bnds_indexes = time_bnds_to_indexes(time_in, time_bnds)

    for i in range(len(time_bnds_indexes)) :
        if time_bnds_indexes[i][0] == -1 :
            var_out[i] = np.nan
            nb_zero += 1
        else :
            # Appel de la fonction
            echantillon_x = x[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1]
            echantillon_y = y[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1]
            result, nb_ok = calcule_Stationnarite_Covar_XY(echantillon_x, echantillon_y, nsub, tolerance_mnq)
            if nb_ok == 0 :
                var_out[i] = np.nan
                nb_zero += 1
            elif nb_ok == -1 :
                var_out[i] = np.nan
                nb_inf += 1
            else :
                var_out[i] = result
                nb_stat_cov += 1
    tab_stat[0] = float(nb_stat_cov);
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
            
def calcule_Stationnarite_Covar_XY(x, y, nsub, tolerance_mnq) :
    """
        Calcule la stationnarité de la covariance de 2 paramètres sur 2 échantillons.
        Retourne le rapport de stationnarité et une valeur diagnostic du calcul :
         0 : impossible de faire le calcul (que des nans pour x|y)
         1 : on a pu faire le calcul
        -1 : on n'a pas pu faire le calcul car trop de valeurs manquantes (tolerance_mnq)
    """
    rapport = 0
    cov_sx_sy = np.array([])
    
    # np.ma.cov(a,b) donne la matrice de covariances suivante : 
    #    cov(a,a)  cov(a,b)
    #    cov(a,b)  cov(b,b)
    # C'est donc l'élément [0,1] qui nous interesse
    
    # on calcule la covariance de l'échantillon complet.
    nb_manquant = np.count_nonzero(np.isnan(x) | np.isnan(y))
    if nb_manquant == x.size :
        return rapport, 0
    pct_manquant = (nb_manquant/x.size)*100
    if (pct_manquant > tolerance_mnq) :
        return rapport, -1
    cov_x_y = np.ma.cov(x,y,rowvar=False)[0][1]
    
    # on découpe l'échantillon en nsub sous-échantillons
    sub_x = np.array_split(x, nsub)
    sub_y = np.array_split(y, nsub)
    # on calcule la covariance pour chaque sous-échantillon si on a suffisamment de données
    for sx,sy in zip(sub_x, sub_y) :
        nb_manquant = np.count_nonzero(np.isnan(sx) | np.isnan(sy))
        pct_manquant = (nb_manquant/sx.size)*100
        if (pct_manquant <= tolerance_mnq) :
            cov_sx_sy = np.append(cov_sx_sy, np.ma.cov(sx,sy,rowvar=False)[0][1])
        
    # on calcule le rapport si on a suffisamment de données
    if len(cov_sx_sy) == 0 :
        return rapport, -1
    rapport = abs((cov_sx_sy.mean() - cov_x_y) / cov_x_y)

    return rapport, 1

