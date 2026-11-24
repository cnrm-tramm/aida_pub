#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np
import datetime, sys


def CovarXYmax_tps_bnds( X, Y, time_in, tolerance_mnq, time_out, time_bnds, tlag_min, tlag_max):
    """
    Calcule le maximum de covariance entre X et Y sur des intervalles donnés par time_bnds,
    en appliquant un décalage variant entre tlag_min et tlagmax. X et Y sont sur la même
    base de temps time_in.

    IN : 
        X           premier vecteur
        Y           second vecteur
        time_in     temps de X et Y	
        tolerance_mnq : nombre de valeurs manquantes au-dela duquel on ne fera pas le calcul
	    time_out  : variable temps de sortie
        time_bnds : intervalles de temps sur lesquels on applique le calcul
        tlag_min    borne minimale de variation du décalage temporel pour le calcul du maximum de covariance (s)
        tlag_max	borne maximale de variation du décalage temporel pour le calcul du maximum de covariance (s)

    OUT : 
        tous les retours sont (devraient être) des np.array
        Cov_xy        covariance 
        Cor_xy        correlation
        Nbsec_valid   nombre de secondes valides sur lequel la covariance a été calculée (s)
        tlag   	      decalage temporel au maximum de covariance (s) 
        cod_ret       code de retour :
                       0 : OK
                      -1 : data_time_in[-1] < data_time_bnds[0][0]
                      -2 : data_time_bnds[-1][1] < data_time_in[0]
        tab_stat      tableau des statistiques :
                      tab_stat[0] = float(nb_moy)
                      tab_stat[1] = float(nb_zero)
                      tab_stat[2] = float(nb_inf)


    @Météo-France CNRM/GMEI/TRAMM 
    le 04/05/2021

    """
    
    #
    # Copie des variables dans des structures numpy
    #
    cod_ret = np.array([0],dtype=np.float) 
    tab_stat = np.array([1,2,3],dtype=np.float) ### commencer à 0 serait aussi bien...
 
    data_X = np.ones(len(X), dtype=float)
    data_X[:] = X
    data_Y = np.ones(len(Y), dtype=float)
    data_Y[:] = Y
    data_time_in = np.ones(len(time_in), dtype=np.float64)
    data_time_in[:] = time_in
    data_tolerance_mnq = np.ones(1, dtype=np.int32)
    data_tolerance_mnq[:] = tolerance_mnq
    data_time_out = np.ones(len(time_out), dtype=np.float64)
    data_time_out[:] = time_out
    data_time_bnds = np.ones((len(time_bnds),2), dtype=np.float64)
    data_time_bnds[:] = time_bnds
    tlag_min = float(tlag_min)
    tlag_max = float(tlag_max)

    #
    # Préparation des tableaux pour les retours
    #
    Cov_XY =  np.ones(len(time_out), dtype=float)*np.nan
    Corr_XY =  np.ones(len(time_out), dtype=float)*np.nan 
    Nbsec_valid = np.ones(len(time_out), dtype=float)*np.nan
    tlag = np.ones(len(time_out), dtype=np.float)*np.nan 

    #
    # Pré-diagnostics
    #
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
        return Cov_XY, Corr_XY, Nbsec_valid, tlag, cod_ret, tab_stat

    #
    # Boucle sur les periodes d'integration données par time_bnds
    #
    for i in range(len(data_time_out)) :
        time_inf = data_time_bnds[i][0]
        time_sup = data_time_bnds[i][1]
        # Appel de la fonction
        cov, cor, nb_sec, lag, nb_ok = calcule_covar_max(data_X, 
                                                         data_Y, 
                                                         data_time_in, 
                                                         tlag_min, 
                                                         tlag_max, 
                                                         time_inf, 
                                                         time_sup)

        if nb_ok == 0 :
            Cov_XY[i] = np.nan
            Corr_XY[i] = np.nan
            Nbsec_valid[i] = 0
            tlag[i] = np.nan
            nb_zero += 1
        elif nb_ok <= data_tolerance_mnq[0] :
            Cov_XY[i] = np.nan
            Corr_XY[i] = np.nan
            Nbsec_valid[i] = 0
            tlag[i] = np.nan
            nb_inf += 1
        else :
            Cov_XY[i] = cov
            Corr_XY[i] = cor
            Nbsec_valid[i] = nb_sec
            tlag[i] = lag
            nb_moy += 1
    tab_stat[0] = float(nb_moy)
    tab_stat[1] = float(nb_zero)
    tab_stat[2] = float(nb_inf)

    return (
           np.array(Cov_XY, dtype=np.float), 
           np.array(Corr_XY, dtype=np.float), 
           np.array(Nbsec_valid, dtype=np.float),
           np.array(tlag, dtype=np.float),
           cod_ret, tab_stat
           )

