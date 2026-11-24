#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

if not os.environ.get('DISPLAY'):
    import matplotlib
    matplotlib.use('Agg')

from optparse import OptionParser, IndentedHelpFormatter
import configparser

import matplotlib.pyplot as plt
import time
import numpy as npy
import re
from pylab import *
import scipy.signal as signal
import math
import itertools

import matplotlib.image as image
import matplotlib.mlab as ml 

from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.widgets import MultiCursor
from matplotlib.image import NonUniformImage
from matplotlib.dates import DateFormatter, SecondLocator, MinuteLocator
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
from matplotlib.font_manager import FontProperties
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from mpl_toolkits.mplot3d import Axes3D

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader
from cartopy.mpl.patch import geos_to_path
import cartopy.io.img_tiles as cimgt


import cartopy
cartopy.config['data_dir'] =  os.path.join(os.getenv('AIDA_HOME'),  'share/common/Cartes')
cartopy.config['pre_existing_data_dir'] = os.path.join(os.getenv('AIDA_HOME'),  'share/common/Cartes')

version = 2.0

if matplotlib.__version__ > '1.0.0' :
    from mpl_toolkits.axisartist.grid_helper_curvelinear import GridHelperCurveLinear
    from mpl_toolkits.axisartist import Subplot
else :
    from mpl_toolkits.axes_grid.grid_helper_curvelinear import GridHelperCurveLinear


PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))
import AIDA
import cfunits as cf

AH = os.getenv('AIDA_HOME')

def read_vect(acq_id, name):
    try:
        vect = AIDA.Vector (acq_id, name)
    except IOError as xxx_todo_changeme:
        (errno, strerror) = xxx_todo_changeme.args
        print("Echec lecture vecteur %s : %s" % (name, strerror))
        return -3
    except AIDA.AidaError as msg:
        Abandon("Probleme AIDA lors lecture vecteur %s : %s" % (name, msg))
        return -2
    return vect

def recup_valeur_config(config, section, nom_var, var_default=None) :

    try:
        str_valeur = config.get(section, nom_var)
    except configparser.NoOptionError:
        str_valeur = var_default

    return str_valeur

def decompose_chaine_operation(str_oper, acqid) :

    rep_data = AIDA.ID_to_datapath(acqid)

    GROUP=re.split('[+-]',str_oper)
    OPER = ''

# Etude premier groupe de l'opération.

    ELEMENT=re.split('[/*]',GROUP[0])
    OPERATEUR = ''

    try :
        data1 = float(ELEMENT[0])
        Unit1 = ELEMENT[0]
    except :
        data_tmp = read_vect(acqid, ELEMENT[0])
        vector_time = data_tmp.attributes["ref_time"]
        try : 
            src = os.path.join(rep_data, vector_time)+'.vbn'
            vector_time = os.readlink(src)[:-4]
        except :
            pass
        Unit1 = data_tmp.attributes["unit"]
        data1 = data_tmp.data
        data_c1 = data1

    if len(ELEMENT) > 1 :
        lc = len(ELEMENT[0])
        OPERATEUR = GROUP[0][lc]
        try :
            data2 = float(ELEMENT[1])
            Unit2 = ELEMENT[1]
        except :
            data_tmp = read_vect(acqid, ELEMENT[1])
            vector_time2 = data_tmp.attributes["ref_time"]
            try : 
                src = os.path.join(rep_data, vector_time2)+'.vbn'
                vector_time2 = os.readlink(src)[:-4]
            except :
                pass
            if vector_time != vector_time2 :
                return None, None, None
            Unit2 = data_tmp.attributes["unit"]
            data2 = data_tmp.data

    if OPERATEUR == '*' :
        data_c1 = data1 * data2
        UnitA = Unit1 + '*' + Unit2
    elif OPERATEUR == '/' :
        data_c1 = data1 / data2
        UnitA = Unit1 + '/' + Unit2
    else :
        UnitA = Unit1

# Si existe, Etude deuxieme groupe de l'opération.

    if len(GROUP) > 1 :
        lc = len(GROUP[0])
        OPER = str_oper[lc]

        ELEMENT=re.split('[/*]',GROUP[1])
        OPERATEUR = ''

        try :
            data1 = float(ELEMENT[0])
            Unit1 = ELEMENT[0]
        except :
            data_tmp = read_vect(acqid, ELEMENT[0])
            vector_time2 = data_tmp.attributes["ref_time"]
            try : 
                src = os.path.join(rep_data, vector_time2)+'.vbn'
                vector_time2 = os.readlink(src)[:-4]
            except :
                pass
            if vector_time != vector_time2 :
                return None, None, None
            Unit1 = data_tmp.attributes["unit"]
            data1 = data_tmp.data
            data_c2 = data1
       
        if len(ELEMENT) > 1 :
           lc = len(ELEMENT[0])
           OPERATEUR = GROUP[1][lc]
           try :
               data2 = float(ELEMENT[1])
               Unit2 = ELEMENT[1]
           except :
               data_tmp = read_vect(acqid, ELEMENT[1])
               vector_time2 = data_tmp.attributes["ref_time"]
               try : 
                   src = os.path.join(rep_data, vector_time2)+'.vbn'
                   vector_time2 = os.readlink(src)[:-4]
               except :
                   pass
               if vector_time != vector_time2 :
                   return None, None, None
               Unit2 = data_tmp.attributes["unit"]
               data2 = data_tmp.data

        if OPERATEUR == '*' :
            data_c2 = data1 * data2
            UnitB = Unit1 + '*' + Unit2
        elif OPERATEUR == '/' :
            data_c2 = data1 / data2
            UnitB = Unit1 + '*' + Unit2
        else :
            UnitB = Unit1

    if OPER == "-" :
       data_f = data_c1 - data_c2
       Unit = UnitA + '-' + UnitB
    elif OPER == "+" :
       data_f = data_c1 + data_c2
       Unit = UnitA + '+' + UnitB
    else :
       data_f = data_c1
       Unit = UnitA

    return vector_time, Unit, data_f

def calcul_bornes_sup(seuils_classe, nb_classe,data) :

    SupMin = npy.nanmin(data)
    seuils_classe.append(SupMin)
    SupMax = npy.nanmax(data)

    SupLong = SupMax - SupMin

    for nc in npy.arange(1, nb_classe) :
        val = int(SupMin + (nc*SupLong)/nb_classe)
        seuils_classe.append(val)

    seuils_classe.append(SupMax)

def Tracer_dsp(Graphe_Config,acqid, repout, repout_sec, Options) :

    def dsp_manq (x, NFFT, fs = 1, taux_manq_max = 0.5, dsp_fois_freq = False, recouvrement = 0, fenetre = lambda n : npy.full(n, 1.0) ) :
        """ 
        Calcul de la DSP d'un signal à partir de la moyennes de DSP (méthode du periodogramme) 

        Entrees :
            x : parametre d'entree
            NFFT : nombre de points de la FFT
            fs : frequence d'échantillonnage de x
            taux_manq_max : taux maximum de valeurs manquantes pour le calcul de la DSP 
            dsp_fois_freq : si True renvoie la DSP*frequence (spectre de puissance)
                            si False renvoie la DSP (densité spectrale de puissance en Hz-1)
            recouvrement : nombre de points de recouvrement des périodes 
            fenetre : fonction fenetre(len(x)) qui renvoie les valeurs de la fenetre de pondération 
                      à appliquer à chaque période. 
                      On peut utiliser les fonctions de Numpy :  npy.hanning, npy.bartlett, npy.blackman, npy.hamming, ...

        Sorties :
            "dict" contenant:
                'dsp' : tableau de valeurs de la DSP
                'freq' : tableau des fréquences correspondant à la DSP
                'n_iter' : nombre de périodes utilisées pour le calcul de la DSP


        remarque : 
        On utilise la fonction de scipy.signal.welch pour calculer la DSP car la 
        certaines versions de la fonction matplotlib.psd ne donnent pas des
        bonnes valeurs de puissance.
        """
 

        spectre={}

        if dsp_fois_freq :
            scale = 'spectrum'
        else: 
            scale = 'density'

    # pour le moment on enleve la moyenne 
    # le choix de ce traitement pourra être passé en argument
        detrending = ml.detrend_mean

        n_recouv = recouvrement*NFFT
        dsp = npy.zeros(NFFT/2+1)
        n_iter = 0
        ideb = 0
        ifin = NFFT
        while   ifin < len(x) :
            x_part = x[ideb : ifin] 
            # traitement des valeurs manquantes
            x_part, rap_manq = remplace_val_manq (x_part, taux_max_manq_interpol = 0.1, val_remplace = 0.0 )

            if ( rap_manq > taux_manq_max ) : 
                ideb= ifin - n_recouv
                ifin = ifin + NFFT - n_recouv
                continue
      
            # calcul de la DSP
            ff, dspw = signal.welch( x_part, fs=fs, window=fenetre(NFFT), nperseg=NFFT, noverlap=n_recouv,  detrend=detrending, scaling=scale )

            dsp = dsp + dspw

            n_iter = n_iter +1 
            ideb= ifin - n_recouv
            ifin = ifin + NFFT - n_recouv 


        if (n_iter != 0 ) :
            dsp = dsp/float(n_iter)
        else : 
            dsp.fill(npy.nan)

        spectre["n_iter"]=n_iter
        spectre['dsp'] = dsp
        spectre["freq"]=npy.append( npy.fft.fftfreq(NFFT, d=1./fs)[0:NFFT/2] , fs/2)

        return spectre 

#--------------------------------------------------------------------------------------
    def remplace_val_manq (x, taux_max_manq_interpol = 0.1, val_remplace = 0.0  ) :
        """ 
        Remplace les valeurs manquantes valant NaN par :
            - une interpolation linéaire si le taux de valeurs manquantes
              est inférieur à 'taux_max_manq_interpol'
            - 'val_remplace' si le taux de valeurs manquantes est supérieur à
              'taux_max_manq_interpol'

        Entrees :
            x : parametre d'entree (tableau Numpy)
            taux_max_manq_interpol : taux  de valeurs manquantes au delà duquel on remplacera les valeurs manquantes par val_remplace
            val_remplace : valeur de substitution des valeurs manquantes

        Sorties :
            x : parametre d'entree dans lequel on a remplace toutes les valeurs manquantes
            rap_manq : taux de valeurs manquantes remplacées
        """

        idx_manq = npy.where ( npy.logical_not( npy.isfinite(x) ))[0]
        n_manq = len ( idx_manq ) 
 
        rap_manq = float(n_manq)/ len(x)

        if ( 0 < rap_manq < taux_max_manq_interpol ) :
            x = interpolin ( x )  
        else :
            x[ idx_manq ] = val_remplace 

        return x, rap_manq

#--------------------------------------------------------------------------------------
    def interpolin (data):
        """ 
        Remplace les valeurs manquantes (NaN) par une interpolation linéaire

        Entree : 
            data (tableau Numpy) : parametre 

        Sortie :
            data (tableau Numpy) : parametre avec valeurs NaN remplacées par une interpolation
        """

        good_indexes = npy.isfinite(data)
        bad_indexes = npy.logical_not(good_indexes)
        good_data = data[good_indexes]
        interpolated = npy.interp(bad_indexes.nonzero()[0], good_indexes.nonzero()[0], good_data)
        data[bad_indexes] = interpolated
        return data

#--------------------------------------------------------------------------------------

    axes=[]
    font = {'family' : 'serif',
        'color'  : 'black',
        'weight' : 'normal',
        'size'   : 8,
        }
    font_legend = FontProperties()
    font_legend.set_size(7)
    Color_courbe = ["Blue","Green","Red","Cyan","Orange","Brown","Yellow","Grey","Black","Purple"]

    try :
        acq_meta = AIDA.Inf(acqid)
    except AIDA.AidaError :
        Message = "\nALARME : Attention Acqid non valid !\n"
        print(Message)
        return

    try :
        date_vol_inf=acq_meta.get_date_acq()
    except :
        Message = "\nALARME : Pas de fichier Inf pour l'acquisition " + acqid + "!\n"
        print(Message)
        return

    second_vol_inf=date2num(date_vol_inf)

    if Options.deb != None and  Options.deb != "acq":
        heure = Options.deb 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_dec =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_dec = acq_meta.get_horaire('decollage')

    if heure_dec == None or  Options.deb == "acq":
        heure_dec = acq_meta.get_acquisition_borne("debut_acquisition")
    heure_dec_int=date2num(heure_dec)
        
    if Options.fin != None and Options.fin != "acq":
        heure = Options.fin 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_att =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_att = acq_meta.get_horaire('atterrissage')

    if heure_att == None or Options.fin == "acq" :
        heure_att = acq_meta.get_acquisition_borne("fin_acquisition")
    heure_att_int=date2num(heure_att)

    try :
        Titre_Graphe_defaut = acq_meta.get_field_value("IDENTIFICATION", "campagne")
    except :
        Titre_Graphe_defaut = ""

    Titre_Graphe = recup_valeur_config(Graphe_Config, 'general_graphe','TitreGraph')
    if Titre_Graphe == None :
        Abandon("dans %s, [SerieTempo] n'a pas de type graphe declare" % (Options.ficapc))

    flg_Titre_Graphe = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'Flg_TitreGraph', var_default="0"))
    flg_Legend = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'Flg_Legend', var_default="0"))
    Flg_top = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'FlgTop', var_default="0"))
    Flg_seg = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'FlgSequence', var_default="0"))

    if Orient_Page == 'Paysage' or  Orient_Page == 'paysage' :
        fig = plt.figure(figsize=(10,8))
    elif Orient_Page == 'Portrait' or Orient_Page == 'portrait':
        fig = plt.figure(figsize=(8,10))
    else :
        dim_page = Orient_Page.split(",")
        fig = plt.figure(figsize=(float(dim_page[0]),float(dim_page[1])))

    try:
        Pos_image = Graphe_Config.get('general_graphe', 'PositionImage')[1:-1].split(",")
        for val in npy.arange(4) :
            try :
                Pos_image[val] = float(Pos_image[val])/100
            except :
                Pos_image[val] = None
    except configparser.NoOptionError:
        Pos_image = [None, None, None, None]
#        Abandon("dans [gene_graphe] pas orientation ")


    if Pos_image[1] != None :
        fig.subplots_adjust(right = float(Pos_image[1]))
    elif  flg_Legend == 0 :
        fig.subplots_adjust(right=0.80)
    else :
        fig.subplots_adjust(right=0.95)

    if Pos_image[0] != None :
        fig.subplots_adjust(left = float(Pos_image[0]))
    else :
        fig.subplots_adjust(left=0.08)

    if Pos_image[2] != None :
        fig.subplots_adjust(bottom = float(Pos_image[2])) 
    else :
        fig.subplots_adjust(bottom=0.08)

    if Pos_image[3] != None :
        fig.subplots_adjust(top = float(Pos_image[3]))
    else :
        fig.subplots_adjust(top=0.88)

# Tracer des logos si demande

# logo METEO_FRANCE
    FlgLogoMF = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'FlagLogoMF', var_default="1"))
    if FlgLogoMF == "1" :
        file_image = os.path.join (AH+'/share/common/logos/color_logomet.png')
        imag = image.imread(file_image)
        fig.figimage(imag, 10, 10)

# Autre logo 
    LogoAutre = recup_valeur_config(Graphe_Config, 'general_graphe', 'LogoAutre')
    if LogoAutre != None and  LogoAutre != "":
        file_image = os.path.join (AH + '/share/common/logos/' + LogoAutre)
        try :
            imag = image.imread(file_image)
            fig.figimage(imag, 500, 10)
        except :
            print("WARNING : fichier " + file_image + " inexistant!")
            pass

    Titre = ""
    try:
        motcle = "NomVecteur"
        liste_vecteur = Graphe_Config.get('Dsp', motcle)

        motcle = "MarqVecteur"
        Mkvecteur = Graphe_Config.get('Dsp', motcle)
        if Mkvecteur != '' :
            mark=  Mkvecteur.split(" ")
        else :
            Mkvecteur = None

        motcle = "ColorVecteur"
        Colvecteur = Graphe_Config.get('Dsp', motcle)
        if Colvecteur != '' :
            coul= Colvecteur.split(" ")
        else :
            Colvecteur = None

        motcle = "EpaisseurLigne"
        LineWidth = Graphe_Config.get('Dsp', motcle)
        if  LineWidth != '' :
            epais= LineWidth.split(" ")
        else :
            LineWidth = None

    except configparser.NoOptionError:
        Abandon("dans %s, [Dsp] n'a pas assez de data" % (Options.ficapc))
        return

    try:
        motcle = "Type_Trait"
        TypeTrait = Graphe_Config.get('Dsp', motcle)
        if  TypeTrait != '' :
            trait= TypeTrait.split(" ")
        else :
            TypeTrait = None
    except configparser.NoOptionError:
        TypeTrait = None

    try:
        motcle = "FlgGrid"
        Flg_grid = int(Graphe_Config.get('Dsp', motcle))
    except configparser.NoOptionError:
        Flg_grid = 0

    try:
        motcle = "EchellesAxeY" 
        ylim = Graphe_Config.get('Dsp', motcle)[1:-1].split(",")
        for val in npy.arange(4) :
            try :
                ylim[val] = float(ylim[val])
            except :
                ylim[val] = None
    except configparser.NoOptionError:
        ylim = [None, None, None, None]

