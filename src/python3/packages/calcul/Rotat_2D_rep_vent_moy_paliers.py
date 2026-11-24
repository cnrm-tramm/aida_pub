#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np
import math
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

    
def inter_bnds_to_indexes(time_in, index_bnds) :
    """
        Calcule les indices de time_in correspondant aux intervalles entre les time_bnds
        et retourne la liste complète des indices (paliers + intervalles)
        Suppose que time_in et time_bnds sont ordonnés chronologiquement
    """
    index_inter_bnds = []
    nb_indices = len(time_in)
    i0 = 0
    for bnds in index_bnds :
        if bnds[0] == -1 :
            continue
        if bnds[0] != i0 :
            index_inter_bnds.append([i0, bnds[0]-1])
        index_inter_bnds.append(list(bnds))
        i0 = bnds[1]+1
    # intervalle de fin si besoin
    if i0 < nb_indices :
        index_inter_bnds.append([i0, nb_indices-1])

    return index_inter_bnds

        
def Rotat_2D_rep_vent_moy_paliers( u, v, w, time_in, time_bnds):
    """
    Application d’une rotation 2D destinée à annuler les composantes transverses (v) et verticales (w)
    moyennes du vent, sur des paliers définis par time_bnds.
    On applique cette rotation en calculant le vent moyen sur chaque palier mais également entre les paliers.

    Input :
        u  : première composante horizontale du vent
        v  : seconde composante horizontale du vent
        w  : composante verticale du vent
        time_in : temps de u,v et w
        time_bnds : intervalles de temps sur et entre lesquels on applique le calcul

    Output :
        u_rot   : première composante horizontale du vent selon U moyen
        v_rot   : seconde composante horizontale du vent dans le repère UVW moyen
        w_rot   : composante verticale du vent dans le repère UVW moyen
        cod_ret : code retour d'écécution


    @Météo-France CNRM/GMEI/TRAMM 
    le 24/11/2023

    """
    
    #
    # Préparation des tableaux pour les retours
    #
    u_rot =  np.ones(u.shape, dtype=float)*np.nan
    v_rot =  np.ones(v.shape, dtype=float)*np.nan
    w_rot =  np.ones(w.shape, dtype=float)*np.nan
    cod_ret = 0
    time_bnds_indexes = time_bnds_to_indexes(time_in, time_bnds)
    index_inter_bnds = inter_bnds_to_indexes(time_in, time_bnds_indexes)

    for i in range(len(index_inter_bnds)) :
    # for i in range(0,1) :
        ideb = index_inter_bnds[i][0]
        ifin = index_inter_bnds[i][1]+1
        if ideb == -1 :
            # palier hors data
            continue
        else :
            # Appel de la fonction      
            if u.ndim == 1 :      
                ur, vr, wr = Rotat_2D_rep_vent_moy(u[ideb:ifin], v[ideb:ifin], w[ideb:ifin])
                u_rot[ideb:ifin] = ur
                v_rot[ideb:ifin] = vr
                w_rot[ideb:ifin] = wr
            else :
                for c in range(u.shape[1]):
                    # On boucle sur les altitudes pour se ramener à un problème 1D
                    ur, vr, wr = Rotat_2D_rep_vent_moy(u[ideb:ifin,c], v[ideb:ifin,c], w[ideb:ifin,c])
                    u_rot[ideb:ifin,c] = ur
                    v_rot[ideb:ifin,c] = vr
                    w_rot[ideb:ifin,c] = wr


    return u_rot, v_rot, w_rot, cod_ret


def Rotat_2D_rep_vent_moy(u, v, w) :
    """
        Double rotation dans le repère du vent moyen destinée à annuler 
        les composantes transverses (v) et verticales (w) moyennes du vent 
        pour ne garder que les fluctuations. 
        On obtient au final, si U est le module du vent :
            umoy=U
            vmoy=0
            wmoy=0
    """    

    # Première rotation autour de l'axe w 
    theta=np.arctan2(np.nanmean(v),np.nanmean(u))
    u1 = u*np.cos(theta) + v*np.sin(theta)
    v1 = -u*np.sin(theta) + v*np.cos(theta)
    w1 = w
    
    # Seconde rotation autour de l'axe v  
    phi = np.arctan2(np.nanmean(w1),np.nanmean(u1))
    # On considère qu'une pente d'écoulement > 20° est suspecte
    if abs(phi) > 0.3490658 : # 20° en radians
        print("PHI>20 !", phi)
        phi = math.copysign(0.3490658,phi) # on fixe phi à 20° en gardant son signe
        print(phi)
    u2 = u1*np.cos(phi) + w1*np.sin(phi)
    v2 = v1
    w2=  -u1*np.sin(phi) + w1*np.cos(phi)
    
    ur = u2
    vr = v2
    wr = w2
    
    return ur, vr, wr
    
