#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np


def Covar_XY_max( X, Y, Fe, Tint, tlag_min, tlag_max):
    """
    Compute maximum covariance between X and Y with timelag varying in tlag_min, tlagmax

    IN : 
        X           premier vecteur
        Y           second vecteur
        Fe          fréquence d'échantillonnage des données (Hz)	
        Tint        Temps d'intégration pour le calcul du flux (s)	
        tlag_min    Borne minimale de variation du décalage temporel pour le calcul du maximum de covariance
        tlag_max	Borne maximale de variation du décalage temporel pour le calcul du maximum de covariance

    OUT : 
        Cov_xy        Covariance 
        Cor_xy        Correlation
        Nbsec_valid   nombre de secondes valides sur lequel la covariance a été calculée (s)
        tlag   	      decalage temporel au maximum de covariance (s) 


    @Météo-France CNRM/GMEI/TRAMM
    W. Maurel 
    le 13/08/2020

    """
    
    nbpt_int = np.floor ((Tint * Fe) + 0.5)

    ntour = int( len(X)//nbpt_int )
    reste = len(X)%nbpt_int

    if reste == 0 :
        r = 0
    else :
        r = 1

    ndecal =  int( Fe * ( tlag_max - tlag_min ) +1 ) 

    Cov_XY_j = np.empty(ndecal)
    Corr_XY_j = np.empty(ndecal)
    Var_X_j = np.empty(ndecal)
    Var_Y_j = np.empty(ndecal)
    nbval_j =  np.empty(ndecal)

    Cov_XY =  np.empty(ntour+r) 
    Corr_XY =  np.empty(ntour+r) 
    tlag = np.empty(ntour+r)  
    Nbsec_valid = np.empty(ntour+r)

    #  boucle sur les periodes d'integration 
    for k in range (ntour) :

        # boucle sur le decalage 
        for j, decal in enumerate ( range (int(tlag_min*Fe), int(tlag_max*Fe + 1) ) ) :

            ideb = int(k*nbpt_int - min(0,tlag_min*Fe) )
            ifin = int((k+1)*nbpt_int - max(0, tlag_max*Fe)  ) 

            Xj = X[ideb+decal:ifin+decal]
            Yj = Y[ideb:ifin]

            idx_x = np.isfinite(Xj)
            idx_y = np.isfinite(Yj)

            idx = np.logical_and(idx_x, idx_y) 

            if not idx.any() :
                Cov_XY_j[j] = np.nan
                Var_X_j[j] = np.nan
                Var_Y_j[j] = np.nan
                nbval_j[j] = 0 
                continue


            fluct_Xj = Xj[idx] - np.mean(Xj[idx])
            fluct_Yj = Yj[idx] - np.mean(Yj[idx])

            Cov_XY_j[j] = np.mean(fluct_Xj*fluct_Yj)
            Var_X_j[j] =  np.var( fluct_Xj ) 
            Var_Y_j[j] =  np.var( fluct_Yj ) 

            nbval_j[j] = len( fluct_Xj ) 

        if np.isfinite(Cov_XY_j).any() : 
            ix = np.argmax( np.abs(Cov_XY_j) )
            Cov_XY[k] =  Cov_XY_j[ix]
            Corr_XY[k] =  Cov_XY_j[ix]/( np.sqrt(Var_X_j[ix] *  Var_Y_j[ix] )) 
            tlag[k] = ix/Fe + tlag_min  
            Nbsec_valid[k] = nbval_j[ix]/Fe
        else :
            Cov_XY[k] = np.nan
            Corr_XY[k] = np.nan 
            tlag[k] = np.nan 
            Nbsec_valid[k] = 0


    nbval_out = k+1
    #     ax[0].plot(Cov_XY_j)
    #f.show()
    if reste != 0 :
        k = k + 1
        Cov_XY[k] = np.nan
        Corr_XY[k] = np.nan 
        tlag[k] = np.nan 
        Nbsec_valid[k] = 0
        nbval_out = k+1


    return  Cov_XY, Corr_XY, Nbsec_valid, tlag

    
