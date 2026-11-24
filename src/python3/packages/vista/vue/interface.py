#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import gi
import matplotlib
# en mode batch, il faut pouvoir fonctionner sans DISPLAY d'ou ce qui suit :
if not os.environ.get('DISPLAY'):
    matplotlib.use('Agg')
else :
    matplotlib.use('GTK3Agg')
    gi.require_version('Gtk', '3.0') 
    from gi.repository import Gtk, GObject, Gdk # @UnresolvedImport
    from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
    from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3
    from matplotlib import pyplot as plt
    gi.require_version('WebKit2', '4.0')
    from gi.repository import WebKit2 as webkit # @UnresolvedImport
    from gi.repository.GdkPixbuf import Pixbuf # @UnresolvedImport
import collections
import configparser
#from math import * #@UnusedWildImport

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
PYTHON_LIB = os.path.join(AH, 'lib', PYTHON_X_Y)
sys.path.append(PYTHON_LIB)
if os.environ.get('DISPLAY'):
    from . import vistaagencement as va
from vista.vue import vistagraph as vg
from vista.modele import date as vd
from vista.modele import classes as vc

version="4.3.5"

    
class UiVista :
    """
        L'interface graphique vista
    """

    def __init__(self, document, console):
        self.document = document
        self.ctrl = None # controler
        self.plateformes = collections.defaultdict(dict)
        self.listeVecteurs = collections.defaultdict(dict)        
        self.treeMenuContextHandlers = {}
        self.handlerAjouter = None
        self.handlerAjouterAvant = None
        self.handlerAjouterApres = None
        self.secteursRDV = ["4", "8", "12", "16", "18", "24", "32", "36"]
        self.couleursRDV = ["afmhot.png", "autumn.png", "bone.png", "cool.png", "copper.png", "gist_heat.png", "gray.png", "hot.png", "pink.png", "spring.png", "summer.png", "winter.png","rainbow.png"]
        self.couleursHov = ["rainbow.png","afmhot.png", "autumn.png", "bone.png", "cool.png", "copper.png", "gist_heat.png", "gray.png", "hot.png", "pink.png", "spring.png", "summer.png", "winter.png"]
        self.couleursDecoupage = ["rainbow.png","afmhot.png", "autumn.png", "bone.png", "cool.png", "copper.png", "gist_heat.png", "gray.png", "hot.png", "pink.png", "spring.png", "summer.png", "winter.png"]
        self.dirIcons = os.getenv('AIDA_HOME')+"/share/vista/icons"
        #Fichier glade
        self.gladefile = "{}/vista/vue/vista.glade".format(PYTHON_LIB)  
        self.wTree = Gtk.Builder()
        self.wTree.add_from_file(self.gladefile)
        
        #Fenêtre principale
        self.window = self.wTree.get_object("rootWindow")
        if (self.window):
            self.window.set_title("Vista - {}".format(self.document.fichier))
            # taille de la fenêtre : on essaye de donner la "meilleure" taille définie empiriquement
            # par smart_width et smart_height. Si l'écran est trop petit on positionne width/height à 90%
            # de la taille de l'écran.
            smart_width = 1050
            smart_height = 870
            screen = self.window.get_screen()
            display = screen.get_display()
            monitor = display.get_monitor(0)
            geo = monitor.get_geometry()
            height = geo.height - 350
            width = 580
            hints = Gdk.Geometry()
            hints.min_height = 300
            hints.min_width = 300
            self.window.set_geometry_hints(None,hints, Gdk.WindowHints.MIN_SIZE)
            self.wTree.get_object("vpanedVista").set_size_request(width,height)
            # ligne suivante désactivée car perturbe le mode console (à supprimer si pas d'effets de bord)
            #self.wTree.get_object("scrolledwindowVista").set_size_request(0,height)
            self.window.set_icon_from_file("{}/vista.png".format(self.dirIcons))
            self.rootWindow = self.window.get_screen().get_root_window()
            if smart_width > (geo.width * 0.9) :
                smart_width = geo.width * 0.9
            if smart_height > (geo.height * 0.9) :
                smart_height = geo.height * 0.9
            self.window.set_default_size(smart_width, smart_height)
        else :
            print("Erreur : pas de rootwindow après construction de l'ihm")
            exit(1)
        self.windowOperation = self.wTree.get_object("dialogEditerVariableOperation")
        # Liste des plateformes
        self.readPlateformes()
        # Liste des vecteurs pour chaque plateforme
        self.readListeVecteurs()
        liststore = Gtk.ListStore(str)            
        for plateforme in sorted(list(self.plateformes.keys()), key=lambda s: s.lower()) :
            liststore.append([plateforme])
        self.liststore = liststore
        
        
        # plateformes pour ST
        completion = Gtk.EntryCompletion()
        completion.set_model(liststore)
        completion.set_text_column(0)
        comboboxentryPlateforme = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme, "comboboxentryPlateforme")
        comboboxentryPlateforme.set_model(liststore)
        comboboxentryPlateforme.set_entry_text_column(0)
        comboboxentryPlateforme.get_child().set_completion(completion)
        self.wTree.get_object("hboxPlateforme").pack_start(comboboxentryPlateforme, True, True, 0)
        # plateformes pour PlotXY
        completion_x = Gtk.EntryCompletion()
        completion_x.set_model(liststore)
        completion_x.set_text_column(0)
        comboboxentryPlateforme_x = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme_x, "comboboxentryPlateforme_x")
        comboboxentryPlateforme_x.set_model(liststore)
        comboboxentryPlateforme_x.set_entry_text_column(0)
        comboboxentryPlateforme_x.get_child().set_completion(completion_x)
        self.wTree.get_object("hboxPlateforme_x").pack_start(comboboxentryPlateforme_x, True, True, 0)
        completion_y = Gtk.EntryCompletion()
        completion_y.set_model(liststore)
        completion_y.set_text_column(0)
        comboboxentryPlateforme_y = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme_y, "comboboxentryPlateforme_y")
        comboboxentryPlateforme_y.set_model(liststore)
        comboboxentryPlateforme_y.set_entry_text_column(0)
        comboboxentryPlateforme_y.get_child().set_completion(completion_y)
        self.wTree.get_object("hboxPlateforme_y").pack_start(comboboxentryPlateforme_y, True, True, 0)
        # plateformes pour Histo
        completion_h = Gtk.EntryCompletion()
        completion_h.set_model(liststore)
        completion_h.set_text_column(0)
        comboboxentryPlateforme_h = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme_h, "comboboxentryPlateforme_h")
        comboboxentryPlateforme_h.set_model(liststore)
        comboboxentryPlateforme_h.set_entry_text_column(0)
        comboboxentryPlateforme_h.get_child().set_completion(completion_h)
        self.wTree.get_object("hboxPlateformeHisto").pack_start(comboboxentryPlateforme_h, True, True, 0)
        # plateformes pour RDV
        completion_x = Gtk.EntryCompletion()
        completion_x.set_model(liststore)
        completion_x.set_text_column(0)
        comboboxentryPlateforme_rdv = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme_rdv, "comboboxentryPlateforme_rdv")
        comboboxentryPlateforme_rdv.set_model(liststore)
        comboboxentryPlateforme_rdv.set_entry_text_column(0)
        comboboxentryPlateforme_rdv.get_child().set_completion(completion_x)
        self.wTree.get_object("hboxPlateformeRDV").pack_start(comboboxentryPlateforme_rdv, True, True, 0)
        # plateformes pour Hov
        completion_x = Gtk.EntryCompletion()
        completion_x.set_model(liststore)
        completion_x.set_text_column(0)
        comboboxentryPlateforme_hov = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme_hov, "comboboxentryPlateforme_hov")
        comboboxentryPlateforme_hov.set_model(liststore)
        comboboxentryPlateforme_hov.set_entry_text_column(0)
        comboboxentryPlateforme_hov.get_child().set_completion(completion_x)
        self.wTree.get_object("hboxPlateformeHov").pack_start(comboboxentryPlateforme_hov, True, True, 0)
        # plateformes pour operation
        completion_operation = Gtk.EntryCompletion()
        completion_operation.set_model(liststore)
        completion_operation.set_text_column(0)
        comboboxentryPlateforme_operation = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme_operation, "comboboxentryPlateforme_operation")
        comboboxentryPlateforme_operation.set_model(liststore)
        comboboxentryPlateforme_operation.set_entry_text_column(0)
        comboboxentryPlateforme_operation.get_child().set_completion(completion_operation)
        comboboxentryPlateforme_operation.set_can_focus(True)
        self.wTree.get_object("hboxOperationPlateforme").pack_start(comboboxentryPlateforme_operation, True, True, 0)
        # plateformes pour affichage conditionnel
        completion_cond = Gtk.EntryCompletion()
        completion_cond.set_model(liststore)
        completion_cond.set_text_column(0)
        comboboxentryPlateforme_cond = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme_cond, "comboboxentryPlateforme_cond")
        comboboxentryPlateforme_cond.set_model(liststore)
        comboboxentryPlateforme_cond.set_entry_text_column(0)
        comboboxentryPlateforme_cond.get_child().set_completion(completion_cond)
        comboboxentryPlateforme_cond.set_can_focus(True)
        self.wTree.get_object("hboxAffichageConditionnelPlateforme").pack_start(comboboxentryPlateforme_cond, True, True, 0)
        # plateformes pour quiver (Hovmoller)
        completion = Gtk.EntryCompletion()
        completion.set_model(liststore)
        completion.set_text_column(0)
        comboboxentryPlateforme_hov_quiver = Gtk.ComboBox(has_entry=True)
        Gtk.Buildable.set_name(comboboxentryPlateforme_hov_quiver, "comboboxentryPlateforme_hov_quiver")
        comboboxentryPlateforme_hov_quiver.set_model(liststore)
        comboboxentryPlateforme_hov_quiver.set_entry_text_column(0)
        comboboxentryPlateforme_hov_quiver.get_child().set_completion(completion)
        self.wTree.get_object("hboxPlateformeHovQuiver").pack_start(comboboxentryPlateforme_hov_quiver, True, True, 0)

        # Nombre de labels à afficher sur l'axe gauche de Hovmoller
        combo_labels_gauche_hov = self.wTree.get_object("comboboxLabelsGaucheHov")
        renderer_text = Gtk.CellRendererText()
        combo_labels_gauche_hov.pack_start(renderer_text, True)
        combo_labels_gauche_hov.add_attribute(renderer_text, "text", 0)
        store_labels_gauche_hov = Gtk.ListStore(str)
        store_labels_gauche_hov.append(["100%"])
        store_labels_gauche_hov.append(["75%"])
        store_labels_gauche_hov.append(["50%"])
        store_labels_gauche_hov.append(["25%"])
        store_labels_gauche_hov.append(["10%"])
        store_labels_gauche_hov.append(["Auto"])
        store_labels_gauche_hov.append(["Aucun"])
        combo_labels_gauche_hov.set_model(store_labels_gauche_hov)       
        combo_labels_gauche_hov.set_active(0)
                
        # Zoom
        combo_zoom = self.wTree.get_object("comboboxZoom")
        renderer_text = Gtk.CellRendererText()
        combo_zoom.pack_start(renderer_text, True)
        combo_zoom.add_attribute(renderer_text, "text", 0)
        store_zoom = Gtk.ListStore(str)
        store_zoom.append(["100%"])
        store_zoom.append(["110%"])
        store_zoom.append(["120%"])
        store_zoom.append(["130%"])
        store_zoom.append(["140%"])
        store_zoom.append(["150%"])
        store_zoom.append(["200%"])
        store_zoom.append(["400%"])
        combo_zoom.set_model(store_zoom)       
        combo_zoom.set_active(0)
        
        # Dates
        self.wTree.get_object("labelMois").set_label(vd.toString(self.document.dateMois, 'mm AAAA'))
        self.wTree.get_object("labelDebut").set_label("du {}".format(vd.toString(self.document.dateDebut, 'JJ/MM/AAAA')))
        self.wTree.get_object("labelFin").set_label("au {}".format(vd.toString(self.document.dateFin, 'JJ/MM/AAAA')))
        
        #Création du treeview    
        self.createDocTree()

        #Liste des logos png(sous share/common/logos)
        listeLogos = self.document.logoList
        liststore = Gtk.ListStore(str)
        liststore.append(["Pas de logo"])
        for i in listeLogos :
            liststore.append([i])
        comboboxLogo = self.wTree.get_object("comboboxLogo")
        comboboxLogo.set_model(liststore)
        renderer_text = Gtk.CellRendererText()
        comboboxLogo.pack_start(renderer_text, True)
        comboboxLogo.add_attribute(renderer_text, "text", 0)
        
        #Position du logo
        liststore = Gtk.ListStore(str, str)
        liststore.append(["haut gauche", "hg"])
        liststore.append(["haut droite", "hd"])
        liststore.append(["bas gauche", "bg"])
        liststore.append(["bas droite", "bd"])
        comboboxPositionLogo = self.wTree.get_object("comboboxPositionLogo")
        comboboxPositionLogo.set_model(liststore)
        renderer_text = Gtk.CellRendererText()
        comboboxPositionLogo.pack_start(renderer_text, True)
        comboboxPositionLogo.add_attribute(renderer_text, "text", 0)
        
        # Position  de la légende (position_ancrage, x_ancrage, y_ancrage, dx, dy)
        liststore = Gtk.ListStore(str, int, float, float)
        liststore.append(["auto", 0, 0, 0])
        liststore.append(["haut droite", 1, 1, 1])
        liststore.append(["haut gauche", 2, 0, 1])
        liststore.append(["bas gauche", 3, 0, 0])
        liststore.append(["bas droite", 4, 1, 0])
        #liststore.append(["droite", 5]) #fait doublon avec 7?
        liststore.append(["centré à gauche", 6, 0, 0.5])
        liststore.append(["centré à droite", 7, 1, 0.5])
        liststore.append(["centré en bas", 8, 0.5, 0])
        liststore.append(["centré en haut", 9, 0.5, 1])
        liststore.append(["centré", 10, 0.5, 0.5])     
        comboboxPositionLegende = self.wTree.get_object("comboboxPositionLegende")
        comboboxPositionLegende.set_model(liststore)
        renderer_text = Gtk.CellRendererText()
        comboboxPositionLegende.pack_start(renderer_text, True)
        comboboxPositionLegende.add_attribute(renderer_text, "text", 0)
        
        #Position du séparateur du vpaned du treeview        
        self.wTree.get_object("vpanedTreeview").set_position(200)
        
        #Fenêtre d'agencement des graphiques dans la page
        buttonAlignGrille = self.wTree.get_object("buttonAlignGrille")
        image = Gtk.Image()
        pb = Pixbuf.new_from_file(self.dirIcons+"/grille.png")
        image.set_from_pixbuf(pb)
        buttonAlignGrille.set_image(image)
        buttonAlignLeft = self.wTree.get_object("buttonAlignLeft")
        image = Gtk.Image()
        pb = Pixbuf.new_from_file(self.dirIcons+"/leftjust.png")
        image.set_from_pixbuf(pb)
        buttonAlignLeft.set_image(image)       
        buttonAlignRight = self.wTree.get_object("buttonAlignRight")
        image = Gtk.Image()
        pb = Pixbuf.new_from_file(self.dirIcons+"/rightjust.png")
        image.set_from_pixbuf(pb)
        buttonAlignRight.set_image(image)
        buttonAlignTop = self.wTree.get_object("buttonAlignTop")
        image = Gtk.Image()
        pb = Pixbuf.new_from_file(self.dirIcons+"/topjust.png")
        image.set_from_pixbuf(pb)
        buttonAlignTop.set_image(image)
        buttonAlignBottom = self.wTree.get_object("buttonAlignBottom")
        image = Gtk.Image()
        pb = Pixbuf.new_from_file(self.dirIcons+"/bottomjust.png")
        image.set_from_pixbuf(pb)
        buttonAlignBottom.set_image(image)
        buttonSameWidth = self.wTree.get_object("buttonSameWidth")
        image = Gtk.Image()
        pb = Pixbuf.new_from_file(self.dirIcons+"/samewidth.png")
        image.set_from_pixbuf(pb)
        buttonSameWidth.set_image(image)
        buttonSameHeight = self.wTree.get_object("buttonSameHeight")
        image = Gtk.Image()
        pb = Pixbuf.new_from_file(self.dirIcons+"/sameheight.png")
        image.set_from_pixbuf(pb)
        buttonSameHeight.set_image(image)
        #self.figAgencement = plt.figure("agencement")
        self.figAgencement = plt.figure(-1)
        self.figAgencement.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        self.axAgencement = self.figAgencement.add_subplot(111)
        controller = va.ControlRectangles(self.figAgencement)
        va.ControlRectangles.labelTitre = self.wTree.get_object("labelTitreGraphiqueAgencement")
        for tl in self.axAgencement.get_xticklabels() + self.axAgencement.get_yticklabels():
            tl.set_visible(False)
        self.axAgencement.xaxis.grid(True, zorder=100)
        self.axAgencement.yaxis.grid(True, zorder=100)
        self.axAgencement.set_xlim(0,100)
        self.axAgencement.set_ylim(0,100)
        self.axAgencement.set_xticks(list(range(0,100,5)))
        self.axAgencement.set_yticks(list(range(0,100,5)))       
        canvasAgencement = FigureCanvas(self.figAgencement)  # a Gtk.DrawingArea
        controller.connect()
        frameAgencement = self.wTree.get_object("frameVistaAgencement")
        frameAgencement.add(canvasAgencement)
        
        self.wTree.get_object("buttonAlignGrille").connect('button-press-event', controller.alignGrille, self.wTree)
        self.wTree.get_object("buttonAlignLeft").connect('button-press-event', controller.alignLeft)
        self.wTree.get_object("buttonAlignRight").connect('button-press-event', controller.alignRight)
        self.wTree.get_object("buttonAlignTop").connect('button-press-event', controller.alignTop)
        self.wTree.get_object("buttonAlignBottom").connect('button-press-event', controller.alignBottom)
        self.wTree.get_object("buttonSameWidth").connect('button-press-event', controller.sameWidth)
        self.wTree.get_object("buttonSameHeight").connect('button-press-event', controller.sameHeight)
        evt = self.wTree.get_object("eventboxVistaPosition")
        evt.set_events(Gdk.EventMask.KEY_PRESS_MASK | Gdk.EventMask.KEY_RELEASE_MASK) #@UndefinedVariable
        
        evt.connect('key-press-event', controller.onKeyPress)
        evt.connect('key-release-event', controller.onKeyRelease)

        # création des boutons VistaColorButton pour le choix des couleurs
        button = VistaColorButton()
        Gtk.Buildable.set_name(button, "mycolorbuttonTraceST")
        button.set_size_request(30,20)
        self.wTree.get_object("hboxCouleurTraceST").pack_start(button, False, False, 0)
        button = VistaColorButton()
        Gtk.Buildable.set_name(button, "mycolorbuttonTracePlotXY")
        button.set_size_request(30,20)
        self.wTree.get_object("hboxCouleurTracePlotXY").pack_start(button, False, False, 0)
        button = VistaColorButton()
        Gtk.Buildable.set_name(button, "mycolorbuttonTraceHisto")
        button.set_size_request(30,20)
        self.wTree.get_object("hboxCouleurTraceHisto").pack_start(button, False, False, 0)
        

        # création de l'arborescence graphique
        self.gdocument = vg.Gdocument(document)
        
        self.window.show_all()
        # image qui apparait quand le document visualisé a été modifié.
        self.wTree.get_object("imageModified").set_visible(False)
        
        # On masque la console
        allocpaned = self.wTree.get_object("vpanedVista").get_allocation()
        if console :
            self.wTree.get_object("vpanedVista").set_position(allocpaned.height - 30)
        else :
            self.wTree.get_object("vpanedVista").set_position(allocpaned.height)
        
        # bouton de gestion de la console
        self.wTree.get_object("buttonViderConsole").set_visible(False)
        self.wTree.get_object("buttonFermerConsole").set_visible(False)
        self.wTree.get_object("buttonInfoConsole").set_visible(False)
        # on cache les imageWarningCalculette
        self.wTree.get_object("imageWarningCalculette1").set_visible(False)
        self.wTree.get_object("imageWarningCalculette2").set_visible(False)
        self.wTree.get_object("imageWarningCalculette3").set_visible(False)
        self.wTree.get_object("imageWarningCalculette4").set_visible(False)
        self.wTree.get_object("imageWarningCalculette5").set_visible(False)
        self.wTree.get_object("imageWarningCalculette6").set_visible(False)
        
        # on est positionné sur un nombre de classe par défaut pour les histo
        self.wTree.get_object("spinbuttonNombreClassesHisto").set_sensitive(True)
        self.wTree.get_object("entryAmplitudeClassesHisto").set_sensitive(False)
        # on rend insensible les choix des min et max pour les histo
        self.wTree.get_object("hboxMinHisto").set_sensitive(False)
        self.wTree.get_object("hboxMaxHisto").set_sensitive(False)

        # on redirige les sorties standard vers la console
        if console :
            sys.stdout = ConsoleOutput(self.wTree.get_object("textviewOutput").get_buffer(),self.wTree.get_object("scrolledwindowConsole"),self.wTree.get_object("itemConsole"),  self.wTree.get_object("buttonInfoConsole"))
            sys.stderr = ConsoleOutput(self.wTree.get_object("textviewOutput").get_buffer(),self.wTree.get_object("scrolledwindowConsole"),self.wTree.get_object("itemConsole"),  self.wTree.get_object("buttonInfoConsole"))
        else :
            self.wTree.get_object("buttonOuvrirConsole").set_visible(False)
            self.wTree.get_object("itemConsole").set_visible(False)

        # widget jauge    
        self.windowJauge = Gtk.Window(type = Gtk.WindowType.POPUP)
        self.windowJauge.set_transient_for(self.window)
        self.windowJauge.set_decorated(False)
        frameJauge = Gtk.Frame()
        self.windowJauge.add(frameJauge)
        scroller = Gtk.ScrolledWindow()
        self.jauge = webkit.WebView()
        self.jauge.set_opacity(0.75)
        scroller.add(self.jauge)
        self.jauge.load_html("<body style=\"margin:0;padding:0;background-color:#EAF97D\">", None)
        frameJauge.add(scroller)
        self.windowJauge.show_all()
        self.windowJauge.set_resizable(True)
        self.windowJauge.set_visible(False)
                    
        # valeurs par defaut pour le découpage en périodes temporelles
        self.wTree.get_object("vboxDecoupageContainer").set_sensitive(False)

        # comobobox pour la couleur du découpage en périodes temporelles
        liststore = Gtk.ListStore(Pixbuf)#@UndefinedVariable
        for img in self.couleursDecoupage :
            pb = Pixbuf.new_from_file_at_size(self.dirIcons+"/"+img, 200, 25)#@UndefinedVariable
            liststore.append([pb])
        comboboxDecoupageCouleur = self.wTree.get_object("comboboxDecoupageCouleur")
        comboboxDecoupageCouleur.set_model(liststore)
        renderer = Gtk.CellRendererPixbuf()
        comboboxDecoupageCouleur.pack_start(renderer, True)
        comboboxDecoupageCouleur.add_attribute(renderer, "pixbuf", 0)
        comboboxDecoupageCouleur.set_active(0)
        
        # comobobox pour le nombre de secteurs de RDV
        liststore = Gtk.ListStore(str)
        for s in self.secteursRDV :
            liststore.append([s])
        comboboxSecteursRDV = self.wTree.get_object("comboboxSecteursRDV")
        comboboxSecteursRDV.set_model(liststore)
        renderer = Gtk.CellRendererText()
        comboboxSecteursRDV.pack_start(renderer, True)
        comboboxSecteursRDV.add_attribute(renderer, "text", 0)
        comboboxSecteursRDV.set_active(3) #rose de 16 par défaut
        
        # comobobox pour le type de RDV
        liststore = Gtk.ListStore(str)
        liststore.append(["contours"])
        liststore.append(["barres"])
        liststore.append(["boîtes"])
        comboboxTypeRDV = self.wTree.get_object("comboboxTypeRDV")
        comboboxTypeRDV.set_model(liststore)
        renderer = Gtk.CellRendererText()
        comboboxTypeRDV.pack_start(renderer, True)
        comboboxTypeRDV.add_attribute(renderer, "text", 0)
        comboboxTypeRDV.set_active(0)
        
        # comobobox pour la couleur de RDV
        liststore = Gtk.ListStore(Pixbuf)#@UndefinedVariable
        for img in self.couleursRDV :
            pb = Pixbuf.new_from_file_at_size(self.dirIcons+"/"+img, 200, 25)#@UndefinedVariable
            liststore.append([pb])
        comboboxCouleurRDV = self.wTree.get_object("comboboxCouleurRDV")
        comboboxCouleurRDV.set_model(liststore)
        renderer = Gtk.CellRendererPixbuf()
        comboboxCouleurRDV.pack_start(renderer, True)
        comboboxCouleurRDV.add_attribute(renderer, "pixbuf", 0)
        comboboxCouleurRDV.set_active(0)

        # comobobox pour la couleur de Hov
        liststore = Gtk.ListStore(Pixbuf)#@UndefinedVariable
        for img in self.couleursHov :
            pb = Pixbuf.new_from_file_at_size(self.dirIcons+"/"+img, 200, 25)#@UndefinedVariable
            liststore.append([pb])
        comboboxCouleurHov = self.wTree.get_object("comboboxCouleurHov")
        comboboxCouleurHov.set_model(liststore)
        renderer = Gtk.CellRendererPixbuf()
        comboboxCouleurHov.pack_start(renderer, True)
        comboboxCouleurHov.add_attribute(renderer, "pixbuf", 0)
        comboboxCouleurHov.set_active(0)
        
        # comobobox pour le pourcentage d'echantillon Hov quiver en X
        comboboxHovQuiverEchantillonX = self.wTree.get_object("comboboxHovQuiverEchantillonX")
        liststore = Gtk.ListStore(str)
        liststore.append(["100"])
        liststore.append(["50"])
        liststore.append(["33"])
        liststore.append(["25"])
        liststore.append(["10"])
        liststore.append(["1"])
        liststore.append(["0.1"])
        liststore.append(["0.01"])
        comboboxHovQuiverEchantillonX.set_model(liststore)       
        comboboxHovQuiverEchantillonX.set_active(0)
        renderer_text = Gtk.CellRendererText()
        comboboxHovQuiverEchantillonX.pack_start(renderer_text, True)
        comboboxHovQuiverEchantillonX.add_attribute(renderer_text, "text", 0)
        
        # comobobox pour le pourcentage d'echantillon Hov quiver en Y
        comboboxHovQuiverEchantillonY = self.wTree.get_object("comboboxHovQuiverEchantillonY")
        liststore = Gtk.ListStore(str)
        liststore.append(["100"])
        liststore.append(["50"])
        liststore.append(["33"])
        liststore.append(["25"])
        liststore.append(["10"])
        liststore.append(["1"])
        liststore.append(["0.1"])
        liststore.append(["0.01"])
        comboboxHovQuiverEchantillonY.set_model(liststore)       
        comboboxHovQuiverEchantillonY.set_active(0)
        renderer_text = Gtk.CellRendererText()
        comboboxHovQuiverEchantillonY.pack_start(renderer_text, True)
        comboboxHovQuiverEchantillonY.add_attribute(renderer_text, "text", 0)
        
        # valeurs par defaut pour hov
        self.wTree.get_object("radiobuttonHovDiscret").set_active(True)
        self.wTree.get_object("checkbuttonHovAuto").set_active(True)
        self.wTree.get_object("hboxLargeurHov").set_sensitive(False)
        self.wTree.get_object("hboxHovShading").set_sensitive(False)
        self.wTree.get_object("checkbuttonHovShading").set_active(True)
        self.wTree.get_object("checkbuttonHovSeuilAuto").set_active(True)        
        self.wTree.get_object("hboxHovSeuil").set_sensitive(False)
        
        # on ajoute les renderer aux combos parametres
        comboboxParametre = self.wTree.get_object("comboboxParametre")       
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_x")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_y")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_h")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_dd")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_ff")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_hov")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxAffichageConditionnelParametre")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxOperationParametre")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_hov_quiver_dd")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_hov_quiver_ff")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_hov_quiver_u")
        comboboxParametre.set_entry_text_column(0)
        comboboxParametre = self.wTree.get_object("comboboxParametre_hov_quiver_v")
        comboboxParametre.set_entry_text_column(0)
        
            
        # image du bouton buttonAffichageConditionnel
        buttonAffichageConditionnel = self.wTree.get_object("buttonAffichageConditionnel")
        img = Gtk.Image()
        img.set_from_pixbuf(Pixbuf.new_from_file(self.dirIcons+"/affichage_conditionnel_20x20.png"))
        buttonAffichageConditionnel.set_image(img)
        buttonAffichageConditionnelHisto = self.wTree.get_object("buttonAffichageConditionnelHisto")
        buttonAffichageConditionnelHisto.set_image(img)
        buttonAffichageConditionnelPlotXY = self.wTree.get_object("buttonAffichageConditionnelPlotXY")
        buttonAffichageConditionnelPlotXY.set_image(img)
        
        
        # bouton legende
        self.wTree.get_object("buttonLegendeST").set_sensitive(False)
        
        #Callbacks
        #self.addCallbacks()
     
    def getChildByName(self, parent, name):
        """
            Cherche dans l'arboresscence un widget correspondant au nom à partir de parent.
            Ca fait la même chose que self.wTree.get_object de libglade si ce n'est qu'on n'est pas obligé
            de rechercher depuis le sommet de l'arbre.
        """
        def iterate_children(widget, name):
            if Gtk.Buildable.get_name(widget) == name:
                return widget
            try:
                for w in widget.get_children():
                    result = iterate_children(w, name)
                    if result is not None:
                        return result
                    else:
                        continue
            except AttributeError:
                pass
        return iterate_children(parent, name)

    def readPlateformes(self) :
        """
            Lecture du fichier plate-formes
        """
        aidaHome = os.getenv('AIDA_HOME')
        aidaProfil = os.getenv('AIDA_PROFIL')
        config = configparser.ConfigParser()
        config.read(aidaHome+"/profils/"+aidaProfil+"/plate-formes", encoding = "ISO-8859-1")
        for section in config.sections() :
            if section == "FORMAT" :
                continue
            self.plateformes[section]["nom"] = section
            if config.has_option(section, "abrev") :
                self.plateformes[section]["abrev"] = config.get(section, "abrev")
            else :
                self.plateformes[section]["abrev"] = None
            if config.has_option(section, "logo_ecran") :
                self.plateformes[section]["logo"] = config.get(section, "logo_ecran")
            else :
                self.plateformes[section]["logo"] = None
        # on ajoute une section vide
        self.plateformes[""]["nom"] = ""
        self.plateformes[""]["abrev"] = ""
        self.plateformes[""]["logo"] = ""
        
    def readListeVecteurs(self):
        """
            Lecture de la liste des vecteurs pour chaque plateforme définie dans les fichiers de config plateforme.txt
        """
        dirConfigVista = os.getenv('AIDA_HOME')+"/share/vista/vecteurs/"+os.getenv('AIDA_PROFIL')
        for plateforme in self.plateformes :
            vecteurs = collections.defaultdict(dict)
            try :
                with open(dirConfigVista+"/"+plateforme+".txt") as f:
                    _ = f.readline()
                    for line in f:                    
                        tab = line.split("_")
                        classe = tab[0].lower()
                        freq = tab[-1].split(".")[0]
                        if not freq in list(vecteurs[classe].keys()) :
                            tab2=[]
                            vecteurs[classe][freq] = tab2                     
                        vecteurs[classe][freq].append(line[0:-1])
                self.listeVecteurs[plateforme] = vecteurs
            except :
                self.listeVecteurs[plateforme] = vecteurs            
    
        
    def removeElement(self, elmt):
        """
            Supprime l'élément du document
        """
        if elmt.id == -1 :
            return
        for p in range (0, len(self.document.pages)) :
            if self.document.pages[p].id == elmt.id :
                self.document.pages.remove(elmt)
                return
            for g in range (0, len(self.document.pages[p].graphiques)) :
                if self.document.pages[p].graphiques[g].id == elmt.id :
                    self.document.pages[p].graphiques.remove(elmt)
                    return
                for t in range (0, len(self.document.pages[p].graphiques[g].traces)) :
                    if self.document.pages[p].graphiques[g].traces[t].id == elmt.id :
                        self.document.pages[p].graphiques[g].traces.remove(elmt)
                        return
        print(("Erreur : aucun élément avec l'id {} n'a été trouvé pour suppression dans le document.".format(elmt.id)))        
        
    
    def setTreeSTore(self) :
        """
            Alimente le treestore
        """
        if self.document is None :
            return
        
        # document
        self.diter = self.treestore.append(None, ['Document',-1])
        # on remplit le TreeStore avec les éléments du document
        for p in range (0, len(self.document.pages)) :
            piter = self.treestore.append(self.diter, ['Page {}'.format(p+1),self.document.pages[p].id])
            for g in range (0, len(self.document.pages[p].graphiques)) :
                giter = self.treestore.append(piter, ['Graphique {}       {}...'.format(self.document.pages[p].graphiques[g].type,self.document.pages[p].graphiques[g].getValue("titre")[0:10]),self.document.pages[p].graphiques[g].id])
                for t in range (0, len(self.document.pages[p].graphiques[g].traces)) :
                    self.treestore.append(giter, ['Tracé          {} {}...'.format(self.document.pages[p].graphiques[g].traces[t].getValue("plateforme"), self.document.pages[p].graphiques[g].traces[t].getValue("parametre")[0:10]),self.document.pages[p].graphiques[g].traces[t].id])
    
    def createDocTree(self):
        """
            Treeview du document : la 2ème colonne n'est pas visualisée. Elle contient l'id de l'élément.
        """
        
        #TreeStore avec 2 colonnes : la 2ème fait référence aux indices des éléments dans le document
        self.treestore = Gtk.TreeStore(str, int)
        self.setTreeSTore()        
        # on crée le TreeView
        self.treeview = Gtk.TreeView(model=self.treestore)
        self.treeview.set_headers_visible(False)
        # on crée les colonnes
        tvcolumn1 = Gtk.TreeViewColumn()
        tvcolumn2 = Gtk.TreeViewColumn()
        tvcolumn2.set_visible(False)
        # on ajoute les colonnes
        self.treeview.append_column(tvcolumn1)
        self.treeview.append_column(tvcolumn2)
        # on crée les cellules
        cell1 = Gtk.CellRendererText()
        # on ajoute les cellules aux colonnes
        tvcolumn1.pack_start(cell1, True)
        # on associe la cellule au treestore
        tvcolumn1.add_attribute(cell1, 'text', 0)
        # on sélectionne le document
        self.treeview.get_selection().select_iter(self.diter)
        # on ajoute le treestore dans la vbox
        vboxDocTree = self.wTree.get_object("vboxDocTree")
        vboxDocTree.pack_start(self.treeview, True, True, 0)
        self.treeview.grab_focus()
        self.treeview.set_search_column(-1) #désactive la recherche par ctrl+F

        
    def ouvreFenetreAgencement(self):
        """
            Ouvre la fenêtre d'agencement des graphiques :
            le contenu de la fenêtre est mis à jour sur l'événement map,
            pour éviter les problèmes de rafraîchissement.
        """
        dialog = self.wTree.get_object("dialogAgencement")
        dialog.set_resizable(False)
        #taille de la fenêtre de tracé de l'agencement en fonction de l'orientation(A4)
        
        widget = self.wTree.get_object("frameVistaAgencement")
        gpage = self.gdocument.getElementById(vc.Document.currentId)
        if gpage.page.getValue("orientation") == "portrait" :
            widget.set_size_request(566,800)
        else :
            widget.set_size_request(800,566)
        
        dialog.show_all()
        
        reponse = dialog.run()
        if reponse == 1 : #valider
            gpage.agencementValide = True
            # mise à jour des coordonnées des graphiques
            for g in gpage.ggraphiques :
                x,y,width,height = va.ControlRectangles.getPosition(g.graphique.id)
                g.graphique.setValue("x", x)
                g.graphique.setValue("y", 100 - y - height)
                g.graphique.setValue("width", width)
                g.graphique.setValue("height", height)
            gpage.page.setValue("autoAgencement", "non")
        dialog.hide()


