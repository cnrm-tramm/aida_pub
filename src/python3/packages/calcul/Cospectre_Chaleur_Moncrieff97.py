#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def Cospectre_Chaleur_Moncrieff97 (nfreq, z, d, L, u_moy ):
    """
    Compute analytic heat cospectrum by Moncrieff 97

    In :
        nfreq : number of frequency of cospectrum
        z : measurement height
        d : displacement height
        L : Monin-Obhukov length
        u_moy : wind speed

    Out :
        nf : frequency of cospectrum
        cospectrum : Heat cospectrum 

    @ CNRM/GMEI/TRAMM - June 2020

    sources :
    Moncrieff and al 1997
    EddyPro : bpcf_cospectral_models.f90

    """

    nseconds = 7200.
    nf=np.empty(int(nfreq))

    nf[0] = 1/nseconds
    for i in range (1, int(nfreq)) : 
        nf[i] = np.exp(np.log(nf[0]) + (np.log(10.)-np.log(nf[0]))/float(nfreq) * float(i+1))

    cospectrum=np.empty((0, len(nf)))

    for L_i, u_moy_i in zip (L, u_moy):

        kf = nf* np.abs((z - d) / u_moy_i)
        zL = (z - d)/L_i
        cosp_i = np.empty(len(nf))

        if(zL > 0.) :
        # conditions stables
        #Scalar fluxes (T, CO2, H2O)
            Ac = 0.284 * ((1. + 6.4 * zL)**0.75)
            Bc = 2.34 * (Ac**(-1.1))
            cosp_i = kf / (nf * (Ac + Bc * kf**2.1) )
        else :
        #unstable conditions
        #Scalar fluxes (T, CO2, H2O)
            idx1 = kf < 0.54
            cosp_i[idx1] = 12.92 * kf[idx1] / (nf[idx1] * (1. + 26.7 * kf[idx1])**1.375)

            idx2 = np.logical_not(idx1) 
            cosp_i[idx2] = 4.378 * kf[idx2] / (nf[idx2] * (1. + 3.8 * kf[idx2])**2.4)

        cospectrum = np.vstack((cospectrum, cosp_i))

    return (nf, cospectrum)


