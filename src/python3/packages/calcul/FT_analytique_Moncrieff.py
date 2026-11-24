#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np

def FT_analytique_Moncrieff ( nfreq, hp_lp, fe, tint, type1, type2, hsep, vsep, type_hp, tauf, u_moy ) :
    """
    Compute analytic transfert function of the eddy-covariance measuremnt system

    In :
        nfreq : number of frequency for transfert function 
        hp_lp : type analaytic FT ( 'HP': high-pass only, 'LP' : low-pass only, 'HPLP' : high-pass and low-pass ) 
        fe : sample frequency (Hz)
        tint : integration duration (s)
        type 1 : type of instrument 1
        type 2 : type of instrument 2
        hsep : horizontal separation between instruments 1 and 2 (m)
        vsep : vertical separation between instruments 1 and 2 (m)
        type_hp : type of fluctuation computing method ( 'ba': block average, 'rm' : moyenne glissante )
        tauf : time constant of running-mean  
        u_moy : wind speed 

    Out :
        nf : frequency 
        TF : Tranfert function

    @ CNRM/GMEI/TRAMM - June 2020
    Moncrieff an al 2004
    Moncrieff an al 1997
    EddyPro : bpcf_moncrieff_97.f90
    """

    nseconds = 7200.

    nf=np.empty(int(nfreq))

    nf[0] = 1/nseconds

    for i in range (1, int(nfreq)) : 
        nf[i] = np.exp(np.log(nf[0]) + (np.log(10.)-np.log(nf[0]))/float(nfreq) * float(i+1))

    TF = np.empty((0, len(nf)) )

    s = hp_lp.strip().upper()

    if s == 'HP' :
        # fonction de transfert passe-haut (HP) uniquement Moncrieff 2004
        for u_moy_i in  u_moy: 
            TF_HP = FT_analytique_HP_Moncrieff_2004 (nf, fe, tint, tauf, type_hp)  
            TF_i = TF_HP * TF_HP
            TF = np.vstack((TF, TF_i))

    elif s == 'LP':
        # fonction de transfert passe-bas (LP) uniquement Moncrieff 1997 
        for u_moy_i in  u_moy: 
            TF_LP = FT_instru_LP_Moncrieff_97 (nf, type1, type2, u_moy_i, vsep, hsep) 
            TF_i = TF_LP
            TF = np.vstack((TF, TF_i))

    elif s == 'HPLP':
        # fonction de transfert passe-bas (LP) et passe-haut (HP) 
        for u_moy_i in  u_moy: 
            TF_HP = FT_analytique_HP_Moncrieff_2004 (nf, fe, tint, tauf, type_hp)  
            TF_LP = FT_instru_LP_Moncrieff_97 (nf, type1, type2, u_moy_i, vsep, hsep) 
            TF_i = TF_LP * TF_HP * TF_HP
            TF = np.vstack((TF, TF_i))
    else :
        # inconnu
        raise ValueError ('+++ : ERREUR {} type de fonction de transfert inconnu.'.format(hp_lp))

    return (nf, TF)


def  FT_analytique_HP_Moncrieff_2004 (nf, fe, tint, tauf, type) :
    """
    Determine la fonction de transfert analytique en fonction
    de la méthode de détermination des fluctuations 
    ( moyenne, tendance linéaire, filtrage passe-haut)

    fe : fréquence d'échantillonnage
    tint : temps d'intégration
    type : type de filtrage (ba, ld, rm )
    """

    dt = 1. / fe
    total_time = tint

    FT = np.empty(len(nf))

    t = type.strip().lower()

    if t == 'ba' :
        phase = np.pi * nf * total_time
        FT = 1. - np.sin(phase)**2 / phase**2
    elif t == 'rm' :
        #For the definition of eta and tau (a and t_d) see Geissler & Ibrom 2008
        eta = np.exp(-dt / tauf)
        tau = eta / (fe* (1. - eta))
        phase = 2.* np.pi * nf * tau
        FT = phase**2 / (1. + phase**2 / eta)
    else :
        FT = np.full(len(nf), np.nan ) 
        raise ValueError ( '+++ ERREUR : type de filtrage {} inconnu'.format(type) )

    return (FT) 

