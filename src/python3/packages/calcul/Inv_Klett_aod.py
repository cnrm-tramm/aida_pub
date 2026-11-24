#!/usr/bin/env python3

import numpy as np

def Inv_Klett_aod(X,range_gate, Z, beta_mol, flg_cloud, AOD_photo,altitude_max,dist_min, beta_a_init, extrap_typ) :
    """
    Klett Inversion Constrained by AOD 

    Input :
        X : backscatter lidar signal
        range_gate : array of gate range of lidar  (array with N line and 2 colums for min and max range) 
        Z : altitude of lidar measurements
        beta_mol : Molecular diffusion
        flg_cld : Cloud flag (0 : no cloud, !=0 : altitude of cloud )
        AOD_photo : Aerosol optical depth
        altitude_max : max ref altitude 
        dist_min : minimal distance from lidar of signal use  
        beta_a_init : valeur initiale de Beta
        extrap_typ : type extrapolation proche du lidar 'cst' or 'lin'

    Output :
        Sigma : Aerosol extinction coefficient (profil 1D) 
        Beta : Aerosol backscatterring coefficient (profil 1D)
        SA   : Lidar ratio. 

    
    
    Auteur :  CNRM/GMEI/TRAMM juillet 2019
                transcodage Python a partir de la filiere BASIC du LOA en Scilab
                fonction scilab originale : Inv_Klett_aod.sci

    """

    # calcul de la resolution du lidar a partir des bornes

    range_resol = np.diff( (range_gate[:,1]+range_gate[:,0])/2. )
    range_resol = np.append ( range_resol, range_resol[-1] )


    #Moleculaire a lire dans le programme avant
    Smol=8*np.pi/3.


    beta_aer = np.empty((0, X.shape[1]))
    sigma_aer = np.empty((0, X.shape[1]))
    SA = np.empty(0)
    BETA=np.zeros(X.shape[1])
    beta_aer_i=np.zeros(X.shape[1])
    sigma_aer_i=np.zeros(X.shape[1])

    for x_i, z_i, alt_max_i, flg_cloud_i, beta_mol_i, aod_photo_i in zip( X, Z, altitude_max, flg_cloud, beta_mol, AOD_photo ) :

        if ( flg_cloud_i > 0 and flg_cloud_i <= alt_max_i) or np.isnan(aod_photo_i) or np.isnan(alt_max_i)  :

            beta_aer = np.vstack((beta_aer, np.full(z_i.shape, np.nan) ))
            sigma_aer = np.vstack((sigma_aer, np.full(z_i.shape, np.nan) ))
            SA = np.append (SA, np.nan )
            continue

        Nref= np.argmin ( np.abs( z_i - alt_max_i) ) + 1 

        int1 = np.empty(Nref)    
        int2 = np.empty(Nref)    
        PHI = np.empty(Nref)    
        BETA[:]= 0.
        beta_aer_i[:] = 0.
        sigma_aer_i[:] = 0.

        BETA[Nref-1]=beta_mol_i[Nref-1]*1+beta_a_init

        Sa_min=1
        Sa_max=150

        while np.abs(Sa_max-Sa_min)>0.1 :
    
            Sa=abs(Sa_max+Sa_min)/2
    
            # la fonction numpy.nancumsum n'existe pas dans la version du
            # package nmupy que nous avons. On fait a la main.
            #int1[0:Nref]=np.nancumsum((Saer_OK-Smol)*beta_mol_i[0:Nref]*range_resol[0:Nref])
            for i in range(len(int1)) :
                int1[i] = np.nansum( (Sa-Smol)*beta_mol_i[0:i+1]*range_resol[0:i+1])
            int1 =2*int1[-1]-2*int1

            PHI=np.log(x_i[0:Nref]/x_i[Nref-1]) + int1[0:Nref]
        
            for i in range(len(int2)) :
                int2[i]=2.*np.nansum(Sa*np.exp(PHI[0:i+1])*range_resol[0:i+1])
            int2[0:Nref]=int2[-1]-int2[0:Nref]

            BETA[0:Nref-1]=(np.exp(PHI[0:Nref-1]))/((1/BETA[Nref-1])+int2[0:Nref-1])
        
            beta_aer_i[0:Nref]=BETA[0:Nref]-beta_mol_i[0:Nref]

            if extrap_typ=='cst' :
                imin =  np.argmin( np.abs(range_gate[:,1] - dist_min)) + 1 
                beta_aer_i[0:imin]=beta_aer_i[imin]*np.ones(beta_aer_i[0:imin].shape )


            sigma_aer_i=Sa*beta_aer_i
            beta_aer_i=np.real(beta_aer_i)
            sigma_aer_i=np.real(sigma_aer_i)
        
            #Calcul de l'AOD du profil
            AOD_i=np.nansum(sigma_aer_i * range_resol)
        
            #print('Sa :', Sa, ' AOD_i :',  AOD_i, 'aod_photo_i :', aod_photo_i  )
            if AOD_i>aod_photo_i :
                Sa_max=Sa
            if AOD_i<aod_photo_i : 
                Sa_min=Sa

            if np.isnan(AOD_i) :
                Sa_min=1
                Sa_max=1
                Sa=0

            if np.isinf(abs(AOD_i)) :
                Sa_min=1
                Sa_max=1
                Sa=0
    
        #Inversion avec le bon Saer

        Saer_OK = Sa
        #print ("Sa : ", Saer_OK, "AOD : ", AOD_i, 'AOD photo :', aod_photo_i)
        for i in range(len(int1)) :
            int1[i] = np.nansum( (Saer_OK-Smol)*beta_mol_i[0:i+1]*range_resol[0:i+1])

        int1=2*int1[-1]-2*int1

        PHI =(np.log(x_i[0:Nref]/x_i[Nref-1]) + int1)
        for i in range(len(int2)) :
            int2[i]=2.*np.nansum(Saer_OK*np.exp(PHI[0:i+1])*range_resol[0:i+1])

        int2=int2[-1]-int2

        BETA[0:Nref-1] =(np.exp(PHI[0:Nref-1]))/((1./BETA[Nref-1])+int2[0:Nref-1])

        beta_aer_i[0:Nref]=BETA[0:Nref]-beta_mol_i[0:Nref]
        if extrap_typ=='cst' :
            imin =  np.argmin( np.abs(range_gate[:,1] - dist_min)) + 1 
            beta_aer_i[0:imin]=beta_aer_i[imin]*np.ones(beta_aer_i[0:imin].shape )


        beta_aer= np.vstack((beta_aer, beta_aer_i))
        sigma_aer_i=Saer_OK*beta_aer_i
        sigma_aer = np.vstack((sigma_aer, sigma_aer_i))
        SA = np.append( SA, Saer_OK)
        

    return sigma_aer, beta_aer, SA 

