#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 08:36:40 2020

@author: jacques
"""
import sys
import os
import gi
import matplotlib
from traceback import format_tb
# en mode batch, il faut pouvoir fonctionner sans DISPLAY d'ou ce qui suit :
if not os.environ.get('DISPLAY'):
    matplotlib.use('Agg')
else :
    matplotlib.use('GTK3Agg')
    from matplotlib import pyplot as plt
    gi.require_version('Gtk', '3.0') 
    from gi.repository import Gtk, GObject, Gdk, GLib # @UnresolvedImport
    gi.require_version('WebKit2', '4.0')
    from gi.repository import WebKit2 as webkit # @UnresolvedImport
    from gi.repository.GdkPixbuf import Pixbuf # @UnresolvedImport
import copy
import re
import threading
import queue
import subprocess as sub
import collections
import numpy as np
import datetime

#from math import * #@UnusedWildImport
import random

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
PYTHON_LIB = os.path.join(AH, 'lib', PYTHON_X_Y)
sys.path.append(PYTHON_LIB)
import AIDA
from vista.modele import date as vd
from vista.modele import classes as vc
from vista.vue import vistagraph as vg
from vista.vue import interface as vi
if os.environ.get('DISPLAY'):
    from vista.vue import vistaagencement as va


import AcqId

class controler :
    """
        Controle tous les évènements
    """
    def __init__(self, vue) :
        self.vue = vue
        self.documentSaved = copy.deepcopy(self.vue.document)
        self.documentVisualized = copy.deepcopy(self.vue.document)
        self.wTree = vue.wTree
        self.window = vue.window
        self.windowOperation = vue.windowOperation
        self.windowJauge = vue.windowJauge
        self.dateDebutVisualized = None
        self.dateFinVisualized = None
        self.dateMoisVisualized = None
        self.typePeriodeVisualized = 0
        self.typePeriodeSelecteur = 0
        self.dateDebutSelecteur = vue.document.dateDebut
        self.dateFinSelecteur = vue.document.dateFin
        self.dateMoisSelecteur = vue.document.dateMois
        self.preview = False
        self.consoleLock = True
        self.modified = False
        self.windowContenu = None # fenêtre d'aide
        self.threadLecture = None # thread de lecture des données
        self.queueLecture = queue.Queue() # queue qui va contenir les exceptions éventuelles du thread de lecture des données
        self.progressBarCanceled = False
        self.parametreTreestore = {} # un cache pour les treestores des parametres
        self.itersParametres = collections.defaultdict(dict) # un cache pour les iters des paramètres
        self.noEvent = False #Permet de traiter ou non les événements (utilisé quand on met à jour les widgets après sélection dans le treeview : pas d'événement à traiter dans ce cas)
        self.updateUiDocument()
        self.checkModified()
        self.updateTreeview()
        self.addCallbacks()
        
    #
    # Méthodes communes
    #
    def getComboIndex(self, w, value, pos) :
        """
            Retourne l'index d'un combobox associé à une valeur.
        """
        store = w.get_model()
        index = 0
        found = 0
        if store != None :
            for row in store :
                if (value == row[pos]) :
                    found = 1
                    break;        
                index += 1
            if ( found == 0 ) :
                index = 0
        return index 

    #
    # document
    #            
    def onFormatToggled(self, w):
        fmt = []
        if self.wTree.get_object("checkbuttonPdf").get_active() :
            fmt.append("pdf")
        if self.wTree.get_object("checkbuttonPs").get_active() :
            fmt.append("ps")
        if self.wTree.get_object("checkbuttonPng").get_active() :
            fmt.append("png")
        chn = ",".join(fmt)
        self.vue.document.getElementById(vc.Document.currentId).setValue("format", chn)
        self.checkModified()
                       
    def onRepertoireChanged(self, w):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("dest_dir", w.get_filename())
        # on affiche le chemin complet de la sélection, pas trouvé d'autre moyen
        self.noEvent = True
        w.set_uri(w.get_filename())
        self.noEvent = False
        self.checkModified()
        
    def onNomFichierChanged(self, w):
        self.vue.document.getElementById(vc.Document.currentId).setValue("dest_fic", w.get_text())
        self.checkModified()
    
    
    
    #
    # page
    #
    def onTitreChanged(self, w):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("titre", w.get_text())
        self.updateTreeview()
        self.checkModified()
        
    def onPoliceChanged(self, w) :
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("policeTitre", w.get_font_name())
        self.checkModified()
                
    def onOrientationToggled(self, w):
        if self.noEvent :
            return
        if not w.get_active() :
            return
        ori = "portrait"
        if self.wTree.get_object("radiobuttonLandscape").get_active() :
            ori = "landscape"
        self.vue.document.getElementById(vc.Document.currentId).setValue("orientation", ori)
        
        # Pour les RDV, on doit garder un carré.
        # On inverse les largeurs et hauteurs sans se préoccuper des coordonnées.
        # Pas de solution miracle (ooffice fait guère mieux).
        page = self.vue.document.getElementById(vc.Document.currentId)
        for g in page.graphiques :
            if g.type == "RDV" :
                width = g.getValue("width")
                height = g.getValue("height")                   
                g.setValue("width", height)
                g.setValue("height", width)          
        
        self.checkModified()
    
    def onButtonAgencementPressed(self, w, e):
        self.vue.ouvreFenetreAgencement()
        self.checkModified()
        
    def onLogoChanged(self, w):
        if self.noEvent :
            return
        if w.get_active() == 0 :
            logo = ""
        else :
            my_iter = w.get_active_iter()
            logo = w.get_model().get(my_iter,0)[0]
            #logo = w.get_child().get_text()
        self.vue.document.getElementById(vc.Document.currentId).setValue("logo", logo)
        self.checkModified()
        
    def onPositionLogoChanged(self, w):
        if self.noEvent :
            return
        liststore = w.get_model()
        value = w.get_active()
        position = liststore[value][1]
        self.vue.document.getElementById(vc.Document.currentId).setValue("positionLogo", position)
        self.checkModified()
    
    
    
    #
    # graphique   
    #         
    def onAutoToggled(self, w, axe):
        if self.noEvent :
            return
        if axe == 'g' :
            wea = "entryEchelleAmplitude"
            wmin = "entryEchelleMin"
            wmax = "entryEchelleMax"
            param = "echelle"
        elif axe == 'd' :
            wea = "entryEchelleAmplitudeDroite"
            wmin = "entryEchelleMinDroite"
            wmax = "entryEchelleMaxDroite"
            param = "echelleDroite"
        else :
            wea = "entryEchelleAmplitudeBas"
            wmin = "entryEchelleMinBas"
            wmax = "entryEchelleMaxBas"
            param = "echelleBas"
            
        auto = "non-auto"
        if w.get_active() :
            auto = "auto"
            self.wTree.get_object(wea).set_sensitive(True)
            self.wTree.get_object(wmin).set_sensitive(False)
            self.wTree.get_object(wmax).set_sensitive(False)
        else :
            self.wTree.get_object(wea).set_sensitive(False)
            self.wTree.get_object(wmin).set_sensitive(True)
            self.wTree.get_object(wmax).set_sensitive(True)
        self.vue.document.getElementById(vc.Document.currentId).setValue(param, auto)
        self.checkModified()
        
    def onAutoHovToggled(self, w, axe):
        if self.noEvent :
            return
        if axe == 'g' :
            wea = None
            wmin = "entryEchelleMinHov"
            wmax = "entryEchelleMaxHov"
            param = "echelle"
        else :
            wea = "entryEchelleAmplitudeDroiteHov" 
            wmin = "entryEchelleMinDroiteHov"
            wmax = "entryEchelleMaxDroiteHov"
            param = "echelleDroite"
            
        auto = "non-auto"
        if w.get_active() :
            auto = "auto"
            if wea :
                self.wTree.get_object(wea).set_sensitive(True)
            self.wTree.get_object(wmin).set_sensitive(False)
            self.wTree.get_object(wmax).set_sensitive(False)
        else :
            if wea :
                self.wTree.get_object(wea).set_sensitive(False)
            self.wTree.get_object(wmin).set_sensitive(True)
            self.wTree.get_object(wmax).set_sensitive(True)
        self.vue.document.getElementById(vc.Document.currentId).setValue(param, auto)
        self.checkModified()
        
    def onAmplitudeChanged(self, w, axe):
        if self.noEvent :
            return
        if axe == 'g' :
            param = "echelleAmplitude"
        elif axe == 'd' :
            param = "echelleAmplitudeDroite"
        else :
            param = "echelleAmplitudeBas"
        strVal = w.get_text()
        if strVal == "" :
            strVal="0.0"
        if strVal[0] == "-" and len(strVal) == 1 :
            strVal="0.0"
        try :
            value = float(strVal)
        except :
            w.set_text(strVal[0:len(strVal)-1])
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue(param, value)
        self.checkModified()
        
    def onAmplitudeHovChanged(self, w, axe):
            if self.noEvent :
                return
            # pour l'instant on ne traite que l'axe droit (Trace ST sur graphique Hov)
            param = "echelleAmplitudeDroiteHov"
            strVal = w.get_text()
            if strVal == "" :
                strVal="0.0"
            if strVal[0] == "-" and len(strVal) == 1 :
                strVal="0.0"
            try :
                value = float(strVal)
            except :
                w.set_text(strVal[0:len(strVal)-1])
                return
            self.vue.document.getElementById(vc.Document.currentId).setValue(param, value)
            self.checkModified()
            
    def onEchelleMinChanged(self, w, axe):
        if self.noEvent :
            return
        if axe == 'g' :
            param = "echelleMin"
        elif axe == 'd' :
            param = "echelleMinDroite"
        else :
            param = "echelleMinBas"
        strVal = w.get_text()
        if strVal == "" :
            strVal="0.0"
        if strVal[0] == "-" and len(strVal) == 1 :
            strVal="0.0"
        try :
            value = float(strVal)
        except :
            w.set_text(strVal[0:len(strVal)-1])
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue(param, value)
        self.checkModified()
        
    def onEchelleMaxChanged(self, w, axe):
        if self.noEvent :
            return
        if axe == 'g' :
            param = "echelleMax"
        elif axe == 'd' :
            param = "echelleMaxDroite"
        else :
            param = "echelleMaxBas"          
        strVal = w.get_text()
        if strVal == "" :
            strVal="0.0"
        if strVal[0] == "-" and len(strVal) == 1 :
            strVal="0.0"
        try :
            value = float(strVal)
        except :
            w.set_text(strVal[0:len(strVal)-1])
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue(param, value)
        self.checkModified()
        
    def onUniteGaucheToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("uniteGauche", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("uniteGauche", "non")
        self.checkModified()
        
    def onUniteDroiteToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("uniteDroite", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("uniteDroite", "non")
        self.checkModified()
        
    def onUniteBasToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("uniteBas", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("uniteBas", "non")
        self.checkModified()
    
    def onLabelsGaucheToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelsGauche", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelsGauche", "non")
        self.checkModified()
        
    def onLabelsGaucheHovChanged(self, w):
        if self.noEvent :
            return
        my_iter = w.get_active_iter()
        qtt_labels = w.get_model().get(my_iter,0)[0]
        self.vue.document.getElementById(vc.Document.currentId).setValue("labelsGaucheHov", qtt_labels)
        self.checkModified()
        
    def onLabelsDroiteToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelsDroite", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelsDroite", "non")
        self.checkModified()
        
    def onLabelsBasToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelsBas", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelsBas", "non")
        self.checkModified()
        
    def onEchelleLogGaucheToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("echelleLogGauche", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("echelleLogGauche", "non")
        self.checkModified()
        
    def onEchelleLogDroiteToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("echelleLogDroite", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("echelleLogDroite", "non")
        self.checkModified()
        
    def onEchelleLogBasToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("echelleLogBas", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("echelleLogBas", "non")
        self.checkModified()
    
    def onLegendeAidaToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            la = "oui"
        else :
            la = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("legendeAida", la)
        self.checkModified()
        
    def onGrilleToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            gr = "oui"
        else :
            gr = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("grille", gr)
        self.checkModified()
        
    def onFitDataToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            fd = "oui"
        else :
            fd = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("fitData", fd)
        self.checkModified()
        
    def onLegendeToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            leg = "oui"
            self.wTree.get_object("buttonLegendeST").set_sensitive(True)
        else :
            leg = "non"
            self.wTree.get_object("buttonLegendeST").set_sensitive(False)
        self.vue.document.getElementById(vc.Document.currentId).setValue("legendeVisible", leg)
        self.checkModified()
        
    def onLegendeClicked(self, w):
        if self.noEvent :
            return
        
        # on efface toutes les vues de legende
        box_legende = self.wTree.get_object("vboxLegende")
        for l in box_legende.get_children() :
            l.destroy()
        # et on les recrée
        graphique = self.vue.document.getElementById(vc.Document.currentId)
        for trace in graphique.traces :
            trace.setBackupCondition()
            trace.setBackupLegende()
            texte = trace.getValue("legende")
            if texte == trace.getDefault("legende") :
                texte = trace.getValue("plateforme")+":"+trace.getValue("parametre")
            self.addLegende(trace.getValue("legendeVisible"), trace.getValue("couleur"), texte, trace)
            if trace.type == "ST" :
                if len(trace.expressions_condition) > 1 :
                    for e in trace.expressions_condition :
                        self.addLegende(e["legendeVisible"], e["couleur"], e["legende"], trace, idc=e["id"])
            elif trace.type == "PlotXY" :
                if len(trace.expressions_condition) > 1 :
                    if trace.getValue("filtrageConditionnel") == "non" :
                        for e in trace.expressions_condition :
                            self.addLegende(e["legendeVisible"], e["couleur"], e["legende"], trace, idc=e["id"])
                    else :
                        for e in trace.expressions_condition[1:] :
                            self.addLegende(e["legendeVisible"], e["couleur"], e["legende"], trace, idc=e["id"])
        self.wTree.get_object("fontbuttonLegende").set_font(graphique.getValue("policeLegende"))
        self.wTree.get_object("windowLegende").show_all()
        #position de la légende
        wpos = self.wTree.get_object("comboboxPositionLegende")
        position = graphique.getValue("positionLegende").split(',')
        index = self.getComboIndex(wpos, int(position[0]), 1)
        wpos.set_active(index)

        # decalages
        wdh = self.wTree.get_object("spinbuttonDecalageLegendeHorizontal")
        wdh.set_value(int(float(position[3])*100))
        wdv = self.wTree.get_object("spinbuttonDecalageLegendeVertical")
        wdv.set_value(int(float(position[4])*100))
        
        # nombre de colonnes
        nbcol = graphique.getValue("ncolLegende")
        wnch = self.wTree.get_object("spinbuttonNbColLegende")
        wnch.set_value(int(nbcol))
        
        self.checkModified()
        
    def addLegende(self, visible, couleur, texte, trace, idc=None):
        """
            Création des widgets permettant de visualiser/modifier la légende d'un tracé
        """
        vbox_legende = self.wTree.get_object("vboxLegende")
        hbox_legende = Gtk.HBox(homogeneous=False, spacing=0)
        vbox_legende.pack_start(hbox_legende, False, False, 0)
        
        # bouton légende visible ou pas
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        image = Gtk.Image()
        if visible == "oui" :
            image.set_from_file(self.vue.dirIcons+"/visible.png")
            button.set_tooltip_text("Cliquer pour rendre la légende invisible")
        else :
            image.set_from_file(self.vue.dirIcons+"/invisible.png")
            button.set_tooltip_text("Cliquer pour rendre la légende visible")
        button.add(image)
        button.set_can_focus(False)                       
        button.connect('clicked', self.onLegendeVisiblePress, trace, idc)
        hbox_legende.pack_start(button, False, False,0)
        
        # bouton couleur
        colorbutton = vi.VistaColorButton()
        colorbutton.set_size_request(40,10)
        colorbutton.set_can_focus(False)
        colorbutton.setRgba(couleur)
        #Gdk.RGBA.parse(colorbutton.rgba, couleur) # @UndefinedVariable
        #colorbutton.modifyBackground(colorbutton.rgba)
    
        hbox_legende.pack_start(colorbutton, False, False,0)
        # zone de texte
        entry = Gtk.Entry()
        entry.set_text(texte)
        entry.connect("changed", self.onLegendeTexteChanged, trace, idc)            
        hbox_legende.pack_start(entry, True, True,10)
                               
        hbox_legende.show_all()
    
    def onLegendeTexteChanged(self, w, trace, idc):
        if idc != None : # légende associée à une condition
            trace.updateCondition(idc, legende=w.get_text())
        else :
            trace.setValue("legende", w.get_text())
            
    def onLegendeVisiblePress(self, w, trace, idc):
        if idc != None : # légende associée à une condition
            visible = trace.expressions_condition[idc]["legendeVisible"]
        else :
            visible = trace.getValue("legendeVisible")
                       
        new_image = Gtk.Image()
        if visible == "oui" :
            new_image.set_from_file(self.vue.dirIcons+"/invisible.png")
            w.set_tooltip_text("Cliquer pour rendre la légende visible")
        else :
            new_image.set_from_file(self.vue.dirIcons+"/visible.png")
            w.set_tooltip_text("Cliquer pour rendre la légende invisible")
        w.set_image(new_image)
        if visible == "oui" :
            visible = "non"
        else :
            visible = "oui"
        if idc != None : # légende associée à une condition
            trace.updateCondition(idc, legende_visible=visible)
        else :
            trace.setValue("legendeVisible", visible)
        
    def onPoliceLegendeChanged(self, w) :
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("policeLegende", w.get_font_name())
        self.checkModified()
    
    def onPositionLegendeChanged(self, w):
        if self.noEvent :
            return
        combo = self.wTree.get_object("comboboxPositionLegende")
        liststore = combo.get_model()
        value = combo.get_active()
        scale_sensitive = True
        if value == 0 : #auto => on désactive les scale de position
            self.noEvent = True
            scale_sensitive = False
            self.wTree.get_object("spinbuttonDecalageLegendeHorizontal").set_value(0)
            self.wTree.get_object("spinbuttonDecalageLegendeVertical").set_value(0)
            self.noEvent = False
        self.wTree.get_object("spinbuttonDecalageLegendeHorizontal").set_sensitive(scale_sensitive)
        self.wTree.get_object("spinbuttonDecalageLegendeVertical").set_sensitive(scale_sensitive)
        position = liststore[value][1]
        x = liststore[value][2]
        y = liststore[value][3]
        dx = self.wTree.get_object("spinbuttonDecalageLegendeHorizontal").get_value() / 100.
        dy = self.wTree.get_object("spinbuttonDecalageLegendeVertical").get_value() / 100.
        str_pos_legende = "{},{},{},{},{}".format(position, x, y, dx, dy)
        self.vue.document.getElementById(vc.Document.currentId).setValue("positionLegende", str_pos_legende)
        self.checkModified()
    
    def onNbColLegendeChanged(self, w):
        if self.noEvent :
            return
        value = int(w.get_value())
        self.vue.document.getElementById(vc.Document.currentId).setValue("ncolLegende", value)
        self.checkModified()
    
    def onAnnulerLegende(self, w):
        if self.noEvent :
            return
        graphique = self.vue.document.getElementById(vc.Document.currentId)
        for trace in graphique.traces :
            trace.restaureBackupCondition()
            trace.restaureBackupLegende()
        self.wTree.get_object("windowLegende").hide()
        self.checkModified()
    
    def onValiderLegende(self, w):
        if self.noEvent :
            return
        self.wTree.get_object("windowLegende").hide()
        self.checkModified()
        
    def onPourcentageToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            norme = "oui"
        else :
            norme = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("norme", norme)
        self.checkModified()        
    
    def onJourNuitToggled(self, w):
        if self.noEvent :
            return
        if self.wTree.get_object("checkbuttonJourNuit").get_active() :
            jn = "oui"
        else :
            jn = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("jourNuit", jn)
        self.checkModified()
        
    def onMoisAnneesToggled(self, w):
        if self.noEvent :
            return
        if self.wTree.get_object("checkbuttonMoisAnnees").get_active() :
            ma = "oui"
        else :
            ma = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("moisAnnees", ma)
        self.checkModified()
        
    def onRegressionToggled(self, w):
        if self.noEvent :
            return
        if self.wTree.get_object("checkbuttonRegression").get_active() :
            reg = "oui"
        else :
            reg = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("regression", reg)
        self.checkModified()
        
    def onXegaleYToggled(self, w):
        if self.noEvent :
            return
        if self.wTree.get_object("checkbuttonXY").get_active() :
            xy = "oui"
        else :
            xy = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("x=y", xy)
        self.checkModified()
        
    def onYegaleNToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            yn = "oui"
            self.wTree.get_object("entryYN").set_sensitive(True)
        else :
            yn = "non"
            self.wTree.get_object("entryYN").set_sensitive(False)
        self.vue.document.getElementById(vc.Document.currentId).setValue("y=n", yn)
        self.checkModified()
    
    def onYNChanged(self, w):
        if self.noEvent :
            return
        strVal = w.get_text()
        if strVal == "" :
            strVal="0.0"
        if strVal[0] == "-" and len(strVal) == 1 :
            strVal="0.0"
        try :
            value = float(strVal)
        except :
            w.set_text(strVal[0:len(strVal)-1])
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("n", value)
        self.checkModified()
    
    def onDecoupageActiverToggled(self, w):
        if self.noEvent :
            return
        wcd = self.wTree.get_object("comboboxDecoupageCouleur")
        wdj = self.wTree.get_object("radiobuttonDecoupageJour")
        wpr = self.wTree.get_object("checkbuttonDecoupagePaletteReverse")
        if w.get_active() :
            da = "oui"
            self.wTree.get_object("vboxDecoupageContainer").set_sensitive(True)               
        else :
            da = "non"
            self.wTree.get_object("vboxDecoupageContainer").set_sensitive(False)
            wcd.set_active(0)
            wdj.set_active(True)
            wpr.set_active(False)
        self.vue.document.getElementById(vc.Document.currentId).setValue("decoupageActiver", da)
        self.checkModified()
    
    def onRadiobuttonDecoupageToggled(self, w, typeDecoupage) :
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("decoupagePeriode", typeDecoupage)
        self.checkModified()
        
    def onDecoupageNombreJoursChanged(self, w) :
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("nombreJoursDecoupage", int(w.get_value())) 
        self.checkModified()
    
    def onCouleurDecoupageChanged(self, w):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("couleurDecoupage", w.get_active())
        self.checkModified()
        
    def onPaletteDecoupageReverseToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            reverse = "oui"
        else :
            reverse = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("reversePaletteDecoupage", reverse)
        self.checkModified()       
        
    def onGroupeLiaisonToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.wTree.get_object("spinbuttonGroupeLiaison").set_sensitive(True)
            groupeLiaison = int(self.wTree.get_object("spinbuttonGroupeLiaison").get_value())
            self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        else :
            self.wTree.get_object("spinbuttonGroupeLiaison").set_sensitive(False)
            groupeLiaison = self.vue.document.getElementById(vc.Document.currentId).getDefault("groupe_liaison")
            self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        self.checkModified()
    
    def onGroupeLiaisonChanged(self, w):
        if self.noEvent :
            return
        groupeLiaison = int(self.wTree.get_object("spinbuttonGroupeLiaison").get_value())
        self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        self.checkModified()
        
    def onGroupeLiaisonHisto3DToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.wTree.get_object("spinbuttonGroupeLiaisonHisto3D").set_sensitive(True)
            groupeLiaison = int(self.wTree.get_object("spinbuttonGroupeLiaisonHisto3D").get_value())
            self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        else :
            self.wTree.get_object("spinbuttonGroupeLiaisonHisto3D").set_sensitive(False)
            groupeLiaison = self.vue.document.getElementById(vc.Document.currentId).getDefault("groupe_liaison")
            self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        self.checkModified()
    
    def onGroupeLiaisonHisto3DChanged(self, w):
        if self.noEvent :
            return
        groupeLiaison = int(self.wTree.get_object("spinbuttonGroupeLiaisonHisto3D").get_value())
        self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        self.checkModified()
        
    def onGroupeLiaisonRDVToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            self.wTree.get_object("spinbuttonGroupeLiaisonRDV").set_sensitive(True)
            groupeLiaison = int(self.wTree.get_object("spinbuttonGroupeLiaisonRDV").get_value())
            self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        else :
            self.wTree.get_object("spinbuttonGroupeLiaisonRDV").set_sensitive(False)
            groupeLiaison = self.vue.document.getElementById(vc.Document.currentId).getDefault("groupe_liaison")
            self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        self.checkModified()
        
    def onGroupeLiaisonRDVChanged(self, w):
        if self.noEvent :
            return
        groupeLiaison = int(self.wTree.get_object("spinbuttonGroupeLiaisonRDV").get_value())
        self.vue.document.getElementById(vc.Document.currentId).setValue("groupe_liaison", groupeLiaison)
        self.checkModified()
        
    def onSecteursRDVChanged(self, w):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("secteursRDV", int(self.vue.secteursRDV[w.get_active()]))
        self.checkModified()
        
    def onTypeRDVChanged(self, w):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("typeRDV", w.get_active())
        self.checkModified()
        
    def onCouleurRDVChanged(self, w):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("couleurRDV", w.get_active())
        self.checkModified()
        
    def onPaletteRDVReverseToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            reverse = "oui"
        else :
            reverse = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("reversePaletteRDV", reverse)
        self.checkModified()

    def onInverseAxeYHovToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            inverse = "oui"
        else :
            inverse = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("inverseAxeYHov", inverse)
        self.checkModified()    
     
    #   
    # trace
    #
    def onPlateformeChanged(self, w, comboParam, attrplateforme, attrparametre, update = True):
        self.noEvent = True # indispensable sinon set_text() de l'entry de comboparam génère un évènement qui peut planter dans certains cas (ouverture d'un nouveau fichier avec une plateforme différente de celle en cours)
        plateforme = w.get_child().get_text()
        if plateforme not in list(self.vue.plateformes.keys()) or plateforme == "" :
            if isinstance(self.getCurrentElement(), vc.Trace) :
                if update :
                    if attrplateforme is not None :
                        self.vue.document.getElementById(vc.Document.currentId).setValue(attrplateforme, "")
                    if attrparametre is not None :
                        self.vue.document.getElementById(vc.Document.currentId).setValue(attrparametre, "")                
            treeStore = Gtk.TreeStore(str)
            self.wTree.get_object(comboParam).set_model(treeStore)
            self.wTree.get_object(comboParam).set_active(-1)
            self.wTree.get_object(comboParam).get_child().set_text("")
            self.wTree.get_object(comboParam).get_child().set_sensitive(False)
            self.noEvent = False
            return
        if update :
            if attrplateforme is not None :
                self.vue.document.getElementById(vc.Document.currentId).setValue(attrplateforme, self.vue.plateformes[plateforme]["abrev"])
        #mise à jour de la liste des paramètres 
        comboboxParametre = self.wTree.get_object(comboParam)
        comboboxParametre.get_child().set_sensitive(True)
        treeStore = Gtk.TreeStore(str)
        vecteurs = self.vue.listeVecteurs[plateforme]
        if plateforme in list(self.parametreTreestore.keys()) :
            treeStore = self.parametreTreestore[plateforme]
        else :
            for _type in sorted(vecteurs.keys()) :
                _iter = treeStore.append (None, ['%s' % _type])
                for freq in list(vecteurs[_type].keys()) :
                    iter2 = treeStore.append (_iter, ['%s' % freq])
                    for vecteur in vecteurs[_type][freq] :
                        param = vecteur[0:-4] #on enlève l'extension .vbn
                        iter3 = treeStore.append (iter2, [param])
                        self.itersParametres[self.vue.plateformes[plateforme]["abrev"]][param] = iter3
                        
            self.parametreTreestore[plateforme] = treeStore
        
        comboboxParametre.set_model(treeStore)
        comboboxParametre.set_active(-1)
        self.wTree.get_object(comboParam).get_child().set_text("")
        self.noEvent = False
        
        self.checkModified()
        
    def onParametreChanged(self, w, param):
        if self.noEvent :
            return
        model = w.get_model ()
        _iter = w.get_active_iter ()
        self.vue.document.getElementById(vc.Document.currentId).setValue(param, model.get_value(_iter, 0))
        self.vue.document.getElementById(vc.Document.currentId).setLegende()
        self.updateTreeview()
        self.checkModified()
        
    def onParametrePressed(self, w, e, combo):
        combo.popup()
        
    def onMyColorbuttonClicked(self, w, e, trace, idc):
        """
            Met à jour la couleur : dans le cas d'une condition, on passe le tracé et l'id de la condition en arguments.
        """
        if self.noEvent :
            return
        
        # on positionne les couleurs de la palette (les 5 premières toujours les mêmes, les autres en fonction des couleurs déjà utilisées)
        couleurs = []
        couleurs.append("#000000")
        couleurs.append("#FF0000")
        couleurs.append("#00FF00")
        couleurs.append("#0000FF")
        couleurs.append("#FF6B00")
        couleursUtilisees = self.vue.document.getListeCouleurs()
        for c in range(len(couleursUtilisees)) :
            if not couleursUtilisees[c] in couleurs :
                couleurs.append(couleursUtilisees[c])
    
        # on complète avec du gris
        while len(couleurs) < 20 :
            couleurs.append("#AAAAAA")
        # on limite à 20 (limite en dur de la palette gtk
        colors = couleurs[0:20]
        settings = Gtk.Settings.get_default()           
        settings.set_property("gtk-color-palette", ":".join(colors))
        
        
        # création du colordialog
        cdia = Gtk.ColorSelectionDialog(title="Select color")
        cdia.set_transient_for(self.window)
        cdia.set_title("Choisir la couleur du tracé")
        colorsel = cdia.get_color_selection()
        
        # on positionne la couleur en cours et la précédente avec la couleur du bouton
        bgcolor = Gdk.RGBA()
        Gdk.RGBA.parse(bgcolor, self.vue.document.getElementById(vc.Document.currentId).getValue("couleur"))
        
        colorsel.set_previous_rgba(bgcolor)
        colorsel.set_current_rgba(bgcolor)
        # on dit qu'on a une palette
        colorsel.set_has_palette(True)
        
        # on ouvre la boite de dialogue
        response = cdia.run()
              
        if response == Gtk.ResponseType.OK:                        
            rgba = colorsel.get_current_rgba()
            couleur = "#{:02X}{:02X}{:02X}".format(int(rgba.red*255), int(rgba.green*255), int(rgba.blue*255))
            w.setRgba(couleur)
            if trace != None and idc != None :
                trace.updateCondition(idc, couleur=couleur)
            else :
                self.vue.document.getElementById(vc.Document.currentId).setValue("couleur", couleur)
            self.checkModified()
        cdia.destroy()
        
        
        
    def onTypeLigneToggled(self, w, typeTrace="ST"):
        if self.noEvent :
            return
        trait = "-"
        if typeTrace == "ST" :
            if self.wTree.get_object("radiobuttonPointille").get_active() :
                trait = ":"
            if self.wTree.get_object("radiobuttonTirete").get_active() :
                trait = "--"
            if self.wTree.get_object("radiobuttonAucunTrait").get_active() :
                trait = "None"
        elif typeTrace == "PlotXY" :
            if self.wTree.get_object("radiobuttonPointillePlotXY").get_active() :
                trait = ":"
            if self.wTree.get_object("radiobuttonTiretePlotXY").get_active() :
                trait = "--"
            if self.wTree.get_object("radiobuttonAucunTraitPlotXY").get_active() :
                trait = "None"
        self.vue.document.getElementById(vc.Document.currentId).setValue("typeLigne", trait)
        self.checkModified()      
    
    def onEpaisseurChanged(self, w) :
        self.vue.document.getElementById(vc.Document.currentId).setValue("epaisseur", int(w.get_value())) 
        self.checkModified()
        
    def onMarqueurToggled(self, w, typeTrace="ST"):
        if self.noEvent :
            return
        point = "None"
        if (typeTrace == "ST") :
            if self.wTree.get_object("radiobuttonMarqueurCroix").get_active() :
                point = "+"
            elif self.wTree.get_object("radiobuttonMarqueurCarre").get_active() :
                point = "s"
            elif self.wTree.get_object("radiobuttonMarqueurRond").get_active() :
                point = "o"            
            elif self.wTree.get_object("radiobuttonMarqueurPoint").get_active() :
                point = "."
            elif self.wTree.get_object("radiobuttonMarqueurTriangle").get_active() :
                point = "^"
        elif (typeTrace == "PlotXY") :
            if self.wTree.get_object("radiobuttonMarqueurCroixPlotXY").get_active() :
                point = "+"
            elif self.wTree.get_object("radiobuttonMarqueurCarrePlotXY").get_active() :
                point = "s"
            elif self.wTree.get_object("radiobuttonMarqueurRondPlotXY").get_active() :
                point = "o"            
            elif self.wTree.get_object("radiobuttonMarqueurPointPlotXY").get_active() :
                point = "."
            elif self.wTree.get_object("radiobuttonMarqueurTrianglePlotXY").get_active() :
                point = "^"
            
        self.vue.document.getElementById(vc.Document.currentId).setValue("marqueur", point)
        self.checkModified()
    
    def onAffichageConditionnelClicked(self, w):
        trace = self.vue.document.getElementById(vc.Document.currentId)
        if trace.type == "ST"  or trace.type == "PlotXY" :
            self.onAffichageConditionnelStandardClicked(w)
        else :
            self.onAffichageConditionnelHistosClicked(w)
            
    def onAffichageConditionnelStandardClicked(self, w):
        if self.noEvent :
            return
        
        trace = self.vue.document.getElementById(vc.Document.currentId)
        # on backup les conditions
        trace.setBackupCondition()
        # on efface toutes les vues de variables
        box_datas = self.wTree.get_object("vboxVariablesConditions")
        for c in box_datas.get_children() :
            if c.get_name() != "hboxBandeauVariablesConditions" :
                c.destroy()
        # et on recrée les nouvelles
        
        # on crée la variable y en mode non-editable et non-deletable
        self.addVariableCondition(trace.getValue('plateforme'), trace.getValue('parametre'), trace, nom_variable = 'y', editable=False, deletable=False, update_model = False)
        # on crée la variable x en mode non-editable et non-deletable pour PlotXY
        if trace.type == "PlotXY" :
            self.addVariableCondition(trace.getValue('plateforme_x'), trace.getValue('parametre_x'), trace, nom_variable = 'x', editable=False, deletable=False, update_model = False)
    
        for d in trace.datas_condition_definition :
            self.addVariableCondition(d["plateforme"], d["parametre"], trace, nom_variable = d["nom"], update_model = False)
    
        
        # on efface toutes les vues de conditions
        box_conditions = self.wTree.get_object("vboxConditions")
        for c in box_conditions.get_children() :
            if c.get_name() != "hboxBandeauConditions" :
                c.destroy()
        # et on recrée les nouvelles           
        for e in trace.expressions_condition :
            self.addCondition(trace, e["id"], e["str"], e["couleur"], e["typeLigne"], e["epaisseur"])
        
        self.wTree.get_object("buttonAddCondition").set_sensitive(True)
        self.wTree.get_object("windowAffichageConditionnel").show_all()
        
    def onAffichageConditionnelHistosClicked(self, w):
        if self.noEvent :
            return
        
        trace = self.vue.document.getElementById(vc.Document.currentId)
        # on backup les conditions
        trace.setBackupCondition()
        # on efface toutes les vues de variables
        box_datas = self.wTree.get_object("vboxVariablesConditions")
        for c in box_datas.get_children() :
            if c.get_name() != "hboxBandeauVariablesConditions" :
                c.destroy()
        # et on recrée les nouvelles
        
        # on crée la variable y en mode non-editable et non-deletable
        self.addVariableCondition(trace.getValue('plateforme'), trace.getValue('parametre'), trace, nom_variable = 'y', editable=False, deletable=False, update_model = False)
        
        for d in trace.datas_condition_definition :
            self.addVariableCondition(d["plateforme"], d["parametre"], trace, nom_variable = d["nom"], update_model = False)
    
        
        # on efface toutes les vues de conditions
        box_conditions = self.wTree.get_object("vboxConditions")
        for c in box_conditions.get_children() :
            if c.get_name() != "hboxBandeauConditions" :
                c.destroy()
        # et on recrée la nouvelle si elle existe           
        if len(trace.expressions_condition) == 2 :
            e = trace.expressions_condition[1]
            self.addCondition(trace, e["id"], e["str"], e["couleur"], e["typeLigne"], e["epaisseur"])
            self.wTree.get_object("buttonAddCondition").set_sensitive(False)
        else :
            self.wTree.get_object("buttonAddCondition").set_sensitive(True)
        
        self.wTree.get_object("windowAffichageConditionnel").show_all()
        
    def onFiltrageConditionnelToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            filtrage = "oui"
        else :
            filtrage = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("filtrageConditionnel", filtrage)
        self.checkModified()
        
    def onCumulToggled(self, w, cumul=0):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("cumul", cumul)
        self.checkModified() 
        
    def checkConditions(self):
        """
            Vérifie les variables et la syntaxe des conditions.
        """
        def hacked(expression):
            """
                Vérifie la présence de mots clés susceptibles d'être dangereux lors d'un exec ou d'un eval
            """
            bad = ["call", "system", "open", "read", "run", "os.", "sys.","process", "command", "import", "def", "print", "map", "input"]
            for b in bad :
                if b in expression.lower() :
                    return True
            return False
        
        trace = self.vue.document.getElementById(vc.Document.currentId)
        variables = trace.datas_condition_definition
        if len(variables)>0 and len(trace.expressions_condition) < 2 :
            vi.VistaDialog("Erreur : aucune condition alors que des variables sont définies.", self.window, markup=False)
            return False
        expression_ok = True
        for c in trace.expressions_condition[1:] : # on checke pas la première réservée pour non évaluable
            if hacked(c["str"]) :
                message = "Erreur sur la condition : {}\nSuspicion de malveillance...".format(c["str"])
                vi.VistaDialog(message, self.window, markup=False)
                return False
            if c["str"].count('(') != c["str"].count(')') :
                expression_ok = False
                e = SyntaxError("Nombre de parenthèses incorrect.")
                break
            # on découpe en sous-expressions pour toutes les évaluer, ce qui n'est pas le cas dans une évaluation multi-expressions
            sous_expressions = re.split("and | or", c["str"])            
            for se in sous_expressions :
                # on rajuste les parenthèses en début et fin 
                npo = se.count('(')
                npf = se.count(')')
                if npo > npf :
                    for i in range(npo-npf) :
                        se = se+")"
                if npf > npo :
                    for i in range(npf-npo) :
                        se = "("+se
                # on teste la sous-expression sur un ensemble de jeux de données aléatoires,
                # en prenant un domaine de définition "large" (<0, =0, >0).
                expression_ok= False
                for i in range(100) :
                    # y est toujours défini (c'est la donnée du tracé)
                    random.seed()
                    y = np.ones(10)*random.randrange(-10,10)
                    # x est toujours défini pour PlotXY
                    if trace.type == "PlotXY" :
                        x = np.ones(10)*random.randrange(-10,10)
                    for v in variables :
                        exec(("{}={}".format(v["nom"], "np.ones(10)*random.randrange(-10,10)")), globals(),locals())
                    try :
                        eval(se)
                        expression_ok = True
                    except Exception :
                        pass
            if not expression_ok :
                break            
        if not expression_ok :
            message = "Erreur sur la condition : {}\nVéfifier que les variables utilisées dans l'expression sont bien définies\net que la syntaxe est correcte.\nPour plus d'informations sur la syntaxe des expressions conditionnelles,\nconsultez le chapitre \"Configurer un tracé\" de la documentation utilisateur\ndans le menu Aide.".format(c["str"])
            vi.VistaDialog(message, self.window, markup=False)
            return False    
        return True
    
    def onValiderAffichageConditionnelClicked(self, w):
        if self.noEvent :
            return
        # controle de la validité des conditions
        e = self.checkConditions()
        if e :
            self.wTree.get_object("windowAffichageConditionnel").hide()
            trace = self.vue.document.getElementById(vc.Document.currentId)
            if trace.type == "ST" or trace.type == "Histo3D" :
                buttonAffichageConditionnel = self.wTree.get_object("buttonAffichageConditionnel")
            elif  trace.type == "Histo" :
                buttonAffichageConditionnel = self.wTree.get_object("buttonAffichageConditionnelHisto")
            else :
                buttonAffichageConditionnel = self.wTree.get_object("buttonAffichageConditionnelPlotXY")
            # on initialise la légende si vide
            for e in trace.expressions_condition :
                e["legende"] = e["str"]
            image = Gtk.Image()       
            if len(trace.expressions_condition)  > 1 :
                image.set_from_pixbuf(Pixbuf.new_from_file(self.vue.dirIcons+"/affichage_conditionnel2_20x20.png"))
            else :
                image.set_from_pixbuf(Pixbuf.new_from_file(self.vue.dirIcons+"/affichage_conditionnel_20x20.png"))
            buttonAffichageConditionnel.set_image(image)
            self.checkModified()
                
    def onAnnulerAffichageConditionnelClicked(self, w):
        if self.noEvent :
            return
        self.wTree.get_object("windowAffichageConditionnel").hide()
        # on restaure les conditions 
        trace = self.vue.document.getElementById(vc.Document.currentId)
        trace.restaureBackupCondition()
        self.checkModified()
            
    def onAddVariableConditionClicked(self, w):
        if self.noEvent :
            return
        dialog_editer = self.wTree.get_object("dialogEditerVariableCondition")
        dialog_editer.show_all()
        combo_plateforme = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableCondition"), "comboboxentryPlateforme_cond")
        combo_plateforme.grab_focus()
        combo_parametre = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableCondition"), "comboboxAffichageConditionnelParametre")
        combo_parametre.set_active(-1)
        combo_parametre.get_child().set_text("")
        if combo_plateforme.get_child().get_text() == "" :
            combo_parametre.get_child().set_sensitive(False) 
        
        reponse = dialog_editer.run()
        if reponse == 1 :
            plateforme = combo_plateforme.get_child().get_text()
            if plateforme in list(self.vue.plateformes.keys()) and plateforme != "" :                    
                model = combo_parametre.get_model ()
                iter1 = combo_parametre.get_active_iter ()
                if iter1 != None :
                    parametre = model.get_value(iter1, 0)                        
                    self.addVariableCondition(self.vue.plateformes[plateforme]["abrev"], parametre, self.vue.document.getElementById(vc.Document.currentId))
                    
        dialog_editer.hide()
    
    def addVariableCondition(self, plateforme, parametre, trace, editable = True, deletable = True, nom_variable = None, update_model = True):
        """
            Met à jour le modèle (par defaut) et crée une vue
        """
        vbox_datas = self.wTree.get_object("vboxVariablesConditions")
        hbox_data = Gtk.HBox(homogeneous=False, spacing=0)
        vbox_datas.pack_start(hbox_data, False, False, 0)
        offset = 65
        
        if nom_variable is None :
            nom_variable = trace.getNomVariableCondition()
       
        if nom_variable != None :
            if update_model : 
                trace.addVariableCondition(nom_variable, plateforme, parametre)                           
            label = Gtk.Label(label="{} = {}:{}".format(nom_variable, plateforme, parametre))                     
            if editable :
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                button.set_can_focus(False)
                button.connect('clicked', self.onEditerVariableConditionClicked, hbox_data, label, trace)
                button.set_tooltip_text("Editer la variable")
                hbox = Gtk.HBox()
                button.add(hbox)
                image = Gtk.Image()
                image.set_from_icon_name('accessories-text-editor', Gtk.IconSize.BUTTON)
                hbox.pack_start(image, False, False, 0)
                hbox_data.pack_start(button, False, False, 0)
                offset = 10
            
            if deletable :
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                button.set_can_focus(False)
                button.connect('clicked', self.onDeleteVariableConditionClicked, hbox_data, nom_variable, trace)
                button.set_tooltip_text("Supprimer la variable")
                hbox = Gtk.HBox()
                button.add(hbox)
                image = Gtk.Image()
                image.set_from_icon_name('edit-delete', Gtk.IconSize.BUTTON)
                hbox.pack_start(image, False, False, 0)
                hbox_data.pack_start(button, False, False, 2)
                offset = 10
                
            hbox_data.pack_start(label, False, False, offset)
            
            hbox_data.show_all()
            vbox_datas.show_all()
    
    def onDeleteVariableConditionClicked(self, w, hbox, nom_variable, trace):
        trace.delVariableCondition(nom_variable)
        hbox.destroy()
                   
    def onEditerVariableConditionClicked(self, w, hbox, label, trace):
        dialog_editer = self.wTree.get_object("dialogEditerVariableCondition")
        tab_label = label.get_text().split("=")
        nom_variable = tab_label[0].strip()
        plateforme = tab_label[1].split(":")[0].strip()
        parametre = tab_label[1].split(":")[1].strip()
        combo_plateforme = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableCondition"), "comboboxentryPlateforme_cond")
        combo_plateforme.grab_focus()
        combo_plateforme.show_all()
        combo_parametre = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableCondition"), "comboboxAffichageConditionnelParametre")
        self.updateUiPlateformeAndParametre(self.wTree.get_object("dialogEditerVariableCondition"), "comboboxentryPlateforme_cond", "condition:"+plateforme,"comboboxAffichageConditionnelParametre" , "condition:"+parametre, None, trace)    
    
        reponse = dialog_editer.run()
        if reponse == 1 :
            plateforme = combo_plateforme.get_child().get_text()
            if plateforme in list(self.vue.plateformes.keys()) and plateforme != "" :                    
                model = combo_parametre.get_model ()
                iter1 = combo_parametre.get_active_iter ()
                if iter1 != None :
                    parametre = model.get_value(iter1, 0)
                    trace.updateVariableCondition(nom_variable, self.vue.plateformes[plateforme]["abrev"], parametre)      
                    label.set_text("{} = {}:{}".format(nom_variable, self.vue.plateformes[plateforme]["abrev"], parametre))
        dialog_editer.hide()
    
    def onAddConditionClicked(self, w):
        if self.noEvent :
            return
        
        trace = self.vue.document.getElementById(vc.Document.currentId)
        idc = trace.addCondition()
        self.addCondition(trace, idc)
        if trace.type != "ST" :
            self.wTree.get_object("buttonAddCondition").set_sensitive(False)
                
    def onDeleteConditionClicked(self, w, hbox_condition, idc, trace):
        trace.delCondition(idc)
        hbox_condition.destroy()
        if trace.type != "ST" :
            self.wTree.get_object("buttonAddCondition").set_sensitive(True)           
        
    def onConditionChanged(self, w, idc, trace):
        trace.updateCondition(idc, expression=w.get_text())
        
    def onColorbuttonConditionSet(self, w, idc, trace) :
        color = w.getColor()
        couleur = "#{:02X}{:02X}{:02X}".format(color.red/256, color.green/256, color.blue/256)
        trace.updateCondition(idc, couleur=couleur)
    
    def onEpaisseurConditionChanged(self, w, idc, trace):
        trace.updateCondition(idc, epaisseur=int(w.get_value()))
            
    def addCondition(self, trace, idc, expression="", couleur="#000000", type_ligne="-", epaisseur=1):
        """
            Création des widgets permettant de visualiser/modifier une condition
        """
        vbox_conditions = self.wTree.get_object("vboxConditions")
        hbox_condition = Gtk.HBox(homogeneous=False, spacing=0)
        vbox_conditions.pack_start(hbox_condition, False, False, 0)
        
        # boutton delete
        button = Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_can_focus(False)
        button.connect('clicked', self.onDeleteConditionClicked, hbox_condition, idc, trace)
        button.set_tooltip_text("Supprimer l'expression")
        hbox = Gtk.HBox()
        button.add(hbox)
        image = Gtk.Image()
        image.set_from_icon_name('edit-delete', Gtk.IconSize.BUTTON)
        hbox.pack_start(image, False, False, 0)            
        hbox_condition.pack_start(button, False, False,0)
        if idc == 0 :
            button.set_sensitive(False)
        # zone de texte
        entry = Gtk.Entry()
        entry.connect('changed', self.onConditionChanged, idc, trace)
        entry.set_text(expression)            
        hbox_condition.pack_start(entry, True, True,10)
        if idc == 0 :
            entry.set_sensitive(False)
        if trace.type == "ST" or trace.type == "PlotXY":
            # bouton choix couleur
            colorbutton = vi.VistaColorButton()
            colorbutton.set_tooltip_text("Modifier la couleur")
            colorbutton.set_size_request(30,30)
            colorbutton.set_can_focus(False)
            colorbutton.setRgba(couleur)
            #Gdk.RGBA.parse(colorbutton.rgba, couleur) # @UndefinedVariable
            #colorbutton.modifyBackground(colorbutton.rgba)
            colorbutton.connect("button-press-event",self.onMyColorbuttonClicked, trace, idc)
            hbox_condition.pack_start(colorbutton, False, False,0)
            # epaisseur
            adj = Gtk.Adjustment(value=1,lower=0,upper=500,step_increment=1,page_increment=5,page_size=0)
            spinbutton = Gtk.SpinButton()
            spinbutton.set_adjustment(adj)
            spinbutton.set_value(float(epaisseur))
            spinbutton.connect('changed', self.onEpaisseurConditionChanged, idc, trace)
            spinbutton.set_tooltip_text("Modifier l'épaisseur")
            hbox_condition.pack_start(spinbutton, False, False,0)
        
        hbox_condition.show_all()
        
    def onRoseStandardToggled(self, w):
        if self.noEvent :
            return
        
        if  w.get_active() :
            self.wTree.get_object("spinbuttonNombreClassesRDV").set_sensitive(False)
            self.wTree.get_object("entryAmplitudeClassesRDV").set_sensitive(False)
            self.wTree.get_object("entryAmplitudeClassesRDV").set_text("1.0")
            self.vue.document.getElementById(vc.Document.currentId).setValue("amplitudeClassesHisto", self.vue.document.getElementById(vc.Document.currentId).getDefault("amplitudeClassesHisto"))
            self.vue.document.getElementById(vc.Document.currentId).setValue("nombreClassesHisto", self.vue.document.getElementById(vc.Document.currentId).getDefault("nombreClassesHisto"))
            self.vue.document.getElementById(vc.Document.currentId).setValue("roseStandard", "oui")
            self.wTree.get_object("frameEchantillonRDV").set_sensitive(False)
            self.wTree.get_object("checkbuttonMaxRDV").set_active(False)
            self.wTree.get_object("entryMinRDV").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("minHisto"))
            self.wTree.get_object("checkbuttonInfRDV").set_active(False)
            self.wTree.get_object("checkbuttonMinRDV").set_active(False)
            self.wTree.get_object("entryMaxRDV").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("maxHisto"))
            self.wTree.get_object("checkbuttonSupRDV").set_active(False)
            
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("roseStandard", "non")
            self.wTree.get_object("frameEchantillonRDV").set_sensitive(True)
            
            
        pass
        
    def onNombreClassesHistoToggled(self, w ,histo="Histo"):
        if self.noEvent :
            return
        if  w.get_active() :
            if histo == "Histo" :
                self.wTree.get_object("spinbuttonNombreClassesHisto").set_sensitive(True)
                self.wTree.get_object("entryAmplitudeClassesHisto").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesHisto").set_text("1.0")
                self.vue.document.getElementById(vc.Document.currentId).setValue("amplitudeClassesHisto", self.vue.document.getElementById(vc.Document.currentId).getDefault("amplitudeClassesHisto"))
                self.vue.document.getElementById(vc.Document.currentId).setValue("nombreClassesHisto", int(self.wTree.get_object("spinbuttonNombreClassesHisto").get_value()))
    
            elif histo == "Histo3D" :
                self.wTree.get_object("spinbuttonNombreClassesHisto3D").set_sensitive(True)
                self.wTree.get_object("entryAmplitudeClassesHisto3D").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesHisto3D").set_text("1.0")
                self.vue.document.getElementById(vc.Document.currentId).setValue("amplitudeClassesHisto", self.vue.document.getElementById(vc.Document.currentId).getDefault("amplitudeClassesHisto"))
                self.vue.document.getElementById(vc.Document.currentId).setValue("nombreClassesHisto", int(self.wTree.get_object("spinbuttonNombreClassesHisto3D").get_value()))
            
            else :
                self.wTree.get_object("spinbuttonNombreClassesRDV").set_sensitive(True)
                self.wTree.get_object("entryAmplitudeClassesRDV").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesRDV").set_text("1.0")
                self.vue.document.getElementById(vc.Document.currentId).setValue("amplitudeClassesHisto", self.vue.document.getElementById(vc.Document.currentId).getDefault("amplitudeClassesHisto"))
                self.vue.document.getElementById(vc.Document.currentId).setValue("nombreClassesHisto", int(self.wTree.get_object("spinbuttonNombreClassesRDV").get_value()))
          
            self.checkModified()
            
    def onAmplitudeClassesHistoToggled(self, w, histo="Histo"):
        
        if self.noEvent :
            return
        if  w.get_active() :
            if histo == "Histo" :
                self.wTree.get_object("spinbuttonNombreClassesHisto").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesHisto").set_sensitive(True)
                self.vue.document.getElementById(vc.Document.currentId).setValue("amplitudeClassesHisto", float(self.wTree.get_object("entryAmplitudeClassesHisto").get_text()))
    
            elif histo == "Histo3D" :
                self.wTree.get_object("spinbuttonNombreClassesHisto3D").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesHisto3D").set_sensitive(True)
                self.vue.document.getElementById(vc.Document.currentId).setValue("amplitudeClassesHisto", float(self.wTree.get_object("entryAmplitudeClassesHisto3D").get_text()))
            
            else :
                self.wTree.get_object("spinbuttonNombreClassesRDV").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesRDV").set_sensitive(True)
                self.vue.document.getElementById(vc.Document.currentId).setValue("amplitudeClassesHisto", float(self.wTree.get_object("entryAmplitudeClassesRDV").get_text()))
    
            self.vue.document.getElementById(vc.Document.currentId).setValue("nombreClassesHisto", self.vue.document.getElementById(vc.Document.currentId).getDefault("nombreClassesHisto"))
    
            self.checkModified()
            
    def onNombreClassesHistoChanged(self, w) :
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("nombreClassesHisto", int(w.get_value()))
           
        self.checkModified()
        
    def onAmplitudeClassesHistoChanged(self, w) :
        if self.noEvent :
            return
        strVal = w.get_text()
        if strVal == "" :
            strVal="0.0"
        if strVal[0] == "-" :
            w.set_text(strVal[0:len(strVal)-1])
            return
        try :
            value = float(strVal)
        except :
            w.set_text(strVal[0:len(strVal)-1])
            return   
        self.vue.document.getElementById(vc.Document.currentId).setValue("amplitudeClassesHisto", value)
       
        self.checkModified()
    
    def onMinHistoToggled(self, w, histo="Histo"):
        if self.noEvent :
            return
        if  w.get_active() :
            if histo == "Histo" :
                self.wTree.get_object("hboxMinHisto").set_sensitive(True)
                self.wTree.get_object("entryMinHisto").set_text(self.vue.document.getElementById(vc.Document.currentId).getValue("minHisto"))
                if self.vue.document.getElementById(vc.Document.currentId).getValue("infHisto") == "oui" :
                    self.wTree.get_object("checkbuttonInfHisto").set_active(True)
                else :
                    self.wTree.get_object("checkbuttonInfHisto").set_active(False)
            elif histo == "Histo3D" :
                self.wTree.get_object("hboxMinHisto3D").set_sensitive(True)
                self.wTree.get_object("entryMinHisto3D").set_text(self.vue.document.getElementById(vc.Document.currentId).getValue("minHisto"))
                if self.vue.document.getElementById(vc.Document.currentId).getValue("infHisto") == "oui" :
                    self.wTree.get_object("checkbuttonInfHisto3D").set_active(True)
                else :
                    self.wTree.get_object("checkbuttonInfHisto3D").set_active(False)
                    
            else :
                self.wTree.get_object("hboxMinRDV").set_sensitive(True)
                self.wTree.get_object("entryMinRDV").set_text(self.vue.document.getElementById(vc.Document.currentId).getValue("minHisto"))
                if self.vue.document.getElementById(vc.Document.currentId).getValue("infHisto") == "oui" :
                    self.wTree.get_object("checkbuttonInfRDV").set_active(True)
                else :
                    self.wTree.get_object("checkbuttonInfRDV").set_active(False)
        else :
            if histo == "Histo" :
                self.wTree.get_object("hboxMinHisto").set_sensitive(False)
                self.wTree.get_object("entryMinHisto").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("minHisto"))
                self.wTree.get_object("checkbuttonInfHisto").set_active(False)
            elif histo == "Histo3D" :
                self.wTree.get_object("hboxMinHisto3D").set_sensitive(False)
                self.wTree.get_object("entryMinHisto3D").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("minHisto"))
                self.wTree.get_object("checkbuttonInfHisto3D").set_active(False)
            else :
                self.wTree.get_object("hboxMinRDV").set_sensitive(False)
                self.wTree.get_object("entryMinRDV").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("minHisto"))
                self.wTree.get_object("checkbuttonInfRDV").set_active(False)
                
    def onMaxHistoToggled(self, w, histo="Histo"):
        if self.noEvent :
            return
        if  w.get_active() :
            if histo == "Histo" :
                self.wTree.get_object("hboxMaxHisto").set_sensitive(True)
                self.wTree.get_object("entryMaxHisto").set_text(self.vue.document.getElementById(vc.Document.currentId).getValue("maxHisto"))
                if self.vue.document.getElementById(vc.Document.currentId).getValue("supHisto") == "oui" :
                    self.wTree.get_object("checkbuttonSupHisto").set_active(True)
                else :
                    self.wTree.get_object("checkbuttonSupHisto").set_active(False)
            elif histo == "Histo3D" :
                self.wTree.get_object("hboxMaxHisto3D").set_sensitive(True)
                self.wTree.get_object("entryMaxHisto3D").set_text(self.vue.document.getElementById(vc.Document.currentId).getValue("maxHisto"))
                if self.vue.document.getElementById(vc.Document.currentId).getValue("supHisto") == "oui" :
                    self.wTree.get_object("checkbuttonSupHisto3D").set_active(True)
                else :
                    self.wTree.get_object("checkbuttonSupHisto3D").set_active(False)
            else :
                self.wTree.get_object("hboxMaxRDV").set_sensitive(True)
                self.wTree.get_object("entryMaxRDV").set_text(self.vue.document.getElementById(vc.Document.currentId).getValue("maxHisto"))
                if self.vue.document.getElementById(vc.Document.currentId).getValue("supHisto") == "oui" :
                    self.wTree.get_object("checkbuttonSupRDV").set_active(True)
                else :
                    self.wTree.get_object("checkbuttonSupRDV").set_active(False)
    
        else :
            if histo == "Histo" :
                self.wTree.get_object("hboxMaxHisto").set_sensitive(False)
                self.wTree.get_object("entryMaxHisto").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("maxHisto"))
                self.wTree.get_object("checkbuttonSupHisto").set_active(False)
            elif histo == "Histo3D" :
                self.wTree.get_object("hboxMaxHisto3D").set_sensitive(False)
                self.wTree.get_object("entryMaxHisto3D").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("maxHisto"))
                self.wTree.get_object("checkbuttonSupHisto3D").set_active(False)
            else :
                self.wTree.get_object("hboxMaxRDV").set_sensitive(False)
                self.wTree.get_object("entryMaxRDV").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("maxHisto"))
                self.wTree.get_object("checkbuttonSupRDV").set_active(False)
                                
    def onMinHistoChanged(self, w):
        if self.noEvent :
            return
        strVal = w.get_text()
        if strVal != "" :
            if strVal[0] == "-" and len(strVal) == 1 :
                strVal="0.0"
            try :
                value = float(strVal)
            except :
                w.set_text(strVal[0:len(strVal)-1])
                return
            self.vue.document.getElementById(vc.Document.currentId).setValue("minHisto", str(value))
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("minHisto", strVal)
    
        self.checkModified()
        
    def onMaxHistoChanged(self, w):
        if self.noEvent :
            return
        strVal = w.get_text()
        if strVal != "" :
            if strVal[0] == "-" and len(strVal) == 1 :
                strVal="0.0"
            try :
                value = float(strVal)
            except :
                w.set_text(strVal[0:len(strVal)-1])
                return
            self.vue.document.getElementById(vc.Document.currentId).setValue("maxHisto", str(value))
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("maxHisto", strVal)
    
        self.checkModified()
        
    def onInfHistoToggled(self, w):
        if self.noEvent :
            return
        if  w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("infHisto", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("infHisto", "non")
            
        self.checkModified()
        
    def onSupHistoToggled(self, w):
        if self.noEvent :
            return
        if  w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("supHisto", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("supHisto", "non")
        self.checkModified()
    
    def onLabelNombreHistoToggled(self, w):
        if self.noEvent :
            return
        if  w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelNombreHisto", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelNombreHisto", "non")
        self.checkModified()
        
    def onLabelPourcentHistoToggled(self, w):
        if self.noEvent :
            return
        if  w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelPourcentHisto", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("labelPourcentHisto", "non")
        self.checkModified()
        
    def onLargeurHisto3DChanged(self, w) :
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("largeurBarre", int(w.get_value()))               
        self.checkModified()
                     
    def onEpaisseurHisto3DChanged(self, w) :
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("epaisseurBarre", int(w.get_value()))              
        self.checkModified()
    
    def onAxeYToggled(self, w, axe_y=0):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("axe_y", axe_y)
        self.checkModified()
        
    def onCouleurHovChanged(self, w):
        if self.noEvent :
            return
        self.vue.document.getElementById(vc.Document.currentId).setValue("couleurHov", w.get_active())
        self.checkModified()
        
    def onPaletteHovReverseToggled(self, w):
        if self.noEvent :
            return
        if w.get_active() :
            reverse = "oui"
        else :
            reverse = "non"
        self.vue.document.getElementById(vc.Document.currentId).setValue("reversePaletteHov", reverse)
        self.checkModified()   
        
    def onTypeHovToggled(self, w):
        if self.noEvent :
            return
        if not w.get_active() and isinstance(w, Gtk.RadioButton) :
            return
        
        # type de diagramme
        discret = self.wTree.get_object("radiobuttonHovDiscret").get_active()
        auto = self.wTree.get_object("checkbuttonHovAuto").get_active()
        shading = self.wTree.get_object("checkbuttonHovShading").get_active()
        iso = self.wTree.get_object("checkbuttonHovIsolignes").get_active()
        
        if discret :
            self.wTree.get_object("hboxHovShading").set_sensitive(False)
            self.wTree.get_object("hboxHovAuto").set_sensitive(True)
            if auto :
                typeHov = "auto"
                self.wTree.get_object("hboxLargeurHov").set_sensitive(False)
                
            else :
                typeHov = "{}%".format(int(self.wTree.get_object("spinbuttonLargeurHov").get_value()))
                self.wTree.get_object("hboxLargeurHov").set_sensitive(True)
        else :
            self.wTree.get_object("hboxHovShading").set_sensitive(True)
            self.wTree.get_object("hboxHovAuto").set_sensitive(False)
            if shading and iso :                        
                typeHov = "iso-shading"
            else :
                if shading :
                    typeHov = "shading"
                else :
                    typeHov = "iso"                  
        
        self.vue.document.getElementById(vc.Document.currentId).setValue("typeHov", typeHov)                        
        self.checkModified()
        
    def onLargeurHovChanged(self, w):
        if self.noEvent :
            return
        typeHov = "{}%".format(int(self.wTree.get_object("spinbuttonLargeurHov").get_value()))
        self.vue.document.getElementById(vc.Document.currentId).setValue("typeHov", typeHov)
        self.checkModified()
    
    def onSeuilAutoHovToggled(self, w) :
        if self.noEvent :
            return
        if w.get_active() :
            self.wTree.get_object("hboxHovSeuil").set_sensitive(False)
            self.wTree.get_object("entryHovSeuilMin").set_text(str(self.vue.document.getElementById(vc.Document.currentId).getDefault("seuilMinHov")))
            self.wTree.get_object("entryHovSeuilMax").set_text(str(self.vue.document.getElementById(vc.Document.currentId).getDefault("seuilMaxHov")))
            self.wTree.get_object("checkbuttonHovHorsGammeVisible").set_active(False)
            self.vue.document.getElementById(vc.Document.currentId).setValue("seuilAutoHov", "oui")
        else :
            self.wTree.get_object("hboxHovSeuil").set_sensitive(True)
            self.vue.document.getElementById(vc.Document.currentId).setValue("seuilAutoHov", "non")
        self.checkModified()
    
    def onSeuilMinHovChanged(self, w) :
        if self.noEvent :
            return
        strVal = w.get_text()
        if strVal == "" :
            strVal="0.0"
        if strVal[0] == "-" and len(strVal) == 1 :
            strVal="0.0"
        self.vue.document.getElementById(vc.Document.currentId).setValue("seuilMinHov", float(strVal))
        self.checkModified()
        
    def onSeuilMaxHovChanged(self, w) :
        if self.noEvent :
            return
        strVal = w.get_text()
        if strVal == "" :
            strVal="0.0"
        if strVal[0] == "-" and len(strVal) == 1 :
            strVal="0.0"
        self.vue.document.getElementById(vc.Document.currentId).setValue("seuilMaxHov", float(strVal))
        self.checkModified()
        
    def onHovHorsGammeVisibleToggled(self, w) :
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("horsGammeVisibleHov", "oui")
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("horsGammeVisibleHov", "non")
        self.checkModified()

    def onQuiverToggled(self, w) :
        if self.noEvent :
            return
        if w.get_active() :
            self.vue.document.getElementById(vc.Document.currentId).setValue("quiverHov", "oui")
            self.wTree.get_object("frameHovQuiver").set_sensitive(True)
        else :
            self.vue.document.getElementById(vc.Document.currentId).setValue("quiverHov", "non")
            self.wTree.get_object("frameHovQuiver").set_sensitive(False)
        self.checkModified() 
        
    def onHovModeQuiverToggled(self, w):
        if self.noEvent :
            return
        if not w.get_active() and isinstance(w, Gtk.RadioButton) :
            return
        
        # mode quiver
        dd_ff = self.wTree.get_object("radiobuttonHovQuiverDdFf").get_active()
        if dd_ff :
            self.wTree.get_object("hboxParametreHovQuiverDd").set_sensitive(True)
            self.wTree.get_object("hboxParametreHovQuiverFf").set_sensitive(True)
            self.wTree.get_object("hboxParametreHovQuiverU").set_sensitive(False)
            self.wTree.get_object("hboxParametreHovQuiverV").set_sensitive(False)
            self.vue.document.getElementById(vc.Document.currentId).setValue("quiverModeUVHov", "non") 
        else :
            self.wTree.get_object("hboxParametreHovQuiverU").set_sensitive(True)
            self.wTree.get_object("hboxParametreHovQuiverV").set_sensitive(True)
            self.wTree.get_object("hboxParametreHovQuiverDd").set_sensitive(False)
            self.wTree.get_object("hboxParametreHovQuiverFf").set_sensitive(False)
            self.vue.document.getElementById(vc.Document.currentId).setValue("quiverModeUVHov", "oui")                  
                                 
        self.checkModified()  
        
    def onHovQuiverEchantillonXChanged(self, w):
        if self.noEvent :
            return
        my_iter = w.get_active_iter()
        echantillon = w.get_model().get(my_iter,0)[0]
        self.vue.document.getElementById(vc.Document.currentId).setValue("echantillonHovQuiverX", echantillon)
        self.checkModified()

    def onHovQuiverEchantillonYChanged(self, w):
        if self.noEvent :
            return
        my_iter = w.get_active_iter()
        echantillon = w.get_model().get(my_iter,0)[0]
        self.vue.document.getElementById(vc.Document.currentId).setValue("echantillonHovQuiverY", echantillon)
        self.checkModified()
    
    #
    #menu
    #
    def onEnregistrer(self, w):
        if self.vue.document.fichier == vc.Document.fichierDefaut :
            self.onEnregistrerSous(w)
            return
        try :
            self.vue.document.setValue("version_vista", vi.version)
            self.documentVisualized.setValue("version_vista", vi.version)
            self.vue.document.saveConfig(self.vue.document.fichier)
        except RuntimeError as e :
            vi.VistaDialog(str(e), self.window)
            return
        self.documentSaved = copy.deepcopy(self.vue.document)
        self.checkModified()
        
    def onEnregistrerSous(self, w):           
        dialog = Gtk.FileChooserDialog(title="Sélectionez un fichier", parent=self.window, action=Gtk.FileChooserAction.SAVE)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            save = True
            self.vue.document.fichier = dialog.get_filename()
            if not self.vue.document.fichier.endswith(".vista") :
                self.vue.document.fichier += ".vista"
            if os.path.exists(self.vue.document.fichier) :
                save = vi.VistaQuestionDialog("<b>Un fichier nommé \"{}\" existe déjà.\n\nVoulez-vous le remplacer?</b>".format(self.vue.document.fichier), self.window).getReponse()
            
            if save :                   
                try :
                    self.vue.document.setValue("version_vista", vi.version)
                    self.documentVisualized.setValue("version_vista", vi.version)
                    self.vue.document.saveConfig(self.vue.document.fichier)
                except RuntimeError as e :
                    dialog.destroy()
                    vi.VistaDialog(str(e), self.window)
                    return
                self.documentSaved = copy.deepcopy(self.vue.document)
                self.window.set_title("Vista - {}".format(self.vue.document.fichier))
            
        elif response == Gtk.ResponseType.CANCEL:
            pass
    
        dialog.destroy()
        self.checkModified()
    
    def onAjouter(self, w, typ):
        selection = self.vue.treeview.get_selection()
        tree_model, tree_iter = selection.get_selected()
        idElmt = tree_model.get_value(tree_iter, 1)
        #model
        elmt = self.vue.document.getElementById(idElmt)
        # ajouter sur un tracé provoque l'ajout d'un tracé après
        if isinstance(elmt, vc.Trace) :
            self.onInserer(self.vue.treeview, False, typ)
            return
        
        newElmt = elmt.appendNew(typ)
        if not newElmt :
            return
        
        #mise à jour de la vue
        elmt = self.vue.gdocument.getElementById(idElmt)
        _ = elmt.appendNew(newElmt)               
        newIter = self.vue.treestore.append(tree_iter, ["",newElmt.id])
        path = self.vue.treestore.get_path(tree_iter)
        self.vue.treeview.expand_row(path, False)
        self.vue.treeview.get_selection().select_iter(newIter)
        path = self.vue.treestore.get_path(newIter)
        self.vue.treeview.set_cursor( path, None, 0)
        
        self.updateTreeview()
        self.checkModified()
        
    def onSupprimer(self, w):
        selection = self.vue.treeview.get_selection()
        tree_model, tree_iter = selection.get_selected()
        iterParent = tree_model.iter_parent(tree_iter)
        idElmt = tree_model.get_value(tree_iter, 1)
        #model
        if self.vue.document.removeElement(idElmt) :         
            self.vue.treestore.remove(tree_iter)
            self.vue.treeview.get_selection().select_iter(iterParent)
            tree_model, tree_iter = selection.get_selected()
            # mise à jour de la vue
            self.vue.gdocument.removeElement(idElmt)
        self.updateTreeview()
        self.checkModified()
            
    
    def onVisualiser(self, w) :
        if self.vue.document.dateDebut > self.vue.document.dateFin :
            message = "La date de début doit être antérieure à la date de fin."
            vi.VistaDialog(message, self.window)
            return
        
        pagesNonValidees = self.vue.gdocument.checkAgencement()
        if len(pagesNonValidees) != 0 :
            message = "L'agencement des graphiques dans les pages suivantes n'a pas été validé :\n"
            for p in pagesNonValidees :
                message += "page {}\n".format(p)
            message += "\nUtiliser l'outil de mise en page pour y remédier."
            vi.VistaDialog(message, self.window)
            return
        
        self.setCursor(Gdk.CursorType.WATCH)  # @UndefinedVariable
        self.vue.document.initLecture()
        self.progressBarCanceled = False
        self.vue.document.arretLecture = False
        self.threadLecture = threading.Thread(target=self.vue.document.updateData, args=(self.queueLecture,))
        self.threadLecture.start()
        self.openProgressBar()
        try :
            exc = self.queueLecture.get(block=False)
        except queue.Empty :
            pass
        else :
            traces = ['\nTraceback (most recent call last):\n']
            traces = traces + format_tb(exc[2])
            raise RuntimeError(str(exc[1])+' '.join(traces))
        
        self.updateNotebookVista(self.vue.gdocument.getNumPage(self.getCurrentId()))
        self.documentVisualized = copy.deepcopy(self.vue.document)
        self.dateDebutVisualized = self.vue.document.dateDebut
        self.dateFinVisualized = self.vue.document.dateFin
        self.dateMoisVisualized = self.vue.document.dateMois
        self.typePeriodeVisualized = self.vue.document.typePeriode
        self.setCursor(None)
        if self.vue.document.messageUpdate != "" :
            vi.VistaDialog(self.vue.document.messageUpdate, self.window)
        self.checkModified()
        
        
    def onReload(self, w):
        self.vue.document.reloadDatas()
        self.onVisualiser(w)
            
    def onDeleteWindow(self, w, e) :
        onquitte = vi.VistaQuestionDialog("<b>Etes-vous sûrs de vouloir quitter Vista ?</b>", self.window).getReponse()
        if onquitte :
            if self.checkModifiedSinceLastSave() :
                save = vi.VistaQuestionDialog("<b>Le fichier \"{}\" a été modifié.\n\nVoulez-vous l'enregistrer ?</b>".format(self.vue.document.fichier), self.window).getReponse()
                if save :
                    self.onEnregistrer(w) 
            Gtk.main_quit()
        return(True)
        
    def onQuitter(self, w) :
        onquitte = vi.VistaQuestionDialog("<b>Etes-vous sûrs de vouloir quitter Vista ?</b>", self.window).getReponse()
        if onquitte :                
            if self.checkModifiedSinceLastSave() :
                save = vi.VistaQuestionDialog("<b>Le fichier \"{}\" a été modifié.\n\nVoulez-vous l'enregistrer ?</b>".format(self.vue.document.fichier), self.window).getReponse()
                if save :
                    self.onEnregistrer(w)
            Gtk.main_quit()
        
    def onNouveau(self, w, checkModified=True) :
        if checkModified :
            if self.checkModifiedSinceLastSave() :
                save = vi.VistaQuestionDialog("<b>Le fichier \"{}\" a été modifié.\n\nVoulez-vous l'enregistrer ?</b>".format(self.vue.document.fichier), self.window).getReponse()
                if save :
                    self.onEnregistrer(w)
                    
        try :
            self.vue.document = vc.Document("DATA", "{}", vi.version)
        except RuntimeError as e :
            vi.VistaDialog(str(e), self.window)
            return
        #dates du document
        self.vue.document.typePeriode = self.typePeriodeSelecteur
        if self.vue.document.typePeriode == 0 : #mois
            self.vue.document.dateMois = self.dateMoisSelecteur
            self.vue.document.dateDebut, self.vue.document.dateFin = vd.debutFinMois(self.vue.document.dateMois)
        else :
            self.vue.document.dateDebut = self.dateDebutSelecteur
            self.vue.document.dateFin = self.dateFinSelecteur
        
        self.documentSaved = copy.deepcopy(self.vue.document)
        self.documentVisualized = copy.deepcopy(self.vue.document)
        self.vue.treestore = Gtk.TreeStore(str, int)
        self.vue.setTreeSTore()            
        self.vue.treeview.set_model(self.vue.treestore)
        self.vue.treeview.grab_focus()
        self.vue.gdocument = vg.Gdocument(self.vue.document)
        self.vue.gdocument.zoom = self.getZoom()
        self.vue.getChildByName(self.window, "comboboxentryPlateforme").set_active(0)
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_x").set_active(0)
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_y").set_active(0)
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_h").set_active(0)
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_rdv").set_active(0)
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov").set_active(0)
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver").set_active(0)
        
        message = self.vue.gdocument.draw()
        self.updateNotebookVista(1)
        self.checkModified()
        if message != "" :
            vi.VistaDialog(message, self.window)
        
    def onOuvrir(self, w):
        if self.checkModifiedSinceLastSave() :
            save = vi.VistaQuestionDialog("<b>Le fichier \"{}\" a été modifié.\n\nVoulez-vous l'enregistrer ?</b>".format(self.vue.document.fichier), self.window).getReponse()
            if save :
                self.onEnregistrer(w)            
        dialog = Gtk.FileChooserDialog(title="Sélectionez un fichier", parent=self.window, action=Gtk.FileChooserAction.OPEN)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)           
        filtre = Gtk.FileFilter()
        Gtk.Buildable.set_name(filtre, "vista")
        filtre.add_pattern("*.json")
        filtre.add_pattern("*.vista")
        Gtk.FileChooser.add_filter(dialog, filtre)
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            #isBatch = self.vue.document.batch
            # On crée un document vide pour effacer un éventuel document déjà ouvert.
            self.onNouveau(w, checkModified=False)
            
            # on crée le nouveau document à partir du fichier 
            try :
                self.vue.document = vc.Document("FICHIER", dialog.get_filename(), vi.version)
                if self.vue.document.compatible == 1 :
                    vi.VistaDialog(self.vue.document.message, self.window)
                elif self.vue.document.compatible == 2 :
                    vi.VistaDialog(self.vue.document.message, self.window)
                    self.documentSaved = copy.deepcopy(self.vue.document)
                    dialog.destroy()
                    return
            except RuntimeError as e :
                dialog.destroy()
                vi.VistaDialog(str(e), self.window)
                return
            
            self.vue.document.batch = False
            self.documentSaved = copy.deepcopy(self.vue.document)
            self.documentVisualized = copy.deepcopy(self.vue.document)
            #dates du document
            self.vue.document.typePeriode = self.typePeriodeSelecteur
            if self.vue.document.typePeriode == 0 : #mois
                self.vue.document.dateMois = self.dateMoisSelecteur
                self.vue.document.dateDebut, self.vue.document.dateFin = vd.debutFinMois(self.vue.document.dateMois)
            else :
                self.vue.document.dateDebut = self.dateDebutSelecteur
                self.vue.document.dateFin = self.dateFinSelecteur
            #pour le checkmodified ...
            self.typePeriodeVisualized = self.typePeriodeSelecteur
            self.dateDebutVisualized = self.dateDebutSelecteur
            self.dateFinVisualized = self.dateFinSelecteur
            self.dateMoisVisualized = self.dateMoisSelecteur
    
            self.window.set_title("Vista - {}".format(self.vue.document.fichier))
            self.vue.treestore = Gtk.TreeStore(str, int)
            self.vue.setTreeSTore()            
            self.vue.treeview.set_model(self.vue.treestore)
            self.vue.treeview.grab_focus()
            self.vue.gdocument = vg.Gdocument(self.vue.document)
            self.vue.gdocument.zoom = self.getZoom()
            oldNoEvent = self.noEvent
            self.noEvent=True
            self.vue.getChildByName(self.window, "comboboxentryPlateforme").set_active(0)
            self.vue.getChildByName(self.window, "comboboxentryPlateforme_x").set_active(0)
            self.vue.getChildByName(self.window, "comboboxentryPlateforme_y").set_active(0)
            self.vue.getChildByName(self.window, "comboboxentryPlateforme_h").set_active(0)
            self.vue.getChildByName(self.window, "comboboxentryPlateforme_rdv").set_active(0)
            self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov").set_active(0)
            self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver").set_active(0)
            
            self.noEvent=oldNoEvent
            self.documentSaved = copy.deepcopy(self.vue.document)
            self.documentVisualized = copy.deepcopy(self.vue.document)
            self.checkModified()
        elif response == Gtk.ResponseType.CANCEL:
            pass
    
        dialog.destroy()
        
    def onItemBarreOutilToggled(self, w):
        if w.get_active() :
            self.wTree.get_object("hboxToolbar").set_visible(True)
        else :
            self.wTree.get_object("hboxToolbar").set_visible(False)
            
    def onItemConsoleToggled(self, w):
        allocpaned = self.wTree.get_object("vpanedVista").get_allocation()
    
        if w.get_active() :
            self.wTree.get_object("vpanedVista").set_position(allocpaned.height -80)
            self.consoleLock = False
            self.wTree.get_object("buttonViderConsole").set_visible(True)
            self.wTree.get_object("buttonFermerConsole").set_visible(True)
            self.wTree.get_object("buttonOuvrirConsole").set_visible(False)
            self.wTree.get_object("buttonInfoConsole").set_visible(False)
        else :
            self.wTree.get_object("vpanedVista").set_position(allocpaned.height-25)
            self.consoleLock = True
            self.wTree.get_object("buttonViderConsole").set_visible(False)
            self.wTree.get_object("buttonFermerConsole").set_visible(False)
            self.wTree.get_object("buttonOuvrirConsole").set_visible(True)
            self.wTree.get_object("buttonInfoConsole").set_visible(False)
        
    def onExporterPdf(self, w):
        self.setCursor(Gdk.CursorType.WATCH)  # @UndefinedVariable
        self.vue.document.updateData()
        message = self.vue.gdocument.exportPdf()
        self.updateNotebookVista(self.vue.gdocument.getNumPage(self.getCurrentId()))# pour raffraichir sinon pb avec zoom matplot
        self.setCursor(None)
        if message != "" :
            vi.VistaDialog(message, self.window)
        else :
            dest_dir =self.vue.document.getValue("dest_dir")
            vi.VistaDialog("L'export au format .pdf est terminé.\nLe fichier est disponible sous {}.".format(dest_dir), self.window)
    
    def onExporterPng(self, w):
        self.setCursor(Gdk.CursorType.WATCH) # @UndefinedVariable
        self.vue.document.updateData()
        message = self.vue.gdocument.exportPng()
        self.updateNotebookVista(self.vue.gdocument.getNumPage(self.getCurrentId()))# pour raffraichir sinon pb avec zoom matplot
        self.setCursor(None)
        if message != "" :
            vi.VistaDialog(message, self.window)
        else :
            dest_dir =self.vue.document.getValue("dest_dir")
            vi.VistaDialog("L'export au format .png est terminé.\nLe fichier est disponible sous {}.".format(dest_dir), self.window)
    
    def onExporterPs(self, w):
        self.setCursor(Gdk.CursorType.WATCH) # @UndefinedVariable
        self.vue.document.updateData()
        message = self.vue.gdocument.exportPs()
        self.updateNotebookVista(self.vue.gdocument.getNumPage(self.getCurrentId()))# pour raffraichir sinon pb avec zoom matplot
        self.setCursor(None)
        if message != "" :
            vi.VistaDialog(message, self.window)
        else :
            dest_dir =self.vue.document.getValue("dest_dir")
            vi.VistaDialog("L'export au format .ps est terminé.\nLe fichier est disponible sous {}.".format(dest_dir), self.window)
                        
    def onImprimer(self, w):
        if len(self.vue.document.pages) == 0 :
            return
        settings = None
        print_op = Gtk.PrintOperation()
        
        if settings != None: 
            print_op.set_print_settings(settings)            
        print_op.connect("begin_print", self.beginPrint)
        print_op.connect("preview", self.printPreview)            
        res = print_op.run(Gtk.PrintOperationAction.PRINT_DIALOG, self.window)            
        if res == Gtk.PrintOperationResult.APPLY:
            settings = print_op.get_print_settings()
            
    def beginPrint(self, operation, context):
        if self.preview :
            self.preview = False
            return
        self.setCursor(Gdk.CursorType.WATCH)  # @UndefinedVariable
        settings = operation.get_print_settings()          
        printer = settings.get_printer()
        self.vue.document.updateData()
        fic = "/var/tmp/vista.{}.pdf".format(os.getpid())
        self.vue.gdocument.exportPdf(fic)
        cmd = os.popen("lp -d {} {}; rm -f {}".format(printer, fic, fic))
        cmd.read()
        self.setCursor(None)
        
    def printPreview(self, operation, context, window, arg):
        self.preview = True
        self.setCursor(Gdk.CursorType.WATCH)  # @UndefinedVariable
        self.vue.document.updateData()
        fic = "/var/tmp/vista.{}.pdf".format(os.getpid())
        self.vue.gdocument.exportPdf(fic)
        cmd = os.popen("evince {}; rm -f {}".format(fic, fic))
        cmd.read()
        self.setCursor(None)
        
    def getZoom(self) :
        """
            Calcule la fraction de zoom correspondant au choix de l'interface
        """
        w = self.wTree.get_object("comboboxZoom")
        my_iter = w.get_active_iter()
        zoom = int(w.get_model().get(my_iter,0)[0][0:-1])/100.
        return zoom
    
    def onZoomChanged(self, w):
        """
            Callback du combobox zoom zoom.
            On utilise GObject.iddle_add pour voir le curseur changer mais
            c'est pas toujours efficace.          
        """
        if self.noEvent == False :
            self.vue.document.updateData()
            GObject.idle_add(self.onZoomChanged2,w)
                    
    def onZoomChanged2(self, w):
        self.vue.gdocument.zoom = self.getZoom()
        self.updateNotebookVista(self.vue.gdocument.getNumPage(self.getCurrentId()))
        self.setCursor(None)
        
    def onZoomActivate(self, w, num_combo):
        """
            Callback des items du menu zoom.
            On utilise GObject.iddle_add pour voir le curseur changer mais
            c'est pas toujours efficace.
            num_combo est le numéro de l'item du combobox de zoom associé afin
            de pouvoir mettre ce dernier à jour.            
        """
        GObject.idle_add(self.onZoomActivate2,w, num_combo)
        
    def onZoomActivate2(self, w, num_combo):
        self.setCursor(Gdk.CursorType.WATCH)  # @UndefinedVariable
        w_combo = self.wTree.get_object("comboboxZoom")
        w_combo.set_active(num_combo)
        self.vue.gdocument.zoom = self.getZoom()
        if self.noEvent == False : # c'est le cas sur onOuvrir : on ne veut pas tracer
            self.updateNotebookVista(self.vue.gdocument.getNumPage(self.getCurrentId()))
        self.setCursor(None)
        
    def onAideAProposActivate(self, w):
        current_year = datetime.datetime.now().year
        vi.VistaDialog("<b>Vista</b>\nVersion : <b>{}</b>\n\nDESR/CNRM/GMEI/TRAMM 2014-{}".format(vi.version, current_year), self.window)
        
    def onAideManuelActivate(self, w):
        """
            Crée la fenêtre d'aide (contenu) qui affiche les pages html
        """         
        def destroyContenu(w):
            self.windowContenu = None
                
        if self.windowContenu is None :
            self.windowContenu = Gtk.Window()
            self.windowContenu.connect("destroy", destroyContenu)
            self.windowContenu.set_title("Aide - Vista")       
            web = webkit.WebView()
            web.set_size_request(903,607)
            web.load_uri("file://"+os.getenv('AIDA_HOME')+"/share/vista/doc/index.html")       
            self.windowContenu.add(web)
            self.windowContenu.show_all()
            self.windowContenu.set_resizable(False)
        else :
            self.windowContenu.present()
    
    def onUpdateListeVecteursActivate(self, w):
        
        def onComboPlateformeChanged(w, date_search):
            plateforme = w.get_child().get_text()
            fic_liste_vecteurs = "{}/share/vista/vecteurs/{}/{}.txt".format(os.getenv('AIDA_HOME'), os.getenv('AIDA_PROFIL'), plateforme)
            try :
                with open(fic_liste_vecteurs) as f :
                    date_search[0] = f.readline()
                    label_last_update.set_markup("Dernière mise à jour le {}/{}/{}".format(date_search[0][6:8],date_search[0][4:6],date_search[0][0:4] ))
                    label_last_update.set_visible(True)
                    label_search_date.set_markup("Début de recherche des vecteurs le {}/{}/{}".format(date_search[0][6:8],date_search[0][4:6],date_search[0][0:4] ))
                    label_search_date.set_visible(True)
                    button_modif_date.set_visible(True)
            except Exception :
                label_last_update.set_visible(False)
                label_search_date.set_visible(False)
                button_modif_date.set_visible(False)
                pass
            
        def onButtonModifSearchDatePressed(w, e, date_search):
            dialog = self.wTree.get_object("dialogPeriode")
            label = self.wTree.get_object("labelSaisiePeriode")
            label.set_text("Sélectionner une date")
            dialog.set_transient_for(self.window)
            calendar = self.wTree.get_object("calendar")
            calendar.select_month(int(vd.toString(self.vue.document.dateMois,"MM"))-1, int(vd.toString(self.vue.document.dateMois,"AAAA")))
            calendar.select_day(1)
            response = dialog.run()
            if response == 0: # valider    
                date_search[0] = vd.calendarToVistadate(self.wTree.get_object("calendar").get_date())[0:8]
                label_search_date.set_markup("Début de recherche des vecteurs le {}/{}/{}".format(date_search[0][6:8],date_search[0][4:6],date_search[0][0:4] ))
            else :
                pass
            dialog.hide()
                
        # on se positionne tout en haut du treeview (pour éviter une mise à jour compliquée
        # de(s) la plateforme(s) et du(es) paramètre(s) si un tracé est séléctionné)
        selection = self.vue.treeview.get_selection()
        treeModel, selectIter = selection.get_selected()
        first_iter = treeModel.get_iter_first()
        selection.select_iter(first_iter)
        self.updateTreeview()

        # création de la boite de dialogue
        self.setCursor(Gdk.CursorType.WATCH)  # @UndefinedVariable
        date_search = [""] # on a besoin d'une variable mutable
        dialog = Gtk.Dialog(title="- Mettre à jour la liste des vecteurs -", parent=self.window, modal=True,destroy_with_parent=True)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        vbox = Gtk.VBox()
        vbox.set_border_width(30)
        dialog.vbox.pack_start(vbox, False, False, 0)
        label = Gtk.Label()
        label.set_markup("Sélectionner la plateforme :")
        vbox.pack_start(label, True, True, 10)           
        dialog.vbox.set_border_width(30)
        completion = Gtk.EntryCompletion()
        completion.set_model(self.vue.liststore)
        completion.set_text_column(0)
        comboboxentryPlateforme = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme, "comboboxentryPlateforme")
        comboboxentryPlateforme.set_model(self.vue.liststore)
        comboboxentryPlateforme.set_entry_text_column(0)
        comboboxentryPlateforme.get_child().set_completion(completion)
        comboboxentryPlateforme.connect("changed",onComboPlateformeChanged, date_search)
    
        vbox.pack_start(comboboxentryPlateforme, True, True, 10)
        label_last_update = Gtk.Label()
        label_last_update.set_markup("Dernière mise à jour le {}".format("JJ/MM/AAAA"))
        vbox.pack_start(label_last_update, False, False, 0)
        hbox = Gtk.HBox()
        label_search_date = Gtk.Label()
        label_search_date.set_markup("Début de recherche des vecteurs le {}".format("JJ/MM/AAAA"))
        hbox.pack_start(label_search_date, False, False, 0)
        vbox.pack_start(hbox, False, False, 0)
        image = Gtk.Image()
        image.set_from_icon_name('accessories-text-editor', Gtk.IconSize.MENU)
        button_modif_date = Gtk.Button()
        button_modif_date.set_image(image)
        button_modif_date.set_can_focus(False)
        button_modif_date.set_relief(Gtk.ReliefStyle.NONE)
        button_modif_date.set_tooltip_text("modifier la date de dernière mise à jour")
        button_modif_date.connect("button-press-event",onButtonModifSearchDatePressed, date_search)
        hbox.pack_start(button_modif_date, False, False, 0)
        vbox.show_all()
        label_last_update.set_visible(False)
        label_search_date.set_visible(False)
        button_modif_date.set_visible(False)
        response = dialog.run()
        if response == Gtk.ResponseType.ACCEPT:
            label.set_text("Traitement en cours ...")
            plateforme = comboboxentryPlateforme.get_child().get_text()
            # on lance la mise à jour
            try :
                if date_search[0] == "" :
                    ret = sub.check_output(["{}/bin/update_liste_vecteurs_vista".format(os.getenv('AIDA_HOME')), "-p", plateforme]).decode('utf-8')
                else :
                    ret = sub.check_output(["{}/bin/update_liste_vecteurs_vista".format(os.getenv('AIDA_HOME')), "-p", plateforme, "-d", date_search[0]]).decode('utf-8')
                self.vue.readListeVecteurs()
            except Exception as e :
                print(e)
                ret = "Erreur : la mise à jour de la liste des vecteurs a échoué pour la plateforme {}.".format(plateforme)
            dialog.destroy()
            vi.VistaDialog(ret, self.window)
            # il faut mettre à jour tous les combobox
            try :
                del(self.parametreTreestore[plateforme])
            except :
                pass
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme"), "comboboxParametre", "plateforme", "parametre")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_x"), "comboboxParametre_x", "plateforme_x", "parametre_x")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_y"), "comboboxParametre_y", "plateforme", "parametre")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_h"), "comboboxParametre_h", "plateforme", "parametre")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_rdv"), "comboboxParametre_dd", "plateforme", "parametre_x")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_rdv"), "comboboxParametre_ff", "plateforme", "parametre")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov"), "comboboxParametre_hov", "plateforme", "parametre")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver"), "comboboxParametre_hov_quiver_dd", "plateformeQuiverHov", "parametre_dd_hov")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver"), "comboboxParametre_hov_quiver_ff", "plateformeQuiverHov", "parametre_ff_hov")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver"), "comboboxParametre_hov_quiver_u", "plateformeQuiverHov", "parametre_u_hov")
            self.onPlateformeChanged(self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver"), "comboboxParametre_hov_quiver_v", "plateformeQuiverHov", "parametre_v_hov")
            
            self.onPlateformeChanged(self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableCondition"), "comboboxentryPlateforme_cond"), "comboboxAffichageConditionnelParametre", None, None)
            self.onPlateformeChanged(self.vue.getChildByName(self.windowOperation, "comboboxentryPlateforme_operation"), "comboboxOperationParametre", None, None)
    
        else :
            dialog.destroy()
        self.setCursor(None)
        
    def onAcqidToDateActivate(self, w):
        dialog = self.wTree.get_object("dialogAcqidToDate")
        dialog.set_transient_for(self.window)
        self.wTree.get_object("entryAcqid").set_text("")
        self.wTree.get_object("entryAcqidDate").set_text("")
        _ = dialog.run()
        dialog.hide()
    
    
    
    #
    #boutons de gestion de la console
    #
    def onButtonOuvrirConsole(self, w) :
        self.wTree.get_object("itemConsole").set_active(True)
        
    def onButtonFermerConsole(self, w) :
        self.wTree.get_object("itemConsole").set_active(False)
    
    def onButtonViderConsole(self, w) :
        self.wTree.get_object("textviewOutput").get_buffer().set_text("")
    
    
    
    #
    # période
    #
    def onButtonPeriodeCLicked(self, w):
        if self.vue.document.typePeriode == 0 :
            # intervalle
            self.vue.document.typePeriode = 1
            self.typePeriodeSelecteur = 1
            self.vue.document.dateDebut = self.dateDebutSelecteur
            self.vue.document.dateFin = self.dateFinSelecteur
        else :
            # mois
            self.vue.document.typePeriode = 0
            self.typePeriodeSelecteur = 0
            self.vue.document.dateMois = self.dateMoisSelecteur
            self.vue.document.dateDebut, self.vue.document.dateFin = vd.debutFinMois(self.vue.document.dateMois)
    
        self.wTree.get_object("notebookPeriode").set_current_page(self.vue.document.typePeriode)
        
        self.checkModified()
            
    def onButtonDateCLicked(self, w, typeDate):
        dialog = self.wTree.get_object("dialogPeriode")
        dialog.set_transient_for(self.window)
        calendar = self.wTree.get_object("calendar")
        label = self.wTree.get_object("labelSaisiePeriode")
        hbox = self.wTree.get_object("hboxAcqidCalendar")
        self.wTree.get_object("entryAcqidCalendar").set_text("")
        if typeDate == 0 : #mois
            label.set_text("Sélectionner une date")
            hbox.set_visible(False)
            calendar.select_month(int(vd.toString(self.vue.document.dateMois,"MM"))-1, int(vd.toString(self.vue.document.dateMois,"AAAA")))
            calendar.select_day(1)
        elif typeDate == 1 : #debut
            label.set_text("Sélectionner une date ou un AcqId")
            hbox.set_visible(True)
            calendar.select_month(int(vd.toString(self.vue.document.dateDebut,"MM"))-1, int(vd.toString(self.vue.document.dateDebut,"AAAA")))
            calendar.select_day(int(vd.toString(self.vue.document.dateDebut,"JJ")))
        elif typeDate == 2 : #fin
            label.set_text("Sélectionner une date ou un AcqId")
            hbox.set_visible(True)
            calendar.select_month(int(vd.toString(self.vue.document.dateFin,"MM"))-1, int(vd.toString(self.vue.document.dateFin,"AAAA")))
            calendar.select_day(int(vd.toString(self.vue.document.dateFin,"JJ")))
    
        response = dialog.run()
        if response == 0: # valider
            if typeDate == 0 : #mois
                chnDate = vd.calendarToVistadate(self.wTree.get_object("calendar").get_date())
                self.vue.document.dateMois = chnDate
                self.vue.document.dateDebut, self.vue.document.dateFin = vd.debutFinMois(chnDate)
                self.dateMoisSelecteur = chnDate
                self.wTree.get_object("labelMois").set_label(vd.toString(chnDate, 'mm AAAA'))
            elif typeDate == 1 : #debut
                chnDate = vd.calendarToVistadate(self.wTree.get_object("calendar").get_date())
                self.vue.document.dateDebut = chnDate
                self.dateDebutSelecteur = chnDate
                self.wTree.get_object("labelDebut").set_label("du {}".format(vd.toString(chnDate, 'JJ/MM/AAAA')))
            elif typeDate == 2 : #fin
                chnDate = vd.calendarToVistadate(self.wTree.get_object("calendar").get_date())
                self.vue.document.dateFin = chnDate
                self.dateFinSelecteur = chnDate
                self.wTree.get_object("labelFin").set_label("au {}".format(vd.toString(chnDate, 'JJ/MM/AAAA')))
            self.checkModified()
        elif response == 1: # annuler
            pass
        dialog.hide()
    
    def onButtonCopierDateDebut(self, w):
        chnDateDebut = self.wTree.get_object("labelDebut").get_label().strip()[3:]
        self.vue.document.dateFin = self.vue.document.dateDebut
        self.dateFinSelecteur = self.dateDebutSelecteur
        self.wTree.get_object("labelFin").set_label("au {}".format(chnDateDebut))
        self.checkModified()
        
    def onButtonCopierDateFin(self, w):
        chnDateFin = self.wTree.get_object("labelFin").get_label().strip()[3:]
        self.vue.document.dateDebut = self.vue.document.dateFin
        self.dateDebutSelecteur = self.dateFinSelecteur
        self.wTree.get_object("labelDebut").set_label("du {}".format(chnDateFin))
        self.checkModified()
        
    def onEntryAcqidCalendarChanged(self, w) :
        calendar = self.wTree.get_object("calendar")
        acqid = self.wTree.get_object("entryAcqidCalendar").get_text()
        try :
            date_acqid = AcqId.AcqId(acqid).acqid_to_date()
            if date_acqid is not None :
                calendar.select_month(int(vd.toString(vd.toVistaDate(date_acqid), "MM"))-1, int(vd.toString(vd.toVistaDate(date_acqid), "AAAA")))
                calendar.select_day(int(vd.toString(vd.toVistaDate(date_acqid), "JJ")))            
        except :
            pass 
    
    
    
    #
    # menu contextuel du treeview
    #
    def onInserer(self, w, before, typ):
        selection = self.vue.treeview.get_selection()
        treeModel, selectIter = selection.get_selected()
        idElmt = treeModel.get_value(selectIter, 1)
        #model
        newElmt = self.vue.document.insertElement(idElmt, before, typ)
        if not newElmt :
            return
        #mise à jour de la vue
        _ = self.vue.gdocument.insertElement(idElmt, newElmt, before)            
        iter_parent = treeModel.iter_parent(selectIter)
        if before :
            newIter = self.vue.treestore.insert_before(iter_parent, selectIter, ["",newElmt.id])
        else :
            newIter = self.vue.treestore.insert_after(iter_parent, selectIter, ["",newElmt.id])            
        try :
            self.vue.treeview.get_selection().select_iter(newIter)
        except Exception as e :
            vi.VistaDialog(str(e), self.window)
            return
        path = self.vue.treestore.get_path(newIter)
        self.vue.treeview.set_cursor( path, None, 0)
        self.updateTreeview()
        self.checkModified()
    
                                  
    def onMenuTreeview(self, w, color):
        #self.vue.treeview.modify_base(Gtk.StateFlags.ACTIVE, color)
        pass
    
    
    
    #
    # treeview
    #
    def treeviewCopier(self) :
        selection = self.vue.treeview.get_selection()
        treeModel, selectIter = selection.get_selected()
        idElmt = treeModel.get_value(selectIter, 1)
        self.vue.document.pressePapier = copy.copy(self.vue.document.getElementById(idElmt))
        self.vue.document.pressePapier.parametres = copy.deepcopy(self.vue.document.pressePapier.parametres)
        
    def treeviewColler(self) :
        selection = self.vue.treeview.get_selection()
        treeModel, selectIter = selection.get_selected()
        idElmt = treeModel.get_value(selectIter, 1)
        # On colle dans le modèle le presse-papier : si le presse-papier
        # est de même type que la sélection, on colle dans le parent de la sélection
        parent = self.vue.document.getElementById(idElmt)
        if isinstance(parent, type(self.vue.document.pressePapier)) :
            parent = parent.parent
        obj_list = parent.paste(self.vue.document.pressePapier)
        if len(obj_list) == 0 :
            return
        # mise à jour de la vue : d'abord les objets graphiques puis le treeview
        elmt = self.vue.gdocument.getElementById(parent.id)
        elmt.paste(obj_list[0])
        parentsIter = {}
        parentsIter[parent.id] = self.getIterById(parent.id)
        for obj in obj_list :
            id_parent = obj.parent.id
            newIter = self.vue.treestore.append(parentsIter[id_parent], ["",obj.id])
            parentsIter[obj.id] = newIter
        path = self.vue.treestore.get_path(parentsIter[parent.id])
        self.vue.treeview.expand_row(path, False)
        self.vue.treeview.get_selection().select_iter(newIter)
        path = self.vue.treestore.get_path(newIter)
        self.vue.treeview.set_cursor( path, None, 0)
        
        self.updateTreeview()
        self.checkModified()
        
    def onTreeviewCopier(self, w):
        self.treeviewCopier()
        
    def onTreeviewColler(self, w):
        self.treeviewColler()
        
    def onTreeviewKeyPress(self, w, event):
        selection = self.vue.treeview.get_selection()
        treeModel, selectIter = selection.get_selected()
        idElmt = treeModel.get_value(selectIter, 1)
        
        if idElmt is not None :
            if event.state & Gdk.ModifierType.CONTROL_MASK :
                if Gdk.keyval_name(event.keyval) == "c" and idElmt != -1:
                    self.treeviewCopier()
                if Gdk.keyval_name(event.keyval) == "v":
                    self.treeviewColler()
                if Gdk.keyval_name(event.keyval) == "Up":
                    print("monter")
                if Gdk.keyval_name(event.keyval) == "Down":
                    print("descendre")
                return True            
        return True
    
    def onTreeviewButtonPress(self, w, event):
        if event.button == 3 :
            x = int(event.x)
            y = int(event.y)
            # on detache les sous-menu graphiques
            self.removeSubmenusGraphiques()
            # on debloque les handlers d'ajout s'ils sont bloqués
            if self.vue.treeMenuContextHandlers[self.handlerAjouter] :
                self.wTree.get_object("menuitemTreeAjouter").handler_unblock(self.handlerAjouter)
                self.vue.treeMenuContextHandlers[self.handlerAjouter] = False
            if self.vue.treeMenuContextHandlers[self.handlerAjouterAvant] :
                self.wTree.get_object("menuitemTreeAjouterAvant").handler_unblock(self.handlerAjouterAvant)
                self.vue.treeMenuContextHandlers[self.handlerAjouterAvant] = False
            if self.vue.treeMenuContextHandlers[self.handlerAjouterApres] :
                self.wTree.get_object("menuitemTreeAjouterApres").handler_unblock(self.handlerAjouterApres)
                self.vue.treeMenuContextHandlers[self.handlerAjouterApres] = False
            
            
            pthinfo = self.vue.treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, _cellx, _celly = pthinfo
                self.vue.treeview.grab_focus()
                self.vue.treeview.set_cursor( path, col, 0)
                elmt = self.getCurrentElement()
                self.wTree.get_object("menuitemTreeCopier").set_sensitive(True)
                self.wTree.get_object("menuitemTreeColler").set_sensitive(False)
                if isinstance(elmt, vc.Document) :
                    self.wTree.get_object("menuitemTreeAjouter").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouter").set_label("Ajouter une page")
                    self.wTree.get_object("menuitemTreeSupprimer").set_sensitive(False)
                    self.wTree.get_object("menuitemTreeAjouterAvant").set_sensitive(False)
                    self.wTree.get_object("menuitemTreeAjouterApres").set_sensitive(False)
                    self.wTree.get_object("menuitemTreeCopier").set_sensitive(False)
                    if isinstance(self.vue.document.pressePapier, vc.Page) :
                        self.wTree.get_object("menuitemTreeColler").set_sensitive(True)
                    
                if isinstance(elmt, vc.Page) :
                    self.wTree.get_object("menuitemTreeAjouter").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouter").set_label("Ajouter un graphique")
                    self.wTree.get_object("menuitemTreeSupprimer").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeSupprimer").set_label("Supprimer la page")                        
                    self.wTree.get_object("menuitemTreeAjouterAvant").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouterAvant").set_label("Ajouter une page avant")
                    self.wTree.get_object("menuitemTreeAjouterApres").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouterApres").set_label("Ajouter une page après")                        
                    # on attache un sous-menu graphiques
                    self.wTree.get_object("menuitemTreeAjouter").set_submenu(self.wTree.get_object("menuAjouterGraphiques"))
                    self.wTree.get_object("menuitemTreeAjouter").handler_block(self.handlerAjouter)
                    self.vue.treeMenuContextHandlers[self.handlerAjouter] = True
                    if isinstance(self.vue.document.pressePapier, vc.Page) or isinstance(self.vue.document.pressePapier, vc.Graphique) :
                        self.wTree.get_object("menuitemTreeColler").set_sensitive(True)
                    
                if isinstance(elmt, vc.Graphique) :
                    if elmt.type == "RDV" and len(elmt.traces) > 0 :
                        self.wTree.get_object("menuitemTreeAjouter").set_sensitive(False)
                    else :
                        self.wTree.get_object("menuitemTreeAjouter").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouter").set_label("Ajouter un tracé")
                    self.wTree.get_object("menuitemTreeSupprimer").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeSupprimer").set_label("Supprimer le graphique")                        
                    self.wTree.get_object("menuitemTreeAjouterAvant").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouterAvant").set_label("Ajouter un graphique avant")
                    self.wTree.get_object("menuitemTreeAjouterApres").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouterApres").set_label("Ajouter un graphique après")
                    # on attache le sous-menu traces pour Hov
                    if elmt.type == "Hov" :
                       self.wTree.get_object("menuitemTreeAjouter").set_submenu(self.wTree.get_object("menuAjouterTracesHov"))
                       self.wTree.get_object("menuitemTreeAjouter").handler_block(self.handlerAjouter)  
                    # on attache les sous-menu graphiques   
                    self.wTree.get_object("menuitemTreeAjouterAvant").set_submenu(self.wTree.get_object("menuAjouterAvantGraphiques"))
                    self.wTree.get_object("menuitemTreeAjouterApres").set_submenu(self.wTree.get_object("menuAjouterApresGraphiques"))
                    self.wTree.get_object("menuitemTreeAjouterAvant").handler_block(self.handlerAjouterAvant)
                    self.vue.treeMenuContextHandlers[self.handlerAjouterAvant] = True
                    self.wTree.get_object("menuitemTreeAjouterApres").handler_block(self.handlerAjouterApres)
                    self.vue.treeMenuContextHandlers[self.handlerAjouterApres] = True
                    if isinstance(self.vue.document.pressePapier, vc.Graphique) or isinstance(self.vue.document.pressePapier, vc.Trace) :
                        self.wTree.get_object("menuitemTreeColler").set_sensitive(True)
    
                if isinstance(elmt, vc.Trace) :
                    self.wTree.get_object("menuitemTreeAjouter").set_sensitive(False)
                    self.wTree.get_object("menuitemTreeSupprimer").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeSupprimer").set_label("Supprimer le tracé")
                    if elmt.type == "RDV" :
                        self.wTree.get_object("menuitemTreeAjouterAvant").set_sensitive(False)
                    else :
                        self.wTree.get_object("menuitemTreeAjouterAvant").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouterAvant").set_label("Ajouter un tracé avant")
                    if elmt.type == "RDV" :
                        self.wTree.get_object("menuitemTreeAjouterApres").set_sensitive(False)
                    else :
                        self.wTree.get_object("menuitemTreeAjouterApres").set_sensitive(True)
                    self.wTree.get_object("menuitemTreeAjouterApres").set_label("Ajouter un tracé après")
                    if isinstance(self.vue.document.pressePapier, vc.Trace) :
                        self.wTree.get_object("menuitemTreeColler").set_sensitive(True)
                    
                menu = self.wTree.get_object("menuTreeview")
                
                #menu.popup(None, None, None, None, event.button, time)
                menu.popup_at_pointer(event)
                
                return True
            
        elif event.button == 1 and event.type == Gdk.EventType.DOUBLE_BUTTON_PRESS :  # @UndefinedVariable
            x = int(event.x)
            y = int(event.y)
            pthinfo = self.vue.treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, _cellx, _celly = pthinfo
                if self.vue.treeview.row_expanded(path) :
                    self.vue.treeview.collapse_row(path)
                else :
                    self.vue.treeview.expand_row(path, False)
            return True
        
    def removeSubmenusGraphiques(self, ):
        # on detache les sous-menu graphiques
        self.wTree.get_object("menuitemTreeAjouter").set_submenu(None)
        self.wTree.get_object("menuitemTreeSupprimer").set_submenu(None)
        self.wTree.get_object("menuitemTreeAjouterAvant").set_submenu(None)
        self.wTree.get_object("menuitemTreeAjouterApres").set_submenu(None)
    
    def onTreeviewChanged(self, selection):
        self.noEvent = True
        model, treeiter = selection.get_selected()
        if treeiter != None :
            # affichage de la bonne page du notebook
            idElmt = model.get_value(treeiter, 1)
            numPage = self.vue.gdocument.getNumPage(idElmt)
            if self.vue.getChildByName(self.window, "notebookVista") != None :
                self.vue.getChildByName(self.window, "notebookVista").set_current_page(numPage)
                #
                # Les lignes qui suivent sont à activer pour rafraichir le tracé dans la page si besoin
                #
                try :
                    canvas = self.vue.gdocument.gpages[numPage].canvas
                    width, height = canvas.get_size_request()
                    canvas.set_size_request(1,1)
                    canvas.set_size_request(width, height)
                except : # le canvas n'est pas encore construit si la page n'a jamais été visualisée
                    pass
            # affichage des propriétés de l'élément
            w = self.vue.getChildByName(self.window, "notebookProprietes")
            wt = self.vue.getChildByName(self.window, "labelProprietes")
            numid = model[treeiter][1]
            vc.Document.currentId = numid
            elmt = self.vue.document.getElementById(numid)
            if isinstance(elmt, vc.Document) :
                wt.set_label("<b>Propriétés du document</b>")                
                self.updateUiDocument()
                w.set_current_page(0) # !!! faire les set_current_page après les update car ca peut appeler des callbacks
            elif isinstance(elmt, vc.Page) :
                self.updateUiPage(elmt)
                w.set_current_page(1)
                wt.set_label("<b>Propriétés de la page</b>")
            elif isinstance(elmt, vc.Graphique) :
                self.updateUiGraphique(elmt)
                if elmt.type == "Histo3D" :
                    w.set_current_page(6)
                    wt.set_label("<b>Propriétés du graphique Histo 3D</b>")
                elif elmt.type == "RDV" :
                    w.set_current_page(8)
                    wt.set_label("<b>Propriétés du graphique rose des vents</b>")
                elif elmt.type == "Hov" :
                    w.set_current_page(9)
                    wt.set_label("<b>Propriétés du graphique Hovmöller</b>")
                elif elmt.type == "PlotXY" :
                    w.set_current_page(2)
                    wt.set_label("<b>Propriétés du graphique PlotXY</b>")
                elif elmt.type == "Histo" :
                    w.set_current_page(2)
                    wt.set_label("<b>Propriétés du graphique Histo</b>")  
                else : # ST
                    w.set_current_page(2)
                    wt.set_label("<b>Propriétés du graphique ST</b>")
            elif isinstance(elmt, vc.Trace) :
                self.updateUiTrace(elmt)
                if elmt.type == "ST" :
                    w.set_current_page(3)
                    wt.set_label("<b>Propriétés du tracé ST</b>")
                elif elmt.type == "Histo3D" :
                    w.set_current_page(3)
                    wt.set_label("<b>Propriétés du tracé Histo3D</b>")
                elif elmt.type == "PlotXY" :
                    w.set_current_page(4)
                    wt.set_label("<b>Propriétés du tracé PlotXY</b>")
                elif elmt.type == "Histo" :
                    w.set_current_page(5)
                    wt.set_label("<b>Propriétés du tracé Histo</b>")
                elif elmt.type == "RDV" :
                    w.set_current_page(7)
                    wt.set_label("<b>Propriétés du tracé Rose des vents</b>")
                elif elmt.type == "Hov" :
                    w.set_current_page(10)
                    wt.set_label("<b>Propriétés du tracé Hovmöller</b>")
        self.noEvent = False
                
    def onTreeviewExpandCollapse(self, treeview, _iter, path):
        #on sélectionne la ligne que l'on expand/collapse sinon on est sans sélection
        self.vue.treeview.get_selection().select_iter(_iter)
     
    
                                
    #
    # vpanedVista : quand la console est masquée, on interdit le resize du vpanel. C'est géré par self.consoleLock
    #
    def onVpanedVistaButtonPress(self, w, event):
        return self.consoleLock
    
    
    
    #
    # boutons d'appel de la calculette
    #
    
    def onButtonCalculettePressed(self, w, e, axe, nomImageWarning) :
        
        if self.noEvent :
            return
        elmt = self.getCurrentElement()
        self.wTree.get_object("labelOperationImageWarning").set_text(nomImageWarning)
        self.wTree.get_object("labelOperationAxe").set_text(axe)
        # Operation
        if axe == "x" :
            operation = elmt.getValue("operation_x")
        else :
            operation = elmt.getValue("operation_y")
        self.noEvent = True
        try :
            self.wTree.get_object("entryExpressionOperation").set_text(operation.split("##")[1])
        except :
           self.wTree.get_object("entryExpressionOperation").set_text("")
        self.noEvent = False
        # Variables
        elmt
        # on backup les opérations
        elmt.setBackupOperation(axe)
        # on efface toutes les vues de variables
        box_datas = self.wTree.get_object("vboxVariablesOperation")
        for c in box_datas.get_children() :
            if c.get_name() != "hboxBandeauVariablesOperation" :
                c.destroy()
        # et on recrée les nouvelles :  on crée systématiquement une variable y en mode non-editable et non-deletable
        if axe == 'x' :
            self.addVariableOperation(elmt.getValue('plateforme_x'), elmt.getValue('parametre_x'), elmt, nom_variable = 'y', editable=False, deletable=False, update_model = False)
            for d in elmt.datas_operation_definition_x :
                self.addVariableOperation(d["plateforme"], d["parametre"], elmt, nom_variable = d["nom"], update_model = False)
        else :
            self.addVariableOperation(elmt.getValue('plateforme'), elmt.getValue('parametre'), elmt, nom_variable = 'y', editable=False, deletable=False, update_model = False)
            for d in elmt.datas_operation_definition_y :
                self.addVariableOperation(d["plateforme"], d["parametre"], elmt, nom_variable = d["nom"], update_model = False)
        
        self.wTree.get_object("labelOperationImageWarning").set_visible(False)
        self.wTree.get_object("labelOperationAxe").set_visible(False)
        self.wTree.get_object("windowOperation").show()

    #
    # boutons de la boîte d'opération
    #
    def checkOperation(self):
        """
            Vérifie les variables et la syntaxe de l'opératiion.
        """
        def hacked(expression):
            """
                Vérifie la présence de mots clés susceptibles d'être dangereux lors d'un exec ou d'un eval
            """
            bad = ["call", "system", "open", "read", "run", "os.", "sys.","process", "command", "import", "def", "print", "map", "input"]
            for b in bad :
                if b in expression.lower() :
                    return True
            return False
        axe = self.wTree.get_object("labelOperationAxe").get_text()
        trace = self.vue.document.getElementById(vc.Document.currentId)
        if axe == 'x' :
            variables = trace.datas_operation_definition_x
            expression_operation = trace.expression_operation_x
        else :
            variables = trace.datas_operation_definition_y
            expression_operation = trace.expression_operation_y
        if len(variables)>0 and len(expression_operation.strip())==0 :
            vi.VistaDialog("Erreur : aucune opération alors que des variables sont définies.", self.window, markup=False)
            return False
        if hacked(expression_operation) :
            message = "Erreur sur l'opération : {}\nSuspicion de malveillance...".format(expression_operation)
            vi.VistaDialog(message, self.window, markup=False)
            return False
        if expression_operation.count('(') != expression_operation.count(')') :
            message = "Erreur sur l'opération : {}\nNombre de parenthèses incorrect.".format(expression_operation)
            vi.VistaDialog(message, self.window, markup=False)
            return False
        # on teste l'opération
        expression_ok = False
        for v in variables :
            exec(("{}={}".format(v["nom"], random.randrange(-10,10))), globals(),locals())
        for i in range(100) : 
            #on prend un domaine de définition empirique mais large (<0, =0, >0)
            # y est toujours défini (c'est la donnée du tracé) et x l'est parfois (PlotXY)
            random.seed()
            y = random.randrange(-10,10)
            x = random.randrange(-10,10)            
            try :
                expression = "from numpy import *\n"+expression_operation
                exec(expression)
                expression_ok = True
            except Exception :
                pass
        if not expression_ok :
                message = "Erreur sur l'opération : {}\nVéfifier que les variables utilisées dans l'expression sont bien définies\net que la syntaxe est correcte.".format(expression_operation)
                vi.VistaDialog(message, self.window, markup=False)
                return False
        return True
        
    def onEntryExpressionOperationChanged(self, w) :
        if self.noEvent :
            return
        trace = self.vue.document.getElementById(vc.Document.currentId)
        str_operation = w.get_text()
        axe = self.wTree.get_object("labelOperationAxe").get_text()
        trace.updateExpressionOperation(str_operation, axe)
    
    def onButtonAnnulerOperationPressed(self, w, e) :
        axe = self.wTree.get_object("labelOperationAxe").get_text()
        trace = self.vue.document.getElementById(vc.Document.currentId)
        # on restaure le backup de l'opération
        trace.restaureBackupOperation(axe)
        self.wTree.get_object("windowOperation").hide()
        
    def onButtonValiderOperationPressed(self, w, e) :
        oper_ok = self.checkOperation()
        if oper_ok :
            trace = self.vue.document.getElementById(vc.Document.currentId)
            axe = self.wTree.get_object("labelOperationAxe").get_text()
            imageWarning = self.wTree.get_object("labelOperationImageWarning").get_text()
            if axe == 'x' :
                expression_operation = trace.expression_operation_x
            else:
                expression_operation = trace.expression_operation_y
            if expression_operation == "" :
                self.wTree.get_object(imageWarning).set_visible(False)
            else:
                self.wTree.get_object(imageWarning).set_visible(True)
                self.wTree.get_object(imageWarning).set_tooltip_text(trace.operationToString(axe))
            self.wTree.get_object("windowOperation").hide()       
            self.checkModified()
        
    def onAddVariableOperationClicked(self, w):
        if self.noEvent :
            return
        dialog_editer = self.wTree.get_object("dialogEditerVariableOperation")
        dialog_editer.show_all()
        combo_plateforme = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableOperation"), "comboboxentryPlateforme_operation")
        combo_plateforme.grab_focus()
        combo_parametre = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableOperation"), "comboboxOperationParametre")
        combo_parametre.set_active(-1)
        combo_parametre.get_child().set_text("")
        if combo_plateforme.get_child().get_text() == "" :
           combo_parametre.get_child().set_sensitive(False) 
        
        reponse = dialog_editer.run()
        if reponse == 1 :
            plateforme = combo_plateforme.get_child().get_text()
            if plateforme in list(self.vue.plateformes.keys()) and plateforme != "" :                    
                model = combo_parametre.get_model ()
                iter1 = combo_parametre.get_active_iter ()
                if iter1 != None :
                    parametre = model.get_value(iter1, 0)                        
                    self.addVariableOperation(self.vue.plateformes[plateforme]["abrev"], parametre, self.vue.document.getElementById(vc.Document.currentId))
                    
        dialog_editer.hide()
    
    def addVariableOperation(self, plateforme, parametre, trace, editable = True, deletable = True, nom_variable = None, update_model = True):
        """
            Met à jour le modèle (par defaut) et crée une vue
        """
        vbox_datas = self.wTree.get_object("vboxVariablesOperation")
        hbox_data = Gtk.HBox(homogeneous=False, spacing=0)
        vbox_datas.pack_start(hbox_data, False, False, 0)
        offset = 65
        axe = self.wTree.get_object("labelOperationAxe").get_text()
        if nom_variable is None :
            nom_variable = trace.getNomVariableOperation()       
        if nom_variable != None :
            if update_model : 
                trace.addVariableOperation(nom_variable, plateforme, parametre, axe)                           
            label = Gtk.Label(label="{} = {}:{}".format(nom_variable, plateforme, parametre))                     
            if editable :
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                button.set_can_focus(False)
                button.connect('clicked', self.onEditerVariableOperationClicked, hbox_data, label, trace)
                button.set_tooltip_text("Editer la variable")
                hbox = Gtk.HBox()
                button.add(hbox)
                image = Gtk.Image()
                image.set_from_icon_name('accessories-text-editor', Gtk.IconSize.BUTTON)
                hbox.pack_start(image, False, False, 0)
                hbox_data.pack_start(button, False, False, 0)
                offset = 10            
            if deletable :
                button = Gtk.Button()
                button.set_relief(Gtk.ReliefStyle.NONE)
                button.set_can_focus(False)
                button.connect('clicked', self.onDeleteVariableOperationClicked, hbox_data, nom_variable, trace)
                button.set_tooltip_text("Supprimer la variable")
                hbox = Gtk.HBox()
                button.add(hbox)
                image = Gtk.Image()
                image.set_from_icon_name('edit-delete', Gtk.IconSize.BUTTON)
                hbox.pack_start(image, False, False, 0)
                hbox_data.pack_start(button, False, False, 2)
                offset = 10                
            hbox_data.pack_start(label, False, False, offset)            
            hbox_data.show_all()
            vbox_datas.show()
    
    def onDeleteVariableOperationClicked(self, w, hbox, nom_variable, trace):
        axe = self.wTree.get_object("labelOperationAxe").get_text()
        trace.delVariableOperation(nom_variable, axe)
        hbox.destroy()
                   
    def onEditerVariableOperationClicked(self, w, hbox, label, trace):
        axe = self.wTree.get_object("labelOperationAxe").get_text()
        dialog_editer = self.wTree.get_object("dialogEditerVariableOperation")
        tab_label = label.get_text().split("=")
        nom_variable = tab_label[0].strip()
        plateforme = tab_label[1].split(":")[0].strip()
        parametre = tab_label[1].split(":")[1].strip()
        combo_plateforme = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableOperation"), "comboboxentryPlateforme_operation")
        combo_plateforme.grab_focus()
        combo_plateforme.show_all()
        combo_parametre = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableOperation"), "comboboxOperationParametre")
        self.updateUiPlateformeAndParametre(self.wTree.get_object("dialogEditerVariableOperation"), "comboboxentryPlateforme_operation", "operation:"+plateforme,"comboboxOperationParametre" , "operation:"+axe+":"+parametre, None, trace)    
    
        reponse = dialog_editer.run()
        if reponse == 1 :
            plateforme = combo_plateforme.get_child().get_text()
            if plateforme in list(self.vue.plateformes.keys()) and plateforme != "" :                    
                model = combo_parametre.get_model ()
                iter1 = combo_parametre.get_active_iter ()
                if iter1 != None :
                    parametre = model.get_value(iter1, 0)
                    trace.updateVariableOperation(nom_variable, self.vue.plateformes[plateforme]["abrev"], parametre, axe)      
                    label.set_text("{} = {}:{}".format(nom_variable, self.vue.plateformes[plateforme]["abrev"], parametre))
        dialog_editer.hide()
    
    #
    # Outil Acqid -> date
    #
    def onButtonAcqidToDatePressed(self, w, e) :    
        acqid = self.wTree.get_object("entryAcqid").get_text()
        try :
            date_acqid = AcqId.AcqId(acqid).acqid_to_date()
            if date_acqid is None :
                texte = "AcqId inexistant"
            else :
                texte = vd.toString(vd.toVistaDate(date_acqid), "JJ/MM/AAAA")            
        except :
            texte = "AcqId incorrect"
        self.wTree.get_object("entryAcqidDate").set_text(texte)
        
    def onEntryAcqidChanged(self, w) :
        self.wTree.get_object("entryAcqidDate").set_text("") 
    
    def onEntryAcqidActivate(self, w) :
        self.onButtonAcqidToDatePressed(None, None)
        
    def onDialogAgencementMap(self, w) :
        """
            Cleare la fenêtre d'agencement et trace les rectangles
            qui matérialisent les graphiques.
            On fait cela sur l'événement map sinon on a un soucis de rafraîchissement.
        """
        plt.figure(-1)
        plt.cla()
        for tl in self.vue.axAgencement.get_xticklabels() + self.vue.axAgencement.get_yticklabels():
            tl.set_visible(False)
        self.vue.axAgencement.xaxis.grid(True, zorder=100)
        self.vue.axAgencement.yaxis.grid(True, zorder=100)
        self.vue.axAgencement.set_xlim(0,100)
        self.vue.axAgencement.set_ylim(0,100)
        self.vue.axAgencement.set_xticks(list(range(0,100,5)))
        self.vue.axAgencement.set_yticks(list(range(0,100,5)))           
        gpage = self.vue.gdocument.getElementById(vc.Document.currentId)
        
        va.ControlRectangles.clear()
        va.ControlRectangles.orientation = gpage.page.getValue("orientation")
        pos=1
        for g in gpage.ggraphiques :
            x,y,width,height = gpage.getPosition(g.id)
            dr = va.DraggableRectangle(self.vue.axAgencement, self.vue.figAgencement, x, 100-y-height, width, height, pos, g.graphique.getValue("titre"), g.graphique.id, g.graphique.type)
            va.ControlRectangles.rectangles.append(dr)
            pos += 1
        self.vue.figAgencement.canvas.draw()
        va.ControlRectangles.ctrlValidite()






    #
    # Méthodes de vérification de la modification du document
    #
    def checkModified(self):
        """
            Vérifie si le document a été modifié par comparaison de la chaine json
        """
        self.checkModifiedSinceLastSave()
            
        # on vérifie si le document visualisé correspond au document
        json1 = {}
        self.vue.document.toJson(json1)
        w = self.vue.getChildByName(self.window, "notebookVista")
        if w is None : 
            return
        modified = False
        json3 = {}
        self.documentVisualized.toJson(json3)
        if json1 != json3 :           
            modified = True
            
        if self.typePeriodeVisualized != self.typePeriodeSelecteur :
            modified = True
        elif  self.typePeriodeVisualized == 0 : # mois
            if self.dateMoisVisualized != None :              
                if vd.toString(self.dateMoisVisualized, "mm AAAA") != vd.toString(self.dateMoisSelecteur, "mm AAAA") :
                    modified = True
        else : # intervalle
            if self.dateDebutVisualized != self.dateDebutSelecteur or self.dateFinVisualized != self.dateFinSelecteur :
                modified = True
            
        if modified :
            self.wTree.get_object("imageModified").set_visible(True)
        else :
            self.wTree.get_object("imageModified").set_visible(False)
        
        self.modified = modified
        
    def checkModifiedSinceLastSave(self):
        """
            Vérifie si le document a été modifié depuis la dernière sauvegarde
        """     
        json1 = {}
        self.vue.document.toJson(json1)
        json2 = {}
        self.documentSaved.toJson(json2)
        if json1 == json2 :
            self.window.set_title("Vista - {}".format(self.vue.document.fichier))
            self.wTree.get_object("itemEnregistrer").set_sensitive(False)
            self.wTree.get_object("toolbuttonEnregistrer").set_sensitive(False)
            return(False)
        else :
            self.window.set_title("Vista - {} (modifié)".format(self.vue.document.fichier))
            self.wTree.get_object("itemEnregistrer").set_sensitive(True)
            self.wTree.get_object("toolbuttonEnregistrer").set_sensitive(True)
            return(True)
            
            
    #
    # Méthodes de mise à jour de la vue
    #            
            
    def updateTreeview(self):
        """
            Met à jour le treeview quand nécessaire.
        """
        
        store = self.vue.treeview.get_model()
        store.foreach(self.updateTreeview2)
        
    def updateTreeview2(self, modele, chemin, _iter):
        """
            Met à jour le numéro des pages du treeview après une insertion ou une suppression de page.
            Met à jour le titre des graphiques.
            Met à jour le titre des tracés.
        """
        idElmt = self.vue.treestore.get(_iter,1)
        elmt = self.vue.document.getElementById(idElmt[0])
        if isinstance(elmt, vc.Page) :
            numPage = self.vue.document.getNumPage(idElmt[0])
            self.vue.treestore.set_value(_iter,0,'Page {}'.format(numPage+1))
        elif isinstance(elmt, vc.Graphique) :
            titre = self.vue.document.toTitle(elmt.getValue("titre"))
            chn = "Graphique {}       {}...".format(elmt.type, titre[0:20])
            self.vue.treestore.set_value(_iter,0,chn)
        elif isinstance(elmt, vc.Trace) :
            chn = "Tracé          {} {}...".format(elmt.getValue("plateforme"),elmt.getValue("parametre")[0:20] )
            self.vue.treestore.set_value(_iter,0,chn)
                           
    def updateUiDocument(self) :
        #format
        fmt = self.vue.document.getValue("format")
        w = self.vue.getChildByName(self.window, "checkbuttonPdf")
        w.unset_state_flags(Gtk.StateFlags.CHECKED)
        if ( fmt.find("pdf") != -1 ) :
            w.set_state_flags(Gtk.StateFlags.CHECKED, False)
        w = self.vue.getChildByName(self.window, "checkbuttonPs")
        w.unset_state_flags(Gtk.StateFlags.CHECKED)
        if ( fmt.find("ps") != -1 ) :
            w.set_state_flags(Gtk.StateFlags.CHECKED, False)
        w = self.vue.getChildByName(self.window, "checkbuttonPng")
        w.unset_state_flags(Gtk.StateFlags.CHECKED)
        if ( fmt.find("png") != -1 ) :
            w.set_state_flags(Gtk.StateFlags.CHECKED, False)
        #fichier
        fic = self.vue.document.getValue("dest_fic")
        w = self.vue.getChildByName(self.window, "entryNomFichier")
        w.set_text(fic)
        # répertoire
        rep = self.vue.document.getValue("dest_dir")
        w = self.vue.getChildByName(self.window, "filechooserbuttonRepertoire")
        w.set_current_folder_uri(rep) 
 
        
    def updateUiPage(self, page) :
        #titre
        w = self.vue.getChildByName(self.window, "entryTitrePage")
        w.set_text(page.getValue("titre"))
        #police du titre
        w = self.vue.getChildByName(self.window, "fontbuttonTitrePage")
        w.set_font(page.getValue("policeTitre"))
        #orientation        
        ori = page.getValue("orientation")
        if ori == "portrait" or ori == "vertical" :
            w = self.vue.getChildByName(self.window,"radiobuttonPortrait")
            w.set_active(True)
        else :
            w = self.vue.getChildByName(self.window, "radiobuttonLandscape")
            w.set_active(True)
        
        #logo
        w = self.vue.getChildByName(self.window, "comboboxLogo")
        logo = page.getValue("logo")
        index = self.getComboIndex(w, logo, 0)
        w.set_active(index)

        #position du logo
        w = self.vue.getChildByName(self.window, "comboboxPositionLogo")
        position = page.getValue("positionLogo")
        index = self.getComboIndex(w, position, 1)
        w.set_active(index)
 
        
    def updateUiGraphique(self, graphique) :
        if graphique.type == "Histo3D" :
            titre = "entryTitreGraphHisto3D"
            fontTitre = "fontbuttonTitreGraphHisto3D"
            self.noEvent = True
            if graphique.getValue("amplitudeClassesHisto") == graphique.getDefault("amplitudeClassesHisto") : #on utilise le nombre de classes
                self.wTree.get_object("radiobuttonNombreClassesHisto3D").set_active(True)
                self.wTree.get_object("spinbuttonNombreClassesHisto3D").set_sensitive(True)
                self.wTree.get_object("entryAmplitudeClassesHisto3D").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesHisto3D").set_text("1.0")
                self.wTree.get_object("spinbuttonNombreClassesHisto3D").set_value(graphique.getValue("nombreClassesHisto"))
            else :
                self.wTree.get_object("radiobuttonAmplitudeClassesHisto3D").set_active(True)
                self.wTree.get_object("spinbuttonNombreClassesHisto3D").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesHisto3D").set_sensitive(True)                
                self.wTree.get_object("entryAmplitudeClassesHisto3D").set_text(str(graphique.getValue("amplitudeClassesHisto")))
                self.wTree.get_object("spinbuttonNombreClassesHisto3D").set_value(graphique.getValue("nombreClassesHisto"))
            self.noEvent = False
            if graphique.getValue("minHisto") != graphique.getDefault("minHisto") :
                self.wTree.get_object("checkbuttonMinHisto3D").set_active(True)
            else :
                self.wTree.get_object("checkbuttonMinHisto3D").set_active(False)
            self.wTree.get_object("checkbuttonMinHisto3D").emit("toggled")
            if graphique.getValue("maxHisto") != graphique.getDefault("maxHisto") :
                self.wTree.get_object("checkbuttonMaxHisto3D").set_active(True)
            else :
                self.wTree.get_object("checkbuttonMaxHisto3D").set_active(False)
            self.wTree.get_object("checkbuttonMaxHisto3D").emit("toggled")
            self.wTree.get_object("spinbuttonLargeurHisto3D").set_value(graphique.getValue("largeurBarre"))
            self.wTree.get_object("spinbuttonEpaisseurHisto3D").set_value(graphique.getValue("epaisseurBarre"))
            
            # legendeAida
            wla = self.vue.getChildByName(self.window, "checkbuttonLegendeAida3D")
            if graphique.getValue("legendeAida") == "oui" :
                wla.set_active(True)
            else :
                wla.set_active(False)
                
            # pourcentage pour histo
            wbp = self.vue.getChildByName(self.window, "checkbuttonPourcentageHisto3D")
            if graphique.getValue("norme") == "oui" :
                wbp.set_active(True)
            else :
                wbp.set_active(False)
                
            # groupe de liaison
            self.noEvent = True
            wgl = self.vue.getChildByName(self.window, "checkbuttonGroupeLiaisonHisto3D")
            self.wTree.get_object("hboxGroupeLiaisonHisto3D").set_visible(True)
            if graphique.getValue("groupe_liaison") != graphique.getDefault("groupe_liaison") :
                wgl.set_active(True)
                self.wTree.get_object("spinbuttonGroupeLiaisonHisto3D").set_value(graphique.getValue("groupe_liaison"))
                self.wTree.get_object("spinbuttonGroupeLiaisonHisto3D").set_sensitive(True)
            else :
                wgl.set_active(False)
                self.wTree.get_object("spinbuttonGroupeLiaisonHisto3D").set_sensitive(False)
            self.noEvent = False
                
        elif graphique.type == "RDV" :
            titre = "entryTitreGraphRDV"
            fontTitre = "fontbuttonTitreGraphRDV"
            self.noEvent = True
            if graphique.getValue("roseStandard") == "oui" :
                self.wTree.get_object("radiobuttonRoseStandard").set_active(True)
                self.wTree.get_object("spinbuttonNombreClassesRDV").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesRDV").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesRDV").set_text("1.0")
                self.wTree.get_object("frameEchantillonRDV").set_sensitive(False)
                self.wTree.get_object("checkbuttonMaxRDV").set_active(False)
                self.wTree.get_object("entryMinRDV").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("minHisto"))
                self.wTree.get_object("checkbuttonInfRDV").set_active(False)
                self.wTree.get_object("checkbuttonMinRDV").set_active(False)
                self.wTree.get_object("entryMaxRDV").set_text(self.vue.document.getElementById(vc.Document.currentId).getDefault("maxHisto"))
                self.wTree.get_object("checkbuttonSupRDV").set_active(False)                
            else :
                if graphique.getValue("amplitudeClassesHisto") == graphique.getDefault("amplitudeClassesHisto") : #on utilise le nombre de classes
                    self.wTree.get_object("radiobuttonNombreClassesRDV").set_active(True)
                    self.wTree.get_object("spinbuttonNombreClassesRDV").set_sensitive(True)
                    self.wTree.get_object("entryAmplitudeClassesRDV").set_sensitive(False)
                    self.wTree.get_object("entryAmplitudeClassesRDV").set_text("1.0")
                    self.wTree.get_object("spinbuttonNombreClassesRDV").set_value(graphique.getValue("nombreClassesHisto"))
                else :
                    self.wTree.get_object("radiobuttonAmplitudeClassesRDV").set_active(True)
                    self.wTree.get_object("spinbuttonNombreClassesRDV").set_sensitive(False)
                    self.wTree.get_object("entryAmplitudeClassesRDV").set_sensitive(True)                
                    self.wTree.get_object("entryAmplitudeClassesRDV").set_text(str(graphique.getValue("amplitudeClassesHisto")))
                    self.wTree.get_object("spinbuttonNombreClassesRDV").set_value(graphique.getValue("nombreClassesHisto"))
            self.noEvent = False
            if graphique.getValue("minHisto") != graphique.getDefault("minHisto") :
                self.wTree.get_object("checkbuttonMinRDV").set_active(True)
            else :
                self.wTree.get_object("checkbuttonMinRDV").set_active(False)
            self.wTree.get_object("checkbuttonMinRDV").emit("toggled")
            if graphique.getValue("maxHisto") != graphique.getDefault("maxHisto") :
                self.wTree.get_object("checkbuttonMaxRDV").set_active(True)
            else :
                self.wTree.get_object("checkbuttonMaxRDV").set_active(False)
            self.wTree.get_object("checkbuttonMaxRDV").emit("toggled")
            
            # legendeAida
            wla = self.vue.getChildByName(self.window, "checkbuttonLegendeAidaRDV")
            if graphique.getValue("legendeAida") == "oui" :
                wla.set_active(True)
            else :
                wla.set_active(False)
            # secteurs, type et couleur    
            self.wTree.get_object("comboboxSecteursRDV").set_active(self.vue.secteursRDV.index(str(graphique.getValue("secteursRDV"))))
            self.wTree.get_object("comboboxTypeRDV").set_active(graphique.getValue("typeRDV"))
            self.wTree.get_object("comboboxCouleurRDV").set_active(graphique.getValue("couleurRDV"))
            wrev = self.vue.getChildByName(self.window, "checkbuttonPaletteRDVReverse")
            if graphique.getValue("reversePaletteRDV") == "oui" :
                wrev.set_active(True)
            else :
                wrev.set_active(False)
                
            # groupe de liaison
            self.noEvent = True
            wgl = self.vue.getChildByName(self.window, "checkbuttonGroupeLiaisonRDV")
            self.wTree.get_object("hboxGroupeLiaisonRDV").set_visible(True)
            if graphique.getValue("groupe_liaison") != graphique.getDefault("groupe_liaison") :
                wgl.set_active(True)
                self.wTree.get_object("spinbuttonGroupeLiaisonRDV").set_value(graphique.getValue("groupe_liaison"))
                self.wTree.get_object("spinbuttonGroupeLiaisonRDV").set_sensitive(True)
            else :
                wgl.set_active(False)
                self.wTree.get_object("spinbuttonGroupeLiaisonRDV").set_sensitive(False)
            self.noEvent = False           
                
        elif graphique.type == "Hov" :
            titre = "entryTitreGraphHov"
            fontTitre = "fontbuttonTitreGraphHov"
            self.noEvent = True
            # legendeAida
            wla = self.vue.getChildByName(self.window, "checkbuttonLegendeAidaHov")
            if graphique.getValue("legendeAida") == "oui" :
                wla.set_active(True)
            else :
                wla.set_active(False)
            # grille
            wgr = self.vue.getChildByName(self.window, "checkbuttonGrilleHov")
            if graphique.getValue("grille") == "oui" :
                wgr.set_active(True)
            else :
                wgr.set_active(False)
            # inversion de l'axe des ordonnées
            wi = self.vue.getChildByName(self.window, "checkbuttonInverseAxeYHov")
            if graphique.getValue("inverseAxeYHov") == "oui" :
                wi.set_active(True)
            else :
                wi.set_active(False)
            self.noEvent = False
            
            #paramètres de l'axe de gauche
            echelleMin = "entryEchelleMinHov"
            echelleMax = "entryEchelleMaxHov"
            auto = "checkbuttonAutoHov"
            uniteGauche = "checkbuttonUniteGaucheHov"
            labelsGauche = "comboboxLabelsGaucheHov"
            logGauche = "checkbuttonEchelleLogGaucheHov"
            
            wmin = self.vue.getChildByName(self.window, echelleMin)
            wmax = self.vue.getChildByName(self.window, echelleMax)
            wauto = self.vue.getChildByName(self.window, auto)
            
            wmin.set_sensitive(False)
            wmax.set_sensitive(False)
            ech = graphique.getValue("echelle")
            if ech.lower() == "auto" :
                wauto.set_active(True)
                emin = graphique.getValue("echelleMin")
                wmin.set_text(str(emin))
                wmax.set_sensitive(False)
                emax = graphique.getValue("echelleMax")
                wmax.set_text(str(emax))
                
            else :
                wmin.set_sensitive(True)
                emin = graphique.getValue("echelleMin")
                wmin.set_text(str(emin))
                wmax.set_sensitive(True)
                emax = graphique.getValue("echelleMax")
                wmax.set_text(str(emax))
                wauto.set_active(False)
            
            # affichage unité axe de gauche
            wug = self.wTree.get_object(uniteGauche)
            if graphique.getValue("uniteGauche") == "oui" :
                wug.set_active(True)
            else :
                wug.set_active(False)
                
            # affichage labels axe de gauche
            wlg = self.wTree.get_object(labelsGauche)
            qtt_labels = graphique.getValue("labelsGaucheHov")
            value = graphique.labels_gauche_hov.index(qtt_labels)
            wlg.set_active(value)
            
            # affichage echelle log axe de gauche
            welg = self.wTree.get_object(logGauche)
            if graphique.getValue("echelleLogGauche") == "oui" :
                welg.set_active(True)
            else :
                welg.set_active(False)
            
            self.wTree.get_object("frameAxeDroit").show_all()

            # paramètres de l'axe de droite
            echelleMinDroite = "entryEchelleMinDroiteHov"
            echelleMaxDroite = "entryEchelleMaxDroiteHov"
            autoDroite = "checkbuttonAutoDroiteHov"
            amplitudeDroite = "entryEchelleAmplitudeDroiteHov"
            uniteDroite = "checkbuttonUniteDroiteHov"
            labelsDroite = "checkbuttonLabelsDroiteHov"
            logDroite = "checkbuttonEchelleLogDroiteHov"
            wmin = self.vue.getChildByName(self.window, echelleMinDroite)
            wmax = self.vue.getChildByName(self.window, echelleMaxDroite)
            wauto = self.vue.getChildByName(self.window, autoDroite)
            wamp = self.vue.getChildByName(self.window, amplitudeDroite)
            
            wmin.set_sensitive(False)
            wmax.set_sensitive(False)
            wamp.set_sensitive(False)
            ech = graphique.getValue("echelleDroite")
            if ech.lower() == "auto" :
                wauto.set_active(True)
                wamp.set_sensitive(True)
                amp = graphique.getValue("echelleAmplitudeDroite")
                emin = graphique.getValue("echelleMinDroite")
                wmin.set_text(str(emin))
                wmax.set_sensitive(False)
                emax = graphique.getValue("echelleMaxDroite")
                wmax.set_text(str(emax))
                wamp.set_text(str(amp))
                
            else :
                wmin.set_sensitive(True)
                emin = graphique.getValue("echelleMinDroite")
                wmin.set_text(str(emin))
                wmax.set_sensitive(True)
                emax = graphique.getValue("echelleMaxDroite")
                wmax.set_text(str(emax))
                wauto.set_active(False)
                wamp.set_sensitive(False)
                amp = graphique.getValue("echelleAmplitudeDroite")
                wamp.set_text(str(amp))          
                
            # affichage unité axe de droite
            wud = self.wTree.get_object(uniteDroite)
            if graphique.getValue("uniteDroite") == "oui" :
                wud.set_active(True)
            else :
                wud.set_active(False)
                
            # affichage labels axe de droite
            wld = self.wTree.get_object(labelsDroite)
            if graphique.getValue("labelsDroite") == "oui" :
                wld.set_active(True)
            else :
                wld.set_active(False)
                
            # affichage echelle log axe de droite
            weld = self.wTree.get_object(logDroite)
            if graphique.getValue("echelleLogDroite") == "oui" :
                weld.set_active(True)
            else :
                weld.set_active(False)
                
        else : # ST , PlotXY, Histo
            titre = "entryTitreGraph"
            fontTitre = "fontbuttonTitreGraphique"
            echelleMin = "entryEchelleMin"
            echelleMax = "entryEchelleMax"
            auto = "checkbuttonAuto"
            amplitude = "entryEchelleAmplitude"
            echelleMinDroite = "entryEchelleMinDroite"
            echelleMaxDroite = "entryEchelleMaxDroite"
            autoDroite = "checkbuttonAutoDroite"
            amplitudeDroite = "entryEchelleAmplitudeDroite"
            uniteGauche = "checkbuttonUniteGauche"
            uniteDroite = "checkbuttonUniteDroite"
            uniteBas = "checkbuttonUniteBas"
            labelsGauche = "checkbuttonLabelsGauche"
            labelsDroite = "checkbuttonLabelsDroite"
            labelsBas = "checkbuttonLabelsBas"
            logGauche = "checkbuttonEchelleLogGauche"
            logDroite = "checkbuttonEchelleLogDroite"
            logBas = "checkbuttonEchelleLogBas"
            periodeActiver = "checkbuttonDecoupageActiver"
            periodeJour = "radiobuttonDecoupageJour"
            periodeMois = "radiobuttonDecoupageMois"
            periodeAn = "radiobuttonDecoupageAn"
            nombreJours = "spinbuttonDecoupageNombreJours"
            
                
            #paramètres de l'axe de gauche commun aux trois graphiques
            wmin = self.vue.getChildByName(self.window, echelleMin)
            wmax = self.vue.getChildByName(self.window, echelleMax)
            wauto = self.vue.getChildByName(self.window, auto)
            wamp = self.vue.getChildByName(self.window, amplitude)
            
            wmin.set_sensitive(False)
            wmax.set_sensitive(False)
            wamp.set_sensitive(False)
            ech = graphique.getValue("echelle")
            if ech.lower() == "auto" :
                wauto.set_active(True)
                wamp.set_sensitive(True)
                amp = graphique.getValue("echelleAmplitude")
                emin = graphique.getValue("echelleMin")
                wmin.set_text(str(emin))
                wmax.set_sensitive(False)
                emax = graphique.getValue("echelleMax")
                wmax.set_text(str(emax))
                wamp.set_text(str(amp))
                
            else :
                wmin.set_sensitive(True)
                emin = graphique.getValue("echelleMin")
                wmin.set_text(str(emin))
                wmax.set_sensitive(True)
                emax = graphique.getValue("echelleMax")
                wmax.set_text(str(emax))
                wauto.set_active(False)
                wamp.set_sensitive(False)
                amp = graphique.getValue("echelleAmplitude")
                wamp.set_text(str(amp))
            
            # affichage unité axe de gauche
            wug = self.wTree.get_object(uniteGauche)
            if graphique.getValue("uniteGauche") == "oui" :
                wug.set_active(True)
            else :
                wug.set_active(False)
                
            # affichage labels axe de gauche
            wlg = self.wTree.get_object(labelsGauche)
            if graphique.getValue("labelsGauche") == "oui" :
                wlg.set_active(True)
            else :
                wlg.set_active(False)
                
            # affichage echelle log axe de gauche
            welg = self.wTree.get_object(logGauche)
            if graphique.getValue("echelleLogGauche") == "oui" :
                welg.set_active(True)
            else :
                welg.set_active(False)
                
            #paramètres de l'axe de droite pour ST et Histo
            if graphique.getValue("type") == "ST" or graphique.getValue("type") != "Histo" :
                self.wTree.get_object("frameAxeDroit").show_all()
                #echelle axe de droite
                wmin = self.vue.getChildByName(self.window, echelleMinDroite)
                wmax = self.vue.getChildByName(self.window, echelleMaxDroite)
                wauto = self.vue.getChildByName(self.window, autoDroite)
                wamp = self.vue.getChildByName(self.window, amplitudeDroite)
                
                wmin.set_sensitive(False)
                wmax.set_sensitive(False)
                wamp.set_sensitive(False)
                ech = graphique.getValue("echelleDroite")
                if ech.lower() == "auto" :
                    wauto.set_active(True)
                    wamp.set_sensitive(True)
                    amp = graphique.getValue("echelleAmplitudeDroite")
                    emin = graphique.getValue("echelleMinDroite")
                    wmin.set_text(str(emin))
                    wmax.set_sensitive(False)
                    emax = graphique.getValue("echelleMaxDroite")
                    wmax.set_text(str(emax))
                    wamp.set_text(str(amp))
                    
                else :
                    wmin.set_sensitive(True)
                    emin = graphique.getValue("echelleMinDroite")
                    wmin.set_text(str(emin))
                    wmax.set_sensitive(True)
                    emax = graphique.getValue("echelleMaxDroite")
                    wmax.set_text(str(emax))
                    wauto.set_active(False)
                    wamp.set_sensitive(False)
                    amp = graphique.getValue("echelleAmplitudeDroite")
                    wamp.set_text(str(amp))          
                    
                # affichage unité axe de droite
                wud = self.wTree.get_object(uniteDroite)
                if graphique.getValue("uniteDroite") == "oui" :
                    wud.set_active(True)
                else :
                    wud.set_active(False)
                    
                # affichage labels axe de droite
                wld = self.wTree.get_object(labelsDroite)
                if graphique.getValue("labelsDroite") == "oui" :
                    wld.set_active(True)
                else :
                    wld.set_active(False)
                    
                # affichage echelle log axe de droite
                weld = self.wTree.get_object(logDroite)
                if graphique.getValue("echelleLogDroite") == "oui" :
                    weld.set_active(True)
                else :
                    weld.set_active(False)
            else :
                self.wTree.get_object("frameAxeDroit").hide()        
                    
            #paramètres de l'axe du bas pour PlotXY et Histo
            if graphique.getValue("type") == "PlotXY" or graphique.getValue("type") == "Histo" :
                self.wTree.get_object("frameAxeBas").show_all()
                if graphique.getValue("type") == "PlotXY" :
                    #echelle axe du bas
                    wmin = self.wTree.get_object("entryEchelleMinBas")
                    wmax = self.wTree.get_object("entryEchelleMaxBas")
                    wauto = self.wTree.get_object("checkbuttonAutoBas")
                    wamp = self.wTree.get_object("entryEchelleAmplitudeBas")
                    
                    wmin.set_sensitive(False)
                    wmax.set_sensitive(False)
                    wamp.set_sensitive(False)
                    ech = graphique.getValue("echelleBas")
                    if ech.lower() == "auto" :
                        wauto.set_active(True)
                        wamp.set_sensitive(True)
                        amp = graphique.getValue("echelleAmplitudeBas")
                        emin = graphique.getValue("echelleMinBas")
                        wmin.set_text(str(emin))
                        wmax.set_sensitive(False)
                        emax = graphique.getValue("echelleMaxBas")
                        wmax.set_text(str(emax))
                        wamp.set_text(str(amp))
                        
                    else :
                        wmin.set_sensitive(True)
                        emin = graphique.getValue("echelleMinBas")
                        wmin.set_text(str(emin))
                        wmax.set_sensitive(True)
                        emax = graphique.getValue("echelleMaxBas")
                        wmax.set_text(str(emax))
                        wauto.set_active(False)
                        wamp.set_sensitive(False)
                        amp = graphique.getValue("echelleAmplitudeBas")
                        wamp.set_text(str(amp))
                else : # pas de choix auto, mn/max pour Histo
                    self.wTree.get_object("hboxAutoBas").hide()
                    self.wTree.get_object("hboxMinMaxBas").hide()
                    
                # affichage unité axe de droite
                wub = self.wTree.get_object(uniteBas)
                if graphique.getValue("uniteBas") == "oui" :
                    wub.set_active(True)
                else :
                    wub.set_active(False)
                        
                # affichage labels axe du bas
                wlb = self.wTree.get_object(labelsBas)
                if graphique.getValue("labelsBas") == "oui" :
                    wlb.set_active(True)
                else :
                    wlb.set_active(False)
                
                # affichage echelle log axe du bas
                welb = self.wTree.get_object(logBas)
                if graphique.getValue("echelleLogBas") == "oui" :
                    welb.set_active(True)
                else :
                    welb.set_active(False)
            else :
                self.wTree.get_object("frameAxeBas").hide()
                            
            # pourcentage pour histo
            wp = self.wTree.get_object("hboxPourcentage")
            if graphique.getValue("type") != "Histo" :
                wp.hide()
            else :
                wbp = self.vue.getChildByName(self.window, "checkbuttonPourcentage")
                if graphique.getValue("norme") == "oui" :
                    wbp.set_active(True)
                else :
                    wbp.set_active(False)
                wp.show_all()
                
            # legendeAida
            wla = self.vue.getChildByName(self.window, "checkbuttonLegendeAida")
            if graphique.getValue("legendeAida") == "oui" :
                wla.set_active(True)
            else :
                wla.set_active(False)
                
            # grille
            wgr = self.vue.getChildByName(self.window, "checkbuttonGrille")
            if graphique.getValue("grille") == "oui" :
                wgr.set_active(True)
            else :
                wgr.set_active(False)
                
            # grille
            wfd = self.vue.getChildByName(self.window, "checkbuttonFitData")
            if graphique.getValue("fitData") == "oui" :
                wfd.set_active(True)
            else :
                wfd.set_active(False)
                                
            # legende ST
            wlg = self.wTree.get_object("checkbuttonLegendeST")
            wbl = self.wTree.get_object("buttonLegendeST")
            if graphique.getValue("legendeVisible") == "oui" :
                wlg.set_active(True)
                wbl.set_sensitive(True)
            else :
                wlg.set_active(False)
                wbl.set_sensitive(False)
                
            # jourNuit
            if graphique.getValue("type") != "ST" :
                self.wTree.get_object("hboxJourNuit").set_visible(False)
            else :
                self.wTree.get_object("hboxJourNuit").set_visible(True)
            wjn = self.vue.getChildByName(self.window, "checkbuttonJourNuit")
            if graphique.getValue("jourNuit") == "oui" :
                wjn.set_active(True)
            else :
                wjn.set_active(False)
                 
            # moisAnnees
            if graphique.getValue("type") != "ST" :
                self.wTree.get_object("hboxJourNuit").set_visible(False)
                self.wTree.get_object("hboxMoisAnnees").set_visible(False)
            else :
                self.wTree.get_object("hboxJourNuit").set_visible(True)
                self.wTree.get_object("hboxMoisAnnees").set_visible(True)
            wma = self.vue.getChildByName(self.window, "checkbuttonMoisAnnees")
            if graphique.getValue("moisAnnees") == "oui" :
                wma.set_active(True)
            else :
                wma.set_active(False)
                 
            # x=y
            wxy = self.vue.getChildByName(self.window, "checkbuttonXY")
            if graphique.getValue("type") == "PlotXY" :
                self.wTree.get_object("hboxXegaleY").set_visible(True)
                if graphique.getValue("x=y") == "oui" :
                    wxy.set_active(True)
                else :
                    wxy.set_active(False)           
            else :
                self.wTree.get_object("hboxXegaleY").set_visible(False)
                wxy.set_active(False)
                
            # y=n
            wyn = self.vue.getChildByName(self.window, "checkbuttonYN")
            if graphique.getValue("type") == "ST" :
                self.wTree.get_object("hboxYegaleN").set_visible(True)
                if graphique.getValue("y=n") == "oui" :
                    wyn.set_active(True)
                    self.vue.getChildByName(self.window, "entryYN").set_sensitive(True)
                else :
                    wyn.set_active(False)
                    self.vue.getChildByName(self.window, "entryYN").set_sensitive(False)           
            else :
                self.wTree.get_object("hboxYegaleN").set_visible(False)
                wyn.set_active(False)
            #n
            if graphique.getValue("type") == "ST" :
                n = graphique.getValue("n")
                self.vue.getChildByName(self.window, "entryYN").set_text(str(n))
                
            # groupe de liaison
            self.noEvent = True
            if graphique.getValue("type") == "Histo" :
                wgl = self.vue.getChildByName(self.window, "checkbuttonGroupeLiaison")
                self.wTree.get_object("hboxGroupeLiaison").set_visible(True)
                if graphique.getValue("groupe_liaison") != graphique.getDefault("groupe_liaison") :
                    wgl.set_active(True)
                    self.wTree.get_object("spinbuttonGroupeLiaison").set_value(graphique.getValue("groupe_liaison"))
                    self.wTree.get_object("spinbuttonGroupeLiaison").set_sensitive(True)
                else :
                    wgl.set_active(False)
                    self.wTree.get_object("spinbuttonGroupeLiaison").set_sensitive(False)
            else :
                self.wTree.get_object("hboxGroupeLiaison").set_visible(False)
            self.noEvent = False

            # découpage période temporelle
            wpa = self.wTree.get_object(periodeActiver)
            if graphique.getValue("decoupageActiver") == "oui" :
                wpa.set_active(True)
            else :
                wpa.set_active(False)
            if graphique.getValue("decoupagePeriode") == "j" :
                wdp = self.wTree.get_object(periodeJour)
                self.wTree.get_object(nombreJours).set_value(graphique.getValue("nombreJoursDecoupage"))
            elif graphique.getValue("decoupagePeriode") == "m" : 
                wdp = self.wTree.get_object(periodeMois) 
            else :
                wdp = self.wTree.get_object(periodeAn)
            wdp.set_active(True)
            self.wTree.get_object("comboboxDecoupageCouleur").set_active(graphique.getValue("couleurDecoupage"))
            wrev = self.vue.getChildByName(self.window, "checkbuttonDecoupagePaletteReverse")
            if graphique.getValue("reversePaletteDecoupage") == "oui" :
                wrev.set_active(True)
            else :
                wrev.set_active(False)
                           
                        
        #attributs communs à tous les types de graphiques  
        #titre
        w = self.vue.getChildByName(self.window, titre)
        w.set_text(graphique.getValue("titre"))
        #police du titre
        w = self.vue.getChildByName(self.window, fontTitre)
        w.set_font(graphique.getValue("policeTitre"))     
        
    def updateUiTrace(self, trace) :
        if trace.type == "ST"  or trace.type == "Histo3D" :
            colorbuttonTrace = "mycolorbuttonTraceST"
            radiobuttonPointille = "radiobuttonPointille"
            radiobuttonTirete = "radiobuttonTirete"
            radiobuttonPlein = "radiobuttonPlein"
            radiobuttonAucunTrait = "radiobuttonAucunTrait"
            spinbuttonEpaisseur = "spinbuttonEpaisseur"
            radiobuttonMarqueurAucun = "radiobuttonMarqueurAucun"
            radiobuttonMarqueurCroix = "radiobuttonMarqueurCroix"
            radiobuttonMarqueurPoint = "radiobuttonMarqueurPoint"
            radiobuttonMarqueurCarre = "radiobuttonMarqueurCarre"
            radiobuttonMarqueurRond = "radiobuttonMarqueurRond"
            radiobuttonMarqueurTriangle = "radiobuttonMarqueurTriangle"
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme", "plateforme","comboboxParametre" , "parametre", "imageWarningCalculette1", trace)    
            self.wTree.get_object("hboxRegression").set_visible(False)
            if trace.type == "Histo3D" :
                self.wTree.get_object("hboxTypeTrait").set_visible(False)
                self.wTree.get_object("hboxEpaisseurTrait").set_visible(False)
                self.wTree.get_object("hboxMarqueur").set_visible(False)
            else :
                self.wTree.get_object("hboxTypeTrait").set_visible(True)
                self.wTree.get_object("hboxEpaisseurTrait").set_visible(True)
                self.wTree.get_object("hboxMarqueur").set_visible(True)
                self.wTree.get_object("hboxAffichageConditionnel").set_visible(True)
                               
            
            buttonAffichageConditionnel = self.wTree.get_object("buttonAffichageConditionnel")
            image = Gtk.Image() 
            if len(trace.expressions_condition) > 1 :
                image.set_from_pixbuf(Pixbuf.new_from_file(self.vue.dirIcons+"/affichage_conditionnel2_20x20.png"))
            else :
                image.set_from_pixbuf(Pixbuf.new_from_file(self.vue.dirIcons+"/affichage_conditionnel_20x20.png"))
                
            buttonAffichageConditionnel.set_image(image)
            # cumul
            if trace.type == "ST" :
                self.wTree.get_object("hboxAffichageCumul").set_visible(True)
            else :
                self.wTree.get_object("hboxAffichageCumul").set_visible(False)
            cumul = trace.getValue("cumul")
            if cumul == 0 :
                w = self.vue.getChildByName(self.window, "radiobuttonCumulAucun")
            elif cumul == 1 :
                w = self.vue.getChildByName(self.window, "radiobuttonCumulSansRaz")
            else :
                w = self.vue.getChildByName(self.window, "radiobuttonCumulAvecRaz")
            w.set_active(True)
            # axe_y
            axe_y = trace.getValue("axe_y")
            if axe_y == 0 :
                w = self.vue.getChildByName(self.window, "radiobuttonAxeYGaucheST")
            elif axe_y == 1 :
                w = self.vue.getChildByName(self.window, "radiobuttonAxeYDroitST")
            else :
                w = self.vue.getChildByName(self.window, "radiobuttonAxeYAutoST")
            w.set_active(True)
                
            
        elif trace.type == "PlotXY" :
            colorbuttonTrace = "mycolorbuttonTracePlotXY"
            radiobuttonPointille = "radiobuttonPointillePlotXY"
            radiobuttonTirete = "radiobuttonTiretePlotXY"
            radiobuttonPlein = "radiobuttonPleinPlotXY"
            radiobuttonAucunTrait = "radiobuttonAucunTraitPlotXY"
            spinbuttonEpaisseur = "spinbuttonEpaisseurPlotXY"
            radiobuttonMarqueurAucun = "radiobuttonMarqueurAucunPlotXY"
            radiobuttonMarqueurCroix = "radiobuttonMarqueurCroixPlotXY"
            radiobuttonMarqueurPoint = "radiobuttonMarqueurPointPlotXY"
            radiobuttonMarqueurCarre = "radiobuttonMarqueurCarrePlotXY"
            radiobuttonMarqueurRond = "radiobuttonMarqueurRondPlotXY"
            radiobuttonMarqueurTriangle = "radiobuttonMarqueurTrianglePlotXY"
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_x", "plateforme_x","comboboxParametre_x" , "parametre_x", "imageWarningCalculette2",trace)
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_y", "plateforme","comboboxParametre_y" , "parametre", "imageWarningCalculette3", trace)
            # regression
            self.wTree.get_object("hboxRegression").set_visible(True)
            wrg = self.vue.getChildByName(self.window, "checkbuttonRegression")            
            if trace.getValue("regression") == "oui" :
                wrg.set_active(True)
            else :
                wrg.set_active(False)
            buttonAffichageConditionnel = self.wTree.get_object("buttonAffichageConditionnelPlotXY")
            image = Gtk.Image() 
            if len(trace.expressions_condition) > 1 :
                image.set_from_pixbuf(Pixbuf.new_from_file(self.vue.dirIcons+"/affichage_conditionnel2_20x20.png"))
            else :
                image.set_from_pixbuf(Pixbuf.new_from_file(self.vue.dirIcons+"/affichage_conditionnel_20x20.png"))

            buttonAffichageConditionnel.set_image(image)
            # axe_y
            axe_y = trace.getValue("axe_y")
            if axe_y == 0 :
                w = self.vue.getChildByName(self.window, "radiobuttonAxeYGauchePlotXY")
            elif axe_y == 1 :
                w = self.vue.getChildByName(self.window, "radiobuttonAxeYDroitPlotXY")
            else :
                w = self.vue.getChildByName(self.window, "radiobuttonAxeYAutoPlotXY")
            w.set_active(True)
            
        elif trace.type == "Histo" :
            colorbuttonTrace = "mycolorbuttonTraceHisto"
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_h", "plateforme","comboboxParametre_h" , "parametre", "imageWarningCalculette4", trace)    
            self.wTree.get_object("hboxRegression").set_visible(False)
            self.noEvent = True
            if trace.getValue("amplitudeClassesHisto") == trace.getDefault("amplitudeClassesHisto") : #on utilise le nombre de classes
                self.wTree.get_object("radiobuttonNombreClassesHisto").set_active(True)
                self.wTree.get_object("spinbuttonNombreClassesHisto").set_sensitive(True)
                self.wTree.get_object("entryAmplitudeClassesHisto").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesHisto").set_text("1.0")
                self.wTree.get_object("spinbuttonNombreClassesHisto").set_value(trace.getValue("nombreClassesHisto"))
            else :
                self.wTree.get_object("radiobuttonAmplitudeClassesHisto").set_active(True)
                self.wTree.get_object("spinbuttonNombreClassesHisto").set_sensitive(False)
                self.wTree.get_object("entryAmplitudeClassesHisto").set_sensitive(True)                
                self.wTree.get_object("entryAmplitudeClassesHisto").set_text(str(trace.getValue("amplitudeClassesHisto")))
                self.wTree.get_object("spinbuttonNombreClassesHisto").set_value(trace.getValue("nombreClassesHisto"))
            self.noEvent = False
            if trace.getValue("minHisto") != trace.getDefault("minHisto") :
                self.wTree.get_object("checkbuttonMinHisto").set_active(True)
            else :
                self.wTree.get_object("checkbuttonMinHisto").set_active(False)
            self.wTree.get_object("checkbuttonMinHisto").emit("toggled")
            if trace.getValue("maxHisto") != trace.getDefault("maxHisto") :
                self.wTree.get_object("checkbuttonMaxHisto").set_active(True)
            else :
                self.wTree.get_object("checkbuttonMaxHisto").set_active(False)
            self.wTree.get_object("checkbuttonMaxHisto").emit("toggled")
            # labels
            if trace.getValue("labelNombreHisto") == "oui" :
                self.wTree.get_object("checkbuttonLabelNombreHisto").set_active(True)
            else :
                self.wTree.get_object("checkbuttonLabelNombreHisto").set_active(False)
            if trace.getValue("labelPourcentHisto") == "oui" :
                self.wTree.get_object("checkbuttonLabelPourcentHisto").set_active(True)
            else :
                self.wTree.get_object("checkbuttonLabelPourcentHisto").set_active(False)
            buttonAffichageConditionnel = self.wTree.get_object("buttonAffichageConditionnelHisto")
            image = Gtk.Image() 
            if len(trace.expressions_condition) > 1 :
                image.set_from_pixbuf(Pixbuf.new_from_file(self.vue.dirIcons+"/affichage_conditionnel2_20x20.png"))
            else :
                image.set_from_pixbuf(Pixbuf.new_from_file(self.vue.dirIcons+"/affichage_conditionnel_20x20.png"))
            buttonAffichageConditionnel.set_image(image)
                
        elif trace.type == "RDV" :
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_rdv", "plateforme","comboboxParametre_dd" , "parametre_x", "imageWarningCalculette5", trace)    
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_rdv", "plateforme","comboboxParametre_ff" , "parametre", "imageWarningCalculette6", trace)    
        
        elif trace.type == "Hov" :
            # typeHov
            self.noEvent = True
            typeHov = trace.getValue("typeHov")
            self.wTree.get_object("spinbuttonLargeurHov").set_value(100.0)
            if typeHov != "iso-shading" and typeHov != "shading" and typeHov != "iso" :
                self.wTree.get_object("radiobuttonHovDiscret").set_active(True)
                self.wTree.get_object("hboxHovShading").set_sensitive(False)
                self.wTree.get_object("hboxHovAuto").set_sensitive(True)                                
                if typeHov == "auto" :
                    self.wTree.get_object("checkbuttonHovAuto").set_active(True)
                    self.wTree.get_object("hboxLargeurHov").set_sensitive(False)
                else :
                    self.wTree.get_object("hboxLargeurHov").set_sensitive(True)
                    value = float((typeHov)[:-1])
                    self.wTree.get_object("spinbuttonLargeurHov").set_value(value)                
                    self.wTree.get_object("checkbuttonHovAuto").set_active(False)
            else :
                self.wTree.get_object("radiobuttonHovInter").set_active(True)
                self.wTree.get_object("hboxHovShading").set_sensitive(True)
                self.wTree.get_object("hboxHovAuto").set_sensitive(False)                
                if typeHov == "iso-shading" :
                    self.wTree.get_object("checkbuttonHovShading").set_active(True)
                    self.wTree.get_object("checkbuttonHovIsolignes").set_active(True)
                if typeHov == "shading" :
                    self.wTree.get_object("checkbuttonHovShading").set_active(True)
                    self.wTree.get_object("checkbuttonHovIsolignes").set_active(False)
                if typeHov == "iso" :
                    self.wTree.get_object("checkbuttonHovIsolignes").set_active(True)
                    self.wTree.get_object("checkbuttonHovShading").set_active(False)
            self.noEvent = False        
            # couleur    
            self.wTree.get_object("comboboxCouleurHov").set_active(trace.getValue("couleurHov"))
            wrev = self.vue.getChildByName(self.window, "checkbuttonPaletteHovReverse")
            if trace.getValue("reversePaletteHov") == "oui" :
                wrev.set_active(True)
            else :
                wrev.set_active(False)
            wa = self.vue.getChildByName(self.window, "checkbuttonHovSeuilAuto")
            if trace.getValue("seuilAutoHov") == "oui" :
                wa.set_active(True)
                self.wTree.get_object("hboxHovSeuil").set_sensitive(False)
                self.noEvent = False
                self.wTree.get_object("entryHovSeuilMin").set_text(str(trace.getDefault("seuilMinHov")))
                self.wTree.get_object("entryHovSeuilMax").set_text(str(trace.getDefault("seuilMaxHov")))
                self.wTree.get_object("checkbuttonHovHorsGammeVisible").set_active(False)
                self.noEvent = True
            else :
                wa.set_active(False)
                self.wTree.get_object("hboxHovSeuil").set_sensitive(True)
                self.noEvent = False
                self.wTree.get_object("entryHovSeuilMin").set_text(str(trace.getValue("seuilMinHov")))
                self.wTree.get_object("entryHovSeuilMax").set_text(str(trace.getValue("seuilMaxHov")))
                if trace.getValue("horsGammeVisibleHov") == "oui" :
                    self.wTree.get_object("checkbuttonHovHorsGammeVisible").set_active(True)
                else :
                    self.wTree.get_object("checkbuttonHovHorsGammeVisible").set_active(False)
                self.noEvent = True        
            
            # plate-forme et parametre        
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_hov", "plateforme","comboboxParametre_hov" , "parametre", "imageWarningCalculette7", trace)
            
            # quiver
            self.noEvent = False
            wq = self.vue.getChildByName(self.window, "checkbuttonHovQuiver")           
            if trace.getValue("quiverHov") == "oui" :
                wq.set_active(True)                               
            else :
                wq.set_active(False)
            wuv = self.vue.getChildByName(self.window, "radiobuttonHovQuiverUV")
            wddff = self.vue.getChildByName(self.window, "radiobuttonHovQuiverDdFf")
            if trace.getValue("quiverModeUVHov") == "oui" :             
                wuv.set_active(True)                               
            else :
                wddff.set_active(True)                
            self.noEvent = True
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_hov_quiver", "plateformeQuiverHov","comboboxParametre_hov_quiver_dd" , "parametre_dd_hov", "imageWarningCalculette7", trace)
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_hov_quiver", "plateformeQuiverHov","comboboxParametre_hov_quiver_ff" , "parametre_ff_hov", "imageWarningCalculette7", trace)
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_hov_quiver", "plateformeQuiverHov","comboboxParametre_hov_quiver_u" , "parametre_u_hov", "imageWarningCalculette7", trace)
            self.updateUiPlateformeAndParametre(self.window, "comboboxentryPlateforme_hov_quiver", "plateformeQuiverHov","comboboxParametre_hov_quiver_v" , "parametre_v_hov", "imageWarningCalculette7", trace)
            
            wex = self.vue.getChildByName(self.window, "comboboxHovQuiverEchantillonX")
            index = self.getComboIndex(wex, trace.getValue("echantillonHovQuiverX"), 0)
            wex.set_active(index)
   
            wey = self.vue.getChildByName(self.window, "comboboxHovQuiverEchantillonY")
            index = self.getComboIndex(wey, trace.getValue("echantillonHovQuiverY"), 0)
            wey.set_active(index)
            self.noEvent = False   

        #couleur
        if trace.type != "RDV" and trace.type != "Hov" :
            w = self.vue.getChildByName(self.window, colorbuttonTrace)
            w.setRgba(trace.getValue("couleur"))
        
        if trace.type != "Histo"  and trace.type != "Histo3D" and trace.type != "RDV" and trace.type != "Hov":
            #trait
            trait = trace.getValue("typeLigne")
            if trait == ":" :
                w = self.vue.getChildByName(self.window, radiobuttonPointille)
                w.set_active(True)
            elif trait == "--" :
                w = self.vue.getChildByName(self.window, radiobuttonTirete)
                w.set_active(True)
            elif trait == "-" :
                w = self.vue.getChildByName(self.window, radiobuttonPlein)
                w.set_active(True)
            else :
                w = self.vue.getChildByName(self.window, radiobuttonAucunTrait)
                w.set_active(True)
                
            #epaisseur
            epaisseur = trace.getValue("epaisseur")
            w = self.vue.getChildByName(self.window, spinbuttonEpaisseur)
            w.set_value(epaisseur)
                
            #points
            point = trace.getValue("marqueur")
            if point == "None" :
                w = self.vue.getChildByName(self.window, radiobuttonMarqueurAucun)
                w.set_active(True)
            elif point == "+" :
                w = self.vue.getChildByName(self.window, radiobuttonMarqueurCroix)
                w.set_active(True)
            elif point == "s" :
                w = self.vue.getChildByName(self.window, radiobuttonMarqueurCarre)
                w.set_active(True)
            elif point == "o" :
                w = self.vue.getChildByName(self.window, radiobuttonMarqueurRond)
                w.set_active(True)
            elif point == "." :
                w = self.vue.getChildByName(self.window, radiobuttonMarqueurPoint)
                w.set_active(True)
            elif point == "^" :
                w = self.vue.getChildByName(self.window, radiobuttonMarqueurTriangle)
                w.set_active(True)
        # Filtrage des données :
        if trace.type == "PlotXY" :
            self.wTree.get_object("hboxFiltrageConditionnel").set_visible(True)
            wfc = self.wTree.get_object("checkbuttonFiltrageConditionnel")
            if trace.getValue("filtrageConditionnel") == "oui" :
                wfc.set_active(True)
            else :
                wfc.set_active(False)               
        else :
            self.wTree.get_object("hboxFiltrageConditionnel").set_visible(False)
                
    def updateUiPlateformeAndParametre(self, window, wplateforme, attrplateforme, wparametre, attrparametre, imagewarningcalculette, trace):
        #plateforme
        w = self.vue.getChildByName(window, wplateforme)
        tab_plateforme = attrplateforme.split(":")
        if tab_plateforme[0] == "condition" or tab_plateforme[0] == "operation" :
            plateforme = tab_plateforme[1]
        else :
            plateforme = trace.getValue(tab_plateforme[0])
        try :
            plateforme_en_cours = self.vue.plateformes[w.get_child().get_text()]["abrev"]
        except :
            plateforme_en_cours = ""        
        if plateforme_en_cours != plateforme or plateforme_en_cours == "" : # pour eviter un appel a onPlateformeChanged
            store = w.get_child().get_completion().get_model()
            texte = w.get_child().get_text()
            index = 0
            found = 0
            if store != None :
                for row in store :
                    if (plateforme == self.vue.plateformes[row[0]]["abrev"]) :
                        w.set_active(index)
                        found = 1
                        break;        
                    index += 1
                if ( found == 0 or plateforme == "" ) : # on active la dernière plateforme sélectionnée pour que le champ plateforme du tracé soit positionné
                    index = 0
                    for row in store :
                        if (texte == self.vue.plateformes[row[0]]["nom"]) :
                            w.set_active(index)
                            break;
                        index += 1 
        
        #paramètre
        axe = 'y'
        w = self.vue.getChildByName(window, wparametre)
        tab_parametre = attrparametre.split(":")
        if tab_parametre[0] == "condition" :
            parametre = tab_parametre[1]
        elif tab_parametre[0] == "operation" :
            axe = tab_parametre[1]
            parametre = tab_parametre[2]
        else :
            parametre = trace.getValue(tab_parametre[0])
            if tab_parametre[0] == "parametre_x" :
                axe = 'x'
        store = w.get_model()
        
        index = 0
        found = 0
        if parametre == "" :
            w.set_active(-1)
            w.get_child().set_text("")
            
        else :
            try :
                my_iter = self.itersParametres[plateforme][parametre]
                w.set_active_iter(my_iter)
            except Exception :
                w.set_active(-1)
                w.get_child().set_text("")
        # affichage du  picto warning si operation
        if imagewarningcalculette != None :
            str_operation = trace.operationToString(axe)
            if str_operation != "" :
                self.wTree.get_object(imagewarningcalculette).set_visible(True)
                self.wTree.get_object(imagewarningcalculette).set_tooltip_text(str_operation)
            else :
                self.wTree.get_object(imagewarningcalculette).set_visible(False)
        
    def findIter(self,modele, chemin, iterateur,dico):
        """
            Retourne l'itérateur du treeview correspondant aux paramètres du dico
        """
        if modele.get_value(iterateur, dico["pos"]) == dico["value"] :
            dico["iter"] = iterateur
            return True
        else :
            return False
        
    def getIterById(self,idElmt) :
        """
            Retourne l'itérateur du treeview correspondant à l'élément
        """
        dico = {"value":idElmt, "pos":1, "iter":None}
        self.vue.treestore.foreach(self.findIter, dico)
        
        return dico["iter"]
                
    def updateNotebookVista(self, numPage):
        """
            Met à jour l'affichage des graphiques dans le notebook.
        """
                           
        def onNotebookPageChanged(w, page, page_num):
            if self.noEvent :
                return
            if self.modified :
                return

            idElmt = self.vue.document.pages[page_num].id
            dico = {"value":idElmt, "pos":1, "iter":None}
            self.vue.treestore.foreach(self.findIter, dico)
            if dico["iter"] != None :
                self.vue.treeview.get_selection().select_iter(dico["iter"])
            if self.vue.getChildByName(self.window, "notebookMplToolbar") != None :
                self.vue.getChildByName(self.window, "notebookMplToolbar").set_current_page(page_num)
            
            #
            # Les lignes qui suivent sont à activer pour rafraichir le tracé dans la page si besoin
            #
            canvas = self.vue.gdocument.gpages[page_num].canvas
            width, height = canvas.get_size_request()
            canvas.set_size_request(1,1)
            canvas.set_size_request(width, height)
                
        def onClickPage(event):
            page_num = self.vue.getChildByName(self.window, "notebookVista").get_current_page()
            gpage = self.vue.gdocument.gpages[page_num]
            for g in gpage.ggraphiques :
                if event.inaxes == g.subplot :
                    g.button_down = True
                    g.x_click = event.x
                    g.y_click = event.y                        
        
        def onReleasePage(event):
            page_num = self.vue.getChildByName(self.window, "notebookVista").get_current_page()
            gpage = self.vue.gdocument.gpages[page_num]
            for g in gpage.ggraphiques :
                g.button_down = False
                
        def onLeavePage(event):
            self.windowJauge.set_visible(False)
            
        def onMotionPage(event):
            page_num = self.vue.getChildByName(self.window, "notebookVista").get_current_page()
            try :
                gpage = self.vue.gdocument.gpages[page_num]
            except IndexError :
                return
            graph_survole = None
            affiche_jauge = False
            for g in gpage.ggraphiques :
                if str(event.inaxes) == str(g.subplot) :
                    affiche_jauge = True
                    graph_survole = g
                    
                    if g.graphique.type == "Histo3D" :
                        if g.button_down :
                            affiche_jauge = False
                            g.graphique.setValue("azimut", int(g.subplot.azim))
                            g.graphique.setValue("elevation", int(g.subplot.elev))
                    break
            # affichage de la jauge
            if affiche_jauge == True :
                str_jauge, width, height = self.getJauge(event, graph_survole)
                if str_jauge is None :
                    self.windowJauge.set_visible(False) 
                else :
                    dpy = self.vue.rootWindow.get_display()
                    #mnger = dpy.get_device_manager()
                    #device = mnger.get_client_pointer()
                    seat = dpy.get_default_seat()
                    device = seat.get_pointer()
                    _, x, y, _ = self.vue.rootWindow.get_device_position_double(device)
                    
                    self.vue.jauge.load_html(str_jauge,None)                                     
                    self.windowJauge.resize(width, height)
                    self.windowJauge.move(int(x+20), int(y+20))
                    self.windowJauge.set_visible(True)                    
            else :
                self.windowJauge.set_visible(False)      
                    
                
        message = self.vue.gdocument.redraw()
        # on ferme les figures
        for gp in self.vue.gdocument.gpages:
            plt.close(gp.id)
            
        if self.vue.getChildByName(self.window, "notebookVista") != None :
            self.vue.getChildByName(self.window, "notebookVista").destroy()
        if self.vue.getChildByName(self.window, "notebookMplToolbar") != None :
            self.vue.getChildByName(self.window, "notebookMplToolbar").destroy()
        oldEvt = self.noEvent
        self.noEvent = True
        notebook = Gtk.Notebook()
        Gtk.Buildable.set_name(notebook, "notebookVista")
        notebook.set_tab_pos(Gtk.PositionType.BOTTOM)
        notebook.set_border_width(10)
        notebook.set_tab_pos(Gtk.PositionType.LEFT)
        notebook.connect("switch-page",onNotebookPageChanged)
        notebook2 = Gtk.Notebook()
        Gtk.Buildable.set_name(notebook2, "notebookMplToolbar")
        notebook2.set_tab_pos(Gtk.PositionType.BOTTOM)
        notebook2.set_border_width(10)
        notebook2.set_tab_pos(Gtk.PositionType.LEFT)
        self.wTree.get_object("hboxMplToolbar").pack_start(notebook2, True, True, 0)
        #notebook.set_size_request(800,800);
        
        #self.wTree.get_object("viewportVista").add(notebook)
        self.wTree.get_object("vboxNotebookVista").pack_start(notebook, False, False, 0)
        for p in range(0, len(self.vue.gdocument.gpages)) :
            vbox = Gtk.VBox(homogeneous=False, spacing=0)
            hbox = Gtk.HBox(homogeneous=False, spacing=0)
            vbox.pack_start(hbox, False, False, 0);
            frame1 = Gtk.Frame()
            hbox.pack_start(frame1, False, False, 0);
            frame1.set_border_width(10)
            frame1.set_label_align(0.5, 0.5)
            frame1.set_shadow_type(Gtk.ShadowType.NONE)
            ori = self.vue.gdocument.gpages[p].page.getValue("orientation")
            if ori == "portrait" :
                frame1.set_size_request(int(round(495*self.vue.gdocument.zoom)),int(round(700*self.vue.gdocument.zoom))) #A4 portrait
            else :
                frame1.set_size_request(int(round(800*self.vue.gdocument.zoom)),int(round(566*self.vue.gdocument.zoom))) #A4 landscape
            self.vue.gdocument.gpages[p].canvas.mpl_connect('button_press_event', lambda event: onClickPage(event))
            self.vue.gdocument.gpages[p].canvas.mpl_connect('button_release_event', lambda event: onReleasePage(event))
            self.vue.gdocument.gpages[p].canvas.mpl_connect('motion_notify_event', lambda event: onMotionPage(event))
            self.vue.gdocument.gpages[p].canvas.mpl_connect('figure_leave_event', lambda event: onLeavePage(event))
            self.vue.gdocument.gpages[p].canvas.set_can_focus(True)
            frame1.add(self.vue.gdocument.gpages[p].canvas)
            toolbar = vi.NavigationToolbar(self.vue.gdocument.gpages[p].canvas, self.window)
            toolbar.show_all()
            self.vue.getChildByName(self.window, "notebookVista").append_page(vbox)
            self.vue.getChildByName(self.window, "notebookMplToolbar").append_page(toolbar)
            vbox.show_all()
        notebook.show()
        notebook2.show_all()
        notebook.set_current_page(numPage)
        notebook2.set_current_page(numPage)
        notebook2.set_show_tabs(False)
        notebook2.set_show_border(False)

        self.noEvent = oldEvt
        if message != "" :
                vi.VistaDialog(message, self.window)


    #
    # Méthodes associées à la ProgressBar de lecture des données
    #
    def openProgressBar(self):
        """
            Ouvre une fenêtre avec une barre de progression
        """
        def onProgressBarAnnuler(w,e):
            self.progressBarCanceled = True
            
            
            
        # pas de progressbar si la lecture dure moins de 1 seconde
        self.threadLecture.join(1.0)
        if self.threadLecture.is_alive() :
            dialog = Gtk.Dialog(title="", parent=self.window, modal=True, destroy_with_parent=True)
            dialog.set_border_width(10)
            dialog.vbox.show()
            label = Gtk.Label()
            label.set_markup("Lecture des données ...")
            label.show()
            # on crée un label pour afficher le texte car le thème MacTy utilisé par défaut n'affiche pas le label créé
            # par l'attribut show_text = True (pb de couleur ton/ton ?)
            label_fraction = Gtk.Label()
            label_fraction.set_markup("0%")
            label_fraction.show()
            dialog.vbox.pack_start(label, False, False, 0)
            dialog.vbox.pack_start(label_fraction, False, False, 0)
            pbar = Gtk.ProgressBar(show_text=False)
            dialog.vbox.pack_start(pbar, True, True, 10)
            pbar.show_all()
            hbox = Gtk.HBox(homogeneous=False, spacing=0)
            button = Gtk.Button()
            img = Gtk.Image()
            img.set_from_icon_name('edit-delete', Gtk.IconSize.BUTTON)
            button.connect("button-press-event", onProgressBarAnnuler)
            button.add(img)
            button.set_can_focus(False)
            button.set_tooltip_text("Arrêter la récupération des données.")
            hbox.pack_end(button, False, False, 0)
            dialog.vbox.pack_start(hbox, False, False, 0)
            hbox.show_all()
            
            _ = GLib.timeout_add (100, self.updateProgressBar, dialog, pbar, label_fraction)
                   
            dialog.run()
        else :
            return
                
    def updateProgressBar(self, window, pbar, label_fraction):
        """
            Met à jour la barre de progression
        """
        try :
            exc = self.queueLecture.get(block=False)
        except queue.Empty :            
            fraction = self.vue.document.getFractionDataLues()
            if self.progressBarCanceled :
                self.vue.document.arretLecture = True
                window.destroy()
                self.vue.document.clearData()
                return False 
            if fraction < 0 :
                window.destroy()
                return False
            else :
                pbar.set_fraction(fraction)
                #pbar.set_text("{:0.1f}%".format(fraction*100))
                label_fraction.set_text("{:0.1f}%".format(fraction*100))
                return True
        else :
            window.destroy()
            self.queueLecture.put(exc)
            return False
    #
    # Autres méthodes
    #
    def getCurrentId(self):
        """
            Retourne l'id de l'élément sélectionné dans le treeview
        """
        selection = self.vue.treeview.get_selection()
        tree_model, tree_iter = selection.get_selected()
        idElmt = tree_model.get_value(tree_iter, 1)
        return idElmt
    
    def getCurrentElement(self):
        """
            Retourne l'élément sélectionné dans le treeview
        """
        elmt = self.vue.document.getElementById(self.getCurrentId())
        return elmt
    
    def setCursor(self, cursorType):
        """
            Modifie le curseur
        """
        if cursorType != None :
            cursor = Gdk.Cursor(cursorType)  # @UndefinedVariable
            self.window.get_window().set_cursor(cursor)
        else :
            self.window.get_window().set_cursor(None)
        Gdk.flush()  # @UndefinedVariable
    
    def getJauge(self, event, g):
        """
            Retourne le texte à afficher dans la jauge ainsi que la taille.
            Le calcul des valeurs à afficher dépend du type de graphique par exemple :
              ST : on cherche les valeurs les plus proches de chaque tracé associées à la valeur de x (le temps)
              PlotXY : on affiche les valeurs sous la souris en utilisant les coordonées graphiques de event (et non les coordonnées data)
            TODO : selon le type de graphique, la largeur de la jauge est fixée ou calculée de façon plus ou moin 
                   empirique. Il faudrait faire un calcul précis en fonction de la taille de la police.
        """
        str_jauge = "<body style=\"margin:0;padding:0;background-color:#EAF97D\"><center><table>"
        str_jauge_x = ""
        str_jauge_y = ""
        x = event.xdata
        y = event.ydata
        xj = None,
        yj = None
        
        try :
            dim_array = int(AIDA.get_dim_array(g.graphique.traces[0].vecteur_y.attributes["dim_array"])[0])
        except :
            dim_array = 1
        if g.graphique.type == "Hov" and dim_array == 1 :
            for t in g.graphique.traces : # en principe y en a qu'un
                xj,yj = t.getData(x, y)
                if xj is None :
                    str_jauge = None
                else :
                    str_jauge_y = "{}<tr><td>{}</td></tr>".format(str_jauge_y, str(yj)[0:15])
                    str_jauge_x = "<tr><td colspan=2><b>{}</td></b></tr>".format(xj)
                if str_jauge is not None :
                    str_jauge += str_jauge_x + str_jauge_y            
            height = 50+(len(g.graphique.traces)*25)
            if str_jauge is not None :
                str_jauge += "</table></center></body>"    
            return str_jauge, 253, height
        
        if g.graphique.type == "RDV" : # pour RDV getData retourne un tuple et une liste
            try :
                for t in g.graphique.traces :
                    xj,yj = t.getData(x, y)
                    str_jauge_x = "<tr><td colspan=2><b>[{}° {}°[</td></b></tr>".format(xj[0], xj[1])
                    str_jauge_y = "<tr><td>total</td><td align=right> {:.1f}%</td><tr>".format(yj[0]*100/len(np.ma.compressed(t.data_y)))
                    for i in yj[1:] :
                        str_jauge_y += "<tr><td>{}</td><td align=right>{}</td></tr>".format(list(i.keys())[0], list(i.values())[0])
                    str_jauge += str_jauge_x + str_jauge_y
            except :
                pass
            
            finally :
                try :
                    height = 50+((len(g.graphique.info_rdv['bins'])-2)*25)
                except :
                    return None, 200, 0
                if str_jauge != None :
                    str_jauge += "</table></center></body>"
                return str_jauge, 200, height
                
        elif g.graphique.type == "PlotXY" or g.graphique.type == "Hov" : 
            # On utilise les coordonnées graphiques event.x et event.y
            # Pour chaque tracé on calcule les coordonnées data correspondant à ces coordonnées graphiques
            # en utilisant l'axe de la data.
            try :
                display_coord = [event.x, event.y]
                is_jauge = False
                xmax= None
                for gt in g.gtraces :
                    t = gt.trace
                    ax = gt.axe_y
                    inv = ax.transData.inverted()
                    ax_coord = inv.transform(display_coord)
                    x = ax_coord[0]
                    y = ax_coord[1]
                    xj,yj = t.getData(x, y)
                    if xmax is None or xj > xmax :
                        xmax = xj
                    if xj != None :
                        is_jauge = True
                    couleur = t.getValue("couleur")
                    if yj is None :
                        yj = "--"
                    if t.type == "Hov":
                        str_jauge_y = "{}<tr><td colspan=2>{} : {}</td></tr>".format(str_jauge_y, list(yj.keys())[0], str(yj[list(yj.keys())[0]])[0:15])
                    else :
                        str_jauge_y = "{}<tr><td width=20 ><div style=\"border:1px solid black;width:10;height:10;background-color:{}\"/></td><td>{}</td></tr>".format(str_jauge_y,couleur, str(yj)[0:15])
                    str_jauge_x = "<tr><td colspan=2><b>{}</td></b></tr>".format(str(xmax)[0:19])
                if  not is_jauge :
                    str_jauge = None
                else :
                    str_jauge += str_jauge_x + str_jauge_y
            except Exception as e:
                pass
            finally:
                height = 50+(len(g.graphique.traces)*25)
                if str_jauge != None :
                    str_jauge += "</table></center></body>"
                return str_jauge, 200, height   
        else :
            try :
                is_jauge = False
                xmax= None
                len_max_yj = 0
                if g.graphique.type == "Histo" :
                    len_label_date_heure = 0
                else :
                    len_label_date_heure = 20
                if g.graphique.type == "Histo3D" :
                    coords = g.subplot.format_coord(event.xdata, event.ydata)
                    x = coords.split(',')[0].split('=')[1]
                for t in g.graphique.traces :
                    xj,yj = t.getData(x, y)
                    if yj is not None :
                        if len(str(yj)) > len_max_yj : # on stocke la longueur max pour calculer la largeur de la jauge
                            len_max_yj = len(str(yj))
                    if xj is not None :
                        if xmax is None or xj > xmax :
                            xmax = xj
                        is_jauge = True
                    couleur = t.getValue("couleur")
                    if yj is None :
                        yj = "--"
                    str_jauge_y = "{}<tr><td width=20 ><div style=\"border:1px solid black;width:10;height:10;background-color:{}\"/></td><td>{}</td></tr>".format(str_jauge_y,couleur, str(yj))
                str_jauge_x = "<tr><td colspan=2><b>{}</td></b></tr>".format(xmax)
                if  not is_jauge :
                    str_jauge = None
                else :
                    str_jauge += str_jauge_x + str_jauge_y
            except :
                pass
            finally:
                height = 50+(len(g.graphique.traces)*25)
                if str_jauge != None :
                    str_jauge += "</table></center></body>"
                if len_max_yj < len_label_date_heure :
                    len_max_yj = len_label_date_heure # taille label date heure (-3)
                width = (len_max_yj+3)*11 # +3 pour le carré de couleur
                return str_jauge, width, height
                
    def addCallbacks(self) :
        """
            Connecte les widgets à leur callback
        """
        # Document
        self.wTree.get_object("checkbuttonPdf").connect("toggled",self.onFormatToggled)
        self.wTree.get_object("checkbuttonPs").connect("toggled",self.onFormatToggled)
        self.wTree.get_object("checkbuttonPng").connect("toggled",self.onFormatToggled)
        self.wTree.get_object("filechooserbuttonRepertoire").connect("selection-changed",self.onRepertoireChanged)
        self.wTree.get_object("entryNomFichier").connect("changed",self.onNomFichierChanged)
        
        # Page
        self.wTree.get_object("entryTitrePage").connect("changed",self.onTitreChanged)
        self.wTree.get_object("radiobuttonPortrait").connect("toggled",self.onOrientationToggled)
        self.wTree.get_object("radiobuttonLandscape").connect("toggled",self.onOrientationToggled)
        self.wTree.get_object("buttonAgencement").connect("button-press-event",self.onButtonAgencementPressed)
        self.wTree.get_object("comboboxLogo").connect("changed",self.onLogoChanged)
        self.wTree.get_object("comboboxPositionLogo").connect("changed",self.onPositionLogoChanged)
        self.wTree.get_object("fontbuttonTitrePage").connect("font-set",self.onPoliceChanged)
        
        
        
        # Graphique
        self.wTree.get_object("entryTitreGraph").connect("changed",self.onTitreChanged)
        self.wTree.get_object("fontbuttonTitreGraphique").connect("font-set",self.onPoliceChanged)
        self.wTree.get_object("entryTitreGraphHisto3D").connect("changed",self.onTitreChanged)
        self.wTree.get_object("fontbuttonTitreGraphHisto3D").connect("font-set",self.onPoliceChanged)
        self.wTree.get_object("entryTitreGraphRDV").connect("changed",self.onTitreChanged)
        self.wTree.get_object("fontbuttonTitreGraphRDV").connect("font-set",self.onPoliceChanged)
        self.wTree.get_object("entryTitreGraphHov").connect("changed",self.onTitreChanged)
        self.wTree.get_object("fontbuttonTitreGraphHov").connect("font-set",self.onPoliceChanged)     
        self.wTree.get_object("checkbuttonAuto").connect("toggled",self.onAutoToggled, 'g')
        self.wTree.get_object("entryEchelleAmplitude").connect("changed",self.onAmplitudeChanged, 'g')
        self.wTree.get_object("entryEchelleMin").connect("changed",self.onEchelleMinChanged, 'g')
        self.wTree.get_object("entryEchelleMax").connect("changed",self.onEchelleMaxChanged, 'g')
        self.wTree.get_object("checkbuttonAutoDroite").connect("toggled",self.onAutoToggled,'d')
        self.wTree.get_object("entryEchelleAmplitudeDroite").connect("changed",self.onAmplitudeChanged, 'd')
        self.wTree.get_object("entryEchelleMinDroite").connect("changed",self.onEchelleMinChanged, 'd')
        self.wTree.get_object("entryEchelleMaxDroite").connect("changed",self.onEchelleMaxChanged, 'd')        
        self.wTree.get_object("checkbuttonAutoBas").connect("toggled",self.onAutoToggled,'b')
        self.wTree.get_object("entryEchelleAmplitudeBas").connect("changed",self.onAmplitudeChanged, 'b')
        self.wTree.get_object("entryEchelleMinBas").connect("changed",self.onEchelleMinChanged, 'b')
        self.wTree.get_object("entryEchelleMaxBas").connect("changed",self.onEchelleMaxChanged, 'b')
        
        self.wTree.get_object("entryEchelleAmplitudeDroiteHov").connect("changed",self.onAmplitudeHovChanged, 'd')
        self.wTree.get_object("checkbuttonAutoHov").connect("toggled",self.onAutoHovToggled, 'g')
        self.wTree.get_object("checkbuttonAutoDroiteHov").connect("toggled",self.onAutoHovToggled,'d')
        self.wTree.get_object("entryEchelleMinDroiteHov").connect("changed",self.onEchelleMinChanged, 'd')
        self.wTree.get_object("entryEchelleMaxDroiteHov").connect("changed",self.onEchelleMaxChanged, 'd')
        self.wTree.get_object("checkbuttonEchelleLogGaucheHov").connect("toggled",self.onEchelleLogGaucheToggled)
        self.wTree.get_object("checkbuttonEchelleLogDroiteHov").connect("toggled",self.onEchelleLogDroiteToggled)
        self.wTree.get_object("checkbuttonUniteDroiteHov").connect("toggled",self.onUniteDroiteToggled)
        self.wTree.get_object("checkbuttonLabelsDroiteHov").connect("toggled",self.onLabelsDroiteToggled)


        self.wTree.get_object("entryEchelleMinHov").connect("changed",self.onEchelleMinChanged, 'g')
        self.wTree.get_object("entryEchelleMaxHov").connect("changed",self.onEchelleMaxChanged, 'g')        
        self.wTree.get_object("checkbuttonUniteGauche").connect("toggled",self.onUniteGaucheToggled)
        self.wTree.get_object("checkbuttonUniteDroite").connect("toggled",self.onUniteDroiteToggled)
        self.wTree.get_object("checkbuttonUniteBas").connect("toggled",self.onUniteBasToggled)
        self.wTree.get_object("checkbuttonLabelsGauche").connect("toggled",self.onLabelsGaucheToggled)
        self.wTree.get_object("comboboxLabelsGaucheHov").connect("changed",self.onLabelsGaucheHovChanged)
        self.wTree.get_object("checkbuttonEchelleLogGauche").connect("toggled",self.onEchelleLogGaucheToggled)
        self.wTree.get_object("checkbuttonEchelleLogDroite").connect("toggled",self.onEchelleLogDroiteToggled)
        self.wTree.get_object("checkbuttonEchelleLogBas").connect("toggled",self.onEchelleLogBasToggled)       
        self.wTree.get_object("checkbuttonLabelsDroite").connect("toggled",self.onLabelsDroiteToggled)
        self.wTree.get_object("checkbuttonLabelsBas").connect("toggled",self.onLabelsBasToggled)
        self.wTree.get_object("checkbuttonLegendeAida").connect("toggled",self.onLegendeAidaToggled)
        self.wTree.get_object("checkbuttonGrille").connect("toggled",self.onGrilleToggled)
        self.wTree.get_object("checkbuttonFitData").connect("toggled",self.onFitDataToggled)
        self.wTree.get_object("checkbuttonLegendeAida3D").connect("toggled",self.onLegendeAidaToggled)
        self.wTree.get_object("checkbuttonLegendeAidaRDV").connect("toggled",self.onLegendeAidaToggled)
        self.wTree.get_object("checkbuttonLegendeAidaHov").connect("toggled",self.onLegendeAidaToggled)
        self.wTree.get_object("checkbuttonGrilleHov").connect("toggled",self.onGrilleToggled)
        self.wTree.get_object("checkbuttonLegendeST").connect("toggled",self.onLegendeToggled)
        self.wTree.get_object("buttonLegendeST").connect("clicked",self.onLegendeClicked)
        
        self.wTree.get_object("checkbuttonLegendeHov").connect("toggled",self.onLegendeToggled)
        self.wTree.get_object("buttonLegendeHov").connect("clicked",self.onLegendeClicked)
        
        self.wTree.get_object("checkbuttonLegendeHisto3D").connect("toggled",self.onLegendeToggled)
        self.wTree.get_object("buttonLegendeHisto3D").connect("clicked",self.onLegendeClicked)
        self.wTree.get_object("fontbuttonLegende").connect("font-set",self.onPoliceLegendeChanged)
        self.wTree.get_object("comboboxPositionLegende").connect("changed",self.onPositionLegendeChanged)
        self.wTree.get_object("spinbuttonDecalageLegendeHorizontal").connect("value-changed",self.onPositionLegendeChanged)
        self.wTree.get_object("spinbuttonDecalageLegendeVertical").connect("value-changed",self.onPositionLegendeChanged)        
        self.wTree.get_object("spinbuttonNbColLegende").connect("value-changed",self.onNbColLegendeChanged)        
        self.wTree.get_object("buttonAnnulerLegende").connect("clicked",self.onAnnulerLegende)
        self.wTree.get_object("buttonValiderLegende").connect("clicked",self.onValiderLegende)
        self.wTree.get_object("checkbuttonPourcentage").connect("toggled",self.onPourcentageToggled)
        self.wTree.get_object("checkbuttonPourcentageHisto3D").connect("toggled",self.onPourcentageToggled)                 
        self.wTree.get_object("checkbuttonJourNuit").connect("toggled",self.onJourNuitToggled)
        self.wTree.get_object("checkbuttonMoisAnnees").connect("toggled",self.onMoisAnneesToggled)   
        self.wTree.get_object("checkbuttonRegression").connect("toggled",self.onRegressionToggled)    
        self.wTree.get_object("checkbuttonXY").connect("toggled",self.onXegaleYToggled)
        self.wTree.get_object("checkbuttonYN").connect("toggled",self.onYegaleNToggled)
        self.wTree.get_object("entryYN").connect("changed",self.onYNChanged)
        self.wTree.get_object("checkbuttonGroupeLiaison").connect("toggled",self.onGroupeLiaisonToggled)
        self.wTree.get_object("spinbuttonGroupeLiaison").connect("value-changed",self.onGroupeLiaisonChanged)
        self.wTree.get_object("checkbuttonGroupeLiaisonRDV").connect("toggled",self.onGroupeLiaisonRDVToggled)
        self.wTree.get_object("spinbuttonGroupeLiaisonRDV").connect("value-changed",self.onGroupeLiaisonRDVChanged)
        self.wTree.get_object("checkbuttonGroupeLiaisonHisto3D").connect("toggled",self.onGroupeLiaisonHisto3DToggled)
        self.wTree.get_object("spinbuttonGroupeLiaisonHisto3D").connect("value-changed",self.onGroupeLiaisonHisto3DChanged)
        self.wTree.get_object("comboboxSecteursRDV").connect("changed",self.onSecteursRDVChanged)
        self.wTree.get_object("comboboxTypeRDV").connect("changed",self.onTypeRDVChanged)
        self.wTree.get_object("comboboxCouleurRDV").connect("changed",self.onCouleurRDVChanged)
        self.wTree.get_object("checkbuttonPaletteRDVReverse").connect("toggled",self.onPaletteRDVReverseToggled)
        self.wTree.get_object("checkbuttonDecoupageActiver").connect("toggled",self.onDecoupageActiverToggled)       
        self.wTree.get_object("spinbuttonDecoupageNombreJours").connect("changed",self.onDecoupageNombreJoursChanged)        
        self.wTree.get_object("comboboxDecoupageCouleur").connect("changed",self.onCouleurDecoupageChanged)
        self.wTree.get_object("checkbuttonDecoupagePaletteReverse").connect("toggled",self.onPaletteDecoupageReverseToggled)
        self.wTree.get_object("radiobuttonDecoupageJour").connect("toggled",self.onRadiobuttonDecoupageToggled, 'j')
        self.wTree.get_object("radiobuttonDecoupageMois").connect("toggled",self.onRadiobuttonDecoupageToggled, 'm')
        self.wTree.get_object("radiobuttonDecoupageAn").connect("toggled",self.onRadiobuttonDecoupageToggled, 'a')
        self.wTree.get_object("checkbuttonInverseAxeYHov").connect("toggled",self.onInverseAxeYHovToggled)

        # Trace                                         
        self.vue.getChildByName(self.window, "comboboxentryPlateforme").connect("changed",self.onPlateformeChanged, "comboboxParametre", "plateforme", "parametre")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_x").connect("changed",self.onPlateformeChanged,"comboboxParametre_x", "plateforme_x", "parametre_x")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_y").connect("changed",self.onPlateformeChanged,"comboboxParametre_y", "plateforme", "parametre")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_h").connect("changed",self.onPlateformeChanged,"comboboxParametre_h", "plateforme", "parametre")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_rdv").connect("changed",self.onPlateformeChanged,"comboboxParametre_dd", "plateforme", "parametre_x")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_rdv").connect("changed",self.onPlateformeChanged,"comboboxParametre_ff", "plateforme", "parametre")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov").connect("changed",self.onPlateformeChanged, "comboboxParametre_hov", "plateforme", "parametre")     
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver").connect("changed",self.onPlateformeChanged,"comboboxParametre_hov_quiver_dd", "plateformeQuiverHov", "parametre_dd_hov")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver").connect("changed",self.onPlateformeChanged,"comboboxParametre_hov_quiver_ff", "plateformeQuiverHov", "parametre_ff_hov")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver").connect("changed",self.onPlateformeChanged,"comboboxParametre_hov_quiver_u", "plateformeQuiverHov", "parametre_u_hov")
        self.vue.getChildByName(self.window, "comboboxentryPlateforme_hov_quiver").connect("changed",self.onPlateformeChanged,"comboboxParametre_hov_quiver_v", "plateformeQuiverHov", "parametre_v_hov")        
            
        self.vue.getChildByName(self.windowOperation, "comboboxentryPlateforme_operation").connect("changed",self.onPlateformeChanged,"comboboxOperationParametre", None, None, False)
        self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableCondition"), "comboboxentryPlateforme_cond").connect("changed",self.onPlateformeChanged,"comboboxAffichageConditionnelParametre", None, None, False)
            
        self.wTree.get_object("comboboxParametre").connect("changed",self.onParametreChanged, "parametre")
        self.wTree.get_object("comboboxParametre_x").connect("changed",self.onParametreChanged, "parametre_x")
        self.wTree.get_object("comboboxParametre_y").connect("changed",self.onParametreChanged,"parametre")
        self.wTree.get_object("comboboxParametre_h").connect("changed",self.onParametreChanged,"parametre")
        self.wTree.get_object("comboboxParametre_dd").connect("changed",self.onParametreChanged,"parametre_x")
        self.wTree.get_object("comboboxParametre_ff").connect("changed",self.onParametreChanged,"parametre")
        self.wTree.get_object("comboboxParametre_hov").connect("changed",self.onParametreChanged,"parametre")
        self.wTree.get_object("comboboxParametre_hov_quiver_dd").connect("changed",self.onParametreChanged,"parametre_dd_hov")
        self.wTree.get_object("comboboxParametre_hov_quiver_ff").connect("changed",self.onParametreChanged,"parametre_ff_hov")
        self.wTree.get_object("comboboxParametre_hov_quiver_u").connect("changed",self.onParametreChanged,"parametre_u_hov")
        self.wTree.get_object("comboboxParametre_hov_quiver_v").connect("changed",self.onParametreChanged,"parametre_v_hov")
        
        # callbacks sur les entry des combobox de paramètres : on déroule le combo parent
        self.wTree.get_object("comboboxParametre").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre"))
        self.wTree.get_object("comboboxParametre_x").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_x"))
        self.wTree.get_object("comboboxParametre_y").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_y"))
        self.wTree.get_object("comboboxParametre_h").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_h"))
        self.wTree.get_object("comboboxParametre_dd").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_dd"))
        self.wTree.get_object("comboboxParametre_ff").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_ff"))
        self.wTree.get_object("comboboxParametre_hov").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_hov"))
        self.wTree.get_object("comboboxParametre_hov_quiver_dd").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_hov_quiver_dd"))
        self.wTree.get_object("comboboxParametre_hov_quiver_ff").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_hov_quiver_ff"))
        self.wTree.get_object("comboboxParametre_hov_quiver_u").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_hov_quiver_u"))
        self.wTree.get_object("comboboxParametre_hov_quiver_v").get_child().connect("button-press-event",self.onParametrePressed, self.wTree.get_object("comboboxParametre_hov_quiver_v"))
        
        combo = self.vue.getChildByName(self.windowOperation, "comboboxOperationParametre")
        combo.get_child().connect("button-press-event",self.onParametrePressed,combo)
        combo = self.vue.getChildByName(self.wTree.get_object("dialogEditerVariableCondition"), "comboboxAffichageConditionnelParametre")
        combo.get_child().connect("button-press-event",self.onParametrePressed,combo)

        self.vue.getChildByName(self.window,"mycolorbuttonTraceST").connect("button-press-event",self.onMyColorbuttonClicked, None, None)
        self.wTree.get_object("radiobuttonPlein").connect("toggled",self.onTypeLigneToggled)
        self.wTree.get_object("radiobuttonPointille").connect("toggled",self.onTypeLigneToggled)
        self.wTree.get_object("radiobuttonTirete").connect("toggled",self.onTypeLigneToggled)
        self.wTree.get_object("radiobuttonAucunTrait").connect("toggled",self.onTypeLigneToggled)
        self.wTree.get_object("spinbuttonEpaisseur").connect("value-changed",self.onEpaisseurChanged)
        self.wTree.get_object("radiobuttonMarqueurAucun").connect("toggled",self.onMarqueurToggled)
        self.wTree.get_object("radiobuttonMarqueurCroix").connect("toggled",self.onMarqueurToggled)
        self.wTree.get_object("radiobuttonMarqueurRond").connect("toggled",self.onMarqueurToggled)
        self.wTree.get_object("radiobuttonMarqueurCarre").connect("toggled",self.onMarqueurToggled)
        self.wTree.get_object("radiobuttonMarqueurPoint").connect("toggled",self.onMarqueurToggled)
        self.wTree.get_object("radiobuttonMarqueurTriangle").connect("toggled",self.onMarqueurToggled)
        self.wTree.get_object("buttonAffichageConditionnel").connect("clicked",self.onAffichageConditionnelClicked)
        self.wTree.get_object("buttonAffichageConditionnelHisto").connect("clicked",self.onAffichageConditionnelClicked)
        self.wTree.get_object("buttonAffichageConditionnelPlotXY").connect("clicked",self.onAffichageConditionnelClicked)
        self.wTree.get_object("checkbuttonFiltrageConditionnel").connect("toggled",self.onFiltrageConditionnelToggled)
        self.wTree.get_object("buttonValiderAffichageConditionnel").connect("clicked",self.onValiderAffichageConditionnelClicked)
        self.wTree.get_object("buttonAnnulerAffichageConditionnel").connect("clicked",self.onAnnulerAffichageConditionnelClicked)
        self.wTree.get_object("buttonAddVariableCondition").connect("clicked",self.onAddVariableConditionClicked)
        self.wTree.get_object("buttonAddCondition").connect("clicked",self.onAddConditionClicked)
        self.wTree.get_object("radiobuttonCumulAucun").connect("toggled",self.onCumulToggled, 0)
        self.wTree.get_object("radiobuttonCumulSansRaz").connect("toggled",self.onCumulToggled, 1)
        self.wTree.get_object("radiobuttonCumulAvecRaz").connect("toggled",self.onCumulToggled, 2)
        
        self.wTree.get_object("radiobuttonAxeYGaucheST").connect("toggled",self.onAxeYToggled, 0)
        self.wTree.get_object("radiobuttonAxeYAutoST").connect("toggled",self.onAxeYToggled, 2)
        self.wTree.get_object("radiobuttonAxeYDroitST").connect("toggled",self.onAxeYToggled, 1)
        self.wTree.get_object("radiobuttonAxeYGauchePlotXY").connect("toggled",self.onAxeYToggled, 0)
        self.wTree.get_object("radiobuttonAxeYAutoPlotXY").connect("toggled",self.onAxeYToggled, 2)
        self.wTree.get_object("radiobuttonAxeYDroitPlotXY").connect("toggled",self.onAxeYToggled, 1)
        
        self.vue.getChildByName(self.window,"mycolorbuttonTracePlotXY").connect("button-press-event",self.onMyColorbuttonClicked, None, None)
        self.wTree.get_object("radiobuttonPleinPlotXY").connect("toggled",self.onTypeLigneToggled,"PlotXY")
        self.wTree.get_object("radiobuttonPointillePlotXY").connect("toggled",self.onTypeLigneToggled,"PlotXY")
        self.wTree.get_object("radiobuttonTiretePlotXY").connect("toggled",self.onTypeLigneToggled,"PlotXY")
        self.wTree.get_object("radiobuttonAucunTraitPlotXY").connect("toggled",self.onTypeLigneToggled,"PlotXY")
        self.wTree.get_object("spinbuttonEpaisseurPlotXY").connect("value-changed",self.onEpaisseurChanged)
        self.wTree.get_object("radiobuttonMarqueurAucunPlotXY").connect("toggled",self.onMarqueurToggled,"PlotXY")
        self.wTree.get_object("radiobuttonMarqueurCroixPlotXY").connect("toggled",self.onMarqueurToggled,"PlotXY")
        self.wTree.get_object("radiobuttonMarqueurRondPlotXY").connect("toggled",self.onMarqueurToggled,"PlotXY")
        self.wTree.get_object("radiobuttonMarqueurCarrePlotXY").connect("toggled",self.onMarqueurToggled,"PlotXY")
        self.wTree.get_object("radiobuttonMarqueurPointPlotXY").connect("toggled",self.onMarqueurToggled,"PlotXY")
        self.wTree.get_object("radiobuttonMarqueurTrianglePlotXY").connect("toggled",self.onMarqueurToggled,"PlotXY")
        self.vue.getChildByName(self.window,"mycolorbuttonTraceHisto").connect("button-press-event",self.onMyColorbuttonClicked, None, None)
        self.wTree.get_object("radiobuttonNombreClassesHisto").connect("toggled",self.onNombreClassesHistoToggled)
        self.wTree.get_object("radiobuttonAmplitudeClassesHisto").connect("toggled",self.onAmplitudeClassesHistoToggled)
        self.wTree.get_object("spinbuttonNombreClassesHisto").connect("value-changed",self.onNombreClassesHistoChanged)
        self.wTree.get_object("entryAmplitudeClassesHisto").connect("changed",self.onAmplitudeClassesHistoChanged)
        self.wTree.get_object("checkbuttonMinHisto").connect("toggled",self.onMinHistoToggled)
        self.wTree.get_object("checkbuttonMaxHisto").connect("toggled",self.onMaxHistoToggled)
        self.wTree.get_object("entryMinHisto").connect("changed",self.onMinHistoChanged)
        self.wTree.get_object("entryMaxHisto").connect("changed",self.onMaxHistoChanged)
        self.wTree.get_object("checkbuttonInfHisto").connect("toggled",self.onInfHistoToggled)
        self.wTree.get_object("checkbuttonSupHisto").connect("toggled",self.onSupHistoToggled)
        self.wTree.get_object("checkbuttonLabelNombreHisto").connect("toggled",self.onLabelNombreHistoToggled)
        self.wTree.get_object("checkbuttonLabelPourcentHisto").connect("toggled",self.onLabelPourcentHistoToggled)
        self.wTree.get_object("radiobuttonNombreClassesHisto3D").connect("toggled",self.onNombreClassesHistoToggled, "Histo3D")
        self.wTree.get_object("radiobuttonAmplitudeClassesHisto3D").connect("toggled",self.onAmplitudeClassesHistoToggled, "Histo3D")
        self.wTree.get_object("spinbuttonNombreClassesHisto3D").connect("value-changed",self.onNombreClassesHistoChanged)
        self.wTree.get_object("entryAmplitudeClassesHisto3D").connect("changed",self.onAmplitudeClassesHistoChanged)
        self.wTree.get_object("checkbuttonMinHisto3D").connect("toggled",self.onMinHistoToggled, "Histo3D")
        self.wTree.get_object("checkbuttonMaxHisto3D").connect("toggled",self.onMaxHistoToggled, "Histo3D")
        self.wTree.get_object("entryMinHisto3D").connect("changed",self.onMinHistoChanged)
        self.wTree.get_object("entryMaxHisto3D").connect("changed",self.onMaxHistoChanged)
        self.wTree.get_object("checkbuttonInfHisto3D").connect("toggled",self.onInfHistoToggled)
        self.wTree.get_object("checkbuttonSupHisto3D").connect("toggled",self.onSupHistoToggled)
        self.wTree.get_object("spinbuttonEpaisseurHisto3D").connect("value-changed",self.onEpaisseurHisto3DChanged)
        self.wTree.get_object("spinbuttonLargeurHisto3D").connect("value-changed",self.onLargeurHisto3DChanged)
        
        self.wTree.get_object("radiobuttonRoseStandard").connect("toggled",self.onRoseStandardToggled)
        self.wTree.get_object("radiobuttonNombreClassesRDV").connect("toggled",self.onNombreClassesHistoToggled, "RDV")
        self.wTree.get_object("radiobuttonAmplitudeClassesRDV").connect("toggled",self.onAmplitudeClassesHistoToggled, "RDV")
        self.wTree.get_object("spinbuttonNombreClassesRDV").connect("value-changed",self.onNombreClassesHistoChanged)
        self.wTree.get_object("entryAmplitudeClassesRDV").connect("changed",self.onAmplitudeClassesHistoChanged)
        self.wTree.get_object("checkbuttonMinRDV").connect("toggled",self.onMinHistoToggled, "RDV")
        self.wTree.get_object("checkbuttonMaxRDV").connect("toggled",self.onMaxHistoToggled, "RDV")
        self.wTree.get_object("entryMinRDV").connect("changed",self.onMinHistoChanged)
        self.wTree.get_object("entryMaxRDV").connect("changed",self.onMaxHistoChanged)
        self.wTree.get_object("checkbuttonInfRDV").connect("toggled",self.onInfHistoToggled)
        self.wTree.get_object("checkbuttonSupRDV").connect("toggled",self.onSupHistoToggled)
        
        self.wTree.get_object("comboboxCouleurHov").connect("changed",self.onCouleurHovChanged)
        self.wTree.get_object("checkbuttonPaletteHovReverse").connect("toggled",self.onPaletteHovReverseToggled)

        self.wTree.get_object("radiobuttonHovDiscret").connect("toggled",self.onTypeHovToggled)
        self.wTree.get_object("radiobuttonHovInter").connect("toggled",self.onTypeHovToggled)
        self.wTree.get_object("checkbuttonHovAuto").connect("toggled",self.onTypeHovToggled)
        self.wTree.get_object("checkbuttonHovShading").connect("toggled",self.onTypeHovToggled)
        self.wTree.get_object("checkbuttonHovIsolignes").connect("toggled",self.onTypeHovToggled)
        self.wTree.get_object("spinbuttonLargeurHov").connect("value-changed",self.onLargeurHovChanged)
        self.wTree.get_object("checkbuttonHovSeuilAuto").connect("toggled",self.onSeuilAutoHovToggled)
        self.wTree.get_object("entryHovSeuilMin").connect("changed",self.onSeuilMinHovChanged)
        self.wTree.get_object("entryHovSeuilMax").connect("changed",self.onSeuilMaxHovChanged)
        self.wTree.get_object("checkbuttonHovHorsGammeVisible").connect("toggled",self.onHovHorsGammeVisibleToggled)
        self.wTree.get_object("checkbuttonHovQuiver").connect("toggled",self.onQuiverToggled)
        self.wTree.get_object("radiobuttonHovQuiverDdFf").connect("toggled",self.onHovModeQuiverToggled)
        self.wTree.get_object("radiobuttonHovQuiverUV").connect("toggled",self.onHovModeQuiverToggled)
        self.wTree.get_object("comboboxHovQuiverEchantillonX").connect("changed",self.onHovQuiverEchantillonXChanged)
        self.wTree.get_object("comboboxHovQuiverEchantillonY").connect("changed",self.onHovQuiverEchantillonYChanged)
        
        
        # Fenêtre            
        self.window.connect("delete_event", self.onDeleteWindow)
        
        # Menu
        self.wTree.get_object("itemQuitter").connect("activate",self.onQuitter)                               
        self.wTree.get_object("itemEnregistrer").connect("activate",self.onEnregistrer)
        self.wTree.get_object("itemEnregistrerSous").connect("activate",self.onEnregistrerSous)
        self.wTree.get_object("itemNouveau").connect("activate",self.onNouveau)
        self.wTree.get_object("itemOuvrir").connect("activate",self.onOuvrir)
        self.wTree.get_object("itemBarreOutil").connect("toggled",self.onItemBarreOutilToggled)
        self.wTree.get_object("itemConsole").connect("toggled",self.onItemConsoleToggled)
        self.wTree.get_object("itemAjouter").connect("activate",self.onAjouter, None)
        self.wTree.get_object("itemSupprimer").connect("activate",self.onSupprimer)
        self.wTree.get_object("itemVisualiser").connect("activate",self.onVisualiser)
        self.wTree.get_object("itemReload").connect("activate",self.onReload)
        self.wTree.get_object("itemExporterPdf").connect("activate",self.onExporterPdf)
        self.wTree.get_object("itemExporterPng").connect("activate",self.onExporterPng)
        self.wTree.get_object("itemExporterPs").connect("activate",self.onExporterPs)
        self.wTree.get_object("itemImprimer").connect("activate",self.onImprimer)
        self.wTree.get_object("itemZoom100").connect("activate",self.onZoomActivate,0)
        self.wTree.get_object("itemZoom110").connect("activate",self.onZoomActivate,1)
        self.wTree.get_object("itemZoom120").connect("activate",self.onZoomActivate,2)
        self.wTree.get_object("itemZoom130").connect("activate",self.onZoomActivate,3)
        self.wTree.get_object("itemZoom140").connect("activate",self.onZoomActivate,4)
        self.wTree.get_object("itemZoom150").connect("activate",self.onZoomActivate,5)
        self.wTree.get_object("itemZoom200").connect("activate",self.onZoomActivate,6)
        self.wTree.get_object("itemZoom400").connect("activate",self.onZoomActivate,7)
        self.wTree.get_object("itemAideAPropos").connect("activate",self.onAideAProposActivate)
        self.wTree.get_object("itemAideManuel").connect("activate",self.onAideManuelActivate)
        self.wTree.get_object("itemUpdateListeVecteurs").connect("activate",self.onUpdateListeVecteursActivate)
        self.wTree.get_object("itemAcqidToDate").connect("activate",self.onAcqidToDateActivate)
        
        #toolbar
        self.wTree.get_object("toolbuttonEnregistrer").connect("clicked",self.onEnregistrer)
        self.wTree.get_object("toolbuttonEnregistrerSous").connect("clicked",self.onEnregistrerSous)
        self.wTree.get_object("toolbuttonAjouter").connect("clicked",self.onAjouter, None)
        self.wTree.get_object("toolbuttonSupprimer").connect("clicked",self.onSupprimer)
        self.wTree.get_object("toolbuttonVisualiser").connect("clicked",self.onVisualiser)
        self.wTree.get_object("toolbuttonReload").connect("clicked",self.onReload)
        self.wTree.get_object("toolbuttonNouveau").connect("clicked",self.onNouveau)
        self.wTree.get_object("toolbuttonOuvrir").connect("clicked",self.onOuvrir)
        self.wTree.get_object("toolbuttonExportPdf").connect("clicked",self.onExporterPdf)
        self.wTree.get_object("toolbuttonExportPng").connect("clicked",self.onExporterPng)
        self.wTree.get_object("toolbuttonExportPs").connect("clicked",self.onExporterPs)
        self.wTree.get_object("toolbuttonImprimer").connect("clicked",self.onImprimer)
        self.wTree.get_object("comboboxZoom").connect("changed",self.onZoomChanged)
        
        #boutons de gestion de la console
        self.wTree.get_object("buttonOuvrirConsole").connect("clicked",self.onButtonOuvrirConsole)
        self.wTree.get_object("buttonInfoConsole").connect("clicked",self.onButtonOuvrirConsole)
        self.wTree.get_object("buttonFermerConsole").connect("clicked",self.onButtonFermerConsole)
        self.wTree.get_object("buttonViderConsole").connect("clicked",self.onButtonViderConsole)
              
        #periode

        self.wTree.get_object("radiobuttonMois").connect("toggled",self.onButtonPeriodeCLicked)
        self.wTree.get_object("buttonMois").connect("clicked",self.onButtonDateCLicked,0)
        self.wTree.get_object("buttonDebut").connect("clicked",self.onButtonDateCLicked,1)
        self.wTree.get_object("buttonFin").connect("clicked",self.onButtonDateCLicked,2)
        self.wTree.get_object("buttonCopierDateDebut").connect("clicked",self.onButtonCopierDateDebut)
        self.wTree.get_object("buttonCopierDateFin").connect("clicked",self.onButtonCopierDateFin)
        self.wTree.get_object("entryAcqidCalendar").connect("changed",self.onEntryAcqidCalendarChanged)
        
        # menu contextuel du treeview            
        self.handlerAjouter = self.wTree.get_object("menuitemTreeAjouter").connect("activate", self.onAjouter, None)
        self.wTree.get_object("menuitemTreeSupprimer").connect("activate", self.onSupprimer)
        self.handlerAjouterAvant =self.wTree.get_object("menuitemTreeAjouterAvant").connect("activate", self.onInserer, True, None)
        self.handlerAjouterApres = self.wTree.get_object("menuitemTreeAjouterApres").connect("activate", self.onInserer, False, None)
        # on stocke l'état bloqué ou non des handlers du menu contextuel
        self.vue.treeMenuContextHandlers[self.handlerAjouter] = False
        self.vue.treeMenuContextHandlers[self.handlerAjouterAvant] = False
        self.vue.treeMenuContextHandlers[self.handlerAjouterApres] = False
        self.wTree.get_object("menuTreeview").connect("hide",self.onMenuTreeview, None)
        self.wTree.get_object("menuTreeview").connect("map",self.onMenuTreeview, Gdk.color_parse("#C4C4C4"))  # @UndefinedVariable
        self.wTree.get_object("menuitemAjouterST").connect("activate", self.onAjouter, "ST")
        self.wTree.get_object("menuitemAjouterPlotXY").connect("activate", self.onAjouter, "PlotXY")
        self.wTree.get_object("menuitemAjouterHisto").connect("activate", self.onAjouter, "Histo")
        self.wTree.get_object("menuitemAjouterHisto3D").connect("activate", self.onAjouter, "Histo3D")
        self.wTree.get_object("menuitemAjouterRDV").connect("activate", self.onAjouter, "RDV")
        self.wTree.get_object("menuitemAjouterHov").connect("activate", self.onAjouter, "Hov")
        self.wTree.get_object("menuitemAjouterTraceHov").connect("activate", self.onAjouter, "Hov")
        self.wTree.get_object("menuitemAjouterTraceST").connect("activate", self.onAjouter, "ST")
        
        self.wTree.get_object("menuitemAjouterAvantST").connect("activate", self.onInserer, True, "ST")
        self.wTree.get_object("menuitemAjouterAvantPlotXY").connect("activate", self.onInserer, True, "PlotXY")
        self.wTree.get_object("menuitemAjouterAvantHisto").connect("activate", self.onInserer, True, "Histo")
        self.wTree.get_object("menuitemAjouterAvantHisto3D").connect("activate", self.onInserer, True, "Histo3D")
        self.wTree.get_object("menuitemAjouterAvantRDV").connect("activate", self.onInserer, True, "RDV")
        self.wTree.get_object("menuitemAjouterAvantHov").connect("activate", self.onInserer, True, "Hov")
        self.wTree.get_object("menuitemAjouterApresST").connect("activate", self.onInserer, False, "ST")
        self.wTree.get_object("menuitemAjouterApresPlotXY").connect("activate", self.onInserer, False, "PlotXY")
        self.wTree.get_object("menuitemAjouterApresHisto").connect("activate", self.onInserer, False, "Histo")
        self.wTree.get_object("menuitemAjouterApresHisto3D").connect("activate", self.onInserer, False, "Histo3D")
        self.wTree.get_object("menuitemAjouterApresRDV").connect("activate", self.onInserer, False, "RDV")
        self.wTree.get_object("menuitemAjouterApresHov").connect("activate", self.onInserer, False, "Hov")
        self.wTree.get_object("menuitemTreeCopier").connect("activate", self.onTreeviewCopier)
        self.wTree.get_object("menuitemTreeColler").connect("activate", self.onTreeviewColler)
        
        
        # treeview
        self.vue.treeview.connect("button-press-event",self.onTreeviewButtonPress)
        self.vue.treeview.connect("key-press-event",self.onTreeviewKeyPress)
        self.vue.treeview.connect("row-expanded",self.onTreeviewExpandCollapse)
        self.vue.treeview.connect("row-collapsed",self.onTreeviewExpandCollapse)
        # les 2 lignes suivantes permettent d'ajouter un evenement changed sur chaque sélection du treeview
        selection = self.vue.treeview.get_selection()
        selection.connect('changed', self.onTreeviewChanged)
        
        # vpanedVista : quand la console est masquée, on interdit le resize du vpanel. C'est géré par self.consoleLock
        self.wTree.get_object("vpanedVista").connect("button-press-event",self.onVpanedVistaButtonPress)

        # boutons d'appel de la calculette
        self.wTree.get_object("buttonCalculette1").connect("button-press-event",self.onButtonCalculettePressed, "y", "imageWarningCalculette1")
        self.wTree.get_object("buttonCalculette2").connect("button-press-event",self.onButtonCalculettePressed, "x", "imageWarningCalculette2")
        self.wTree.get_object("buttonCalculette3").connect("button-press-event",self.onButtonCalculettePressed, "y", "imageWarningCalculette3")
        self.wTree.get_object("buttonCalculette4").connect("button-press-event",self.onButtonCalculettePressed, "y", "imageWarningCalculette4")
        self.wTree.get_object("buttonCalculette5").connect("button-press-event",self.onButtonCalculettePressed, "x", "imageWarningCalculette5")
        self.wTree.get_object("buttonCalculette6").connect("button-press-event",self.onButtonCalculettePressed, "y", "imageWarningCalculette6")
        self.wTree.get_object("buttonCalculette7").connect("button-press-event",self.onButtonCalculettePressed, "y", "imageWarningCalculette7")

        # boutons de la boîte d'opération
        self.wTree.get_object("buttonAnnulerOperation").connect("button-press-event",self.onButtonAnnulerOperationPressed)
        self.wTree.get_object("buttonValiderOperation").connect("button-press-event",self.onButtonValiderOperationPressed)
        self.wTree.get_object("buttonAddVariableOperation").connect("clicked",self.onAddVariableOperationClicked)
        self.wTree.get_object("entryExpressionOperation").connect("changed",self.onEntryExpressionOperationChanged)
        
        # Outil Acqid -> date
        self.wTree.get_object("buttonAcqidToDate").connect("button-press-event",self.onButtonAcqidToDatePressed)
        self.wTree.get_object("entryAcqid").connect("changed",self.onEntryAcqidChanged)
        self.wTree.get_object("entryAcqid").connect("activate",self.onEntryAcqidActivate)
        
        # Fenêtre d'agencement des graphiques
        self.wTree.get_object("dialogAgencement").connect("map",self.onDialogAgencementMap) 
   
