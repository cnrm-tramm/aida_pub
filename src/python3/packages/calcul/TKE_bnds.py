#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np
import datetime

def fct_TKE_bnds(X_in, Y_in, Z_in, time_in, bnds, rap_mnq) :
    """
        Appel de la fonction de calcul de TKE pour prendre en compte les dimensions 1D et 2D
        
        Input :
            X_in      : 1e composante du vent 
            Y_in      : 2e composante du vent
            Z_in      : composante verticale du vent
            time_in   : temps associé au vecteur X_in, Y_in et Z_in
            fe        : Fréquence de X_in, Y_in et Z_in
            rap_mnq   : Fraction de valeurs manquantes minimale pour le calcul de TKE 
                        (compris entre  0 et 1 )

        Output :
            TKE_calc : TKE calculée à partir de X_in, V_in, Z_in

        @Météo-France CNRM/GMEI/TRAMM 
        le 04/07/2023
    """
    
    # Défintion d'un vecteur temps régulier 
    # avec comme pas de temps le temps d'intégration pour le calcul des covariances
    time_bnds_indexes = time_bnds_to_indexes(time_in, bnds)

    #Initialisation du tableau TKE_out
    if X_in.ndim == 1:
        var_out = np.zeros((bnds.shape[0]),dtype="f")*np.nan
        # Tableau statistiques
        # Element 1 : nombre de données moyennées
        # Element 2 : nombre de périodes où il manquait des données pour calculer la moyenne
        tab_stat = np.array([0,0],dtype=np.int)
        
    else :
        var_out = np.zeros((bnds.shape[0],X_in.shape[1]),dtype="f")*np.nan
        tab_stat = np.zeros((2,X_in.shape[1]),dtype=np.int)
    
    if X_in.ndim == 1:
        var_out, tab_stat = calc_TKE_1D(var_out, X_in,Y_in,Z_in, time_bnds_indexes,rap_mnq,tab_stat)
    else : 
        for c in range(0,X_in.shape[1],1):
        
            var_out[:,c],tab_stat[:,c] = calc_TKE_1D(var_out[:,c],X_in[:,c], Y_in[:,c], Z_in[:,c], time_bnds_indexes, rap_mnq,tab_stat[:,c])

    return var_out, tab_stat

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


def calc_TKE_1D (TKE_1D_out,X,Y,Z,bounds_indexes,rap_mnq,statistiques_out) :
    """
    Calcule la TKE pour un vecteur 1D sur un temps d'intégration donné
    """

    for t in range(bounds_indexes.shape[0]):
    # for t in range(86397,(len(time_integration)-3),1):

        # # On calcule le ratio entre données correctes et données totales dans l'intervalle considéré
        nb_data_X = len(X[bounds_indexes[t][0]:bounds_indexes[t][1]][~np.isnan(X[bounds_indexes[t][0]:bounds_indexes[t][1]])])/len(X[bounds_indexes[t][0]:bounds_indexes[t][1]])
        nb_data_Y = len(Y[bounds_indexes[t][0]:bounds_indexes[t][1]][~np.isnan(Y[bounds_indexes[t][0]:bounds_indexes[t][1]])])/len(Y[bounds_indexes[t][0]:bounds_indexes[t][1]])
        nb_data_Z = len(Z[bounds_indexes[t][0]:bounds_indexes[t][1]][~np.isnan(Z[bounds_indexes[t][0]:bounds_indexes[t][1]])])/len(Z[bounds_indexes[t][0]:bounds_indexes[t][1]])
 
        if nb_data_X < rap_mnq or nb_data_Y < rap_mnq or nb_data_Z < rap_mnq :
            # Si on a pas assez de données dans une période de temps pour faire la moyenne
            TKE_1D_out[t] = np.nan
            statistiques_out[1] = statistiques_out[1]+1
        else :

            # Si on a assez de données on calcule la TKE            
            TKE_1D_out[t] = 0.5*(np.nanvar(X[bounds_indexes[t][0] : bounds_indexes[t][1]],axis = 0) + 
                                 np.nanvar(Y[bounds_indexes[t][0] : bounds_indexes[t][1]],axis = 0) + 
                                 np.nanvar(Z[bounds_indexes[t][0] : bounds_indexes[t][1]],axis = 0))


            statistiques_out[0] = statistiques_out[0]+1
    return TKE_1D_out, statistiques_out