# Récupération liste vecteurs 
    vect = liste_vecteur.split(" ")

    flg_read_ok = 0
    unit2 = ""
    unit1 = ""
    for nbv in arange(len(vect)) :
        try :
            if vect[nbv].find('-') + vect[nbv].find('+') \
                    + vect[nbv].find('*') + vect[nbv].find('/')  >= 0 :
                data_vect=[]
                vector_time=""
                Unit=""
                Titre1 = vect[nbv]
                vector_time, Unit , data_vect = decompose_chaine_operation(vect[nbv], acqid)
                dim_array = "1"
                Titre = vect[nbv]
                if vector_time == None :
                    print("Attention operation " + vect[nbv] + " impossible, temps differents")
                    break
            else :
                data1=read_vect(acqid,vect[nbv])
                if data1 < 0 :
                    axg = fig.add_subplot(2,1,1)
                    axt = axg
                    axes.append(axt)
                    flg_read_ok = flg_read_ok + 1
                    continue

                data_vect = data1.data
                vector_time = data1.attributes["ref_time"]
                Unit = data1.attributes["unit"]
                try :
                    Unit = data1.attributes["unit"]
                except :
                    Unit = 'Inconnu'

                try :
                    dim_array = data1.attributes["dim_array"]
                except KeyError:
                    dim_array = "1"
            
                try :
                    Titre = data1.attributes["english_name"]
                except KeyError:
                    Titre = vect[nbv]

            if Unit == "mbar" : 
                Unit = "hPa"

            if Unit == "degres" : 
                Unit = "degree"

            date=read_vect(acqid, vector_time)
            int_dec = 0
            int_att = len(date.data)
            date_data = []
            for i in arange(len(date.data)) :
                if date.data[i] < (heure_dec_int - second_vol_inf ) *86400 :
                    int_dec = i
                if date.data[i] < (heure_att_int - second_vol_inf ) *86400 :
                    int_att = i
                date_data.append((date.data[i]/86400) + second_vol_inf)

            if heure_dec == None or heure_att == None :
                print("PAS HEURES DEBUT ACQUISTION OU FIN ACQUISITION")
                xmin = min (date_data)
                xmax = max (date_data)
            else :
                xmin = date2num(heure_dec)
                xmax = date2num(heure_att)
            flg_data = 0
        except :
            flg_read_ok = flg_read_ok + 1
            flg_data = -1

# Gestion des axes y en fonction des unités
        if unit1 == "":
            unit1 = Unit
            unit2 =  "??"
            nb_unit = 1
            if (len(vect) > 1 ) : Titre = vect[nbv]
            axg = fig.add_subplot(2,1,1)
            axt = axg
        else :
            if Unit != unit1 and Unit != unit2 and nb_unit == 2 :
                print("ALARME : Trop d'unite pour le graphe ! ")
                break
            if Unit == unit1 :
                axt = axg
            elif Unit == unit2 :
                axt = axh
            else :
                axh = axg.twinx()
                unit2 = Unit
                nb_unit = 2
                axt = axh

        if flg_data == 0 :
            if dim_array == "1" :
                if len(vect) == 1 and flg_Titre_Graphe == 0 : 
                    axt.set_title(Titre, fontdict=font)    
                axt.set_ylabel(Unit, fontdict=font)    
                axt.set_xlabel("Heure UTC", fontdict=font)    
                if Colvecteur != 'None' :
                    try :
                        Colvec = coul[nbv]
                    except :
                        Colvec = Color_courbe[nbv]
                else :
                    Colvec = Color_courbe[nbv]

                if Mkvecteur != 'None' :
                    try :
                        Markv = mark[nbv]
                    except :
                        Markv = ''
                else :
                    Markvec = ''

                if LineWidth != 'None' :
                    try :
                        Epaisv = epais[nbv]
                    except :
                        Epaisv = 1
                else :
                    Epaisv = 1

                if TypeTrait != 'None' :
                    try :
                        Typev = trait[nbv]
                    except :
                        Typev = "Continu"
                else :
                    Typev = "Continu"

                if Markv == "Aucun" :
                    Markv = ""

                if Typev == 'Continu' :
                    c_trait = '-'
                elif Typev == 'Tiret' :
                    c_trait = '--'
                elif Typev == 'Pointille' :
                    c_trait = ':'
                elif Typev == 'Nuage' :
                    c_trait = Markv + 'S'
                elif Typev == 'Aucun' :
                    c_trait = Markv
                else :
                    c_trait = ''

                axt.plot_date(date_data[int_dec:int_att],data_vect[int_dec:int_att], c_trait,color=Colvec,linewidth=float(Epaisv),label=vect[nbv])

                ymin, ymax = axt.get_ylim()
                if ymin < 0 and ymax > 0 :
                    axt.axhline(y=0,linestyle='--',linewidth=1., color='black')

                if  flg_Legend == 0 :
                    if Unit == unit1 :
                        axt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0., prop=font_legend)
                    else :
                        axt.legend(bbox_to_anchor=(1, 0), loc=2, borderaxespad=0., prop=font_legend)
                elif  flg_Legend == 1 :
                        axt.legend(prop=font_legend)
                axt.set_xlim([xmin,xmax])
                axt.set_xticklabels(date_data,fontsize=8)
                for tick in axg.get_yticklabels() :
                    tick.set_fontsize(8)
                try :
                    for tick in axh.get_yticklabels() :
                        tick.set_fontsize(8)
                except :
                    pass
                axt.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                fig.autofmt_xdate()
            else :
                print("Pas de graphe DSP avec les vecteurs dim_array > 1")
                return

# PLOT DSP
            ax_dsp = fig.add_subplot(2, 1, 2)
            ax_dsp.set_xscale("log")
            ax_dsp.set_yscale("log")
            ax_dsp.set_xlabel('Fréquence')
            ax_dsp.set_ylabel('Power Spectral Density (dB/Hz)')
            axes.append(ax_dsp)
            ax_dsp.grid(True)

            fs = len(date_data[int_dec:int_att]) / (date_data[int_att] - date_data[int_dec])
            taille_fft = min(2048, len(data_vect[int_dec:int_att])//2)

            spectre = dsp_manq (data_vect[int_dec:int_att],taille_fft , fs = fs, taux_manq_max = 0.5, dsp_fois_freq = False, recouvrement = 0, fenetre = lambda n : npy.full(n, 1.0) )

            ax_dsp.plot(spectre["freq"][1:], spectre["dsp"][1:])



        if Flg_grid == 1 :
            axt.grid(True)
        axes.append(axt)

    if flg_read_ok == len(vect) :
        axt.set_title(vect[nbv], fontdict=font)    
        xn, xx = axt.get_xlim()
        topx = xn + (xx - xn)/2
        axt.text(topx, 0.5, 'PAS DE DONNEES', {'color' : 'r', 'fontsize' : 8})

# Cas d'echelle(s) fixe(s) 
    if ylim[0] != None or ylim[1] != None :
        ymin =  ylim[0]
        ymax =  ylim[1]
        axg.set_ylim(ymin, ymax)

    if unit2 != "??" :
        if ylim[2] != None or ylim[3] != None :
            ymin =  ylim[2]
            ymax =  ylim[3]
            axh.set_ylim(ymin, ymax)


#   Affichages des tops si demandes
    if Flg_top == 1 :
        try :
            data_top = read_vect(acqid, "top_MAIN_0")
            vector_time_top = data_top.attributes["ref_time"]
            date_top = read_vect(acqid, vector_time_top)

            time_top = []
            top_data = []
            top_type = []
            for nt in npy.arange(len(data_top.data)) :
                res = "{0:016b}".format(int(data_top.data[nt].hex(), 16))
                top_type.append(int(str(res)[0:7],2))
                time_top.append(date_top.data[nt])
                top_data.append(int(str(res)[7:16],2))
            flg_top = 1
            IHM.graph_gene.FlgTop = 1
        except :
            try : 
                data_top = read_vect(acqid, "topnb_cal_1")
                vector_time_top = data_top.attributes["ref_time"]
                date_top = read_vect(acqid, vector_time_top)

                time_top = []
                top_data = []
                for nt in npy.arange(len(data_top.data)) :
                    if int(data_top.data[nt]) > 0 :
                        time_top.append(date_top.data[nt])
                        top_data.append(data_top.data[nt])
            except :
                print("WARNING : Pas de fichier des tops présent dans le répertoire")
                Flg_top = 0

    if Flg_top == 1 :
        ymin, ymax = axt.get_ylim()
        xmin, xmax = axt.get_xlim()
        Tymax = ymax - ( 0.05 * (ymax-ymin))
        for nt in npy.arange(len(time_top)) :
            topx = second_vol_inf + time_top[nt]/86400
            axt.axvline(x = topx, linestyle = ':')
            if topx >= xmin and topx <= xmax :
                axt.text(topx, Tymax, top_data[nt], {'color' : 'r', 'fontsize' : 8}, rotation = 90)
            else :
                axt.axvline(x = time_top[nt], linestyle = '--')
            if time_top[nt] >= xmin and time_top[nt] <= xmax :
                 axt.text(time_top[nt], Tymax, nt, {'color' : 'r', 'fontsize' : 8}, rotation = 90)

# Afichage des sequences si demandé
    if Flg_seq == 1 :
        print("AFFICHAGE SEQUENCES") 
        try : 
            for (typ, seq) in acq_meta.iter_items_str('SEQUENCES') :
                champs = seq.split('/')
                if champs[0] != 'SEQUENCES' :
                    if typ == 'palier' :
                        color = 'Blue'
                    if typ == 'sondage' :
                        color = 'Red'
                    deb = champs[1]
                    hd = int(deb[0:2])
                    md = int(deb[2:4])
                    sd = int(deb[4:6])
                    fin =  champs[2]
                    hf = int(fin[0:2])
                    mf = int(fin[2:4])
                    sf = int(fin[4:6])
                    XSeqMin = second_vol_inf+int(hd*3600+md*60+sd)/86400.
                    XSeqMax = second_vol_inf+int(hf*3600+mf*60+sf)/86400.

#                    print XSeqMin, XSeqMax
                    for n_ax in npy.arange(len(axes)) :
                        axt = axes[n_ax]
                        ymin, ymax = axt.get_ylim()
                        data_poly=[(XSeqMin,ymin),(XSeqMin,ymax),(XSeqMax,ymax),(XSeqMax,ymin)]
                        poly = Polygon(data_poly, color=color, alpha=0.2)
                        axt.add_patch(poly)
        except :
            print("PROBLEME LECTURE DES SEQUENCES")

    plt_f = AIDA.plt_by_abrev[acqid[0:2]]

#    Ecriture des titres
    if Titre_Graphe != "" :
#        Titre= Titre_Graphe.decode("utf-8")
        Titre= Titre_Graphe
    else :
        Titre= "Campagne " + Titre_Graphe_defaut + " " + Options.ficapc

    if flg_Titre_Graphe == 0 :
        plt.figtext(0.5, 0.970, Titre, ha='center', color='black')
        Titre2= plt_f.nom_serie_mesure + " " +  plt_f.nom + " "  + acqid + " du " + date_vol_inf.strftime("%d/%m/%Y")
        plt.figtext(0.5, 0.945, Titre2, ha='center', color='black')
        Titre3= "de " + heure_dec.strftime("%Hh%Mm%S") + " a " +  heure_att.strftime("%Hh%Mm%S") + ' UTC'
        plt.figtext(0.5, 0.920, Titre3, ha='center', color='black')
    else :
        plt.figtext(0.5, 0.97, Titre, ha='center', color='black')

    if Options.out == 'Ecran' :
        plt.show()
    else :
        if  os.path.isdir(repout) == False :
            Message = "INFO : Dépot du (ou des) fichier(s) résultat(s) dans le répertoire " + repout
            print(Message)
            try :
                os.makedirs(repout)
                os.chmod(repout,0o775)
            except :
                print("ALARME : CREATION REPERTOIRE ECHOUE")
                repout = repout_sec

        Sauvegarde_graphe(acqid, Options, repout, fig)

def Tracer_SerieTempo(Graphe_Config,acqid, repout, repout_sec, Options) :

    axes=[]
    font = {'family' : 'serif',
        'color'  : 'black',
        'weight' : 'normal',
        'size'   : 8,
        }
    font_legend = FontProperties()
    font_legend.set_size(7)
    Color_courbe = ["Blue","Green","Red","Cyan","Orange","Brown","Yellow","Grey","Black","Purple"]

#    ymax =  -10000000
#    ymin =  10000000

    try :
        acq_meta = AIDA.Inf(acqid)
    except AIDA.AidaError :
        Message = "\nALARME : Attention Acqid non valid !\n"
        print(Message)
        return

    try :
        date_vol_inf=acq_meta.get_date_acq()
    except :
        Message = "\nALARME : Pas de fichier Inf pour l'acquisition " + acqid + "!\n"
        print(Message)
        return

    second_vol_inf=date2num(date_vol_inf)

    if Options.deb != None and  Options.deb != "acq":
        heure = Options.deb 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_dec =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_dec = acq_meta.get_horaire('decollage')

    if heure_dec == None or  Options.deb == "acq":
        heure_dec = acq_meta.get_acquisition_borne("debut_acquisition")
    heure_dec_int=date2num(heure_dec)
        
    if Options.fin != None and Options.fin != "acq":
        heure = Options.fin 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_att =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_att = acq_meta.get_horaire('atterrissage')

    if heure_att == None or Options.fin == "acq" :
        heure_att = acq_meta.get_acquisition_borne("fin_acquisition")
    heure_att_int=date2num(heure_att)

    try :
        Titre_Graphe_defaut = acq_meta.get_field_value("IDENTIFICATION", "campagne")
    except :
        Titre_Graphe_defaut = ""

    try:
#        Titre_Graphe = Graphe_Config.get('general_graphe', 'TitreGraph').decode("utf-8")
        Titre_Graphe = Graphe_Config.get('general_graphe', 'TitreGraph')
        Orient_Page = Graphe_Config.get('general_graphe', 'Orientation')
    except configparser.NoOptionError:
        Abandon("INFO_APC : dans [SerieTempo] n'a pas de type graphe declare")

    try:
        flg_Titre_Graphe = int(Graphe_Config.get('general_graphe', 'Flg_TitreGraph'))
    except configparser.NoOptionError:
        flg_Titre_Graphe = 0
        Abandon("INFO_APC : dans [gene_graphe] pas Flg_TitreGraphe ")

    try:
        flg_Legend = int(Graphe_Config.get('general_graphe', 'Flg_Legend'))
    except configparser.NoOptionError:
        flg_Legend = 0
        Abandon("INFO_APC : dans [gene_graphe] pas Flg_Legend ")

    try:
        Flg_top = int(Graphe_Config.get('general_graphe', 'FlgTop'))
    except configparser.NoOptionError:
        Abandon("INFO_APC : dans[SerieTempo] pas de flag top : Pas d affichage")
        Flg_top = 0

    try:
        Flg_seq = int(Graphe_Config.get('general_graphe', 'FlgSequence'))
    except configparser.NoOptionError:
        Abandon("INFO_APC : [SerieTempo] pas de flag sequence : Pas d affichage")
        Flg_seq = "0"

    try:
        NbGraph = int(Graphe_Config.get('SerieTempo', 'NbGraph'))
        print("NBGRAPHE = ", NbGraph)
    except configparser.NoOptionError:
        Abandon("INFO_APC : dans [SerieTempo] pas NbGraph" )

    if Orient_Page == 'Paysage' or  Orient_Page == 'paysage' :
        fig = plt.figure(figsize=(10,8))
    elif Orient_Page == 'Portrait' or Orient_Page == 'portrait':
        fig = plt.figure(figsize=(8,10))
    else :
        dim_page = Orient_Page.split(",")
        fig = plt.figure(figsize=(float(dim_page[0]),float(dim_page[1])))

    try:
        Type_graphe_serie = Graphe_Config.get('general_graphe', 'TypeGrapheSerie')
    except configparser.NoOptionError:
        Type_graphe_serie = ""
        Abandon("INOF_APC : dans [general_graphe] pas TypeGrapheSerie")

    try:
        Pos_image = Graphe_Config.get('general_graphe', 'PositionImage')[1:-1].split(",")
        for val in npy.arange(4) :
            try :
                Pos_image[val] = float(Pos_image[val])/100
            except :
                Pos_image[val] = None
    except configparser.NoOptionError:
        Pos_image = [None, None, None, None]
#        Abandon("dans [gene_graphe] pas orientation ")

    if Pos_image[1] != None :
        fig.subplots_adjust(right = float(Pos_image[1]))
    elif  flg_Legend == 0 :
        fig.subplots_adjust(right=0.80)
    else :
        fig.subplots_adjust(right=0.95)

    if Pos_image[0] != None :
        fig.subplots_adjust(left = float(Pos_image[0]))
    else :
        fig.subplots_adjust(left=0.08)

    if Pos_image[2] != None :
        fig.subplots_adjust(bottom = float(Pos_image[2])) 
    else :
        fig.subplots_adjust(bottom=0.08)

    if Pos_image[3] != None :
        fig.subplots_adjust(top = float(Pos_image[3]))
    else :
        fig.subplots_adjust(top=0.88)

# Tracer des logos si demande

# logo METEO_FRANCE
    FlgLogoMF = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'FlagLogoMF', var_default="1"))
    if FlgLogoMF == "1" :
        file_image = os.path.join (AH+'/share/common/logos/color_logomet.png')
        imag = image.imread(file_image)
        fig.figimage(imag, 10, 10)

