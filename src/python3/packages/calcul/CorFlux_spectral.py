#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def CorFlux_spectral ( freq, cospectre, fonction_transfert, flux ) :
    """
    Compute spectral correction and corrected flux
    with cospectra and transfer function of the measurements system
   
    In :
        freq : frequency of cospectrum
        cospectre : ideal cospectrum
        fonction_transfert : transfer function of the measurement system
        flux : flux to be corrected

    Out :
        flux_cor : corrected flux
        cor_spectrale : spectral correction

    @ CNRM/GMEI/TRAMM - June 2020
    """

    # nf est un tableau de bornes (nfreq x 2)
    # on calcule la moyenne

    nf = (freq[:,0]+ freq[:,1])/2.

    # plage min et max de la partie du cospectre à integrer
    nf_min = 1./5000.
    nf_max = 100.

    cor_spectrale = np.empty(0)
    flux_cor = np.empty(0)

    id = np.logical_and (nf > nf_min, nf < nf_max)
    d_nf = np.diff(nf[id]) 

    for cosp_i, TF_i in zip (cospectre, fonction_transfert) :
        IntCO = 0.
        IntTFCO = 0.

        #Integration du cospectre et du cospectre filtré 
        IntCO = np.nansum ( cosp_i[id][0:-1]*d_nf ) 
        IntTFCO = np.nansum ( TF_i[id][0:-1]*cosp_i[id][0:-1]*d_nf )

        cor_spectrale_i =  IntCO/IntTFCO

        cor_spectrale = np.append( cor_spectrale, cor_spectrale_i )

    flux_cor = flux * cor_spectrale 

    return ( flux_cor, cor_spectrale )

