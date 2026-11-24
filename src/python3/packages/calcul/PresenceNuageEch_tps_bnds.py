#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import warnings
import datetime 
from scipy.stats import hmean
 
def fait_calcul_pres_nuage_tps_bnds (var_in1,var_in2,var_in3, 
                             time_in,
                             tolerance_mnq,
                             time_out, 
                             time_bnds,
                             fonction,
                             arg_sup) :
    """
    Effectue le calcul de la fonction "fonction" aux temps "time_out" sur
    des intervalles définis par "time_bnds".

    Input :
        var_in1,2,3 : variables d'entrée sur lesquelles on opère le calcul
        time in : variable temps associé à var_in
        tolerance_mnq : nombre de valeurs manquantes au-dela duquel on ne fera pas le calcul
        time_out  : variable temps de sortie
        time_bnds : intervalles de temps sur lesquels on applique le calcul
        fonction : fonction de calcul
        arg_sup: arguments de la fonction

    Output :
        var_out : variable calculée
        codret: code retour
        tab_stat : tableau de diagnostics

        
    Auteur :  CNRM/GMEI/TRAMM décembre 2020         
    """

    #
    # Copie des variables dans des structures numpy
    #
    cod_ret = np.array([0],dtype=np.float) 
    tab_stat = np.array([1,2,3],dtype=np.float) 
    data_var_in1 = np.ones(len(var_in1), dtype=float)
    data_var_in1[:] = var_in1
    data_var_in2 = np.ones(len(var_in2), dtype=float)
    data_var_in2[:] = var_in2
    data_var_in3 = np.ones(len(var_in3), dtype=float)
    data_var_in3[:] = var_in3
    data_time_in = np.ones(len(time_in), dtype=np.float64)
    data_time_in[:] = time_in
    data_tolerance_mnq = np.ones(1, dtype=np.int32)
    data_tolerance_mnq[:] = tolerance_mnq
    data_time_out = np.ones(len(time_out), dtype=np.float64)
    data_time_out[:] = time_out
    data_fonction = np.ones(len(fonction), dtype='S1')
    data_fonction[:] = fonction[:]
    fn = ''.join([ x.decode('utf-8') for x in data_fonction ])
    data_arg_sup = np.ones(len(arg_sup), dtype='S1')
    data_arg_sup[:] = arg_sup[:]
    # c'est un array de string , il faut le transformer en string
    sarg_sup = ''.join([ x.decode('utf-8') for x in data_arg_sup ])
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
        tab_stat[0] = nb_moy;
        tab_stat[1] = nb_zero;
        tab_stat[2] = nb_inf;
        cod_ret[0] = pre_diag;
        return var_out, cod_ret, tab_stat;

    time_bnds_indexes = time_bnds_to_indexes(data_time_in, data_time_bnds)

    for i in range(len(data_time_out)) :
        if time_bnds_indexes[i][0] == -1 :
            var_out[i] = np.nan
            nb_zero += 1
        else :

            # Appel de la fonction
            result, nb_ok = globals()[fn](var_in1[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1],var_in2[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1],var_in3[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1],sarg_sup)

            if nb_ok == 0 :
                var_out[i] = np.nan
                nb_zero += 1
            elif nb_ok <= data_tolerance_mnq[0] :
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

def calcule_presence_nuage(echantillon1,echantillon2,echantillon3,sarg_sup) :
    """
        Verifie si on a u moins 1 top < val_seuil sur au moins une des couches
        Le résultat contient le pourcentage de top < val_seuil / rapport au nombre de top total
        
    """
    nb_ok=0
    with warnings.catch_warnings():
        warnings.filterwarnings('error') 
        try :
            t=sarg_sup.split(':')
            inv=(float(sarg_sup.split(':')[0]))
            # on prend toutes les valeurs comprises entre time_inf et time_sup logical_and done true et where les selectionne
            # calcul de de présence d'au moins 1 top sur une des 3 couches
            # on veut calculer la moyenne des couches
            # tableau de valeurs valides ou inv pour chaque couche
            nptop=np.array([],dtype=float)
            n=0
            epsilon=0.0001
            for ech1,ech2,ech3 in zip(echantillon1,echantillon2,echantillon3):
                if abs(ech1 -inv) > epsilon or abs(ech2 - inv ) > epsilon or abs(ech3 -inv) >epsilon:
                   nptop=np.append(nptop,1)
                else:
                   nptop=np.append(nptop,0)
                n=n+1
            som=0
            n=0
            for top in nptop:
                som=top +som
                n=n+1
            res=som/n*100.
            result=som*100./n
            nb_ok=echantillon1.size - np.count_nonzero(np.isnan(echantillon1))

        except RuntimeWarning :
            result = np.nan
            nb_ok=0

    return result,nb_ok

