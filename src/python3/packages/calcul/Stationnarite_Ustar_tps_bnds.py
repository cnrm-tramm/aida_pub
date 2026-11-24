#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import warnings
import datetime
from math import sqrt 

def fct_Stationnarite_Ustar_tps_bnds (u, v, w, time_in, nsub, tolerance_mnq, time_out, time_bnds) :
    """
    Effectue le calcul de la stationnarité de Ustar
    aux temps "time_out" sur des intervalles définis par "time_bnds".
    u, v, w ont la même base de temps.
    Cette fonction calcule le rapport suivant :
        Rapport = [ moyenne(Ustar sur T1) - Ustar sur T2 ] / ( ustar sur T2 ) 
        avec T2=intervalle de temps de chaque time_bnds
             T1=T2/nsub
    Foken considère que si Rapport < 30 % les conditions sont stationnaires
    
    Input :
        u : composante u du vent (masked array)
        v : composante v du vent (masked array)
        w : composante w du vent (masked array)
        time_in : variable temps associé à u,v,w
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
    # Initialisation des variables
    #
    cod_ret = 0 
    tab_stat = np.array([1,2,3],dtype=np.float)
    
    #
    # Pré-diagnostics
    #
    var_out = np.ones(len(time_out), dtype=float)*np.nan
    pre_diag = 0
    nb_stat_ustar = 0
    nb_zero = 0
    nb_inf = 0
    
    if time_in[-1] < time_bnds[0][0] :
        pre_diag = -1
        nb_zero = len(time_out)
    if time_bnds[-1][1] < time_in[0] :
        pre_diag = -2
        nb_zero = len(time_out)
    if pre_diag != 0 :
        tab_stat[0] = nb_stat_ustar;
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
            echantillon_u = u[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1]
            echantillon_v = v[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1]
            echantillon_w = w[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1]
            result, nb_ok = calcule_Stationnarite_Ustar(echantillon_u, echantillon_v, echantillon_w, nsub, tolerance_mnq)
            if nb_ok == 0 :
                var_out[i] = np.nan
                nb_zero += 1
            elif nb_ok == -1 :
                var_out[i] = np.nan
                nb_inf += 1
            else :
                var_out[i] = result
                nb_stat_ustar += 1
    tab_stat[0] = float(nb_stat_ustar);
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
            
def calcule_Stationnarite_Ustar(u, v, w, nsub, tolerance_mnq) :
    """
        Calcule la stationnarité de Ustar sur un échantillon u,v,w.
        Retourne le rapport de stationnarité et une valeur diagnostic du calcul :
         0 : impossible de faire le calcul (que des nans pour u|v|w)
         1 : on a pu faire le calcul
        -1 : on n'a pas pu faire le calcul car trop de valeurs manquantes (tolerance_mnq)
    """
    rapport = 0
    ustar_s = np.array([]) # tableau des ustar des sous-échantillons
    
    # np.ma.cov(a,b) donne la matrice de covariances suivante : 
    #    cov(a,a)  cov(a,b)
    #    cov(a,b)  cov(b,b)
    # C'est donc l'élément [0,1] qui nous interesse
    
    # on calcule ustar de l'échantillon complet.
    nb_manquant = np.count_nonzero(np.isnan(u) | np.isnan(v) | np.isnan(w))
    if nb_manquant == u.size :
        return rapport, 0
    pct_manquant = (nb_manquant/u.size)*100
    if (pct_manquant > tolerance_mnq) :
        return rapport, -1
    cov_wu = np.ma.cov(w,u,rowvar=False)[0][1]
    cov_wv = np.ma.cov(w,v,rowvar=False)[0][1]
    ustar = sqrt(sqrt(cov_wu*cov_wu + cov_wv*cov_wv))
    
    # on découpe l'échantillon en nsub sous-échantillons
    sub_u = np.array_split(u, nsub)
    sub_v = np.array_split(v, nsub)
    sub_w = np.array_split(w, nsub)
    # on calcule ustar pour chaque sous-échantillon si on a suffisamment de données
    for su,sv,sw in zip(sub_u, sub_v, sub_w) :
        nb_manquant = np.count_nonzero(np.isnan(su) | np.isnan(sv) | np.isnan(sw))
        pct_manquant = (nb_manquant/su.size)*100
        if (pct_manquant <= tolerance_mnq) :
            cov_sw_su = np.ma.cov(sw,su,rowvar=False)[0][1]
            cov_sw_sv = np.ma.cov(sw,sv,rowvar=False)[0][1]
            ustar_su_sv_sw = sqrt(sqrt(cov_sw_su*cov_sw_su + cov_sw_sv*cov_sw_sv))
            ustar_s = np.append(ustar_s, ustar_su_sv_sw)
        
    # on calcule le rapport si on a suffisamment de données
    if len(ustar_s) == 0 :
        return rapport, -1
    rapport = abs((ustar_s.mean() - ustar) / ustar)

    return rapport, 1

