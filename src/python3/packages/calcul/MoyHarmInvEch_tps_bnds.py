#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import warnings
import datetime 
from scipy.stats import hmean

def fct_MoyHarmInvEch_tps_bnds (var_in, time_in, tolerance_mnq, time_out, time_bnds, val_inv, val_repl) :
    """
    Effectue le calcul de la fonction "fonction" aux temps "time_out" sur
    des intervalles définis par "time_bnds".

    Input :
        var_in : variable d'entrée sur laquelle on opère le calcul
        time in : variable temps associé à var_in
        tolerance_mnq : nombre de valeurs manquantes au-dela duquel on ne fera pas le calcul
        time_out  : variable temps de sortie
        val_inv : valeur invalide pour laquelle l'écart-type n'est pas calculé
        val_remplac : valeur de remplacement quand la valeur atteint val_inv avec une tolérance

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
    var_out = np.ones(var_in.shape, dtype=float)*np.nan
    pre_diag = 0
    nb_moy = 0
    nb_zero = 0
    nb_inf = 0
    
    if time_in[-1] < time_bnds[0][0] :
        pre_diag = -1
        nb_zero = len(time_bnds)
    if time_bnds[-1][1] < time_in[0] :
        pre_diag = -2
        nb_zero = len(time_bnds)
    if pre_diag != 0 :
        tab_stat[0] = nb_moy
        tab_stat[1] = nb_zero
        tab_stat[2] = nb_inf
        cod_ret[0] = pre_diag
        return var_out, cod_ret, tab_stat

    time_bnds_indexes = time_bnds_to_indexes(time_in, time_bnds)

    for i in range(len(time_bnds_indexes)) :
        if time_bnds_indexes[i][0] == -1 :
            var_out[i] = np.nan
            nb_zero += 1
        else :
            # Appel de la fonction
            result, nb_ok = calcule_moyharminv(var_in[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1],val_inv,val_repl)
            if nb_ok == 0 :
                var_out[i] = np.nan
                nb_zero += 1
            elif nb_ok <= tolerance_mnq :
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

    return index_bnds

def calcule_moyharminv(echantillon,val_inv,val_replac) :
    """
        Calcule la moyenne sur un echantillon sauf pour les valeurs = val_inv .
        Si une des valeurs de l'intervale est invalide le calcul est considéré comme invalide et le resultat
        sera égal a val_replac
        si la valeur est mise a val_inv on considere qu'elle est valide pour le calcul de la tolérance: augmentation de nb_Ok
        harmonic_mean de numpy Pas encore implémentée dans les sources python3.7 ? ou 3.5
        creation d'un masque array pour gérer les val_inv + les Nan
    """
    nb_ok = 0
    
    with warnings.catch_warnings():
        warnings.filterwarnings('error') 
        try :
            #annulation des Nan  sinon on ne peut pas comparer aux val_inv
            nb_total=len(echantillon)
            mx2=np.ma.masked_array(echantillon,np.isnan(echantillon))
            mx2=mx2.compressed()
            nb_ok=len(mx2)
            nb_nan=nb_total - nb_ok
            #recherche de valeurs invalides dans l'échantillon
            mx=np.ma.masked_array(mx2,mx2>=val_inv)
	    #on invalide aussi les matrices vides ou totalement masquées non traitées par hmean
            nb_valid=len(mx[~mx.mask])
            # si on a au moins 1 valeur invalide le resultat est invalide
            if nb_valid < nb_ok:
                result = val_replac
            elif nb_valid == nb_ok:
                result= hmean(mx)
            else:
                result = np.nan
        except RuntimeWarning as e:
            print("ERR:{}".format(e))
            result = np.nan
    nb_ok = echantillon.size - np.count_nonzero(np.isnan(echantillon))
    
    return result, nb_ok