def FT_instru_LP_Moncrieff_97 (nf, type1, type2, u_moy, vsep, hsep) :
    """
    Determine la fonction de transfert analytique du 
    système de mesure en fonction de la configuration instrumentale
    """
    # caractéristiques des capteurs (source EddyPro : retrieve_sensor_params.f90 )

    param_sonic = { 
        'hs_50':{   'vpath_length' : 0.125, 
                    'hpath_length' : 0.110, 
                    'tau': 1. / 50.}, 
        'hs_100':{
            'vpath_length': 0.125,
            'hpath_length': 0.110,
            'tau': 1./ 100},
        'r2':{ 
            'vpath_length': 0.125,
            'hpath_length': 0.110,
            'tau': 1./ 50. },
        'r3_50':{
            'vpath_length': 0.125,
            'hpath_length': 0.110,
            'tau': 1. / 50 },
        'r3_100':{
            'vpath_length': 0.125,
            'hpath_length': 0.110,
            'tau': 1./ 100},
        'r3a_100':{
            'vpath_length': 0.125,
            'hpath_length': 0.110,
            'tau': 1./ 100} ,
        'wm':{
            'vpath_length': 0.125,
            'hpath_length': 0.110,
            'tau': 1./32},
        'wmpro':{
            'vpath_length': 0.125,
            'hpath_length': 0.110,
            'tau ': 1./ 40},
        'usoni3_cage_mp':{
            'vpath_length': 0.131,    
            'hpath_length': 0.099,    
            'tau ': 1./ 30},
        'usoni3_classa_mp':{
            'vpath_length': 0.131,    
            'hpath_length': 0.099,    
            'tau': 1./ 30},
        'usa1_standard':{
            'vpath_length': 0.131,    #to be verified
            'hpath_length': 0.099,    #to be verified
            'tau': 1./25},
        'usa1_fast':{
            'vpath_length': 0.131,    #to be verified
            'hpath_length': 0.099,    #to be verified
            'tau': 1./50},
        'csat3':{ 
            'vpath_length': 0.115,
            'hpath_length': 0.058,
            'tau': 1./ 60},
        'csat3b':{ 
            'vpath_length': 0.115,
            'hpath_length': 0.058,
            'tau': 1./ 60},
        '81000': {                   # memes caractersitiques pou 81000v, 81000re, 81000vre
            'vpath_length ': 0.150,
            'tau': 1./40 }
        }

    param_irga = { 
                'li7500':{
                    'vpath_length': 0.127,
                    'hpath_length': 0.0095,
                    'tau': 0.1},
                'li7500a': { # memes caracteristiques pour li7500rs,li7500ds
                     'vpath_length': 0.127,
                     'hpath_length': 0.0095,
                     'tau': 0.1},
                'li7200' : {  # memes caracteristiques pour li7200rs
                    'vpath_length': 0.127,
                    'hpath_length': 0.0127,
                    'tau': 0.1 }, 
                'li7700': {
                    'vpath_length': 0.50,
                    'hpath_length': 0.0635,
                    'tau': 0.1 }, 
                'li6262': {
                    'vpath_length': 0.152,
                    'hpath_length': 0.013,
                    'tau': 0.1 }, 
                'li7000': {
                    'vpath_length': 0.152,
                    'hpath_length': 0.0095,
                    'tau' : 0.1 }, 
                    }


    TF_1 = fonction_TF (type1, param_sonic, param_irga, nf, u_moy, vsep, hsep) 
    TF_2 = fonction_TF (type2, param_sonic, param_irga, nf, u_moy, vsep, hsep) 


    return ( TF_1 * TF_2 )

def fonction_TF (type, param_sonic, param_irga, nf, u_moy, vsep, hsep) :  
    """
    Calcule la fonction de transfert en fonction de type
    """

    t = type.strip().lower()

    if t in  param_sonic.keys() :
        TF = TF_sonic(  nf, param_sonic[type], u_moy ) 
    elif t in param_irga.keys() :
        TF = TF_open_irga ( nf, param_irga[type], u_moy, vsep, hsep )
    else :
        TF = np.full(len(nf), np.nan ) 
        raise ValueError (  '+++ ERREUR : type de capteur {} inconnu'.format(type) )
    return TF

    
def TF_sonic ( nf, param_sonic, u_moy ) :
    """
    Calcule la fonction de transfert pour un parametre du sonique

    source : EDDYPRO fonction AnalyticLowPassTransferFunction
    """

    TF = np.empty(len(nf))

    sonic_freq = 1./ param_sonic['tau']
    fp_sonic =  nf * np.abs(param_sonic['vpath_length'] / u_moy)
    #sonic dynamic frequency response
    dsonic = 1. / np.sqrt(1. + (2. * np.pi * nf / sonic_freq)**2 )
    #sonic path-averaging
    wsonic = (2.0 / (np.pi * fp_sonic)) * (1. + np.exp(-2. * np.pi * fp_sonic) / 2. 
                    - 3.*(1. - np.exp(-2.0 * np.pi * fp_sonic)) / (4. * np.pi * fp_sonic))

    TF= dsonic*wsonic
    return (TF) 

def TF_open_irga ( nf, param_irga, u_moy, vsep, hsep ) :
    """
    Calcul de la fonction de transfert pour un parametre venant de l'IRGA
    
    source : EDDYPRO fonction AnalyticLowPassTransferFunction
    """

    TF = np.empty(len(nf))

    irga_freq = 1. / param_irga['tau']
    fp_irga = nf * np.abs(param_irga['vpath_length'] / u_moy)
    fs_ver  = nf * np.abs(vsep / u_moy)
    fs_lat  = nf * np.abs(hsep / u_moy)

    #irga dynamic frequency response
    dirga  = 1.0 / np.sqrt(1.0 + (2.0 * np.pi * nf /  irga_freq)**2 )
    # irga path-averaging
    wirga =  np.sqrt((3. + np.exp(-2.*np.pi*fp_irga) - 4./(2.*np.pi*fp_irga) * 
                    (1. - np.exp(-2.*np.pi*fp_irga))) / (2.*np.pi*fp_irga) )

    #irga separations (vertical and horizontal)
    sver = np.exp(-9.9*fs_ver**1.5)
    shor = np.exp(-9.9*fs_lat**1.5)

    TF = wirga*dirga*sver*shor

    return (TF) 