# Autre logo 
    LogoAutre = recup_valeur_config(Graphe_Config, 'general_graphe', 'LogoAutre')
    if LogoAutre != None and  LogoAutre != "":
        file_image = os.path.join (AH + '/share/common/logos/' + LogoAutre)
        try :
            imag = image.imread(file_image)
            fig.figimage(imag, 500, 10)
        except :
            print("WARNING : fichier " + file_image + " inexistant!")
            pass


    for ng in range(int(NbGraph)) :

        Titre = ""
        try:
            motcle = "NomVecteur" + str(ng+1)
            liste_vecteur = Graphe_Config.get('SerieTempo', motcle)

            motcle = "MarqVecteur" + str(ng+1)
            Mkvecteur = Graphe_Config.get('SerieTempo', motcle)
            if Mkvecteur != '' :
                mark=  Mkvecteur.split(" ")
            else :
                Mkvecteur = None

            motcle = "ColorVecteur" + str(ng+1)
            Colvecteur = Graphe_Config.get('SerieTempo', motcle)
            if Colvecteur != '' :
                coul= Colvecteur.split(" ")
            else :
                Colvecteur = None

            motcle = "EpaisseurLigne" + str(ng+1)
            LineWidth = Graphe_Config.get('SerieTempo', motcle)
            if  LineWidth != '' :
                epais= LineWidth.split(" ")
            else :
                LineWidth = None
        except configparser.NoOptionError:
            Abandon("dans %s, [SerieTempo] n'a pas assez de data" % (Options.ficapc))
            continue

        try:
            motcle = "Type_Trait" + str(ng+1)
            TypeTrait = Graphe_Config.get('SerieTempo', motcle)
            if  TypeTrait != '' :
                trait= TypeTrait.split(" ")
            else :
                TypeTrait = None
        except configparser.NoOptionError:
            TypeTrait = None

        try:
            motcle = "FlgGrid" + str(ng+1)
            Flg_grid = int(Graphe_Config.get('SerieTempo', motcle))
        except configparser.NoOptionError:
            Flg_grid = 0

        try:
            motcle = "EchellesAxeY" + str(ng+1)
            ylim = Graphe_Config.get('SerieTempo', motcle)[1:-1].split(",")
            for val in npy.arange(4) :
                try :
                    ylim[val] = float(ylim[val])
                except :
                    ylim[val] = None
        except configparser.NoOptionError:
            ylim = [None, None, None, None]

        try:
            motcle = "Type_echelle" + str(ng+1)
            type_echelle = Graphe_Config.get('SerieTempo', motcle)
        except configparser.NoOptionError:
            type_echelle = 'lineaire'

        vect = liste_vecteur.split(" ")

        flg_read_nok = 0
        unit2 = ""
        unit1 = ""
        nbg_mq = 0
        for nbv in arange(len(vect)) :
            try :
                if vect[nbv].find('-') + vect[nbv].find('+') \
                        + vect[nbv].find('*') + vect[nbv].find('/')  >= 0 :
                    data_vect=[]
                    vector_time=""
                    Unit=""
                    Titre1 = vect[nbv]
                    vector_time, Unit , data_vect = decompose_chaine_operation(vect[nbv], acqid)
                    dim_array = "1"
                    Titre = vect[nbv]
                    if vector_time == None :
                        print("Attention operation " + vect[nbv] + " impossible, temps differents")
                        break
                else :
                    data1=read_vect(acqid,vect[nbv])
                    if len(data1.data) < 0 :
                        if ng == 0 :
                            axg = fig.add_subplot(NbGraph,1,ng+1)
                        else :
                            axg = fig.add_subplot(NbGraph,1,ng+1,sharex=axes[0])
                        axt = axg
                        axes.append(axt)
                        flg_read_nok = flg_read_nok + 1
                        Abandon("ERREUR : PROBLEME LECTURE VECTEUR " + vect[nbv])
                        xn, xx = axt.get_xlim()
                        topx = xn + (xx - xn)/2
                        yn, yx = axt.get_ylim()
                        topy = yn + (yx - yn)/2
                        nbg_mq = mbg_mq + 1
#                        print nbg_mq, len(vect)
                        continue

                    data_vect = data1.data
                    vector_time = data1.attributes["ref_time"]
                    Unit = data1.attributes["unit"]
                    try :
                        Unit = data1.attributes["unit"]
                        cfunit = cf.Units(Unit)
                    except :
                        Unit = 'Inconnu'

                    try :
                        dim_array = data1.attributes["dim_array"]
                    except KeyError:
                        dim_array = "1"
            
                    try :
                        Titre = data1.attributes["english_name"]
                    except KeyError:
                        Titre = vect[nbv]

#                if Unit == "mbar" : 
#                    Unit = "hPa"
#
#                if Unit == "degres" : 
#                    Unit = "degree"

                date=read_vect(acqid, vector_time)
                int_dec = 0
                int_att = len(date.data)
                date_data = []
                for i in arange(len(date.data)) :
                    if date.data[i] < (heure_dec_int - second_vol_inf ) *86400 :
                        int_dec = i
                    if date.data[i] < (heure_att_int - second_vol_inf ) *86400 :
                        int_att = i
                    date_data.append((date.data[i]/86400) + second_vol_inf)

                if heure_dec == None or heure_att == None :
                    Abandon("INFO : PAS HEURES DEBUT ACQUISTION OU FIN ACQUISITION")
                    xmin = min (date_data)
                    xmax = max (date_data)
                else :
                    xmin = date2num(heure_dec)
                    xmax = date2num(heure_att)
                flg_data = 0
            except :
                flg_read_nok = flg_read_nok + 1
                flg_data = -1

#            if nbv == 0 :
            if unit1 == "":
                unit1 = Unit
                cfunit1 = cfunit
                unit2 =  "??"
                nb_unit = 1
                if (len(vect) > 1 ) : Titre = vect[nbv]
                if ng == 0 :
                    axg = fig.add_subplot(NbGraph,1,ng+1)
                else :
                    axg = fig.add_subplot(NbGraph,1,ng+1,sharex=axes[0])
                axt = axg
            else :
                if cfunit1.equivalent(cfunit) :
                    print(Unit, unit1)
                    print("Unités compatible : Conversion automatique")
                    Unit = unit1
                    cf.Units.conform(data_vect, cfunit, cfunit1, inplace=True)
                if Unit != unit1 and Unit != unit2 and nb_unit == 2 :
                    Abandon("ALARME : Trop d'unite pour le graphe ! ")
                    break
                if Unit == unit1 :
                    axt = axg
                elif Unit == unit2 :
                    axt = axh
                else :
                    axh = axg.twinx()
                    unit2 = Unit
                    cfunit2 = cfunit
                    nb_unit = 2
                    axt = axh

            if flg_data == 0 :
                if dim_array == "1" :
                    if len(vect) == 1 and flg_Titre_Graphe == 0 : 
                        axt.set_title(Titre, fontdict=font)    
                    axt.set_ylabel(Unit, fontdict=font)    
                    axt.set_xlabel("Heure UTC", fontdict=font)    
                    if Colvecteur != 'None' :
                        try :
                            Colvec = coul[nbv]
                        except :
                            Colvec = Color_courbe[nbv]
                    else :
                        Colvec = Color_courbe[nbv]

                    if Mkvecteur != 'None' :
                        try :
                            Markv = mark[nbv]
                        except :
                            Markv = ''
                    else :
                        Markvec = ''

                    if LineWidth != 'None' :
                        try :
                            Epaisv = epais[nbv]
                        except :
                            Epaisv = 1
                    else :
                        Epaisv = 1

                    if TypeTrait != 'None' :
                        try :
                            Typev = trait[nbv]
                        except :
                            Typev = "Continu"
                    else :
                        Typev = "Continu"

                    if Markv == "Aucun" :
                        Markv = ""

                    if Typev == 'Continu' :
                        c_trait = '-'
                    elif Typev == 'Tiret' :
                        c_trait = '--'
                    elif Typev == 'Pointille' :
                        c_trait = ':'
                    elif Typev == 'Nuage' :
                        c_trait = Markv + 'S'
                    elif Typev == 'Aucun' :
                        c_trait = Markv
                    else :
                        c_trait = ''

                    axt.plot_date(date_data[int_dec:int_att],data_vect[int_dec:int_att], c_trait,color=Colvec,linewidth=float(Epaisv),label=vect[nbv])

                    if type_echelle == 'log' :
                        axt.set_yscale("log")

                    ymin, ymax = axt.get_ylim()
                    if sign(ymin) != sign(ymax) :
                        axt.axhline(y=0,linestyle='--',linewidth=1., color='black')

                    if  flg_Legend == 0 :
                        if Unit == unit1 :
                            axt.legend(bbox_to_anchor=(1, 1), loc=2, borderaxespad=0., prop=font_legend)
                        else :
                            axt.legend(bbox_to_anchor=(1, 0), loc=2, borderaxespad=0., prop=font_legend)
                    elif  flg_Legend == 1 :
                            axt.legend(prop=font_legend)
                    axt.set_xlim([xmin,xmax])
#                    axt.set_xticklabels(date_data,fontsize=8)
                    for tick in axg.get_yticklabels() :
                        tick.set_fontsize(8)
                    try :
                        for tick in axh.get_yticklabels() :
                            tick.set_fontsize(8)
                    except :
                        pass
                    axt.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))

                    if Pos_image[2] != None :
                        fig.autofmt_xdate(bottom=Pos_image[2])
                    else :
                        fig.autofmt_xdate()

                else :
                    nbct = int(dim_array)
                    nbc = 30
                    nbt = len(date_data)
                    grf = []
                    datX = []
                    iz = npy.arange(nbct)
                    lz = 0
                    nbd = 0
                    maxdata = 0

                    if Type_graphe_serie == "Image" :
                        try : 
                            Ylabel = data1.attributes["unit_bornes"]
                        except :
                            Ylabel = 'Indice'
                            
                        if Ylabel == "" :
                            Ylabel = 'Indice'

                        axt.set_ylabel(Ylabel)

                        try : 
                            Titre_image = data1.attributes["name"]
                        except :
                            Titre_image = vect[nbv]

                        font_Titre = {'family' : 'serif',
                                'color'  : 'black',
                                'weight' : 'normal',
                                'size'   : 10,
                               }
                        axg.set_title(Titre_image, fontdict=font_Titre)

                        for nz in  iz :
                            ys = []
                            nbd = 0
                            for nd in  npy.arange(nbt) :
                                if date_data[nd] > xmin and \
                                            date_data[nd] < xmax :
                                    nbd = nbd + 1
                                    if nz == 0 :
                                        datX.append((date_data[nd]-second_vol_inf)*86400)
                                    dxl = math.log(data_vect[nd][nz]+1,10)
                                    maxdata = max(maxdata, dxl)
                                    ys.append(dxl)
                    
                            if len(ys) > 1 :
                                grf.append(ys)

                        nbct = int(dim_array)
                        try :
                            str_bornes = data1.attributes["bornes"]
                            Bornes = npy.array(AIDA.strBornes_to_array(str_bornes))[:,:,0][0]
                        except :
                            print("Probleme lecture bornes dans vecteur")

                        dtmin =  npy.nanmin(data1.data)
                        dmin = math.log(dtmin+1, 10)
                        dtmax =  npy.nanmax(data1.data)
                        dmax = math.log(dtmax+1, 10)

                        maxdata=maxdata+1
                        l_ticks =  npy.arange(int(maxdata))
                        t_ticks = 10**l_ticks
                        interp='nearest'

                        c = axt.pcolormesh(datX,Bornes,grf, vmin=dmin,vmax=dmax, alpha = 1.0, cmap=matplotlib.cm.YlOrBr)
                        axt.set_ylim(0, Bornes[-1])

                        axt.set_xlim(datX[0],datX[nbd-1])
                        cbar = fig.colorbar(c, ticks=l_ticks, orientation='horizontal')
                        cbar.ax.set_xticklabels(t_ticks)

                    elif Type_graphe_serie == "Cumul" :
                        for nz in  iz :
                            ys = []
                            nbd = 0
                            for nd in  npy.arange(nbt) :
                                if date_data[nd] > xmin and \
                                            date_data[nd] < xmax :
                                    nbd = nbd + 1
                                    if nz == 0 :
                                        datX.append(date_data[nd])
                                    dxl = data_vect[nd*nbct + nz]
                                    maxdata = max(maxdata, dxl)
                                    ys.append(dxl)
                    
                            if len(ys) > 1 :
                                grf.append(ys)

                        axt.stackplot(datX, grf)

                        axt.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                        minorlocator   = AutoMinorLocator()
                        axt.xaxis.set_minor_locator(minorlocator)
                        fig.autofmt_xdate()
                        axt.set_xlim(datX[0],datX[nbd-1])
                    elif Type_graphe_serie == "Superposition" :
                        for nz in  iz :
                            ys = []
                            nbd = 0
                            for nd in  npy.arange(nbt) :
                                if date_data[nd] > xmin and \
                                            date_data[nd] < xmax :
                                    nbd = nbd + 1
                                    if nz == 0 :
                                        datX.append(date_data[nd])
                                    dxl = data_vect[nd*nbct + nz]
                                    maxdata = max(maxdata, dxl)
                                    ys.append(dxl)
                    
                            if len(ys) > 1 :
                                grf.append(ys)
                        for ng in  npy.arange(len(grf)) :
                            axt.plot_date(datX, grf[ng],'-')
                        axt.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                        minorlocator   = AutoMinorLocator()
                        axt.xaxis.set_minor_locator(minorlocator)
                        fig.autofmt_xdate()
                        axt.set_xlim(datX[0],datX[nbd-1])

            if nbg_mq == len(vect) :
                axg.text(topx, topy, 'PAS DE DONNEES', {'color' : 'red', 'fontsize' : 12})

            if Flg_grid == 1 :
                axt.grid(True)
            axes.append(axt)

##        if flg_read_nok == len(vect) :
#            axt.set_title(vect[nbv], fontdict=font)    
#            xn, xx = axt.get_xlim()
#            topx = xn + (xx - xn)/2
#            print xn, xx, topx, axt
##            axt.text(topx, 0.5, 'PAS DE DONNEES', {'color' : 'r', 'fontsize' : 8})

# Cas d'echelle(s) fixe(s) 
        if ylim[0] != None or ylim[1] != None :
            ymin =  ylim[0]
            ymax =  ylim[1]
            axg.set_ylim(ymin, ymax)

        if unit2 != "??" :
            if ylim[2] != None or ylim[3] != None :
                ymin =  ylim[2]
                ymax =  ylim[3]
                axh.set_ylim(ymin, ymax)


#   Affichages des tops si demandes
        if Flg_top == 1 :
            if ng == 0 : Abandon("INFO : AFFICHAGE DES TOPS")
            try :
                data_top = read_vect(acqid, "top_MAIN_0")
                vector_time_top = data_top.attributes["ref_time"]
                date_top = read_vect(acqid, vector_time_top)

                time_top = []
                top_data = []
                top_type = []
                for nt in npy.arange(len(data_top.data)) :
                    res = "{0:016b}".format(int(data_top.data[nt].hex(), 16))
                    top_type.append(int(str(res)[0:7],2))
                    time_top.append(date_top.data[nt])
                    top_data.append(int(str(res)[7:16],2))
                flg_top = 1
            except :
                try : 
                    data_top = read_vect(acqid, "topnb_cal_1")
                    vector_time_top = data_top.attributes["ref_time"]
                    date_top = read_vect(acqid, vector_time_top)

                    time_top = []
                    top_data = []
                    for nt in npy.arange(len(data_top.data)) :
                        if int(data_top.data[nt]) > 0 :
                            time_top.append(date_top.data[nt])
                            top_data.append(data_top.data[nt])
                except :
                   Abandon("ERREUR : Pas de fichier des tops présent pour l acqid")
                   Flg_top = 0

        if Flg_top == 1 and flg_read_nok != len(vect) :
            ymin, ymax = axt.get_ylim()
            xmin, xmax = axt.get_xlim()
            Tymax = ymax - ( 0.05 * (ymax-ymin))
            for nt in npy.arange(len(time_top)) :
                topx = second_vol_inf + time_top[nt]/86400
                axt.axvline(x = topx, linestyle = ':')
                if topx >= xmin and topx <= xmax :
                    axt.text(topx, Tymax,  top_data[nt], {'color' : 'r', 'fontsize' : 8}, rotation = 90)
                else :
                    axt.axvline(x = time_top[nt], linestyle = '--')
                if time_top[nt] >= xmin and time_top[nt] <= xmax :
                     axt.text(time_top[nt], Tymax,  top_data[nt], {'color' : 'r', 'fontsize' : 8}, rotation = 90)

