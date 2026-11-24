#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" 

Filtrage_spectral.py : Fonction de filtrage des fréquences pour le traitement
                       des données du lidar Cimel.
                       Cette fonction est appelées par un opérateur Aida écrit
                       en langage C.

   Input argumentstest_oper_csv.py
   ---------------
  
        - pr2: the Pr2 signal from the LIDAR remote sensing
        - A varie entre 0 et 1. est correspond au % des frequences filtrées.
          (0 correspond a aucun filtrage).
  
   Output argument
   ---------------
  
        - X_f : signal filtré
  
   Auteur 
   ------
        - CNRM/GMEI:TRAMM  P. Richard Fevrier 2018 a partir d'un script
                 scilab ecrit par le LOA.
"""

import sys
import os
import numpy as np

PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))
import AIDA


def Filtre_spectral_1D(PrB, A, str_bornes, zmin, extrap_typ) :
    """ 
        pr2: the Pr2 signal from the LIDAR remote sensing
        A varie entre 0 et 1. est correspond au % des frequences filtrées.
          (0 correspond a aucun filtrage.)
    """ 


    X_f=np.copy(PrB)

    # lorsque dans le .fil A = 0.7 et que la fonction de calcul est lancée par
    # FVB, ici A = 0.699999988079071 ce qui engendre des différences entre FVB
    # et ADC...
    # la bidouille suivante permet de retrouver A = 0.7
    A = round(A, 2)



    power=np.floor(np.log10(np.nanmean(PrB[:,100:150])))
    ###print(power)

# pour chaque temps :
    for nc in np.arange(len(PrB)) :
        Pr = PrB[nc,:]

# limitation de la puissance de 10
#        power=np.floor(np.log10(np.nanmean(Pr[100:150])))
        Pr=Pr*np.power(10., -float(power) +1 )

        xPr = np.copy(Pr)

#on s'assure que le nb d'altitude est pair
#sinon on en ajoute une.

        if len(Pr)/2. != np.floor((len(Pr)/2)+0.5) :
            Pr = np.append(Pr,Pr[-1])

#transformation directe
        TFX = np.fft.fft(Pr)

# on modifie le signal pour que les plus basses fréquences soient au milieu
        dim = len(TFX)
        FFT=[]
        FFT[0:int(dim/2)]=TFX[int(dim/2):dim]
        FFT[int(dim/2):dim]=TFX[0:int(dim/2)]

        larg = np.floor( 0.5 + ( A * len(Pr)/2) )
        larg = len(Pr)/2 -larg 
    
# une gaussienne
        MU = len(TFX)/2 
        STDEV = larg/2
        absc = np.arange(0, len(TFX))
        gauss = []


        gauss=np.exp(-((absc-MU)/(np.sqrt(2)*STDEV))**2)


#On multiplie la fft par la gaussienne
        FFT_gauss=FFT*gauss;

#On remet a l'endroit le spectre
        TF_gauss=[]
        TF_gauss[0:int(dim/2)]=FFT_gauss[int(dim/2):dim]
        TF_gauss[int(dim/2):dim]=FFT_gauss[0:int(dim/2)]


#On fait la transformation inverse
        X_tmp=np.fft.ifft(TF_gauss)
        X_f[nc,1:]=np.real(X_tmp[0:len(xPr)-1]);

#Extrapolation

    PR_tmp = []
    PR2_calc = []
    PR2_calc = np.empty(X_f.shape)

# Récupération des bornes
    z = np.array(AIDA.strBornes_to_array(str_bornes))[:,:,0][0]
    porte = z[2] - z[1]
    imin = np.argmin(abs(z - zmin))

    for nc in np.arange(len(X_f)) :

        if extrap_typ=="cst" :
            low=np.ones((1,imin))*X_f[nc,imin+1];
            PR2_calc[nc,:]=X_f[nc,:]
            PR2_calc[nc,0:imin]=low

        if extrap_typ=="lin" : 
            slope = porte/(X_f[nc,imin+1]-X_f[nc,imin])
            origin = (imin+1*porte)-(X_f[nc,imin]*slope)+((imin-1)*porte)  #On sait que le point de coo imin+1 appartient à la droit
            PR_tmp = (z[0:imin]+porte-origin)/slope
            PR2_calc[nc,:]=X_f[nc,:]
            PR2_calc[nc,0:imin]=PR_tmp

    return PR2_calc

