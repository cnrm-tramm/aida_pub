#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def Cospectre_Mouvement_Moncrieff97 (nfreq, z, d, L, u_moy ):
    """
    Compute analytic of wu cospectrum by Moncrieff 97

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
            Ac = 0.124 * ((1. + 7.9 * zL)**0.75)
            Bc = 2.34 * (Ac**(-1.1))
            cosp_i = kf / (nf * (Ac + Bc * kf**2.1) )
        else :
        #unstable conditions
            idx1 = kf < 0.24
            cosp_i[idx1] = 20.78 * kf[idx1] / (nf[idx1] * (1. + 31.0 * kf[idx1])**1.575)

            idx2 = np.logical_not(idx1) 
            cosp_i[idx2] = 12.66 * kf[idx2] / (nf[idx2] * (1. + 9.6 * kf[idx2])**2.4)

        cospectrum = np.vstack((cospectrum, cosp_i))

    return (nf, cospectrum)