# Afichage des sequences si demandé
        if Flg_seq == 1 and flg_read_nok != len(vect) :
            if ng == 0 : Abandon("INFO : AFFICHAGE SEQUENCES" )
            try : 
                for (typ, seq) in acq_meta.iter_items_str('SEQUENCES') :
                    champs = seq.split('/')
                    if champs[0] != 'SEQUENCES' :
                        if typ == 'palier' :
                            color = 'Blue'
                        if typ == 'sondage' :
                            color = 'Red'
                        deb = champs[1]
                        hd = int(deb[0:2])
                        md = int(deb[2:4])
                        sd = int(deb[4:6])
                        fin =  champs[2]
                        hf = int(fin[0:2])
                        mf = int(fin[2:4])
                        sf = int(fin[4:6])
                        XSeqMin = second_vol_inf+int(hd*3600+md*60+sd)/86400.
                        XSeqMax = second_vol_inf+int(hf*3600+mf*60+sf)/86400.

                        nba = 1
                        ymin, ymax = axt.get_ylim()
                        data_poly=[(XSeqMin,ymin),(XSeqMin,ymax),(XSeqMax,ymax),(XSeqMax,ymin)]
                        poly = Polygon(data_poly, color=color, alpha=0.2)
                        axt.add_patch(poly)
            except :
                Abandon("ERREUR : PROBLEME LECTURE DES SEQUENCES")

    plt_f = AIDA.plt_by_abrev[acqid[0:2]]

#    Ecriture des titres
    if Titre_Graphe != "" :
        Titre= Titre_Graphe 
    else :
        Titre= "Campagne " + Titre_Graphe_defaut + " " + Options.ficapc

    if flg_Titre_Graphe == 0 :
        plt.figtext(0.5, 0.970, Titre, ha='center', color='black')
        Titre2= plt_f.nom_serie_mesure + " " +  plt_f.nom + " "  + acqid + " du " + date_vol_inf.strftime("%d/%m/%Y")
        plt.figtext(0.5, 0.945, Titre2, ha='center', color='black')
        Titre3= "de " + heure_dec.strftime("%Hh%Mm%S") + " a " +  heure_att.strftime("%Hh%Mm%S") + ' UTC'
        plt.figtext(0.5, 0.920, Titre3, ha='center', color='black')
    else :
        plt.figtext(0.5, 0.97, Titre, ha='center', color='black')

    if Options.out == 'Ecran' :
        plt.show()
    else :
        if  os.path.isdir(repout) == False :
            Message = "INFO : Dépot du (ou des) fichier(s) résultat(s) dans le répertoire " + repout
            Abandon(Message)
            try :
                os.makedirs(repout)
                os.chmod(repout,0o775)
            except :
                Abandon("ALARME : CREATION REPERTOIRE ECHOUE")
                repout = repout_sec

        Sauvegarde_graphe(acqid, Options, repout, fig)

def Tracer_XY(Graphe_Config,acqid, repout,repout_sec, Options) :

    axes=[]
    font_legend = FontProperties()
    font_legend.set_size(7)
    ymax =  -10000000
    ymin =  10000000
    xmax =  -10000000
    xmin =  10000000
    UnitX1 = ""
    UnitY1 = ""
    UnitX2 = ""
    UnitY2 = ""
    flg_read_ok = 0


    try:
        Titre_Graphe = Graphe_Config.get('general_graphe', 'TitreGraph')
    except configparser.NoOptionError:
        Titre_Graphe = ""
        Abandon("dans [gene_graphe] pas Titre_Graphe ")

    try:
        flg_Titre_Graphe = Graphe_Config.get('general_graphe', 'Flg_TitreGraph')
    except configparser.NoOptionError:
        flg_Titre_Graphe = 0

    try:
        flg_Legend = int(Graphe_Config.get('general_graphe', 'Flg_Legend'))
    except configparser.NoOptionError:
        flg_Legend = 0
        Abandon("dans [gene_graphe] pas Flg_Legend ")

    try:
        Orient_Page = Graphe_Config.get('general_graphe', 'Orientation')
    except configparser.NoOptionError:
        Abandon("dans [gene_graphe] pas orientation ")

    try:
        Pos_image = Graphe_Config.get('general_graphe', 'PositionImage')[1:-1].split(",")
        for val in npy.arange(4) :
            try :
                Pos_image[val] = float(Pos_image[val])/100
            except :
                Pos_image[val] = None
    except configparser.NoOptionError:
        Pos_image = [None, None, None, None]
#        Abandon("dans [gene_graphe] pas orientation ")

    try:
        NbGraph = Graphe_Config.get('Plot_XY', 'NbGraph')
    except configparser.NoOptionError:
        Abandon("dans [gene_graphe] pas NbGraph ")

    try:
        Flg_grid = int(Graphe_Config.get('Plot_XY', 'FlgGrid'))
    except configparser.NoOptionError:
        Flg_grid = 0
        Abandon("dans [Plot_XY] pas FlgGrid ")

    if Orient_Page == 'Paysage' or  Orient_Page == 'paysage' :
        fig = plt.figure(figsize=(10,8))
    elif Orient_Page == 'Portrait' or Orient_Page == 'portrait' or  Orient_Page == '' :
        fig = plt.figure(figsize=(8,10))
    else :
        dim_page = Orient_Page.split(",")
        fig = plt.figure(figsize=(float(dim_page[0]),float(dim_page[1])))


    if  flg_Legend == 0 :
        fig.subplots_adjust(right=0.80)
    else :
        fig.subplots_adjust(right=0.95)
    fig.subplots_adjust(left=0.08)
    fig.subplots_adjust(top=0.88)
    fig.subplots_adjust(bottom=0.08)

    if Pos_image[0] != None :
        fig.subplots_adjust(left = float(Pos_image[0]))
    if Pos_image[1] != None :
        fig.subplots_adjust(right = float(Pos_image[1]))
    if Pos_image[2] != None :
        fig.subplots_adjust(bottom = float(Pos_image[2])) 
    if Pos_image[3] != None :
        fig.subplots_adjust(top = float(Pos_image[3]))

# Tracer des logos si demande

# logo METEO_FRANCE
    FlgLogoMF = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'FlagLogoMF', var_default="1"))
    if FlgLogoMF == "1" :
        file_image = os.path.join (AH+'/share/common/logos/color_logomet.png')
        imag = image.imread(file_image)
        fig.figimage(imag, 10, 10)

# Autre logo 
    LogoAutre = recup_valeur_config(Graphe_Config, 'general_graphe', 'LogoAutre')
    if LogoAutre != None and  LogoAutre != "":
        file_image = os.path.join (AH + '/share/common/logos/' + LogoAutre)
        try :
            imag = image.imread(file_image)
            fig.figimage(imag, 500, 10)
        except :
            print("WARNING : fichier " + file_image + " inexistant!")
            pass

    try :
        acq_meta = AIDA.Inf(acqid)
    except AIDA.AidaError :
        Message = "\nALARME : Attention Acqid non valid !\n"
        print(Message)
        return

    try :
        date_vol_inf=acq_meta.get_date_acq()
    except :
        Message = "\nALARME : Pas de fichier Inf pour l'acquisition " + acqid + "!\n"
        print(Message)
        return

    second_vol_inf=date2num(date_vol_inf)

    if Options.deb != None and  Options.deb != "acq":
        heure = Options.deb 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_dec =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_dec = acq_meta.get_horaire('decollage')

    if heure_dec == None or  Options.deb == "acq":
        heure_dec = acq_meta.get_acquisition_borne("debut_acquisition")
    heure_dec_int=date2num(heure_dec)
        
    if Options.fin != None and Options.fin != "acq":
        heure = Options.fin 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_att =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_att = acq_meta.get_horaire('atterrissage')

    if heure_att == None or Options.fin == "acq" :
        heure_att = acq_meta.get_acquisition_borne("fin_acquisition")
    heure_att_int=date2num(heure_att)

    if heure_dec == None or heure_att == None :
        print("PAS HEURES DEBUT ACQUISTION OU FIN ACQUISITION")
        hmin = min (date.data)
        hmax = max (date.data)
    else :
        hmin = date2num(heure_dec)

    try :
        Titre_Graphe_defaut = acq_meta.get_field_value("IDENTIFICATION", "campagne")
    except :
        Titre_Graphe_defaut = ""

    try:
        motcle = "EchellesAxeY_0"
        ylim = Graphe_Config.get('Plot_XY', motcle)[1:-1].split(",")
        for val in npy.arange(4) :
            try :
                ylim[val] = float(ylim[val])
            except :
                ylim[val] = None
    except configparser.NoOptionError:
        ylim = [None, None, None, None]

    for ng in range(int(NbGraph)) :
        try:
            mot_cle = "NomVecteurX_" + str(ng)
            vecteur_X = Graphe_Config.get('Plot_XY', mot_cle)
        except configparser.NoOptionError:
            Abandon("dans [Plot_XY] pas %s" % (motcle))

        if vecteur_X.find('-') + vecteur_X.find('+') \
                        + vecteur_X.find('*') + vecteur_X.find('/')  >= 0 :
            data_vect=[]
            vector_time_X=""
            UnitX=""
            TitreX = vecteur_X
            vector_time_X, UnitX , dataX = decompose_chaine_operation(vecteur_X, acqid)
            if vector_time_X == None :
                Message = "Attention operation " + vecteur_X + " impossible, temps differents"
                Abandon(Message, gtk.MESSAGE_ERROR)
                break
        else :
            data1=read_vect(acqid, vecteur_X)
            if len(data1.data) < 0 :
                print("PAS DE DONNES pour " + vecteur_X)
                if ng == 0 :
                    axg = fig.add_subplot(1,1,1)
                    axes.append(axg)
                flg_read_ok = flg_read_ok + 1
                continue
            else :
                TitreX = vecteur_X
                try :
                    vector_time_X = data1.attributes["ref_time"]
                except KeyError:
                    vector_time_X = vecteur_X
                UnitX = data1.attributes["unit"]
                dataX = data1.data

        date_time=read_vect(acqid, vector_time_X)
        int_dec = 0
        int_att = len(date_time.data)
        for i in arange(len(date_time.data)) :
            if date_time.data[i] < (heure_dec_int - second_vol_inf ) * 86400 :
                int_dec = i
            if date_time.data[i] < (heure_att_int - second_vol_inf ) * 86400 :
                int_att = i

        try:
            motcle = "Type_Trait_" + str(ng)
            trait = Graphe_Config.get('Plot_XY', motcle)
            if trait == 'Continu' :
                car_t = '-'
            elif trait == 'Tiret' :
                car_t = '--'
            elif trait == 'Pointille' :
                car_t = ':'
            elif trait == 'Nuage' :
                car_t = 'S'
            else :
                car_t = ''
        except configparser.NoOptionError:
            Abandon("dans [Plot_XY] pas %s" % (motcle))
            continue

        try:
            motcle = "MarqVecteur_" + str(ng)
            Mkvecteur = Graphe_Config.get('Plot_XY', motcle)
            if Mkvecteur == 'Aucun' :
                Mkvecteur = ''
        except configparser.NoOptionError:
            Abandon("dans [Plot_XY] pas %s" % (motcle))
            continue

        try:
            motcle = "ColorVecteur_" + str(ng)
            Colvecteur = Graphe_Config.get('Plot_XY', motcle)
        except configparser.NoOptionError:
            Abandon("dans [Plot_XY] pas %s" % (motcle))
            continue

        try:
            motcle = "EpaisseurLigne_" + str(ng)
            LineWidth = int(Graphe_Config.get('Plot_XY', motcle))
        except configparser.NoOptionError:
            Abandon("dans [Plot_XY] pas %s" % (motcle))
            continue

        try:
            motcle = "FonctionVecteur_" + str(ng)
            Fonction = Graphe_Config.get('Plot_XY', motcle)
        except configparser.NoOptionError:
            Abandon("dans [Plot_XY] pas %s" % (motcle))
            continue

        try:
            motcle = "NomVecteurY_" + str(ng)
            vecteur_Y = Graphe_Config.get('Plot_XY', motcle)
        except configparser.NoOptionError:
            Abandon("dans [Plot_XY] pas %s" % (motcle))
            continue

        if vecteur_Y.find('-') + vecteur_Y.find('+') \
                        + vecteur_Y.find('*') + vecteur_Y.find('/')  >= 0 :
            data_vect=[]
            vector_time_Y=""
            TitreY = vecteur_Y
            vector_time_Y, UnitY , dataY = decompose_chaine_operation(vecteur_Y, acqid)
            if vector_time_Y == None :
                Message = "Attention operation " + vecteur_Y + " impossible, temps differents"
                Abandon(Message, gtk.MESSAGE_ERROR)
                break
        else :
            data1=read_vect(acqid, vecteur_Y)
            try :
                if data1 < 0 :
                    continue
            except :
                pass

            if len(data1.data) < 0 :
                if ng == 0 :
                    axg = fig.add_subplot(1,1,1)
                    axes.append(axg)
                flg_read_ok = flg_read_ok + 1
                continue
            else :
                TitreY = vecteur_Y
                vector_time_Y = data1.attributes["ref_time"]
                try :
                    UnitY = data1.attributes["unit"]
                except KeyError:
                    UnitY = "Inconnu"
                dataY = data1.data

        if vector_time_X != vector_time_Y :
                Abandon("Attention vecteurs temps differents : %s et %s" % (vector_time_X, vector_time_Y))

        if UnitY == "mbar" : 
            UnitY = "hPa"

        if UnitY == "degres" : 
            UnitY = "degree"

#        if ng == 0 :
        if UnitY1 == "" : 
            UnitY1 = UnitY
            UnitY2 = ""
            nb_unity = 1
            Titre_UnitY1 = UnitY + " : " + vecteur_Y
            flg_unity = 0

            UnitX1 = UnitX
            UnitX2 = ""
            nb_unitx = 1
            Titre_UnitX1 = UnitX + " : " + vecteur_X
            flg_unitx = 0

            axg = fig.add_subplot(1, 1, 1)
            axes.append(axg)
            axt = axg
        else :
            flg_unitx = -1
            if UnitX != UnitX1 and UnitX != UnitX2 and nb_unitx == 2 :
                print("ALARME : Trop d'unite pour le graphe : Axe X! ")
                break
            if UnitX == UnitX1 :
                Titre_UnitX1 = Titre_UnitX1 + ", " + vecteur_X
                flg_unitx = 0
            elif UnitX == UnitX2 :
                Titre_UnitX2 = Titre_UnitX2 + ", " + vecteur_X
                flg_unitx = 1
            else :
                UnitX2 = UnitX
                Titre_UnitX2 = UnitX2 + " : " + vecteur_X
                nb_unitx = 2
                flg_unitx = 2

            flg_unity = -1
            if UnitY != UnitY1 and UnitY != UnitY2 and nb_unity == 2 :
                print("ALARME : Trop d'unite pour le graphe : Axe Y! ")
                break
            if UnitY == UnitY1 :
                Titre_UnitY1 = Titre_UnitY1 + ", " + vecteur_Y
                flg_unity = 0
                if flg_unitx == 0 :
                    axt = axg
                elif flg_unitx == 1 :
                    axt = axj
                elif flg_unitx == 2 :
                    axj = axg.twiny()
                    axes.append(axj)
                    axt = axj
            elif UnitY == UnitY2 :
                Titre_UnitY2 = Titre_UnitY2 + ", " + vecteur_Y
                flg_unity = 1
                if flg_unitx == 0 :
                    axt = axh
                elif flg_unitx == 1 :
                    axt = axi
                elif flg_unitx == 2 :
                    axi = axh.twiny()
                    axt = axi
            else :
                UnitY2 = UnitY
                Titre_UnitY2 = UnitY2 + " : " + vecteur_Y
                flg_unity = 2
                nb_unity = 2
                if flg_unitx == 0 :
                    axh = axg.twinx()
                    axes.append(axh)
                    axt = axh
                elif flg_unitx == 1 :
                    axt = axh
                    axi = axj.twinx()
                    axes.append(axi)
                    axt = axi
                elif flg_unitx == 2 :
                    axh = axg.twinx()
                    axi = axh.twiny()
                    axes.append(axi)
                    axt = axi

        if flg_unitx == 0 :
            axt.set_xlabel(Titre_UnitX1)
        elif flg_unitx >= 1 :
            axt.set_xlabel(Titre_UnitX2)

        if flg_unity == 0 :
            axt.set_ylabel(Titre_UnitY1)
        elif flg_unity >= 1 :
            axt.set_ylabel(Titre_UnitY2)

        dataX_TMP = npy.array([])
        dataY_TMP = npy.array([])
        for nd in npy.arange(int_dec,int_att) :
            if math.isnan(dataX[nd]) == False and math.isnan(dataY[nd]) == False :
                dataX_TMP = npy.append(dataX_TMP, dataX[nd])
                dataY_TMP = npy.append(dataY_TMP, dataY[nd])

        if len(dataX_TMP) > 0 and len(dataY_TMP) > 0 :
            xmax = max(max(dataX_TMP),xmax)
            xmin = min(min(dataX_TMP),xmin)
            XX=[xmin,xmax]