def calcule_covar_max(data_X, data_Y, time_in, tlag_min, tlag_max, time_inf, time_sup, ) :
    """
        Calcule le maximum de covariance sur la période de temps définie par time_inf
        et time_sup. On retourne aussi la corrélation, et le décalage correspondant
        à ce maximum aisi que le nombre de secondes utilisées pour le calcul.
        L'algorithme fait varier X entre [time_inf+tlag_min, time_sup+tlag_max] et
        corrèle à chaque itération avec Y[time_inf, time_sup].
    """
    # Préparation des données
    echantillon_X = data_X[np.where(np.logical_and(time_in>time_inf+tlag_min, time_in<=time_sup+tlag_max))]
    echantillon_Y = data_Y[np.where(np.logical_and(time_in>time_inf, time_in<=time_sup))]
    nb_loop = len(echantillon_X)-len(echantillon_Y)+1
    time_X = time_in[np.where(np.logical_and(time_in>time_inf+tlag_min, time_in<=time_sup+tlag_max))]
    time_Y = time_in[np.where(np.logical_and(time_in>time_inf, time_in<=time_sup))]
    Fe = len(time_Y)/(time_Y[-1] - time_Y[0])

    # Tableaux résultats
    T_Cov_XY = np.empty(nb_loop)
    T_Corr_XY = np.empty(nb_loop)
    T_Var_X = np.empty(nb_loop)
    T_Var_Y = np.empty(nb_loop)
    T_nbval =  np.empty(nb_loop)

    # Décalages successifs de X
    for j in range(nb_loop) :
        Xj = echantillon_X[j:j+len(echantillon_Y)]
        Yj = echantillon_Y
        idx_x = np.isfinite(Xj)
        idx_y = np.isfinite(Yj)
        idx = np.logical_and(idx_x, idx_y) 

        if not idx.any() :
            T_Cov_XY[j] = np.nan
            T_Var_X[j] = np.nan
            T_Var_Y[j] = np.nan
            T_nbval[j] = 0 
            continue
        fluct_Xj = Xj[idx] - np.mean(Xj[idx])
        fluct_Yj = Yj[idx] - np.mean(Yj[idx])

        T_Cov_XY[j] = np.mean(fluct_Xj*fluct_Yj)
        T_Var_X[j] =  np.var( fluct_Xj ) 
        T_Var_Y[j] =  np.var( fluct_Yj ) 
        T_nbval[j] = len( fluct_Xj )

    if np.isfinite(T_Cov_XY).any() : 
        ix = np.argmax( np.abs(T_Cov_XY) )
        Cov_XY =  T_Cov_XY[ix]
        Corr_XY =  T_Cov_XY[ix]/( np.sqrt(T_Var_X[ix] *  T_Var_Y[ix] )) 
        tlag = time_X[ix+1] - time_Y[0]
        Nbsec_valid = T_nbval[ix]/Fe
        nb_ok = T_nbval[ix]
    else :
        Cov_XY = np.nan
        Corr_XY = np.nan 
        tlag = np.nan 
        Nbsec_valid = 0
        nb_ok = 0

    return Cov_XY, Corr_XY, Nbsec_valid, tlag, nb_ok 

