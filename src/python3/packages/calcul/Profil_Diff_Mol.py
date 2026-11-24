#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 
"""

import numpy as np

def Profil_Diff_Mol(range_gate, z,T0,P0,lambda0) :
    """ 
      Process Extinction and Backscatter coefficient for a standard molecular atmosphere
      
      Input :
         range_gate : array of gate range of lidar  (array with N line and 2 colums for min and max range) 
         z : Range vector
         T0 : Temperature at sea level (K)
         P0 : Pressure at sea level (hPa)
         lambda : Wavelength (nm)

      Output : 
        amol : coefficient d'extinction
        bmol : coefficient de retrodiffusion
        trayleigh : coefficient rayleigh 
        pr2_mol : signal moleculaire retroduiffuse

      Auteur :  CNRM/GMEI/TRAMM février 2018
                transcode de scilab en Python a partir de la filiere BASIC du LOA 
                fonction scilab originale : Std_Atm.sci
    """ 


    #standart gradients & parameters
    dTdz_tropo = -6.5
    dTdz_strato = 1.4
    dTdz_meso = -2.4
    z_tpause = 13.
    z_spause = 55.
    p_He = 8.
    Tz = np.empty(z.shape[1])
    Pz = np.empty(z.shape[1])
    bmol = np.empty((0, z.shape[1]))
    amol = np.empty((0, z.shape[1]))
    pr2_mol = np.empty((0, z.shape[1]))
    trayleigh = np.empty((0, z.shape[1]))

    # calcul de la resolution du lidar a partir des bornes

    range_resol = np.diff( (range_gate[:,1]+range_gate[:,0])/2. )
    range_resol = np.append ( range_resol, range_resol[-1] )

    nl = len(z[0,:])

    # on boucle sur le temps 
    for z_i in z :  
        try : 
            z_i = z_i/1000.
            n_tpause = int( np.floor(0.5+(np.interp(z_tpause,z_i[0:-1],np.arange(1,nl))) ) )
            n_spause = int( np.floor(0.5+(np.interp(z_spause,z_i[0:-1],np.arange(1,nl))) ) )
            Tz[0:n_tpause] = T0 + dTdz_tropo*z_i[0:n_tpause]
            Tz[n_tpause:n_spause] = T0 + dTdz_tropo*z_i[n_tpause] + dTdz_strato*(z_i[n_tpause:n_spause] - z_i[n_tpause])
            Tz[n_spause:nl] = T0 + dTdz_tropo*z_i[n_tpause] + dTdz_strato*(z_i[n_spause] - z_i[n_tpause]) + dTdz_meso*(z_i[n_spause:]-z_i[n_spause])
            Pz = (100.*P0*np.exp(-z_i /p_He))
    
            N_m =  Pz/(8.314/(6.023e+23)*Tz)
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

  