#            axg.set_xlim(XX)
            legende=vecteur_X + "/" + vecteur_Y

            if car_t == 'S' :
                Taille = LineWidth * LineWidth * LineWidth/20.
#                axt.scatter(dataX_TMP,dataY_TMP,marker='.',s=Taille,color=Colvecteur,label=legende)
                axt.scatter(dataX[int_dec:int_att],dataY[int_dec:int_att],marker='.',s=Taille,color=Colvecteur,label=legende)
            else :
                carac = car_t + Mkvecteur
#                axt.plot(dataX_TMP,dataY_TMP, carac,color=Colvecteur,linewidth=LineWidth, label = legende)
                axt.plot(dataX[int_dec:int_att],dataY[int_dec:int_att], carac,color=Colvecteur,linewidth=LineWidth, label = legende)

            if ( Fonction == "Regression lineaire" ) :
                dataX_TMP = npy.array([])
                dataY_TMP = npy.array([])
                for nd in npy.arange(int_dec,int_att) :
                    if math.isnan(dataX[nd]) == False and math.isnan(dataY[nd]) == False :
                        dataX_TMP = npy.append(dataX_TMP, dataX[nd])
                        dataY_TMP = npy.append(dataY_TMP, dataY[nd])
 
                m, b = polyfit(dataX_TMP, dataY_TMP, 1)

                axt.plot(dataX,m*dataX+b,'-', color=Colvecteur)
            elif ( Fonction == "X=Y" ) :
                axt.plot(dataX,dataX,'-', color=Colvecteur)
            elif ( Fonction == "Y=0" ) :
                axt.axhline(y=0,linestyle='-',linewidth=1., color=Colvecteur)
        else :
            flg_read_ok = flg_read_ok + 1

# Cas d'echelle(s) fixe(s) 

    if flg_read_ok == int(NbGraph) :
        xn, xx = axg.get_xlim()
        topx = xn + (xx - xn)/2
        axg.text(topx, 0.5, 'PAS DE DONNEES', {'color' : 'r', 'fontsize' : 8})

    if ylim[0] != None or ylim[1] != None :
        ymin =  ylim[0]
        ymax =  ylim[1]
        axg.set_ylim(ymin, ymax)

    if ylim[2] != None or ylim[3] != None :
        axg.set_xlim(ylim[2], ylim[3])

#    if UnitY2 != "??" :
#        if ylim[2] != None or ylim[3] != None :
#            ymin =  ylim[2]
#            ymax =  ylim[3]
#            axh.set_ylim(ymin, ymax)


    if Flg_grid == 1 :
        axg.grid(True)
    
    if  flg_Legend == 0 :
        if len(axes) == 1 :
            axg.legend(bbox_to_anchor = (1, 1), loc = 1, borderaxespad = 0., prop = font_legend)
        else :
            axg.legend(bbox_to_anchor = (0, 0), loc = 0, borderaxespad = 0., prop = font_legend)

        try :
            axh.legend(bbox_to_anchor = (1, 0), loc = 4, borderaxespad = 0., prop = font_legend)
        except :
            pass
        try :
            axi.legend(bbox_to_anchor = (1, 1), loc = 4, borderaxespad = 0., prop = font_legend)
        except :
            pass
        try :
            axj.legend(bbox_to_anchor = (0, 1), loc = 4, borderaxespad = 0., prop = font_legend)
        except :
            pass

    plt_f = AIDA.plt_by_abrev[acqid[0:2]]

    if Titre_Graphe != "" :
        Titre= Titre_Graphe 
    else :
        Titre= "Campagne " + Titre_Graphe_defaut + " " + Options.ficapc

    plt.figtext(0.5, 0.980, Titre, ha='center', color='black')
    
    if flg_Titre_Graphe == 0 :
        Titre2 = plt_f.nom_serie_mesure + " " +  plt_f.nom + " "  + acqid + " du " + date_vol_inf.strftime("%d/%m/%Y")
        plt.figtext(0.5, 0.955, Titre2, ha='center', color='black')
        Titre3 = "de " + heure_dec.strftime("%Hh%Mm%S") + " a " +  heure_att.strftime("%Hh%Mm%S") + ' UTC'
        plt.figtext(0.5, 0.930, Titre3, ha='center', color='black')

    if Options.out == 'Ecran' :
        plt.show()
    else :
        if  os.path.isdir(repout) == False :
            Message = "INFO : Dépot du (ou des) fichier(s) résultat(s) dans le répertoire " + repout
            print(Message)
            try :
                os.makedirs(repout)
                os.chmod(repout,0o775)
            except :
                print("ALARME : CREATION REPERTOIRE ECHOUE")
                repout = repout_sec

        Sauvegarde_graphe(acqid, Options, repout, fig)


def Tracer_Trajec(Graphe_Config,acqid, repout,repout_sec, Options) :

    def calculateBasemapTicks(minMaxList, nrOfParalles = 3, nrOfMeridians = 3):
        """
        Attempts to calculate meaningful ranges for .basemap.drawparallels
        and .drawmeridians. Enter a <minMaxList> in the form
        [lng_min, lng_max, lat_min, lat_max]. 
        Note that you might get rather ugly floats. I suggest using formatting
        as in ".drawparallels(..., fmt='%.4f')" or similar.
        """

        pAdjust = (minMaxList[3]-minMaxList[2])*0.1
        mAdjust = (minMaxList[1]-minMaxList[0])*0.1
        parallels = np.linspace(minMaxList[2]+pAdjust,minMaxList[3]-pAdjust,
                            nrOfParalles)
        meridians = np.linspace(minMaxList[0]+mAdjust,minMaxList[1]-mAdjust,
                            nrOfMeridians)
        return parallels, meridians

    axes=[]
    font_legend = FontProperties()
    font_legend.set_size(10)

    try:
        Titre_Graphe = Graphe_Config.get('general_graphe', 'TitreGraph')
        if Titre_Graphe == "None" :
            Titre_Graphe = None
    except configparser.NoOptionError:
        Titre_Graphe = ""
        Abandon("dans [gene_graphe] pas TitreGraph ")

    try:
        flg_Titre_Graphe = Graphe_Config.get('general_graphe', 'Flg_TitreGraph')
    except configparser.NoOptionError:
        flg_Titre_Graphe = 0
        Abandon("dans [gene_graphe] pas Flg_TitreGraphe ")

    try:
        Orient_Page = Graphe_Config.get('general_graphe', 'Orientation')
    except configparser.NoOptionError:
        Abandon("dans [gene_graphe] pas orientation ")

    if Orient_Page == 'Paysage' or  Orient_Page == 'paysage' :
        fig = plt.figure(figsize=(10,8))
    elif Orient_Page == 'Portrait' or Orient_Page == 'portrait':
        fig = plt.figure(figsize=(8,10))
    else :
        dim_page = Orient_Page.split(",")
        fig = plt.figure(figsize=(float(dim_page[0]),float(dim_page[1])))

    try:
        flg_Legend = int(Graphe_Config.get('general_graphe', 'Flg_Legend'))
    except configparser.NoOptionError:
        flg_Legend = 0
        Abandon("dans [gene_graphe] pas Flg_Legend ")

    try:
        Pos_image = Graphe_Config.get('general_graphe', 'PositionImage')[1:-1].split(",")
        for val in npy.arange(4) :
            try :
                Pos_image[val] = float(Pos_image[val])/100
            except :
                Pos_image[val] = None
    except configparser.NoOptionError:
        Pos_image = [None, None, None, None]
#        Abandon("dans [gene_graphe] pas orientation ")

    if Pos_image[1] != None :
        fig.subplots_adjust(right = float(Pos_image[1]))
    elif  flg_Legend == 0 :
        fig.subplots_adjust(right=0.80)
    else :
        fig.subplots_adjust(right=0.95)

    if Pos_image[0] != None :
        fig.subplots_adjust(left = float(Pos_image[0]))
    else :
        fig.subplots_adjust(left=0.08)

    if Pos_image[2] != None :
        fig.subplots_adjust(bottom = float(Pos_image[2])) 
    else :
        fig.subplots_adjust(bottom=0.08)

    if Pos_image[3] != None :
        fig.subplots_adjust(top = float(Pos_image[3]))
    else :
        fig.subplots_adjust(top=0.88)

# Tracer des logos si demande

# logo METEO_FRANCE
    FlgLogoMF = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'FlagLogoMF', var_default="1"))
    if FlgLogoMF == "1" :
        file_image = os.path.join (AH+'/share/common/logos/color_logomet.png')
        imag = image.imread(file_image)
        fig.figimage(imag, 10, 10)

# Autre logo 
    LogoAutre = recup_valeur_config(Graphe_Config, 'general_graphe', 'LogoAutre')
    if LogoAutre != None and  LogoAutre != "":
        file_image = os.path.join (AH + '/share/common/logos/' + LogoAutre)
        try :
            imag = image.imread(file_image)
            fig.figimage(imag, 500, 10)
        except :
            print("WARNING : fichier " + file_image + " inexistant!")
            pass

    try :
        acq_meta = AIDA.Inf(acqid)
    except AIDA.AidaError :
        Message = "\nALARME : Attention Acqid non valid !\n"
        print(Message)
        return

    try :
        date_vol_inf=acq_meta.get_date_acq()
    except :
        Message = "\nALARME : Pas de fichier Inf pour l'acquisition " + acqid + "!\n"
        print(Message)
        return

    try :
        Titre_Graphe_defaut = acq_meta.get_field_value("IDENTIFICATION", "campagne")
    except :
        Titre_Graphe_defaut = ""

    second_vol_inf=date2num(date_vol_inf)

    if Options.deb != None and  Options.deb != "acq":
        heure = Options.deb 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_dec =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_dec = acq_meta.get_horaire('decollage')

    if heure_dec == None or  Options.deb == "acq":
        heure_dec = acq_meta.get_acquisition_borne("debut_acquisition")
    heure_dec_int=date2num(heure_dec)
        
    if Options.fin != None and Options.fin != "acq":
        heure = Options.fin 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_att =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_att = acq_meta.get_horaire('atterrissage')

    if heure_att == None or Options.fin == "acq" :
        heure_att = acq_meta.get_acquisition_borne("fin_acquisition")
    heure_att_int=date2num(heure_att)

    if heure_dec == None or heure_att == None :
        print("PAS HEURES DEBUT ACQUISTION OU FIN ACQUISITION")
        xmin = min (date.data)
        xmax = max (date.data)
    else :
        xmin = date2num(heure_dec)
        xmax = date2num(heure_att)

    try:
        mot_cle = "NomVecteur_lat"
        vecteur_lat = Graphe_Config.get('Trajectoire', mot_cle)
    except configparser.NoOptionError:
        Abandon("dans [Trajectoire] pas %s" % (motcle))

    try:
        mot_cle = "NomVecteur_lon"
        vecteur_lon = Graphe_Config.get('Trajectoire', mot_cle)
    except configparser.NoOptionError:
        Abandon("dans [Trajectoire] pas %s" % (motcle))

    try:
        mot_cle = "NomVecteur_alt"
        vecteur_alt = Graphe_Config.get('Trajectoire', mot_cle)
    except configparser.NoOptionError:
        Abandon("dans [Trajectoire] pas %s" % (motcle))

    try:
        mot_cle = "Dimension"
        DimD = Graphe_Config.get('Trajectoire', mot_cle)
    except configparser.NoOptionError:
        Abandon("dans [Trajectoire] pas %s" % (mot_cle))

    try:
        FlgTop = int(Graphe_Config.get('general_graphe', 'FlgTop'))
    except configparser.NoOptionError:
        Abandon("INFO_APC : dans[SerieTempo] pas de flag top : Pas d affichage")
        FlgTop = 0

    if FlgTop == 1 :
        try :
            data_top = read_vect(acqid, "top_MAIN_0")
            vector_time_top = data_top.attributes["ref_time"]
            date_top = read_vect(acqid, vector_time_top)
            FlgTop = 2
        except :
            try :
                data_top = read_vect(acqid, "topnb_cal_1")
                vector_time_top = data_top.attributes["ref_time"]
                date_top = read_vect(acqid, vector_time_top)
            except :
                print("PAS DE FICHIER DES TOPS")

    try:
        mot_cle = "FlgSupCouleur"
        Flg_sup_couleur = int(Graphe_Config.get('Trajectoire', mot_cle))
    except configparser.NoOptionError:
        Flg_sup_couleur = 0

    if Flg_sup_couleur == 1 :
        try:
            seuils_classe_sup_couleur=[]
            mot_cle = "VecteurSupCouleur"
            vect_sup_couleur = Graphe_Config.get('Trajectoire', mot_cle)
            data_couleur = read_vect(acqid, vect_sup_couleur)

            mot_cle = "NbClasseSupCouleur"
            nb_classe_sup_couleur = int(Graphe_Config.get('Trajectoire', mot_cle))
            mot_cle = "SeuilsClasseSupCouleur"
            seuils_classe_couleur = Graphe_Config.get('Trajectoire', mot_cle)[1:-1].split(",")
            if "None" in seuils_classe_couleur :
                calcul_bornes_sup(seuils_classe_sup_couleur, nb_classe_sup_couleur,data_couleur.data)
            else :
                seuils_classe_sup_couleur = list(map(float, seuils_classe_couleur))
        except configparser.NoOptionError:
            Flg_sup_couleur = 0

    try:
        mot_cle = "FlgSupVent"
        Flg_sup_vent = int(Graphe_Config.get('Trajectoire', mot_cle))
    except configparser.NoOptionError:
        Flg_sup_vent = 0

    try:
        mot_cle = "FlgSupTexte"
        Flg_sup_texte = int(Graphe_Config.get('Trajectoire', mot_cle))
    except configparser.NoOptionError:
        Flg_sup_texte = 0

    if Flg_sup_vent == 1 :
        Flg_vent = 1
        try:
            mot_cle = "VecteurSupVent1"
            vect_sup_vent1 = Graphe_Config.get('Trajectoire', mot_cle)
            mot_cle = "VecteurSupVent2"
            vect_sup_vent2 = Graphe_Config.get('Trajectoire', mot_cle)
            mot_cle = "PeriodeSupVent"
            periode_sup_vent = int(Graphe_Config.get('Trajectoire', mot_cle))
            data_vent1 = read_vect(acqid, vect_sup_vent1)
            if len(data_vent1.data) < 0 :
                print('PROBLEME LECTURE VECTEUR : ', vect_sup_vent1)
                Flg_vent = -1
                Flg_sup_vent = 0 
            else :    
                data_vent2 = read_vect(acqid, vect_sup_vent2)
                if len(data_vent2.data) < 0 :
                    print('PROBLEME LECTURE VECTEUR : ', vect_sup_vent2)
                    Flg_vent = -1
                    Flg_sup_vent = 0 

            if Flg_vent > 0 :
                if vect_sup_vent1[0:5].lower() == 'ven_d' and vect_sup_vent2[0:5].lower() == 'ven_f' :
                    ven_e = []
                    ven_n = []
                    print("CONVERSION DD-FF")
                    for n_pr in npy.arange(len(data_vent1.data)) :
                        ven_e.append(-1.94384449*data_vent2.data[n_pr]*math.sin(data_vent1.data[n_pr]*3.14/180))
                        ven_n.append(-1.94384449*data_vent2.data[n_pr]*math.cos(data_vent1.data[n_pr]*3.14/180))
                else :
                    if data_vent1.attributes["unit"] == "m/s" :
#                        print "CONVERSION EN KT." + ChampSup[0].get_text()
                        print("CONVERSION EN KT." + vect_sup_vent1)
                        ven_e = data_vent1.data * 1.94384449
                    elif data_vent1.attributes["unit"] == "kt" :
                        ven_e = npy.array(data_vent1.data)

                    if data_vent2.attributes["unit"] == "m/s" :
#                        print "CONVERSION EN KT." + ChampSup[1].get_text()
                        print("CONVERSION EN KT." + vect_sup_vent2)
                        ven_n = data_vent2.data * 1.94384449
                    elif data_vent2.attributes["unit"] == "kt" :
                        ven_n = npy.array(data_vent2.data)

        except configparser.NoOptionError:
            Flg_sup_vent = 0

    if Flg_sup_texte == 1 :
        try:
            mot_cle = "VecteurSupTexte"
            vect_sup_texte = Graphe_Config.get('Trajectoire', mot_cle)
            mot_cle = "PeriodeSupTexte"
            periode_sup_texte = int(Graphe_Config.get('Trajectoire', mot_cle))
            data_texte = read_vect(acqid, vect_sup_texte)
        except configparser.NoOptionError:
            Flg_sup_texte = 0


