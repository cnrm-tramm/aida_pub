#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np

def fct_TKE(X_in, Y_in, Z_in, time_in, T_int, rap_mnq) :
    """
        Appel de la fonction de calcul de TKE pour prendre en compte les dimensions 1D et 2D
        
        Input :
            X_in      : 1e composante du vent 
            Y_in      : 2e composante du vent
            Z_in      : composante verticale du vent
            time_in   : temps associé au vecteur X_in, Y_in et Z_in
            fe        : Fréquence de X_in, Y_in et Z_in
            T_int     : temps d'intégration pour le calcul des covariances
            rap_mnq   : Fraction de valeurs manquantes minimale pour le calcul de TKE 
                        (compris entre  0 et 1 )

        Output :
            TKE_calc : TKE calculée à partir de X_in, V_in, Z_in

        @Météo-France CNRM/GMEI/TRAMM 
        le 04/07/2023
    """
    # Code de retour
    cod_ret = 0

    #
    # Pré-diagnostics
    #
    # Défintion d'un vecteur temps régulier 
    # avec comme pas de temps le temps d'intégration pour le calcul des covariances
    # On ajoute un élément de plus à la fin de time_integration pour que la boucle de la TKE prenne en compte le dernier élément
    time_integration = np.arange(time_in[0], (time_in[-1]+3*T_int), T_int)
    time_in = np.append(time_in,(time_in[1] - time_in[0])+time_in[-1])
       
    #Initialisation du tableau TKE_out
    if X_in.ndim == 1:
        # Tableau statistiques
        # Element 1 : nombre de données moyennées
        # Element 2 : nombre de périodes où il manquait des données pour calculer la moyenne
        tab_stat = np.array([0,0],dtype='f')
        var_out = np.ones((len(time_integration)-3),dtype='f')*np.nan
    else :
        # Tableau statistiques
        # Element 1 : nombre de données moyennées
        # Element 2 : nombre de périodes où il manquait des données pour calculer la moyenne
        tab_stat = np.zeros((2,X_in.shape[1]),dtype='f')
        var_out = np.ones(((len(time_integration)-3),X_in.shape[1]),dtype='f')*np.nan

    ###
    # Diagnostics
    ###
    if T_int < 0 :
        cod_ret = -1
    if rap_mnq > 1 or rap_mnq < 0 :
        cod_ret = -3

    if cod_ret != 0 :
        return var_out, cod_ret, tab_stat
    
    # Pour prendre en compte l'aspect 2D, on regarde la dimension de X_in
    # Si X_in est 2D, dans ce cas on boucle sur les colonnes
    if X_in.ndim == 1 :
        var_out, tab_stat = calc_TKE_1D(var_out,X_in,Y_in,Z_in, time_in,time_integration,rap_mnq,tab_stat)

    else : 
        for c in range(0,X_in.shape[1],1):
        
            var_out[:,c],tab_stat[:,c] = calc_TKE_1D(var_out[:,c],X_in[:,c], Y_in[:,c], Z_in[:,c], time_in, time_integration, rap_mnq,tab_stat[:,c])

    return var_out, cod_ret, np.array(tab_stat, dtype = int)



def calc_TKE_1D (TKE_1D_out,X,Y,Z,time_in,time_integration,rap_mnq,statistiques_out) :
    """
    Calcule la TKE pour un vecteur 1D sur un temps d'intégration donné
    """
    index = np.searchsorted(time_in,time_integration, side = "left")

    for t in range(0,(len(time_integration)-3),1):
    # for t in range(86397,(len(time_integration)-3),1):

        # On cherche la position des valeurs qui correspondent à l'intervalle de temps considéré
        # On cherche le temps minimal le plus proche 
        index_tps_min = np.argmin(np.abs(time_in[index[t]:index[t]+2] - time_integration[t])) + index[t]
        
        # On cherche le temps maximal le plus proche 
        index_tps_max = np.argmin(np.abs(time_in[index[t+1]:index[t+2]] - time_integration[t+1])) + index[t+1]

        # # On calcule le ratio entre données correctes et données totales dans l'intervalle considéré
        nb_data_X = len(X[index_tps_min:index_tps_max][~np.isnan(X[index_tps_min:index_tps_max])])/len(X[index_tps_min:index_tps_max])
        nb_data_Y = len(Y[index_tps_min:index_tps_max][~np.isnan(Y[index_tps_min:index_tps_max])])/len(Y[index_tps_min:index_tps_max])
        nb_data_Z = len(Z[index_tps_min:index_tps_max][~np.isnan(Z[index_tps_min:index_tps_max])])/len(Z[index_tps_min:index_tps_max])
 
        if nb_data_X < rap_mnq or nb_data_Y < rap_mnq or nb_data_Z < rap_mnq :
            # Si on a pas assez de données dans une période de temps pour faire la moyenne
            TKE_1D_out[t] = np.nan
            statistiques_out[1] = statistiques_out[1]+1
        else :

            # Si on a assez de données on calcule la TKE            
            TKE_1D_out[t] = 0.5*(np.nanvar(X[index_tps_min : index_tps_max],axis = 0) + 
                                 np.nanvar(Y[index_tps_min : index_tps_max],axis = 0)+ 
                                 np.nanvar(Z[index_tps_min : index_tps_max],axis = 0))


            statistiques_out[0] = statistiques_out[0]+1
    return TKE_1D_out, statistiques_out
