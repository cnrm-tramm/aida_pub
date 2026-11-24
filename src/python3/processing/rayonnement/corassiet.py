#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 15 08:53:50 2017

@author: bouchara
"""



import numpy as np
import sys
import os

def possol(JQUANT,HD,XLON,XLAT):

    FAC  = np.pi/180.0
    PI2  = 2.0*np.pi
    A0   = -0.000075
    A1   = -0.001868
    A2   = 0.032077 
    A3   = 0.014615 
    A4   = 0.040849 
    B0   = 0.006918 
    B1   = -0.399912 
    B2   = 0.070257 
    B3   = -0.006758 
    B4   = 0.000907
    B5   = -0.002697
    B6   = 0.001480
    XJ   = np.float(JQUANT)
    TET  = 2.0*np.pi*(XJ-1.0)/365.0
    CT   = np.cos(TET)
    ST   = np.sin(TET)
    C2T  = np.cos(2*TET)
    S2T  = np.sin(2*TET)
    C3T  = np.cos(3*TET)
    S3T  = np.sin(3*TET)
    XLA  = XLAT*FAC
    TSM  = HD+XLON/15.0
    ET   = A0+A1*CT+A2*ST+A3*C2T+A4*S2T
    ET   = ET*12.0*60.0/np.pi
    TSV  = TSM-ET/60.0
    AH   = TSV-12.0
    AH   = AH*15.0*FAC
    
    DELTA   = B0+B1*CT+B2*ST+B3*C2T+B4*S2T+B5*C3T+B6*S3T
    AMUZERO = np.sin(XLA)*np.sin(DELTA)+np.cos(XLA)*np.cos(DELTA)*np.cos(AH)
    ELEV    = np.arcsin(AMUZERO)
    AZ      = np.cos(DELTA)*np.sin(AH)/np.cos(ELEV)
    
    for i in range(np.size(AZ)):
        if (AZ[i]>1.0):
            AZ[i]=1.0
        if (AZ[i]<-1.0):
            AZ[i]=-1.0
    CAZ  = -np.cos(XLA)*np.sin(DELTA)+np.sin(XLA)*np.cos(DELTA)*np.cos(AH)
    CAZ  = CAZ/np.cos(ELEV)
    AZIM = np.arcsin(AZ)
    
    for i in range(np.size(CAZ)):
        if (CAZ[i]<0):
            AZIM[i]=np.pi-AZIM[i]
        if ((CAZ[i]>0) and(AZ[i]<0)):
            AZIM[i]=2.0*np.pi+AZIM[i]
    AZIM=AZIM+np.pi
    
    for i in range(np.size(AZIM)):
        if (AZIM[i]>PI2):
            AZIM[i]=AZIM[i]-PI2
    THETA0=90.0-ELEV/FAC
    PHI0=AZIM/FAC
    
    return THETA0,PHI0,AMUZERO

def corrassiet(JQUANT,TU,XLON,XLAT,CAP,ROLL,PITCH,OFROL,OFTAG,SWDOWNbrut):
    
    """
    ROLL            angle de gite, ou roulis(degres)
    PITCH           assiette longitudinale, ou tangage
    OFROL           decalage entre le roulis de l'instrument et celui de la plateforme(degres)
    OFTAG           decalage entre le tangage de l'instrumentet celui de la plate_forme(degres)
    SWDOWNbrut      flux global incident brut(Watt par metres carres)
    CAP             Azimut(ou cap)de la plate_forme de mesure(degres)  
    TU              temps universel(secondes)
    JQUANT          jour de l'année   
    XLON            longitude
    XLAT            latitude
    """
    THETA0,PHI0,AMUZERO=possol(JQUANT,TU,XLON,XLAT)
    
#C-----------------------------------------
#C TEMPS SOLAIRE MOYEN (HEURE DECIMALE)
#      TSM = HD + XLON/15.0D+00
#C-----------------------------------------
    
    OFROL = np.tan(OFROL*np.pi/180.0)    
    OFTAG = np.tan(OFTAG*np.pi/180.0)
    HD    = TU/3600.0
    for i in range(np.size(CAP)):    
        if float(CAP[i]) < 0.0 :
            CAP[i]=CAP[i]+360.0
    
    THETA0,PHI0,AMUZERO = possol(JQUANT,HD,XLON,XLAT)
    H0   = (90.0-THETA0)*np.pi/180.0
    R    = ROLL*np.pi/180.0
    P    = PITCH*np.pi/180.0
    DELP = (PHI0-CAP)*np.pi/180.0
    DSIR = np.sin(R)
    DCOR = np.cos(R)
    DSIP = np.sin(P)
    DCOP = np.cos(P)
    DSIA = np.sin(DELP)
    DCOA = np.cos(DELP)
    DTAH = np.tan(H0)
    DC0  = DSIR*DSIA-DCOR*DCOA*DSIP    
    X0   = DC0/DTAH+DCOR*DCOP
    DC1  = -DCOR*DSIA+DSIR*DCOA*DSIP
    X1   = DC1/DTAH+DSIR*DCOP     
    DC2  = DCOP*DCOA
    X2   = DC2/DTAH+DSIP
    XN   = X0+OFROL*X1-OFTAG*X2
    XN   = XN/np.sqrt(1.0+OFROL*OFROL+OFTAG*OFTAG)
    
    C    = AMUZERO
    Xas  = np.longdouble(1.0-(3.9-12.5*C+17.5*(C**2)-8.9*(C**3))/100.0)

    SWDOWNcorrige=np.longdouble(SWDOWNbrut/(XN*Xas))

    return XN,Xas,SWDOWNbrut,SWDOWNcorrige