# Lecture des fichiers de donnees

    data_lat=read_vect(acqid,vecteur_lat)
# Lecture fichier temps
    data_lon=read_vect(acqid,vecteur_lon)
    vector_time = data_lon.attributes["ref_time"]

    date_time = read_vect(acqid, vector_time)
    date_data = date_time.data/86400 + second_vol_inf

    int_dec = 0
    int_att = len(date_data)-1
    for i in npy.arange(len(date_data)) :
        if date_data[i] < xmin :
            int_dec = i
        if date_data[i] < xmax :
            int_att = i

    lat_min = 100
    lat_max = -100
    data_lat_max=[]
    for no in arange(len(data_lat.data[int_dec:int_att])) :
        nl = no + int_dec
        if math.isnan(data_lat.data[nl]) == False :
            if data_lat.data[nl] < lat_min : lat_min = data_lat.data[nl]
            if data_lat.data[nl] > lat_max : lat_max = data_lat.data[nl]
    lat_min = lat_min - 0.1
    lat_max = lat_max + 0.1

    for nl in arange(len(data_lat.data)) :
        data_lat_max.append(lat_max)

        data_lon=read_vect(acqid,vecteur_lon)
    lon_min = 181
    lon_max = -181

    data_lon_min=[]
    for no in arange(len(data_lon.data[int_dec:int_att])) :
        nl = no + int_dec
        if math.isnan(data_lon.data[nl]) == False :
            if data_lon.data[nl] < lon_min : lon_min = data_lon.data[nl]
            if data_lon.data[nl] > lon_max : lon_max = data_lon.data[nl]
    lon_min = lon_min - 0.01
    lon_max = lon_max + 0.01
    for nl in arange(len(data_lon.data)) :
        data_lon_min.append(lon_min)

# Lecture fichier temps
    vector_time = data_lon.attributes["ref_time"]

    date_time = read_vect(acqid, vector_time)
    date_data = date_time.data/86400 + second_vol_inf

    int_dec = 0
    int_att = len(date_data)-1
    for i in npy.arange(len(date_data)) :
        if date_data[i] < xmin :
            int_dec = i
        if date_data[i] < xmax :
            int_att = i

    try:
        motcle = "ColorVecteur"
        Colvecteur = Graphe_Config.get('Trajectoire', motcle)
    except configparser.NoOptionError:
        Abandon("dans [Trajectoire] pas %s" % (motcle))
#        continue

    try:
        motcle = "EpaisseurLigne"
        LineWidth = Graphe_Config.get('Trajectoire', motcle)
    except configparser.NoOptionError:
        Abandon("dans [Trajectoire] pas %s" % (motcle))
#        continue

    if DimD == '3D' :
        data_alt=read_vect(acqid,vecteur_alt)
        alt_min = npy.nanmin(data_alt.data[int_dec:int_att])
        alt_max = npy.nanmax(data_alt.data[int_dec:int_att])

        ax1 = Axes3D(fig, xlim=[lon_min, lon_max], ylim=[lat_min, lat_max])
        ax1.set_zlim(bottom=0)

        target_projection = ccrs.PlateCarree()
        
        feature = cfeature.NaturalEarthFeature('cultural', 'admin_0_countries', '10m',edgecolor='green')

        geoms = feature.geometries()

        geoms = [target_projection.project_geometry(geom, feature.crs)
         for geom in geoms]

        paths = list(itertools.chain.from_iterable(geos_to_path(geom) for geom in geoms))

# At this point, we start working around mpl3d's slightly broken interfaces.
# So we produce a LineCollection rather than a PathCollection.
        segments = []
        for path in paths:
            vertice_ok =[]
            vertices = [vertex for vertex, _ in path.iter_segments()]
            vertices = npy.asarray(vertices)
            for nl in npy.arange(len(vertices)) :
                if vertices[nl][0] > lon_min and vertices[nl][0] <  lon_max\
                    and  vertices[nl][1] > lat_min and vertices[nl][1] < lat_max :
                    vertice_ok.append(vertices[nl])
                if (len(vertice_ok)) > 0 :
                    segments.append(vertice_ok)

        lc = LineCollection(segments, color='black')

        ax1.add_collection3d(lc)



#AJOUT POUR CARTE    
#        m = Basemap(projection = 'cyl', llcrnrlon = lon_min-0.5, llcrnrlat = lat_min - 0.5, 
#        urcrnrlon = lon_max+0.5, urcrnrlat = lat_max+0.5, resolution = 'i', ax = ax1)

#        try :
#            ax1.add_collection3d(m.drawcoastlines())
#        except :
#            pass
#        try :
#            ax1.add_collection3d(m.drawcountries())
#        except :
#            pass
#        try :
#            ax1.add_collection3d(m.drawstates())
#            ax1.add_collection3d(m.drawrivers(linewidth=1, color='b'))
#        except :
#            pass
#
#        x, y = m(data_lon.data, data_lat.data)

        ax1.set_xlabel("Longitude")    
        ax1.set_xticks(np.arange(int(lon_min),int( lon_max),1))
        ax1.set_ylabel("Latitude")    
        ax1.set_yticks(np.arange(int(lat_min),int( lat_max),1))
        ax1.set_zlabel("Altitude (m)")    
        ax1.plot(data_lon.data[int_dec:int_att],data_lat.data[int_dec:int_att],zs=0,zdir='z',linestyle='dashed',\
                        color='grey',linewidth=0.5)
        ax1.plot(data_lon.data[int_dec:int_att],data_lat_max[int_dec:int_att],data_alt.data[int_dec:int_att],\
                        linestyle='dashed',color='grey',linewidth=0.5)
        ax1.plot(data_lon_min[int_dec:int_att],data_lat.data[int_dec:int_att],data_alt.data[int_dec:int_att],\
                        linestyle='dashed',color='grey',linewidth=0.5)

        if FlgTop == 1 :
            for idb in np.where(data_top.data[int_dec:int_att] != 0)[0]:
                idx = idb + int_dec
                ax1.text(data_lon.data[idx], data_lat.data[idx], data_alt.data[idx], data_top.data[idx])
                ax1.scatter(data_lon.data[idx], data_lat.data[idx], data_alt.data[idx])
        elif FlgTop == 2: 
            for nt in npy.arange(len(data_top.data)) :
                difference_time = npy.absolute(date_time.data-date_top.data[nt])
                idx = difference_time.argmin()
                if  difference_time[idx] < 1 :
                    res = "{0:016b}".format(int(data_top.data[nt].hex(), 16))
                    top_type = int(str(res)[0:7],2)
                    top_data = int(str(res)[7:16],2)
                    ax1.text(data_lon.data[idx], data_lat.data[idx], data_alt.data[idx], top_data)
                    ax1.scatter(data_lon.data[idx], data_lat.data[idx], data_alt.data[idx])


        if Flg_sup_couleur == 1 :
            SupMin = min(data_couleur.data[int_dec:int_att])
            SupMax = max(data_couleur.data[int_dec:int_att])

            colormap = ['purple','Blue', 'Green', 'Yellow', 'Orange','Red','Brown','Grey']
            deb = int_dec
            nbcolor = nb_classe_sup_couleur
            if data_couleur.data[deb] < seuils_classe_sup_couleur[0] or \
               data_couleur.data[deb] > seuils_classe_sup_couleur[nbcolor] :
                cl = -1
                cl_en_cours = -1
            else :
                for n_classe in npy.arange(1,nbcolor+1) :
                    if data_couleur.data[deb] < seuils_classe_sup_couleur[int(n_classe)] :
                        cl_en_cours = int(n_classe)
                        cl = int(n_classe)
                        colt = colormap[int(cl_en_cours-1)]
                        break

                for npt in npy.arange(int_dec,int_att) :
                    if npy.isnan(data_couleur.data[npt]) == False :
                        if data_couleur.data[npt] < seuils_classe_sup_couleur[0] or \
                               data_couleur.data[npt] > seuils_classe_sup_couleur[nbcolor] :
                            cl = -1
                        else :
                            for n_classe in npy.arange(1,nb_classe_sup_couleur+1) :
                                if data_couleur.data[npt] < seuils_classe_sup_couleur[int(n_classe)] :
                                    cl = int(n_classe)
                                    break
                        if cl != cl_en_cours :
                            if cl_en_cours >= 0 :
                                ax1.plot(data_lon.data[deb:npt], data_lat.data[deb:npt], data_alt.data[deb:npt],\
                                        linewidth = 3, color = colt)
                            cl_en_cours = cl
                            if cl_en_cours >= 0 :
                                colt = colormap[int(cl_en_cours-1)]
                            else :
                                colt = 'white'
                            deb = npt

            if cl_en_cours >= 0 :
                ax1.plot(data_lon.data[deb:int_att], data_lat.data[deb:int_att], data_alt.data[deb:int_att],\
                             linewidth = 3, color = colt)

            for n_classe in npy.arange(nb_classe_sup_couleur) :
                font_txt = FontProperties()
                font_txt.set_size(8)
                text_leg = str(seuils_classe_sup_couleur[int(n_classe)]) + " -> " + \
                           str(seuils_classe_sup_couleur[int(n_classe+1)])
                ax1.plot(data_lon.data[int_att:int_att], data_lat.data[int_att:int_att], data_alt.data[int_att:int_att],\
                            label = text_leg, linewidth = 3, color = colormap[int(n_classe)])
                Titre_legend = vect_sup_couleur + '\n (' + data_couleur.attributes["unit"] + ')'
                ax1.legend(fontsize=8, title = Titre_legend)

        else :
            ax1.set_zlim(0,alt_max)
            ax1.plot(data_lon.data[int_dec:int_att], data_lat.data[int_dec:int_att], data_alt.data[int_dec:int_att],\
                             linewidth = 3, color =Colvecteur )
#            ax1.plot(x,y,data_alt.data,\
#                        label='parametric curve',linewidth=LineWidth, color=Colvecteur)

        if Flg_sup_texte == 1 :
            for n_data in npy.arange(int_dec,int_att,300) :
                ax1.text(data_lon.data[n_data], data_lat.data[n_data],data_alt.data[n_data],int(data_texte.data[n_data]))
            xlabel_texte = "Texte : " + vect_sup_texte + "(" + data_texte.attributes["unit"] + ")"
            if xlabel_texte != "" :
                ax1.text2D(0.05, 0.03,xlabel_texte,transform=ax1.transAxes)

    elif DimD == '2D' :
# Calcul elements fond de carte
        mot_cle = "Flg_2D_Waypoints"
        Flg_2D_Waypoints= int(recup_valeur_config(Graphe_Config, 'general_graphe', mot_cle, var_default="0"))

        mot_cle = "Flg_2D_Fleuves"
        Flg_2D_Fleuves = int(recup_valeur_config(Graphe_Config, 'general_graphe', mot_cle, var_default="0"))

        mot_cle = "Flg_2D_Dep"
        Flg_2D_Dep = int(recup_valeur_config(Graphe_Config, 'general_graphe', mot_cle, var_default="0"))

        mot_cle = "Flg_2D_Relief"
        Flg_2D_Relief = int(recup_valeur_config(Graphe_Config, 'general_graphe', mot_cle, var_default="0"))

        mot_cle = "Flg_2D_TerreMer"
        Flg_2D_TerreMer = int(recup_valeur_config(Graphe_Config, 'general_graphe', mot_cle, var_default="0"))

        if (lat_max - lat_min > lon_max - lon_min) :
            dl = (lat_max - lat_min) - (lon_max - lon_min) + 0.2
            latn = lat_min - 0.1
            latx = lat_max + 0.1
            lonn = lon_min - dl/2
            lonx = lon_max + dl/2
        else :
            dl = (lon_max - lon_min) - (lat_max - lat_min) + 0.2
            latn = lat_min - dl/2
            latx = lat_max + dl/2
            lonn = lon_min - 0.1
            lonx = lon_max + 0.1

# meridians on bottom and left
        ax1 = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        if Flg_2D_TerreMer == 1 :
            print("MASQUE TERRE-MER")
            ax1.add_feature(cfeature.LAND.with_scale('10m'), zorder=1, edgecolor='black', facecolor=cfeature.COLORS['land'])
            ax1.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=1, edgecolor='blue', facecolor=cfeature.COLORS['water'])
        ax1.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor="green")
        ax1.add_feature(cfeature.COASTLINE.with_scale('10m'))
        ax1.gridlines(draw_labels=True, linewidth=0.5, color='grey')
 
        if Flg_2D_Fleuves == 1 :
            ax1.add_feature(cfeature.RIVERS.with_scale('10m'), zorder=1, edgecolor='blue')

        if Flg_2D_Relief == 1 :
            fname = os.path.join(os.getenv('AIDA_HOME'),  'share/common/Cartes/shapefiles/natural_earth/raster', 'HYP_50M_SR.tif')
            ax1.imshow(imread(fname), origin='upper', transform=ccrs.PlateCarree(), extent=[-180, 180, -90, 90])

            ax1.set_extent([lonn, lonx, latn, latx])
            ax1.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=1, edgecolor='blue', facecolor=cfeature.COLORS['water'])

        if Flg_2D_Dep == 1 :
            fond_cartes = os.path.join(os.getenv('AIDA_HOME'), 'share/aidaplot/Cartes/FRA_dep.shp')
            shape_feature = ShapelyFeature(Reader(fond_cartes).geometries(),
                             ccrs.PlateCarree(), edgecolor='black', facecolor=(0,0,0,0))
            ax1.add_feature(shape_feature)

        if Flg_2D_Waypoints == 1 :
            print ("AFFICHAGE POINTS CARACTERISTIQUES")
            for inf_item in acq_meta.iter_items_str('POINTS_CARACTERISTIQUES') :
                wpt = AIDA.PointRep(inf_item=inf_item)
                ax1.plot(wpt.lon, wpt.lat, marker='o')
                ax1.text(wpt.lon, wpt.lat, str(wpt.nom))

        if FlgTop == 1 :
            for idb in np.where(data_top.data[int_dec:int_att] != 0)[0]:
                idx = idb + int_dec
                ax1.text(data_lon.data[idx], data_lat.data[idx], data_top.data[idx])
                ax1.scatter(data_lon.data[idx], data_lat.data[idx])
        elif FlgTop == 2: 
            for nt in npy.arange(len(data_top.data)) :
                difference_time = npy.absolute(date_time.data-date_top.data[nt])
                idx = difference_time.argmin()
                if  difference_time[idx] < 1 :
                    res = "{0:016b}".format(int(data_top.data[nt].hex(), 16))
                    top_type = int(str(res)[0:7],2)
                    top_data = int(str(res)[7:16],2)
                    ax1.text(data_lon.data[idx], data_lat.data[idx], top_data)
                    ax1.scatter(data_lon.data[idx], data_lat.data[idx])

        if Flg_sup_couleur == 1 :
            colormap = ['purple','Blue', 'Green', 'Yellow', 'Orange','Red','Brown','Grey']
            colormap_v = colormap[0:nb_classe_sup_couleur]
            cmap = ListedColormap(colormap_v)
            norm = BoundaryNorm(seuils_classe_sup_couleur, cmap.N)
            points = npy.array([data_lon.data[int_dec:int_att], data_lat.data[int_dec:int_att]]).T.reshape(-1, 1, 2)
            segments = npy.concatenate([points[:-1], points[1:]], axis=1)

            lc = LineCollection(segments, cmap=cmap, norm=norm)
            lc.set_array(data_couleur.data[int_dec:int_att])
            lc.set_linewidth(3)

            ax1.add_collection(lc)

            for n_classe in npy.arange(nb_classe_sup_couleur) :
                font_txt = FontProperties()
                font_txt.set_size(8)
                text_leg = str(seuils_classe_sup_couleur[int(n_classe)]) + " -> " + \
str(seuils_classe_sup_couleur[int(n_classe+1)])
                ax1.plot(data_lon.data[int_att:int_att], data_lat.data[int_att:int_att],\
                            label = text_leg, linewidth = 3, color = colormap[int(n_classe)])
                Titre_legende = vect_sup_couleur + '\n (' + data_couleur.attributes["unit"] + ')'
                ax1.legend(loc=1, fontsize=8, title = Titre_legende)
        else :
            ax1.plot(data_lon.data[int_dec:int_att], data_lat.data[int_dec:int_att],\
                            linewidth = 1.5, color = 'r')
        
        xlabel_texte = ""
        if Flg_sup_texte == 1 :
            for n_data in npy.arange(int_dec,int_att,300) :
                ax1.text(data_lon.data[n_data], data_lat.data[n_data],int(data_texte.data[n_data]))
            xlabel_texte = "Texte : " + vect_sup_texte + "(" + data_texte.attributes["unit"] + ")"

        if Flg_sup_vent == 1 :
            ax1.barbs(data_lon.data[int_dec:int_att:periode_sup_vent], data_lat.data[int_dec:int_att:periode_sup_vent], ven_e[int_dec:int_att:periode_sup_vent],
                            ven_n[int_dec:int_att:periode_sup_vent], length=6, pivot='tip')
            try :
                xlabel_texte = xlabel_texte + "\nVent : " + vect_sup_vent1 + "/" + vect_sup_vent2
            except :
                xlabel_texte = "Vent : " +  vect_sup_vent1 + "/" + vect_sup_vent2

        if xlabel_texte != "" :
            print("ECRITURE LABEL")
