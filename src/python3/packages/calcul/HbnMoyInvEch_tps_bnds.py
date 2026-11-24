#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import numpy as np
import warnings
import datetime 
from scipy.stats import hmean
 
def fait_calcul_tps_bnds_3couches (var_in1,var_in2,var_in3, 
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
        var_out1, var_out2, var_out3    : variables calculées
        cod_ret                         : code retour
        tab_stat1, tab_stat2, tab_stat3 : tableaux de diagnostics respectifs de
                                          var_out1, var_out2,.var_out3

        
    Auteur :  CNRM/GMEI/TRAMM décembre 2020         
    """

    #
    # Copie des variables dans des structures numpy
    #
    cod_ret = np.array([0],dtype=np.float) 
    tab_stat1 = np.array([1,2,3],dtype=np.float) 
    tab_stat2 = np.array([1,2,3],dtype=np.float) 
    tab_stat3 = np.array([1,2,3],dtype=np.float) 
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
    var_out1 = np.ones(len(time_out), dtype=float)*np.nan
    var_out2 = np.ones(len(time_out), dtype=float)*np.nan
    var_out3 = np.ones(len(time_out), dtype=float)*np.nan
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
        tab_stat1[0] = nb_moy;
        tab_stat1[1] = nb_zero;
        tab_stat1[2] = nb_inf;
        cod_ret[0] = pre_diag;
        return var_out1, var_out2, var_out3, cod_ret, tab_stat1, tab_stat2, tab_stat3

    time_bnds_indexes = time_bnds_to_indexes(data_time_in, data_time_bnds)

    for i in range(len(time_bnds_indexes)) :
      if time_bnds_indexes[i][0] == -1 :
            var_out1[i] = np.nan
            nb_zero += 1
      else :

        # Appel de la fonction
        result1, result2, result3, nb_ok,nb_ok1,nb_ok2 = globals()[fn](var_in1[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1],var_in2[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1],var_in3[time_bnds_indexes[i][0]:time_bnds_indexes[i][1]+1],sarg_sup)
        nb_moy = 0
        nb_zero = 0
        nb_inf = 0
        if nb_ok == 0 :
            var_out1[i] = np.nan
            nb_zero += 1
        elif nb_ok <= data_tolerance_mnq[0] :
            var_out1[i] = np.nan
            nb_inf += 1
        else :
            var_out1[i] = result1
            nb_moy += 1
        tab_stat1[0] = float(nb_moy);
        tab_stat1[1] = float(nb_zero);
        tab_stat1[2] = float(nb_inf);

        nb_moy = 0
        nb_zero = 0
        nb_inf = 0
        if nb_ok1 == 0 :
            var_out2[i] = np.nan
            nb_zero += 1
        elif nb_ok1 <= data_tolerance_mnq[0] :
            var_out2[i] = np.nan
            nb_inf += 1
        else :
            var_out2[i] = result2
            nb_moy += 1
        tab_stat2[0] = float(nb_moy);
        tab_stat2[1] = float(nb_zero);
        tab_stat2[2] = float(nb_inf);

        nb_moy = 0
        nb_zero = 0
        nb_inf = 0
        if nb_ok2 == 0 :
            var_out3[i] = np.nan
            nb_zero += 1
        elif nb_ok2 <= data_tolerance_mnq[0] :
            var_out3[i] = np.nan
            nb_inf += 1
        else :
            var_out3[i] = result3
            nb_moy += 1
        tab_stat3[0] = float(nb_moy);
        tab_stat3[1] = float(nb_zero);
        tab_stat3[2] = float(nb_inf);

    return np.array(var_out1, dtype=np.float), \
           np.array(var_out2, dtype=np.float), \
           np.array(var_out3, dtype=np.float), \
           cod_ret,                            \
           tab_stat1, tab_stat2, tab_stat3

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


# fonction de calcul de la moyenne en mettant la moyenne a val_rempl si une des valeur de l'échantillon atteint val_inv
def calcule_moy_with_inv(echantillon,val_inv, val_replac):
    couche_inv=False
    moy=np.nan
    nb_ok=0
    # on teste la présence de valeurs inv
    epsilon=0.0001
    for ech in echantillon:
        if abs(ech-val_inv) < epsilon:
            couche_inv=True
    # si on a trouvé une valeur invalide on met la moyenne a inv
    if couche_inv:
        moy=val_replac
        nb_ok=echantillon.size - np.count_nonzero(np.isnan(echantillon))
    else:
        moy=np.nanmean(echantillon)
        nb_ok=echantillon.size - np.count_nonzero(np.isnan(echantillon))
    return moy,nb_ok

# fonction de calcul de la moyenne en mettant la moyenne à val_rempl si les valeurs de echantillon=val_inv > tolerance_inv
def calcule_moy_with_inv_and_tolerance(echantillon,val_inv, val_replac,tolerance_inv):
    couche_inv=False
    nb_inv=0 # nb de couche inv dans l'échantillon
    nb_valid=0 # nb de couche valide
    moy=np.nan
    nb_ok=0
    som_valid=0
    # on teste la présence de valeurs inv
    epsilon=0.0001
    for ech in echantillon:
        #on exclut les nans de l'échantillon
        if not np.isnan(ech):
          if abs(ech-val_inv) < epsilon:
            nb_inv=nb_inv+1
            couche_inv=True
          else: 
            nb_valid=nb_valid+1
            som_valid=som_valid+ech

    # on a trouve des couches valides et invalides dans l'échantillon cela dépent de la tolerance_inv
    if couche_inv: 
        #on exclut les nans de l'échantillon
        nb_ok=echantillon.size - np.count_nonzero(np.isnan(echantillon))
        # si trop de valeur invalide dans l'échantillon on met a val_remplac
        if nb_inv/(nb_valid+nb_inv)>tolerance_inv:
            moy=val_replac
        # sinon on fait la moyenne de ce qui reste et on compte à la main le nb d'erreur
        else:
            if nb_valid !=0:
                moy=som_valid/nb_valid
            else:
                moy=np.nan
                nb_ok=0
    # sinon on fait la moyenne de l'échantillon
    else:
        moy=np.nanmean(echantillon)
        nb_ok=echantillon.size - np.count_nonzero(np.isnan(echantillon))
    return moy,nb_ok

def calcule_moy_3couches(echantillon1,echantillon2,echantillon3, sarg_sup) :
    """
        Calcule la moyenne sur l'intervalle défini par time_inf et time_sup, si le nombre de couches reste constante pendant la periode. Sinon on met valeur indéterminée: val_replac=sarg_sup[1]
        Calcule la moyenne sur l'intervalle défini par time_inf et time_sup et met a val_replac toutes les moyennes dont un des elements est = inv.
        si la valeur est mise a val_replac on considere qu'elle est valide: augmentation de nb_Ok
        
    """
    avec_tolerance=True
    with warnings.catch_warnings():
        warnings.filterwarnings('error') 
        try :
            #t=sarg_sup.split(':')
            inv=(float(sarg_sup.split(':')[0]))
            val_replac=float(sarg_sup.split(':')[1])
            try:
                tolerance_inv=float(sarg_sup.split(':')[2])
            except Exception as e:
                print("INFO pas de tolerance_inv:{}".format(e))
                avec_tolerance=False
                tolerance_inv=0

            # calcul du nombre de couche: en fait il y a toujours 3 couches mais elles peuvent avoir:
            # une valeur finie, 
            # une valeur seuillée :valeur=inv 
            # ou manquante: valeur = nan
            # => on vérifie que le type de couche ne change pas sur la période d'échantillonage: couche val finie, inv ou Nan
            # si la valeur est val_inv tout le temps, la valeur est mises a val_rempl
            # par contre si la valeur est non seuillée mais que des valeurs atteignent inv la moyenne est mise a nan
            # tableau de valeurs valides ou inv pour chaque couche


            # recherche des changements de couche inférieures à val_seuil
            couche_inv=False
            debut = True
            epsilon=0.0001 # precision
            for ech1,ech2,ech3 in zip(echantillon1,echantillon2,echantillon3):
                # calcul du nb de couche initiale 
                nbcouche=0
                if debut:
                    for ech in [ech1,ech2,ech3]:
                        if abs(ech - inv) > epsilon:
                            nbcouche=nbcouche+1
                    nbcoucheprec=nbcouche
                    debut=False
                #vérification que le nb de couche ne change pas ensuite
                else:
                    nbcouche=0
                    for ech in [ech1,ech2,ech3]:
                        if abs(ech - inv) > epsilon:
                            nbcouche=nbcouche+1
                    if nbcouche!=nbcoucheprec:
                        couche_inv=True
                    nbcouche_prec=nbcouche
                #print("nbcouche={}couche_inv={}".format(nbcouche_prec,couche_inv))

            nb_ok=np.zeros(3)   # tableau des resultats des moyennes
            result=np.full([3],np.nan)  # tableau des resultats des nb_ok
            # si le nb de couche a changé pendant la période. On invalide les donnees (NaN)
            if couche_inv==True:
                result[0] = np.nan
                result[1] = np.nan
                result[2] = np.nan
            else:
                if avec_tolerance:
                    # on calcule une moyenne en fonction d'une tolerance de valeurs invalidées: essai a 30%
                    result[0],nb_ok[0]=calcule_moy_with_inv_and_tolerance(echantillon1,inv, val_replac,tolerance_inv)
                    result[1],nb_ok[1]=calcule_moy_with_inv_and_tolerance(echantillon2,inv, val_replac,tolerance_inv)
                    result[2],nb_ok[2]=calcule_moy_with_inv_and_tolerance(echantillon3,inv, val_replac,tolerance_inv)
                else:
                    # on met a val_replace des qu'une valeur pas de valeur finie a valeur seuillée sur la période
                    result[0],nb_ok[0]=calcule_moy_with_inv(echantillon1,inv, val_replac)
                    result[1],nb_ok[1]=calcule_moy_with_inv(echantillon2,inv, val_replac)
                    result[2],nb_ok[2]=calcule_moy_with_inv(echantillon3,inv, val_replac)

        except RuntimeWarning as e:
            #print("RuntimeWarning:{}".format(e))
            result[0] = np.nan
            result[1] = np.nan
            result[2] = np.nan
            nb_ok[0]=0
            nb_ok[1]=0
            nb_ok[2]=0

    return result[0],result[1],result[2],nb_ok[0], nb_ok[1],nb_ok[2]