if os.environ.get('DISPLAY'):
    class NavigationToolbar(NavigationToolbar2GTK3):
        """
            Classe qui gère un toolbar matplotlib.
            On modifie les icones des boutons.
            On visualide le mode en cours par changement des icones sur button-press-event.
        """
        
        toolitems = [
            ('Home', 'Retour vue initiale', 'home.jpeg', 'home'), 
            ('Back', 'Retour vue précédente', 'Back.jpeg', 'back'), 
            ('Forward', 'Aller vue suivante', 'Next.jpeg', 'forward'), 
            ('Pan', 'Déplacement dans axes', 'move.jpeg', 'pan'), 
            ('Zoom', 'Zoom rectangle', 'loupe.jpeg', 'zoom')]
        dirIcons = os.getenv('AIDA_HOME')+"/share/vista/icons"  
        toolicons = [ dirIcons+"/home.png", dirIcons+"/gtk-go-forward-rtl.png",dirIcons+"/gtk-go-forward-ltr.png",dirIcons+"/pan.png",dirIcons+"/zoom.png",]
        modes = ['', '', '', 'pan/zoom', 'zoom rect']
        
        def __init__(self, canvas, window):
            NavigationToolbar2GTK3.__init__(self, canvas, window)
            self.setImages()
            self.mode_prec = ''
            
        def onPress(self,w, idx):
            """
                Callback des boutons : en fonction du mode, on change l'image des boutons pour "allumer"
                l'action en cours.
            """
            w_zoom = self.getChildByName(self, 'Zoom')
            w_pan = self.getChildByName(self, 'Pan')
            if self.mode_prec == self.modes[idx] :
                if self.modes[idx] != '' :
                    w_zoom.get_icon_widget().set_from_pixbuf(Pixbuf.new_from_file(self.toolicons[4]))
                    w_pan.get_icon_widget().set_from_pixbuf(Pixbuf.new_from_file(self.toolicons[3]))
                self.mode_prec = ''
            else :
                if self.modes[idx] != '' :
                    img = self.toolicons[idx]
                    img = img[:-4]+"_selected.png"
                    w_zoom.get_icon_widget().set_from_pixbuf(Pixbuf.new_from_file(self.toolicons[4]))
                    w_pan.get_icon_widget().set_from_pixbuf(Pixbuf.new_from_file(self.toolicons[3]))
                    w.get_icon_widget().set_from_pixbuf(Pixbuf.new_from_file(img))
                self.mode_prec = self.modes[idx]
            
                      
        def setImages(self):
            """
                Cherche dans l'arborescence du toolbar Matplotlib les widgets de type GtkToolButton et positionne les bons pictos
            """      
            def iterate_children(widget, idx=0):
                try:
                    for w in widget.get_children():
                        if isinstance(w,Gtk.ToolButton) :
                            img = Gtk.Image()
                            img.set_from_pixbuf(Pixbuf.new_from_file(self.toolicons[idx]))
                            w.set_icon_widget(img)
                            Gtk.Buildable.set_name(w, self.toolitems[idx][0])
                            w.connect('clicked', self.onPress, idx)
                            idx += 1
                        result = iterate_children(w, idx)
                        if result is not None:
                            return result
                        else:
                            continue
                except AttributeError :
                    pass
            return iterate_children(self)
    
        def getChildByName(self, parent, name):
            """
                Cherche dans l'arboresscence du toolbar le bouton correspondant au nom.
            """
            def iterate_children(widget, name):
                if Gtk.Buildable.get_name(widget) == name:
                    return widget
                try:
                    for w in widget.get_children():
                        result = iterate_children(w, name)
                        if result is not None:
                            return result
                        else:
                            continue
                except AttributeError:
                    pass
            return iterate_children(parent, name)
                 
        def set_message(self, s):
            """
                Redéfinition de la méthode pour ne pas afficher le label à coté des boutons.
            """
            self.message.set_label("")
                   