#            ax1.set_xlabel(xlabel_texte)

    elif DimD.startswith('2Dv') :

        data_alt=read_vect(acqid,vecteur_alt)
        ax1 = fig.add_axes([0.1, 0.1, 0.8, 0.8])

        if  DimD == "2Dva" :
            data_geo=data_lat.data
            data_txt = "Latitude"
        else :
            data_geo=data_lon.data
            data_txt = "Longitude"

        if FlgTop == 1 :
            for idb in np.where(data_top.data[int_dec:int_att] != 0)[0]:
                idx = idb + int_dec
                ax1.text(data_geo[idx], data_alt.data[idx], data_top.data[idx])
                ax1.scatter(data_geo[idx], data_alt.data[idx])
        elif FlgTop == 2: 
            for nt in npy.arange(len(data_top.data)) :
                difference_time = npy.absolute(date_time.data-date_top.data[nt])
                idx = difference_time.argmin()
                if  difference_time[idx] < 1 :
                    res = "{0:016b}".format(int(data_top.data[nt].hex(), 16))
                    top_type = int(str(res)[0:7],2)
                    top_data = int(str(res)[7:16],2)
                    ax1.text(data_geo[idx], data_alt.data[idx], top_data)
                    ax1.scatter(data_geo[idx], data_alt.data[idx])

        if Flg_sup_couleur == 1 :
            colormap = ['purple','Blue', 'Green', 'Yellow', 'Orange','Red','Brown','Grey']
            colormap_v = colormap[0:nb_classe_sup_couleur]
            cmap = ListedColormap(colormap_v)
            norm = BoundaryNorm(seuils_classe_sup_couleur, cmap.N)
            points = npy.array([data_geo[int_dec:int_att], data_alt.data[int_dec:int_att]]).T.reshape(-1, 1, 2)
            segments = npy.concatenate([points[:-1], points[1:]], axis=1)

            lc = LineCollection(segments, cmap=cmap, norm=norm)
            lc.set_array(data_couleur.data[int_dec:int_att])
            lc.set_linewidth(3)

            ax1.add_collection(lc)

            for n_classe in npy.arange(nb_classe_sup_couleur) :
                font_txt = FontProperties()
                font_txt.set_size(8)
                text_leg = str(seuils_classe_sup_couleur[int(n_classe)]) + " -> " + \
str(seuils_classe_sup_couleur[int(n_classe+1)])
                ax1.plot(data_geo[int_att:int_att], data_alt.data[int_att:int_att],\
                            label = text_leg, linewidth = 3, color = colormap[int(n_classe)])
                Titre_legende = vect_sup_couleur + '\n (' + data_couleur.attributes["unit"] + ')'
                ax1.legend(loc=1, fontsize=8, title = Titre_legende)
        else :
            ax1.plot(data_geo[int_dec:int_att], data_alt.data[int_dec:int_att], linewidth = 1.5, color = 'r')
        
        if Flg_sup_vent == 1 :
            ax1.barbs(data_geo[int_dec:int_att:periode_sup_vent], data_alt.data[int_dec:int_att:periode_sup_vent], ven_e[int_dec:int_att:periode_sup_vent],
                            ven_n[int_dec:int_att:periode_sup_vent], length=6, pivot='tip', flip_barb=False)
            try :
                xlabel_texte = xlabel_texte + "\nVent : " + vect_sup_vent1 + "/" + vect_sup_vent2
            except :
                xlabel_texte = "Vent : " +  vect_sup_vent1 + "/" + vect_sup_vent2

        ax1.set_xlabel(data_txt)
        ax1.grid(True)
        ax1.set_ylabel("Altitude")    
#        ax1.set_xlim(lon_min, lon_max)
#       ax1.set_ylim(lat_min, lat_max)

    plt_f = AIDA.plt_by_abrev[acqid[0:2]]

    if Titre_Graphe != "" :
        Titre= Titre_Graphe 
    else :
        Titre= "Campagne " + Titre_Graphe_defaut + " " + Options.ficapc
    plt.figtext(0.5, 0.970, Titre, ha='center', color='black')

    if flg_Titre_Graphe == 0 :
        Titre2= plt_f.nom_serie_mesure + " " +  plt_f.nom + " "  + acqid + " du " + date_vol_inf.strftime("%d/%m/%Y")
        plt.figtext(0.5, 0.945, Titre2,
                    ha='center', color='black')
        Titre3= "de " + heure_dec.strftime("%Hh%Mm%S") + " a " +  heure_att.strftime("%Hh%Mm%S") + ' UTC'
        plt.figtext(0.5, 0.920, Titre3,
                    ha='center', color='black')

    if Options.out == 'Ecran' :
        plt.show()
    else :
        if  os.path.isdir(repout) == False :
            Message = "INFO : Dépot du (ou des) fichier(s) résultat(s) dans le répertoire " + repout
            print(Message)
            try :
                os.makedirs(repout)
                os.chmod(repout,0o775)
            except :
                print("ALARME : CREATION REPERTOIRE ECHOUE")
                repout = repout_sec

        Sauvegarde_graphe(acqid, Options, repout, fig)


def Tracer_Sondage(Graphe_Config,acqid, repout,repout_sec, Options) :

    def fEw(tt) :
        t = tt + 273.15 
        if tt < 0 :
            result = npy.exp((-6024.5282 / float(t)) + (29.32707) \
                            + (1.0613868  *0.01* float(t)) \
                            - (1.3198825 * 0.00001 * float(t)* float(t)) \
                            - (0.49382577 * math.log(float(t))))
        else  :
            result = npy.exp((-6096.9385 / float(t)) + (21.2409642) \
                            - (2.711193  *0.01* float(t)) \
                            + (1.673952 * 0.00001 * float(t)* float(t))\
                            + (2.433502 * math.log(float(t))))

        return result/100.

    def fCl(t) :
# Chaleur latente de vaporisation a T degres C
        result = 1000. * (2500.9 - 2.365 * t)
        return result

    def tr(x, y):
        x, y = npy.asarray(x), npy.asarray(y)
        return x+y, y

    def inv_tr(x, y):
        x, y = npy.asarray(x), npy.asarray(y)
        return x-y, y

    global NBG

    font_titre = FontProperties()
    font_titre.set_size(10)
    font_graduation = FontProperties(weight='bold')
    font_graduation.set_size(8)
    Pmax = 1050
    Pmin = 100
    flg_T = 0
    flg_Tp = 0
    flg_Tr = 0
    flg_V = 0


# Recuperation information vol

    try :
        acq_meta = AIDA.Inf(acqid)
    except AIDA.AidaError :
        Message = "\nALARME : Attention Acqid non valid !\n"
        print(Message)
        return

    try :
        Titre_Graphe_defaut = acq_meta.get_field_value("IDENTIFICATION", "campagne")
    except :
        Titre_Graphe_defaut = ""

    try :
        date_vol_inf=acq_meta.get_date_acq()
    except :
        Message = "\nALARME : Pas de fichier Inf pour l'acquisition " + acqid + "!\n"
        print(Message)
        return

    second_vol_inf=date2num(date_vol_inf)

    if Options.deb != None and  Options.deb != "acq":
        heure = Options.deb 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_dec =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_dec = acq_meta.get_horaire('decollage')

    if heure_dec == None or  Options.deb == "acq":
        heure_dec = acq_meta.get_acquisition_borne("debut_acquisition")
    heure_dec_int=date2num(heure_dec)
        
    if Options.fin != None and Options.fin != "acq":
        heure = Options.fin 
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        hdeb = hh*3600 + mm*60 + ss
        heure_att =  num2date(second_vol_inf + float(hdeb)/86400)
    else  :
        heure_att = acq_meta.get_horaire('atterrissage')

    if heure_att == None or Options.fin == "acq" :
        heure_att = acq_meta.get_acquisition_borne("fin_acquisition")
    heure_att_int=date2num(heure_att)

    Titre_Graphe = recup_valeur_config(Graphe_Config, 'general_graphe','TitreGraph')
    if Titre_Graphe == None :
        Abandon("dans %s, [SerieTempo] n'a pas de type graphe declare" % (Options.ficapc))

    Orient_Page = recup_valeur_config(Graphe_Config, 'general_graphe','Orientation')
    flg_Titre_Graphe = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'Flg_TitreGraph', var_default="0"))
    flg_Legend = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'Flg_Legend', var_default="0"))
    NbGraph = int(recup_valeur_config(Graphe_Config, 'Sondage', 'NbGraph', var_default="0"))

    if Orient_Page == 'Paysage' or  Orient_Page == 'paysage' :
        fig = plt.figure(figsize=(10,8))
    elif Orient_Page == 'Portrait' or Orient_Page == 'portrait':
        fig = plt.figure(figsize=(8,10))
    else :
        dim_page = Orient_Page.split(",")
        fig = plt.figure(figsize=(float(dim_page[0]),float(dim_page[1])))

    try:
        Pos_image = Graphe_Config.get('general_graphe', 'PositionImage')[1:-1].split(",")
        for val in npy.arange(4) :
            try :
                Pos_image[val] = float(Pos_image[val])/100
            except :
                Pos_image[val] = None
    except configparser.NoOptionError:
        Pos_image = [None, None, None, None]
#        Abandon("dans [gene_graphe] pas orientation ")

    if Pos_image[1] != None :
        fig.subplots_adjust(right = float(Pos_image[1]))
    elif  flg_Legend == 0 :
        fig.subplots_adjust(right=0.80)
    else :
        fig.subplots_adjust(right=0.95)

    if Pos_image[0] != None :
        fig.subplots_adjust(left = float(Pos_image[0]))
    else :
        fig.subplots_adjust(left=0.08)

    if Pos_image[2] != None :
        fig.subplots_adjust(bottom = float(Pos_image[2])) 
    else :
        fig.subplots_adjust(bottom=0.08)

    if Pos_image[3] != None :
        fig.subplots_adjust(top = float(Pos_image[3]))
    else :
        fig.subplots_adjust(top=0.88)

# Tracer des logos si demande

# logo METEO_FRANCE
    FlgLogoMF = int(recup_valeur_config(Graphe_Config, 'general_graphe', 'FlagLogoMF', var_default="1"))
    if FlgLogoMF == "1" :
        file_image = os.path.join (AH+'/share/common/logos/color_logomet.png')
        imag = image.imread(file_image)
        fig.figimage(imag, 10, 10)

# Autre logo 
    LogoAutre = recup_valeur_config(Graphe_Config, 'general_graphe', 'LogoAutre')
    if LogoAutre != None and  LogoAutre != "":
        file_image = os.path.join (AH + '/share/common/logos/' + LogoAutre)
        try :
            imag = image.imread(file_image)
            fig.figimage(imag, 500, 10)
        except :
            print("WARNING : fichier " + file_image + " inexistant!")
            pass

    plt_f = AIDA.plt_by_abrev[acqid[0:2]]

# Ecriture du titre
    if Titre_Graphe != "" :
        Titre= Titre_Graphe 
    else :
        Titre= "Campagne " + Titre_Graphe_defaut + " " + Options.ficapc

    if flg_Titre_Graphe == 0 :
        plt.figtext(0.5, 0.970, Titre, ha='center', color='black')
        Titre2= plt_f.nom_serie_mesure + " " +  plt_f.nom + " "  + acqid + " du " + date_vol_inf.strftime("%d/%m/%Y")
        plt.figtext(0.5, 0.945, Titre2, ha='center', color='black')
        Titre3= "de " + heure_dec.strftime("%Hh%Mm%S") + " a " +  heure_att.strftime("%Hh%Mm%S") + ' UTC'
        plt.figtext(0.5, 0.920, Titre3, ha='center', color='black')
    else :
        plt.figtext(0.5, 0.97, Titre, ha='center', color='black')

    vectorT = recup_valeur_config(Graphe_Config, 'Sondage', "NomVecteurX")
    vectorP = recup_valeur_config(Graphe_Config, 'Sondage', "NomVecteurY")
    vectorTp = recup_valeur_config(Graphe_Config, 'Sondage', "NomVecteurTM")
    vectorTr = recup_valeur_config(Graphe_Config, 'Sondage', "NomVecteurTd")
    vectorV1 = recup_valeur_config(Graphe_Config, 'Sondage', "NomVecteurV1")
    vectorV2 = recup_valeur_config(Graphe_Config, 'Sondage', "NomVecteurV2")
    if vectorT == '' or vectorP == '' or  vectorT == None or vectorP == None:
        Abandon("dans %s, [Sondage] n'a pas assez de data" % (Options.ficapc))
        return

# lecture de donnees

    if vectorP != '' :
        data_P = read_vect(acqid, vectorP)
    if vectorT != '' :
        data_T = read_vect(acqid, vectorT)
        flg_T = 1
    if vectorTp != '' :
        data_Tp = read_vect(acqid, vectorTp)
        flg_Tp = 1
    if vectorTr != '' :
        data_Tr = read_vect(acqid, vectorTr)
        flg_Tr = 1
    if vectorV1 != '' and vectorV2 != '' :
        data_V1 = read_vect(acqid, vectorV1)
        data_V2 = read_vect(acqid, vectorV2)
        flg_V = 1

    data_45 = []
    data_Ec = []
    data_Nc = []
    data_Pc = []

#Recuperation vecteur temps

    vector_time = data_P.attributes["ref_time"]
    date_time = read_vect(acqid, vector_time)

#conversion de temperatures 
    
    pas_vent = 300
    for n_pr in npy.arange(len(data_P.data)) :
        if npy.mod(n_pr, pas_vent) == 0 :
            data_Pc.append(data_P.data[n_pr])
            data_45.append(int(45))
            if vectorV1.lower().startswith("ven_e") and vectorV2.lower().startswith("ven_n") :

                data_Ec.append(data_V1.data[n_pr])
                data_Nc.append(data_V2.data[n_pr])
            elif vectorV1.lower().startswith("ven_d") and vectorV2.lower().startswith("ven_f") :

                data_Ec.append(-1*data_V2.data[n_pr]*math.sin(data_V1.data[n_pr]*3.14/180))
                data_Nc.append(-1*data_V2.data[n_pr]*math.cos(data_V1.data[n_pr]*3.14/180))
            elif  vectorV1 != '' or vectorV2 != '' :
                Message = "ALARME : Choix incoherent pour le vent\n choisir DD et FF ou u et v !"
                print(Message)
                return

        pr = data_P.data[n_pr]
        Prop = ((math.log(Pmax, 10) - math.log (pr, 10))/(math.log(Pmax, 10) - math.log (Pmin, 10)))
        if flg_T == 1 :
            data_T.data[n_pr] = data_T.data[n_pr] + 90 * Prop
        if flg_Tp == 1 :
            data_Tp.data[n_pr] = data_Tp.data[n_pr] + 90 * Prop
        if flg_Tr == 1 :
            data_Tr.data[n_pr] = data_Tr.data[n_pr] + 90 * Prop

    grid_helper = GridHelperCurveLinear((tr, inv_tr))

    ax = Subplot(fig, 1, 1, 1, grid_helper = grid_helper)
    fig.add_subplot(ax)

# Trace des Isobares
# ------------------

    Tmax = 50.
    Tmin = -20.
#    ax.set_aspect("auto", adjustable = "box-forced")
    ax.set_xlim(Tmin, Tmax)
    ax.set_ylim(0, 90)
    ax.axis["left"].toggle(ticklabels = False)
#    ax.axis["bottom"].major_ticklabels.set_color("y")
    majorLocator   = MultipleLocator(10)
    majorFormatter = FormatStrFormatter('%d')
    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_major_formatter(majorFormatter)
    ax.grid(False, axis = 'y')

    ax2 = ax.twinx()
    ax2.semilogy()
    ax2.set_aspect("auto", adjustable = "box")
    ax2.set_xlim(Tmin, Tmax)
    ax2.set_ylim(1050, 100)

    majorLocator   = MultipleLocator(100)
    majorFormatter = FormatStrFormatter('%d')
    ax2.yaxis.set_major_locator(majorLocator)
    ax2.yaxis.set_major_formatter(majorFormatter)

    ax2.grid(True, axis = 'y')



# Trace des Isothermes
# --------------------
    x2 = npy.arange(140) -90
    l_te = x2[:140, npy.newaxis]
    l_pr = [100, 1050]
    segs = npy.zeros((len(l_te), 2, 2), float)
    segs[:, :, 1] = l_pr
    segs[:, :, 0] = l_te 

# Pente des temperatures
    for nt in l_te :
        r = l_te[nt] + 90 
        segs[int(nt):int(nt+1), 0, 0] = r

#                                linewidths    = (1, 0.3, 0.3, 0.3, 0.3, 0.7, 0.3, 0.3, 0.3, 0.3),  \
    line_segments = LineCollection(segs,  \
                                linewidths    = (1, 0, 0, 0, 0, 0, 0, 0, 0, 0),  \
                                colors        = 'y',  \
                                linestyle = 'solid')
    ax2.add_collection(line_segments)

