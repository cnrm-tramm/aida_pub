#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""

import numpy as np


def Inv_Klett_sa(X, range_gate, Z, beta_mol, flg_cloud, altitude_max, dist_min,beta_a_init,Sa,extrap_typ) :
    """
    Klett Inversion Constrained by SA

    Input :
        x : backscatter lidar signal
        x_range_gate : array of gate range of lidar  (array with N line and 2 colums for min and max range) 
        z : altitude of lidar measurements
        beta_mol : Molecular diffusion
        flg_cld : Cloud flag (0 : no flag, !=0 : altitude of cloud )
        altitude_max : max ref altitude 
        dist_min : 
        beta_a_init : valeur initiale de Beta
        sa : value of Sa 
        extrap_typ : type extrapolation proche du lidar 'cst' or 'lin'

    Output :
        Beta : Aerosol backscatterring coefficient (profil 1D)
        aod :  Aerosol optical depth 

    
    
    Auteur :  CNRM/GMEI/TRAMM février 2018
                transcodage de scilab en Python a partir de la filiere BASIC du LOA 
                fonction scilab originale : Inv_Klett_sa.sci
    """

    Xc = np.copy(X)

    # calcul de la resolution du lidar a partir des bornes

    range_resol = np.diff( (range_gate[:,1]+range_gate[:,0])/2. )
    range_resol = np.append ( range_resol, range_resol[-1] )

    #Moleculaire a lire dans le programme avant
    Smol=8*np.pi/3.

    beta_aer = np.empty((0, X.shape[1]))
    AOD = np.empty(0)
    BETA=np.zeros(X.shape[1])
    beta_aer_i=np.zeros(X.shape[1])

    k = 0
    for x_i, z_i, alt_max_i, flg_cloud_i, beta_mol_i in zip( Xc, Z, altitude_max, flg_cloud, beta_mol ) : 

        BETA[:] = 0.
        beta_aer_i[:] = 0.

        if flg_cloud_i > 0 and flg_cloud_i <= alt_max_i :
            beta_aer = np.vstack((beta_aer, np.full(z_i.shape, np.nan) ))
            AOD = np.append( AOD, np.nan)
            continue
        
        Nref= np.argmin ( np.abs( z_i - alt_max_i) ) + 1 
        #print ('flgcld, alt_max_i, Nref : ', flg_cloud_i, alt_max_i, Nref)
        BETA[Nref-1]=beta_mol_i[Nref-1]*1+beta_a_init


        Saer_OK=Sa
          
        int1 = np.empty(Nref)    
        int2 = np.empty(Nref)    
        #Inversion avec le bon Saer

        # la fonction numpy.nancumsum n'existe pas dans la version du
        # package nmupy que nous avons. On fait a la main.
        #int1[0:Nref]=np.nancumsum((Saer_OK-Smol)*beta_mol_i[0:Nref]*range_resol[0:Nref])
        for i in range(len(int1)) :
            int1[i] = np.nansum( (Saer_OK-Smol)*beta_mol_i[0:i+1]*range_resol[0:i+1])
        int1=2.*int1[-1]-2.*int1

        PHI =(np.log(x_i[0:Nref]/x_i[Nref-1]) + int1)

        #    int2=2.*np.nancumsum(Saer_OK*np.exp(PHI[0:Nref])*range_resol[0:Nref])
        for i in range(len(int2)) :
            int2[i]=2.*np.nansum(Saer_OK*np.exp(PHI[0:i+1])*range_resol[0:i+1])

        int2=int2[-1]-int2


        BETA[0:Nref-1] =(np.exp(PHI[0:Nref-1]))/((1/BETA[Nref-1])+int2[0:Nref-1])

        beta_aer_i[0:Nref]=BETA[0:Nref]-beta_mol_i[0:Nref]

        if extrap_typ=='cst' :
            imin =  np.argmin( np.abs(range_gate[:,1] - dist_min)) + 1 
            beta_aer_i[0:imin]=beta_aer_i[imin]*np.ones(beta_aer_i[0:imin].shape )

        
        #Calcul de l'AOD du profil
        sigma_aer= Saer_OK*beta_aer_i
        #vec_AOD=np.cumsum(sigma_aer * range_resol)
        #AOD_i=vec_AOD[-1]
        AOD_i = np.nansum (sigma_aer * range_resol) 

#        print ('AOD :', k, AOD_i)

        beta_aer= np.vstack((beta_aer, beta_aer_i))
        AOD = np.append( AOD, AOD_i)
        
        k = k+1
        

    return beta_aer,AOD 