class ConsoleOutput:
    """
        Ecriture des logs dans une console
    """
    def __init__(self, buff, sw, itemConsole, infoConsole):
        #self.source=source
        self.buffer = buff
        self.buf = []
        self.sw = sw
        self.itemConsole = itemConsole
        self.infoConsole = infoConsole
        

    def updateBuffer(self):
        self.buffer.insert(self.buffer.get_end_iter(), ''.join(self.buf))
        self.buf = []
        #position scrollbar
        alloc = self.sw.get_vscrollbar().get_allocation()
        adj = self.sw.get_vadjustment()
        adj.set_value(adj.get_upper() - alloc.height)
        self.sw.set_vadjustment(adj)
        #bouton infoConsole
        if self.itemConsole.get_active() == True :
            self.infoConsole.set_visible(False)
        else :
            self.infoConsole.set_visible(True)

    def write(self, data):
        self.buf.append(data)
        if data.endswith('\n'):
            GObject.idle_add(self.updateBuffer)

    def __del__(self):
        if self.buf != []:
            GObject.idle_add(self.updateBuffer)
    
    def updateScroll(self):
        #on positionne le scroll sur la dernière ligne    
        adj = self.sw.get_vadjustment()
        adj.set_value(adj.get_upper())
        self.sw.set_vadjustment(adj)
  
    def isatty(self) :
        return False
    
    
