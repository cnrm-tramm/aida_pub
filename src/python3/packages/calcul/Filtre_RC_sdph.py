#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
"""
import sys
import numpy as np
import datetime

def Filtre_RC_sdph(X_in, fe, fc, typ) :
    """ Filtre RC sans décalage de phase

        Input :
            X_in  : Variable flag d'entrée
            time_in :     temps de X
            fe    : Fréquence de X
            fc    : Fréquence de coupure
            typ   : type de filtre (0:passe bas, 1:passe haut)

        Output :
            Y : Variable X filtrée


        @Météo-France CNRM/GMEI/TRAMM
        le 04/07/2023
    """
    # Pré-diagnostics
    cod_ret = 0

    # controles
    if fc < 0 :
       cod_ret = -1
    if fe < 0 :
       cod_ret = -2
    if int(typ) not in [0,1] :
       cod_ret = -4

    if cod_ret != 0 :
        X_fil = np.empty(len(X_in), dtype=float)
        X_fil[:] = np.nan
        return X_fil, cod_ret

    if fc == 0:
        return  X_in, 0

    # Préparation des tableaux pour les retours
    if X_in.ndim == 1 :
        X_out =  np.ones(len(X_in), dtype=float)*np.nan
    else :
        X_out = np.ones(X_in.shape, dtype = float)*np.nan

    # Pour prendre en compte l'aspect 2D, on regarde la dimension de X_in
    # Si X_in est 2D, dans ce cas on boucle sur les colonnes
    if X_in.ndim == 1 :
        # Données 1D
        X_out = filtre_RC_1D(X_in, fc, fe, typ)
    else :
        # Données 2D
        for c in range (0,X_in.shape[1]) :
            X_out[:,c] = filtre_RC_1D(X_in[:,c], fc, fe, typ)

    return X_out,cod_ret


def filtre_RC_1D (data, fc, fe, typ) :
    """ Applique un filtre RC aux données 1D
        Si typ = 1, c'est un filtre passe-haut qui est appliqué
    """
    # Définitions des constantes
    tau = 1. / (2 * np.pi * fc)
    a1 = np.exp(-1.0 / (fe * tau))
    b1 = 1.0 - a1

    data_out =  np.ones(len(data), dtype=float)*np.nan
    Ndata = data.size

    # on se positionne sur la première valeur non nan
    i = 0
    while np.isnan(data[i]) and (i < Ndata) :
        data_out[i] = data[i]
        i = i+1

    if i >= Ndata :
      # On n'a eu que des valeurs manquantes.
      return data

    data_out[i] = data[i]
    memoire = data_out[i]

    # Puisqu'on va faire des [i-1] dans la boucle, il
    # est capital de s'assurer que i>0.
    # On fait donc i = i+1
    i = i+1

    # s'il n'y a pas de nan dans data :
    if np.where(np.isnan(data))[0].size == 0 :
        while i < Ndata :
            data_out[i] = a1 * data_out[i - 1] + b1 * data[i]
            i = i+1
    else :
        while i < Ndata :
            if np.isnan(data[i]) :
                data_out[i] = data[i]
                if not np.isnan (data[i - 1]) :
                    memoire = data_out[i - 1]
                    # la condition (i-1 > 0) est assurée car i>0,
                    # car le cas  !isfinite (data[0]) a été traité
                    # par la boucle préliminaire  while (...)
            else :
                if np.isnan (data[i - 1]) :
                    data_out[i] = a1 * memoire + b1 * data[i]
                else :
                    data_out[i] = a1 * data_out[i - 1] + b1 * data[i]
            i = i+1

    if (typ == 1) :
        # filtre passe haut : on enlève les basses réquences au signal d'entrée
        data_out = data - data_out

    return data_out
