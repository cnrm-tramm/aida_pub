#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 12:06:59 2017

@author: bouchara
"""
import numpy as np
import sys
import os

import matplotlib.pyplot as plt
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))
import AIDA


import corassiet as ps
import matplotlib as mpl



def lecture_donnees(nom_vol):
    time_1 = AIDA.Vector(nom_vol,'rft_TIME_1').data
    lati_1 = AIDA.Vector(nom_vol,'pos_lat_aipov_1').data
    long_1 = AIDA.Vector(nom_vol,'pos_lon_aipov_1').data
    alti_1 = AIDA.Vector(nom_vol,'alt_aipov_1').data
    capgeo_1=AIDA.Vector(nom_vol,'att_capgeo_aipov_1').data
    roll_1 = AIDA.Vector(nom_vol,'att_roul_aipov_1').data
    pitch_1 = AIDA.Vector(nom_vol,'att_tang_aipov_1').data
    swdown_1 = AIDA.Vector(nom_vol,'ray_glob_h_sync_1').data

    return time_1,lati_1,long_1,alti_1 ,capgeo_1,roll_1,pitch_1,swdown_1

    
if __name__=="__main__":
    
    plt.close('all')

    argv = sys.argv[1:]
    argc = len(argv)

    if argc != 5:       # test et validation
        print("ATTENTION : il faut 5 arguments acqid palier_droite palier_gauche palier_face palier_dos")
        sys.exit(1)

    acqid = argv[0]
    pal_d = argv[1]
    pal_g = argv[2]
    pal_f = argv[3]
    pal_a = argv[4]

    print(acqid, pal_d, pal_g, pal_f, pal_a)

    acq_meta = AIDA.Inf(acqid)
    for (typ, seq) in acq_meta.iter_items_str('SEQUENCES') :
        champs = seq.split('/')
        if champs[0] in (pal_d, pal_g, pal_f, pal_a) :
                deb = champs[1]
                hd = int(deb[0:2])
                md = int(deb[2:4])
                sd = int(deb[4:6])
                fin =  champs[2]
                hf = int(fin[0:2])
                mf = int(fin[2:4])
                sf = int(fin[4:6])
                XSeqMin = int(hd*3600+md*60+sd)
                XSeqMax = int(hf*3600+mf*60+sf)
                if champs[0] == pal_d :
                    droite=[XSeqMin, XSeqMax]
                if champs[0] == pal_g :
                    gauche=[XSeqMin, XSeqMax]
                if champs[0] == pal_f :
                    face=[XSeqMin, XSeqMax]
                if champs[0] == pal_a :
                    dos=[XSeqMin, XSeqMax]

    print(face, dos, droite, gauche)

    segments2=[face,dos]
    segments1=[droite,gauche]

    print("=========================")
    print("nom_vol:",acqid)
    print("=========================")
    acq_meta = AIDA.Inf(acqid)
    ab= acq_meta.get_date_acq()

    numjour=float(ab.strftime("%j"))

    timei,lati,longi,alti ,cap_geo,roll,pitch,swdown_0=lecture_donnees(acqid)
    pos_theta_0_i=roll
    pos_phi_0_i=pitch
    mpl_fig = plt.figure()
    ax = mpl_fig.add_subplot(211)

    couleur=["red","blue"]
   
    OFTAG=[0.0]
    OFROL=np.arange(-3.0,3.0,0.5)
    lofr=len(OFROL)

    lrl=[]
    sdl=[]
        
    theta_0,phi_0,amu_zero=ps.possol(numjour,timei/3600.0,longi,lati)
    segments=segments1   
    for segment in segments:

        mini=segment[0]
        maxi=segment[1]
        minimum=min([j for j in range(len(timei)) if timei[j]>mini])
        maximum=max([j for j in range(len(timei)) if timei[j]<maxi])

        print(segment)
        resultat_theta=np.mean(theta_0[minimum:maximum])
        print("THETA", resultat_theta)
        resultat_phi=np.nanmean(phi_0[minimum:maximum])
        print("PHI", resultat_phi)
        resultat_cap=np.nanmean(cap_geo[minimum:maximum])
        print("CAP", resultat_cap)
    
        for ofrol in OFROL:
            for oftag in OFTAG:
                Xna_0,Xasa,SWD_0,SWD_c=ps.corrassiet(numjour,timei,longi,lati,cap_geo,roll,pitch,ofrol,oftag,swdown_0)

                SWD_c1= SWD_c[minimum:maximum]
                SWD_01=SWD_0[minimum:maximum]

                lrl.append(np.nanmean(SWD_c1))
                sdl.append(np.nanstd(SWD_c1))
                


        if (segment==droite):
            print("droite")
            print("")
            plt.plot(OFROL[0:lofr-1],lrl[0:lofr-1],'b-')
        elif (segment==gauche):
            print("gauche")
            plt.plot(OFROL[0:lofr-1],lrl[lofr:2*lofr-1],'r-')
            print("")

    mpl.rcParams['xtick.labelsize'] = 6          
    plt.legend(['soleil à droite','soleil à gauche' ],loc="lower right",fontsize=7)    
    plt.xlabel('Ofrol',size=6)
    plt.ylabel('Watts par metre carré')
    plt.title(acqid+" flux descendants corriges oftag="+str(OFTAG[0]),fontsize=9)
    plt.show

    plt.close

    numjour=float(ab.strftime("%j"))

    ax = mpl_fig.add_subplot(212)

    color=["red","blue"]

    OFROL=[0.0]         
    OFTAG= np.arange(-3.0,3.0,0.5)        
    loft=len(OFTAG)

    lrl=[]
    sdl=[]

    segments=segments2
    for segment in segments:
        mini=segment[0]
        maxi=segment[1]
        minimum=min([j for j in range(len(timei)) if timei[j]>mini])
        maximum=max([j for j in range(len(timei)) if timei[j]<maxi])

        print(segment)
        resultat_theta=np.mean(theta_0[minimum:maximum])
        print("THETA", resultat_theta)
        resultat_phi=np.nanmean(phi_0[minimum:maximum])
        print("PHI", resultat_phi)
        resultat_cap=np.nanmean(cap_geo[minimum:maximum])
        print("CAP", resultat_cap)

        for ofrol in OFROL:    
            for oftag in OFTAG:
            
                Xna_0,Xasa,SWD_0,SWD_c=ps.corrassiet(numjour,timei,longi,lati,cap_geo,roll,pitch,ofrol,oftag,swdown_0)
            
                SWD_c1= SWD_c[minimum:maximum]
                SWD_01=SWD_0[minimum:maximum]

                lrl.append(np.nanmean(SWD_c1))
                sdl.append(np.nanstd(SWD_c1))
                


        if (segment==face):
            print("face")
            print("")
            plt.plot(OFTAG[0:loft-1],lrl[0:loft-1],'b-')
        elif (segment==dos):
            print("dos")
            plt.plot(OFTAG[0:loft-1],lrl[loft:2*loft-1],'r-')
            print("")
    mpl.rcParams['xtick.labelsize'] = 6  
    plt.legend(['soleil de face','soleil de dos' ],loc="lower right",fontsize=7)
    plt.xlabel('Oftag',size=6)
    plt.ylabel('Watts par metre carré')
 
    plt.title(acqid+" flux descendant corrige ofrol="+str(OFROL[0]),fontsize=9)

    plt.show()

    
    