class VistaDialog :
    """
        Ouvre une boîte de dialogue avec le message passé en argument.
    """    
    def __init__(self, message, window=None, markup=True):
        dialog = Gtk.Dialog(title="- Message Vista -", parent=window, modal=True, destroy_with_parent=True)
        # on ajoute un bouton puis on remplace son label par une icone
        button = dialog.add_button("",1)
        button.get_child().destroy()
        hbox = Gtk.Box()
        image = Gtk.Image()
        image.set_from_icon_name('gtk-apply', Gtk.IconSize.BUTTON)
        hbox.pack_end(image, False, False, 0)
        button.add(hbox)
        button.show_all()
        
        label = Gtk.Label(margin=30)
        if markup :
            label.set_markup(message)
        else :
            label.set_text(message)
        dialog.vbox.pack_start(label, False, False, 0)
        label.show()
        dialog.run()
        dialog.destroy()
        
class VistaQuestionDialog :
    """
        Ouvre une boîte de dialogue de type question avec le message passé en argument.
    """
    def __init__(self, message, window=None) :        
        dialog = Gtk.MessageDialog(parent=window, message_type=Gtk.MessageType.QUESTION, buttons=Gtk.ButtonsType.YES_NO)
        dialog.set_markup(message)
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            self.rep = True
        else :
            self.rep = False
        dialog.destroy()
    
    def getReponse(self):
        return self.rep

