#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""

import numpy as np

def auto_tempe_unit (T) :
    
    if (np.nanmedian(T) > 100.)  or (np.isnan(T).all()) :
        CtoK = 0.
    else : 
        CtoK = 273.15

    return CtoK

def Profil_Diff_Mol_reel (range_gate, zlid, z,Tz,Pz,lambda0) :
    """ 
      Process Extinction and Backscatter coefficient for a standard molecular atmosphere
      
      Input :
         range_gate : array of gate range of lidar  (array with N line and 2 colums for min and max range) 
         zlid : altitude of lidar gate 
         z : altitude of the T,P, profile
         Tz : Temperature profile (K)
         Pz : Pressure at sea level (hPa)
         lambda : Wavelength (nm)

      Output : 
        amol : coefficient d'extinction
        bmol : coefficient de retrodiffusion
        trayleigh : coefficient rayleigh 
        pr2_mol : signal moleculaire retroduiffuse

      Auteur :  CNRM/GMEI/TRAMM octobre 2019
    """ 

    p_He = 8.
    bmol = np.empty((0, zlid.shape[1]))
    amol = np.empty((0, zlid.shape[1]))
    pr2_mol = np.empty((0, zlid.shape[1]))
    trayleigh = np.empty((0, zlid.shape[1]))

    # calcul de la resolution du lidar a partir des bornes

    range_resol = np.diff( (range_gate[:,1]+range_gate[:,0])/2. )
    range_resol = np.append ( range_resol, range_resol[-1] )

    nl = len(zlid[0,:])

    CtoK = auto_tempe_unit( Tz )  

    # on inverse les tableaux car pour np.interp()
    # il faut que z soit croissant 
    if np.nanmean(z[:,-1] - z[:,0]) <0  :
        z = np.fliplr(z) 
        Tz = np.fliplr(Tz) 
        Pz = np.fliplr(Pz) 

    # on boucle sur le temps 
    for zlid_i, z_i,Tz_i, Pz_i in zip(zlid, z, Tz, Pz) :  
        try : 
            T_inter = np.interp ( zlid_i , z_i, Tz_i, left=np.nan, right=np.nan)
            P_inter = np.interp ( zlid_i , z_i, Pz_i, left=np.nan, right=np.nan)
    
            N_m =  (P_inter*100.)/(8.314/(6.023e+23)*(T_inter + CtoK))
            section_m = 5.45*(550./float(lambda0))**4.09*1e-32

            bmol_i =  N_m*section_m
            amol_i = 8.0*np.pi*bmol_i/3.0
        
            trayleigh_i=np.exp(-2*np.cumsum(amol_i*range_resol))
            pr2_mol_i =bmol_i*trayleigh_i
        except ValueError :
            amol_i = np.full( nl, np.nan)
            bmol_i = np.full( nl, np.nan)
            trayleigh_i = np.full( nl, np.nan)
            pr2_mol_i = np.full( nl, np.nan)

        amol = np.vstack( (amol, amol_i))
        bmol = np.vstack( (bmol, bmol_i) )
        trayleigh = np.vstack((trayleigh, trayleigh_i) ) 
        pr2_mol = np.vstack( (pr2_mol, pr2_mol_i) )

    return amol, bmol, trayleigh, pr2_mol

  




