#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Ce module rassemble des outils (fonctions, classes) pour
    tracer les graphiques aidaplot.
    il utilise la bibliothèque graphique MATPLOTLIB.
"""

import os, sys
try :
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except Exception:
    print("Attention problème chargement GTK 3", file=sys.stderr)

import math
import matplotlib
import numpy as npy
import re
import time 
import itertools

from matplotlib.dates import DateFormatter, num2date, date2num
from matplotlib.figure import Figure
import matplotlib.mlab as ml 
from matplotlib.image import imread

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature
from cartopy.io.shapereader import Reader
from cartopy.mpl.patch import geos_to_path
import cartopy.io.img_tiles as cimgt


import cartopy
cartopy.config['data_dir'] =  os.path.join(os.getenv('AIDA_HOME'),  'share/common/Cartes')
cartopy.config['pre_existing_data_dir'] = os.path.join(os.getenv('AIDA_HOME'),  'share/common/Cartes')

import logging
mpl_logger = logging.getLogger("matplotlib")
mpl_logger.setLevel(logging.WARNING)

#from scipy import  stats
#from pylab import *
import scipy.signal as signal

from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
#from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas


from matplotlib.widgets import RectangleSelector
from matplotlib.patches import Rectangle
from matplotlib.collections import PolyCollection, LineCollection
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, AutoMinorLocator
from matplotlib.font_manager import FontProperties
from matplotlib.image import NonUniformImage
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Polygon

from mpl_toolkits.mplot3d import Axes3D

if matplotlib.__version__ > '1.0.0' :
    from mpl_toolkits.axisartist.grid_helper_curvelinear import GridHelperCurveLinear
    from mpl_toolkits.axisartist import Subplot
else :
    from mpl_toolkits.axes_grid.grid_helper_curvelinear import GridHelperCurveLinear

PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))
import AIDA
import cfunits as cf

global Config_Couleur
Config_Couleur = {0:"Blue", 1:"Green", 2:"Red", 3:"Cyan", 4:"Orange", \
                    5:"Brown", 6:"Yellow", 7:"Grey", 8:"Black", 9:"Purple"}



class Abandon(Exception):
    """ Une exception pour arrêter le travail lorsqu'il n'y a
        rien d'autre de possible.

    Attributs:
        msg  -- explication sur l'erreur

    """
    def __init__(self, msg, Type):
        dialog = Gtk.MessageDialog(
        None, 0,
            Type,
            Gtk.ButtonsType.CLOSE,
            msg)
        dialog.run()
        dialog.destroy()
        Exception.__init__(self, msg)
        self.msg = msg


class SnaptoCursor:
    """
    Like Cursor but the crosshair snaps to the nearest x, y point
    For simplicity, I'm assuming x is sorted
    """
    def __init__(self, axes, x, y, bn_canvas, ngv):
        self.canvas = bn_canvas
        fig = self.canvas.get_nth_page(0)
#        fig.toolbar = self
        self.ly = [ ax.axvline(color = 'k') for ax in axes]  # the vert line
        self.x = x
        self.y = y
        # text location in axes coords
        font_txt = FontProperties()
        font_txt.set_size(10)
        decal_ly = -0.3 * ngv + 0.2
        self.txt = [ ax.text(1.07, decal_ly, '', transform = ax.transAxes, fontproperties = font_txt) for ax in axes]
        self.idco = 0
        fig.draw()

    def mouse_move(self, event, l_axes, IHM):
        """ Affichage de l'heure et des valeurs au niveau du 
            curseur pour l'ensemble des courbes séries.
        """

        if not event.inaxes: return

        x, y = event.xdata, event.ydata

        na = -1
        nb = -1
        axtmp = 'None'
        txt_tmp = ""
        for nb in npy.arange(len(self.ly)) :
            try :
                indx = npy.searchsorted(self.x[nb], [x])[0]
                x = self.x[nb][indx]
                x1 = self.x[nb][indx-1]
            except IndexError :
                break

# Choix affichage date a la seconde ou plus precis
# si frequence < 1hz affichage en seconde
# sinon affichage millieme de seconde
# 1/86400 = 0,000011574
            if ( x - x1 ) < 0.00001 :
                format_date = '%Hh%Mmn%S.%fs'
            else :
                format_date = '%Hh%Mmn%Ss'

            if IHM.graph_gene.unit_temp == "Heure" :
                heureX = num2date(x).strftime(format_date)
            else :
                heureX = num2date(700000 + x/86400).strftime(format_date)
            self.ly[nb].set_xdata(x)
            y = self.y[nb][indx]
            if axtmp != "None" :
                na = na + 1
                txt_tmp = txt_tmp + "\ny" + str(na) + " = " + str(y)
            else :
                if nb >= 1 :
                    self.txt[nb-1].set_text(txt_tmp)
                na = 0
                txt_tmp = heureX
                txt_tmp = txt_tmp + "\ny" + str(na) + " = " + str(y)
                axtmp = l_axes[nb]

        if nb >= 0 and len(txt_tmp) > 5 :
            self.txt[nb].set_text(txt_tmp)

        nb = self.canvas.get_current_page()
        fig = self.canvas.get_nth_page(nb)
        fig.draw()
        fig.grab_focus()

    def update(self) :
        pass

def ajuste_axe_y (ax) :
    ax_select = []
    gr_ax = None
    ylim = npy.inf, -npy.inf
    nbgr = 0

    for nba in npy.arange(len(ax)) :
        if ax[nba].get_geometry() != gr_ax :
            ax_select.append(ax[nba])
            gr_ax = ax[nba].get_geometry()
            Num_gr = nbgr

    xlim = ax_select[0].get_xlim()
    
    for nba in npy.arange(0, len(ax_select)) :
        ylim = npy.inf, -npy.inf
        for nbl in npy.arange(len(ax_select[nba].lines)) :
            l = ax_select[nba].lines[nbl]
            x, y = l.get_data()
            try :
               if len(x) < 3 :
                   pass
            except : 
                break

            if len(x) > 3 :
               start, stop = npy.searchsorted(x, xlim)
               yc = y[max(start-1, 0):(stop+1)]
               ylim = min(ylim[0], npy.nanmin(yc)), max(ylim[1], npy.nanmax(yc))
               diff = max(ylim) - min(ylim)
               if diff != 0.0 :
                   ymax = max(ylim) + diff * 0.1
                   ymin = min(ylim) - diff * 0.1
                   ax_select[nba].set_ylim(ymin, ymax)

def key_press(event, ax, fig, cursor, IHM):
    """
        Code des raccourcis clavier utilisables sur les graphiques.
    """

# switching on/off a grid in current axes (default key 'g')
    if event.key in ['G', 'g']:
        event.inaxes.grid()
        fig.canvas.draw()

# Activation ou désactivation du curseur sur les graphes.
    if event.key in ['D', 'd'] and cursor != None :
        if cursor.idco != 0 :
            print (' désactive cursor.')
            fig.canvas.mpl_disconnect(cursor.idco)
            for nb in npy.arange(len(cursor.ly)) :
                cursor.ly[nb].set_visible(False)
                cursor.txt[nb].set_text(" ")
                cursor.idco = 0
            fig.canvas.draw()
        else :
            print (' active cursor.')
#            cursor.idco = fig.canvas.mpl_connect('motion_notify_event', lambda e1:cursor.mouse_move(e1, ax))
            cursor.idco = 0
            for nb in npy.arange(len(cursor.ly)) :
                cursor.ly[nb].set_visible(True)
            fig.canvas.draw()

# Augmentation de la taille du graphe
    if event.key in ['+']:
        hf, wf = fig.get_size_inches()
        hf2 = hf*1.1
        wf2 = wf*1.1
        hc, wc = fig.canvas.get_size_request()
        hc2 = round(hc*1.1)
        wc2 = round(wc*1.1)
        fig.set_size_inches(hf2, wf2)
        fig.canvas.set_size_request(hc2, wc2)
        fig.canvas.draw()

# Diminution de la taille du graphe
    if event.key in ['-']:
        hf, wf = fig.get_size_inches()
        hf2 = hf/1.1
        wf2 = wf/1.1
        hc, wc = fig.canvas.get_size_request()
        hc2 = round(hc/1.1)
        wc2 = round(wc/1.1)
        fig.set_size_inches(hf2, wf2)
        fig.canvas.set_size_request(hc2, wc2)
        fig.canvas.draw()

    if event.key in ['P', 'p']:
        if IHM != None :
            print(IHM.graph_gene.E_xmin.get_text())
            print(IHM.graph_gene.E_xmax.get_text())
            print(event.inaxes.get_xlim())

# Ajustement optimal de l'axe X.
    if event.key in ['X', 'x']:
        print("AJUSTEMENT DES GRAPHES AXES X")

        ax_select = []
        gr_ax = None
        nbgr = 0
        for nba in npy.arange(len(ax)) :
            if ax[nba].get_geometry() != gr_ax :
                ax_select.append(ax[nba])
                gr_ax = ax[nba].get_geometry()
                Num_gr = nbgr

        xlim = ax_select[0].get_xlim()
        for nba in npy.arange(0, len(ax_select)) :
            xlm = npy.inf, -npy.inf
            for nbl in npy.arange(len(ax_select[nba].lines)) :
                l = ax_select[nba].lines[nbl]
                x, y = l.get_data()
                if len(x) < 3 :
                    break
                xlm = min(x), max(x)
                ax_select[nba].set_xlim(xlm)

# Ajustement optimal de l'axe Y.
    if event.key in ['Y', 'y']:
        ajuste_axe_y(ax)


# Ajustement manuel de l'axe Y.
    if event.key in ['C', 'c'] :

        print("C")
        ax_select = []
        gr_ax = ax[0].get_geometry()
        nbgr = 0
        for nba in npy.arange(len(ax)) :
            if ax[nba].get_geometry() != gr_ax :
                nbgr = nbgr + 1
                gr_ax = ax[nba].get_geometry()

            if ax[nba].get_geometry() == event.inaxes.get_geometry() :
                ax_select.append(ax[nba])
                Num_gr = nbgr

        ymn1, ymx1 = ax_select[0].get_ylim()
        xmn1, xmx1 = ax_select[0].get_xlim()
        unit1 = ax_select[0].get_ylabel()
        unit3 = ax_select[0].get_xlabel()
        ax0 = ax_select[0]
        ax1 = None
        ymn2 = ""
        ymx2 = ""
        xmn2 = ""
        xmx2 = ""
        flg_axe_droit = 0
        flg_axe_haut = 0
        for nba in npy.arange(1, len(ax_select)) :
            if ax_select[nba].get_ylabel() != unit1 :
                ymn2, ymx2 = ax_select[nba].get_ylim()
#                unit2 = ax_select[nba].get_ylabel()
                ax1 = ax_select[nba]
                flg_axe_droit = 1
            if ax_select[nba].get_xlabel() != unit3 :
                xmn2, xmx2 = ax_select[nba].get_xlim()
                ax1 = ax_select[nba]
                flg_axe_haut = 1

# Create a new window

        window = Gtk.Window()
        window.set_title("configuration axe Y")
        window.set_size_request(300, 200)

# Creation d'un tableau de 3x4.
        tableau = Gtk.Table(7, 3, True)
        window.add(tableau)

        L_AxeG  = Gtk.Label("Axe Gauche")
        tableau.attach(L_AxeG, 1, 2, 0, 1)

        if flg_axe_droit == 1 :
            L_AxeD  = Gtk.Label("Axe Droit")
            tableau.attach(L_AxeD, 2, 3, 0, 1)


        L_ymin = Gtk.Label("Y min")
        E_ymin1 = Gtk.Entry()
        E_ymin1.set_text(str(ymn1))
        tableau.attach(L_ymin, 0, 1, 2, 3)
        tableau.attach(E_ymin1, 1, 2, 2, 3)
        if flg_axe_droit == 1 :
            E_ymin2 = Gtk.Entry()
            E_ymin2.set_text(str(ymn2))
            tableau.attach(E_ymin2, 2, 3, 2, 3)

        L_ymax = Gtk.Label("Y max")
        E_ymax1 = Gtk.Entry()
        E_ymax1.set_text(str(ymx1))
        tableau.attach(L_ymax, 0, 1, 1, 2)
        tableau.attach(E_ymax1, 1, 2, 1, 2)
        if flg_axe_droit == 1 :
            E_ymax2 = Gtk.Entry()
            E_ymax2.set_text(str(ymx2))
            tableau.attach(E_ymax2, 2, 3, 1, 2)

        cb_fixe = Gtk.CheckButton("Echelle(s) fixe(s).")
        tableau.attach(cb_fixe, 0, 3, 4, 5)
        L_fixe = Gtk.Label("Champs vide => valeur automatique")
        tableau.attach(L_fixe, 0, 3, 5, 6)
        b1 = Gtk.Button('OK')
        tableau.attach(b1, 2, 3, 6, 7)


        if flg_axe_droit == 0 :
            b1.connect('clicked', redraw, window, fig, ax0, E_ymin1, E_ymax1, None, None, None, cb_fixe, IHM.graph_gene.graphes[Num_gr])
        else :
            b1.connect('clicked', redraw, window, fig, ax0, E_ymin1, E_ymax1, ax1, E_ymin2, E_ymax2, cb_fixe, IHM.graph_gene.graphes[Num_gr])

        window.show_all()

def redraw(self, win, fig, ax0, Eymin1, Eymax1, ax1, Eymin2, Eymax2, ech_fix, ihmg) :
    if Eymin1.get_text() != "" :
        try :
            ymin = float(Eymin1.get_text())
        except :
            ymin = None
    else :
        ymin = None

    if Eymax1.get_text() != "" :
        try :
            ymax = float(Eymax1.get_text())
        except :
            ymax = None
    else :
        ymax = None

    ax0.set_ylim(ymin, ymax)

    if ax1 != None :
        if Eymin2.get_text() != "" :
            try :
                ymin2 = float(Eymin2.get_text())
            except :
                ymin2 = None
        else :
            ymin2 = None

        if Eymax2.get_text() != "" :
            try :
                ymax2 = float(Eymax2.get_text())
            except :
                ymax2 = None
        else :
            ymax2 = None

        ax1.set_ylim(ymin2, ymax2)
    else :
        ymin2 = None
        ymax2 = None

    if ech_fix.get_active() == True :
        ihmg.ylim = [ymin, ymax, ymin2, ymax2]
        print("ECHELLE FIXE")
    else :
        ihmg.ylim = [None, None, None, None]
        print("ECHELLE AUTO")

    fig.canvas.draw()
    win.destroy()

def toggle_selector(event, ax, xmin, xmax, ymin, ymax, IHM, fig, cursor):
    if event.key in ['D', 'd']:
        if cursor.idco != 0 :
            fig.canvas.mpl_disconnect(cursor.idco)
            for nb in npy.arange(len(cursor.ly)) :
                cursor.ly[nb].set_visible(False)
                cursor.txt[nb].set_text(" ")
                cursor.idco = 0
            fig.canvas.draw()
        else :
            cursor.idco = fig.canvas.mpl_connect('motion_notify_event', lambda e1:cursor.mouse_move)
            for nb in npy.arange(len(cursor.ly)) :
                cursor.ly[nb].set_visible(True)
            fig.canvas.draw()

    if event.key in ['P', 'p']:
        if IHM != None :
            IHM.graph_gene.E_xmin.get_text()

def focus(self, event, l_axes):
    self.canvas.grab_focus()

def read_vect(acq_id, name, attributes_only = False, alarme = 1):
    try:
        vect = AIDA.Vector (acq_id, name, attributes_only = attributes_only)
    except ValueError :
        if alarme == 1 :
            Abandon("Echec lecture du vecteur %s." % (name), Gtk.MessageType.ERROR)
            return None
        else :
            return -1
    except IOError as xxx_todo_changeme:
        (errno, strerror) = xxx_todo_changeme.args
        if alarme == 1 :
            Abandon("Erreur lecture du vecteur %s : %s" % (name, strerror), Gtk.MessageType.ERROR)
            return None
        else :
            return -1
    except AIDA.AidaError as msg:
        if alarme == 1 :
            raise Abandon("Probleme AIDA lors lecture vecteur %s : %s" % (name, msg), Gtk.MessageType.ERROR)
            return None
        else :
            return -1
    return vect

def decompose_chaine_operation(str_oper, acqid) :

    rep_data = AIDA.ID_to_datapath(acqid)

    GROUP = re.split('[+-]', str_oper)
    OPER = ''

# Etude premier groupe de l'opération.

    ELEMENT = re.split('[/*]', GROUP[0])
    OPERATEUR = ''

    try :
        data1 = float(ELEMENT[0])
        Unit1 = ELEMENT[0]
    except :
        data_tmp = read_vect(acqid, ELEMENT[0])
        if data_tmp == None :
            return -1, 0, None

        vector_time = data_tmp.attributes["ref_time"]
        try :
            src = os.path.join(rep_data, vector_time)+'.vbn'
            vector_time = os.readlink(src)[:-4]
        except :
            pass

        try :
            Unit1 = data_tmp.attributes["unit"]
        except :
            Unit1 = "without"

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
            if data_tmp == None :
                return -1, 0, None
            vector_time2 = data_tmp.attributes["ref_time"]
            try :
                src = os.path.join(rep_data, vector_time2)+'.vbn'
                vector_time2 = os.readlink(src)[:-4]
            except :
                pass
            if vector_time != vector_time2 :
                return None, None, None
            try :
                Unit2 = data_tmp.attributes["unit"]
            except :
                Unit2 = "without"

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

        ELEMENT = re.split('[/*]', GROUP[1])
        OPERATEUR = ''

        try :
            data1 = float(ELEMENT[0])
            Unit1 = ELEMENT[0]
        except :
            data_tmp = read_vect(acqid, ELEMENT[0])
            if data_tmp == None :
                return -1, 0, None
            vector_time2 = data_tmp.attributes["ref_time"]
            try :
                src = os.path.join(rep_data, vector_time2)+'.vbn'
                vector_time2 = os.readlink(src)[:-4]
            except :
                pass
            if vector_time != vector_time2 :
                return None, None, None

            try :
                Unit1 = data_tmp.attributes["unit"]
            except :
                Unit1 = "without"

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
                if data_tmp == None :
                    return -1, 0, None
                vector_time2 = data_tmp.attributes["ref_time"]
                try :
                    src = os.path.join(rep_data, vector_time2)+'.vbn'
                    vector_time2 = os.readlink(src)[:-4]
                except :
                    pass
                if vector_time != vector_time2 :
                    return None, None, None

                try :
                    Unit2 = data_tmp.attributes["unit"]
                except :
                    Unit2 = "without"

                data2 = data_tmp.data

        if OPERATEUR == '*' :
            data_c2 = data1 * data2
            UnitB = Unit1 + '*' + Unit2
        elif OPERATEUR == '/' :
            data_c2 = data1 / data2
            UnitB = Unit1 + '/' + Unit2
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

def Tracer_emagramme(self, IHM, bn_canvas, Choix_entry, ChampSaisie, F_pres) :

    if matplotlib.__version__ < '1.0.0' :
        Message = "Version Matploblib trop ancienne, pas de tracer trajectoire"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return


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

# Effacement graphe page 1
    canvas = bn_canvas.get_nth_page(0)
    fig = canvas.figure

    if IHM.graph_gene.PositionImage[0] != None or IHM.graph_gene.PositionImage[1] != None :
        fig.subplots_adjust(left = IHM.graph_gene.PositionImage[0])
        fig.subplots_adjust(right = IHM.graph_gene.PositionImage[1])
    else :
        fig.subplots_adjust(right = 0.8)

    if IHM.graph_gene.PositionImage[2] != None or IHM.graph_gene.PositionImage[3] != None :
        fig.subplots_adjust(bottom = IHM.graph_gene.PositionImage[2])
        fig.subplots_adjust(top = IHM.graph_gene.PositionImage[3])

    for ax in fig.get_axes() :
        ax.cla()
        fig.clear()

    for ax in fig.get_axes() :
        ax.cla()
        fig.clear()

# Effacement page(s) suivante(s)
    for nb in npy.arange(1, bn_canvas.get_n_pages()) :
        bn_canvas.remove_page(1)

# Recuperation information vol

    IHM.recup_fic_inf(ChampSaisie, F_pres, IHM)
    acqid = IHM.graph_gene.acqid

    try :
        pltf = AIDA.plt_by_abrev[acqid[0:2]]
    except :
        if acqid == "" :
            Message = "Saisir un acqid !"
        else :
            Message = "Acqid pas valid!"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return

#    second_vol = date2num(IHM.graph_gene.date_acquisition)

    subtitre = str(Choix_entry["Titre"].get_text())
    soustitre = str(Choix_entry["SousTitre"].get_text())

    if subtitre == "" and IHM.graph_gene.TitreGraph != "" :
        Choix_entry["Titre"].set_text( IHM.graph_gene.TitreGraph)
        subtitre = str(IHM.graph_gene.TitreGraph)
    elif  subtitre != "" :
        IHM.graph_gene.TitreGraph = subtitre

    fig.text(0.5, 0.975, subtitre, horizontalalignment = 'center', verticalalignment = 'top')

    if soustitre != "" :
        Choix_entry["SousTitre"].set_text(soustitre)
        subtitre2 = soustitre
    else :
        try :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid + ' du ' + \
                       IHM.graph_gene.date_acquisition.strftime('%d/%m/%y'))
        except :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid)


    fig.text(0.5, 0.955, subtitre2, horizontalalignment = 'center', verticalalignment = 'top')

    vectorP = Choix_entry["Vecteur0"].get_text()
    vectorT = Choix_entry["Vecteur1"].get_text()
    vectorTp = Choix_entry["Vecteur2"].get_text()
    vectorTr = Choix_entry["Vecteur3"].get_text()
    vectorV1 = Choix_entry["Vecteur4"].get_text()
    vectorV2 = Choix_entry["Vecteur5"].get_text()

# lecture de donnees

    if vectorP != '' :
        data_P = read_vect(acqid, vectorP)
        if data_P == None :
            return
        data_P.data[ data_P.data < 10 ] = 10
    if vectorT != '' :
        data_T = read_vect(acqid, vectorT)
        if data_T != None :
            flg_T = 1
    if vectorTp != '' :
        data_Tp = read_vect(acqid, vectorTp)
        if data_Tp != None :
            flg_Tp = 1
    if vectorTr != '' :
        data_Tr = read_vect(acqid, vectorTr)
        if data_Tr != None :
            flg_Tr = 1
    if vectorV1 != '' and vectorV2 != '' :
        data_V1 = read_vect(acqid, vectorV1)
        data_V2 = read_vect(acqid, vectorV2)
        if data_V1 != None and data_V2 != None :
            flg_V = 1

    data_45 = []
    data_Ec = []
    data_Nc = []
    data_Pc = []

#Recuperation vecteur temps

    vector_time = data_P.attributes["ref_time"]
    date_time = read_vect(acqid, vector_time)

#conversion de temperatures

    pas_vent = 50

    if vectorV1[0:5].lower() == 'ven_e' and vectorV2[0:5].lower() == 'ven_n' :
        if data_V1.attributes["unit"] == "m/s" :
            print("CONVERSION EN KT." + vectorV1)
            conv_Ec = 1.94384449
        elif data_V1.attributes["unit"] == "kt" :
            conv_Ec = 1
        if data_V2.attributes["unit"] == "m/s" :
            print("CONVERSION EN KT." + vectorV2)
            conv_Nc = 1.94384449
        elif data_V2.attributes["unit"] == "kt" :
            conv_Nc = 1
        for n_pr in npy.arange(0,len(data_P.data)) :
            if npy.mod(n_pr, pas_vent) == 0 :
                data_Pc.append(data_P.data[n_pr])
                data_45.append(int(45))
                data_Ec.append(data_V1.data[n_pr] * conv_Ec)
                data_Nc.append(data_V2.data[n_pr] * conv_Nc)

            pr = data_P.data[n_pr]
            Prop = ((math.log(Pmax, 10) - math.log (pr, 10))/(math.log(Pmax, 10) - math.log (Pmin, 10)))
            if flg_T == 1 :
                data_T.data[n_pr] = data_T.data[n_pr] + 90 * Prop
            if flg_Tp == 1 :
                data_Tp.data[n_pr] = data_Tp.data[n_pr] + 90 * Prop
            if flg_Tr == 1 :
                data_Tr.data[n_pr] = data_Tr.data[n_pr] + 90 * Prop

    elif vectorV1[0:5].lower() == 'ven_d' and vectorV2[0:5].lower() == 'ven_f' :
        if data_V2.attributes["unit"] == "m/s" :
            print("CONVERSION EN KT." + vectorV2)
            conv_Vc = 1.94384449
        elif ven_1.attributes["unit"] == "kt" :
            conv_Ec = 1

        for n_pr in npy.arange(0,len(data_P.data)) :
            if npy.mod(n_pr, pas_vent) == 0 :
                data_Pc.append(data_P.data[n_pr])
                data_45.append(int(45))
                data_Ec.append(-1*data_V2.data[n_pr]*conv_Vc*math.sin(data_V1.data[n_pr]*3.14/180))
                data_Nc.append(-1*data_V2.data[n_pr]*conv_Vc*math.cos(data_V1.data[n_pr]*3.14/180))

            pr = data_P.data[n_pr]
            Prop = ((math.log(Pmax, 10) - math.log (pr, 10))/(math.log(Pmax, 10) - math.log (Pmin, 10)))
            if flg_T == 1 :
                data_T.data[n_pr] = data_T.data[n_pr] + 90 * Prop
            if flg_Tp == 1 :
                data_Tp.data[n_pr] = data_Tp.data[n_pr] + 90 * Prop
            if flg_Tr == 1 :
                data_Tr.data[n_pr] = data_Tr.data[n_pr] + 90 * Prop

    elif  vectorV1 != '' or vectorV2 != '' :
            Message = u"Choix incoherent pour le vent\n choisir DD et FF ou u et v !"
            raise Abandon(Message, Gtk.MessageType.ERROR)

    grid_helper = GridHelperCurveLinear((tr, inv_tr))

    ax = Subplot(fig, 1, 1, 1, grid_helper = grid_helper)
    fig.add_subplot(ax)

# Trace des Isobares
# ------------------

    Tmax = 50.
    Tmin = -20.
    ax.set_xlim(Tmin, Tmax)
    ax.set_ylim(0, 90)
    ax.axis["left"].toggle(ticklabels = False)
#    ax.axis["bottom"].major_ticklabels.set_color("y")
    majorLocator   = MultipleLocator(10)
    majorFormatter = FormatStrFormatter('%d')
    ax.xaxis.set_major_locator(majorLocator)
    ax.xaxis.set_major_formatter(majorFormatter)
#    ax.set_xticks([10., 20., 30.])
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
#    ax2.set_xticks([10, 20, 30])

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

    line_segments = LineCollection(segs,  \
                                linewidths    = (1, 0.3, 0.3, 0.3, 0.3, 0.7, 0.3, 0.3, 0.3, 0.3),  \
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

    ep_rw = [1, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, \
             1, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 1, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1, \
             0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1, 0.5, 0.5, 0.5, 0.5, 1]
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
                ax2.text(IsoT-1, l_p2[npr], l_t2[nt],
                    rotation = -40,
                    weight = 8,
                    color = 'g',
                    horizontalalignment = 'center',
                    verticalalignment = 'bottom',
                    fontproperties = font_graduation)

    line_segments = LineCollection(segs,
                                linewidths    = (1, 0.5),
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


    line_segments = LineCollection(segs,
                                linewidths    = (1, 0.5, 0.5, 0.5, 0.5),
                                colors       = 'g',
                                linestyle = 'dashed')
    ax2.add_collection(line_segments)

# conversion hhmmss en seconde
    if IHM.graph_gene.unit_temp == "Seconde" :
        heure = (IHM.graph_gene.E_xmin.get_text())
        xmin = int(heure)
        IHM.graph_gene.Adj_deb_trace.set_value(int(heure))
        heure = (IHM.graph_gene.E_xmax.get_text())
        xmax = int(heure)
        IHM.graph_gene.Adj_fin_trace.set_value(int(heure))
    else  :
        heure = (IHM.graph_gene.E_xmin.get_text())
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        xmin = hh*3600 + mm*60 + ss
        IHM.graph_gene.Adj_deb_trace.set_value(hh*3600 + mm*60 + ss)
        heure = (IHM.graph_gene.E_xmax.get_text())
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        xmax = hh*3600 + mm*60 + ss
        IHM.graph_gene.Adj_fin_trace.set_value(hh*3600 + mm*60 + ss)

    int_dec = 0
    int_dec2 = 0
    int_att = len(date_time.data)-1
    int_att2 = int(int_att/pas_vent)

    for i in npy.arange(len(date_time.data)) :
        if date_time.data[i] < xmin :
            int_dec = i
            int_dec2 = int(i/pas_vent)
        if date_time.data[i] < xmax :
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

    ax2.legend(bbox_to_anchor = (1, 1), loc = 2, borderaxespad = 0., prop = font_titre)
    toggle_selector.RS = []
    toggle_selector.RS.append(RectangleSelector(ax, \
                lambda e1, e2:line_select_callback(e1, e2, IHM), \
                            useblit = True, \
                            button = [1, 3], # don't use middle button\
                            minspanx = 5, minspany = 5, \
                            spancoords = 'pixels'))
    toggle_selector.RS[0].set_active(True)

    if IHM.graph_gene.graphes[0].ylim[0] != None or IHM.graph_gene.graphes[0].ylim[1] != None :
        ymin =  IHM.graph_gene.graphes[0].ylim[0]
        ymax =  IHM.graph_gene.graphes[0].ylim[1]
        ax2.set_ylim(ymin, ymax)

    if IHM.graph_gene.graphes[0].ylim[2] != None or IHM.graph_gene.graphes[0].ylim[3] != None :
        xmin =  IHM.graph_gene.graphes[0].ylim[2]
        xmax =  IHM.graph_gene.graphes[0].ylim[3]
        ax2.set_xlim(xmin, xmax)

    fig.canvas.draw()
    IHM.graph_gene.acqid_trace = acqid

def Tracer_visu1D(self, IHM, bn_canvas, Choix_entry, ChampSaisie, F_pres) :

    if matplotlib.__version__ < '1.0.0' :
        Message = "Version Matploblib trop ancienne, pas de tracer trajectoire"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return

    font_titre = FontProperties()
    font_titre.set_size(10)

# Effacement graphe page 1
    canvas = bn_canvas.get_nth_page(0)
    fig = canvas.figure
    fig.subplots_adjust(right = 0.8)

# Effacement page(s) suivante(s)
    for nb in npy.arange(1, bn_canvas.get_n_pages()) :
        bn_canvas.remove_page(1)

# Recuperation information vol

    IHM.recup_fic_inf(ChampSaisie, F_pres, IHM)
    acqid = IHM.graph_gene.acqid
    try :
        pltf = AIDA.plt_by_abrev[acqid[0:2]]
    except :
        if acqid == "" :
            Message = "Saisir un acqid !"
        else :
            Message = "Acqid pas valid!"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return

    second_vol = date2num(IHM.graph_gene.date_acquisition)

    if IHM.graph_gene.heure_dec == None or IHM.graph_gene.heure_att == None :
        print ("PAS HEURES DECOLLAGE ET ATTERISSAGE")
        xmin = min (date.data)
        xmax = max (date.data)
    else :
        xmin = date2num(IHM.graph_gene.heure_dec)
        xmax = date2num(IHM.graph_gene.heure_att)

    vect = Choix_entry["Vecteur"].get_text()
    IHM.graph_gene.nb_graphe = 1
    IHM.graph_gene.graphes[0].vecteur_Y = vect

    dataX = read_vect(acqid, vect)
    if dataX == None :
        return

    try :
        vector_time_X = dataX.attributes["ref_time"]
        nbct = int(dataX.attributes["dim_array"])
        UnitX = dataX.attributes["unit"] + "(" + vect + ")"
    except KeyError:
        vector_time_X = vect
        UnitX = "Inconnu"

    date_time = read_vect(acqid, vector_time_X)

# conversion hhmmss en seconde
    if IHM.graph_gene.unit_temp == "Seconde" :
        heure = (IHM.graph_gene.E_xmin.get_text())
        xmin = int(heure)
        IHM.graph_gene.Adj_deb_trace.set_value(int(heure))
        heure = (IHM.graph_gene.E_xmax.get_text())
        xmax = int(heure)
        IHM.graph_gene.Adj_fin_trace.set_value(int(heure))
    else  :
        heure = (IHM.graph_gene.E_xmin.get_text())
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        xmin = hh*3600 + mm*60 + ss
        IHM.graph_gene.Adj_deb_trace.set_value(hh*3600 + mm*60 + ss)
        heure = (IHM.graph_gene.E_xmax.get_text())
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        xmax = hh*3600 + mm*60 + ss
        IHM.graph_gene.Adj_fin_trace.set_value(hh*3600 + mm*60 + ss)

    int_dec = 0
    int_att = len(date_time.data)-1
    for i in npy.arange(len(date_time.data)) :
        if date_time.data[i] < xmin :
            int_dec = i
        if date_time.data[i] < xmax :
            int_att = i

    date_data = npy.array([])
    for i in npy.arange(len(date_time.data)) :
        date_data = npy.append(date_data, second_vol + date_time.data[i]/86400)

#    Titre = "Visu 1D " + acqid
    subtitre = str(Choix_entry["Titre"].get_text())
    soustitre = str(Choix_entry["SousTitre"].get_text())

    if subtitre == "" and IHM.graph_gene.TitreGraph != "" :
        Choix_entry["Titre"].set_text( IHM.graph_gene.TitreGraph)
        subtitre = str(IHM.graph_gene.TitreGraph)
    elif  subtitre != "" :
        IHM.graph_gene.TitreGraph = subtitre

    fig.text(0.5, 0.975, subtitre, horizontalalignment = 'center', verticalalignment = 'top')

    if soustitre != "" :
        Choix_entry["SousTitre"].set_text(soustitre)
        subtitre2 = soustitre
    else :
        try :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid + ' du ' + \
                       IHM.graph_gene.date_acquisition.strftime('%d/%m/%y'))
        except :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid)

    fig.text(0.5, 0.955, subtitre2, horizontalalignment = 'center', verticalalignment = 'top')


    axg = fig.add_subplot(111, projection = '3d')
#    axg.set_title(Titre)
    axg.set_xlabel(UnitX)

    nbc = nbct
    nbt = len(date_data)
    grf = []
    iz = npy.arange(nbc)
    nbd = 0
    maxdata = 0

    data2=dataX.data.T.astype('float64')
    date2 = (date_data - second_vol)*86400
    for nc in  npy.arange(nbc) :
        ys = data2[nc][int_dec:int_att]
#        ys.append(data2[nc])
        maxdata = max(maxdata, max(data2[nc]))
        ys[0] = 0
        ys[-1] = 0
        grf.append(list(zip(date2, ys)))



    poly = PolyCollection(grf, edgecolors = 'red',  facecolors = 'green')

#    poly.set_alpha(0.5)
    poly.set_alpha(1)
#    axg.add_collection3d(poly, zs = date_data[int_dec:int_att], zdir = 'y')
    axg.add_collection3d(poly, zs = npy.arange(nbc) , zdir = 'x')

    axg.set_ylabel('Seconce')
    axg.set_ylim3d(min(date2[int_dec:int_att]), max(date2[int_dec:int_att]))

#    if IHM.graph_gene.unit_temp == "Heure" :
#        axg.yaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
    axg.set_xlabel('Classe')
    axg.set_xlim3d(0, nbc-1)
    axg.set_zlabel('Z')
    axg.set_zlim3d(0, maxdata)

    fig.canvas.draw()
    IHM.graph_gene.acqid_trace = acqid

def Tracer_XY(self, IHM, bn_canvas, Choix_entry, ChampSaisie, F_pres) :

    axes = []
    ymax = -10000000
    ymin = 10000000
    xmax = -10000000
    xmin = 10000000
    nb_graphe = 0
    nbv = 0
    coul = ['black', 'red', 'blue', 'green','cyan','orange']
    nb_graphe = nb_graphe + 1
    font_legende = FontProperties()
    font_legende.set_size(7)

# Effacement graphe page 1
    canvas = bn_canvas.get_nth_page(0)
    fig = canvas.figure

    if IHM.graph_gene.PositionImage[0] != None or IHM.graph_gene.PositionImage[1] != None :
        fig.subplots_adjust(left = IHM.graph_gene.PositionImage[0])
        fig.subplots_adjust(right = IHM.graph_gene.PositionImage[1])
    else :
        fig.subplots_adjust(right = 0.8)

    if IHM.graph_gene.PositionImage[2] != None or IHM.graph_gene.PositionImage[3] != None :
        fig.subplots_adjust(bottom = IHM.graph_gene.PositionImage[2])
        fig.subplots_adjust(top = IHM.graph_gene.PositionImage[3])

    for ax in fig.get_axes() :
        ax.cla()
        fig.clear()

# Effacement page(s) suivante(s)
    for nb in npy.arange(1, bn_canvas.get_n_pages()) :
        bn_canvas.remove_page(1)

# Recuperation information vol

    IHM.recup_fic_inf(ChampSaisie, F_pres, IHM)
    acqid = IHM.graph_gene.acqid

    try :
        pltf = AIDA.plt_by_abrev[acqid[0:2]]
    except :
        if acqid == "" :
            Message = "Saisir un acqid !"
        else :
            Message = "Acqid pas valid!"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return

    subtitre = str(Choix_entry["Titre"].get_text())
    soustitre = str(Choix_entry["SousTitre"].get_text())
    if subtitre == "" and IHM.graph_gene.TitreGraph != "" :
        Choix_entry["Titre"].set_text( IHM.graph_gene.TitreGraph)
        subtitre = str(IHM.graph_gene.TitreGraph)
    elif  subtitre != "" :
        IHM.graph_gene.TitreGraph = subtitre

    fig.text(0.5, 0.975, subtitre, horizontalalignment = 'center', verticalalignment = 'top')

    if soustitre != "" :
        Choix_entry ["SousTitre"].set_text(soustitre)
        subtitre2 = soustitre
    else :
        try :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid + ' du ' + \
                       IHM.graph_gene.date_acquisition.strftime('%d/%m/%y'))
        except :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid)

    fig.text(0.5, 0.955, subtitre2, horizontalalignment = 'center', verticalalignment = 'top')

    for nb in npy.arange(int(IHM.graph_gene.nb_graphe)) :

        if IHM.graph_gene.graphes[nb].vecteur_X != "" \
                    and IHM.graph_gene.graphes[nb].vecteur_Y != "" :
            vect_X = IHM.graph_gene.graphes[nb].vecteur_X
            vect_Y = IHM.graph_gene.graphes[nb].vecteur_Y
#            IHM.graph_gene.nb_graphe = IHM.graph_gene.nb_graphe + 1
        else :
            continue

        if vect_X.find('-') + vect_X.find('+') \
                + vect_X.find('*') + vect_X.find('/')  >= 0 :
#            data_vect=[]
            vector_time_X = ""
            UnitX = ""
            vector_time_X, UnitX , dataX = decompose_chaine_operation(vect_X, acqid)
            if vector_time_X == None :
                Message = "Attention operation " + vect_X + " impossible, temps differents"
                Abandon(Message, Gtk.MessageType.ERROR)
                break
        else :
            data1 = read_vect(acqid, vect_X)
            if data1 == None :
                break
                       
            vector_time_X = data1.attributes["ref_time"]
            try :
                UnitX = data1.attributes["unit"]
            except :
                UnitX = "Inconnue"
    
            dataX = data1.data

        date_time = read_vect(acqid, vector_time_X)

# conversion hhmmss en seconde
        if IHM.graph_gene.unit_temp == "Seconde" :
            heure = (IHM.graph_gene.E_xmin.get_text())
            hmin = int(heure)
            IHM.graph_gene.Adj_deb_trace.set_value(int(heure))
            heure = (IHM.graph_gene.E_xmax.get_text())
            hmax = int(heure)
            IHM.graph_gene.Adj_fin_trace.set_value(int(heure))
        elif IHM.graph_gene.unit_temp == "Heure" :
            heure = (IHM.graph_gene.E_xmin.get_text())
            hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
            hmin = hh*3600 + mm*60 + ss
            IHM.graph_gene.Adj_deb_trace.set_value(hh*3600 + mm*60 + ss)
            heure = (IHM.graph_gene.E_xmax.get_text())
            hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
            hmax = hh*3600 + mm*60 + ss
            IHM.graph_gene.Adj_fin_trace.set_value(hh*3600 + mm*60 + ss)
        else  :
            hmin = min(date_time.data)
            hmax = max(date_time.data)


        int_dec = 0
        int_att = len(date_time.data)-1
        for i in npy.arange(len(date_time.data)) :
            if date_time.data[i] < hmin :
                int_dec = i
            if date_time.data[i] < hmax :
                int_att = i

        if vect_Y.find('-') + vect_Y.find('+') \
                + vect_Y.find('*') + vect_Y.find('/')  >= 0 :
            vector_time_Y = ""
            UnitY = ""
            vector_time_Y, UnitY , dataY = decompose_chaine_operation(vect_Y, acqid)
            if vector_time_Y == None :
                Message = "Attention operation " + vect_Y + " impossible, temps differents"
                Abandon(Message, Gtk.MessageType.ERROR)
                break
        else :
            data1 = read_vect(acqid, vect_Y)
            if data1 == None :
                break

            vector_time_Y = data1.attributes["ref_time"]
            try :
                UnitY = data1.attributes["unit"]
            except :
                UnitY = "Inconnue"
    
            dataY = data1.data

        if nbv == 0 :
            UnitY1 = UnitY
            UnitY2 = "??"
            nb_unity = 1
            Titre_UnitY1 = UnitY + " : " + vect_Y
            flg_unity = 0

            UnitX1 = UnitX
            UnitX2 = ""
            nb_unitx = 1
            Titre_UnitX1 = UnitX + " : " + vect_X
            flg_unitx = 0

            axg = fig.add_subplot(1, 1, 1)
            axes.append(axg)
            axt = axg
        else :
            flg_unitx = -1
            if UnitX != UnitX1 and UnitX != UnitX2 and nb_unitx == 2 :
                print ("ALARME : Trop d'unite pour le graphe : Axe X! ")
                break
            if UnitX == UnitX1 :
                Titre_UnitX1 = Titre_UnitX1 + ", " + vect_X
                flg_unitx = 0
            elif UnitX == UnitX2 :
                Titre_UnitX2 = Titre_UnitX2 + ", " + vect_X
                flg_unitx = 1
            else :
                UnitX2 = UnitX
                Titre_UnitX2 = UnitX2 + " : " + vect_X
                nb_unitx = 2
                flg_unitx = 2

            flg_unity = -1
            if UnitY != UnitY1 and UnitY != UnitY2 and nb_unity == 2 :
                print ("ALARME : Trop d'unite pour le graphe : Axe Y! ")
                break
            if UnitY == UnitY1 :
                Titre_UnitY1 = Titre_UnitY1 + ", " + vect_Y
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
                Titre_UnitY2 = Titre_UnitY2 + ", " + vect_Y
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
                Titre_UnitY2 = UnitY2 + " : " + vect_Y
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


        if (int_att - int_dec ) < 100000 :
            dataX_TMP = npy.array([])
            dataY_TMP = npy.array([])
            for nd in npy.arange(int_dec, int_att) :
                if math.isnan(dataX[nd]) == False and math.isnan(dataY[nd]) == False :
                    dataX_TMP = npy.append(dataX_TMP, dataX[nd])
                    dataY_TMP = npy.append(dataY_TMP, dataY[nd])
        else :
            dataX_TMP = dataX[int_dec:int_att]
            dataY_TMP = dataY[int_dec:int_att]


        xmin = min(min(dataX_TMP), xmin) * 0.95
        xmax = max(max(dataX_TMP), xmax) * 1.05
        XX = [xmin, xmax]

#        axt.set_xlim(XX)

# Recuperation couleur
        coul = IHM.graph_gene.graphes[nbv].couleur

# Recuperation Type trait
        trait = IHM.graph_gene.graphes[nbv].type_trait
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

# Recuperation Fonction
        Fonct = IHM.graph_gene.graphes[nbv].fonction
        if Fonct == "Regression linéaire" :
            m, b = npy.polyfit(dataX_TMP.astype('float64'), dataY_TMP.astype('float64'), 1)
            r_cor = npy.corrcoef(dataX_TMP.astype('float64'), dataY_TMP.astype('float64'))[0, 1]
            axt.plot(dataX, m*dataX+b, '-', color = coul )
            str_reg = "Y= " + str(m) + " X + " + str(b) + ",  Corr = " + str(r_cor)
            fig.text(0.2, 0.02, str_reg)

        if Fonct == "Regression polynomiale" :
            a, b, c = npy.polyfit(dataX_TMP.astype('float64'), dataY_TMP.astype('float64'), 2)
            Xmin = round(min(dataX_TMP))
            Xmax = round(max(dataX_TMP))
            Xpas = (Xmax - Xmin)/100
            lst_reg = npy.arange(Xmin, Xmax, Xpas)
            p = npy.poly1d(npy.polyfit(dataX_TMP.astype('float64'), dataY_TMP.astype('float64'), 2))
#            axt.plot(lst_reg, a*(lst_reg**2)+b*lst_reg+c, '-', color = coul , linewidth = 2)
            axt.plot(lst_reg, p(lst_reg), '-', color = coul )
            str_reg = "Y= " + str(a) + " X^2 + " + str(b) + " X + " + str(c)
            fig.text(0.2, 0.02, str_reg)

        if Fonct == "X=Y" :
            axt.plot(dataX, dataX, '-', color = coul )

# Recuperation marqueur
        carac = IHM.graph_gene.graphes[nbv].type_mark
        if carac == 'Aucun' :
            carac = ''

# Recuperation epaisseur trait
        Epais = int(IHM.graph_gene.graphes[nbv].epais_trait)
        legende = vect_X + "/" + vect_Y
        if car_t == 'S' :
            Taille = Epais * Epais * Epais/20.
            axt.scatter(dataX[int_dec:int_att], dataY[int_dec:int_att], \
                         marker = '.', s = Taille, color = coul, label = legende)
        else :
            carac = car_t + carac
            axt.plot(dataX[int_dec:int_att], dataY[int_dec:int_att], \
                         carac, color = coul, label = legende , linewidth = Epais)
        nbv = nbv + 1

    if IHM.graph_gene.graphes[0].ylim[0] != None or IHM.graph_gene.graphes[0].ylim[1] != None :
        ymin =  IHM.graph_gene.graphes[0].ylim[0]
        ymax =  IHM.graph_gene.graphes[0].ylim[1]
        axg.set_ylim(ymin, ymax)

    if UnitY2 != "??" :
        if IHM.graph_gene.graphes[0].ylim[2] != None or IHM.graph_gene.graphes[0].ylim[3] != None :
            ymin =  IHM.graph_gene.graphes[0].ylim[2]
            ymax =  IHM.graph_gene.graphes[0].ylim[3]
            axh.set_ylim(ymin, ymax)

    if len(axes) == 1 :
        axg.legend(bbox_to_anchor = (1, 1), loc = 4, borderaxespad = 0., prop = font_legende)
    else :
        axg.legend(bbox_to_anchor = (0, 0), loc = 0, borderaxespad = 0., prop = font_legende)

    try :
        axh.legend(bbox_to_anchor = (1, 0), loc = 4, borderaxespad = 0., prop = font_legende)
    except :
        pass
    try :
        axi.legend(bbox_to_anchor = (1, 1), loc = 4, borderaxespad = 0., prop = font_legende)
    except :
        pass
    try :
        axj.legend(bbox_to_anchor = (0, 1), loc = 4, borderaxespad = 0., prop = font_legende)
    except :
        pass
    fig.canvas.mpl_connect('motion_notify_event', lambda e1:focus(fig, e1, axes))

    if IHM.graph_gene.key_id != 0 :
        fig.canvas.mpl_disconnect(IHM.graph_gene.key_id)
    IHM.graph_gene.key_id = fig.canvas.mpl_connect('key_press_event', lambda e1:key_press(e1, axes, fig, None, IHM))

    fig.canvas.draw()
    IHM.graph_gene.acqid_trace = acqid

def Tracer_trajectoire(self, IHM, bn_canvas, ChampVecteurs, ChampAcqid, ChampSup, F_pres, F_zoom) :

    def couleur_point (data_col, IHML, loc, lac, alc, lon, lox, lan, lax, aln, alx) :
        if data_col == None :
            if lac < lan or lac > lax or loc < lon or loc > lox or alc < aln or alc > alx :
                cl = -1
            else :
                cl = 1
            return cl

        nbcolor = int(IHML.graph_gene.graphes[0].nb_classe_couleur)
        if lac < lan or lac > lax or loc < lon or loc > lox or alc < aln or alc > alx :
            cl = -1
        elif ( npy.isnan(data_col)) :
            cl = -1
        elif data_col < IHML.graph_gene.graphes[0].seuils_classe_couleur[0] or \
            data_col > IHML.graph_gene.graphes[0].seuils_classe_couleur[nbcolor] :
            cl = -1
        else :
            for nc in npy.arange(1, nbcolor+1) :
                if data_col <= IHML.graph_gene.graphes[0].seuils_classe_couleur[int(nc)] :
                    cl = int(nc)
                    break
        return cl


    if matplotlib.__version__ < '1.0.0' :
        Message = "Version Matploblib trop ancienne, pas de tracer trajectoire"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return

    nb_graphe = 0

# Effacement graphe page 1
    canvas = bn_canvas.get_nth_page(0)
    fig = canvas.figure
    xlim_en_cours = ()
    ylim_en_cours = ()

    if IHM.graph_gene.PositionImage[0] != None or IHM.graph_gene.PositionImage[1] != None :
        fig.subplots_adjust(left = IHM.graph_gene.PositionImage[0])
        fig.subplots_adjust(right = IHM.graph_gene.PositionImage[1])
    else :
        fig.subplots_adjust(right = 0.9)

    if IHM.graph_gene.PositionImage[2] != None or IHM.graph_gene.PositionImage[3] != None :
        fig.subplots_adjust(bottom = IHM.graph_gene.PositionImage[2])
        fig.subplots_adjust(top = IHM.graph_gene.PositionImage[3])

    for ax in fig.get_axes() :
        xlim_en_cours  = ax.get_xlim()
        ylim_en_cours  = ax.get_ylim()
        ax.cla()
        fig.clear()

# Effacement page(s) suivante(s)
    for nb in npy.arange(1, bn_canvas.get_n_pages()) :
        bn_canvas.remove_page(1)

    acq_id_old = IHM.graph_gene.acqid
# Recuperation information vol

    IHM.recup_fic_inf(ChampAcqid, F_pres, IHM)
    acqid = IHM.graph_gene.acqid
    acq_meta = AIDA.Inf(acqid)

    nb_graphe = nb_graphe + 1
    IHM.graph_gene.nb_graphe = 1
    vect_lat = ChampVecteurs["vecteur_lat"].get_text()
    IHM.graph_gene.graphes[0].vecteur_Y = vect_lat
    vect_lon = ChampVecteurs["vecteur_lon"].get_text()
    IHM.graph_gene.graphes[0].vecteur_X = vect_lon
    vect_alt = ChampVecteurs["vecteur_alt"].get_text()
    IHM.graph_gene.graphes[0].vecteur_Z = vect_alt

    try :
        pltf = AIDA.plt_by_abrev[acqid[0:2]]
    except :
        if acqid == "" :
            Message = "Saisir un acqid !"
        else :
            Message = "Acqid pas valid!"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return

    subtitre = str(ChampVecteurs["Titre"].get_text())
    soustitre = str(ChampVecteurs["SousTitre"].get_text())
    if subtitre == "" and IHM.graph_gene.TitreGraph != "" :
        ChampVecteurs["Titre"].set_text( IHM.graph_gene.TitreGraph)
        subtitre = str(IHM.graph_gene.TitreGraph)
    elif  subtitre != "" :
        IHM.graph_gene.TitreGraph = subtitre

    fig.text(0.5, 0.975, subtitre, horizontalalignment = 'center', verticalalignment = 'top')

    if soustitre != "" :
        ChampVecteurs["SousTitre"].set_text(soustitre)
        subtitre2 = soustitre
    else :
        try :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid + ' du ' + \
                       IHM.graph_gene.date_acquisition.strftime('%d/%m/%y'))
        except :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid)

    fig.text(0.5, 0.955, subtitre2, horizontalalignment = 'center', verticalalignment = 'top')

    try :
        second_vol = date2num(IHM.graph_gene.date_acquisition)
    except :
        second_vol = 1

# Lecture fichier latitude
    lat = read_vect(acqid, vect_lat)
    if lat == None :
        return

# Lecture fichier longitude
    lon = read_vect(acqid, vect_lon)
    if lon == None :
        return

# Lecture fichier temps
    vector_time_lat = lon.attributes["ref_time"]
    vector_time_lon = lat.attributes["ref_time"]
    if vector_time_lon != vector_time_lat :
        Message = "Les vecteurs Latitude et Longitude doivent avoir le même ref_time"
        Abandon(Message, Gtk.MessageType.ERROR)
        return

    
    date_time = read_vect(acqid, vector_time_lat)
    data_date = date_time.data/86400 + second_vol

# conversion hhmmss en seconde
    if IHM.graph_gene.unit_temp == "Seconde" :
        heure = (IHM.graph_gene.E_xmin.get_text())
        xmin = second_vol + (int(heure))/86400.
        IHM.graph_gene.Adj_deb_trace.set_value(int(heure))
        heure = (IHM.graph_gene.E_xmax.get_text())
        xmax = second_vol + (int(heure))/86400.
        IHM.graph_gene.Adj_fin_trace.set_value(int(heure))
    elif IHM.graph_gene.unit_temp == "Heure" :
        heure = (IHM.graph_gene.E_xmin.get_text())
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        xmin = second_vol + (hh*3600 + mm*60 + ss)/86400.
        IHM.graph_gene.Adj_deb_trace.set_value(hh*3600 + mm*60 + ss)
        heure = (IHM.graph_gene.E_xmax.get_text())
        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
        xmax = second_vol + (hh*3600 + mm*60 + ss)/86400.
        IHM.graph_gene.Adj_fin_trace.set_value(hh*3600 + mm*60 + ss)
    else :
        xmin = min(data_date)
        xmax = max(data_date)

    int_dec = 0
    int_att = len(data_date)-1
    for i in npy.arange(len(data_date)) :
        if data_date[i] < xmin :
            int_dec = i
        if data_date[i] < xmax :
            int_att = i

    lat_min = 100
    lat_max = -100
    data_lat_max = []
    for nk in npy.arange(len(lat.data[int_dec: int_att])) :
        nl = int_dec + nk
        if math.isnan(lat.data[nl]) == False :
            if lat.data[nl] < lat_min : lat_min = lat.data[nl]
            if lat.data[nl] > lat_max : lat_max = lat.data[nl]

    if IHM.graph_gene.adj_fixe != None : 
        print( IHM.graph_gene.adj_fixe.get_active())
        print( IHM.graph_gene.adj_lat_min.get_value())
        print( IHM.graph_gene.adj_lat_max.get_value())

        if IHM.graph_gene.adj_fixe.get_active() == True :
#    if acqid == IHM.graph_gene.acqid_trace :
            try :
                lat_min_en_cours = IHM.graph_gene.adj_lat_min.get_value()
                lat_max_en_cours = IHM.graph_gene.adj_lat_max.get_value()
            except :
                lat_min_en_cours = lat_min - 0.1
                lat_max_en_cours = lat_max + 0.1
        else :
            lat_min_en_cours = lat_min - 0.1
            lat_max_en_cours = lat_max + 0.1
    else :
        lat_min_en_cours = lat_min - 0.1
        lat_max_en_cours = lat_max + 0.1

    for nl in npy.arange(len(lat.data)) :
        data_lat_max.append(lat_max_en_cours)

    lon_min = 181
    lon_max = -181
    marge_lat_lon = 0.2
    data_lon_min = []
    for nk in npy.arange(len(lon.data[int_dec : int_att])) :
        nl = int_dec + nk
        if math.isnan(lon.data[nl]) == False :
            if lon.data[nl] < lon_min : lon_min = lon.data[nl]
            if lon.data[nl] > lon_max : lon_max = lon.data[nl]

    if IHM.graph_gene.adj_fixe != None : 
        if IHM.graph_gene.adj_fixe.get_active() == True :
#    if acqid == IHM.graph_gene.acqid_trace :
            try :
                lon_min_en_cours = IHM.graph_gene.adj_lon_min.get_value()
                lon_max_en_cours = IHM.graph_gene.adj_lon_max.get_value()
            except :
                lon_min_en_cours = lon_min - marge_lat_lon
                lon_max_en_cours = lon_max + marge_lat_lon
        else :
            lon_min_en_cours = lon_min - marge_lat_lon
            lon_max_en_cours = lon_max + marge_lat_lon
    else :
        lon_min_en_cours = lon_min - marge_lat_lon
        lon_max_en_cours = lon_max + marge_lat_lon

    for nl in npy.arange(len(lon.data)) :
        data_lon_min.append(lon_min_en_cours)

    Titre = "Trajectoire vol " + acqid
    xlabel_texte = ""

# Lecture fichier altitude
    if ChampVecteurs["bt_3D"].get_active() == True :
        if IHM.graph_gene.graphes[0].dimension != "3D" or  acqid != IHM.graph_gene.acqid_trace :
            xlim_en_cours = ()
            ylim_en_cours = ()


        IHM.graph_gene.graphes[0].dimension = "3D"
        axg = Axes3D(fig, xlim=[lon_min_en_cours, lon_max_en_cours], ylim=[lat_min_en_cours, lat_max_en_cours])
        axg.set_zlim(bottom=0)

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
                if vertices[nl][0] > lon_min_en_cours and vertices[nl][0] <  lon_max_en_cours\
                    and  vertices[nl][1] > lat_min_en_cours and vertices[nl][1] < lat_max_en_cours :
                    vertice_ok.append(vertices[nl])
                if (len(vertice_ok)) > 0 :
                    segments.append(vertice_ok)

        lc = LineCollection(segments, color='black')

#        axg.add_collection3d(lc)


        axg.set_xlabel('X')
        axg.set_ylabel('Y')
        axg.set_zlabel('Height')

        axg.set_xlim3d(lon_min_en_cours, lon_max_en_cours)
        axg.set_ylim3d(lat_min_en_cours, lat_max_en_cours)

#AJOUT POUR CARTE
        central_lat = (lon_min_en_cours + lon_max_en_cours)/2
        central_lon = (lat_min_en_cours + lat_max_en_cours)/2
        extent = [lat_min_en_cours,lon_max_en_cours ,lat_min_en_cours ,lat_max_en_cours ]
        central_lon = npy.mean(extent[:2])
        central_lat = npy.mean(extent[2:])

        alt = read_vect(acqid, vect_alt)
        vector_time_alt = alt.attributes["ref_time"]
        if vector_time_alt != vector_time_lat :
            Message = "Les vecteurs Altitude, Latitude et Longitude doivent avoir le même ref_time"
            raise Abandon(Message, Gtk.MessageType.ERROR)
            return

        alt_min = 10000
        alt_max = 0
        for nl in npy.arange(len(alt.data)) :
            if math.isnan(alt.data[nl]) == False :
                if alt.data[nl] < alt_min : alt_min = alt.data[nl]
                if alt.data[nl] > alt_max : alt_max = alt.data[nl]

        if IHM.graph_gene.adj_fixe != None : 
            if IHM.graph_gene.adj_fixe.get_active() == True :
                try :
                    alt_min_en_cours = IHM.graph_gene.adj_alt_min.get_value()
                    alt_max_en_cours = IHM.graph_gene.adj_alt_max.get_value()
                except :
                    alt_min_en_cours = alt_min
                    alt_max_en_cours = alt_max
            else :
                alt_min_en_cours = alt_min
                alt_max_en_cours = alt_max
        else :
            alt_min_en_cours = alt_min
            alt_max_en_cours = alt_max

        axg.set_xlabel("Longitude")
        axg.set_ylabel("Latitude")
        axg.set_zlabel("Altitude (m)")

        axg.set_zlim3d(alt_min_en_cours, alt_max_en_cours)
        if ChampVecteurs["Tops"].get_text() != "" :
            try :
                vect_top = ChampVecteurs["Tops"].get_text()
                data_top = read_vect(acqid, vect_top, alarme = 0)
                vector_time_top = data_top.attributes["ref_time"]
                date_top = read_vect(acqid, vector_time_top)

                for nt in npy.arange(len(data_top.data)) :
                    difference_time = npy.absolute(date_time.data-date_top.data[nt])
                    idx = difference_time.argmin()
                    if  difference_time[idx] < 1 :
                        res = "{0:016b}".format(int(data_top.data[nt].hex(), 16))
                        top_type = int(str(res)[0:7],2)
                        top_data = int(str(res)[7:16],2)
                        axg.text(lon.data[idx], lat.data[idx], alt.data[idx], top_data)
                        axg.scatter(lon.data[idx], lat.data[idx], alt.data[idx])
                flg_top = 1
                IHM.graph_gene.FlgTop = 1
            except :
                try :
                    data_top = read_vect(acqid, vect_top)
                    vector_time_top = data_top.attributes["ref_time"]
                    date_top = read_vect(acqid, vector_time_top)
                    if vector_time_top != vector_time_lat :
                        Message = "Affichage des TOP qu'en 1 hz"
                        raise Abandon(Message, Gtk.MessageType.ERROR)
                    else :
                        for idb in npy.where(data_top.data[int_dec:int_att] != 0)[0]:
                            idx = idb + int_dec
                            axg.text(lon.data[idx], lat.data[idx], alt.data[idx], data_top.data[idx])
                            axg.scatter(lon.data[idx], lat.data[idx], alt.data[idx])
                        flg_top = 1
                        IHM.graph_gene.FlgTop = 1
                except :
                    print("PROBLEME AFFICHAGE TOPS!")

        if ChampSup[3].get_text() != "" :
            IHM.graph_gene.graphes[0].flg_sup_texte = 1
            data_texte = read_vect(acqid, ChampSup[3].get_text())
            for n_data in npy.arange(int_dec, int_att, 300) :
                axg.text(lon.data[n_data], lat.data[n_data], alt.data[n_data], int(data_texte.data[n_data]))

            try :
                unit_txt =  data_texte.attributes["unit"]
            except :
                unit_txt = "Inconnue"
            xlabel_texte = "Texte : " + ChampSup[3].get_text() + "(" + unit_txt + ")"
        else :
            IHM.graph_gene.graphes[0].flg_sup_texte = 0

        if ChampSup[2].get_text() != "" :
            IHM.graph_gene.graphes[0].flg_sup_couleur = 1
            data_couleur = read_vect(acqid, ChampSup[2].get_text())
#            SupMin = min(data_couleur.data[int_dec:int_att])
#            SupMax = max(data_couleur.data[int_dec:int_att])

            colormap = ['purple', 'Blue', 'Green', 'Yellow', \
                                    'Orange', 'Red', 'Brown', 'Grey']
            deb = int_dec
            nbcolor = int(IHM.graph_gene.graphes[0].nb_classe_couleur)
            cl = couleur_point(data_couleur.data[deb], IHM, lon.data[deb], lat.data[deb], alt.data[deb],
                    lon_min_en_cours, lon_max_en_cours, lat_min_en_cours, lat_max_en_cours,
                    alt_min_en_cours, alt_max_en_cours )
            cl_en_cours = cl
            if cl > 0 :
                colt = colormap[int(cl_en_cours-1)]

            for npt in npy.arange(int_dec, int_att) :
                cl = couleur_point(data_couleur.data[npt], IHM, lon.data[npt], lat.data[npt], alt.data[npt],
                        lon_min_en_cours, lon_max_en_cours, lat_min_en_cours, lat_max_en_cours,
                        alt_min_en_cours, alt_max_en_cours )

                if cl != cl_en_cours :
                    if cl_en_cours >= 0 :
                        axg.plot(lon.data[deb:npt], lat.data[deb:npt], alt.data[deb:npt], \
                                 linewidth = 3, color = colt)
                        axg.plot(lon.data[deb:npt], lat.data[deb:npt], zs = alt_min_en_cours, \
                                 zdir = 'z', linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                        axg.plot(lon.data[deb:npt], data_lat_max[deb:npt], alt.data[deb:npt], \
                                 linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                        axg.plot(data_lon_min[deb:npt], lat.data[deb:npt], alt.data[deb:npt], \
                                 linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                    cl_en_cours = cl
                    if cl_en_cours >= 0 :
                        colt = colormap[int(cl_en_cours-1)]
                    else :
                        colt = 'white'
                    deb = npt

            if cl_en_cours >= 0 :
                axg.plot(lon.data[deb:int_att], lat.data[deb:int_att], alt.data[deb:int_att], \
                           linewidth = 3, color = colt)
                axg.plot(lon.data[deb:int_att], lat.data[deb:int_att], zs = alt_min_en_cours, \
                          zdir = 'z', linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                axg.plot(lon.data[deb:int_att], data_lat_max[deb:int_att], alt.data[deb:int_att], \
                         linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                axg.plot(data_lon_min[deb:int_att], lat.data[deb:int_att], alt.data[deb:int_att], \
                         linestyle = 'dashed', color = 'grey', linewidth = 0.5)

            for n_classe in npy.arange(IHM.graph_gene.graphes[0].nb_classe_couleur) :
                font_txt = FontProperties()
                font_txt.set_size(8)
                text_leg = str(IHM.graph_gene.graphes[0].seuils_classe_couleur[int(n_classe)]) + " -> " + \
                           str(IHM.graph_gene.graphes[0].seuils_classe_couleur[int(n_classe+1)])
                axg.plot(lon.data[int_att:int_att], lat.data[int_att:int_att], alt.data[int_att:int_att], \
                           label = text_leg, linewidth = 3, color = colormap[int(n_classe)])
                axg.legend(fontsize=8, title =  ChampSup[2].get_text())

        else :
            deb = int_dec
            IHM.graph_gene.graphes[0].flg_sup_couleur = 0
            cl = couleur_point(None, IHM, lon.data[deb], lat.data[deb], alt.data[deb],
                    lon_min_en_cours, lon_max_en_cours, lat_min_en_cours, lat_max_en_cours,
                    alt_min_en_cours, alt_max_en_cours )
            cl_en_cours = cl
            if cl > 0 :
                colt = "red"

            for npt in npy.arange(int_dec, int_att) :
                cl = couleur_point(None, IHM, lon.data[npt], lat.data[npt], alt.data[npt],
                        lon_min_en_cours, lon_max_en_cours, lat_min_en_cours, lat_max_en_cours,
                        alt_min_en_cours, alt_max_en_cours )

                if cl != cl_en_cours :
                    if cl_en_cours >= 0 :
                        axg.plot(lon.data[deb:npt], lat.data[deb:npt], alt.data[deb:npt], \
                                 linewidth = 3, color = colt)
                        axg.plot(lon.data[deb:npt], lat.data[deb:npt], zs = alt_min_en_cours, \
                                 zdir = 'z', linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                        axg.plot(lon.data[deb:npt], data_lat_max[deb:npt], alt.data[deb:npt], \
                                 linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                        axg.plot(data_lon_min[deb:npt], lat.data[deb:npt], alt.data[deb:npt], \
                                 linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                    cl_en_cours = cl
                    if cl_en_cours >= 0 :
                        colt = 'red'
                    else :
                        colt = 'white'
                    deb = npt

            if cl_en_cours >= 0 :
                axg.plot(lon.data[deb:int_att], lat.data[deb:int_att], alt.data[deb:int_att], \
                           linewidth = 3, color = colt)
                axg.plot(lon.data[deb:int_att], lat.data[deb:int_att], zs = alt_min_en_cours, \
                          zdir = 'z', linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                axg.plot(lon.data[deb:int_att], data_lat_max[deb:int_att], alt.data[deb:int_att], \
                         linestyle = 'dashed', color = 'grey', linewidth = 0.5)
                axg.plot(data_lon_min[deb:int_att], lat.data[deb:int_att], alt.data[deb:int_att], \
                         linestyle = 'dashed', color = 'grey', linewidth = 0.5)

    elif  ChampVecteurs["bt_2Dh"].get_active() == True :
        if acqid != IHM.graph_gene.acqid_trace or ylim_en_cours[1] > 90 :
            xlim_en_cours = ()
            ylim_en_cours = ()

        central_lon = (lon_min_en_cours + lon_max_en_cours)/2
        central_lat = (lat_min_en_cours + lat_max_en_cours)/2
        largeur_lon = (lon_max_en_cours - lon_min_en_cours)
        largeur_lat = (lat_max_en_cours - lat_min_en_cours)
        if largeur_lat < ( largeur_lon * 0.5 ) :
           lat_min_en_cours = central_lat - largeur_lon * 0.25
           lat_max_en_cours = central_lat + largeur_lon * 0.25
        if largeur_lon < ( largeur_lat * 0.5 ) :
           lon_min_en_cours = central_lon - largeur_lat * 0.25
           lon_max_en_cours = central_lon + largeur_lat * 0.25

        IHM.graph_gene.graphes[0].dimension = "2D"
        axg = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        dn_grille = 2

        if IHM.graph_gene.Flg_2D_TerreMer == 1 :
             axg.add_feature(cfeature.LAND.with_scale('10m'), zorder=1, edgecolor='black', facecolor=cfeature.COLORS['land'],alpha=0.5)
             axg.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=1, edgecolor='black', facecolor=cfeature.COLORS['water'],alpha=0.5)
        axg.add_feature(cfeature.BORDERS.with_scale('10m'), edgecolor="dimgrey")
        axg.add_feature(cfeature.COASTLINE.with_scale('10m'),  edgecolor="black")

        axg.gridlines(draw_labels=True, linewidth=0.5, color='grey')

        if IHM.graph_gene.Flg_2D_Fleuves == 1 :
             axg.add_feature(cfeature.RIVERS.with_scale('10m'), zorder=1, edgecolor='blue')
        if IHM.graph_gene.Flg_2D_Relief == 1 :
             fname = os.path.join(os.getenv('AIDA_HOME'),  'share/common/Cartes/shapefiles/natural_earth/raster', 'HYP_50M_SR.tif')
             axg.imshow(imread(fname), origin='upper', transform=ccrs.PlateCarree(), extent=[-180, 180, -90, 90])

             axg.set_extent([lon_min_en_cours, lon_max_en_cours, lat_min_en_cours, lat_max_en_cours])
             axg.add_feature(cfeature.OCEAN.with_scale('10m'), zorder=1, edgecolor='black', facecolor=cfeature.COLORS['water'],alpha=0.5)

        if ChampVecteurs["Tops"].get_text() != "" :
            try :
                vect_top = ChampVecteurs["Tops"].get_text()
                data_top = read_vect(acqid, vect_top, alarme = 0)
                vector_time_top = data_top.attributes["ref_time"]
                date_top = read_vect(acqid, vector_time_top)

                for nt in npy.arange(len(data_top.data)) :
                    difference_time = npy.absolute(date_time.data-date_top.data[nt])
                    idx = difference_time.argmin()
                    if  difference_time[idx] < 1 :
                        res = "{0:016b}".format(int(data_top.data[nt].hex(), 16))
                        top_type = int(str(res)[0:7],2)
                        top_data = int(str(res)[7:16],2)
                        axg.text(lon.data[idx], lat.data[idx], top_data)
                        axg.scatter(lon.data[idx], lat.data[idx])
                flg_top = 1
                IHM.graph_gene.FlgTop = 1
            except :
                try :
                    data_top = read_vect(acqid, vect_top)
                    vector_time_top = data_top.attributes["ref_time"]
                    date_top = read_vect(acqid, vector_time_top)
                    if vector_time_top != vector_time_lat :
                        Message = "Affichage des TOP qu'en 1 hz"
                        Abandon(Message, Gtk.MessageType.ERROR)
                    else :
                        for idb in npy.where(data_top.data[int_dec:int_att] != 0)[0]:
                            idx = idb + int_dec
                            axg.text(lon.data[idx], lat.data[idx], data_top.data[idx])
                            axg.scatter(lon.data[idx], lat.data[idx])
                        flg_top = 1
                        IHM.graph_gene.FlgTop = 1
                except :
                    print("PAS DE FICHIER DES TOPS")

# Récupération des fond de cartes France
        if IHM.graph_gene.Flg_2D_Dep == 1 :
            fond_cartes = os.path.join(os.getenv('AIDA_HOME'), 'share/common/Cartes/shapefiles/France/FRA_dep.shp')

            shape_feature = ShapelyFeature(Reader(fond_cartes).geometries(),
                                ccrs.PlateCarree(), edgecolor='black', facecolor=(0,0,0,0))
            axg.add_feature(shape_feature)

        ylabel_texte = "Latitude"
        xlabel_texte = "Longitude"

# Calcul dimension fond de carte
#        if (lat_max - lat_min > lon_max - lon_min) :
#            dl = (lat_max - lat_min) - (lon_max - lon_min) + 2
#            latn = lat_min - 1
#            latx = lat_max + 1
#            lonn = lon_min - dl/2
#            lonx = lon_max + dl/2
#        else :
#            dl = (lon_max - lon_min) - (lat_max - lat_min) + 2
#            latn = lat_min - dl/2
#            latx = lat_max + dl/2
#            lonn = lon_min - 1
#            lonx = lon_max + 1

#        if xlim_en_cours == () :
#        xlim_en_cours = (lonn, lonx)
        axg.set_xlim(lon_min_en_cours, lon_max_en_cours)
#        if ylim_en_cours == () :
#        ylim_en_cours = (latn, latx)
        axg.set_ylim(lat_min_en_cours,lat_max_en_cours )

        axg.grid(True)
# AJOUT SUPERPOSITON

        if ChampSup[3].get_text() != "" :
            vect_sup = ChampSup[3].get_text()
            IHM.graph_gene.graphes[0].flg_sup_texte = 1
            data_texte = read_vect(acqid, vect_sup)
            if vect_sup.find('time') >= 0 or vect_sup.find('TIME') >= 0 :
                for n_data in npy.arange(int_dec, int_att, 300) :
                    axg.text(lon.data[n_data], lat.data[n_data], time.strftime('%H:%M:%S',time.gmtime(data_texte.data[n_data])))
            else :
                for n_data in npy.arange(int_dec, int_att, 300) :
                    axg.text(lon.data[n_data], lat.data[n_data], int(data_texte.data[n_data]))

            try :
                unit_txt =  data_texte.attributes["unit"]
            except :
                unit_txt = "Inconnue"
            xlabel_texte = xlabel_texte + "\n Texte : " + ChampSup[3].get_text()  + "(" + unit_txt + ")"

        else :
            IHM.graph_gene.graphes[0].flg_sup_texte = 0

        if ChampSup[2].get_text() != "" :
            IHM.graph_gene.graphes[0].flg_sup_couleur = 1
            data_couleur = read_vect(acqid, ChampSup[2].get_text())
            colormap = ['purple', 'Blue', 'Green', 'Yellow', 'Orange', 'Red', 'Brown', 'Grey']
            colormap_v = colormap[0:int(IHM.graph_gene.graphes[0].nb_classe_couleur)]
            cmap = ListedColormap(colormap_v)
            norm = BoundaryNorm(IHM.graph_gene.graphes[0].seuils_classe_couleur, cmap.N)
            points = npy.array([lon.data[int_dec:int_att], lat.data[int_dec:int_att]]).T.reshape(-1, 1, 2)
            segments = npy.concatenate([points[:-1], points[1:]], axis=1)

            lc = LineCollection(segments, cmap=cmap, norm=norm)
            lc.set_array(data_couleur.data[int_dec:int_att])
            lc.set_linewidth(3)

            axg.add_collection(lc)

            for n_classe in npy.arange(IHM.graph_gene.graphes[0].nb_classe_couleur) :
                font_txt = FontProperties()
                font_txt.set_size(8)
                text_leg = str(IHM.graph_gene.graphes[0].seuils_classe_couleur[int(n_classe)]) + " -> " + \
str(IHM.graph_gene.graphes[0].seuils_classe_couleur[int(n_classe+1)])
                axg.plot(lon.data[int_att:int_att], lat.data[int_att:int_att], \
                          label = text_leg, linewidth = 3, color = colormap[int(n_classe)])
                titre_legende = ChampSup[2].get_text() + '\n (' + data_couleur.attributes["unit"] + ')'
                axg.legend(fontsize=8, title= titre_legende)

        else :
            IHM.graph_gene.graphes[0].flg_sup_couleur = 0
            axg.plot(lon.data[int_dec:int_att], lat.data[int_dec:int_att], linewidth = 1.5, color = 'r' )

        if ChampSup[0].get_text() != "" and ChampSup[1].get_text() != "" :
            IHM.graph_gene.graphes[0].flg_sup_vent = 1
            ven_1 = read_vect(acqid, ChampSup[0].get_text())
            ven_2 = read_vect(acqid, ChampSup[1].get_text())

            if ChampSup[0].get_text()[0:5].lower() == 'ven_d' and ChampSup[1].get_text()[0:5].lower() == 'ven_f' :
                ven_e = []
                ven_n = []
                print("CONVERSION DD-FF")
                for n_pr in npy.arange(len(ven_1.data)) :
                    ven_e.append(-1.94384449*ven_2.data[n_pr]*math.sin(ven_1.data[n_pr]*3.14/180))
                    ven_n.append(-1.94384449*ven_2.data[n_pr]*math.cos(ven_1.data[n_pr]*3.14/180))
            else :
                if ven_1.attributes["unit"] == "m/s" :
                    print("CONVERSION EN KT." + ChampSup[0].get_text())
                    ven_e = ven_1.data * 1.94384449
                elif ven_1.attributes["unit"] == "kt" :
                    ven_e = ven_1.data

                    print("CONVERSION EN KT." + ChampSup[1].get_text())
                if ven_2.attributes["unit"] == "m/s" :
                    print("CONVERSION EN KT." + ChampSup[1].get_text())
                    ven_n = ven_2.data * 1.94384449
                elif ven_2.attributes["unit"] == "kt" :
                    ven_n = ven_2.data

            per_vent = IHM.graph_gene.graphes[0].periode_trace_vent
            axg.barbs(lon.data[int_dec:int_att:per_vent], lat.data[int_dec:int_att:per_vent], ven_e[int_dec:int_att:per_vent],
                       ven_n[int_dec:int_att:per_vent], length=6, pivot='tip', flip_barb=False)
            xlabel_texte = xlabel_texte + "\n vent : " + ChampSup[0].get_text() + "/" +  ChampSup[1].get_text()
        else :
            IHM.graph_gene.graphes[0].flg_sup_vent = 0


        if IHM.graph_gene.Flg_2D_Waypoints == 1 :
            print ("AFFICHAGE POINTS CARACTERISTIQUES")
            for inf_item in acq_meta.iter_items_str('POINTS_CARACTERISTIQUES') :
                wpt = AIDA.PointRep(inf_item=inf_item)
                axg.plot(wpt.lon, wpt.lat, marker='o')
                axg.text(wpt.lon, wpt.lat, str(wpt.nom))

        toggle_selector.RS = []
        toggle_selector.RS.append(RectangleSelector(axg, lambda e1, e2:line_select_callback(e1, e2, None),
                        useblit = True,
                        button = [1, 3], # don't use middle button
                        minspanx = 5, minspany = 5,
                        spancoords = 'pixels'))
        toggle_selector.RS[0].set_active(True)
        fig.canvas.mpl_connect('key_press_event', lambda e1: toggle_selector(e1, axg, lon_min, lon_max, lat_min, lat_max, None, fig, cursor))

    elif  ChampVecteurs["bt_2Dv"].get_active() == True :
        if  acqid != IHM.graph_gene.acqid_trace :
            xlim_en_cours = ()
            ylim_en_cours = ()

        axg = fig.add_axes([0.1, 0.1, 0.8, 0.8])

        alt = read_vect(acqid, vect_alt)
        vector_time_alt = alt.attributes["ref_time"]
        if vector_time_alt != vector_time_lat :
            Message = "Les vecteurs Altitude et Latitude ou Longitude doivent avoir le même ref_time"
            raise Abandon(Message, Gtk.MessageType.ERROR)
            return


        if  ChampVecteurs["2Deo"].get_active() == True :
            data_geo=lon.data
            data_txt = "Longitude"
            if  IHM.graph_gene.graphes[0].dimension != "2Dvo" :
                xlim_en_cours = ()
                ylim_en_cours = ()
            IHM.graph_gene.graphes[0].dimension = "2Dvo"
        else :
            data_geo=lat.data
            data_txt = "Latitude"
            if  IHM.graph_gene.graphes[0].dimension != "2Dva" :
                xlim_en_cours = ()
                ylim_en_cours = ()
            IHM.graph_gene.graphes[0].dimension = "2Dva"

        if ChampSup[2].get_text() != "" :
            IHM.graph_gene.graphes[0].flg_sup_couleur = 1
            data_couleur = read_vect(acqid, ChampSup[2].get_text())
            colormap = ['purple', 'Blue', 'Green', 'Yellow', 'Orange', 'Red', 'Brown', 'Grey']
            colormap_v = colormap[0:int(IHM.graph_gene.graphes[0].nb_classe_couleur)]
            cmap = ListedColormap(colormap_v)
            norm = BoundaryNorm(IHM.graph_gene.graphes[0].seuils_classe_couleur, cmap.N)
            points = npy.array([data_geo[int_dec:int_att], alt.data[int_dec:int_att]]).T.reshape(-1, 1, 2)
            segments = npy.concatenate([points[:-1], points[1:]], axis=1)

            lc = LineCollection(segments, cmap=cmap, norm=norm)
            lc.set_array(data_couleur.data[int_dec:int_att])
            lc.set_linewidth(3)

            axg.add_collection(lc)

            for n_classe in npy.arange(IHM.graph_gene.graphes[0].nb_classe_couleur) :
                font_txt = FontProperties()
                font_txt.set_size(8)
                text_leg = str(IHM.graph_gene.graphes[0].seuils_classe_couleur[int(n_classe)]) + " -> " + \
str(IHM.graph_gene.graphes[0].seuils_classe_couleur[int(n_classe+1)])
                axg.plot(data_geo[int_att:int_att], alt.data[int_att:int_att], \
                          label = text_leg, linewidth = 3, color = colormap[int(n_classe)])
                titre_legende = ChampSup[2].get_text() + '\n (' + data_couleur.attributes["unit"] + ')'
#                axg.legend(fontsize=8, title= ChampSup[2].get_text())
                axg.legend(fontsize=8, title= titre_legende)
                axg.grid(True)
        else :
            IHM.graph_gene.graphes[0].flg_sup_couleur = 0
            axg.plot(data_geo[int_dec:int_att], alt.data[int_dec:int_att],linewidth = 1.5, color = 'r')
            axg.grid(True)
            
        if ChampVecteurs["Tops"].get_text() != "" :
            try :
                vect_top = ChampVecteurs["Tops"].get_text()
                data_top = read_vect(acqid, vect_top, alarme = 0)
                vector_time_top = data_top.attributes["ref_time"]
                date_top = read_vect(acqid, vector_time_top)

                for nt in npy.arange(len(data_top.data)) :
                    difference_time = npy.absolute(date_time.data-date_top.data[nt])
                    idx = difference_time.argmin()
                    if  difference_time[idx] < 1 :
                        res = "{0:016b}".format(int(data_top.data[nt].hex(), 16))
                        top_type = int(str(res)[0:7],2)
                        top_data = int(str(res)[7:16],2)
                        axg.text(data_geo[idx], alt.data[idx], top_data)
                        axg.plot(data_geo[idx], alt.data[idx],'ro')
                flg_top = 1
                IHM.graph_gene.FlgTop = 1
            except :
                try :
                    data_top = read_vect(acqid, vect_top)
                    vector_time_top = data_top.attributes["ref_time"]
                    date_top = read_vect(acqid, vector_time_top)
                    if vector_time_top != vector_time_lat :
                        Message = "Affichage des TOP qu'en 1 hz"
                        raise Abandon(Message, Gtk.MessageType.ERROR)
                    else :
                        for idb in npy.where(data_top.data[int_dec:int_att] != 0)[0]:
                            idx = idb + int_dec
                            axg.text(data_geo[idx], alt.data[idx], data_top.data[idx])
                            axg.plot(data_geo[idx], alt.data[idx],'ro')
                        flg_top = 1
                        IHM.graph_gene.FlgTop = 1
                except :
                    print("PAS DE FICHIER DES TOPS")

        ylabel_texte = "Altitude"
        xlabel_texte = data_txt

        if ChampSup[0].get_text() != "" and ChampSup[1].get_text() != "" :
            IHM.graph_gene.graphes[0].flg_sup_vent = 1
            ven_1 = read_vect(acqid, ChampSup[0].get_text())
            ven_2 = read_vect(acqid, ChampSup[1].get_text())

            if ChampSup[0].get_text()[0:5].lower() == 'ven_d' and ChampSup[1].get_text()[0:5].lower() == 'ven_f' :
                ven_e = []
                ven_n = []
                print("CONVERSION DD-FF")
                for n_pr in npy.arange(len(ven_1.data)) :
                    ven_e.append(-1.94384449*ven_2.data[n_pr]*math.sin(ven_1.data[n_pr]*3.14/180))
                    ven_n.append(-1.94384449*ven_2.data[n_pr]*math.cos(ven_1.data[n_pr]*3.14/180))
            else :
                if ven_1.attributes["unit"] == "m/s" :
                    print("CONVERSION EN KT." + ChampSup[0].get_text())
                    ven_e = ven_1.data * 1.94384449
                elif ven_1.attributes["unit"] == "kt" :
                    ven_e = ven_1.data

                    print("CONVERSION EN KT." + ChampSup[1].get_text())
                if ven_2.attributes["unit"] == "m/s" :
                    print("CONVERSION EN KT." + ChampSup[1].get_text())
                    ven_n = ven_2.data * 1.94384449
                elif ven_2.attributes["unit"] == "kt" :
                    ven_n = ven_2.data

            per_vent = IHM.graph_gene.graphes[0].periode_trace_vent
            axg.barbs(data_geo[int_dec:int_att:per_vent], alt.data[int_dec:int_att:per_vent], ven_e[int_dec:int_att:per_vent],
                       ven_n[int_dec:int_att:per_vent], length=6, pivot='tip', flip_barb=False)
            xlabel_texte = xlabel_texte + "\n vent : " + ChampSup[0].get_text() + "/" +  ChampSup[1].get_text()
        else :
            IHM.graph_gene.graphes[0].flg_sup_vent = 0

# AJOUT SUPERPOSITON


        axg.set_ylabel(ylabel_texte)
        axg.set_xlabel(xlabel_texte)

    fig.canvas.draw()

    if IHM.graph_gene.adj_fixe != None : 
        zoom_fixe = IHM.graph_gene.adj_fixe.get_active() 
    else :
        zoom_fixe = False

    for obj in F_zoom.get_children() :
        F_zoom.remove(obj)

    B_pres = Gtk.VBox(False, 5)
    F_zoom.add(B_pres)

    if ChampVecteurs["bt_3D"].get_active() == True :
        boite_lat = Gtk.HBox(False, 0)
        B_pres.pack_start(boite_lat, False, False, 10)
        boite_lon = Gtk.HBox(False, 0)
        B_pres.pack_start(boite_lon, False, False, 10)
        boite_alt = Gtk.HBox(False, 0)
        B_pres.pack_start(boite_alt, False, False, 10)
        boite_fixe = Gtk.HBox(False, 0)
        B_pres.pack_start(boite_fixe, False, False, 10)

        adjust_latn = Gtk.Adjustment(lat_min_en_cours, lat_min-1, lat_max+2, 0.1, 1.0, 1.0)
        IHM.graph_gene.adj_lat_min = adjust_latn
        latmin = Gtk.HScale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjust_latn)
        adjust_latx = Gtk.Adjustment(lat_max_en_cours, lat_min-1, lat_max+2, 0.1, 1.0, 1.0)
        IHM.graph_gene.adj_lat_max = adjust_latx
        latmax = Gtk.HScale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjust_latx)

        adjust_lonn = Gtk.Adjustment(lon_min_en_cours, lon_min-1, lon_max+2, 0.1, 1.0, 1.0)
        IHM.graph_gene.adj_lon_min = adjust_lonn
        lonmin = Gtk.HScale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjust_lonn)
        adjust_lonx = Gtk.Adjustment(lon_max_en_cours, lon_min-1, lon_max+2, 0.1, 1.0, 1.0)
        IHM.graph_gene.adj_lon_max = adjust_lonx
        lonmax = Gtk.HScale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjust_lonx)

#        adjust_altn = Gtk.Adjustment(alt_min_en_cours, alt_min-100, alt_max+100, 10, 100, 100)
        adjust_altn = Gtk.Adjustment(alt_min_en_cours, 0, alt_max+100, 10, 100, 100)
        IHM.graph_gene.adj_alt_min = adjust_altn
        altmin = Gtk.HScale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjust_altn)
        adjust_altx = Gtk.Adjustment(alt_max_en_cours, alt_min+100, alt_max+200, 10, 100, 100)
        IHM.graph_gene.adj_alt_max = adjust_altx
        altmax = Gtk.HScale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjust_altx)

        latmin_label = Gtk.Label("Lat min")
        boite_lat.pack_start(latmin_label, False, False, 0)
        boite_lat.pack_start(latmin, True, True, 0)

        latmax_label = Gtk.Label("Lat max")
        boite_lat.pack_start(latmax_label, False, False, 0)
        boite_lat.pack_start(latmax, True, True, 0)

        lonmin_label = Gtk.Label("Lon min")
        boite_lon.pack_start(lonmin_label, False, False, 0)
        boite_lon.pack_start(lonmin, True, True, 0)

        lonmax_label = Gtk.Label("Lon max")
        boite_lon.pack_start(lonmax_label, False, False, 0)
        boite_lon.pack_start(lonmax, True, True, 0)

        altmin_label = Gtk.Label("Alt min")
        boite_alt.pack_start(altmin_label, False, False, 0)
        boite_alt.pack_start(altmin, True, True, 0)

        altmax_label = Gtk.Label("alt max")
        boite_alt.pack_start(altmax_label, False, False, 0)
        boite_alt.pack_start(altmax, True, True, 0)

        cb_fixe2 = Gtk.CheckButton("Echelle(s) fixe(s).")
        cb_fixe2.set_active(zoom_fixe)
        boite_fixe.pack_start(cb_fixe2, True, True, 0)
        IHM.graph_gene.adj_fixe = cb_fixe2

        B_pres.show_all()

    fig.canvas.draw()
    IHM.graph_gene.acqid_trace = acqid

def Tracer_serie(self, IHM, bn_canvas, ChampSaisie1, ChoixBornes, ChampSaisie2, F_pres) :

    axes = []
    data_all = []
    date_all = []

# Effacement graphe page 1
    canvas = bn_canvas.get_nth_page(0)
    fig = canvas.figure

    if IHM.graph_gene.PositionImage[0] != None or IHM.graph_gene.PositionImage[1] != None :
        fig.subplots_adjust(left = IHM.graph_gene.PositionImage[0])
        fig.subplots_adjust(right = IHM.graph_gene.PositionImage[1])
    else :
        fig.subplots_adjust(right = 0.8)

    if IHM.graph_gene.PositionImage[2] != None or IHM.graph_gene.PositionImage[3] != None :
        fig.subplots_adjust(bottom = IHM.graph_gene.PositionImage[2])
        fig.subplots_adjust(top = IHM.graph_gene.PositionImage[3])
    else :
        fig.subplots_adjust(top = 0.9)

    for ax in fig.get_axes() :
        ax.cla()
        fig.clear()

# Effacement page(s) suivante(s)
    for nb in npy.arange(1, bn_canvas.get_n_pages()) :
        bn_canvas.remove_page(1)

# Initialisation des variables pour nouvelles pages.
    NB = 0
    fig_width_cm = 21
    fig_height_cm = 29.7
    inches_per_cm = 1 / 2.58                     # Convert cm to inches
    fig_width = fig_width_cm * inches_per_cm     # width in inches
    fig_height = fig_height_cm * inches_per_cm   # height in inches
    fig_size = [fig_width, fig_height]

# Calcul nombre de graphe à tracer
    for nb in npy.arange(6) :
        cle = "Vecteur" + str(nb)
        if ChampSaisie1[cle].get_text() != "" :
            NB = NB + 1

# Calcul nombre de page
# Création des pages supplémentaires si nécessaire
    NGP = int(IHM.graph_gene.nb_graphe_par_page)
    NbPage = int(NB/NGP)
    if npy.mod(NB, NGP) > 0 :
        NbPage = NbPage + 1
    for np in npy.arange(NbPage-1) :
        fig2 = Figure(figsize = fig_size)
        fig2.subplots_adjust(right = 0.8)
        canvas2 = FigureCanvas(fig2)  # a Gtk.DrawingArea
        canvas2.set_size_request(700, 500)
        LabelPage = "Page " + str(np + 2)
        L_canvas2 = Gtk.Label(LabelPage)
        bn_canvas.append_page(canvas2, L_canvas2)
        bn_canvas.show_all()
#    bn_canvas.parent_instance.show_all()

# Recuperation information du vol dans le fichier .inf
    IHM.recup_fic_inf(ChampSaisie2, F_pres, IHM)
    acqid = IHM.graph_gene.acqid

    try :
        second_vol = date2num(IHM.graph_gene.date_acquisition)
    except :
        second_vol = 1

# Création du titre principal de la (ou des) page(s)
    try :
        pltf = AIDA.plt_by_abrev[acqid[0:2]]
    except :
        if acqid == "" :
            Message = "Saisir un acqid !"
        else :
            Message = "Acqid pas valid!"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return

    subtitre = str(ChampSaisie1["Titre"].get_text())
    soustitre = str(ChampSaisie1["SousTitre"].get_text())
    if subtitre == "" and IHM.graph_gene.TitreGraph != "" :
        ChampSaisie1["Titre"].set_text( IHM.graph_gene.TitreGraph)
        subtitre = str(IHM.graph_gene.TitreGraph)
    elif  subtitre != "" :
        IHM.graph_gene.TitreGraph = subtitre

    if soustitre != "" :
        ChampSaisie1["SousTitre"].set_text(soustitre)
        subtitre2 = soustitre
    else :
        try :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid + ' du ' + \
                       IHM.graph_gene.date_acquisition.strftime('%d/%m/%y'))
        except :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid)

    IHM.graph_gene.nb_graphe = 0

# Pour chaque page
    for npage in npy.arange(NbPage) :
        if round(NB - NGP * npage) < NGP :
            NGPl = round(NB - NGP * npage)
        else :
            NGPl = NGP
        fig = bn_canvas.get_nth_page(npage).figure

        fig.text(0.5, 0.975, subtitre, horizontalalignment = 'center', verticalalignment = 'top')
        fig.text(0.5, 0.955, subtitre2, horizontalalignment = 'center', verticalalignment = 'top')

        ngv = 0
# Pour chaque graphe de la page
        for ng in npy.arange(NGP) :
            nb = npage * NGP + ng
            cle = "Vecteur" + str(nb)
            if ChampSaisie1[cle].get_text() != "" :
                ngv = ngv + 1
                IHM.graph_gene.nb_graphe = IHM.graph_gene.nb_graphe + 1
                IHM.graph_gene.graphes[nb].vecteur_Y = ChampSaisie1[cle].get_text()
                ymax = -10000000
                ymin = 10000000
                Titre = ""

                vect = ChampSaisie1[cle].get_text().split(" ")
                if IHM.graph_gene.graphes[nb].couleur != 'None' :
                    try :
                        color_courbes_import = IHM.graph_gene.graphes[nb].couleur.split(" ")
                        flg_color_import = 1
                    except :
                        flg_color_import = 0
                else :
                    flg_color_import = 0

                if IHM.graph_gene.graphes[nb].type_trait != 'None' :
                    try :
                        type_trait = IHM.graph_gene.graphes[nb].type_trait.split(" ")
                        flg_type_trait = 1
                    except :
                        type_trait = 'Continu'
                        flg_type_trait = 0
                else :
                    type_trait = 'Continu'
                    flg_type_trait = 0

                if IHM.graph_gene.graphes[nb].axe != 'None' :
                    try :
                        axe = IHM.graph_gene.graphes[nb].axe.split(" ")
                        flg_axe = 1
                    except :
                        axe = 'gauche'
                        flg_axe = 0
                else :
                    axe = 'gauche'
                    flg_axe = 0

                if IHM.graph_gene.graphes[nb].type_mark != 'None' :
                    try :
                        type_mark = IHM.graph_gene.graphes[nb].type_mark.split(" ")
                        flg_type_mark = 1
                    except :
                        type_mark = ''
                        flg_type_mark = 0
                else :
                    mark = ''
                    flg_type_mark = 0

                if IHM.graph_gene.graphes[nb].epais_trait != 'None' :
                    try :
                        epais_trait = IHM.graph_gene.graphes[nb].epais_trait.split(" ")
                        flg_epais_trait = 1
                    except :
                        epais_trait = '0'
                        flg_epais_trait = 0
                else :
                    epais_trait = '0'
                    flg_epais_trait = 0

                if type_mark[0] == 'Aucun' :
                    mark = ''
                else :
                    mark = type_mark[0]

                type_echelle =  IHM.graph_gene.graphes[nb].type_echelle

# Pour chaque vecteur du graphe
                flg_profil = 0
                flg_axd=0
                flg_top = 0
                for nbv in npy.arange(len(vect)) :
                    if flg_profil == 1 :
                        flg_profil = 0
                        continue
                    if vect[nbv].find('-') + vect[nbv].find('+') \
                        + vect[nbv].find('*') + vect[nbv].find('/')  >= 0 :
                        data_vect = []
                        vector_time = ""
                        Unit = ""
                        cfunit = cf.Units("without")
                        Titre1 = vect[nbv]
                        vector_time, Unit , data_vect = decompose_chaine_operation(vect[nbv], acqid)
                        if vector_time == None :
                            Message = "Attention operation " + vect[nbv] + " impossible, temps differents"
                            Abandon(Message, Gtk.MessageType.ERROR)
                            break
                        dim_array = 1
                        if data_vect is None :
                            break
                    else :
                        data1 = read_vect(acqid, vect[nbv])
                        if data1 == None :
                            continue
                        
                        if len(vect) == 1 :
                            try :
                                Titre1 = data1.attributes["name"]
                            except :
                                Titre1 = vect[nbv]
                        else :
                            Titre1 = vect[nbv]

                        vector_time = data1.attributes["ref_time"]

                        try :
                           Unit = data1.attributes["unit"]
                           cfunit = cf.Units(Unit)
                        except :
                           Unit = "without"

                        try :
                            dim_array = data1.attributes["dim_array"]
                        except :
                            dim_array = 1

                        data_vect = data1.data

                    if flg_color_import == 1 :
                        try :
                            Couleur_courbe = color_courbes_import[nbv]
                        except :
                            Couleur_courbe = Config_Couleur[nbv]
                    else :
                        Couleur_courbe = Config_Couleur[nbv]

                    if flg_type_trait == 1 :
                        try :
                            trait = type_trait[nbv]
                        except :
                            trait = "Continu"
                    else :
                        trait = "Continu"

                    if flg_axe == 1 :
                        try :
                            c_axe = axe[nbv]
                        except :
                            c_axe = "Auto"
                    else :
                        c_axe = "Auto"

                    if flg_epais_trait == 1 :
                        try :
                            epais = int(epais_trait[nbv])
                        except :
                            epais = 1
                    else :
                        epais = 1

                    if flg_type_mark == 1 :
                        try :
                            mark = type_mark[nbv]
                        except :
                            mark = ""
                    else :
                        mark = " "

                    if mark == "Aucun" :
                        mark = ""

                    if trait == 'Continu' :
                        c_trait = mark + '-'
                    elif trait == 'Tiret' :
                        c_trait = mark + '--'
                    elif trait == 'Pointille' :
                        c_trait = mark + ':'
                    elif trait == 'Nuage' :
                        c_trait = mark + 'S'
                    elif trait == 'Aucun' :
                        c_trait = mark
                    else :
                        c_trait = ''

                    date = read_vect(acqid, vector_time)
                    data_date = date.data/86400 + second_vol

# conversion hhmmss en seconde
                    if IHM.graph_gene.unit_temp == "Seconde" :
                        heure = (IHM.graph_gene.E_xmin.get_text())
                        xmin = second_vol + (int(heure))/86400.
                        IHM.graph_gene.Adj_deb_trace.set_value(int(heure))
                        heure = (IHM.graph_gene.E_xmax.get_text())
                        xmax = second_vol + (int(heure))/86400.
                        IHM.graph_gene.Adj_fin_trace.set_value(int(heure))
                    elif IHM.graph_gene.unit_temp == "Heure" :
                        heure = (IHM.graph_gene.E_xmin.get_text())
                        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
                        xmin = second_vol + (hh*3600 + mm*60 + ss)/86400.
                        IHM.graph_gene.Adj_deb_trace.set_value(hh*3600 + mm*60 + ss)
                        heure = (IHM.graph_gene.E_xmax.get_text())
                        hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
                        xmax = second_vol + (hh*3600 + mm*60 + ss)/86400.
                        if xmax < xmin :
                            xmax = xmax + 1
                            hh = hh + 24
                        IHM.graph_gene.Adj_fin_trace.set_value(hh*3600 + mm*60 + ss)
                    else :
                        xmin = min(data_date)
                        xmax = max(data_date)

# Gestion des unités
# a faire : utiliser udunit+"---"s
                    if nbv == 0 :
                        unit1 = Unit
                        cfunit1 = cfunit
                        unit2 = "??"
                        nb_unit = 1
                        Titre = Titre1
                        if len(axes) == 0 :
                            axg = fig.add_subplot(NGPl, 1, ng+1)
                        else :
                            axg = fig.add_subplot(NGPl, 1, ng+1, sharex = axes[0])
                        axt = axg
                    else :
                        if cfunit1.equivalent(cfunit) :
                            print(Unit, unit1)
                            print("Unités compatible : Conversion automatique")
                            Unit = unit1
                            cf.Units.conform(data_vect, cfunit, cfunit1, inplace=True)
                        if Unit != unit1 and Unit != unit2 and nb_unit == 2 :
                            print("ALARME : Trop d'unite pour le graphe ! ")
                            break
                        if Unit == unit1 :
                            axt = axg
                        elif Unit == unit2 :
                            axt = axd
                        else :
                            if  flg_axd == 0 :
                                axd = axg.twinx()
                                flg_axd = 1
                            unit2 = Unit
                            cfunit2 = cfunit
#                            if unit2 == 'meter' :
#                                unit2 = 'm'
                            axt = axd

                        Titre = Titre + ', ' + vect[nbv]

                    if c_axe == "Droite" :
                        if flg_axd == 0 :
                            axd = axg.twinx()
                            flg_axd = 1
                        axt = axd
                    elif c_axe == "Gauche" :
                        axt = axg

                    font_titre = FontProperties()
                    font_titre.set_size(10)
                    axg.set_title(Titre, weight = 100, fontproperties = font_titre)
                    axt.set_ylabel(Unit)
                    axt.set_autoscale_on(True)

# Graduation axe X et tracé du graphe
                    if int(dim_array) == 1 :
                        if IHM.graph_gene.unit_temp == "Heure"  or IHM.graph_gene.unit_temp == "None" :
                            try :
                                axt.plot_date(data_date, data_vect, c_trait, label = vect[nbv], linewidth=epais, color = Couleur_courbe)
                                if type_echelle == 'log' :
                                    axt.set_yscale("log")
                            except :
                                Abandon("Probleme tracé série %s" % (vect), Gtk.MessageType.ERROR)
                                return

                            interv = round((xmax - xmin)*86400/10)
                            if interv < 1 : interv = 1
                            axt.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                            minorlocator   = AutoMinorLocator()
                            axt.xaxis.set_minor_locator(minorlocator)
                            fig.autofmt_xdate()
                            axt.axis([xmin, xmax, None, None])
                        else :
                            datetmp = (data_date - second_vol) *86400
                            axt.plot(datetmp, data_vect, c_trait, label = vect[nbv], linewidth=epais, color = Couleur_courbe)
                            if type_echelle == 'log' :
                                axt.set_yscale("log")
                            xmintmp = (xmin - second_vol) * 86400
                            xmaxtmp = (xmax - second_vol) * 86400
                            axt.axis([xmintmp, xmaxtmp, None, None])

                        ymin, ymax = axt.get_ylim()
                        if npy.sign(ymin) != npy.sign(ymax) :
                            axt.axhline(y = 0, linestyle = '--', linewidth = 1, color = 'black')

                        axg.legend(bbox_to_anchor = (1, 1), loc = 2, borderaxespad = 0., prop = font_titre)

                        try :
                            if flg_axd == 1 :
                                axd.legend(bbox_to_anchor = (1, 0), loc = 3, borderaxespad = 0., prop = font_titre)
                        except :
                            pass

                        axg.set_autoscaley_on(True)

                        axes.append(axt)

                        data_all.append(data_vect)
                        if IHM.graph_gene.unit_temp == "Heure" or IHM.graph_gene.unit_temp == "None" :
                            date_all.append(data_date)
                        else :
                            date_all.append(datetmp)
                    else :
                        nbct = int(dim_array)
                        try :
                            str_bornes = data1.attributes["bornes"]
                            Bornes = str_bornes.split(';')
                            if len(Bornes) == nbct :
                                flg_borne = 1
                            else :
                                flg_borne = 0
                        except :
                            flg_borne = 0

                        nbct = int(dim_array)
                        nbc = nbct
                        nbt = len(data_date)
                        grf = []
                        datX = []
                        iz = npy.arange(nbc)
                        nbd = 0
                        maxdata = 0

                        if IHM.graph_gene.Type_graphe_serie == "Image" :
                            try : 
                                Ylabel = data1.attributes["unit_bornes"]
                            except :
                                Ylabel = 'Indice'
                            
                            if Ylabel == "" :
                                Ylabel = 'Indice'

                            axg.set_ylabel(Ylabel)

                            if ChoixBornes[0].get_text() != "Auto" :
                                try :
                                    dtmin = float(ChoixBornes[0].get_text())
                                    dmin = math.log(dtmin+1, 10)
                                except :
                                    dtmin =  npy.nanmin(data1.data)
                                    dmin = math.log(dtmin+1, 10)
                            else :
                                dtmin = max(npy.nanmin(data1.data),0)
                                dmin = math.log(dtmin+1, 10)

                            if ChoixBornes[1].get_text() != "Auto" :
                                try :
                                    dtmax = float(ChoixBornes[1].get_text())
                                    dmax = math.log(dtmax+1, 10)
                                except :
                                    dtmax =  npy.nanmax(data1.data)
                                    dmax = math.log(dtmax+1, 10)
                            else :
                                dtmax = npy.nanmax(data1.data)
                                dmax = math.log(dtmax+1, 10)
                                
                            for nz in  iz :
                                ys = []
                                nbd = 0
                                for nd in  npy.arange(nbt) :
                                    if data_date[nd] > xmin and \
                                               data_date[nd] < xmax :
                                        nbd = nbd + 1
                                        if nz == 0 :
                                            datX.append((data_date[nd]-second_vol)*86400)
                                        try :
                                            dxl = math.log(data_vect[nd][nz]+1, 10)
                                        except ValueError :
                                            dxl = 0
                                        maxdata = max(maxdata, dxl)
                                        ys.append(dxl)

                                if len(ys) > 1 :
                                    grf.append(ys)

                            nbct = int(dim_array)
                            try :
                                str_bornes = data1.attributes["bornes"]
                                Bornes = npy.array(AIDA.strBornes_to_array(str_bornes))[:,:,0][0]
                                if len(Bornes) == nbct :
                                    flg_borne = 1
                                else :
                                    Bornes=npy.arange(nbct)
                                    flg_borne = 0
                            except :
                                Bornes=npy.arange(nbct)
                                flg_borne = 0

                            maxdata = maxdata+1
                            l_ticks = npy.arange(int(maxdata))
                            t_ticks = 10**l_ticks
                            interp = 'nearest'

#                            im = NonUniformImage(axg, interpolation=interp,
#                                               cmap=matplotlib.cm.YlOrBr, origin='lower')
#                            im.set_data(datX, iz, grf)
                            c = axg.pcolormesh(datX,Bornes,grf, vmin=dmin,vmax=dmax, alpha = 1.0, cmap=matplotlib.cm.YlOrBr)
#                            axg.images.append(im)
                            axg.set_ylim(0, Bornes[-1])
                            axg.set_xlim(datX[0], datX[nbd-1])
                            #fig.colorbar(c, ax=axg,  orientation='horizontal', fraction=.1) 
                            cbar = fig.colorbar(c, ticks=l_ticks, orientation='horizontal')
                            cbar.ax.set_xticklabels(t_ticks)

                        elif IHM.graph_gene.Type_graphe_serie == "Profil" :

                            flg_profil = 1
                            if vect[nbv][0:3] == 'alt' :
                                alti=data1
                                nbv = nbv + 1
                                data1=read_vect(acqid, vect[nbv])
                            else :
                                nbv = nbv + 1
                                alti=read_vect(acqid, vect[nbv])

                            try :
                                Titre = data1.attributes["english_name"]
                            except KeyError :
                                Titre = vect[nbv]
                            axg.set_title(Titre, weight = 100, fontproperties = font_titre)

                            date_sec = second_vol + date.data/86400
                            date_2D = npy.tile(date_sec,(len(alti.data[0]),1)).T
                            
                            if ChoixBornes[0].get_text() != "Auto" :
                                try :
                                    dmin = float(ChoixBornes[0].get_text())
                                except :
                                    dmin =  npy.nanmin(data1.data)
                            else :
                                dmin = npy.nanmin(data1.data)

                            if ChoixBornes[1].get_text() != "Auto" :
                                try :
                                    dmax = float(ChoixBornes[1].get_text())
                                except :
                                    dmax =  npy.nanmax(data1.data)
                            else :
                                dmax = npy.nanmax(data1.data)
                                
                            smin = npy.nanmin(date_sec)
                            smax = npy.nanmax(date_sec)

                            dataOK = npy.nan_to_num(data1.data)
                            altiOK = npy.nan_to_num(alti.data)
                            c = axg.pcolormesh(date_2D,altiOK,dataOK,vmin=dmin,vmax=dmax, alpha = 0.5, cmap=matplotlib.cm.nipy_spectral)
                            if IHM.graph_gene.unit_temp == "Heure"  or IHM.graph_gene.unit_temp == "None" :
                                axg.xaxis_date()
                                axg.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                                minorlocator   = AutoMinorLocator()
                                axg.xaxis.set_minor_locator(minorlocator)
                                fig.autofmt_xdate()

                            axg.set_xlim(xmin, xmax)
                            fig.colorbar(c, ax=axg,  orientation='horizontal', fraction=.1) 

                        elif IHM.graph_gene.Type_graphe_serie == "Cumul" :
                            cmap = matplotlib.cm.get_cmap('jet')
                            leg_line = []
                            color_line = []
                            for nz in  iz :
                                colorN = (nz+1.)/nbc
                                colorS = cmap(colorN)
                                color_line.append(colorS)
                                if flg_borne == 0 :
                                    line = "Inconnu"
                                else :
                                    line = Titre1 + " " + Bornes[nz]
                                ys = []
                                nbd = 0
                                for nd in  npy.arange(nbt) :
                                    if data_date[nd] > xmin and \
                                               data_date[nd] < xmax :
                                        nbd = nbd + 1
                                        if nz == 0 :
                                            datX.append(data_date[nd])
                                        dxl = data_vect[nd][nz]
                                        maxdata = max(maxdata, dxl)
                                        ys.append(dxl)

                                if len(ys) > 1 and math.isnan(ys[0]) == False :
                                    grf.append(ys)
                                    leg_line.append(line[57:])

                            stack_coll = axg.stackplot(datX, grf)
                            proxy_rects = [Rectangle((0, 0), 1, 1, fc=pc.get_facecolor()[0]) for pc in stack_coll]

                            axg.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                            axg.legend(proxy_rects, leg_line, bbox_to_anchor = (1, 1), loc = 2, borderaxespad = 0., prop = font_titre)
                            minorlocator   = AutoMinorLocator()
                            axg.xaxis.set_minor_locator(minorlocator)
                            fig.autofmt_xdate()
                            if len(datX) == 1 :
                                axg.set_xlim(int(datX[0]), int(datX[0]+1))
                            else :
                                axg.set_xlim(datX[0], datX[nbd-1])
                        elif IHM.graph_gene.Type_graphe_serie == "Superposition" :
                            cmap = matplotlib.cm.get_cmap('jet')
                            leg_line = []
                            for nz in  iz :
                                if flg_borne == 0 :
                                    line = "Inconnu"
                                else :
                                    #line = Titre1 + " " + Bornes[nz]
                                    line = Bornes[nz]
                                leg_line.append(line)
                                ys = []
                                nbd = 0
                                for nd in  npy.arange(nbt) :
                                    if data_date[nd] > xmin and \
                                           data_date[nd] < xmax :
                                        nbd = nbd + 1
                                        if nz == 0 :
                                            datX.append(data_date[nd])
                                        dxl = data_vect[nd][nz]
                                        maxdata = max(maxdata, dxl)
                                        ys.append(dxl)

                                if len(ys) >= 1:
                                    grf.append(ys)

                            for ng in  npy.arange(len(grf)) :
                                 colorN = (ng+1.)/len(grf)
                                 colorS = cmap(colorN)
#                                 axg.plot_date(datX, grf[ng], '-', c=colorS)
                                 axg.plot_date(datX, grf[ng], c_trait)
                            axg.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                            axg.legend(tuple(leg_line), bbox_to_anchor = (1, 1), loc = 2, borderaxespad = 0., prop = font_titre)
                            minorlocator   = AutoMinorLocator()
                            axg.xaxis.set_minor_locator(minorlocator)
                            fig.autofmt_xdate()
                            if len(datX) == 1 :
                                axg.set_xlim(int(datX[0]), int(datX[0]+1))
                            else :
                                axg.set_xlim(datX[0], datX[nbd-1])
                        axes.append(axg)

# Cas d'echelle(s) fixe(s)

            try :
                if IHM.graph_gene.graphes[ng].ylim[0] != None or IHM.graph_gene.graphes[ng].ylim[1] != None :
                    ymin =  IHM.graph_gene.graphes[ng].ylim[0]
                    ymax =  IHM.graph_gene.graphes[ng].ylim[1]
                    axg.set_ylim(ymin, ymax)

                if unit2 != "??" :
                    if IHM.graph_gene.graphes[ng].ylim[2] != None or IHM.graph_gene.graphes[ng].ylim[3] != None :
                        ymin =  IHM.graph_gene.graphes[ng].ylim[2]
                        ymax =  IHM.graph_gene.graphes[ng].ylim[3]
                        axd.set_ylim(ymin, ymax)
            except :
                continue

# Afichage des tops si demandé
    if ChampSaisie1["Tops"].get_text() != "" and flg_top == 0 :
        try :
            vect_top =  ChampSaisie1["Tops"].get_text()
            data_top = read_vect(acqid, vect_top, alarme = 0)
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
                data_top = read_vect(acqid, vect_top)
                vector_time_top = data_top.attributes["ref_time"]
                date_top = read_vect(acqid, vector_time_top)
    
                time_top = []
                top_data = []
                for nt in npy.arange(len(data_top.data)) :
                    format_top = data_top.attributes["format"]
                    if format_top == "string32" :
                        time_top.append(date_top.data[nt])
                        top_data.append(data_top.data[nt])
                    elif int(data_top.data[nt]) > 0 :
                        time_top.append(date_top.data[nt])
                        top_data.append(data_top.data[nt])
                flg_top = 1
                IHM.graph_gene.FlgTop = 1
            except :
                print("PROBLEME AFFICHAGE TOPS!")

    if IHM.graph_gene.Type_graphe_serie != "Profil" :
        cursor = SnaptoCursor(axes, date_all , data_all, bn_canvas, ngv)

    nax = -1
    for n_ax in npy.arange(len(axes)) :
        nax = nax + 1
        axt = axes[n_ax]
        ymin, ymax = axt.get_ylim()
        xmin, xmax = axt.get_xlim()
        Tymax = ymax - ( 0.05 * (ymax-ymin))
        if flg_top == 1 :
            for nt in npy.arange(len(time_top)) :
                if IHM.graph_gene.unit_temp == "Heure" :
                    topx = second_vol + time_top[nt]/86400
                    axt.axvline(x = topx, linestyle = ':')
                    if topx >= xmin and topx <= xmax :
                        axt.text(topx, Tymax, top_data[nt], {'color' : 'r', 'fontsize' : 10}, rotation = 90)
                    else :
                        axt.axvline(x = time_top[nt], linestyle = '--')
                else :
                    axt.axvline(x = time_top[nt] , linestyle = ':')
                    if time_top[nt] >= xmin and time_top[nt] <= xmax :
                        axt.text(time_top[nt], Tymax, top_data[nt], {'color' : 'r', 'fontsize' : 10}, rotation = 90)
                flg_top = 2

# Afichage des sequences si demandé
    if ChampSaisie1["Sequence"].get_active() == True :
        IHM.graph_gene.FlgSequence = 1
        try :
            acqmeta = AIDA.Inf(acqid)
            for (typ, seq) in acqmeta.iter_items_str('SEQUENCES') :
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
                    XSeqMin = second_vol+int(hd*3600+md*60+sd)/86400.
                    XSeqMax = second_vol+int(hf*3600+mf*60+sf)/86400.

                    for n_ax in npy.arange(len(axes)) :
                        axt = axes[n_ax]
                        ymin, ymax = axt.get_ylim()
                        data_poly = [(XSeqMin, ymin), (XSeqMin, ymax), (XSeqMax, ymax), (XSeqMax, ymin)]
                        poly = Polygon(data_poly, color=color, alpha=0.2)
                        axt.add_patch(poly)
        except :
            print("PROBLEME LECTURE DES SEQUENCES")

    if IHM.graph_gene.cursor_id != 0 :
        fig.canvas.mpl_disconnect(IHM.graph_gene.cursor_id)

    if IHM.graph_gene.key_id != 0 :
        for np in npy.arange(NbPage) :
            fig = bn_canvas.get_nth_page(np).figure
            fig.canvas.mpl_disconnect(IHM.graph_gene.key_id)

    for np in npy.arange(NbPage) :

        fig = bn_canvas.get_nth_page(np).figure
        IHM.graph_gene.key_id = fig.canvas.mpl_connect('key_press_event', lambda e1:key_press(e1, axes, fig, cursor, IHM))
#        if int(dim_array) == 1 :
#            cursor.idco = fig.canvas.mpl_connect('motion_notify_event', lambda e1:cursor.mouse_move(e1, axes))
#            IHM.graph_gene.cursor_id = cursor.idco
#        else :
#            if IHM.graph_gene.cursor_id != 0 :
#                fig.canvas.mpl_disconnect(cursor.idco)
        cursor.idco = fig.canvas.mpl_connect('motion_notify_event', lambda e1:cursor.mouse_move(e1, axes, IHM))
        IHM.graph_gene.cursor_id = cursor.idco
        fig.canvas.draw()
        fig.canvas.grab_focus()
        ajuste_axe_y(axes)
    IHM.graph_gene.acqid_trace = acqid

def Tracer_dsp(self, IHM, bn_canvas, ChampSaisie1, ChampSaisie2, F_pres) :

#--------------------------------------------------------------------------------------
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
        dsp = npy.zeros(int(NFFT/2+1))
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
        spectre["freq"]=npy.append( npy.fft.fftfreq(NFFT, d=1./round(fs))[0:round(NFFT/2)] , round(fs/2))

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
    def droites_log ( freq, spectre, pente = -5./3. , offset = 1) :

        d1 = npy.empty(len(freq))

        max_y = npy.max (spectre[1:])
        if ( npy.isnan(max_y) ) :  
           d1.fill(npy.nan) 
           return d1

        idx_max_y = npy.argmax(spectre[1:])

        k1 = npy.floor ( npy.log10(max_y) ) - offset 

# la premiere valeur de freq est égale à 0
# on met la valeur de la droite à nan

        d1[0] = npy.nan
        d1[1:] = npy.power(10., k1)*npy.power(freq[1:], pente) 

        return d1

#--------------------------------------------------------------------------------------


    axes = []
    data_all = []
    date_all = []
    spectre = {}


# Effacement graphe page 1
    canvas = bn_canvas.get_nth_page(0)
    fig = canvas.figure

    if IHM.graph_gene.PositionImage[0] != None or IHM.graph_gene.PositionImage[1] != None :
        fig.subplots_adjust(left = IHM.graph_gene.PositionImage[0])
        fig.subplots_adjust(right = IHM.graph_gene.PositionImage[1])
    else :
        fig.subplots_adjust(right = 0.8)

    if IHM.graph_gene.PositionImage[2] != None or IHM.graph_gene.PositionImage[3] != None :
        fig.subplots_adjust(bottom = IHM.graph_gene.PositionImage[2])
        fig.subplots_adjust(top = IHM.graph_gene.PositionImage[3])
    else :
        fig.subplots_adjust(top = 0.9)

    for ax in fig.get_axes() :
        ax.cla()
        fig.clear()

# Effacement page(s) suivante(s)
    for nb in npy.arange(1, bn_canvas.get_n_pages()) :
        bn_canvas.remove_page(1)

# Initialisation des variables pour nouvelles pages.
    NB = 0
    fig_width_cm = 21
    fig_height_cm = 29.7
    inches_per_cm = 1 / 2.58                     # Convert cm to inches
    fig_width = fig_width_cm * inches_per_cm     # width in inches
    fig_height = fig_height_cm * inches_per_cm   # height in inches
    fig_size = [fig_width, fig_height]

# Recuperation information du vol dans le fichier .inf
    IHM.recup_fic_inf(ChampSaisie2, F_pres, IHM)
    acqid = IHM.graph_gene.acqid

    try :
        second_vol = date2num(IHM.graph_gene.date_acquisition)
    except :
        second_vol = 1

# Création du titre principal de la (ou des) page(s)
    try :
        pltf = AIDA.plt_by_abrev[acqid[0:2]]
    except :
        if acqid == "" :
            Message = "Saisir un acqid !"
        else :
            Message = "Acqid pas valid!"
        raise Abandon(Message, Gtk.MessageType.ERROR)
        return

    subtitre = str(ChampSaisie1["Titre"].get_text())
    soustitre = str(ChampSaisie1["SousTitre"].get_text())
    if subtitre == "" and IHM.graph_gene.TitreGraph != "" :
        ChampSaisie1["Titre"].set_text( IHM.graph_gene.TitreGraph)
        subtitre = str(IHM.graph_gene.TitreGraph)
    elif  subtitre != "" :
        IHM.graph_gene.TitreGraph = subtitre

    if soustitre != "" :
        ChampSaisie1["SousTitre"].set_text(soustitre)
        subtitre2 = soustitre
    else :
        try :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid + ' du ' + \
                       IHM.graph_gene.date_acquisition.strftime('%d/%m/%y'))
        except :
            subtitre2 =  str(pltf.nom_serie_mesure + " " +  pltf.nom + " " + acqid)

    IHM.graph_gene.nb_graphe = 0

    canvas = bn_canvas.get_nth_page(0)
    fig = canvas.figure
    fig.subplots_adjust(right = 0.8)

    fig.text(0.5, 0.975, subtitre, horizontalalignment = 'center', verticalalignment = 'top')
    fig.text(0.5, 0.955, subtitre2, horizontalalignment = 'center', verticalalignment = 'top')

    if ChampSaisie1["Vecteur"].get_text() != "" :
        IHM.graph_gene.nb_graphe = IHM.graph_gene.nb_graphe + 1
        IHM.graph_gene.graphes[0].vecteur_Y = ChampSaisie1["Vecteur"].get_text()
        ymax = -10000000
        ymin = 10000000
        Titre = ""

        vect = ChampSaisie1["Vecteur"].get_text().split(" ")
        if IHM.graph_gene.graphes[0].couleur != 'None' :
            try :
                color_courbes_import = IHM.graph_gene.graphes[0].couleur.split(" ")
                flg_color_import = 1
            except :
                flg_color_import = 0
        else :
            flg_color_import = 0

        if IHM.graph_gene.graphes[0].type_trait != 'None' :
            try :
                type_trait = IHM.graph_gene.graphes[0].type_trait.split(" ")
                flg_type_trait = 1
            except :
                type_trait = 'Continu'
                flg_type_trait = 0
        else :
            type_trait = 'Continu'
            flg_type_trait = 0

        if IHM.graph_gene.graphes[0].type_mark != 'None' :
            try :
                type_mark = IHM.graph_gene.graphes[0].type_mark.split(" ")
                flg_type_mark = 1
            except :
                type_mark = ''
                flg_type_mark = 0
        else :
            mark = ''
            flg_type_mark = 0

        if IHM.graph_gene.graphes[0].epais_trait != 'None' :
            try :
                epais_trait = IHM.graph_gene.graphes[0].epais_trait.split(" ")
                flg_epais_trait = 1
            except :
                epais_trait = '0'
                flg_epais_trait = 0
        else :
            epais_trait = '0'
            flg_epais_trait = 0

        if type_mark[0] == 'Aucun' :
            mark = ''
        else :
            mark = type_mark[0]

# Pour chaque vecteur du graphe
        for nbv in npy.arange(len(vect)) :
            if vect[nbv].find('-') + vect[nbv].find('+') \
                + vect[nbv].find('*') + vect[nbv].find('/')  >= 0 :
                data_vect = []
                vector_time = ""
                Unit = ""
                Titre1 = vect[nbv]
                vector_time, Unit , data_vect = decompose_chaine_operation(vect[nbv], acqid)
                if vector_time == None :
                    Message = "Attention operation " + vect[nbv] + " impossible, temps differents"
                    Abandon(Message, Gtk.MessageType.ERROR)
                    break
                dim_array = 1
            else :
                data1 = read_vect(acqid, vect[nbv])
                if len(vect) == 1 :
                    try :
                        Titre1 = data1.attributes["name"]
                    except :
                        Titre1 = vect[nbv]
                else :
                    Titre1 = vect[nbv]
                vector_time = data1.attributes["ref_time"]
                try :
                    Unit = data1.attributes["unit"]
                except :
                    Unit = "Inconnue"
                dim_array = data1.attributes["dim_array"]
                data_vect = data1.data

            if flg_color_import == 1 :
                try :
                    Couleur_courbe = color_courbes_import[nbv]
                except :
                    Couleur_courbe = Config_Couleur[nbv]
            else :
                Couleur_courbe = Config_Couleur[nbv]

            if flg_type_trait == 1 :
                try :
                    trait = type_trait[nbv]
                except :
                    trait = "Continu"
            else :
                trait = "Continu"

            if flg_epais_trait == 1 :
                try :
                    epais = int(epais_trait[nbv])
                except :
                    epais = 1
            else :
                epais = 1

            if flg_type_mark == 1 :
                try :
                    mark = type_mark[nbv]
                except :
                    mark = ""
            else :
                mark = " "

            if mark == "Aucun" :
                mark = ""

            if trait == 'Continu' :
                c_trait = mark + '-'
            elif trait == 'Tiret' :
                c_trait = mark + '--'
            elif trait == 'Pointille' :
                c_trait = mark + ':'
            elif trait == 'Nuage' :
                c_trait = mark + 'S'
            elif trait == 'Aucun' :
                c_trait = mark
            else :
                c_trait = ''

            if Unit == "mbar" :
                Unit = "hPa"

            if Unit == "degres" :
                Unit = "degree"

            date = read_vect(acqid, vector_time)
            data_date = date.data/86400 + second_vol

# conversion hhmmss en seconde
            if IHM.graph_gene.unit_temp == "Seconde" :
                heure = (IHM.graph_gene.E_xmin.get_text())
                xmin = second_vol + (int(heure))/86400.
                IHM.graph_gene.Adj_deb_trace.set_value(int(heure))
                heure = (IHM.graph_gene.E_xmax.get_text())
                xmax = second_vol + (int(heure))/86400.
                IHM.graph_gene.Adj_fin_trace.set_value(int(heure))
            elif IHM.graph_gene.unit_temp == "Heure" :
                heure = (IHM.graph_gene.E_xmin.get_text())
                hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
                xmin = second_vol + (hh*3600 + mm*60 + ss)/86400.
#                if xmin > date2num(IHM.graph_gene.heure_dec) + 0.5 :
#                    xmin = xmin - 1
#                            hh =  23 - hh
                IHM.graph_gene.Adj_deb_trace.set_value(hh*3600 + mm*60 + ss)
                heure = (IHM.graph_gene.E_xmax.get_text())
                hh, mm, ss = int(heure[0:2]), int(heure[2:4]), int(heure[4:6])
                xmax = second_vol + (hh*3600 + mm*60 + ss)/86400.
                if xmax < xmin :
                    xmax = xmax + 1
                    hh = hh + 24
                IHM.graph_gene.Adj_fin_trace.set_value(hh*3600 + mm*60 + ss)
            else :
                xmin = min(data_date)
                xmax = max(data_date)

            int_dec = 0
            int_att = len(data_date)-1
            for i in npy.arange(len(data_date)) :
                if data_date[i] < xmin :
                    int_dec = i
                if data_date[i] < xmax :
                    int_att = i

# Gestion des unités
# a faire : utiliser udunit+"---"s
            if ChampSaisie1["Dsp_seul"].get_active() == True :
                nb_plot = 1
            else :
                nb_plot = 2

            if nbv == 0 :
                unit1 = Unit
                unit2 = "??"
                nb_unit = 1
                Titre = Titre1
                if len(axes) == 0 :
                    axg = fig.add_subplot(nb_plot, 1, 1)
                else :
                    axg = fig.add_subplot(nb_plot, 1, 1, sharex = axes[0])
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
                    axt = axh

                Titre = Titre + ', ' + vect[nbv]

            font_titre = FontProperties()
            font_titre.set_size(10)
            axg.set_title(Titre, weight = 100, fontproperties = font_titre)
            axt.set_ylabel(Unit)
            axt.set_autoscale_on(True)

# Graduation axe X et tracé du graphe
            if nb_plot == 2 :
                if IHM.graph_gene.unit_temp == "Heure"  or IHM.graph_gene.unit_temp == "None" :
                    try :
                        axt.plot_date(data_date, data_vect, c_trait, label = vect[nbv], linewidth=epais, color = Couleur_courbe)
                    except :
                        raise Abandon("Probleme tracé série %s" % (vect), Gtk.MessageType.ERROR)
                        return
                    interv = int((xmax - xmin)*86400/10)
                    if interv < 1 : interv = 1
                    axt.xaxis.set_major_formatter(DateFormatter("%H:%M:%S"))
                    minorlocator   = AutoMinorLocator()
                    axt.xaxis.set_minor_locator(minorlocator)
                    fig.autofmt_xdate()
                    axt.axis([xmin, xmax, None, None])
                else :
                    datetmp = (data_date - second_vol) *86400
                    axt.plot(datetmp, data_vect, c_trait, label = vect[nbv], linewidth=epais, color = Couleur_courbe)
                    xmintmp = (xmin - second_vol) * 86400
                    xmaxtmp = (xmax - second_vol) * 86400
                    axt.axis([xmintmp, xmaxtmp, None, None])

                axt.axhline(y = 0, linestyle = '--', linewidth = 1, color = 'black')

                axt.legend(bbox_to_anchor = (1, 1), loc = 2, borderaxespad = 0., prop = font_titre)

                try :
                    axh.legend(bbox_to_anchor = (1, 0), loc = 3, borderaxespad = 0., prop = font_titre)
                except :
                    pass

                axg.set_autoscaley_on(True)

                axes.append(axt)

                data_all.append(data_vect)
                if IHM.graph_gene.unit_temp == "Heure" or IHM.graph_gene.unit_temp == "None" :
                    date_all.append(data_date)
                else :
                    date_all.append(datetmp)

# PLOT DSP
            if nbv == 0 :
                ax_dsp = fig.add_subplot(nb_plot, 1, nb_plot)
                ax_dsp.set_xscale("log")
                ax_dsp.set_yscale("log")
                ax_dsp.set_xlabel('Fréquence')
                ax_dsp.set_ylabel('Power Spectral Density (dB/Hz)')
    #            axes.append(ax_dsp)
                ax_dsp.grid(True)

            fs = len(data_date[int_dec:int_att]) / ((data_date[int_att] - data_date[int_dec])*86400)
            taille_fft = min(2048, len(data_vect[int_dec:int_att])//2)

            spectre = dsp_manq (data_vect[int_dec:int_att],taille_fft , fs = fs, taux_manq_max = 0.5, dsp_fois_freq = False, recouvrement = 0, fenetre = lambda n : npy.full(n, 1.0) )

            x_part, rap_manq = remplace_val_manq (data_vect, taux_max_manq_interpol = 0.1, val_remplace = 0.0 )

            ax_dsp.plot(spectre["freq"][1:-1], spectre["dsp"][1:-1], color = Couleur_courbe, label = vect[nbv])
            ax_dsp.legend(bbox_to_anchor = (1, 0), loc = 3, borderaxespad = 0., prop = font_titre)

            if ChampSaisie1["Dsp_droite"].get_active() == True :
                d1 = droites_log (  spectre["freq"], spectre["dsp"], offset=3)
                ax_dsp.plot ( spectre["freq"], d1, '--', color=Couleur_courbe)

#
# Cas d'echelle(s) fixe(s)

        try :
            if IHM.graph_gene.graphes[0].ylim[0] != None or IHM.graph_gene.graphes[0].ylim[1] != None :
                ymin =  IHM.graph_gene.graphes[0].ylim[0]
                ymax =  IHM.graph_gene.graphes[0].ylim[1]
                axg.set_ylim(ymin, ymax)

            if unit2 != "??" :
                if IHM.graph_gene.graphes[0].ylim[2] != None or IHM.graph_gene.graphes[0].ylim[3] != None :
                    ymin =  IHM.graph_gene.graphes[0].ylim[2]
                    ymax =  IHM.graph_gene.graphes[0].ylim[3]
                    axh.set_ylim(ymin, ymax)
        except :
            pass

    cursor = SnaptoCursor(axes, date_all , data_all, bn_canvas, 2)

# Afichage des sequences si demandé
#    if ChampSaisie1["Dsp_seul"].get_active() == True :
#        IHM.graph_gene.FlgSequence = 1
#        try :
#            acqmeta = AIDA.Inf(acqid)
#            for (typ, seq) in acqmeta.iter_items_str('SEQUENCES') :
#                champs = seq.split('/')
#                if champs[0] != 'SEQUENCES' :
#                    if typ == 'palier' :
#                        color = 'Blue'
#                    if typ == 'sondage' :
#                        color = 'Red'
#                    deb = champs[1]
#                    hd = int(deb[0:2])
#                    md = int(deb[2:4])
#                    sd = int(deb[4:6])
#                    fin =  champs[2]
#                    hf = int(fin[0:2])
#                    mf = int(fin[2:4])
#                    sf = int(fin[4:6])
#                    XSeqMin = second_vol+int(hd*3600+md*60+sd)/86400.
#                    XSeqMax = second_vol+int(hf*3600+mf*60+sf)/86400.
#
#                    for n_ax in npy.arange(len(axes)) :
#                        axt = axes[n_ax]
#                        ymin, ymax = axt.get_ylim()
#                        data_poly = [(XSeqMin, ymin), (XSeqMin, ymax), (XSeqMax, ymax), (XSeqMax, ymin)]
#                        poly = Polygon(data_poly, color=color, alpha=0.2)
#                        axt.add_patch(poly)
#        except :
#            print("PROBLEME LECTURE DES SEQUENCES")

#    if IHM.graph_gene.cursor_id != 0 :
#        fig.canvas.mpl_disconnect(IHM.graph_gene.cursor_id)

    if IHM.graph_gene.cursor_id != 0 :
        fig.canvas.mpl_disconnect(cursor.idco)
        IHM.graph_gene.cursor_id = 0

    cursor.idco = fig.canvas.mpl_connect('motion_notify_event', lambda e1:cursor.mouse_move(e1, axes, IHM))
    IHM.graph_gene.cursor_id = cursor.idco

    axes.append(ax_dsp)
    if IHM.graph_gene.key_id != 0 :
        fig = bn_canvas.get_nth_page(0).figure
        fig.canvas.mpl_disconnect(IHM.graph_gene.key_id)

    IHM.graph_gene.key_id = fig.canvas.mpl_connect('key_press_event', lambda e1:key_press(e1, axes, fig, None, IHM))

    fig.canvas.draw()
    IHM.graph_gene.acqid_trace = acqid

def main(argv = None):

    pass

if __name__ == "__main__":

    main()