if os.environ.get('DISPLAY'):                                      
    class VistaColorButton(Gtk.EventBox):
        '''
        Bouton dont on peut positionner la couleur quelque soit le thème :
            en effet, suivant le thème, il n'est pas possible de modifier le style de certains widgets quelle que soit
            la méthode utilisée (modify_bg, style, rc_param, ...). Le widget EventBox déroge à cet état de fait.
        Construit à partir d'un eventbox à l'intérieur d'une frame.
        Un texte peut être passé au constructeur.
        '''
        id_classe_css = 0
        def __init__(self, label = ""):
            super(VistaColorButton, self).__init__()
            self.label = Gtk.Label(label=label) 
            self.vbox = Gtk.VBox(homogeneous=False, spacing=0) 
            self.hbox = Gtk.HBox(homogeneous=False, spacing=0)
            self.hbox.pack_start(self.vbox, True, False, 0)
            self.vbox.pack_start(self.label, True, False, 0)
            
            # on trace une frame pour que ca ressemble un peu plus à un bouton
            self.frame = Gtk.Frame()
            self.frame.add(self.hbox)
            self.add(self.frame)
    
            self.label.set_xalign(0.5)
            self.label.set_yalign(0.5)
            
            # callbacks
            self.connect("enter-notify-event", self.onButtonEnter)
            self.connect("leave-notify-event", self.onButtonLeave)

            # couleur du bouton
            self.rgba = Gdk.RGBA(0,0,0)
            self.modifyBackground(self.rgba)

            # id de la classe css du bouton
            self.id_classe_css = VistaColorButton.id_classe_css
            VistaColorButton.id_classe_css += 1

            # nom du widget = id css
            self.set_name("vistaColorButton")
            
        def show(self):
            super(VistaColorButton, self).show()
            self.hbox.show()
            self.vbox.show()
            self.frame.show()
            self.label.show()
    
        def setText(self, text):
            self.label.set_text(text)
        
        def setRgba(self, couleur):
            if couleur is not None:
                Gdk.RGBA.parse(self.rgba, couleur)
                self.modifyBackground(self.rgba)
                        
        def onButtonEnter(self, widget, event = None):
            # on modifie légèrement la couleur
            percent = 50
            R = (self.rgba.red*percent/100.) + (1 - percent/100.)
            G = (self.rgba.green*percent/100.) + (1 - percent/100.)
            B = (self.rgba.blue*percent/100.) + (1 - percent/100.)
            A = self.rgba.alpha
            rgba = Gdk.RGBA()       
            Gdk.RGBA.parse(rgba, "rgba({},{},{},{})".format(R*255,G*255,B*255,A*255))
            self.modifyBackground(rgba)
            
        def onButtonLeave(self, widget, event = None):
            self.modifyBackground(self.rgba)

        def modifyBackground(self, rgba) :
            """
                Positionne le background du colorButton en utilisant du css :
                on définit une classe 'cameleon' que l'on modifie à la volée
            """
            str_color = rgba.to_string()
            style_provider = Gtk.CssProvider()
            css_classe = "cameleon_{}".format(self.id_classe_css)
            css_data = """.{} {{ \n
                                background-color: {};\n
                                }} \n
                           #vistaColorButton {{ \n
                                background-image: none;\n
                                }} \n
                       """.format(css_classe, str_color)
            style_provider.load_from_data(bytes(css_data.encode()))
            Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
            ctx = self.get_style_context()
            ctx.remove_class(css_classe)
            ctx.add_class(css_classe)
        
