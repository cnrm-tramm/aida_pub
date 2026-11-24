#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""
import sys
import numpy as np


def fct_Extract_Closest_PointLatLonAlt(X_in, lats, lons, alts, tgt_lat, tgt_lon, tgt_alt):
    """
    

    Input :


    Output :

        
    Auteur :  CNRM/GMEI/TRAMM avril 2024
    """

    # Préparation altitude :
    # alts = alts[0,:,:,0].flatten()
    RAYON_TERRE = 6375e3
    print(tgt_lat)
    print(tgt_lon)
    print(tgt_alt)
    tgt_lat = np.ones(len(lats))*tgt_lat
    tgt_lon = np.ones(len(lons))*tgt_lon
    tgt_alt = np.ones(len(alts))*tgt_alt
    alts = np.array(alts)
    d = (np.deg2rad(lats-tgt_lat)*RAYON_TERRE)**2 + (np.deg2rad(lons-tgt_lon)*RAYON_TERRE*np.cos(np.deg2rad(lats)))**2+(1/9.80665*alts-tgt_alt)**2

    indice = d.argsort()[0]

    index_D = np.unravel_index(indice, X_in[0,:,:,0].shape)
    print(index_D)

    X_out = X_in[:,index_D[0],index_D[1],:]

    return(X_out)
