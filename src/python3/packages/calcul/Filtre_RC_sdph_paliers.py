#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np
import datetime

def time_bnds_to_indexes(time_in, time_bnds) :
    """
        Calcule les indices de time_in correspondant au time_bnds.
        Suppose que time_in et time_bnds sont ordonnés chronologiquement
    """
    index_bnds = np.zeros((len(time_bnds),2), dtype=np.int)
    i=0
    for j in range(len(time_bnds)) :
        if time_in[0] > time_bnds[j][1] :
            # palier avant la première data
            index_bnds[j] = [-1, -1]
            continue
        if time_in[-1] < time_bnds[j][0] :
            # palier après la première data
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

def Filtre_RC_sdph_paliers( X_in, time_in, fe, fc, typ, time_bnds):
    """
    Applique un filtre RC sur des paliers.

    Input :
        X_in  : Variable flag d'entrée
        time_in :     temps de X
        fe    : Fréquence de X
        fc    : Fréquence de coupure
        typ   : type de filtre (0:passe bas, 1:passe haut)
        time_bnds : intervalles de temps sur lesquels on applique le calcul

    Output :
        Y : Variable X filtrée


    @Météo-France CNRM/GMEI/TRAMM 
    le 16/12/2022

    """
    #
    # Copie des variables dans des structures numpy
    #
    cod_ret = np.array([0],dtype=np.float) 
    tab_stat = np.array([1,2,3],dtype=np.float)

    # controles
    if fc < 0 :
       cod_ret[0] = -1
    if fe < 0 :
       cod_ret[0] = -2
    if typ not in [0,1] :
       cod_ret[0] = -3
    if cod_ret[0] != 0 :
        X_fil = np.empty(len(X_in), dtype=float)
        X_fil[:] = np.nan
        return Y, cod_ret
    #
    # Préparation des tableaux pour les retours
    #
    X_fil =  np.ones(len(X_in), dtype=float)*np.nan

    time_bnds_indexes = time_bnds_to_indexes(time_in, time_bnds)

    for i in range(len(time_bnds_indexes)) :
        ideb = time_bnds_indexes[i][0]
        ifin = time_bnds_indexes[i][1]+1
        if ideb == -1 :
            # palier hors data
            continue
        else :
            # Appel de la fonction            
            result = filtre_RC_sdph(X_in[ideb:ifin], fe, fc, typ)
            X_fil[ideb:ifin] = result

    return X_fil, cod_ret


def filtre_RC_sdph(data, fe, fc, typ) :
    """
        Filtre RC sans décalage de phase
    """
    tau = 1. / (2 * np.pi * fc);
    a1 = np.exp(-1.0 / (fe * tau));
    b1 = 1.0 - a1;
    
    data_fil = np.ones(len(data), dtype=float)
    data_fil[:] = np.nan
    
    Ndata = data.size
    # on se positionne sur la première valeur non nan
    i = 0;
    while np.isnan(data[i]) and (i < Ndata-1) :
        data_fil[i] = data[i]
        i = i+1
        
    if i >= Ndata :
      # On n'a eu que des valeurs manquantes.
      return data

    # TODO : au lieu de prendre data[i], faire une
    # moyenne de N valeurs de data, N étant calculé
    # en fonction de fe et tau. */
    data_fil[i] = data[i]
    memoire = data_fil[i]
    
    # Puisqu'on va faire des [i-1] dans la boucle, il 
    # est capital de s'assurer que i>0. 
    # On fait donc i = i+1  
    i = i+1;
    
    # s'il n'y a pas de nan dans data :
    if np.where(np.isnan(data))[0].size == 0 :
        while i < Ndata :    
            data_fil[i] = a1 * data_fil[i - 1] + b1 * data[i]
            i = i+1    
    else :
        while i < Ndata :
            if np.isnan(data[i]) :
                data_fil[i] = data[i]
                if not np.isnan (data[i - 1]) :
                    memoire = data_fil[i - 1]
                    # la condition (i-1 > 0) est assurée car i>0,
                    # car le cas  !isfinite (data[0]) a été traité 
                    # par la boucle préliminaire  while (...)
            else :
                if np.isnan (data[i - 1]) :
                    # TODO : calculer la longueur du trou.
                    # Si trou > N(tau, fe), repartir comme en début 
                    # de vecteur (calcul de moyenne). 
                    data_fil[i] = a1 * memoire + b1 * data[i]
                else :
                    data_fil[i] = a1 * data_fil[i - 1] + b1 * data[i]
            i = i+1
            
    if (typ == 1) :
        # filtre passe haut : on enlève les basses réquences au signal d'entrée
        data_fil = data - data_fil
  
    return data_fil
    