# Trace des IsoRw
# ---------------
    k622 = 621.98       # 1000 * rapport masses molaires vapeur/air sec
    l_rw = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 1.2, 1.4, 1.6, \
            1.8, 2, 2.2, 2.4, 2.6, 2.8, 3, 3.5, 4, 4.5, 5, 6, 7, 8, 9, 10, \
            12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40]
    l_trw = [0.5, 1, 2, 3, 4, 5, 10, 20]
    l_pr = [200, 1050]
    segs = npy.zeros((len(l_rw), 2, 2), float)
    segs[:, :, 1] = l_pr
    Prop = ((math.log(Pmax, 10) - math.log (200, 10))/(math.log(1050, 10) \
                    - math.log (100, 10)))

    for npr in npy.arange(len(l_pr)):
        for nt in npy.arange(len(l_rw)) :
            rw622 = float(l_rw[nt])/(float(l_rw[nt]) + k622)
            val = math.log((float(l_pr[npr]) * rw622/6.107), 10)/math.log(10, 10)
            trw = 237.3 * val/(7.45 - val)
            if npr == 0 :
                trw = trw + 90 * Prop
            segs[nt:nt+1, npr, 0] = trw

    for nt in npy.arange(len(l_trw)) :
        rw622 = float(l_trw[nt])/(float(l_trw[nt]) + k622)
        val = math.log((690 * rw622/6.107), 10)/math.log(10, 10)
        trw = 237.3 * val/(7.45 - val)
        f_txt =  trw + 16.5
        ax2.text(f_txt, 690, l_trw[nt],
                rotation=20,
                weight=8,
                color='y',
                horizontalalignment='center',
                verticalalignment='bottom',
                fontproperties = font_graduation)



#    ep_rw = [1, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, \
#             1, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 1, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1, \
#             0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1]
    ep_rw = [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, \
             1, 0.0, 0.0, 0.0, 0.0, 1, 0.0, 1, 0.0, 1, 0.0, 0.0, 0.0, 0.0, 1, \
             0.0, 0.0, 0.0, 0.0, 1, 0.0, 0.0, 0.0, 0.0, 1, 0.0, 0.0, 0.0, 0.0, 1]
    line_segments = LineCollection(segs, 
                                linewidths    = ep_rw, 
                                colors        = 'y', 
                                linestyle = 'dashed')
    ax2.add_collection(line_segments)


# Trace des IsoThetaW
# -------------------

    t0 = 273.15
    pui = 2./7.
    l_t2 = npy.arange(-30, 155, 5)
    l_p2 = npy.arange(1050, 99, -50)

    segs = npy.zeros((len(l_t2), len(l_p2), 2), float)
    segs[:, :, 1] = l_p2
    for npr in npy.arange(len(l_p2)):
        Prop = ((math.log(Pmax, 10) \
                        - math.log (l_p2[npr], 10))/(math.log(Pmax, 10) \
                        - math.log (Pmin, 10)))
        for nt in npy.arange(len(l_t2)) :
            IsoT = (l_t2[nt] + t0)/math.pow((1000/float(l_p2[npr])), pui)
            IsoT = IsoT - t0 + 90 * Prop
            segs[nt:nt+1, npr, 0] = IsoT

            if l_t2[nt] >= 0 and l_t2[nt] < 80 and npy.mod(l_t2[nt], 10) == 0 and l_p2[npr] == 550 :
                ax2.text(IsoT-1, l_p2[npr],l_t2[nt], 
                    rotation=-40,
                    weight=8,
                    color='g',
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    fontproperties = font_graduation)


#                                linewidths    = (1, 0.5), 
    line_segments = LineCollection(segs, 
                                linewidths    = (1, 0.0), 
                                colors        = 'g', 
                                linestyle = 'solid')
    ax2.add_collection(line_segments)

# Trace des IsoThetaPW
# -------------------

    t0 = 273.15
    k622 = 621.98
    kRa = 287.049
    kCpa = 1004.671
    deb = -80

    ra622 = k622/kRa/1000.
    cpa622 = kCpa/k622*1000.

    l_t1 = npy.arange(-40, 34, 2)
    l_t2 = npy.arange(deb, 50, 5)
    segs = npy.zeros((len(l_t1), len(l_t2), 2), float)

    n_teta = -1

    for teta in l_t1 :
        n_teta = n_teta + 1
        teta_k = teta + t0
        Ew_teta = fEw(teta)
        Ew_teta1000 = 1000. - Ew_teta
        R_teta = Ew_teta / Ew_teta1000 * float(fCl(teta)) / teta_k

        n_t = -1

        for tt in l_t2 :
            n_t = n_t + 1
            t_k = tt + t0
            Ew_t = float(fEw(tt))
            rt1 = Ew_t * float(fCl(tt))/t_k
            tlog = float(math.log(t_k/teta_k))
            rt2 = 4180. * tlog * (Ew_t + Ew_teta)
            rt = ra622 * ( cpa622 * tlog - R_teta)
            p = Ew_teta1000 + npy.exp(float(rt))
            for i in npy.arange(1, 30, 1) :
                pp = rt + ra622 * (rt2/(Ew_teta1000 + p) + rt1 / float(p))
                p = Ew_teta1000 * npy.exp(pp)
            press = p + Ew_t

            Prop = ((math.log(Pmax, 10) \
                            - math.log (press, 10))/(math.log(Pmax, 10) \
                            - math.log (Pmin, 10)))
            segs[n_teta:n_teta+1, n_t:n_t+1, 0] = tt + 90 * Prop
            segs[n_teta:n_teta+1, n_t:n_t+1, 1] = press

            if teta >= -10 and npy.mod(teta, 10) == 0 and tt == -30 :
                ax2.text(tt+90*Prop, press, teta,
                    rotation=-70,
                    weight=8,
                    color='g',
                    horizontalalignment='center',
                    verticalalignment='bottom',
                    fontproperties = font_graduation)


#                                linewidths    = (1, 0.5, 0.5, 0.5, 0.5), 
    line_segments = LineCollection(segs, 
                                linewidths    = (1, 0, 0, 0, 0), 
                                colors       = 'g', 
                                linestyle = 'dashed')
    ax2.add_collection(line_segments)

# conversion hhmmss en seconde
    if heure_dec == None or heure_att == None :
        print("PAS HEURES DEBUT ACQUISTION OU FIN ACQUISITION")
        xmin = min (date_time.data)
        xmax = max (date_time.data)
    else :
        xmin = date2num(heure_dec)
        xmax = date2num(heure_att)

    int_dec = 0
    int_dec2 = 0
    int_att = len(date_time.data)-1
    int_att2 = int_att/pas_vent

    for i in npy.arange(len(date_time.data)) :
        if date_time.data[i] < (heure_dec_int - second_vol_inf ) *86400 :
            int_dec = i
            int_dec2 = int(i/pas_vent)
        if date_time.data[i] < (heure_att_int - second_vol_inf ) *86400 :
            int_att = i
            int_att2 = int(i/pas_vent)

# tracer data

    ax2.plot(data_T.data[int_dec:int_att], data_P.data[int_dec:int_att], \
                    color = 'red', label = vectorT, linewidth = 2)
    if flg_Tp == 1 :
        ax2.plot(data_Tp.data[int_dec:int_att], data_P.data[int_dec:int_att], \
                        color = 'Blue', label = vectorTp, linewidth = 2)
    if flg_Tr == 1 :
        ax2.plot(data_Tr.data[int_dec:int_att], data_P.data[int_dec:int_att], \
                        color = 'cyan', label = vectorTr, linewidth = 2)

    if flg_V == 1 :
        ax2.barbs(data_45[int_dec2:int_att2], data_Pc[int_dec2:int_att2], \
                        data_Ec[int_dec2:int_att2], data_Nc[int_dec2:int_att2], \
                        length = 8, pivot = 'tip', label = 'Vent ', color = 'black')

    if flg_Legend == 0 :
        ax2.legend(bbox_to_anchor = (1, 1), loc = 2, borderaxespad = 0., prop = font_titre, edgecolor = "black")

    try:
        motcle = "EchellesAxe"
        AxeLim = Graphe_Config.get('Sondage', motcle)[1:-1].split(",")
        for val in npy.arange(4) :
            try :
                AxeLim[val] = float(AxeLim[val])
            except :
                AxeLim[val] = None

        ax2.set_ylim(AxeLim[0], AxeLim[1])
        ax2.set_xlim(AxeLim[2], AxeLim[3])

    except configparser.NoOptionError:
        AxeLim = [None, None, None, None]

#        if acqid[0:2] == "as" :
#	    print acqid[0:2],"ATR"
#            ax2.set_ylim(1050, 300)
#            ax2.set_xlim(0, 50)
#        else :
#	    print acqid[0:2],"FALCON"
#            ax2.set_ylim(1050, 100)
#            ax2.set_xlim(-10, 50)

    if Options.out == 'Ecran' :
        plt.show()
        print("Sortie ECRAN ")
    else :
        if  os.path.isdir(repout) == False :
            Message = "INFO : Dépot du (ou des) fichier(s) résultat(s) dans le répertoire " + repout
            print(Message)
            try :
                os.makedirs(repout)
                os.chmod(repout,0o775)
            except :
                print("ALARME : CREATION REPERTOIRE ECHOUE")
                repout = repout_sec

        Sauvegarde_graphe(acqid, Options, repout, fig)

def Sauvegarde_graphe(acqid, Options, repout, fig) : 
    FormatOut = Options.fout
    if  FormatOut == None :
        FormatOut="pdf png"

    if Options.out== 'Fichier' :
        nom_fic_out =  acqid + '-' + Options.ficapc
    else :
        nom_fic_out =  acqid + '-' + Options.out

    print("INFO : FormatOut = " + FormatOut)
    L_format = FormatOut.split(" ")
    for nbv in arange(len(L_format)) :
        if  L_format[nbv] == 'pdf' :
            nom_fic_pdf = nom_fic_out + '.pdf'
            file_sortie = os.path.join (repout, nom_fic_pdf)
            print("INFO : Ecriture fichier PDF :",file_sortie)
            pdf = PdfPages(file_sortie)
            savefig(pdf, format='pdf')
            close()
            pdf.close()
        else :
            nom_fic_out2 = nom_fic_out + '.' + L_format[nbv]
            file_sortie = os.path.join (repout, nom_fic_out2)
            print("INFO : Ecriture fichier ",L_format[nbv]," ",file_sortie)
            try :
                print(L_format[nbv])
                fig.savefig(file_sortie, format= L_format[nbv], dpi = 300)
            except ValueError:
                print("Format de sortie ",L_format[nbv], " inconnu!!")
                print("Formats reconnus : emf, eps, jpeg, jpg, pdf, png,\
 ps, raw, rgba, svg, svgz, tif, tiff")

class Abandon(Exception):
    """ Un message pour arreter le travail lorsqu'il n'y a
        rien d'autre de possible.

    Attributs:
        msg  -- explication sur l'erreur

    """
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg
        print(msg)



def main(argv=None):


# Récupération des arguments

    fmt_help = IndentedHelpFormatter(indent_increment=4,max_help_position=40, width=80, short_first=False)
    usage = "usage: %prog -i nom_fichier_apc -a acq_id [options]\n   ou \n\
%prog nom_fichier_apc acq_id"
    parser = OptionParser(usage=usage, add_help_option=True, formatter=fmt_help)

    parser.add_option("-a", "--acq_id", dest="acq_id", type='string',
                  help="Identification acquisition")
    parser.add_option("-i", "--in", dest="ficapc", type='string',
                  help="Nom du fichier apc")
    parser.add_option("-d", "--dest", dest="dest", type='string', default = None,
                    help="Répertoire de dépot du graphique élaboré.")
    parser.add_option("-o", "--out", dest="out", type='string', default = None,
                    help="\"Ecran\" ou nom du fichier de sortie sans extension.")
    parser.add_option("-f", "--format", dest="fout", type='string', default = None,
                    help="formats de sortie : ps png gif pdf...")
    parser.add_option("-s", "--seq", dest="seq", type='string', default = None,
                    help="nom de la séquence horaire dans le fichier inf, prioritaire sur les options -b et -f")
    parser.add_option("-b", "--deb", dest="deb", type='string', default = None,
                    help="heure du début du tracé YYMMSS")
    parser.add_option("-g", "--fin", dest="fin", type='string', default = None,
                    help="heure du fin du tracé YYMMSS")

    (options, args) = parser.parse_args()

    if len(args) == 2 :
        options.acq_id = args[1]
        options.ficapc = args[0]

# Récupération de l'acqid (Obligatoire)
    if options.acq_id == None :
        parser.error('Argument -a acq_id obligatoire!')
    else :
        acq_id = options.acq_id

# Récupération fichier de config du graphique .apc (Obligatoire)
    if options.ficapc == None :
        parser.error('Argument -i nom_fichier_apc obligatoire!')
    else :
        ficapc = options.ficapc

    if ficapc[-4:] != '.apc' :
        ficapc = ficapc + '.apc'
    

# Recherche du fichier de config du graphique .apc
# fichier dans le répertoire de travail
    fic_config1 = os.path.join ('.', ficapc) 
# fichier dans le répertoire local grafdef
    fic_config2 = os.path.join (AH+'/local/grafdef', ficapc)
# fichier dans le répertoire public grafdef
    fic_config3 = os.path.join (AH+'/appli/grafdef', ficapc)

    if os.path.isfile(fic_config1) :
        fic_config = fic_config1
        rep_out_sec = os.path.dirname(fic_config)
    elif os.path.isfile(fic_config2) :
        fic_config = fic_config2
        rep_out_sec = os.path.join (AH+'/local/grafout')
    elif os.path.isfile(fic_config3) :
        fic_config = fic_config3
        rep_out_sec = os.path.join (AH+'/appli/grafout')
    else :
        print('ALARME : FICHIER ' + ficapc + ' INEXISTANT ')
        return 2
        
    print('INFO : Fichier apc utilise ' + fic_config)

# Récupération répertoire de dépot des fichiers résultats (Facultatif)
    if options.dest != None :
        if  os.path.isdir(options.dest) == False :
            Message = "\nINFO :  Le répertoire de destination " + options.dest + " n'existe pas!\n"
            print(Message)
            rep_out = os.path.dirname(fic_config).replace("grafdef","grafout")
        else :
            rep_out = options.dest
    else : 
        rep_out = os.path.dirname(fic_config).replace("grafdef","grafout")

    Message = "INFO : Dépot du (ou des) fichier(s) résultat(s) dans le répertoire " + rep_out
    print(Message)

# Lecture du fichier config du graphique.
    Graphe_cfg = configparser.RawConfigParser()
    Graphe_cfg.read(fic_config)
    Type_Graphe=""

    for balise in Graphe_cfg.sections():
        if balise == 'general_graphe':
            try:
                Type_Graphe = Graphe_cfg.get(balise, 'TypGraph')
                continue
            except configparser.NoOptionError:
                Abandon("dans %s, %s n'a pas de type graphe declare" % (fic_config, balise))
                break

        if balise != Type_Graphe :
            Abandon("Incoherence entre TypGraph (%s) et balise (%s) dans %s" % (Type_Graphe,balise, fic_config))
            break

# Modification des données du fichier en fonction des arguments de lancement.
# Modification de la sortie

    if options.out == None :
        options.out =  Graphe_cfg.get('general_graphe', 'Destination')
        try :
            options.fout =  Graphe_cfg.get('general_graphe', 'FormatOut')
        except configparser.NoOptionError :
            options.fout = 'pdf png'
    elif options.out == "Imprimante" :
        options.fout =  "ps"
    elif options.out != "Ecran" :
        if options.fout == None :
            print("Preciser le format désiré avec l'option -f.")
            return

# Initialiasation des heures de début et fin des données utlisées si option sequence.
    try :
        acq_meta = AIDA.Inf(acq_id)
    except AIDA.AidaError :
        Message = "\nALARME : Attention Acqid non valid !\n"
        print(Message)
        return

    for (typ, seq) in acq_meta.iter_items_str('SEQUENCES') :
        print(options.seq)
        champs = seq.split('/')
        if champs[0] == options.seq :
            options.deb = champs[1]
            options.fin = champs[2]

    if Type_Graphe  == 'SerieTempo' :
        Tracer_SerieTempo(Graphe_cfg,acq_id,rep_out, rep_out_sec, options)

    if Type_Graphe  == 'Plot_XY' :
        Tracer_XY(Graphe_cfg,acq_id,rep_out, rep_out_sec, options)

    if Type_Graphe  == 'Trajectoire' :
        Tracer_Trajec(Graphe_cfg,acq_id,rep_out, rep_out_sec, options)

    if Type_Graphe  == 'Sondage' :
        Tracer_Sondage(Graphe_cfg,acq_id,rep_out, rep_out_sec, options)

    if Type_Graphe  == 'Dsp' :
        Tracer_dsp(Graphe_cfg,acq_id,rep_out, rep_out_sec, options)

if __name__ == "__main__" :
    sys.exit(main())

