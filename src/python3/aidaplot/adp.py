#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
from optparse import OptionParser, IndentedHelpFormatter
import configparser as ConfigParser
import math
import matplotlib
import numpy as npy
import time
import re
import cfunits as cf

try :
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GObject, Pango
except Exception:
    print("Attention problème chargement GTK 3", file=sys.stderr)


import threading


#twidget = Gtk.EXPAND | Gtk.FILL | Gtk.SHRINK
twidget = None

from matplotlib.dates import num2date, date2num
from matplotlib.figure import Figure
from matplotlib import rcParams

from matplotlib.backend_bases import NavigationToolbar2, cursors
from matplotlib.widgets import SubplotTool
from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3
from gi.repository.GdkPixbuf import Pixbuf # @UnresolvedImport

#from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas

Version = 3.0  # Version ubuntu 22.04

# Alimentation constante
Config_TypeTrait = {0:"Aucun", 1:"Continu", 2:"Tiret", 3:"Pointille", 4:"Nuage"}
Config_Marqueur = {0:"Aucun", 1:"o", 2:"+", 3:"*", 4:"v"}
Config_Fonction = {0:"Aucune", 1:"Regression linéaire", 2:"Regression polynomiale", 3:"Y=0", 4:"X=Y"}
Config_Axe = {0:"Auto", 1:"Gauche", 2:"Droite"}
Vecteurs_sondage = ["Pression", "Temperature", "Tprim", "T rosee", "dd ou u", "ff ou v"]

#coul = ['red', 'black', 'blue', 'green']

##_new_tooltip_api = (Gtk.pyGtk_version[1] >= 12)
_new_tooltip_api = 1


cursord = {
    cursors.MOVE          : Gdk.Cursor(Gdk.CursorType.FLEUR),
    cursors.HAND          : Gdk.Cursor(Gdk.CursorType.HAND2),
    cursors.POINTER       : Gdk.Cursor(Gdk.CursorType.LEFT_PTR),
    cursors.SELECT_REGION : Gdk.Cursor(Gdk.CursorType.TCROSS),
    }

PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
AH = os.getenv('AIDA_HOME')
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
import AIDA
import adp_tracer as adpt

FontL = Pango.FontDescription("sans 8")
FontL.set_size=(1024*8)

class Abandon(Exception):
    """ Une exception pour arrêter le travail lorsqu'il n'y a
        rien d'autre de possible.

    Attributs:
        msg  -- explication sur l'erreur

    """
    def __init__(self, msg, Type, msg2 = None):
        dialog = Gtk.MessageDialog(
            None,
            Gtk.MessageType.WARNING,
            buttons = Gtk.ButtonsType.OK)
        dialog.set_markup(msg)
        if msg2 != None :
            dialog.format_secondary_text(msg2)

        dialog.run()
        dialog.destroy()
        Exception.__init__(self, msg)
        self.msg = msg

class FileChooserDialog(Gtk.FileChooserDialog):
    """
    selected and presents the user with a menu of supported image formats
    """
    def __init__ (self,
                  title   = 'Save file',
                  parent  = None,
                  action  = Gtk.FileChooserAction.SAVE,
                  buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_SAVE,  Gtk.ResponseType.OK),
                  path    = None,
                  filetypes = [],
                  default_filetype = None
                  ) :
        super(FileChooserDialog, self).__init__ (title, parent, action, buttons)
        super(FileChooserDialog, self).set_do_overwrite_confirmation(True)
        self.set_default_response (Gtk.ResponseType.OK)

        if not path: path = os.getcwd() + os.sep

        # create an extra widget to list supported image formats
        self.set_current_folder (path)
        self.set_current_name ('image.' + default_filetype)

        hbox = Gtk.HBox (spacing = 10)
        hbox.pack_start (Gtk.Label ("File Format:"), False, True, 0)


        self.filetypes = filetypes
        self.sorted_filetypes = list(filetypes.items())
        self.sorted_filetypes.sort()
        default = 0

        liststore = Gtk.ListStore(str)
        for i, (ext, name) in enumerate(self.sorted_filetypes):
            liststore.append([ext])
            if ext == default_filetype:
                default = i

        cbox = Gtk.ComboBox.new_with_model(liststore)
        cell = Gtk.CellRendererText()
        cbox.pack_start(cell, True)
        cbox.add_attribute(cell, 'text', 0)
        hbox.pack_start (cbox, True, True, 0)
        cbox.set_active(default)
        self.ext = default_filetype

    def get_filename_from_user (self):
        """ Recuperation du nom de fichier
        """
        while True:
            filename = None
            if self.run() != int(Gtk.ResponseType.OK):
                break
            filename = self.get_filename()
            break

        self.hide()
        return filename, self.ext


class NavigationToolbar(NavigationToolbar2GTK3):
        """
            Classe qui gère un toolbar matplotlib.
            On modifie les icones des boutons.
            On visualide le mode en cours par changement des icones sur button-press-event.
        """
        toolitems = (
            ('Tracer', 'Tracer graphe', 'Tracer.jpeg', 'home'),
            ('Home', 'Retour vue initiale', 'home.jpeg', 'home'),
            ('Back', 'Retour vue précédente', 'Back.jpeg', 'back'),
            ('Forward', 'Aller vue suivante', 'Next.jpeg', 'forward'),
            ('Pan', 'Déplacement dans axes', 'move.jpeg', 'pan'),
            ('Zoom', 'Zoom rectangle', 'loupe.jpeg', 'zoom'),
            ('Configure', 'Configuration', 'subplots.jpeg', 'configure_subplots'),
            ('Efface', 'Efface le graphe', 'clear.jpeg', 'clear_figure'),
            ('Sauvegarde', 'Sauvegarde le graphe', 'Sauve.jpeg', 'save_figure'),
            ('Impression', 'Impression le graphe', 'imprimer.jpeg', 'save_figure')
            )
        AH = os.getenv('AIDA_HOME')
        dirIcons = os.path.join(AH, 'share/aidaplot/Bitmaps')
        toolicons = [ dirIcons+"/Tracer.jpeg", dirIcons+"/home.jpeg",dirIcons+"/Back.jpeg",dirIcons+"/Next.jpeg",dirIcons+"/move.jpeg",dirIcons+"/loupe.jpeg", dirIcons+"/subplots.jpeg", dirIcons+"/clear.jpeg", dirIcons+"/Sauve.jpeg",dirIcons+"/imprimer.jpeg",]
        modes = ['', '', '', '', 'pan/zoom', 'zoom rect','configure_subplots', '', '']

#        AH = os.getenv('AIDA_HOME')
#        dirIcons = os.path.join(AH, 'share/aidaplot/Bitmaps')


#        toolicons = [ dirIcons+"/home.png", dirIcons+"/gtk-go-forward-rtl.png",dirIcons+"/gtk-go-forward-ltr.png",dirIcons+"/pan.png",dirIcons+"/zoom.png",]
#        modes = ['', '', '', 'pan/zoom', 'zoom rect']

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
#                            w.connect('clicked', self.onPress, idx)
                            idx += 1
                        result = iterate_children(w, idx)
                        if result is not None:
                            return result
                        else:
                            continue
                except AttributeError :
                    pass
            return iterate_children(self)

#            for text, tooltip_text, image_file, callback in self.tool_yitems:
#                if text is None:
#                    self.insert( Gtk.SeparatorToolItem(), -1 )
#                    continue
##                fname = os.path.join(basedir, image_file + '.png')
#                fname = os.path.join(basedir, image_file)
#                image = Gtk.Image()
#                image.set_from_file(fname)
#                tbutton = Gtk.ToolButton()
#                tbutton.set_label(text)
#                tbutton.set_icon_widget(image)
#                self.insert(tbutton, -1)
#                if callback != None :
#                    tbutton.connect('clicked', getattr(self, callback))
#                tbutton.set_tooltip_text(tooltip_text)
#
#            toolitem = Gtk.SeparatorToolItem()
#            self.insert(toolitem, -1)
#            toolitem.set_draw(False)
#            toolitem.set_expand(True)

#            toolitem = Gtk.ToolItem()
#            self.insert(toolitem, -1)
##            self.message = Gtk.Label()
#            toolitem.add(self.message)

#            self.show_all()



        def set_message(self, s):
            """
                Redéfinition de la méthode pour ne pas afficher le label à coté des boutons.
            """
            self.message.set_label("")

        def clear_figure(self, *args):
            self.canvas.figure.clear()
            self.canvas.draw()

        def save_figure(self, *args):
            dialogue = Gtk.FileChooserDialog(title="Sauvegarde graphe.",
                           parent=None,
                           action=Gtk.FileChooserAction.SAVE)
            dialogue.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
                            Gtk.STOCK_HELP, Gtk.ResponseType.HELP)
            dialogue.set_default_response(Gtk.ResponseType.OK)
            dialogue.set_select_multiple(False)
            dialogue.set_do_overwrite_confirmation(True)
            AH = os.getenv('AIDA_HOME')
            basedir = os.path.join(AH, 'tmp')
            dialogue.set_current_folder(basedir)
            flg_s = True
            while flg_s == True :
                reponse = dialogue.run()
                if reponse == Gtk.ResponseType.OK:
                    fname = dialogue.get_filename()
                    if fname:
                        try:
                            self.canvas.print_figure(fname)
                        except :
                            message = "Problème sauvegarde figure !"
                            Abandon(message, Gtk.MessageType.ERROR)
    
                    dialogue.destroy()
                    flg_s = False
                elif reponse == Gtk.ResponseType.CANCEL :
                    dialogue.destroy()
                    flg_s = False
                elif reponse == Gtk.ResponseType.HELP:
                    message = "Désolé, Pas encore de fichier d'aide "
                    print (message)
                    reponse = 0

        def on_print_dialog(self, widget = None):
        
            settings = None
            print_op = Gtk.PrintOperation()
        
            if settings != None: 
                print_op.set_print_settings(settings)            
            print_op.connect("begin_print", self.begin_print)
            print_op.connect("preview", self.draw_page)            
#        res = print_op.run(Gtk.PrintOperationAction.PRINT_DIALOG, self.window)            
            res = print_op.run(Gtk.PrintOperationAction.PRINT_DIALOG)            
            if res == Gtk.PrintOperationResult.APPLY:
                settings = print_op.get_print_settings()
            
        def begin_print(self, operation, context):
            fic = 'TOTO.ps'
            h, w = self.canvas.figure.get_size_inches()
            self.canvas.figure.set_size_inches(8.75, 9.2875)
            self.canvas.print_figure(fic, format = "ps")
            settings = operation.get_print_settings()
            printer = settings.get_printer()
            self.canvas.figure.set_size_inches(h, w)
            cmd = os.popen("lp -d {} {}; rm -f {}".format(printer, fic, fic))
            cmd.read()

        def draw_page (self, oper, operation, context, page_number):
            self.preview = True
            fic = 'TOTO.ps'

            h, w = self.canvas.figure.get_size_inches()
            self.canvas.figure.set_size_inches(8.75, 9.2875)

            self.canvas.print_figure(fic, format = "ps", orientation = 'portrait', dpi=100)
            self.canvas.figure.set_size_inches(h, w)

            visual_pdf = ["xdg-open", "gs", "atril", "evince"]
            for visu in visual_pdf :
                cmd = "which " + visu + " > /dev/null"
                Retour_cmd = os.system(cmd)

                if Retour_cmd == 0 :
                    exe = visu

            cmd = os.popen(exe + " {}; rm -f {}".format(fic, fic))
            cmd.read()



class myThread (threading.Thread):
    def __init__(self,MonIhm, widget, champsaisie, ind, acqid,progressbar, liststore_X, filtremodele_X, montre_reftime_X, liststore_Y, filtremodele_Y, montre_reftime_Y, list_reftime, canvas) :
      threading.Thread.__init__(self)
      self.MonIhm = MonIhm
      self.champsaisie = champsaisie
      self.ind = ind
      self.acqid= acqid
      self.progressbar = progressbar
      self.liststore_X = liststore_X
      self.filtremodele_X = filtremodele_X
      self.montre_reftime_X = montre_reftime_X
      self.liststore_Y = liststore_Y
      self.filtremodele_Y = filtremodele_Y
      self.montre_reftime_Y = montre_reftime_Y
      self.list_reftime = list_reftime
      self.canvas = canvas

    def run(self):
      self.Choix_vecteurs_XY(self.MonIhm, self.champsaisie,  self.ind, self.acqid,self.progressbar, self.liststore_X,
              self.filtremodele_X, self.montre_reftime_X, self.liststore_Y, self.filtremodele_Y, self.montre_reftime_Y,
              self.list_reftime, self.canvas)

    def Choix_vecteurs_XY(self,MonIhm, champsaisie, ind, E_acqid,progBar, Lstore_X, filtX, mrft_X, Lstore_Y, filtY, mrft_Y, lsttime, canvas):

        progBar.set_text("Traitement en cours...")

        try :
            acqid = E_acqid.get_text()
            rep_data = AIDA.ID_to_datapath(acqid)
        except AIDA.AidaError :
            message = "Attention Acqid non valid !"
            print(massage)
            #raise Abandon(message, Gtk.MessageType.ERROR)
            return

        try :
            liste_data = recup_liste_vecteur(rep_data)
        except:
            liste_data = []
            
        if ( len(liste_data) == 0 ) :
            message = "Pas de fichier pour l'acquisition " + acqid + " dans " + rep_data + "!"
#            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        liste_data.append("")
        liste_data_sort = sorted(liste_data, key = str.lower)

        nbv = 0
        nbc = 0
        MonIhm.dict_link_time = {'time':'lien'}
        liste_oper_sort = sorted(list(MonIhm.graph_gene.vecteurs_operations.keys()), key = str.lower)
        for fic in  liste_oper_sort :
            Iter = Lstore_X.insert(1)
            vect_time = MonIhm.graph_gene.vecteurs_operations[fic]
            Lstore_X.set(Iter, 0, fic, 1, vect_time)
            if fic == MonIhm.graph_gene.graphes[ind].vecteur_X  :
                nbc = nbv + len(MonIhm.graph_gene.vecteurs_operations)
            nbv = nbv + 1

        np = 0
        for fic in liste_data_sort :
            if ((fic.endswith("vbn.gz"))) :
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                fic_sans_ext = fic[0:len(fic)-4]
            np = np + 1
            progBar.set_fraction(np*1.0/len(liste_data_sort))
            progBar.set_text("Elaboration ihm choix vecteurs")
            try :
                info_vect = adpt.read_vect(acqid, fic[0:len(fic)-4], attributes_only = True, alarme = 0 )
                if info_vect != -1 :
                    vector_time_X = info_vect.attributes["ref_time"]
                    src = os.path.join(rep_data, vector_time_X)+'.vbn'
                    try :
                        link_time = os.readlink(src)
                        if (vector_time_X in MonIhm.dict_link_time) == False :
                            MonIhm.dict_link_time[vector_time_X] = link_time[0:len(link_time)-4]
                            MonIhm.dict_link_time[link_time[0:len(link_time)-4]] = vector_time_X
                    except OSError :
                        pass
                else :
                    vector_time_X = " "
            except :
                vector_time_X = " "

            if len(fic) > 5 :
                sys.stdout.flush()
                sys.stderr.flush()
                iter_X = Lstore_X.append()
                Lstore_X.set(iter_X, 0, fic_sans_ext, 1, vector_time_X)
                if fic[0:len(fic)-4] == MonIhm.graph_gene.graphes[ind].vecteur_X  :
                    nbc = nbv

                sys.stdout.flush()
                sys.stderr.flush()
                Iter_Y = Lstore_Y.append()
                Lstore_Y.set(Iter_Y, 0, fic_sans_ext, 1, vector_time_X)
                if fic[0:len(fic)-4] == MonIhm.graph_gene.graphes[ind].vecteur_Y  :
                    nbc = nbv


            nbv = nbv + 1
            if not vector_time_X in lsttime :
                lsttime.append(vector_time_X)

        mrft_X = lsttime[:]
        filtX.set_visible_func(MonIhm.visible_cb, mrft_X)
        mrft_Y = lsttime[:]
        filtY.set_visible_func(MonIhm.visible_cb, mrft_Y)

        progBar.set_text("Traitement terminé!")
        time.sleep(1)
        progBar.hide()
        MonIhm.ihm_choix_vecteurs = None
        canvas.get_property("window").set_cursor(Gdk.Cursor(Gdk.CursorType.LEFT_PTR))

#        nbv = 0
#        nbc = 0
#        Iter = Lstore_Y.append()
#        Lstore_Y.set(Iter, 0, ' ')
#        for fic in  liste_oper_sort :
#            Iter = Lstore_Y.append()
#            Lstore_Y.set(Iter, 0, fic)
#            if fic == self.graph_gene.graphes[ind].vecteur_Y  :
#                nbc = nbv + len(self.graph_gene.vecteurs_operations)
#            nbv = nbv + 1
#
#        for fic in liste_data_sort :
#            if len(fic) > 5 :
#                Iter_Y = Lstore_Y.append()
#                if ((fic.endswith("vbn.gz"))) :
#                    Lstore_Y.set(Iter_Y, 0, fic[0:len(fic)-7])
#                    fic_sans_ext = fic[0:len(fic)-7]
#                else :
#                    Lstore_Y.set(Iter_Y, 0, fic[0:len(fic)-4])
#                    fic_sans_ext = fic[0:len(fic)-4]
#            if fic_sans_ext == self.graph_gene.graphes[ind].vecteur_Y  :
#                nbc = nbv
#
#            nbv = nbv + 1


class meta_graph :

    def __init__ (self, type_graph) :

        self.graphes = []
        self.version = Version
        self.Orientation = 'portrait'
        self.Destination = 'Ecran'
        self.type_graphe = type_graph
        self.nb_graphe = 0
        self.nb_graphe_par_page = 6
        self.TitreGraph = "Campagne"
        self.SousTitreGraph = ""
        self.acqid = ""
        self.acqid_trace = ""
        self.unit_temp = ""
        self.B_Tracer_handler_id = None
        self.cursor_id = 0
        self.key_id = 0
        self.nom_fic_batch = None
        self.campagne = ""
        self.plateforme = ""
        self.FlgTop = 0
        self.vect_sup_top = ""
        self.FlgSequence = 0
        self.FlgDroiteDsp = 0
        self.Type_graphe_serie = 'Cumul'
        self.minProfil = -999
        self.maxProfil = -999
        self.vecteurs_operations = {}
        self.Flg_2D_Waypoints = 0
        self.Flg_2D_Fleuves = 0
        self.Flg_2D_Dep = 0
        self.Flg_2D_Relief = 0
        self.Flg_2D_TerreMer = 0
        self.PositionImage = [None, None, None, None]
        for nb in npy.arange(6) :
            Graphe = graphe ()
            self.graphes.append(Graphe)
        AH = os.getenv('AIDA_HOME')
        self.apc_basedir = os.path.join(AH, 'local/grafdef')

    def importer(self, bouton, ihm, cadre_vect, choix_acqid, bn_canvas, boit, \
                       BarreOutils, cadre_presentation, cadre_zoom) :

        for ng in  npy.arange(6) :
            del self.graphes[0]
        self.nb_graphe = 0

        for nb in npy.arange(6) :
            Graphe = graphe ()
            self.graphes.append(Graphe)

        dialogue = Gtk.FileChooserDialog(title="Ouvrir.. FICHIER",
                               parent=None,
                               action=Gtk.FileChooserAction.OPEN)
        dialogue.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialogue.add_buttons(Gtk.STOCK_OPEN, Gtk.ResponseType.OK)


        dialogue.set_default_response(Gtk.ResponseType.OK)
        dialogue.set_select_multiple(False)

        dialogue.set_current_folder(self.apc_basedir)

        vbox = Gtk.VBox(homogeneous=False, spacing=10)

        bouton_lieu_1 = Gtk.RadioButton.new_with_label_from_widget(None, "Prive")
        bouton_lieu_1.connect("toggled", self.fct_rappel, dialogue)
        bouton_lieu_1.show()
        vbox.pack_start(bouton_lieu_1, True, True, 0)

        bouton_lieu_2 = Gtk.RadioButton.new_with_label_from_widget(bouton_lieu_1, "Public")
        bouton_lieu_2.show()

        vbox.pack_start(bouton_lieu_2, True, True, 0)

        dialogue.set_extra_widget(vbox)
        canvas = bn_canvas.get_nth_page(0)
        fig = canvas.figure

        flg_s = True
        while flg_s == True :
            flg_lecture = True
            reponse = dialogue.run()
            if reponse == Gtk.ResponseType.OK:
                self.nom_fic_batch = dialogue.get_filename()
                self.current_folder = dialogue.get_current_folder()
                self.apc_basedir = self.current_folder

                graphe_cfg = ConfigParser.RawConfigParser()
                graphe_cfg.read(self.nom_fic_batch)

# Lecture partie "general_graphe" du fichier apc

                balise = 'general_graphe'
                if balise in graphe_cfg.sections():
                    try:
                        self.version = graphe_cfg.get(balise, 'Version')
                        self.nb_graphe_par_page = int(graphe_cfg.get(balise, 'NbGraphParPage'))
                        self.Orientation = graphe_cfg.get(balise, 'Orientation')
                        Type_Graphe = graphe_cfg.get(balise, 'TypGraph')
                        self.TypGraph = graphe_cfg.get(balise, 'Orientation')
                        self.TitreGraph = graphe_cfg.get(balise, 'TitreGraph')
                        self.Destination = graphe_cfg.get(balise, 'Destination')
                    except ConfigParser.NoOptionError:
                        message = "Dans " + self.nom_fic_batch + ", " + balise + \
                                        " n'a pas de type graphe declare"
                        Abandon(message, Gtk.MessageType.ERROR)
                        flg_lecture = False

                    try:
                        self.SousTitreGraph = graphe_cfg.get(balise, 'SousTitreGraph')
                    except ConfigParser.NoOptionError:
                        self.SousTitreGraph = ""

                    try:
                        self.Type_graphe_serie = graphe_cfg.get(balise, 'TypeGrapheSerie')
                    except ConfigParser.NoOptionError:
                        self.Type_graphe_serie = ""

                    try:
                        self.nb_graphe = graphe_cfg.get(balise, 'NbGraph')
                    except ConfigParser.NoOptionError:
                        self.nb_graphe = self.nb_graphe_par_page

                    try:
                        motcle = "PositionImage"
                        self.PositionImage = graphe_cfg.get(balise, motcle)[1:-1].split(", ")
                        for val in npy.arange(4) :
                            try :
                                self.PositionImage[val] = float(self.PositionImage[val])/100
                            except :
                                self.PositionImage[val] = None
                    except ConfigParser.NoOptionError:
                        self.PositionImage = [None, None, None, None]

                    if Type_Graphe  == 'SerieTempo' :
                        try:
                            self.FlgTop = graphe_cfg.get(balise, 'FlgTop')
                        except ConfigParser.NoOptionError:
                            message = "Pas d'affichage des top"
                            print (message)

                        try:
                            self.FlgSequence = graphe_cfg.get(balise, 'FlgSequence')
                        except ConfigParser.NoOptionError:
                            message = "Pas d'affichage des sequences"
                            print (message)

                    if Type_Graphe  == 'Trajectoire' :
                        try:
                            self.Flg_2D_Waypoints = int(graphe_cfg.get(balise, 'Flg_2D_Waypoints'))
                        except ConfigParser.NoOptionError:
                            message = "Pas d'affichage des Waypoints"
                            print (message)

                        try:
                            self.Flg_2D_Fleuves = int(graphe_cfg.get(balise, 'Flg_2D_Fleuves'))
                        except ConfigParser.NoOptionError:
                            message = "Pas d'affichage des fleuves"
                            print (message)

                        try:
                            self.Flg_2D_Dep = int(graphe_cfg.get(balise, 'Flg_2D_Dep'))
                        except ConfigParser.NoOptionError:
                            message = "Pas d'affichage des départements"
                            print (message)

                        try:
                            self.Flg_2D_Relief = int(graphe_cfg.get(balise, 'Flg_2D_Relief'))
                        except ConfigParser.NoOptionError:
                            message = "Pas d'affichage du relief"
                            print (message)

                        try:
                            self.Flg_2D_TerreMer = graphe_cfg.get(balise, 'Flg_2D_TerreMer')
                        except ConfigParser.NoOptionError:
                            message = "Pas d'affichage du masque terre-mer"
                            print (message)

                else :
                    message = "Pas de partie 'general_graphe' dans le fichier apc."
                    Abandon(message, Gtk.MessageType.ERROR)
                    flg_lecture = False

# Lecture partie Type_graphe du fichier apc
                if Type_Graphe not in graphe_cfg.sections() and flg_lecture == True :
                    message = "Incoherence entre TypGraph (" + Type_Graphe + ")  \
                               et balise (" + balise + ") dans " + self.nom_fic_batch
                    Abandon(message, Gtk.MessageType.ERROR)
                    flg_lecture = False

                if Type_Graphe  == 'SerieTempo' and flg_lecture == True :
                    print ("TYPE_GRAPHE = SerieTempo")
                    try:
                        NbGraph = graphe_cfg.get('SerieTempo', 'NbGraph')
                    except ConfigParser.NoOptionError:
                        message = "Dans " + self.nom_fic_batch + "[SerieTempo] pas NbGraph"
                        Abandon(message, Gtk.MessageType.ERROR)
                        continue

                    liste_infos = {}
                    for ng in range(int(NbGraph)) :
                        try:
                            motcle = "NomVecteur" + str(ng+1)
                            liste_infos[motcle] = graphe_cfg.get('SerieTempo', motcle)
                            self.graphes[ng].vecteur_Y = graphe_cfg.get('SerieTempo', motcle)
                            motcle = "MarqVecteur" + str(ng+1)
                            self.graphes[ng].type_mark = graphe_cfg.get('SerieTempo', motcle)
                            motcle = "ColorVecteur" + str(ng+1)
                            self.graphes[ng].couleur = graphe_cfg.get('SerieTempo', motcle)
                            motcle = "EpaisseurLigne" + str(ng+1)
                            self.graphes[ng].epais_trait = graphe_cfg.get('SerieTempo', motcle)
                        except ConfigParser.NoOptionError:
                            message = "Dans " + self.nom_fic_batch + "[SerieTempo] pas assez de data"
                            Abandon(message, Gtk.MessageType.ERROR)
                            flg_lecture = False
                            continue

                        motcle = "Axes" + str(ng+1)
                        try:
                            self.graphes[ng].axe = graphe_cfg.get('SerieTempo', motcle)
                        except ConfigParser.NoOptionError:
                            self.graphes[ng].axe = "Gauche"
                            pass

                        try:
                            motcle = "Type_Trait" + str(ng+1)
                            self.graphes[ng].type_trait = graphe_cfg.get('SerieTempo', motcle)
                        except ConfigParser.NoOptionError:
                            if self.graphes[ng].type_mark == '-' :
                                self.graphes[ng].type_mark == ''
                                self.graphes[ng].type_trait = '-'
                            pass

                        try:
                            motcle = "Type_echelle" + str(ng+1)
                            self.graphes[ng].type_echelle = graphe_cfg.get('SerieTempo', motcle)
                        except ConfigParser.NoOptionError:
                            pass

                        try:
                            motcle = "EchellesAxeY" + str(ng+1)
                            self.graphes[ng].ylim = graphe_cfg.get('SerieTempo', motcle)[1:-1].split(",")
                            for val in npy.arange(4) :
                                try :
                                    self.graphes[ng].ylim[val] = float(self.graphes[ng].ylim[val])
                                except :
                                    self.graphes[ng].ylim[val] = None
                        except ConfigParser.NoOptionError:
                            self.graphes[ng].ylim = [None, None, None, None]

                    try:
                        motcle = "ExtremColobar"
                        ext_Col = graphe_cfg.get('general_graphe', motcle)[1:-1].split(", ")
                        try :
                            self.minProfil = int(ext_Col[0])
                        except :
                            self.minProfil = -999
                        try :
                            self.maxProfil = int(ext_Col[1])
                        except :
                            self.maxProfil = -999
                    except ConfigParser.NoOptionError:
                        self.minProfil = -999
                        self.maxProfil = -999

                    try:
                        liste_infos["Titre"] = self.TitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de titre")

                    try:
                        liste_infos["SousTitre"] = self.SousTitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de sous titre")

                    try:
                        liste_infos["Top"] = self.FlgTop
                    except ConfigParser.NoOptionError:
                        liste_infos["Top"] = 0
                        print ("Pas d'info sur le tops")

                    try:
                        liste_infos["Sequence"] = self.FlgSequence
                    except ConfigParser.NoOptionError:
                        liste_infos["Sequence"] = 0
                        print ("Pas d'info sur affichage des sequences")

                    if flg_lecture == True :
                        ihm.ihm_serie(None, cadre_vect, choix_acqid, bn_canvas, BarreOutils, \
                                    cadre_presentation, cadre_zoom, liste_infos)
                        flg_s = False

                if Type_Graphe  == 'Dsp' and flg_lecture == True :
                    print ("TYPE_GRAPHE = Dsp")

                    liste_infos = {}
                    try:
                        motcle = "NomVecteur"
                        liste_infos[motcle] = graphe_cfg.get('Dsp', motcle)
                        self.graphes[0].vecteur_Y = graphe_cfg.get('Dsp', motcle)
                        motcle = "MarqVecteur"
                        self.graphes[0].type_mark = graphe_cfg.get('Dsp', motcle)
                        motcle = "ColorVecteur"
                        self.graphes[0].couleur = graphe_cfg.get('Dsp', motcle)
                        motcle = "EpaisseurLigne"
                        self.graphes[0].epais_trait = graphe_cfg.get('Dsp', motcle)
                    except ConfigParser.NoOptionError:
                        message = "Dans " + self.nom_fic_batch + "[Dsp] pas assez de data"
                        raise Abandon(message, Gtk.MessageType.ERROR)
                        flg_lecture = False
                        continue

                    try:
                        motcle = "Type_Trait"
                        self.graphes[0].type_trait = graphe_cfg.get('Dsp', motcle)
                    except ConfigParser.NoOptionError:
                        if self.graphes[0].type_mark == '-' :
                            self.graphes[0].type_mark == ''
                            self.graphes[0].type_trait = '-'
                        continue

                    try:
                        motcle = "EchellesAxeY"
                        self.graphes[0].ylim = graphe_cfg.get('Dsp', motcle)[1:-1].split(", ")
                        for val in npy.arange(4) :
                            try :
                                self.graphes[0].ylim[val] = float(self.graphes[0].ylim[val])
                            except :
                                self.graphes[0].ylim[val] = None
                    except ConfigParser.NoOptionError:
                        self.graphes[0].ylim = [None, None, None, None]

                    try:
                        liste_infos["Titre"] = self.TitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de titre")

                    try:
                        liste_infos["SousTitre"] = self.SousTitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de sous titre")

                    try:
                        liste_infos["Top"] = self.FlgTop
                    except ConfigParser.NoOptionError:
                        liste_infos["Top"] = 0
                        print ("Pas d'info sur le tops")

                    try:
                        liste_infos["Sequence"] = self.FlgSequence
                    except ConfigParser.NoOptionError:
                        liste_infos["Sequence"] = 0
                        print ("Pas d'info sur affichage des sequences")

                    try:
                        liste_infos["Droite_dsp"] = self.FlgDroiteDsp
                    except ConfigParser.NoOptionError:
                        liste_infos["Droite_dsp"] = 0
                        print ("Pas d'info sur affichage droite -5/3")

                    if flg_lecture == True :
                        ihm.ihm_dsp(None, cadre_vect, choix_acqid, bn_canvas, BarreOutils, \
                                    cadre_presentation, cadre_zoom, liste_infos)
                        flg_s = False

                if Type_Graphe  == 'Plot_XY' and flg_lecture == True :
                    print ("TYPE_GRAPHE = Plot_XY")
                    try:
                        NbGraph = graphe_cfg.get('Plot_XY', 'NbGraph')
                    except ConfigParser.NoOptionError:
                        message = "Dans " + self.nom_fic_batch + "[Plot_XY] pas NbGraph"
                        Abandon(message, Gtk.MessageType.ERROR)

                    liste_infos = {}
                    liste_infos["nbgraph"]=NbGraph
                    for ng in range(int(NbGraph)) :
                        try:
                            motcle = "NomVecteurX_" + str(ng)
                            liste_infos[motcle]=graphe_cfg.get('Plot_XY', motcle)
                            self.graphes[ng].vecteur_X = graphe_cfg.get('Plot_XY', motcle)
                            motcle = "NomVecteurY_" + str(ng)
                            liste_infos[motcle]=graphe_cfg.get('Plot_XY', motcle)
                            self.graphes[ng].vecteur_Y = graphe_cfg.get('Plot_XY', motcle)
                            motcle = "Type_Trait_" + str(ng)
                            self.graphes[ng].type_trait = graphe_cfg.get('Plot_XY', motcle)
                            motcle = "MarqVecteur_" + str(ng)
                            self.graphes[ng].type_mark = graphe_cfg.get('Plot_XY', motcle)
                            motcle = "ColorVecteur_" + str(ng)
                            self.graphes[ng].couleur = graphe_cfg.get('Plot_XY', motcle)
                            motcle = "EpaisseurLigne_" + str(ng)
                            self.graphes[ng].epais_trait = graphe_cfg.get('Plot_XY', motcle)
                            motcle = "FonctionVecteur_" + str(ng)
                            self.graphes[ng].fonction = graphe_cfg.get('Plot_XY', motcle)
                        except ConfigParser.NoOptionError:
                            message = "Dans " + self.nom_fic_batch + "[Plot_XY] pas assez de data"
                            Abandon(message, Gtk.MessageType.ERROR)
                            flg_lecture = False
                            continue

                        try:
                            motcle = "EchellesAxeY_" + str(ng)
                            self.graphes[ng].ylim = graphe_cfg.get('Plot_XY', motcle)[1:-1].split(",")
                            for val in npy.arange(4) :
                                try :
                                    self.graphes[ng].ylim[val] = float(self.graphes[ng].ylim[val])
                                except :
                                    self.graphes[ng].ylim[val] = None
                        except ConfigParser.NoOptionError:
                            self.graphes[ng].ylim = [None, None, None, None]

                    try:
                        liste_infos["Titre"] = self.TitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de titre")

                    try:
                        liste_infos["SousTitre"] = self.SousTitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de sous titre")

                    if flg_lecture == True :
                        flg_s = False
                        ihm.ihm_XY(None, cadre_vect, choix_acqid, bn_canvas, BarreOutils, \
                                    cadre_presentation, cadre_zoom, liste_infos)

                if Type_Graphe  == 'Trajectoire' and flg_lecture == True :
                    print ("TYPE_GRAPHE = Trajectoire")
                    liste_infos = {}
                    try:
                        motcle = "NomVecteur_lon"
                        self.graphes[0].vecteur_X = graphe_cfg.get('Trajectoire', motcle)
                        liste_infos[motcle] = self.graphes[0].vecteur_X
                        motcle = "NomVecteur_lat"
                        self.graphes[0].vecteur_Y = graphe_cfg.get('Trajectoire', motcle)
                        liste_infos[motcle] = self.graphes[0].vecteur_Y
                        motcle = "NomVecteur_alt"
                        self.graphes[0].vecteur_Z = graphe_cfg.get('Trajectoire', motcle)
                        liste_infos[motcle] = self.graphes[0].vecteur_Z
                        motcle = "Dimension"
                        self.graphes[0].dimension = graphe_cfg.get('Trajectoire', motcle)
                        liste_infos[motcle] = self.graphes[0].dimension
                        motcle = "ColorVecteur"
                        self.graphes[0].couleur = graphe_cfg.get('Trajectoire', motcle)
                        motcle = "EpaisseurLigne"
                        self.graphes[0].epais_trait = graphe_cfg.get('Trajectoire', motcle)
                    except ConfigParser.NoOptionError:
                        message = "Dans " + self.nom_fic_batch + "[Trajectoire] pas assez de data"
                        Abandon(message, Gtk.MessageType.ERROR)
                        flg_lecture = False

                    try:
                        motcle = "FlgSupCouleur"
                        self.graphes[0].flg_sup_couleur = int(graphe_cfg.get('Trajectoire', motcle))
                    except ConfigParser.NoOptionError:
                        print ("Pas de superposition couleur")
                        self.graphes[0].flg_sup_couleur = 0

                    if  self.graphes[0].flg_sup_couleur == 1 :
                        try :
                            motcle = "VecteurSupCouleur"
                            self.graphes[0].vect_sup_couleur = graphe_cfg.get('Trajectoire', motcle)
                            motcle = "NbClasseSupCouleur"
                            self.graphes[0].nb_classe_couleur = int(graphe_cfg.get('Trajectoire', motcle))
                            motcle = "SeuilsClasseSupCouleur"
                            seuils_classe_couleur = graphe_cfg.get('Trajectoire', motcle)[1:-1].split(",")
                            self.graphes[0].seuils_classe_couleur = list(map(float, seuils_classe_couleur))
                        except ConfigParser.NoOptionError:
                            continue

                    try:
                        motcle = "FlgSupVent"
                        self.graphes[0].flg_sup_vent = int(graphe_cfg.get('Trajectoire', motcle))
                    except ConfigParser.NoOptionError:
                        print ("Pas de superpositionu vent")
                        self.graphes[0].flg_sup_vent = 0

                    if  self.graphes[0].flg_sup_vent == 1 :
                        try:
                            motcle = "VecteurSupVent1"
                            self.graphes[0].vect_sup_vent1 = graphe_cfg.get('Trajectoire', motcle)
                            motcle = "VecteurSupVent2"
                            self.graphes[0].vect_sup_vent2 = graphe_cfg.get('Trajectoire', motcle)
                            motcle = "PeriodeSupVent"
                            self.graphes[0].periode_sup_vent = int(graphe_cfg.get('Trajectoire', motcle))
                        except ConfigParser.NoOptionError:
                            continue

                    try:
                        motcle = "FlgSupTexte"
                        self.graphes[0].flg_sup_texte = int(graphe_cfg.get('Trajectoire', motcle))
                    except ConfigParser.NoOptionError:
                        print ("Pas de superpositionu texte")
                        self.graphes[0].flg_sup_texte = 0

                    if  self.graphes[0].flg_sup_texte == 1 :
                        try:
                            motcle = "VecteurSupTexte"
                            self.graphes[0].vect_sup_texte = graphe_cfg.get('Trajectoire', motcle)
                            motcle = "PeriodeSupTexte"
                            self.graphes[0].periode_sup_texte = int(graphe_cfg.get('Trajectoire', motcle))
                        except ConfigParser.NoOptionError:
                            continue

                    try:
                        liste_infos["Titre"] = self.TitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de titre")

                    try:
                        liste_infos["SousTitre"] = self.SousTitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de sous titre")

                    if flg_lecture == True :
                        flg_s = False
                        ihm.ihm_trajec(None, cadre_vect, choix_acqid, bn_canvas, BarreOutils,
                                cadre_presentation, cadre_zoom, liste_infos)

                if Type_Graphe  == 'Sondage' and flg_lecture == True :
                    print ("TYPE_GRAPHE = Sondage")
                    liste_infos = {}
                    try:
                        motcle = "NomVecteurY"
                        self.graphes[0].vecteur_Y = graphe_cfg.get('Sondage', motcle)
                        liste_infos[motcle]=self.graphes[0].vecteur_Y
                        motcle = "NomVecteurX"
                        self.graphes[0].vecteur_X = graphe_cfg.get('Sondage', motcle)
                        liste_infos[motcle] = self.graphes[0].vecteur_X
                        motcle = "NomVecteurTM"
                        self.graphes[0].vecteur_TM = graphe_cfg.get('Sondage', motcle)
                        liste_infos[motcle] = self.graphes[0].vecteur_TM
                        motcle = "NomVecteurTd"
                        self.graphes[0].vecteur_TD = graphe_cfg.get('Sondage', motcle)
                        liste_infos[motcle] = self.graphes[0].vecteur_TD
                        motcle = "NomVecteurV1"
                        self.graphes[0].vecteur_V1 = graphe_cfg.get('Sondage', motcle)
                        liste_infos[motcle] = self.graphes[0].vecteur_V1
                        motcle = "NomVecteurV2"
                        self.graphes[0].vecteur_V2 = graphe_cfg.get('Sondage', motcle)
                        liste_infos[motcle] = self.graphes[0].vecteur_V2
                    except ConfigParser.NoOptionError:
                        message = "Dans " + self.nom_fic_batch + "[Sondage] pas assez de data"
                        Abandon(message, Gtk.MessageType.ERROR)
                        flg_lecture = False

                    try:
                        motcle = "EchellesAxe"
                        self.graphes[0].ylim = graphe_cfg.get('Sondage', motcle)[1:-1].split(", ")
                        for val in npy.arange(4) :
                            try :
                                self.graphes[0].ylim[val] = float(self.graphes[0].ylim[val])
                            except :
                                self.graphes[0].ylim[val] = None
                    except ConfigParser.NoOptionError:
                        self.graphes[0].ylim = [None, None, None, None]

                    try:
                        liste_infos["Titre"] = self.TitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de titre")

                    try:
                        liste_infos["SousTitre"] = self.SousTitreGraph
                    except ConfigParser.NoOptionError:
                        print ("Pas de sous titre")

                    if flg_lecture == True :
                        flg_s = False
                        ihm.ihm_sondage(None, cadre_vect, choix_acqid, bn_canvas, BarreOutils,
                                cadre_presentation, cadre_zoom, liste_infos)
            elif reponse == Gtk.ResponseType.CANCEL:
                flg_s = False

        dialogue.destroy()

    def export(self, bouton, flg) :

        if self.type_graphe == "" or self.type_graphe == None :
            message = "Type de graphe non renseigné."
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        if (self.type_graphe == 'SerieTempo' or self.type_graphe == 'Dsp' ) \
                and self.graphes[0].vecteur_Y == "" :
            message = "Pas de vecteur saisi pour tracé série"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        if self.type_graphe == 'Plot_XY' and self.graphes[0].vecteur_Y == "" \
                      and self.graphes[0].vecteur_X == "":
            message = "Pas de vecteur saisi plot XY."
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        if self.type_graphe == "Trajectoire" :
            if self.graphes[0].dimension == "2D" :
                if self.graphes[0].vecteur_X == "" or self.graphes[0].vecteur_Y == "" :
                    message = "Pas de vecteur saisi pour trajectoire 2D"
                    raise Abandon(message, Gtk.MessageType.ERROR)
                    return
            if self.graphes[0].dimension == "3D" :
                if self.graphes[0].vecteur_X == "" or self.graphes[0].vecteur_Y == "" \
                            or self.graphes[0].vecteur_Z == "" :
                    message = "Pas de vecteur saisi pour trajectoire 3D"
                    raise Abandon(message, Gtk.MessageType.ERROR)
                    return

        if self.type_graphe == "Sondage" and self.graphes[0].vecteur_X == "" :
            message = "Pas de vecteur saisi pour tracer un sondage."
            raise Abandon(message, Gtk.MessageType.ERROR)
            return
	    
        nom_fic_ags = self.graphes[0].vecteur_Y + '.apc'

# Récupération de la date et heure
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
# Vérification du nouveau PyGtk : c'est une nouvelle classe de PyGtk 2.4
#        if gtk.pygtk_version < (2, 3, 90):
#            print ("Cet exemple nécessite PyGtk 2.3.90 ou ultérieur")
#            raise SystemExit

        dialogue = Gtk.FileChooserDialog(title="Sauvegarde fichier apc..",
                       parent=None,
                       action=Gtk.FileChooserAction.SAVE)
        dialogue.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialogue.add_buttons(Gtk.STOCK_SAVE, Gtk.ResponseType.OK)
        dialogue.add_buttons(Gtk.STOCK_HELP, Gtk.ResponseType.HELP)
        dialogue.set_default_response(Gtk.ResponseType.OK)
        dialogue.set_select_multiple(False)
        dialogue.set_do_overwrite_confirmation(True)

        AH = os.getenv('AIDA_HOME')
        basedir = os.path.join(AH, 'local/grafdef')
        dialogue.set_current_folder(basedir)
        if self.nom_fic_batch == None :
            dialogue.set_current_name("No_name.apc")
        else :
            nom_fic_sauv = os.path.basename(self.nom_fic_batch)
            dialogue.set_current_name(nom_fic_sauv)
            dialogue.set_current_folder(self.current_folder)

# Elaboration boite de dialogue specifique pour
# sauvegarde fichier apc.

        B_hbox1 = Gtk.HBox(homogeneous=False, spacing=10)

        F_optg = Gtk.Frame()
        F_optg.set_label("Options Générales")
        F_optp = Gtk.Frame()
        F_optp.set_label("Présentation")
        B_hbox1.pack_start(F_optg, True, True, 0)
        B_hbox1.pack_start(F_optp, True, True, 0)

        B_vbox_g = Gtk.VBox(homogeneous=False, spacing=0)

        F_optg.add(B_vbox_g)

        L_G_typ = Gtk.Label()
        L_G_typ.set_markup("- Type fichier apc")
        L_G_typ.set_justify(Gtk.Justification.LEFT)
        B_vbox_g.pack_start(L_G_typ, True, True, 0)

        B_hbox_1 = Gtk.HBox(homogeneous=True, spacing=0)
        B_vbox_g.pack_start(B_hbox_1, True, True, 0)
        bouton_lieu_1 = Gtk.RadioButton.new_with_label_from_widget(None, "Prive")
        bouton_lieu_1.connect("toggled", self.fct_rappel, dialogue)
        bouton_lieu_1.show()
        B_hbox_1.pack_start(bouton_lieu_1, True, True, 0)

        bouton_lieu_2 = Gtk.RadioButton.new_with_label_from_widget(bouton_lieu_1, "Public")
#        bouton_lieu_2.connect("toggled", self.fct_rappel, dialogue)
        bouton_lieu_2.show()
        B_hbox_1.pack_start(bouton_lieu_2, True, True, 0)

        L_G_typ = Gtk.Label()
        L_G_typ.set_markup("- Type sortie")
        L_G_typ.set_justify(Gtk.Justification.LEFT)
        B_vbox_g.pack_start(L_G_typ, True, True, 0)

        B_hbox_1 = Gtk.HBox(homogeneous=True, spacing=0)
        B_vbox_g.pack_start(B_hbox_1, True, True, 0)
        bouton_out_1 = Gtk.RadioButton.new_with_label_from_widget(None, "Ecran")
        bouton_out_1.show()
        B_hbox_1.pack_start(bouton_out_1, True, True, 0)

        bouton_out_2 = Gtk.RadioButton.new_with_label_from_widget(bouton_out_1, "Fichier")
        bouton_out_2.show()
        B_hbox_1.pack_start(bouton_out_2, True, True, 0)

        B_hbox_1 = Gtk.HBox(homogeneous=False, spacing=0)
        B_vbox_g.pack_start(B_hbox_1, False, False, 0)
        L_format_fichier = Gtk.Label()
        L_format_fichier.set_markup("Format fichier sortie :")
        B_hbox_1.pack_start(L_format_fichier, True, True, 0)
        E_format_fichier = Gtk.Entry()
        E_format_fichier.set_size_request(80, 5)
        B_hbox_1.pack_start(E_format_fichier, True, True, 0)



        B_vbox_p = Gtk.VBox(homogeneous=False, spacing=10)
        F_optp.add(B_vbox_p)
#        B_hbox1.pack_start(B_vbox_p, True, False, 0)

        bouton_LogoMF = Gtk.CheckButton()
        bouton_LogoMF.set_label("Logo Meteo-France")
        bouton_LogoMF.show ()
        B_vbox_p.pack_start(bouton_LogoMF, True, True, 0)

        B_hbox_1 = Gtk.HBox(homogeneous=True, spacing=0)
        B_vbox_p.pack_start(B_hbox_1, True, True, 0)
        bouton_Logo = Gtk.CheckButton()
        bouton_Logo.set_label("Autre Logo")
        B_hbox_1.pack_start(bouton_Logo, True, True, 0)
        E_fichier_logo = Gtk.Entry()
        E_fichier_logo.set_size_request(80, 5)
        B_hbox_1.pack_start(E_fichier_logo, True, True, 0)

        L_P_Ori = Gtk.Label()
        L_P_Ori.set_markup("- Type sortie")
        B_vbox_p.pack_start(L_P_Ori, True, True, 0)

        B_hbox_1 = Gtk.HBox(homogeneous=True, spacing=0)
        B_vbox_p.pack_start(B_hbox_1, True, True, 0)
        bouton_ori_1 = Gtk.RadioButton.new_with_label_from_widget(None, "Paysage")
        bouton_ori_1.show()
        B_hbox_1.pack_start(bouton_ori_1, True, True, 0)

        bouton_ori_2 = Gtk.RadioButton.new_with_label_from_widget(bouton_ori_1, "Portrait")
        bouton_ori_2.show()
        B_hbox_1.pack_start(bouton_ori_2, True, True, 0)


        B_hbox1.show_all()

        dialogue.set_extra_widget(B_hbox1)

        flg_s = True
        while flg_s == True :
            reponse = dialogue.run()
            if reponse == Gtk.ResponseType.HELP:
                Fichier_aide = os.path.join (AH+'/share/aidaplot/Aide_sauvegarde_fichier_apc_dans_adp.pdf')
                os.system('xdg-open ' + Fichier_aide)
                reponse = 0

            if reponse == Gtk.ResponseType.OK:
                if bouton_out_1.get_active() == True :
                    self.Destination = "Ecran"
                else :
                    self.Destination = os.path.splitext(os.path.basename(dialogue.get_filename()))[0]

                if bouton_ori_1.get_active() == True :
                    self.Orientation = "Paysage"
                else :
                    self.Orientation = "Portrait"

                if bouton_LogoMF.get_active() == True :
                    self.flg_LogoMF = 1
                else :
                    self.flg_LogoMF = 0

                if bouton_Logo.get_active() == True :
                    if E_format_fichier.get_text() != "" :
                        self.logoAutre = E_fichier_logo.get_text()
                        print((self.logoAutre))
                    else :
                        self.logoAutre = ""
                else :
                    self.logoAutre = ""

                if E_format_fichier.get_text() != "" :
                    self.FormatOut = E_format_fichier.get_text()
                else :
                    self.FormatOut = "png"

                try :
                    fic_ags = open(dialogue.get_filename(), "w")
                except IOError:
                    message = "Impossible créer fichier " + dialogue.get_filename()
                    raise Abandon(message, Gtk.MessageType.WARNING)
                    break


                fic_ags.write('[general_graphe]\n')
                fic_ags.write('Version = %s\n' % Version)
                fic_ags.write('DateCreation = %s\n' % now_str)
                fic_ags.write('TypGraph = %s\n' % self.type_graphe)
                fic_ags.write('NbGraphParPage = %s\n' % self.nb_graphe)
                fic_ags.write('Orientation = %s\n' % self.Orientation)
                fic_ags.write('TitreGraph = %s\n' % self.TitreGraph)
                fic_ags.write('SousTitreGraph = %s\n' % self.SousTitreGraph)
                fic_ags.write('Destination = %s\n' % self.Destination)
                fic_ags.write('FlagLogoMF = %s\n' % self.flg_LogoMF)
                fic_ags.write('LogoAutre = %s\n' % self.logoAutre)
                fic_ags.write('FormatOut = %s\n' % self.FormatOut)


                pi_left = int(self.Figure.subplotpars.left*100)
                pi_right = int(self.Figure.subplotpars.right*100)
                pi_bottom = int(self.Figure.subplotpars.bottom*100)
                pi_top = int(self.Figure.subplotpars.top*100)
                pi_hspace = int(self.Figure.subplotpars.left*100)
                pi_wspace = int(self.Figure.subplotpars.wspace*100)

                fic_ags.write("PositionImage = [%d, %d, %d, %d, %d, %d]\n" % \
                  (pi_left, pi_right, pi_bottom, pi_top, pi_hspace, pi_hspace))
                if self.type_graphe  == 'SerieTempo' :
                    fic_ags.write('FlgTop = %s\n' % self.FlgTop)
                    fic_ags.write('VecteurSupTop = %s\n' % self.vect_sup_top)
                    fic_ags.write('FlgSequence = %s\n' % self.FlgSequence)
                    fic_ags.write('TypeGrapheSerie = %s\n' % self.Type_graphe_serie)


                    if self.Type_graphe_serie == 'Profil' :
                        fic_ags.write("ExtremColobar = [%d, %d]" % (int(self.minProfil), int(self.maxProfil)))

                if self.type_graphe  == 'Trajectoire' :
                    fic_ags.write('FlgTop = %s\n' % self.FlgTop)
                    fic_ags.write('VecteurSupTop = %s\n' % (self.vect_sup_top))
                    fic_ags.write('Flg_2D_Waypoints = %s\n' % self.Flg_2D_Waypoints)
                    fic_ags.write('Flg_2D_Dep = %s\n' % self.Flg_2D_Dep)
                    fic_ags.write('Flg_2D_Fleuves = %s\n' % self.Flg_2D_Fleuves)
                    fic_ags.write('Flg_2D_Relief = %s\n' % self.Flg_2D_Relief)
                    fic_ags.write('Flg_2D_TerreMer = %s\n' % self.Flg_2D_TerreMer)

                nb_gr = 0
                for i in npy.arange(6) :
                    if self.type_graphe == 'Plot_XY' :
                        if self.graphes[i].vecteur_X != "" and self.graphes[i].vecteur_Y != "" :
                            nb_gr = nb_gr + 1

                    elif self.type_graphe == 'SerieTempo' :
                        if self.graphes[i].vecteur_Y != "" :
                            nb_gr = nb_gr + 1

                    else :
                        nb_gr = 1

                fic_ags.write('[%s]\n' % self.type_graphe)
                fic_ags.write('NbGraph = %d\n' % nb_gr)

                for i in npy.arange(nb_gr) :
                    if self.type_graphe == 'Plot_XY' :
                        if self.graphes[i].vecteur_X != "" and self.graphes[i].vecteur_Y != "" :
                            fic_ags.write('NomVecteurX_%d = %s\n' % (i, self.graphes[i].vecteur_X))
                            fic_ags.write('NomVecteurY_%d = %s\n' % (i, self.graphes[i].vecteur_Y))
                            fic_ags.write('Type_Trait_%d = %s\n' % (i, self.graphes[i].type_trait))
                            fic_ags.write('MarqVecteur_%d = %s\n' % (i, self.graphes[i].type_mark))
                            fic_ags.write('ColorVecteur_%d = %s\n' % (i, self.graphes[i].couleur))
                            fic_ags.write('EpaisseurLigne_%d = %s\n' % (i, self.graphes[i].epais_trait))
                            fic_ags.write('FonctionVecteur_%d = %s\n' % (i, self.graphes[i].fonction))
                            fic_ags.write('EchellesAxeY_%d = %s\n' % (i, self.graphes[i].ylim))

                    if self.type_graphe == 'SerieTempo' :
                        if self.graphes[i].vecteur_Y != "" :
                            fic_ags.write('NomVecteur%d = %s\n' % (i+1, self.graphes[i].vecteur_Y))
                            fic_ags.write('Type_Trait%d = %s\n' % (i+1, self.graphes[i].type_trait))
                            fic_ags.write('MarqVecteur%d = %s\n' % (i+1, self.graphes[i].type_mark))
                            fic_ags.write('ColorVecteur%d = %s\n' % (i+1, self.graphes[i].couleur))
                            fic_ags.write('Axes%d = %s\n' % (i+1, self.graphes[i].axe))
                            fic_ags.write('EpaisseurLigne%d = %s\n' % (i+1, self.graphes[i].epais_trait))
                            fic_ags.write('EchellesAxeY%d = %s\n' % (i+1, self.graphes[i].ylim))
                            fic_ags.write('Type_echelle%d = %s\n' % (i+1, self.graphes[i].type_echelle))

                    if self.type_graphe == 'Dsp' :
                        if self.graphes[i].vecteur_Y != "" :
                            fic_ags.write('NomVecteur = %s\n' % (self.graphes[i].vecteur_Y))
                            fic_ags.write('Type_Trait = %s\n' % (self.graphes[i].type_trait))
                            fic_ags.write('MarqVecteur = %s\n' % (self.graphes[i].type_mark))
                            fic_ags.write('ColorVecteur = %s\n' % (self.graphes[i].couleur))
                            fic_ags.write('EpaisseurLigne = %s\n' % (self.graphes[i].epais_trait))
                            fic_ags.write('EchellesAxeY = %s\n' % (self.graphes[i].ylim))
                            fic_ags.write('FlgDroiteDsp = %s\n' % (self.graphes[i].FlgDroiteDsp))

                    if self.type_graphe == 'Sondage' :
                        if self.graphes[i].vecteur_X != "" and self.graphes[i].vecteur_Y != "" :
                            fic_ags.write('NomVecteurX = %s\n' % (self.graphes[i].vecteur_X))
                            fic_ags.write('NomVecteurY = %s\n' % (self.graphes[i].vecteur_Y))
                            fic_ags.write('NomVecteurTM = %s\n' % (self.graphes[i].vecteur_TM))
                            fic_ags.write('NomVecteurTd = %s\n' % (self.graphes[i].vecteur_TD))
                            fic_ags.write('NomVecteurV1 = %s\n' % (self.graphes[i].vecteur_V1))
                            fic_ags.write('NomVecteurV2 = %s\n' % (self.graphes[i].vecteur_V2))

                    if self.type_graphe == 'Trajectoire' :
                        if self.graphes[i].vecteur_X != "" :
                            fic_ags.write('NomVecteur_lon = %s\n' % (self.graphes[i].vecteur_X))
                        if self.graphes[i].vecteur_Y != "" :
                            fic_ags.write('NomVecteur_lat = %s\n' % (self.graphes[i].vecteur_Y))
                        if self.graphes[i].vecteur_Z != "" :
                            fic_ags.write('NomVecteur_alt = %s\n' % (self.graphes[i].vecteur_Z))
                        fic_ags.write('Dimension = %s\n' % (self.graphes[i].dimension))
                        fic_ags.write('ColorVecteur = green\n')
                        fic_ags.write('EpaisseurLigne = 1\n')
                        fic_ags.write('FlgSupCouleur = %s\n' % (self.graphes[i].flg_sup_couleur))
                        if self.graphes[i].flg_sup_couleur == 1 :
                            fic_ags.write('VecteurSupCouleur = %s\n' % (self.graphes[i].vect_sup_couleur))
                            fic_ags.write('NbClasseSupCouleur = %d\n' % (int(self.graphes[i].nb_classe_couleur)))
                            fic_ags.write('SeuilsClasseSupCouleur = %s\n' % (self.graphes[i].seuils_classe_couleur))
                        fic_ags.write('FlgSupVent = %s\n' % (self.graphes[i].flg_sup_vent))
                        if self.graphes[i].flg_sup_vent == 1 :
                            fic_ags.write('VecteurSupVent1 = %s\n' % (self.graphes[i].vect_sup_vent1))
                            fic_ags.write('VecteurSupVent2 = %s\n' % (self.graphes[i].vect_sup_vent2))
                            fic_ags.write('PeriodeSupVent = %s\n' % (self.graphes[i].periode_trace_vent))
                        fic_ags.write('FlgSupTexte = %s\n' % (self.graphes[i].flg_sup_texte))
                        if self.graphes[i].flg_sup_texte == 1 :
                            fic_ags.write('VecteurSupTexte = %s\n' % (self.graphes[i].vect_sup_texte))
                            fic_ags.write('PeriodeSupTexte = %s\n' % (self.graphes[i].periode_trace_texte))


                fic_ags.close()
                dialogue.destroy()
                flg_s = False
            elif reponse == Gtk.ResponseType.CANCEL or reponse == -4:
                print ('On ferme, pas de fichier sélectionné.')
                dialogue.destroy()
                flg_s = False

    def fct_rappel(self, widget, dialog):
        AH = os.getenv('AIDA_HOME')
        if ("desactive", "active")[widget.get_active()] == "active" :
            basedir = os.path.join(AH, 'local/grafdef')
        else :
            basedir = os.path.join(AH, 'appli/grafdef')
        if  os.path.isdir(basedir) :
            dialog.set_current_folder(basedir)
        else :
            message = "Repertoire " + basedir + " non accessible!"
            raise Abandon(message, Gtk.MessageType.WARNING)


class graphe :

    def __init__ (self) :
        self.vecteur_X = ""
        self.vecteur_Y = ""
        self.vecteur_Z = ""
        self.vecteur_TM = ""
        self.vecteur_TD = ""
        self.vecteur_V1 = ""
        self.vecteur_V2 = ""
        self.flg_sup_vent = 0
        self.vect_sup_vent1 = ""
        self.vect_sup_vent2 = ""
        self.flg_sup_texte = 0
        self.vect_sup_texte = ""
        self.flg_sup_couleur = 0
        self.vect_sup_couleur = ""
        self.dimension = "2D"
        self.type_trait = "Continu"
        self.type_mark = 'Aucun'
        self.epais_trait = 1
        self.axe = "Auto"
        self.couleur = None
        self.type_echelle = "lineaire"
        self.fonction = 'aucune'
        self.periode_trace_vent = 500
        self.periode_trace_texte = 300
        self.nb_classe_couleur = 4
        self.nb_courbe = 1
        self.seuils_classe_couleur = []
        self.ylim = [None, None, None, None]

    def __del__ (self) :
        class_name = self.__class__.__name__

class sauvegarde_fig :
    # On recupere le nom du fichier choisi et on l'affiche dans la console
    def ok_fichier(self, w, fig):
       # pdf = PdfPages(self.selectfichier.get_filename())
       # title('Page One')
       # pdf.savefig(fig) # or you can pass a Figure object to pdf.savefig
       # pdf.close()
        fig.savefig(self.selectfichier.get_filename(), papertype = 'A4', orientation = 'landscape')
        self.selectfichier.destroy()

    def destroy(self, widget):
        self.selectfichier.destroy()


    def __init__(self, widget, fig):
        # Creation d'un nouveau widget de selection de fichier
        self.selectfichier = Gtk.FileSelection("Selection de fichier")

        self.selectfichier.connect("destroy", self.destroy)
        # Connexion du bouton OK a la methode ok_fichier()
        self.selectfichier.ok_button.connect("clicked", self.ok_fichier, fig)

        # Connexion du bouton Annuler a la destruction du widget
        self.selectfichier.cancel_button.connect("clicked",
                                         lambda w: self.selectfichier.destroy())

        # Definissons le fichier, comme s'il s'agissait d'une boite de dialogue
        # d'enregistrement de fichier et que nous donnions un fichier par defaut
        self.selectfichier.set_filename("sauve_fig.png")
        self.selectfichier.show()

def change_champ_entry(Entry, IHM, champ) :
    if champ == 0 :
        IHM.graph_gene.minProfil = Entry.get_text()
    elif  champ == 1 :
        IHM.graph_gene.maxProfil = Entry.get_text()
    print(Entry.get_text(), IHM.graph_gene.minProfil,IHM.graph_gene.maxProfil )

def init_champ_meta(Entry, graphe, nbe) :
    if graphe.type_graphe == "SerieTempo" :
        graphe.graphes[nbe].vecteur_Y = Entry.get_text()

    if graphe.type_graphe == "Plot_XY" :
        if nbe % 2 == 0 :
            graphe.graphes[nbe/2].vecteur_X = Entry.get_text()
        else :
            graphe.graphes[(nbe-1)/2].vecteur_Y = Entry.get_text()

    if graphe.type_graphe == "Trajectoire" :
        if nbe == 0 :
            graphe.graphes[0].vecteur_X = Entry.get_text()
        elif  nbe == 1 :
            graphe.graphes[0].vecteur_Y = Entry.get_text()
        elif  nbe == 2 :
            graphe.graphes[0].vecteur_Z = Entry.get_text()

    if graphe.type_graphe == "Sondage" :
        if nbe == 0 :
            graphe.graphes[0].vecteur_X = Entry.get_text()
        elif  nbe == 1 :
            graphe.graphes[0].vecteur_Y = Entry.get_text()
        elif  nbe == 2 :
            graphe.graphes[0].vecteur_TM = Entry.get_text()
        elif  nbe == 3 :
            graphe.graphes[0].vecteur_TD = Entry.get_text()
        elif  nbe == 4 :
            graphe.graphes[0].vecteur_V1 = Entry.get_text()
        elif  nbe == 5 :
            graphe.graphes[0].vecteur_V2 = Entry.get_text()

def line_select_callback(eclick, erelease, IHM):
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    xmn = min(x1, x2)
    xmx = max(x1, x2)
    ymn = min(y1, y2)
    ymx = max(y1, y2)
    if  IHM.graph_gene.type_graphe == 'Visu emagramme' :
        l_sI = npy.arange(-90, 40, 10)
        l_sC = []
        for nl in npy.arange(len(l_sI)) :
            l_sC.append(str(l_sI[nl]))
        Prop = ((math.log(1050, 10) - math.log (ymx, 10))/(math.log(1050, 10) - math.log (100, 10)))
        l_x = l_sI + 90 * Prop
        eclick.inaxes.set_xticklabels(l_sC)
        eclick.inaxes.set_xticks(l_x)
        eclick.inaxes.axis([xmn, xmx, ymx, ymn])
    else :
        eclick.inaxes.axis([xmn, xmx, ymn, ymx])

    second_vol = date2num(IHM.graph_gene.date_acquisition)
    if IHM.graph_gene.unit_temp == "Seconde" :
        IHM.graph_gene.E_xmin.set_text(str(int(xmn)))
        IHM.graph_gene.Adj_deb_trace.set_value(int(xmn))
        IHM.graph_gene.E_xmax.set_text(str(int(xmx)))
        IHM.graph_gene.Adj_fin_trace.set_value(int(xmx))
    else  :
        heure = (xmn - second_vol) * 86400
        IHM.graph_gene.Adj_deb_trace.set_value(int(heure))
        heure = (xmx - second_vol) * 86400
        IHM.graph_gene.Adj_fin_trace.set_value(int(heure))

    for nb in npy.arange(len(adpt.toggle_selector.RS)) :
        adpt.toggle_selector.RS[nb].set_active(True)

def select_canvas(self, page, n_page, BarreOutils):
    BarreOutils.canvas = self.get_nth_page(n_page)

def Efface_tout(self, fig) :
    for ax in fig.get_axes() :
        ax.cla()
        fig.clear()
    fig.canvas.draw()

def zoom_trajectoire(self, axg, latmin, latmax, lonmin, lonmax, altmin, altmax) :
    axg.set_xlim3d(lonmin.get_value(), lonmax.get_value())
    axg.set_ylim3d(latmin.get_value(), latmax.get_value())
    axg.set_zlim3d(altmin.get_value(), altmax.get_value())

def combo_sequence_change(Combo, Combo_unit, E_deb, E_fin, second_ini) :
    model = Combo.get_model()
    index = Combo.get_active()
    sequence = model[index][0].split("/")

    model = Combo_unit.get_model()
    index = Combo_unit.get_active()
    unit = model[index][0]

    d_deb = sequence[1]
    d_fin = sequence[2]

    if unit == "Heure" :
        E_deb.set_text(d_deb)
        E_fin.set_text(d_fin)
    if unit == "Seconde" :
        hh, mm, ss = int(d_deb[0:2]), int(d_deb[2:4]), int(d_deb[4:6])
        E_deb.set_text(str((hh*3600 + mm*60 + ss)))
        hh2, mm, ss = int(d_fin[0:2]), int(d_fin[2:4]), int(d_fin[4:6])
        if hh2 < hh :
            hh2 = hh2 + 24
        E_fin.set_text(str((hh2*3600 + mm*60 + ss)))


def combo_unit_temp_change(Combo, IHM, E_deb, E_fin, second_ini) :
    model = Combo.get_model()
    index = Combo.get_active()
    unit = model[index][0]
    IHM.graph_gene.unit_temp = unit
    if unit == "Heure" :
        h_avant = E_deb.get_text()
        i_dat = second_ini + int(h_avant)/86400.
        E_deb.set_text(num2date(i_dat).strftime('%H%M%S'))
        h_avant = E_fin.get_text()
        i_dat = second_ini + int(h_avant)/86400.
        E_fin.set_text(num2date(i_dat).strftime('%H%M%S'))
    if unit == "Seconde" :
        h_avant = E_deb.get_text()
        hh, mm, ss = int(h_avant[0:2]), int(h_avant[2:4]), int(h_avant[4:6])
        E_deb.set_text(str((hh*3600 + mm*60 + ss)))
        h_avant = E_fin.get_text()
        hh2, mm, ss = int(h_avant[0:2]), int(h_avant[2:4]), int(h_avant[4:6])
        if hh2 < hh :
            hh2 = hh2 + 24
        E_fin.set_text(str((hh2*3600 + mm*60 + ss)))

def modif_Date_trace(ajust, IHM, Entre, second_ini, Combo) :
    model = Combo.get_model()
    index = Combo.get_active()
    unit = model[index][0]
    IHM.graph_gene.unit_temp = unit
    if unit == "Heure" :
        i_dat = second_ini + ajust.get_value()/86400
        Entre.set_text(num2date(i_dat).strftime('%H%M%S'))
    if unit == "Seconde" :
        Entre.set_text(str(int(ajust.get_value())))

def recup_liste_vecteur(repertoire) :
    try :
        liste_vecteur = [f for f in os.listdir(repertoire) \
            if ((f.endswith("vbn") or (f.endswith("vbn.gz"))) \
            and f.startswith(".") == False )]
    except OSError:
        liste_vecteur = []

    return liste_vecteur

class Create_IHM :

    DIM_FEN_l = 1018
    DIM_FEN_L = 980
    DEF_ESP = 8

    def __init__(self, acqid_arg, vecteur_arg):

        AH = os.getenv('AIDA_HOME')
        basedir = os.path.join(AH, 'share/aidaplot/Bitmaps')

        self.fenetre = Gtk.Window()
        self.fenetre.set_default_size(self.DIM_FEN_L, self.DIM_FEN_l)
        self.fenetre.connect("destroy", Gtk.main_quit)
        self.fenetre.connect("delete-event", self.quitter_adp)

        self.fenetre.set_title("AidaPlot")

        scrolledwindow = Gtk.ScrolledWindow()

        boite_v_gene = Gtk.VBox(homogeneous=False, spacing=self.DEF_ESP)

        scrolledwindow.add(boite_v_gene)
        self.fenetre.add(scrolledwindow)

        boite_h_H = Gtk.HBox(homogeneous=False, spacing=self.DEF_ESP)
        boite_h_H.set_size_request(self.DIM_FEN_l, 55)
        boite_h_B = Gtk.HBox(homogeneous=False, spacing=self.DEF_ESP)
        boite_v_gene.pack_start(boite_h_H, False, False, 0)
        boite_v_gene.pack_start(boite_h_B, True, True, 0)

# Boite verticale Gauche

        boite_v_G = Gtk.VBox(homogeneous=False, spacing=self.DEF_ESP)
        boite_v_G.set_size_request(200, 900)
        boite_h_B.pack_start(boite_v_G, False, False, 0)
        self.fenetre.set_border_width(5)

        cadre_acqid = Gtk.Frame()
        cadre_acqid.set_label("Choix acquisition")
        boite_choix_acqid = Gtk.HBox(homogeneous=False, spacing=self.DEF_ESP)
        bouton_parcourir = Gtk.Button()
        bouton_parcourir.set_label("Choix")
#        bouton_parcourir.get_child().override_font(Pango.FontDescription("sans 8"))
        label_acqid = Gtk.Label()
        label_acqid.set_markup("acq_id")
        E_choix_acqid = Gtk.Entry()
        E_choix_acqid.set_size_request(120, 25)
        if acqid_arg is not None :
            E_choix_acqid.set_text(acqid_arg)

#        E_choix_acqid.modify_font(FontL)
        bouton_info = Gtk.Button()
        bouton_info.set_label("Info")
#        bouton_info.get_child().override_font(Pango.FontDescription("sans 8"))
#        bouton_info.get_child().modify_font(FontL)
#        bouton_info.set_size_request(45, 20)
        bouton_info.connect("clicked", self.ihm_info_acqid, E_choix_acqid)

        boite_choix_acqid.pack_start(bouton_parcourir, False, False, 0)
        boite_choix_acqid.pack_start(label_acqid, False, False, 0)
        boite_choix_acqid.pack_start(E_choix_acqid, False, False, 0)
        boite_choix_acqid.pack_start(bouton_info, False, False, 0)
        boite_v_G.pack_start(cadre_acqid, False, False, 0)
        cadre_acqid.add(boite_choix_acqid)

        cadre_vect = Gtk.Frame()
        cadre_vect.set_label("Choix vecteur")
        boite_v_G.pack_start(cadre_vect, False, False, 0)

        separateur = Gtk.HSeparator()
        boite_v_G.pack_start(separateur, True, False, 0)

        cadre_zoom = Gtk.Frame()
        boite_v_G.pack_start(cadre_zoom, False, False, 0)

        cadre_presentation = Gtk.Frame()
        cadre_presentation.set_label("Présentation graphe")
        boite_v_G.pack_end(cadre_presentation, False, False, 0)

        self.graph_gene = meta_graph(None)
        E_choix_acqid.connect("activate", self.recup_fic_inf, cadre_presentation, self)
        bouton_parcourir.connect("clicked", self.Parcourir_dir, E_choix_acqid, cadre_presentation)

# Boite verticale Droite

        fig_width_cm = 21
        fig_height_cm = 29.7
        inches_per_cm = 1 / 2.58               # Convert cm to inches
        fig_width = fig_width_cm * inches_per_cm # width in inches
        fig_height = fig_height_cm * inches_per_cm       # height in inches
        fig_size = [fig_width, fig_height]

        fig = Figure(figsize = fig_size)
        self.graph_gene.Figure = fig

        canvas = FigureCanvas(fig)  # a Gtk.DrawingArea
        canvas.set_size_request(700, 500)

        boite_v_D = Gtk.VBox(homogeneous=False, spacing=self.DEF_ESP)
        boite_h_B.pack_start(boite_v_D, True, True, 0)


        BN_Canvas = Gtk.Notebook()
        BN_Canvas.set_tab_pos(Gtk.PositionType.TOP)
        L_canvas = Gtk.Label()
        L_canvas.set_markup("Page 1")
        boite_v_D.pack_start(BN_Canvas, True, True, 0)
        BN_Canvas.append_page(canvas, L_canvas)

        boite_h2 = Gtk.HBox(homogeneous=False, spacing=self.DEF_ESP)
        boite_v_D.pack_start(boite_h2, False, True, 0)

        BarreOutils = self._get_toolbar(canvas, self.fenetre)

        BarreOutils.show()

        BN_Canvas.connect("switch-page", select_canvas, BarreOutils)

        bouton_reset = BarreOutils.get_nth_item(8)
#        bouton_reset.connect("clicked", Efface_tout, fig)

# Boite Horizontal Haute

        toolConfig_action = (
            ('bouton_quitter', "/quitter.xpm",self.quitter_adp,0),
            ('bouton_importer', "/importer.xpm",self.graph_gene.importer,1),
            ('bouton_exporter', "/exporter.xpm",self.graph_gene.export,0),
            ('bouton_sondage', "/sondage.xpm",self.ihm_sondage,2),
            ('bouton_serie', "/serie.xpm",self.ihm_serie,2),
            ('bouton_data1D', "/data1D.xpm",self.ihm_visu1D,2),
            ('bouton_trajec', "/trajec.xpm",self.ihm_trajec,2),
            ('bouton_plotxy', "/plotxy.xpm",self.ihm_XY,2),
            ('bouton_dsp', "/dsp.xpm",self.ihm_dsp,2),
        )

        for widget, icon, action, flg in toolConfig_action :
            widget = Gtk.Button()
            image = Gtk.Image()
            image.set_from_file(basedir + icon)
            widget.add(image)
            if flg == 0 :
                boite_h_H.pack_start(widget, False, False, 0)
                widget.connect("clicked", action, None)
            elif flg == 1 :
                boite_h_H.pack_start(widget, False, False, 0)
                widget.connect("clicked", action, self, cadre_vect, E_choix_acqid, BN_Canvas, boite_v_D, BarreOutils, cadre_presentation, cadre_zoom)
            elif flg == 2 :
                boite_h_H.pack_end(widget, False, False, 0)
                widget.connect("clicked", action, cadre_vect, E_choix_acqid, BN_Canvas, BarreOutils, cadre_presentation, cadre_zoom, None)

        boite_h2.pack_start(BarreOutils, True, True, 0)
        if vecteur_arg is not None :
            liste_info={}
            motcle = "NomVecteur1"
            liste_info[motcle] = vecteur_arg
            motcle = "Titre"
            liste_info[motcle] = "Non"
            self.ihm_serie(self, cadre_vect, E_choix_acqid, BN_Canvas, BarreOutils, cadre_presentation, cadre_zoom, liste_info)

        self.fenetre.show_all ()

    def quitter_fenetre(self, widget, event, win, var):
        if var == 1 :
            self.win_sup_vent = 0
        elif var == 2 :
            self.win_sup_couleur = 0
        elif var == 3 :
            self.win_sup_texte = 0
        elif var == 4 :
            self.win_choix_vecteur_serie = 0
        win.destroy()

    def quitter_adp(self, widget, event):
        dialog = Gtk.MessageDialog(parent=self.fenetre,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO)
        dialog.set_markup( "Voulez-vous quitter adp?")

        dialog.set_title("Quitter")

        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            Gtk.main_quit()
            return False # returning False makes "destroy-event" be signalled
                         # for the window.
        else:
            return True # returning True avoids it to signal "destroy-event"

    def ihm_info_acqid(self, widget, champsaisie):

        acqid = champsaisie.get_text()
        if acqid == '' :
            message = "Attention Choix acquisition non rempli !"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        try :
            rep_data = AIDA.ID_to_datapath(acqid)
        except AIDA.AidaError :
            message = "Attention acq_id non valid!"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        liste_data = recup_liste_vecteur(rep_data)
        if ( len(liste_data) == 0 ) :
            message = "Pas de fichier pour l'acquisition " + acqid + " dans " + rep_data + "!"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        try :
            acq_meta = AIDA.Inf(acqid)
        except AIDA.AidaError :
            message = "Attention Acqid non valid !"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        Info = acq_meta.get_field_value("IDENTIFICATION", "plate-forme")
        Texte_eti = "* Plate-Forme : " +  Info + "\n"
        Info = acq_meta.get_field_value("IDENTIFICATION", "campagne")
        Texte_eti = Texte_eti + "* Campagne : " +  Info + "\n"
        Info = str(acq_meta.get_acquisition_borne("debut_acquisition"))
        Texte_eti = Texte_eti + "* Début acquisition : " + Info  + "\n"
        Info = str(acq_meta.get_acquisition_borne("fin_acquisition"))
        Texte_eti = Texte_eti + "* Fin acquisition : " + Info + "\n"

        liste_data.append("")
        liste_data_sort = sorted(liste_data, key = str.lower)

        # Create a new window
        window = Gtk.Window()
        window.set_title("Information acqid")
        window.set_size_request(600, 300)

        B_V_Gene = Gtk.VBox(homogeneous=False, spacing=self.DEF_ESP)
        B_H_Saisie = Gtk.HBox(homogeneous=False, spacing=self.DEF_ESP)
        B_V_Gene.pack_start(B_H_Saisie, True, True, 0)

        B_button = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Gene.pack_start(B_button, False, True, 0)

        B_Liste = Gtk.Frame()
        B_Liste.set_label("liste vecteurs                ")


        scrolledwindow = Gtk.ScrolledWindow()
        B_H_Saisie.pack_start(B_Liste, False, True, 0)
        B_Liste.add(scrolledwindow)

        B_Infos = Gtk.VBox(homogeneous=False, spacing=1)
        B_H_Saisie.pack_start(B_Infos, True, True, 0)

        cadre = Gtk.Frame()
        cadre.set_label("Informations fichier INF")
        etiquette = Gtk.Label()
        etiquette.set_markup(Texte_eti)
        etiquette.set_line_wrap(True)
        cadre.add(etiquette)
        B_Infos.pack_start(cadre, False, False, 0)

        cadre2 = Gtk.Frame()
        cadre2.set_label("Informations Vecteur")
        etiquette2 = Gtk.Label()
        cadre2.add(etiquette2)
        B_Infos.pack_start(cadre2, False, False, 0)

        B_quit = Gtk.Button()
        B_quit.set_label('Quitter')
        B_quit.set_relief(Gtk.ReliefStyle.HALF)

        B_button.pack_end(B_quit, False, True, 0)

        # create a liststore with one string column to use as the model
        liststore = Gtk.ListStore(str)
        for fic in liste_data_sort :
            Iter = liststore.append()
            if ((fic.endswith("vbn.gz"))) :
                liststore.set(Iter, 0, fic[0:len(fic)-7])
            else :
                liststore.set(Iter, 0, fic[0:len(fic)-4])

        # create the TreeView using liststore
        treeview = Gtk.TreeView(model=liststore)
        selection = treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        selection.connect("changed", self.Affiche_infos_vecteur, acqid, etiquette2)

        # create a CellRenderer to render the data
        cell = Gtk.CellRendererText()

        # create the TreeViewColumns to display the data
        tvcolumn = Gtk.TreeViewColumn('Nom du vecteur', cell, text=0)

        # add columns to treeview
        treeview.append_column(tvcolumn)

        # Allow sorting on the column
        tvcolumn.set_sort_column_id(0)

        B_quit.connect_object('clicked', lambda w: w.destroy(), window)

        # make treeview searchable
        treeview.set_search_column(0)

        scrolledwindow.add(treeview)
        window.add(B_V_Gene)
        window.show_all()

    def Affiche_infos_vecteur(self, selection, acqid, Etiq_v):

# Recherche vecteur selectionne
        tv = selection.get_tree_view()
        model = tv.get_model()
        sel = selection.get_selected_rows()
        if sel:
            model, Path = sel
            try :
                for p_pt in Path :
                    p_iter = model.get_iter(p_pt)
                    vect = model.get_value(p_iter, 0)
            except TypeError:
                return
        info_vect = adpt.read_vect(acqid, vect, attributes_only = True, alarme = 0 )
        Texte_eti="  "
        if info_vect != -1 :
            try :
                Info = info_vect.attributes["name"]
                Texte_eti = "* Name : " +  Info + "\n"
            except :
                Texte_eti = "* Name : Inconnu\n"

            try :
                Info = info_vect.attributes["unit"]
                Texte_eti = Texte_eti + "* Unite : " +  Info + "\n"
            except :
                Texte_eti = Texte_eti + "* Unite : Inconnu\n"

            try :
                Info = info_vect.attributes["format"]
                Texte_eti = Texte_eti + "* Format : " +  Info + "\n"
            except :
                Texte_eti = Texte_eti + "* Format : Inconnu\n"

            try :
                Info = info_vect.attributes["freq_ech"]
                Texte_eti = Texte_eti + "* Frequence (Ref_time) : " +  Info
            except :
                Texte_eti = Texte_eti + "* Frequence : Inconnu"

            try :
                Info = info_vect.attributes["ref_time"]
                Texte_eti = Texte_eti + "  (" +  Info +")\n"
            except :
                Texte_eti = Texte_eti + "(Inconnu)\n"

            try :
                Info = info_vect.attributes["origine"]
                Texte_eti = Texte_eti + "* Origine : " +  Info + "\n"
            except :
                Texte_eti = Texte_eti + "* Origine : Inconnu\n"

            if Info == "traitement" or Info == "traitement fvb":
                try :
                    Info = info_vect.attributes["fct_origine"]
                    Texte_eti = Texte_eti + "* Fonction : " +  Info + "\n"
                except :
                    Texte_eti = Texte_eti + "* Fonction : Inconnu\n"
            else :
                try :
                    L_Info = info_vect.attributes["chaine_mesure"].split(" ")
                    for nbi in npy.arange(len(L_Info)) :
                        Info = info_vect.attributes[L_Info[nbi]]
                        Texte_eti = Texte_eti + "* " + L_Info[nbi] + " : " + Info + "\n"
                except :
                    Texte_eti = Texte_eti + "* Fonction : Inconnu\n"

            try :
                Info =  info_vect.attributes["date_creation"]
                Texte_eti = Texte_eti + "* Date creation : " +  Info + "\n"
            except :
                Texte_eti = Texte_eti + "* Date creation : Inconnu\n"

        Etiq_v.set_text(Texte_eti)



    def recup_fic_inf(self, entry, F_pres, IHM):

        acqid = entry.get_text()
        try :
            acqid_en_cours = IHM.graph_gene.acqid
        except :
            acqid_en_cours = None

        if acqid != acqid_en_cours :
            try :
                acq_meta = AIDA.Inf(acqid)
            except AIDA.AidaError :
                message = "Attention Acqid non valid !"
                raise Abandon(message, Gtk.MessageType.ERROR)
                return
            except KeyError as err_info:
                message = u"Attention Acqid non valid !"
                raise Abandon(message, Gtk.MessageType.ERROR, msg2=str(err_info) )
                return

            IHM.graph_gene.acqid = acqid
            IHM.graph_gene.heure_dec = acq_meta.get_horaire('decollage')
            IHM.graph_gene.heure_att = acq_meta.get_horaire('atterrissage')
            IHM.graph_gene.deb_acq = acq_meta.get_acquisition_borne("debut_acquisition")
            if IHM.graph_gene.heure_dec == None :
                IHM.graph_gene.heure_dec = IHM.graph_gene.deb_acq
            IHM.graph_gene.fin_acq = acq_meta.get_acquisition_borne("fin_acquisition")
            if IHM.graph_gene.heure_att == None :
                IHM.graph_gene.heure_att = IHM.graph_gene.fin_acq
            IHM.graph_gene.plateforme = acq_meta.get_field_value("IDENTIFICATION", "plate-forme")
            IHM.graph_gene.campagne = acq_meta.get_field_value("IDENTIFICATION", "campagne")
            try :
                IHM.graph_gene.TitreGraph = "Campagne " + IHM.graph_gene.campagne
            except :
                IHM.graph_gene.TitreGraph = ""
            try :
                IHM.graph_gene.date_acquisition = acq_meta.get_date_acq()
            except KeyError:
                message = "Pas de fichier Inf pour l'acquisition " + acqid + " !"
                IHM.graph_gene.unit_temp = 'None'
                raise Abandon(message, Gtk.MessageType.ERROR)
                return

            for obj in F_pres.get_children() :
                F_pres.remove(obj)

            try :
                IHM.ihm_sequences(acq_meta, F_pres)
            except :
                return

    def _get_toolbar(self, canvas, boite):
        # must be inited after the window, drawingArea and figrcParamsure
        # attrs are set
        if matplotlib.rcParams['toolbar'] == 'classic':
            BarreOutils = NavigationToolbar (canvas, boite)
        elif matplotlib.rcParams['toolbar'] == 'toolbar2':
            BarreOutils = NavigationToolbar (canvas, boite)
#            BarreOutils = NavigationToolbar2GTK3 (canvas, boite)
        else:
            BarreOutils = None
        return BarreOutils


    def ihm_sequences(IHM, acqmeta, F_pres) :

        if IHM.graph_gene.heure_dec != None and IHM.graph_gene.heure_att != None :
            second_vol = date2num(IHM.graph_gene.date_acquisition)
            xmin = date2num(IHM.graph_gene.heure_dec)
            xmax = date2num(IHM.graph_gene.heure_att)
            amin = date2num(IHM.graph_gene.deb_acq)
            amax = date2num(IHM.graph_gene.fin_acq)
        else :
            second_vol = date2num(IHM.graph_gene.date_acquisition)
            xmin = date2num(IHM.graph_gene.deb_acq)
            xmax = date2num(IHM.graph_gene.fin_acq)
            amin = date2num(IHM.graph_gene.deb_acq)
            amax = date2num(IHM.graph_gene.fin_acq)
        valx = int((amax - second_vol) * 86400)
        valn = int((amin - second_vol) * 86400)
        valnc = int((xmin - second_vol) * 86400)
        valxc = int((xmax - second_vol) * 86400)
        valn = min(valn, valnc)
        valx = max(valx, valxc)

        B_pres = Gtk.HBox(homogeneous=False, spacing=5)
        B_Choix = Gtk.VBox(homogeneous=False, spacing=5)
        #B_Choix.set_size_request(120, 90)
        B_Debut_trace = Gtk.VBox(homogeneous=False, spacing=5)
        #B_Debut_trace.set_size_request(60, 90)
        B_Fin_trace = Gtk.VBox(homogeneous=False, spacing=5)
        #B_Fin_trace.set_size_request(60, 90)
        B_pres.pack_start(B_Choix, False, True, 0)
        B_pres.pack_start(B_Debut_trace, False, True, 0)
        B_pres.pack_start(B_Fin_trace, False, True, 0)

        L_Choix = Gtk.Label()
        L_Choix.set_markup("Choix séquence")
        Cmb_Sequence = Gtk.ComboBoxText()
        #Cmb_Sequence.set_size_request(60, 25)
#        Cmb_Sequence.get_child().modify_font(FontL)

# Sequence vol
        try :
            seq_d = int(IHM.graph_gene.heure_dec.strftime('%H%M%S'))
            seq_f = int(IHM.graph_gene.heure_att.strftime('%H%M%S'))
            if seq_f < seq_d :
                seq_f = seq_f + 240000
                seq_str = 'Vol/' + IHM.graph_gene.heure_dec.strftime('%H%M%S') + '/' + str(seq_f)
            else :
                seq_str = 'Vol/' + IHM.graph_gene.heure_dec.strftime('%H%M%S') + \
                          '/' + IHM.graph_gene.heure_att.strftime('%H%M%S')
            Cmb_Sequence.append_text(seq_str)
        except :
            print ("Pas de séquence de vol")

# Sequence Acquisition
        try :
            seq_d = int(IHM.graph_gene.deb_acq.strftime('%H%M%S'))
            seq_f = int(IHM.graph_gene.fin_acq.strftime('%H%M%S'))
            if seq_f < seq_d :
                seq_f = seq_f + 240000
                seq_str = 'Acq/' + IHM.graph_gene.deb_acq.strftime('%H%M%S') + '/' + str(seq_f)
            else :
                seq_str = 'Acq/' + IHM.graph_gene.deb_acq.strftime('%H%M%S') + \
                          '/' + IHM.graph_gene.fin_acq.strftime('%H%M%S')

            Cmb_Sequence.append_text(seq_str)
        except :
            print ("Pas de séquence d'acquisition")

        for (typ, seq) in acqmeta.iter_items_str('SEQUENCES') :
            champs = seq.split('/')
            if champs[0] != 'SEQUENCES' :
                seq_str = champs[0]+'/'+champs[1]+'/'+champs[2]
                Cmb_Sequence.append_text(seq_str)
        Cmb_Sequence.set_active(0)
        Cmb_Unite_temps = Gtk.ComboBoxText()
        Cmb_Unite_temps.append_text('Heure')
        Cmb_Unite_temps.append_text('Seconde')
        Cmb_Unite_temps.set_active(0)
        IHM.graph_gene.unit_temp = 'Heure'
        B_Choix.pack_start(L_Choix, False, True, 0)
        B_Choix.pack_start(Cmb_Sequence, False, True, 0)
        B_Choix.pack_start(Cmb_Unite_temps, False, True, 0)

        L_Debut_trace = Gtk.Label()
        L_Debut_trace.set_markup("Debut trace")
        E_Debut_trace = Gtk.Entry()
        E_Debut_trace.set_width_chars(8)
        IHM.graph_gene.E_xmin = E_Debut_trace
        #E_Debut_trace.set_size_request(60, 25)
        E_Debut_trace.set_text(num2date(xmin).strftime('%H%M%S'))
        Aj_Debut_trace = Gtk.Adjustment(value=valnc, lower=valn, upper=valx, step_increment=1, page_increment=60, page_size=1)
        Aj_Debut_trace.connect("value_changed", modif_Date_trace, IHM, E_Debut_trace, second_vol, Cmb_Unite_temps)
        IHM.graph_gene.Adj_deb_trace = Aj_Debut_trace
        S_Debut_trace = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Aj_Debut_trace)
        S_Debut_trace.set_digits(0)
        S_Debut_trace.set_draw_value(False)
        B_Debut_trace.pack_start(L_Debut_trace, False, True, 0)
        B_Debut_trace.pack_start(E_Debut_trace, False, True, 0)
        B_Debut_trace.pack_start(S_Debut_trace, False, True, 0)

#        if (int(xmax) - int(xmin)) == 1 :
#            flg_d = 24000
        L_Fin_trace = Gtk.Label()
        L_Fin_trace.set_markup("Fin trace")
        E_Fin_trace = Gtk.Entry()
        E_Fin_trace.set_width_chars(8)
        IHM.graph_gene.E_xmax = E_Fin_trace
#        E_Fin_trace.set_size_request(60, 25)
###        if int(H_Fin_Trace) < int(H_Deb_Trace) :
###            H_Fin_Trace = str( int(H_Fin_Trace) + 240000)
        E_Fin_trace.set_text(num2date(xmax).strftime('%H%M%S'))
        Aj_Fin_trace = Gtk.Adjustment(value=valxc, lower=valn, upper=valx, step_increment=1, page_increment=60, page_size=1)
        Aj_Fin_trace.connect("value_changed", modif_Date_trace, IHM, E_Fin_trace, second_vol, Cmb_Unite_temps)
        IHM.graph_gene.Adj_fin_trace = Aj_Fin_trace
        S_Fin_trace = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Aj_Fin_trace)
        S_Fin_trace.set_digits(0)
        S_Fin_trace.set_draw_value(False)
        B_Fin_trace.pack_start(L_Fin_trace, False, True, 0)
        B_Fin_trace.pack_start(E_Fin_trace, False, True, 0)
        B_Fin_trace.pack_start(S_Fin_trace, False, True, 0)

        F_pres.add(B_pres)
        Cmb_Unite_temps.connect('changed', combo_unit_temp_change, IHM, E_Debut_trace, E_Fin_trace, second_vol)
        Cmb_Sequence.connect('changed', combo_sequence_change, Cmb_Unite_temps, E_Debut_trace, E_Fin_trace, second_vol)

        if IHM.graph_gene.type_graphe == "Trajectoire" :
            print ("Trace IHM zoom trajectoire")

        B_pres.show_all()


    def ihm_trajec(self, widget, cadre_vect, choix_acqid, bn_canvas, BarreOutils, cadre_presentation, cadre_zoom, liste_infos) :

        AH = os.getenv('AIDA_HOME')
        basedir = os.path.join(AH, 'share/aidaplot/Bitmaps')

        toolConfig2D = (
            ('Affichage des points caractéristiques', "Flg_2D_Waypoints"),
            ('Affichage fleuves et rivières', "Flg_2D_Fleuves"),
            ('Affichage limites départements', "Flg_2D_Dep"),
            ('Affichage relief', "Flg_2D_Relief"),
            ('Affichage masque terre-mer', "Flg_2D_TerreMer"),
        )

        self.graph_gene.type_graphe = "Trajectoire"
        self.graph_gene.adj_fixe = None
        if liste_infos == None :
            for ng in  npy.arange(6) :
                del self.graph_gene.graphes[0]
            self.graph_gene.nb_graphe = 0

            for nb in npy.arange(6) :
                Graphe = graphe ()
                self.graph_gene.graphes.append(Graphe)

        for obj in cadre_vect.get_children() :
            cadre_vect.remove(obj)

        choix_vecteur = []
        choix_entry = {}
        BV_choix_vecteur = Gtk.VBox(homogeneous=False, spacing=5)

        BH_choix = Gtk.HBox(homogeneous=False, spacing=5)
        BV_choix_vecteur.pack_start(BH_choix, False, True, 0)
        bouton_parcourir = Gtk.Button()
        bouton_parcourir.set_label('Choix')
#        bouton_parcourir.get_child().modify_font(Pango.FontDescription("sans 8"))
        bouton_parcourir.set_size_request(45, 20)
        label_vecteur = Gtk.Label()
        label_vecteur.set_markup("Latitude")
        E_choix_vecteur_lat = Gtk.Entry()
        E_choix_vecteur_lat.connect("activate", init_champ_meta,self.graph_gene,0)
        E_choix_vecteur_lat.set_width_chars(25)
#        E_choix_vecteur_lat.modify_font(Pango.FontDescription("sans 9") )
        BH_choix.pack_start(bouton_parcourir, False, False, 0)
        BH_choix.pack_start(label_vecteur, False, False, 0)
        BH_choix.pack_end(E_choix_vecteur_lat, False, False, 0)
        choix_vecteur.append(E_choix_vecteur_lat)
        choix_entry["vecteur_lat"] = E_choix_vecteur_lat
        bouton_parcourir.connect("button-press-event", self.Choix_vecteur_serie_1D, 4, choix_vecteur, 0, choix_acqid)

        BH_choix = Gtk.HBox(homogeneous=False, spacing=5)
        BV_choix_vecteur.pack_start(BH_choix, False, True, 0)
        bouton_parcourir = Gtk.Button()
        bouton_parcourir.set_label('Choix')
#        bouton_parcourir.get_child().modify_font(Pango.FontDescription("sans 8"))
        bouton_parcourir.set_size_request(45, 20)
        label_vecteur = Gtk.Label()
        label_vecteur.set_markup("Longitude")
        E_choix_vecteur_lon = Gtk.Entry()
        E_choix_vecteur_lon.connect("activate", init_champ_meta,self.graph_gene,1)
        E_choix_vecteur_lon.set_width_chars(25)
#        E_choix_vecteur_lon.modify_font(Pango.FontDescription("sans 9") )
        BH_choix.pack_start(bouton_parcourir, False, False, 0)
        BH_choix.pack_start(label_vecteur, False, False, 0)
        BH_choix.pack_end(E_choix_vecteur_lon, False, False, 0)
        choix_vecteur.append(E_choix_vecteur_lon)
        choix_entry["vecteur_lon"] = E_choix_vecteur_lon
        bouton_parcourir.connect("button-press-event", self.Choix_vecteur_serie_1D, 3, choix_vecteur, 1, choix_acqid)

        BH_choix = Gtk.HBox(homogeneous=False, spacing=5)
        BV_choix_vecteur.pack_start(BH_choix, False, True, 0)
        bouton_parcourir = Gtk.Button()
        bouton_parcourir.set_label('Choix')
#        bouton_parcourir.get_child().modify_font(Pango.FontDescription("sans 8"))
        bouton_parcourir.set_size_request(45, 20)
        label_vecteur = Gtk.Label()
        label_vecteur.set_markup("Altitude")
        E_choix_vecteur_alt = Gtk.Entry()
        E_choix_vecteur_alt.connect("activate", init_champ_meta,self.graph_gene,2)
        E_choix_vecteur_alt.set_width_chars(25)
#        E_choix_vecteur_alt.modify_font(Pango.FontDescription("sans 9") )
        BH_choix.pack_start(bouton_parcourir, False, False, 0)
        BH_choix.pack_start(label_vecteur, False, False, 0)
        BH_choix.pack_end(E_choix_vecteur_alt, False, False, 0)
        choix_vecteur.append(E_choix_vecteur_alt)
        choix_entry["vecteur_alt"] = E_choix_vecteur_alt
        bouton_parcourir.connect("button-press-event", self.Choix_vecteur_serie_1D, 2, choix_vecteur, 2, choix_acqid)
        self.win_choix_vecteur_serie = 0

        bt_3D = Gtk.RadioButton.new_with_label_from_widget(None, "Trajectoire 3D")
        BV_choix_vecteur.pack_start(bt_3D, True, True, 0)
        choix_entry["bt_3D"] = bt_3D
        bt_2Dh = Gtk.RadioButton.new_with_label_from_widget(bt_3D, "Trajectoire 2D horizontale")
        BV_choix_vecteur.pack_start(bt_2Dh, True, True, 0)
        choix_entry["bt_2Dh"] = bt_2Dh
        bt_2Dv = Gtk.RadioButton.new_with_label_from_widget(bt_3D, "Trajectoire 2D verticale")
        BV_choix_vecteur.pack_start(bt_2Dv, True, True, 0)
        choix_entry["bt_2Dv"] = bt_2Dv
        bt_2Dh.set_active(True)

        separateur = Gtk.HSeparator()
        BV_choix_vecteur.pack_start(separateur, True, False, 0)

# Box titre du graphique
        BV_Titre = Gtk.VBox(homogeneous=False, spacing=5)
        L_Titre = Gtk.Label()
        L_Titre.set_markup("Titre du graphique")
        E_Titre = Gtk.Entry()
        BV_Titre.pack_start(L_Titre, False, True, 0)
        BV_Titre.pack_start(E_Titre, False, True, 0)
        L_SousTitre = Gtk.Label()
        L_SousTitre.set_markup("Sous Titre.")
        E_SousTitre = Gtk.Entry()
        BV_Titre.pack_start(L_SousTitre, False, True, 0)
        BV_Titre.pack_start(E_SousTitre, False, True, 0)
        BV_choix_vecteur.pack_start(BV_Titre, False, True, 0)
        choix_entry["Titre"] = E_Titre
        choix_entry["SousTitre"]=E_SousTitre
        if liste_infos != None :
            if liste_infos["Titre"] != "" :
                E_Titre.set_text(liste_infos["Titre"])
            elif self.graph_gene.campagne != "" :
                E_Titre.set_text(self.graph_gene.TitreGraph)
            if liste_infos["SousTitre"] != "" :
                E_SousTitre.set_text(liste_infos["SousTitre"])
            elif self.graph_gene.campagne != "" :
                E_SousTitre.set_text(self.graph_gene.SousTitreGraph)

        separateur = Gtk.HSeparator()
        BV_choix_vecteur.pack_start(separateur, True, False, 0)

# Box configuration fond de cartes
        BV_PtC = Gtk.VBox(homogeneous=False, spacing=5)
        for text, flag,  in toolConfig2D :
            C_PtC = Gtk.CheckButton()
            C_PtC.set_label(text)
            if getattr(self.graph_gene, flag) == 1 :
                C_PtC.set_active(True) 
            BV_PtC.pack_start(C_PtC, False, True, 0)
            C_PtC.connect('toggled', self.change_etat_btn, flag, None, 1, 0)
            choix_entry[flag] = C_PtC
        BV_choix_vecteur.pack_start(BV_PtC, False, True, 0)

        C_PtD = Gtk.RadioButton.new_with_label_from_widget(None,"2D Est/Ouest")
        choix_entry["2Deo"] = C_PtD
        BV_PtC.pack_start(C_PtD, False, True, 0)
        C_PtD2 = Gtk.RadioButton.new_with_label_from_widget(C_PtD,"2D Nord/Sud")
        choix_entry["2Dns"] = C_PtD2
        BV_PtC.pack_start(C_PtD2, False, True, 0)
#        C_PtC = Gtk.CheckButton()
#        C_PtC.set_label("Affichage des tops")
#        choix_entry["Tops"] = C_PtC
#        C_PtC.connect('toggled', self.change_etat_btn, "FlgTop", None, 1, 0)
#        BV_PtC.pack_start(C_PtC, False, True, 0)

        bt_2Dh.connect('toggled', self.change_type_traj, choix_entry,1)
        bt_2Dv.connect('toggled', self.change_type_traj, choix_entry,1)

        separateur = Gtk.HSeparator()
        BV_choix_vecteur.pack_start(separateur, True, False, 0)

# Box superposition
        B_VSup = Gtk.VBox(homogeneous=False, spacing=5)
        BV_choix_vecteur.pack_start(B_VSup, False, True, 0)

        L_Sup = Gtk.Label()
        L_Sup.set_markup("Superposition")
        B_VSup.pack_start(L_Sup, False, True, 0)

        B_Sup = Gtk.HBox(homogeneous=False, spacing=5)
        B_VSup.pack_start(B_Sup, False, True, 0)

        B_sup_vent = Gtk.VBox(homogeneous=False, spacing=0)
        bt_sup_vent = Gtk.ToggleButton()
        image = Gtk.Image()
        image.set_from_file(basedir+"/sup_vent.xpm")
        bt_sup_vent.add(image)
        E_sup_vent1 = Gtk.Entry()
        E_sup_vent1.set_width_chars(15)
#        E_sup_vent1.modify_font(Pango.FontDescription("sans 7") )
        try :
            E_sup_vent1.set_text(self.graph_gene.graphes[0].vect_sup_vent1)
        except :
            print ("Pas de valeur vent1 ")
        E_sup_vent2 = Gtk.Entry()
        E_sup_vent2.set_width_chars(15)
#        E_sup_vent2.modify_font(Pango.FontDescription("sans 7") )
        try :
            E_sup_vent2.set_text(self.graph_gene.graphes[0].vect_sup_vent2)
        except :
            print ("Pas de valeur vent2 ")
        B_Sup.pack_start(B_sup_vent, False, True, 0)
        B_sup_vent.pack_start(bt_sup_vent, False, True, 0)
        B_sup_vent.pack_start(E_sup_vent1, False, True, 0)
        B_sup_vent.pack_start(E_sup_vent2, False, True, 0)
        Choix_sup = []
        Choix_sup.append(E_sup_vent1)
        Choix_sup.append(E_sup_vent2)
        bt_sup_vent.connect("button-press-event", self.ihm_Choix_Sup_vent, Choix_sup, choix_acqid)
        self.win_sup_vent = 0


        B_sup_couleur = Gtk.VBox(homogeneous=False, spacing=5)
        bt_sup_couleur = Gtk.ToggleButton()
        image = Gtk.Image()
        image.set_from_file(basedir+"/sup_couleur.xpm")
        bt_sup_couleur.add(image)
        E_sup_couleur = Gtk.Entry()
        E_sup_couleur.set_width_chars(15)
#        E_sup_couleur.modify_font(Pango.FontDescription("sans 7") )
        try :
            E_sup_couleur.set_text(self.graph_gene.graphes[0].vect_sup_couleur)
        except :
            print ("Pas de valeur couleur ")
        Choix_sup.append(E_sup_couleur)
        bt_sup_couleur.connect("button-press-event", self.ihm_Choix_Sup_vecteur, E_sup_couleur, choix_acqid, "Couleur")
        self.win_sup_couleur = 0
        B_Sup.pack_start(B_sup_couleur, False, True, 0)
        B_sup_couleur.pack_start(bt_sup_couleur, False, True, 0)
        B_sup_couleur.pack_start(E_sup_couleur, False, True, 0)

        B_sup_texte = Gtk.VBox(homogeneous=False, spacing=5)
        bt_sup_texte = Gtk.ToggleButton()
        image = Gtk.Image()
        image.set_from_file(basedir+"/sup_texte.xpm")
        bt_sup_texte.add(image)
        E_sup_texte = Gtk.Entry()
        E_sup_texte.set_width_chars(15)
#        E_sup_texte.modify_font(Pango.FontDescription("sans 7") )
        try :
            E_sup_texte.set_text(self.graph_gene.graphes[0].vect_sup_texte)
        except :
            print ("Pas de valeur texte ")
        Choix_sup.append(E_sup_texte)
        B_Sup.pack_start(B_sup_texte, False, True, 0)
        bt_sup_texte.connect("button-press-event", self.ihm_Choix_Sup_vecteur, E_sup_texte, choix_acqid, "Texte")
        self.win_sup_texte = 0
        B_sup_texte.pack_start(bt_sup_texte, False, True, 0)
        B_sup_texte.pack_start(E_sup_texte, False, True, 0)

        B_Sup2 = Gtk.HBox(homogeneous=False, spacing=5)
        B_VSup.pack_start(B_Sup2, False, True, 0)

        B_sup_top = Gtk.VBox(homogeneous=False, spacing=5)
        bt_sup_top = Gtk.ToggleButton()
        image = Gtk.Image()
        image.set_from_file(basedir+"/top.jpeg")
        bt_sup_top.add(image)
        E_sup_top = Gtk.Entry()
        E_sup_top.set_width_chars(15)
#        E_sup_texte.modify_font(Pango.FontDescription("sans 7") )
        try :
            E_sup_top.set_text(self.vect_sup_top)
        except :
            print ("Pas de valeur texte ")
        choix_entry["Tops"] = E_sup_top
        Choix_sup.append(E_sup_top)
        B_Sup2.pack_start(B_sup_top, False, True, 0)
        bt_sup_top.connect("button-press-event", self.ihm_Choix_Sup_vecteur, E_sup_top, choix_acqid, "Top")
        self.win_sup_top = 0
        B_sup_top.pack_start(bt_sup_top, False, True, 0)
        B_sup_top.pack_start(E_sup_top, False, True, 0)

        if liste_infos != None :
            try :
                motcle = "NomVecteur_lon"
                E_choix_vecteur_lon.set_text(liste_infos[motcle])
                motcle = "NomVecteur_lat"
                E_choix_vecteur_lat.set_text(liste_infos[motcle])
                motcle = "NomVecteur_alt"
                E_choix_vecteur_alt.set_text(liste_infos[motcle])
            except :
                pass
        cadre_vect.add(BV_choix_vecteur)

        cadre_vect.show_all()
        cadre_presentation.show_all()
        BarreOutils.update()
        bouton_tracer = BarreOutils.get_nth_item(0)

        if liste_infos != None :
            if liste_infos["Dimension"] == "3D" :
                bt_3D.set_active(True)
                choix_entry["Flg_2D_Waypoints"].show()
                choix_entry["Flg_2D_Fleuves"].show()
                choix_entry["Flg_2D_Dep"].show()
                choix_entry["Flg_2D_Relief"].show()
                choix_entry["Flg_2D_TerreMer"].show()
                C_PtC.hide()
                C_PtD.hide()
                C_PtD2.hide()
            elif liste_infos["Dimension"] == "2D" :
                bt_2Dh.set_active(True)
                C_PtD.hide()
                C_PtD2.hide()
            elif liste_infos["Dimension"] == "2Dvo" :
                bt_2Dv.set_active(True)
                C_PtD.set_active(True)
                choix_entry["Flg_2D_Waypoints"].hide()
                choix_entry["Flg_2D_Fleuves"].hide()
                choix_entry["Flg_2D_Dep"].hide()
                choix_entry["Flg_2D_Relief"].hide()
                choix_entry["Flg_2D_TerreMer"].hide()
            elif liste_infos["Dimension"] == "2Dva" :
                bt_2Dv.set_active(True)
                C_PtD2.set_active(True)
                choix_entry["Flg_2D_Waypoints"].hide()
                choix_entry["Flg_2D_Fleuves"].hide()
                choix_entry["Flg_2D_Dep"].hide()
                choix_entry["Flg_2D_Relief"].hide()
                choix_entry["Flg_2D_TerreMer"].hide()
        else :
            C_PtD.hide()
            C_PtD2.hide()

        try:
            bouton_tracer.disconnect(self.graph_gene.B_Tracer_handler_id)
        except TypeError :
            pass

        self.graph_gene.B_Tracer_handler_id = bouton_tracer.connect("clicked", adpt.Tracer_trajectoire, self, bn_canvas, choix_entry, choix_acqid, Choix_sup, cadre_presentation, cadre_zoom)

    def  change_etat_btn (self, widget, flg, ind, ok, nok):
        if ind != None :
            attr = self.graph_gene.graphes[ind-1]
        else :
            attr = self.graph_gene

        if  widget.get_active() == True :
            setattr(attr, flg, ok)
        else :
            setattr(attr, flg, nok)

    def  change_type_traj (self, widget, choix_vect, int_type_traj):

        if choix_vect["bt_3D"].get_active() == True :
            self.graph_gene.graphes[0].dimension = "3D"

        if choix_vect["bt_2Dv"].get_active() == True :
            choix_vect["2Deo"].show()
            choix_vect["2Dns"].show()
            if choix_vect["2Deo"].get_active() == True :
                self.graph_gene.graphes[0].dimension = "2Dvo"
            if choix_vect["2Dns"].get_active() == True :
                self.graph_gene.graphes[0].dimension = "2Dva"
        else :
            choix_vect["2Deo"].hide()
            choix_vect["2Dns"].hide()


        if choix_vect["bt_2Dh"].get_active() == True :
            choix_vect["Flg_2D_Waypoints"].show()
            choix_vect["Flg_2D_Fleuves"].show()
            choix_vect["Flg_2D_Dep"].show()
            choix_vect["Flg_2D_Relief"].show()
            choix_vect["Flg_2D_TerreMer"].show()
            self.graph_gene.graphes[0].dimension = "2D"
        else :
            choix_vect["Flg_2D_Waypoints"].hide()
            choix_vect["Flg_2D_Fleuves"].hide()
            choix_vect["Flg_2D_Dep"].hide()
            choix_vect["Flg_2D_Relief"].hide()
            choix_vect["Flg_2D_TerreMer"].hide()


    def ihm_visu1D(self, widget, cadre_vect, choix_acqid, bn_canvas, BarreOutils, cadre_presentation, cadre_zoom, liste_infos) :

        self.graph_gene.type_graphe = "Visu1D"

        for obj in cadre_vect.get_children() :
            cadre_vect.remove(obj)
        cadre_vect.set_label("Choix Vecteurs")

        for obj in cadre_zoom.get_children() :
            cadre_zoom.remove(obj)

        choix_entry = {}
        choix_vecteur = []
        B_choix_vecteur = Gtk.VBox(homogeneous=False, spacing=5)

        B_choix = Gtk.HBox(homogeneous=False, spacing=5)
        B_choix_vecteur.pack_start(B_choix, False, True, 0)
        bouton_parcourir = Gtk.Button()
        bouton_parcourir.set_label('Choix')
#        bouton_parcourir.get_child().modify_font(Pango.FontDescription("sans 8"))
        bouton_parcourir.set_size_request(45, 20)
        label_vecteur = Gtk.Label()
        label_vecteur.set_markup("Param")
        choix_vecteur_tmp = Gtk.Entry()
        choix_vecteur_tmp.set_width_chars(25)
#        choix_vecteur_tmp.modify_font(Pango.FontDescription("sans 9") )
        bouton_clear = Gtk.Button()
        bouton_clear.set_label("Efface")
#        bouton_clear.get_child().modify_font(Pango.FontDescription("sans 8"))

        B_choix.pack_start(bouton_parcourir, False, False, 0)
        B_choix.pack_start(label_vecteur, False, False, 0)
        B_choix.pack_start(choix_vecteur_tmp, False, False, 0)
        B_choix.pack_start(bouton_clear, False, False, 0)
        choix_entry["Vecteur"]=choix_vecteur_tmp
        choix_vecteur.append(choix_vecteur_tmp)
        bouton_parcourir.connect("button-press-event", self.Choix_vecteur_serie_1D, 5, choix_vecteur, 0, choix_acqid)
        bouton_clear.connect("clicked", self.Efface_choix, choix_vecteur_tmp, -1)

        separateur = Gtk.HSeparator()
        B_choix_vecteur.pack_start(separateur, True, False, 0)

        B_Titre = Gtk.VBox(homogeneous=False, spacing=5)
        L_Titre = Gtk.Label()
        L_Titre.set_markup("Titre du graphique.")
        E_Titre = Gtk.Entry()
        B_Titre.pack_start(L_Titre, False, True, 0)
        B_Titre.pack_start(E_Titre, False, True, 0)
        L_SousTitre = Gtk.Label()
        L_SousTitre.set_markup("Sous Titre.")
        E_SousTitre = Gtk.Entry()
        B_Titre.pack_start(L_SousTitre, False, True, 0)
        B_Titre.pack_start(E_SousTitre, False, True, 0)
        B_choix_vecteur.pack_start(B_Titre, False, True, 0)
        choix_entry["Titre"]=E_Titre
        choix_entry["SousTitre"]=E_SousTitre
        if liste_infos != None :
            if liste_infos["Titre"] != "" :
                E_Titre.set_text(liste_infos["Titre"])
            elif self.graph_gene.campagne != "" :
                E_Titre.set_text(self.graph_gene.TitreGraph)
            if liste_infos["SousTitre"] != "" :
                E_SousTitre.set_text(liste_infos["SousTitre"])
            elif self.graph_gene.campagne != "" :
                E_SousTitre.set_text(self.graph_gene.SousTitreGraph)

        cadre_vect.add(B_choix_vecteur)
        cadre_vect.show_all()
        BarreOutils.update()
        bouton_tracer = BarreOutils.get_nth_item(0)
        try:
            bouton_tracer.disconnect(self.graph_gene.B_Tracer_handler_id)
        except TypeError :
            pass

        cadre_presentation.show_all()
        cadre_zoom.show_all()

        self.win_choix_vecteur_serie = 0

        self.graph_gene.B_Tracer_handler_id = bouton_tracer.connect("clicked", adpt.Tracer_visu1D, self, bn_canvas, choix_entry, choix_acqid, cadre_presentation)


    def ihm_dsp(self, widget, cadre_vect, choix_acqid, bn_canvas, BarreOutils, cadre_presentation, cadre_zoom, liste_infos) :

        self.graph_gene.type_graphe = "Dsp"

        for obj in cadre_vect.get_children() :
            cadre_vect.remove(obj)
        cadre_vect.set_label("Choix Vecteurs")

        for obj in cadre_zoom.get_children() :
            cadre_zoom.remove(obj)

        choix_entry = {}
        choix_vecteur = []
        BV_choix_vecteur = Gtk.VBox(homogeneous=False, spacing=5)

        BH_choix = Gtk.HBox(homogeneous=False, spacing=5)
        BV_choix_vecteur.pack_start(BH_choix, False, True, 0)
        bouton_parcourir = Gtk.Button()
        bouton_parcourir.set_label("Choix")
#        bouton_parcourir.get_child().modify_font(Pango.FontDescription("sans 8"))
        bouton_parcourir.set_size_request(45, 20)
        label_vecteur = Gtk.Label()
        label_vecteur.set_markup("Param")
        E_vecteur_tmp = Gtk.Entry()
        E_vecteur_tmp.set_width_chars(15)
#        E_vecteur_tmp.set_size_request(110, 25)
        if liste_infos != None :
            try :
                motcle = "NomVecteur"
                E_vecteur_tmp.set_text(liste_infos[motcle])
            except :
                pass

        bouton_clear = Gtk.Button()
        bouton_clear.set_label("Efface")
#        bouton_clear.get_child().modify_font(Pango.FontDescription("sans 8"))

        BH_choix.pack_start(bouton_parcourir, False, False, 0)
        BH_choix.pack_start(label_vecteur, False, False, 0)
        BH_choix.pack_start(E_vecteur_tmp, False, False, 0)
        BH_choix.pack_start(bouton_clear, False, False, 0)
        choix_vecteur.append(E_vecteur_tmp)
        choix_entry["Vecteur"]=E_vecteur_tmp
        bouton_parcourir.connect("button-press-event", self.Choix_vecteur_serie_1D, 6, choix_vecteur, 0, choix_acqid)
        bouton_clear.connect("clicked", self.Efface_choix, E_vecteur_tmp, -1)

        separateur = Gtk.HSeparator()
        BV_choix_vecteur.pack_start(separateur, True, False, 0)

        BV_Titre = Gtk.VBox(homogeneous=False, spacing=5)
        L_Titre = Gtk.Label()
        L_Titre.set_markup("Titre du graphique.")
        E_Titre = Gtk.Entry()
        E_Titre.set_width_chars(8)
        BV_Titre.pack_start(L_Titre, False, True, 0)
        BV_Titre.pack_start(E_Titre, False, True, 0)
        L_SousTitre = Gtk.Label()
        L_SousTitre.set_markup("Sous Titre.")
        E_SousTitre = Gtk.Entry()
        BV_Titre.pack_start(L_SousTitre, False, True, 0)
        BV_Titre.pack_start(E_SousTitre, False, True, 0)
        BV_choix_vecteur.pack_start(BV_Titre, False, True, 0)
        choix_entry["Titre"]=E_Titre
        choix_entry["SousTitre"]=E_SousTitre
        if liste_infos != None :
            if liste_infos["Titre"] != "" :
                E_Titre.set_text(liste_infos["Titre"])
            elif self.graph_gene.campagne != "" :
                E_Titre.set_text(self.graph_gene.TitreGraph)
            if liste_infos["SousTitre"] != "" :
                E_SousTitre.set_text(liste_infos["SousTitre"])
            elif self.graph_gene.campagne != "" :
                E_SousTitre.set_text(self.graph_gene.SousTitreGraph)

# Choix affichage des sequences
        BV_Sup = Gtk.VBox(homogeneous=False, spacing=5)
        BV_choix_vecteur.pack_start(BV_Sup, False, True, 0)

        C_Dsp = Gtk.CheckButton()
        C_Dsp.set_label("Affichage DSP seul")
        if liste_infos != None :
            if liste_infos["Sequence"] == "1" :
                Dsp.set_active(True)
        BV_Sup.pack_start(C_Dsp, False, True, 0)
        choix_entry["Dsp_seul"]=C_Dsp

        C_droite_dsp = Gtk.CheckButton()
        C_droite_dsp.set_label("Affichage droite pente -5/3")
        if liste_infos != None :
            if liste_infos["Droite_dsp"] == "1" :
                C_droite_dsp.set_active(True)
        BV_Sup.pack_start(C_droite_dsp, False, True, 0)
        choix_entry["Dsp_droite"]=C_droite_dsp

        cadre_vect.add(BV_choix_vecteur)
        cadre_vect.show_all()
        BarreOutils.update()
        bouton_tracer = BarreOutils.get_nth_item(0)
        try:
            bouton_tracer.disconnect(self.graph_gene.B_Tracer_handler_id)
        except TypeError :
            pass

        cadre_presentation.show_all()
        cadre_zoom.show_all()

        self.win_choix_vecteur_serie = 0

        self.graph_gene.B_Tracer_handler_id = bouton_tracer.connect("clicked", adpt.Tracer_dsp, self, bn_canvas, choix_entry, choix_acqid, cadre_presentation)


    def ihm_serie(self, widget, cadre_vect, choix_acqid, bn_canvas, BarreOutils, cadre_presentation, cadre_zoom, liste_infos) :
        trace=0

        self.graph_gene.type_graphe = "SerieTempo"
        if liste_infos == None :
            for ng in  npy.arange(6) :
                del self.graph_gene.graphes[0]
            self.graph_gene.nb_graphe = 0

            for nb in npy.arange(6) :
                Graphe = graphe ()
                self.graph_gene.graphes.append(Graphe)

        for obj in cadre_vect.get_children() :
            cadre_vect.remove(obj)
        cadre_vect.set_label("Choix Vecteurs")

        for obj in cadre_zoom.get_children() :
            cadre_zoom.remove(obj)

        choix_entry = {}
        choix_vecteur = []
        choix_bornes = []
        B_choix_vecteur = Gtk.VBox(homogeneous=False, spacing=5)

        for i in npy.arange(6) :
            B_choix = Gtk.HBox(homogeneous=False, spacing=5)
            B_choix_vecteur.pack_start(B_choix, False, True, 0)
            bouton_parcourir = Gtk.Button()
            bouton_parcourir.set_label("Choix")
#            bouton_parcourir.get_child().modify_font(Pango.FontDescription("sans 8"))
#            bouton_parcourir.set_size_request(45, 20)
            E_vecteur_tmp = Gtk.Entry()
            E_vecteur_tmp.connect("activate", init_champ_meta,self.graph_gene,i)
            E_vecteur_tmp.set_width_chars(20)
            E_vecteur_tmp.set_text("")
#            E_vecteur_tmp.modify_font(Pango.FontDescription("sans 9") )
            if liste_infos != None :
                try :
                    motcle = "NomVecteur" + str(i+1)
                    E_vecteur_tmp.set_text(liste_infos[motcle])
                    trace=0
                except :
                    pass
                if liste_infos["Titre"] == "Non" :
                    liste_infos = None
            bouton_clear = Gtk.Button()
            bouton_clear.set_label("Efface")
#            bouton_clear.get_child().modify_font(Pango.FontDescription("sans 8"))

            B_choix.pack_start(bouton_parcourir, False, True, 0)
            B_choix.pack_start(E_vecteur_tmp, False, False, 0)
            B_choix.pack_start(bouton_clear, False, True, 0)
            choix_vecteur.append(E_vecteur_tmp)
            cle = "Vecteur" + str(i)
            choix_entry[cle] = E_vecteur_tmp
            bouton_parcourir.connect("button-press-event", self.Choix_vecteur_serie_1D, 1, choix_vecteur, i, choix_acqid)
            bouton_clear.connect("clicked", self.Efface_choix, E_vecteur_tmp, -1)

        separateur = Gtk.HSeparator()
        B_choix_vecteur.pack_start(separateur, True, False, 0)


# Creation d'un gradateur horizontal pout choisir le nombre de
# graphes par pages.
        B_NbGraphePage = Gtk.HBox(homogeneous=False, spacing=5)
        B_choix_vecteur.pack_start(B_NbGraphePage, False, False, 0)

        etiquette = Gtk.Label()
        etiquette.set_markup("Nb graphes par page :")
        B_NbGraphePage.pack_start(etiquette, False, False, 0)

        try :
            Adj_nbGraphePage = Gtk.Adjustment(value=float(self.graph_gene.nb_graphe_par_page), \
                    lower=1.0, upper=6.0, step_increment=1.0, page_increment=1.0, page_size=0.0)
        except :
            Adj_nbGraphePage = Gtk.Adjustment(value=6.0 ,lower=1.0, upper=6.0, \
                    step_increment=1.0, page_increment=1.0, page_size=0.0)

        Adj_nbGraphePage.connect("value_changed", self.modif_NbGraphePage)
        gradateur = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Adj_nbGraphePage)
        gradateur.set_digits(0)
        B_NbGraphePage.pack_start(gradateur, True, True, 0)

# Creation d'un combo pour choix de type de graphe si dim_array > 1
        B_TypeGrapheArray = Gtk.HBox(homogeneous=False, spacing=5)
        B_choix_vecteur.pack_start(B_TypeGrapheArray, False, False, 0)

        combolabel = Gtk.Label()
        combolabel.set_markup("Graphes multidimensionels :")
#        combo = Gtk.ComboBoxText()
        combo = Gtk.ComboBoxText()
        combo.append_text('Cumul')
        combo.append_text('Superposition')
        combo.append_text('Image')
        combo.append_text('Profil')
#        combo.append_text('Coupe')
        if self.graph_gene.Type_graphe_serie == 'Superposition' :
            combo.set_active(1)
        elif self.graph_gene.Type_graphe_serie == 'Image' :
            combo.set_active(2)
        elif self.graph_gene.Type_graphe_serie == 'Profil' :
            combo.set_active(3)
        else :
            combo.set_active(0)

        B_TypeGrapheArray.pack_start(combolabel, False, False, 0)
        B_TypeGrapheArray.pack_start(combo, False, False, 0)

        B_BornesProfil = Gtk.HBox(homogeneous=False, spacing=5)
        B_choix_vecteur.pack_start(B_BornesProfil, False, False, 0)
        L_minProfil = Gtk.Label()
        L_minProfil.set_markup("Cmap min :")
        E_minProfil = Gtk.Entry()
#        E_minProfil.set_size_request(20, 25)
        E_minProfil.set_width_chars(8)
        choix_bornes.append(E_minProfil)
        E_minProfil.connect("activate", change_champ_entry, self, 0)
        if self.graph_gene.minProfil != -999 :
            try :
                E_minProfil.set_text(str(self.graph_gene.minProfil))
            except :
                E_minProfil.set_text("Auto")
        else :
            E_minProfil.set_text("Auto")

        L_maxProfil = Gtk.Label()
        L_maxProfil.set_markup("Cmap max :")
        E_maxProfil = Gtk.Entry()
#        E_maxProfil.set_size_request(50, 25)
        E_maxProfil.set_width_chars(8)
        choix_bornes.append(E_maxProfil)
        E_maxProfil.connect("activate", change_champ_entry, self, 1)
        if self.graph_gene.maxProfil != -999 :
            try :
                E_maxProfil.set_text(str(self.graph_gene.maxProfil))
            except :
                E_maxProfil.set_text("Auto")
        else :
            E_maxProfil.set_text("Auto")

        B_BornesProfil.pack_start(L_minProfil, False, True, 0)
        B_BornesProfil.pack_start(E_minProfil, False, True, 0)
        B_BornesProfil.pack_start(L_maxProfil, False, True, 0)
        B_BornesProfil.pack_start(E_maxProfil, False, True, 0)
        B_BornesProfil.hide()
        combo.connect('changed', self.changed_presentation_serie, B_BornesProfil)


        separateur = Gtk.HSeparator()
        B_choix_vecteur.pack_start(separateur, True, False, 0)

# Creation d'une de saisie pour le titre
        B_Titre = Gtk.VBox(homogeneous=False, spacing=5)
        L_Titre = Gtk.Label()
        L_Titre.set_markup("Titre du graphique")
        E_Titre = Gtk.Entry()
        B_Titre.pack_start(L_Titre, False, True, 0)
        B_Titre.pack_start(E_Titre, False, True, 0)
        L_SousTitre = Gtk.Label()
        L_SousTitre.set_markup("Sous Titre.")
        E_SousTitre = Gtk.Entry()
        B_Titre.pack_start(L_SousTitre, False, True, 0)
        B_Titre.pack_start(E_SousTitre, False, True, 0)
        B_choix_vecteur.pack_start(B_Titre, False, True, 0)
        choix_entry["Titre"] = E_Titre
        choix_entry["SousTitre"] = E_SousTitre
        if liste_infos != None :
            if liste_infos["Titre"] != "" :
                E_Titre.set_text(liste_infos["Titre"])
            elif self.graph_gene.campagne != "" :
                E_Titre.set_text(self.graph_gene.TitreGraph)
            if liste_infos["SousTitre"] != "" :
                E_SousTitre.set_text(liste_infos["SousTitre"])
            elif self.graph_gene.campagne != "" :
                E_SousTitre.set_text(self.graph_gene.SousTitreGraph)

        separateur = Gtk.HSeparator()
        B_choix_vecteur.pack_start(separateur, True, False, 0)

# Choix affichage des tops
        B_Top = Gtk.VBox(homogeneous=False, spacing=5)
#        C_Top = Gtk.CheckButton()
#        C_Top.set_label("Affichage tops")
#        if liste_infos != None :
#            if liste_infos["Top"] == "1" :
#                C_Top.set_active(True)
#        B_Top.pack_start(C_Top, False, True, 0)
        B_choix_vecteur.pack_start(B_Top, False, True, 0)

# Choix affichage des sequences
        C_Seq = Gtk.CheckButton()
        C_Seq.set_label("Affichage des sequences")
        if liste_infos != None :
            if liste_infos["Sequence"] == "1" :
                C_Seq.set_active(True)
        B_Top.pack_start(C_Seq, False, True, 0)
        choix_entry["Sequence"] = C_Seq

        BarreOutils.update()
        bouton_tracer = BarreOutils.get_nth_item(0)
        try:
            bouton_tracer.disconnect(self.graph_gene.B_Tracer_handler_id)
        except TypeError :
            pass

        self.win_choix_vecteur_serie = 0

        bt_Top = Gtk.ToggleButton()
        image = Gtk.Image()
        AH = os.getenv('AIDA_HOME')
        basedir = os.path.join(AH, 'share/aidaplot/Bitmaps')
        image.set_from_file(basedir+"/top.jpeg")
        bt_Top.add(image)
        E_Top = Gtk.Entry()
        E_Top.set_width_chars(15)
        try :
            E_Top.set_text(self.graph_gene.graphes[0].vect_Top)
        except :
            print ("Pas d'affichage des tops ")
        B_Top.pack_start(bt_Top, False, True, 0)
        B_Top.pack_start(E_Top, False, True, 0)
        choix_entry["Tops"] = E_Top
        bt_Top.connect("button-press-event", self.ihm_Choix_Sup_vecteur, E_Top, choix_acqid, "Top")


        cadre_vect.add(B_choix_vecteur)
        cadre_vect.show_all()
        cadre_presentation.show_all()
        cadre_zoom.show_all()
        if self.graph_gene.Type_graphe_serie != 'Profil' or self.graph_gene.Type_graphe_serie != 'Image':
            B_BornesProfil.hide()

        if trace == 1 :
            adpt.Tracer_serie(None,self, bn_canvas, choix_entry, choix_bornes, choix_acqid, cadre_presentation)
        self.graph_gene.B_Tracer_handler_id = bouton_tracer.connect("clicked", adpt.Tracer_serie, self, bn_canvas, choix_entry, choix_bornes, choix_acqid, cadre_presentation)

    def modif_NbGraphePage(self, adjust) :
        self.graph_gene.nb_graphe_par_page = int(adjust.get_value())

    def ihm_sondage(self, widget, cadre_vect, choix_acqid, bn_canvas, BarreOutils, cadre_presentation, cadre_zoom, liste_infos) :

        self.graph_gene.type_graphe = "Sondage"
        if liste_infos == None :
            for ng in  npy.arange(6) :
                del self.graph_gene.graphes[0]
            self.graph_gene.nb_graphe = 0

            for nb in npy.arange(6) :
                Graphe = graphe ()
                self.graph_gene.graphes.append(Graphe)

        L_sond = ["Pression", "Temperature", "Tprim", "Trosee", "dd ou u", "ff ou v"]
        Titre_sond = ["NomVecteurY", "NomVecteurX", "NomVecteurTM", "NomVecteurTd", "NomVecteurV1", "NomVecteurV2"]

        for obj in cadre_vect.get_children() :
            cadre_vect.remove(obj)
        cadre_vect.set_label("Choix Vecteurs")

        for obj in cadre_zoom.get_children() :
            cadre_zoom.remove(obj)

        choix_vecteur = []
        choix_entry = {}
        boite_choix_vecteur = Gtk.VBox(homogeneous=False, spacing=5)

        for i in npy.arange(6) :
            boite_choix = Gtk.HBox(homogeneous=False, spacing=5)
            boite_choix_vecteur.pack_start(boite_choix, False, True, 0)
            bouton_parcourir = Gtk.Button()
            bouton_parcourir.set_label("Choix")
            bouton_parcourir.set_size_request(45, 20)
            label_vecteur = Gtk.Label()
            label_vecteur.set_markup(L_sond[i])
            E_vecteur_tmp = Gtk.Entry()
            E_vecteur_tmp.connect("activate", init_champ_meta,self.graph_gene,i)
            E_vecteur_tmp.set_width_chars(8)
            if liste_infos != None  :
                try :
                    E_vecteur_tmp.set_text(liste_infos[Titre_sond[i]])
                except :
                    pass
            bouton_clear = Gtk.Button()
            bouton_clear.set_label("Efface")

            boite_choix.pack_start(bouton_parcourir, False, False, 0)
            boite_choix.pack_start(label_vecteur, False, False, 0)
            boite_choix.pack_end(bouton_clear, False, False, 0)
            boite_choix.pack_end(E_vecteur_tmp, False, False, 0)
            cle = "Vecteur" + str(i)
            choix_entry[cle] = E_vecteur_tmp
            choix_vecteur.append(E_vecteur_tmp)
            bouton_parcourir.connect("clicked", self.Choix_vecteurs_sondage, 1, choix_vecteur, i, choix_acqid)
            bouton_clear.connect("clicked", self.Efface_choix, E_vecteur_tmp, -1)

        separateur = Gtk.HSeparator()
        boite_choix_vecteur.pack_start(separateur, True, False, 0)

        B_Titre = Gtk.VBox(homogeneous=False, spacing=5)
        L_Titre = Gtk.Label()
        L_Titre.set_markup("Titre du graphique")
        E_Titre = Gtk.Entry()
        B_Titre.pack_start(L_Titre, False, True, 0)
        B_Titre.pack_start(E_Titre, False, True, 0)
        L_SousTitre = Gtk.Label()
        L_SousTitre.set_markup("Sous Titre.")
        E_SousTitre = Gtk.Entry()
        B_Titre.pack_start(L_SousTitre, False, True, 0)
        B_Titre.pack_start(E_SousTitre, False, True, 0)
        boite_choix_vecteur.pack_start(B_Titre, False, True, 0)
        choix_entry["Titre"] = E_Titre
        choix_entry["SousTitre"]=E_SousTitre
        if liste_infos != None :
            if liste_infos["Titre"] != "" :
                E_Titre.set_text(liste_infos["Titre"])
            elif self.graph_gene.campagne != "" :
                E_Titre.set_text(self.graph_gene.TitreGraph)
            if liste_infos["SousTitre"] != "" :
                E_SousTitre.set_text(liste_infos["SousTitre"])
            elif self.graph_gene.campagne != "" :
                E_SousTitre.set_text(self.graph_gene.SousTitreGraph)

        cadre_vect.add(boite_choix_vecteur)
        cadre_vect.show_all()
        BarreOutils.update()
        bouton_tracer = BarreOutils.get_nth_item(0)
        try:
            bouton_tracer.disconnect(self.graph_gene.B_Tracer_handler_id)
        except TypeError :
            pass

        cadre_presentation.show_all()
        cadre_zoom.show_all()

        self.graph_gene.B_Tracer_handler_id = bouton_tracer.connect("clicked", adpt.Tracer_emagramme, self, bn_canvas, choix_entry, choix_acqid, cadre_presentation)

    def ihm_XY(self, widget, cadre_vect, choix_acqid, bn_canvas, BarreOutils, cadre_presentation, cadre_zoom, liste_infos) :

        self.graph_gene.type_graphe = "Plot_XY"
        self.ihm_choix_vecteurs = None
        if liste_infos == None :
            for ng in  npy.arange(6) :
                del self.graph_gene.graphes[0]
            self.graph_gene.nb_graphe = 0

            for nb in npy.arange(6) :
                Graphe = graphe ()
                self.graph_gene.graphes.append(Graphe)

        for obj in cadre_vect.get_children() :
            cadre_vect.remove(obj)

        for obj in cadre_zoom.get_children() :
            cadre_zoom.remove(obj)

        choix_entry = {}
        choix_vecteurs = []
        B_choix_vecteur = Gtk.VBox(homogeneous=False, spacing=5)

        for i in npy.arange(6) :
            B_choix = Gtk.HBox(homogeneous=False, spacing=5)
            B_choix_vecteur.pack_start(B_choix, False, True, 0)
            bouton_parcourir = Gtk.Button()
            bouton_parcourir.set_label("Choix ")
#            bouton_parcourir.get_child().modify_font(Pango.FontDescription("sans 8"))
#            bouton_parcourir.set_size_request(45, 20)
            label_vecteur = Gtk.Label()
            label_vecteur.set_markup("X")
            E_choix_vecteur_X = Gtk.Entry()
            E_choix_vecteur_X.set_width_chars(20)
            E_choix_vecteur_X.connect("activate", init_champ_meta,self.graph_gene,2*i)
#            E_choix_vecteur_X.set_width_chars(25)
#            E_choix_vecteur_X.modify_font(Pango.FontDescription("sans 9") )
            bouton_parcourir.connect("clicked", self.Choix_vecteurs_XY2, choix_vecteurs, i, choix_acqid, bn_canvas)
            B_choix.pack_start(bouton_parcourir, False, True, 0)
            B_choix.pack_start(label_vecteur, False, True, 0)
            B_choix.pack_start(E_choix_vecteur_X, False, True, 0)
            choix_vecteurs.append(E_choix_vecteur_X)
            choix_entry["VecteurX"] = E_choix_vecteur_X

            B_choix = Gtk.HBox(homogeneous=False, spacing=5)
            B_choix_vecteur.pack_start(B_choix, False, True, 0)
            bouton_clear = Gtk.Button()
            bouton_clear.set_label("Efface")
#            bouton_clear.get_child().modify_font(Pango.FontDescription("sans 8"))
#            bouton_clear.set_size_request(45, 20)
            label_vecteur = Gtk.Label()
            label_vecteur.set_markup("Y")
            E_choix_vecteur_Y = Gtk.Entry()
            E_choix_vecteur_Y.connect("activate", init_champ_meta,self.graph_gene,2*i+1)
            E_choix_vecteur_Y.set_width_chars(20)
#            E_choix_vecteur_Y.modify_font(Pango.FontDescription("sans 9") )
            B_choix.pack_start(bouton_clear, False, False, 0)
            B_choix.pack_start(label_vecteur, False, False, 0)
            B_choix.pack_start(E_choix_vecteur_Y, False, False, 0)
            choix_entry[E_choix_vecteur_X] = E_choix_vecteur_Y
            choix_vecteurs.append(E_choix_vecteur_Y)
            bouton_clear.connect("clicked", self.Efface_choix, choix_vecteurs, i)

            if liste_infos != None :
                try:
                    motcle = "NomVecteurX_" + str(i)
                    E_choix_vecteur_X.set_text(liste_infos[motcle])
                    motcle = "NomVecteurY_" + str(i)
                    E_choix_vecteur_Y.set_text(liste_infos[motcle])
                except :
                    continue
            separateur = Gtk.HSeparator()
            B_choix_vecteur.pack_start(separateur, True, False, 0)

        separateur = Gtk.HSeparator()
        B_choix_vecteur.pack_start(separateur, True, False, 0)

        B_Titre = Gtk.VBox(homogeneous=False, spacing=5)
        L_Titre = Gtk.Label()
        L_Titre.set_markup("Titre du graphique")
        E_Titre = Gtk.Entry()
        B_Titre.pack_start(L_Titre, False, True, 0)
        B_Titre.pack_start(E_Titre, False, True, 0)
        L_SousTitre = Gtk.Label()
        L_SousTitre.set_markup("Sous Titre.")
        E_SousTitre = Gtk.Entry()
        B_Titre.pack_start(L_SousTitre, False, True, 0)
        B_Titre.pack_start(E_SousTitre, False, True, 0)
        B_choix_vecteur.pack_start(B_Titre, False, True, 0)
        choix_entry["Titre"] = E_Titre
        choix_entry["SousTitre"]=E_SousTitre
        if liste_infos != None :
            if liste_infos["Titre"] != "" :
                E_Titre.set_text(liste_infos["Titre"])
            elif self.graph_gene.campagne != "" :
                E_Titre.set_text(self.graph_gene.TitreGraph)
            if liste_infos["SousTitre"] != "" :
                E_SousTitre.set_text(liste_infos["SousTitre"])
            elif self.graph_gene.campagne != "" :
                E_SousTitre.set_text(self.graph_gene.SousTitreGraph)

        cadre_vect.add(B_choix_vecteur)
        cadre_vect.show_all()
        cadre_zoom.show_all()

        BarreOutils.update()
        bouton_tracer = BarreOutils.get_nth_item(0)
        try:
            bouton_tracer.disconnect(self.graph_gene.B_Tracer_handler_id)
        except TypeError :
            print (" ")

        self.graph_gene.B_Tracer_handler_id = bouton_tracer.connect("clicked", adpt.Tracer_XY, self, bn_canvas, choix_entry, choix_acqid, cadre_presentation)


    def path_TO_acqid(self, platf, an, per):
        """ Renvoie l identifiant acq_id en fonction du repertoire de depot
        """

        abrv = ""
        acq_id = ""
        AH = os.getenv('AIDA_HOME')
        PROFIL=os.getenv('AIDA_PROFIL', '')
        path = os.path.join(AH, "profils", PROFIL, "plate-formes")
        cfg = ConfigParser.ConfigParser()
        cfg.read(path, encoding='ISO8859-15')
        for section in cfg.sections():
            if  platf == section :
                abrv = cfg.get(section, 'abrev')
                break

        acq_id = abrv + an[2:4] + per
        return acq_id

    def Parcourir_dir(self, widget, champsaisie, F_pres):
        REP_DATA = os.getenv('AIDA_DATA')
        if REP_DATA is None :
            AH = os.getenv('AIDA_HOME')
            REP_DATA = os.path.join(AH, 'data')
        REP_OK = False
        
        dialogue = Gtk.FileChooserDialog(title="Sélectionez répertoire", parent=None, action=Gtk.FileChooserAction.SELECT_FOLDER)
        dialogue.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        dialogue.set_current_folder(REP_DATA)

        while REP_OK == False :
            reponse = dialogue.run()
            if reponse == Gtk.ResponseType.OK:
                rep = dialogue.get_filename().split("/")
                PER = rep[len(rep)-1]
                AN = rep[len(rep)-2]
                PLAT = rep[len(rep)-3]
                acqid = self.path_TO_acqid(PLAT, AN, PER)
                try :
                    acq_meta = AIDA.Inf(acqid)
                    vect = dialogue.get_filename()[len(dialogue.get_current_folder())+1: len(dialogue.get_filename())-4]
                    champsaisie.set_text(acqid)
                    self.recup_fic_inf(champsaisie, F_pres, self)
                    REP_OK = True
                except :
                    message = "Attention Acqid non valid !"
                    Abandon(message, Gtk.MessageType.ERROR)
            elif reponse == Gtk.ResponseType.CANCEL:
                print ('Attention, pas de fichier selectionné.')
                REP_OK = True
        dialogue.destroy()

    def Efface_choix(self, widget, champsaisie, ind):
        if ind >= 0 :
            self.graph_gene.graphes[ind].vecteur_X = ''
            self.graph_gene.graphes[ind].vecteur_Y = ''
            champsaisie[2*ind].set_text("")
            champsaisie[2*ind+1].set_text("")
        else :
            champsaisie.set_text('')

    def reset_cb(self, selection, champ, ind, combobox, fltrmod, mrft):

# Recherche du numero courbe demande
        model = combobox.get_model()
        index = combobox.get_active()
        if index >= 0:
            indg = int(model[index][0]) -1
        else :
            indg = ind
            if indg >= 10 :
                indg = indg -10

# Recherche indice du vecteur demande
        if ind > 20 :
            indice = 0
            indg = 0
        elif ind >= 10 :
            if ind % 2 == 0 :
                indice = 2 * indg
            else :
                indice = 2 * indg + 1
        else :
            indice = indg

# Mise a jour de la liste des vecteurs (avec le meme rft_time)
        del mrft[:]

        for rft in self.list_reftime[:] :
            mrft.append(rft)

        fltrmod.refilter()

    def valid_selection_vecteurs_1D(self, btn, champ, etiq_info, typ_filter, win) :

        if typ_filter == 1 :
            nb_graphe = 6
        elif typ_filter < 5 :
            nb_graphe = 3
        else :
            nb_graphe = 1

        for ng in npy.arange(nb_graphe) :
            t_vect_eti = etiq_info[ng].get_text()
            list_vecteurs = t_vect_eti.replace("\n"," ")
            champ[ng].set_text(list_vecteurs)
            if typ_filter == 1 :
                self.graph_gene.graphes[ng].vecteur_Y = list_vecteurs
            elif typ_filter == 4 :
                if list_vecteurs.startswith("alt") :
                    self.graph_gene.graphes[0].vecteur_Z = list_vecteurs
                elif list_vecteurs.lower().startswith("pos_lon"):
                    self.graph_gene.graphes[0].vecteur_X = list_vecteurs
                elif list_vecteurs.lower().startswith("pos_lat") :
                    self.graph_gene.graphes[0].vecteur_Y = list_vecteurs

        if win != None :
            self.win_choix_vecteur_serie = 0
            win.destroy()

    def quite_config_vecteurs_1D(self, EventB, selection, champs, win) :

        t_vect_eti = ''
# Recherche vecteur selectionne
        tv = selection.get_tree_view()
        model = tv.get_model()
        iter1 = model.get_iter_first()
        for p_pt in  npy.arange(len(model)) :
            vect = model.get_value(iter1, 0)
            if t_vect_eti == '' :
                t_vect_eti = vect
            else :
                t_vect_eti = t_vect_eti +'\n'+vect

            try :
                iter1 = model.iter_next(iter1)
            except TypeError:
                return

        champs.set_text(t_vect_eti)
        win.destroy()


    def selection_sup(self, selection, chx, champ):
# Recherche vecteur selectionne
        tv = selection.get_tree_view()
        model = tv.get_model()
        sel = selection.get_selected_rows()
        if sel:
            model, Path = sel
            try :
                for p_pt in Path :
                    p_iter = model.get_iter(p_pt)
                    vect = model.get_value(p_iter, 0)
                    champ.set_text(vect)
                    if int(chx) == 1 :
                        self.graph_gene.graphes[0].vect_sup_vent1 = vect
                    elif int(chx) == 2 :
                        self.graph_gene.graphes[0].vect_sup_vent2 = vect
                    elif int(chx) == 3 :
                        self.graph_gene.graphes[0].vect_sup_texte = vect
                    elif int(chx) == 4 :
                        self.graph_gene.vect_sup_top = vect
                    else :
                        self.graph_gene.graphes[0].vect_sup_indic
            except TypeError:
                return


    def selection_cb(self, selection, champ, ind, combobox, fltrmod, mrft, E_equa):

# Recherche du numero courbe demande
        if combobox != None :
            model = combobox.get_model()
            index = combobox.get_active()
        else :
            index = -1

        if index >= 0:
            try :
                indg = int(model[index][0]) -1
            except :
                if model[index][0] == "Latitude" : indg = 0
                elif model[index][0] == "Longitude" : indg = 1
                elif model[index][0] == "Altitude" : indg = 2
        else :
            indg = ind
            if indg >= 10 :
                indg = indg -10
            if indg >= 10 :
                indg = indg -10

# Recherche indice du vecteur demande
        if ind >= 30 :
            indice = ind - 30
            indg = 0
        elif ind > 20 :
            indice = 0
            indg = 0
        elif ind >= 10 :
            if ind % 2 == 0 :
                indice = 2 * indg
            else :
                indice = 2 * indg + 1
        else :
            indice = indg

# Recherche vecteur selectionne
        tv = selection.get_tree_view()
        model = tv.get_model()
        sel = selection.get_selected_rows()
        vect = ''

        if sel:
            model, Path = sel
            try :
                if self.type_choix_serie == 'direct' :
                    champ[indice].set_text('')
                for p_pt in Path :
                    p_iter = model.get_iter(p_pt)
                    vect = model.get_value(p_iter, 0)
                    if mrft != None :
                        rft_time  = model.get_value(p_iter, 1)
# remplissage ihm avec nom vecteur

                    if self.type_choix_serie == 'direct' :
                        champ[indice].set_text(vect)

                        if ind < 10 or (ind < 20 and ind%2 == 1) or ind == 30 :
                            self.graph_gene.graphes[indg].vecteur_Y = vect
                        elif (ind < 20 and ind%2 == 0) or ind == 31 :
                            self.graph_gene.graphes[indg].vecteur_X = vect
                        elif ind == 32 :
                            self.graph_gene.graphes[indg].vecteur_TM = vect
                        elif ind == 33 :
                            self.graph_gene.graphes[indg].vecteur_TD = vect
                        elif ind == 34 :
                            self.graph_gene.graphes[indg].vecteur_V1 = vect
                        elif ind == 35 :
                            self.graph_gene.graphes[indg].vecteur_V2 = vect
                    else :
                        t_vect_eti = E_equa.get_text()
                        if t_vect_eti == '' :
                            t_vect_eti = vect
                        else :
                            if t_vect_eti[-1] in ["-", "+", "*", "/"] :
                                t_vect_eti = t_vect_eti + vect
                            else :
                                message = "Inserer un operateur (+ - * ou /) entre 2 vecteurs ou effacer pour nouvelle opération."
                                Abandon(message, Gtk.MessageType.ERROR)
                        E_equa.set_text(t_vect_eti)

            except TypeError:
                print("ERREUR")
                return
        nbg = 0
        for i in npy.arange(6) :
            if ind < 10 and self.graph_gene.graphes[i].vecteur_Y != '' :
                nbg = nbg + 1
            if ind >= 10 and self.graph_gene.graphes[i].vecteur_Y != ''  and self.graph_gene.graphes[i].vecteur_X != '' :
                nbg = nbg + 1
        self.graph_gene.nb_graphe = nbg

# Mise a jour de la liste des vecteurs (avec le meme rft_time)
        if mrft != None :
            try :
                del mrft[:]
                if rft_time != " " :
                    mrft.append(rft_time)
                    if rft_time in self.dict_link_time :
                        mrft.append(self.dict_link_time[rft_time])
                    mrft.append(" ")
                else :
                    for rft in self.list_reftime[:] :
                        mrft.append(rft)

                if len(mrft) > 0 :
                    fltrmod.set_visible_func(self.visible_cb, mrft)

                fltrmod.refilter()
            except :
                pass


    def efface_equation(self, selection, E_equa):
        E_equa.set_text("")

    def valid_operation_XY(self, selection, E_equa, liste_fic, fltrmod_X, fltrmod_Y):

        acqid = self.graph_gene.acqid
        t_oper = E_equa.get_text()

# test operation et recherche vecteur temps
        liste_elem = re.split('[+-\/\*]', t_oper)
        vector_time = ""
        for elem in liste_elem :
            try :
                data = adpt.read_vect(acqid, elem, attributes_only = True, alarme = 0)
                vector_time = data.attributes["ref_time"]
                pass
            except :
                continue
        self.graph_gene.vecteurs_operations[t_oper] = vector_time

#        fltrmod_Y.clear()
        Iter = fltrmod_Y.append()
        fltrmod_Y.set(Iter, 0, "")

        liste_data_sort = sorted(list(self.graph_gene.vecteurs_operations.keys()), key = str.lower)
        for fic in  liste_data_sort :
            Iter = fltrmod_X.insert(1)
            fltrmod_X.set(Iter, 0, fic, 1, vector_time)
            Iter = fltrmod_Y.append()
            fltrmod_Y.set(Iter, 0, fic)

        liste_data_sort = sorted(liste_fic, key = str.lower)
        for fic in liste_data_sort :
            if len(fic) < 5 :
                continue
            Iter = fltrmod_Y.append()
            fltrmod_Y.set(Iter, 0, fic[0:len(fic)-4])

    def valid_operation(self, selection, etiq_info, l_button, E_equa, liste_fic, fltrmod):

        for np in npy.arange(len(l_button)) :
            if  l_button[np].get_active() :
                index = np

        acqid = self.graph_gene.acqid
        t_oper = E_equa.get_text()

# test operation et recherche vecteur temps
        liste_elem = re.split('[+-\/\*]', t_oper)
        vector_time = ""
        for elem in liste_elem :
            try :
                data = adpt.read_vect(acqid, elem, attributes_only = True, alarme = 0)
                vector_time = data.attributes["ref_time"]
                pass
            except :
                continue
        self.graph_gene.vecteurs_operations[t_oper] = vector_time

        t_vect_eti =  etiq_info[index].get_text()
#    t_oper.replace(' ', '')
        if t_vect_eti != "" :
            if t_oper != "" :
                t_total = t_vect_eti + '\n' + t_oper
            else :
                t_total = t_vect_eti
        else :
            t_total = t_oper

        etiq_info[index].set_text(t_total)
        E_equa.set_text(" ")

#        fltrmod.clear()
        Iter = fltrmod.append()
        fltrmod.set(Iter, 0, "")

        liste_data_sort = sorted(list(self.graph_gene.vecteurs_operations.keys()), key = str.lower)
        for fic in  liste_data_sort :
            Iter = fltrmod.append()
            fltrmod.set(Iter, 0, fic)

        liste_data_sort = sorted(liste_fic, key = str.lower)
        for fic in liste_data_sort :
            if len(fic) < 5 :
                continue
            Iter = fltrmod.append()
            fltrmod.set(Iter, 0, fic[0:len(fic)-4])


    def maj_selection_cb(self, selection, etiq_info, l_button, E_equa):

        for np in npy.arange(len(l_button)) :
            if  l_button[np].get_active() :
                index = np

        if self.type_choix_serie == 'direct' :
            t_vect_eti = ''
        else :
            t_vect_eti = E_equa.get_text()

# Recherche vecteur selectionne
        tv = selection.get_tree_view()
        model = tv.get_model()
        sel = selection.get_selected_rows()
        if sel:
            model, Path = sel
            if Path == [] :
                return
            try :
                for p_pt in Path :
                    p_iter = model.get_iter(p_pt)
                    vect = model.get_value(p_iter, 0)

                    if t_vect_eti == '' :
                        t_vect_eti = vect
                    else :
                        if self.type_choix_serie == 'direct' :
                            t_vect_eti = t_vect_eti +'\n'+vect
                        else :
                            if t_vect_eti[-1] in ["-", "+", "*", "/", " "] :
                                t_vect_eti = t_vect_eti +vect
                            else :
                                message = "Inserer un operateur (+ - * ou /) entre 2 vecteurs ou effacer pour nouvelle opération."
                                Abandon(message, Gtk.MessageType.ERROR)

            except TypeError:
                return
            if self.type_choix_serie == 'direct' :
                etiq_info[index].set_text(t_vect_eti)
            else :
                E_equa.set_text(t_vect_eti)


    def filtre_vecteur(self, widget, selectX, list_fic, fltrmod, E_regex, type_filt, l_button):

        if  type_filt == 1 or type_filt == 6 :
            liste_data = list_fic
        elif type_filt < 5 :
            for nb in npy.arange(len(l_button)) :
                if l_button[nb].get_active() == True :
                    ind = nb
            if ind == 2 :
                liste_data = [f for f in list_fic if f.startswith("alt")]
            if ind == 1 :
                liste_data = [f for f in list_fic if f.lower().startswith("pos_lon") ]
            if ind == 0 :
                liste_data = [f for f in list_fic if  f.lower().startswith("pos_lat") ]

        regex = E_regex.get_text()
        if regex != "" :
            lst_regex = regex.split("*")

            deb_regex = lst_regex[0]
            if len(lst_regex) == 1 :
                fin_regex = lst_regex[0]+".vbn"
            elif len(lst_regex) == 2 :
                fin_regex = lst_regex[1]+".vbn"
            elif len(lst_regex) == 3 :
                mil_regex = lst_regex[1]
                fin_regex = lst_regex[2]+".vbn"

            liste_data2 = [f for f in liste_data if f.startswith(deb_regex)]
            liste_data3 = [f for f in liste_data2 if f.endswith(fin_regex)]
            if len(lst_regex) == 3 :
                liste_data4 = [f for f in liste_data3 if mil_regex in f ]
            else :
                liste_data4 = liste_data3
        else :
            liste_data4 = list_fic

        liste_data_sort = sorted(liste_data4, key = str.lower)
        fltrmod.clear()
        for fic in liste_data_sort :
            Iter = fltrmod.append()
            fltrmod.set(Iter, 0, fic[0:len(fic)-4])

    def change_choix_courbes_1D(self, button_actif, select, list_fic, lststore, etiq_info, l_button):
        nbv = 0
        nbx = []

        if button_actif.get_active() == False :
            return

        if  len(etiq_info) == 3 :
            if l_button == 3 :
                liste_data = [f for f in list_fic if f.startswith("alt")]
            if l_button == 2 :
                liste_data = [f for f in list_fic if f.lower().startswith("pos_lon")]
            if l_button == 1 :
                liste_data = [f for f in list_fic if f.lower().startswith("pos_lat")]
            liste_data_sort = sorted(liste_data, key = str.lower)
            lststore.clear()
            for fic in liste_data_sort :
                Iter = lststore.append()
                lststore.set(Iter, 0, fic[0:len(fic)-4])
        else :
            liste_data_sort = sorted(list_fic, key = str.lower)


        index = l_button - 1
        t_vect_eti = etiq_info[index].get_text()

        list_vecteurs = t_vect_eti.split("\n")
        if len(list_vecteurs) <= 1 and list_vecteurs[0] == "" :
            nbx.append(0)
        else :

            for fic in liste_data_sort :
#            for fic in  sorted(list_fic, key = str.lower) :
                if fic[0:len(fic)-4] in list_vecteurs :
                    nbx.append(nbv)
                nbv = nbv + 1

        select.unselect_all()
        for nbi in nbx :
            select.select_path(nbi)


    def changed_choix_courbes(self, combobox, selectX, selectY, list_fic, fltrmod, mrft, lsttime):
        nbv = 0
        nbx = []
        nby = []
        flg_traj = 0

        model = combobox.get_model()
        index = combobox.get_active()
        if index >= 0 :
            try :
                ind = int(model[index][0]) - 1
            except :
                if model[index][0] == "Latitude" : ind = 0
                elif model[index][0] == "Longitude" : ind = 1
                elif model[index][0] == "Altitude" : ind = 2
                flg_traj = 1

        for fic in list_fic :
            if fic[0:len(fic)-4] in self.graph_gene.graphes[ind].vecteur_X.split(" ") :
                nbx.append(nbv)
            if fic[0:len(fic)-4] in self.graph_gene.graphes[ind].vecteur_Y.split(" ")  :
                nby.append(nbv)
            nbv = nbv + 1

        if selectX != None :
            selectX.unselect_all()
            for nbi in nbx :
                selectX.select_path(nbi)

        if mrft != None :
            del mrft[:]
            for rft in list_reftime[:] :
                mrft.append(rft)
            fltrmod.refilter()

        if selectY != None :
            selectY.unselect_all()
            for nbi in nby :
                selectY.select_path(nbi)

        if flg_traj == 1 :
            if ind == 2 :
                liste_data = [f for f in list_fic if f.startswith("alt")]
            if ind == 1 :
                liste_data = [f for f in list_fic if f.lower().startswith("pos_lon")]
            if ind == 0 :
                liste_data = [f for f in list_fic if f.lower().startswith("pos_lat")]
        else :
            liste_data = list_fic

        liste_data_sort = sorted(list(self.graph_gene.vecteurs_operations.keys()), key = str.lower)
        for fic in  liste_data_sort :
            Iter = fltrmod.append()
            fltrmod.set(Iter, 0, fic)

        liste_data_sort = sorted(liste_data, key = str.lower)
        for fic in liste_data_sort :
            Iter = fltrmod.append()
            fltrmod.set(Iter, 0, fic[0:len(fic)-4])


    def changed_presentation_serie(self, combobox, Hbox):
        model = combobox.get_model()
        index = combobox.get_active()
        if model[index][0] == "Profil" or model[index][0] == 'Image' :
            Hbox.show()
        else:
            Hbox.hide()

        self.graph_gene.Type_graphe_serie = model[index][0]
        return

    def changed_indice(self, combobox, choix_courbe, motcle):
        try :
            model = choix_courbe.get_model()
            index = choix_courbe.get_active()
            ind = int(model[index][0])
        except :
            index = choix_courbe
            if index < 10 :
                ind = index
            else :
                nci = index % 10
                ind = int((index - nci)/10)

        if index >= 0 :
            if motcle == "Type" :
                model = combobox.get_model()
                index = combobox.get_active()
                self.graph_gene.graphes[ind-1].type_trait = model[index][0]
            if motcle == "Epais" :
                model = combobox.get_model()
                index = combobox.get_active()
                self.graph_gene.graphes[ind-1].epais_trait = int(model[index][0])
            if motcle == "Mark" :
                model = combobox.get_model()
                index = combobox.get_active()
                self.graph_gene.graphes[ind-1].type_mark = model[index][0]
            if motcle == "Coul" :
                model = combobox.get_model()
                index = combobox.get_active()
                self.graph_gene.graphes[ind-1].couleur = model[index][0]
            if motcle == "Fonct" :
                model = combobox.get_model()
                index = combobox.get_active()
                self.graph_gene.graphes[ind-1].fonction = model[index][0]
        return

    def maj_periode_vent(self, adjust) :
        self.graph_gene.graphes[0].periode_trace_vent = int(adjust.get_value())

    def maj_nb_couleur(self, adjust, E_Bo) :
        self.graph_gene.graphes[0].nb_classe_couleur = int(adjust.get_value())
        for nb in npy.arange(1, int(adjust.get_value())) :
            E_Bo[nb].set_sensitive(True)

        for nb in npy.arange(int(adjust.get_value()), 8) :
            E_Bo[nb].set_sensitive(False)
            E_Bo[nb].set_text("")

    def ihm_Choix_Sup_vent(self, widget, event, E_sup, E_acqid):

        acqid = E_acqid.get_text()
       
        if self.graph_gene.graphes[0].vecteur_X == "" and self.graph_gene.graphes[0].vecteur_Y == "" :
            message="Saisir en premier les vecteurs à tracer !"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return
        else :
            info_vect = adpt.read_vect(acqid, self.graph_gene.graphes[0].vecteur_X, attributes_only = True, alarme = 0 )
            freq_time_X = info_vect.attributes["freq_ech"]
            freq_sup = "_"+freq_time_X+".vbn"
            
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            E_sup[0].set_text("")
            E_sup[1].set_text("")
            return

        if self.win_sup_vent != 0 :
            self.win_sup_vent.present()
            return

        if acqid == '' :
            message = "Attention Choix acquisition non rempli"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        try :
            rep_data = AIDA.ID_to_datapath(acqid)
        except AIDA.AidaError :
            message = "Attention Acqid non valid !"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        liste_data = recup_liste_vecteur(rep_data)
        if ( len(liste_data) == 0 ) :
            message = "Pas de fichier pour l'acquisition " + acqid + " dans " + rep_data + "!"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        liste_data.append("")
        liste_data_sort = sorted(liste_data, key = str.lower)

        # Creation d'une nouvelle fenetre
        window = Gtk.Window()
        window.connect("delete-event", self.quitter_fenetre, window, 1)
        self.win_sup_vent = window

        window.set_title("Selection vecteurs")
        window.set_size_request(300, 500)

        vbox = Gtk.VBox(homogeneous=False, spacing=5)
        v2box = Gtk.VBox(homogeneous=False, spacing=5)
        eb = Gtk.EventBox()
        eb.add(v2box)
        eb.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(red = 60000, green = 60000, blue = 65535))

        boite_v_gene = Gtk.VBox(homogeneous=False, spacing= self.DEF_ESP)
        hbutton = Gtk.HBox(homogeneous=False, spacing=0)
        vbox.pack_start(eb, True, True, 2)

# Hbox choix vecteur V1
        scrolledwindow_V1 = Gtk.ScrolledWindow()
        scrolledwindow_V1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        v2box.pack_start(scrolledwindow_V1, True, True, 3)

        # create a liststore with one string column to use as the model
        liststore_V1 = Gtk.ListStore(str)
        filtremodele_V1 = liststore_V1.filter_new()
        nbv = 0
        nbc = 0
        iter_V1 = liststore_V1.append()
        liststore_V1.set(iter_V1, 0, "")
        for fic in [f for f in liste_data_sort if ((f.lower().startswith("ven_dd") or f.startswith("ven_e"))
                  and (f.find(freq_sup) >= 0) ) ] :
            iter_V1 = liststore_V1.append()
            if ((fic.endswith("vbn.gz"))) :
                liststore_V1.set(iter_V1, 0, fic[0:len(fic)-7])
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                liststore_V1.set(iter_V1, 0, fic[0:len(fic)-4])
                fic_sans_ext = fic[0:len(fic)-4]
            if fic_sans_ext == self.graph_gene.graphes[0].vect_sup_vent1  :
                nbc = nbv
            nbv = nbv + 1

        # create the TreeView using liststore
        treeview_V1 = Gtk.TreeView(model=liststore_V1)
        selection_V1 = treeview_V1.get_selection()
        treeview_V1.set_model(filtremodele_V1)
        selection_V1.select_path(nbc)
        selection_V1.connect("changed", self.selection_sup, 1, E_sup[0])

        # create a CellRenderer to render the data
        cell_V1 = Gtk.CellRendererText()
        cell_V1.set_property('font-desc', Pango.FontDescription("sans 8") )

        # create the TreeViewColumns to display the data
        tvcolumn_V1 = Gtk.TreeViewColumn('Vent DD ou n', cell_V1, text=0)

        # add columns to treeview
        treeview_V1.append_column(tvcolumn_V1)

        # Allow sorting on the column
        tvcolumn_V1.set_sort_column_id(0)

        # make treeview searchable
        treeview_V1.set_search_column(0)

        scrolledwindow_V1.add(treeview_V1)

# Hbox choix vecteur V2
        scrolledwindow_V2 = Gtk.ScrolledWindow()
        scrolledwindow_V2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        v2box.pack_start(scrolledwindow_V2, True, True, 3)

        # create a liststore with one string column to use as the model
        liststore_V2 = Gtk.ListStore(str)
        filtremodele_V2 = liststore_V2.filter_new()
        nbv = 0
        nbc = 0
        iter_V2 = liststore_V2.append()
        liststore_V2.set(iter_V2, 0, "")
        for fic in [f for f in liste_data_sort if ((f.lower().startswith("ven_ff") or f.startswith("ven_n"))
                  and f.endswith(freq_sup)) ] :

            iter_V2 = liststore_V2.append()
            liststore_V2.set(iter_V2, 0, fic[0:len(fic)-4])
            if fic[0:len(fic)-4] == self.graph_gene.graphes[0].vect_sup_vent2  :
                nbc = nbv
            nbv = nbv + 1

        # create the TreeView using liststore
        treeview_V2 = Gtk.TreeView(model=liststore_V2)
        selection_V2 = treeview_V2.get_selection()
        treeview_V2.set_model(filtremodele_V2)
        selection_V2.select_path(nbc)
        selection_V2.connect("changed", self.selection_sup, 2, E_sup[1])

        # create a CellRenderer to render the data
        cell_V2 = Gtk.CellRendererText()
        cell_V2.set_property('font-desc', Pango.FontDescription("sans 8") )

        # create the TreeViewColumns to display the data
        tvcolumn_V2 = Gtk.TreeViewColumn('Vent FF ou n', cell_V2, text=0)

        # add columns to treeview
        treeview_V2.append_column(tvcolumn_V2)

        # Allow sorting on the column
        tvcolumn_V2.set_sort_column_id(0)

        # make treeview searchable
        treeview_V2.set_search_column(0)

        scrolledwindow_V2.add(treeview_V2)

# Creation d'un gradateur horizontal pout choisir la période
# d'affichage des données

        etiquette = Gtk.Label()
        etiquette.set_markup("période de tracé du vent :")
        vbox.pack_start(etiquette, False, False, 0)

        Adj_periode_vent = Gtk.Adjustment(value=self.graph_gene.graphes[0].periode_trace_vent,\
                lower=10.0, upper=600.0, step_increment=1, page_increment=10, page_size=0)
        Adj_periode_vent.connect("value_changed", self.maj_periode_vent)
        gradateur = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Adj_periode_vent)
        gradateur.set_digits(0)
        vbox.pack_start(gradateur, False, True, 0)

        B_ok = Gtk.Button()
        B_ok.set_label('OK')
        hbutton.pack_end(B_ok, False, False, 0)
        vbox.pack_start(hbutton, False, False, 0)
        B_ok.connect("clicked", self.quitter_fenetre, None, window, 1)
        window.add(vbox)
        window.show_all()


    def calcul_bornes_sup(self, widget, E_Bo, selection, adj, acqid):
# Recherche vecteur selectionne
        tv = selection.get_tree_view()
        model = tv.get_model()
        sel = selection.get_selected_rows()
        if sel:
            model, Path = sel
            try :
                for p_pt in Path :
                    p_iter = model.get_iter(p_pt)
                    vect = model.get_value(p_iter, 0)
            except TypeError:
                return

        nbc = adj.get_value()
        data_couleur = adpt.read_vect(acqid, vect)
        SupMin = npy.nanmin(data_couleur.data)
        E_Bo[0].set_text(str(SupMin))
        SupMax = npy.nanmax(data_couleur.data)
        E_Bo[8].set_text(str(SupMax))
        SupLong = SupMax - SupMin
        for nc in npy.arange(1, nbc) :
            val = int(SupMin + (nc*SupLong)/nbc)
            E_Bo[int(nc)].set_text(str(val))

    def ihm_Choix_Sup_vecteur(self, widget, event, E_sup, E_acqid, type_sup):

        acqid = E_acqid.get_text()
        self.win_Top = 0
       
        if self.graph_gene.graphes[0].vecteur_X == "" and self.graph_gene.graphes[0].vecteur_Y == "" :
            message="Saisir en premier les vecteurs à tracer !"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return
        elif type_sup == "Top" :
            freq_sup = "vbn"
        else :
            info_vect = adpt.read_vect(acqid, self.graph_gene.graphes[0].vecteur_X, attributes_only = True, alarme = 0 )
            freq_time_X = info_vect.attributes["freq_ech"]
            if float(freq_time_X) < 1 and float(freq_time_X) > 0. :
                int_freq = int(1/float(freq_time_X))
                freq_time_X = "%" + str(int_freq)
                print(freq_time_X)
            freq_sup = "_"+freq_time_X+".vbn"
            
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            E_sup.set_text("")
            return

        if acqid == '' :
            message = "Attention Choix acquisition non rempli !"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        try :
            rep_data = AIDA.ID_to_datapath(acqid)
        except AIDA.AidaError :
            message = "Attention acq_id non valid!"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        liste_data_all = recup_liste_vecteur(rep_data)
        if type_sup == "Top" :
            liste_data = [f for f in liste_data_all if f.startswith("top")]
        else :
            liste_data = liste_data_all

        liste_data_sort = sorted(liste_data, key = str.lower)
        if ( len(liste_data_sort) == 0 ) :
            message = "Pas de fichier pour l'acquisition " + acqid + " dans " + rep_data + "!"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        # Create a new window si necessaire
        if type_sup == "Top" :
            if self.win_Top != 0 :
                self.win_Top.present()
                return
            else :
                window = Gtk.Window()
                window.connect("delete-event", self.quitter_fenetre, window, 2)
                self.win_Top = window

        if type_sup == "Couleur" :
            if self.win_sup_couleur != 0 :
                self.win_sup_couleur.present()
                return
            else :
                window = Gtk.Window()
                window.connect("delete-event", self.quitter_fenetre, window, 2)
                self.win_sup_couleur = window

        if type_sup == "Texte" :
            if self.win_sup_texte != 0 :
                self.win_sup_texte.present()
                return
            else :
                window = Gtk.Window()
                window.connect("delete-event", self.quitter_fenetre, window, 3)
                self.win_sup_texte = window

        window.set_title("Selection vecteurs 1D")
        window.set_size_request(600, 500)

        B_V_Gene = Gtk.VBox(homogeneous=False, spacing=0)
        B_H_Saisie = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Gene.pack_start(B_H_Saisie, True, True, 0)

        B_button = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Gene.pack_start(B_button, False, True, 0)

        B_ok = Gtk.Button()
        B_ok.set_label('OK')
        B_button.pack_end(B_ok, False, True, 0)

        B_V_Saisie = Gtk.VBox()
        B_H_Saisie.pack_start(B_V_Saisie, True, True, 0)

        scrolledwindow = Gtk.ScrolledWindow()
        B_V_Saisie.pack_start(scrolledwindow, True, True, 0)

        B_H_Cherche = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Saisie.pack_start(B_H_Cherche, False, True, 0)

        L_Cherche = Gtk.Label()
        L_Cherche.set_markup("Filtre :")
        L_Cherche.set_size_request(50, 5)
        E_Cherche = Gtk.Entry()
        E_Cherche.set_size_request(60, 5)
        Bu_Cherche = Gtk.Button()
        image = Gtk.Image()
        AH = os.getenv('AIDA_HOME')
        basedir = os.path.join(AH, 'share/aidaplot/Bitmaps')
        image.set_from_file(basedir + "/Cherche.xpm")
        Bu_Cherche.add(image)

        B_H_Cherche.pack_start(L_Cherche, False, True, 0)
        B_H_Cherche.pack_start(E_Cherche, True, True, 0)
        B_H_Cherche.pack_start(Bu_Cherche, False, True, 0)

        cadre = Gtk.Frame()
        cadre.set_label("Présentation")

        B_vbox_g = Gtk.VBox(homogeneous=False, spacing=0)
        cadre.add(B_vbox_g)
        B_H_Saisie.pack_start(cadre, True, True, 0)

        if type_sup == "Couleur" :
# Creation d'un gradateur horizontal pout choisir la période
# d'affichage des données

            etiquette = Gtk.Label()
            etiquette.set_markup("Nombre de couleur :")
            B_vbox_g.pack_start(etiquette, False, False, 0)

            Adj_nb_couleur = Gtk.Adjustment(value=self.graph_gene.graphes[0].nb_classe_couleur,\
                    lower=1.0, upper=8.0, step_increment=1, page_increment=1, page_size=0)
            gradateur = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=Adj_nb_couleur)
            gradateur.set_digits(0)
            B_vbox_g.pack_start(gradateur, False, True, 0)

            separateur = Gtk.HSeparator()
            B_vbox_g.pack_start(separateur, False, True, 1)

            etiquette = Gtk.Label()
            etiquette.set_markup("Saisie des bornes :")
            B_vbox_g.pack_start(etiquette, False, False, 0)
            bt_calcul_bornes = Gtk.Button()
            bt_calcul_bornes.set_label("Calcul")
            B_vbox_g.pack_start(bt_calcul_bornes, False, False, 0)

            B_Hbox1 = Gtk.HBox(homogeneous=False, spacing=0)
            B_Vbox1 = Gtk.VBox(homogeneous=False, spacing=0)
            B_Vbox2 = Gtk.VBox(homogeneous=False, spacing=0)
            B_Hbox1.pack_start(B_Vbox1, False, False, 0)
            B_Hbox1.pack_end(B_Vbox2, False, False, 0)
            B_vbox_g.pack_start(B_Hbox1, False, False, 0)

            etiquette = Gtk.Label()
            etiquette.set_markup("Min :")
            B_Vbox1.pack_start(etiquette, False, False, 0)
            E_min = Gtk.Entry()
            E_min.set_size_request(60, 5)
            try :
                E_min.set_text(str(self.graph_gene.graphes[0].seuils_classe_couleur[0]))
            except :
                print ("Pas de valeur min")
            B_Vbox1.pack_start(E_min, False, False, 0)

            etiquette = Gtk.Label()
            etiquette.set_markup("Max :")
            B_Vbox2.pack_start(etiquette, False, False, 0)
            E_max = Gtk.Entry()
            E_max.set_size_request(60, 5)
            try :
                nbcx = int(self.graph_gene.graphes[0].nb_classe_couleur)
                E_max.set_text(str(self.graph_gene.graphes[0].seuils_classe_couleur[nbcx]))
            except :
                print ("Pas de valeur max")
            B_Vbox2.pack_start(E_max, False, False, 0)

            etiquette = Gtk.Label()
            etiquette.set_markup("Bornes :")
            B_vbox_g.pack_start(etiquette, False, False, 0)
            B_Hbox2 = Gtk.HBox(homogeneous=False, spacing=0)
            B_vbox_g.pack_start(B_Hbox2, False, False, 0)

            L_B = []
            L_B.append(E_min)
            for neb in npy.arange(1, 8) :
                E_B = Gtk.Entry()
                E_B.set_size_request(30, 5)
                B_Hbox2.pack_start(E_B, True, True, 0)
                L_B.append(E_B)
                if self.graph_gene.graphes[0].nb_classe_couleur > neb :
                    E_B.set_sensitive(True)
                    try :
                        E_B.set_text(str(self.graph_gene.graphes[0].seuils_classe_couleur[neb]))
                    except :
                        print(("Pas de valeur " + str(neb)))
                else :
                    E_B.set_sensitive(False)

            L_B.append(E_max)

            Adj_nb_couleur.connect("value_changed", self.maj_nb_couleur, L_B)

        # create a liststore with one string column to use as the model
        liststore = Gtk.ListStore(str)
        nbv = 0
        nbc = 0
        Iter = liststore.append()
        liststore.set(Iter, 0, " ")
        for fic in [f for f in liste_data_sort if (f.find(freq_sup) >= 0) ] :
            Iter = liststore.append()
            if ((fic.endswith("vbn.gz"))) :
                liststore.set(Iter, 0, fic[0:len(fic)-7])
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                liststore.set(Iter, 0, fic[0:len(fic)-4])
                fic_sans_ext = fic[0:len(fic)-4]
            if fic_sans_ext == self.graph_gene.graphes[0].vect_sup_couleur or \
                      fic_sans_ext == self.graph_gene.graphes[0].vect_sup_texte :
                nbc = nbv
            nbv = nbv + 1

        # create the TreeView using liststore
        treeview = Gtk.TreeView(model=liststore)
        selection = treeview.get_selection()
        selection.select_path(nbc)

        # create a CellRenderer to render the data
        cell = Gtk.CellRendererText()

        # create the TreeViewColumns to display the data
        tvcolumn = Gtk.TreeViewColumn('Nom', cell, text=0)

        # add columns to treeview
        treeview.append_column(tvcolumn)

        # Allow sorting on the column
        tvcolumn.set_sort_column_id(0)

        if type_sup == "Couleur" :
            bt_calcul_bornes.connect("clicked", self.calcul_bornes_sup, L_B, selection, Adj_nb_couleur, acqid)
            B_ok.connect("clicked", self.valid_Choix_Sup_couleur, L_B, selection, Adj_nb_couleur, E_sup, window)
        elif type_sup == "Texte" :
            selection.connect("changed", self.selection_sup, 3, E_sup )
            B_ok.connect("clicked", self.quitter_fenetre, None, window, 3)
        elif type_sup == "Top":
            selection.connect("changed", self.selection_sup, 4, E_sup )
            B_ok.connect("clicked", self.quitter_fenetre, None, window, 3)

        treeview.set_search_column(0)

        scrolledwindow.add(treeview)
        window.add(B_V_Gene)
        window.show_all()

    def valid_Choix_Sup_couleur(self, widget, E_Bo, selection, Adj_nb_couleur, E_sup_c, win) :
# Recherche vecteur selectionne
        self.graph_gene.graphes[0].nb_classe_couleur = Adj_nb_couleur.get_value()
        ncv = 0
        del(self.graph_gene.graphes[0].seuils_classe_couleur[:])
        if E_Bo[0].get_text() == "" or E_Bo[8].get_text() == "" :
            message = "Attention saisie des bornes obligatoire!"
            raise Abandon(message, Gtk.MESSAGE_ERROR)
            print ("ATTENTION PAS DE VALEURS")
        else :
            for nc in npy.arange(9) :
                try :
                    self.graph_gene.graphes[0].seuils_classe_couleur.append(float(E_Bo[nc].get_text()))
                    ncv = ncv + 1
                except :
                    continue

            tv = selection.get_tree_view()
            model = tv.get_model()
            sel = selection.get_selected_rows()
            if sel:
                model, Path = sel
                try :
                    for p_pt in Path :
                        p_iter = model.get_iter(p_pt)
                        vect = model.get_value(p_iter, 0)
                        E_sup_c.set_text(vect)
                        self.graph_gene.graphes[0].vect_sup_couleur = vect
                except TypeError:
                    return

            self.quitter_fenetre(None, widget, win, 2)


    def Choix_vecteur_serie_1D(self, widget, event, type_filter, champsaisie, ind, champsaisie2):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            champsaisie[ind].set_text("")
            return

        if self.win_choix_vecteur_serie != 0 :
            self.win_choix_vecteur_serie.present()
            return

        acqid = champsaisie2.get_text()
        self.graph_gene.acqid = acqid
        if acqid == '' :
            message = "Attention Choix acquisition non rempli !"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        try :
            rep_data = AIDA.ID_to_datapath(acqid)
        except AIDA.AidaError :
            message = "Attention acq_id non valid!"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        liste_data_all = recup_liste_vecteur(rep_data)
        if ( len(liste_data_all) == 0 ) :
            message = "Pas de fichier pour l'acquisition " + acqid + " dans " + rep_data + "!"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        flg_serie = 0
        if type_filter == 1 :
            titre_label = ['Graph1', 'Graph2', 'Graph3', 'Graph4', 'Graph5', 'Graph6']
            flg_serie = 1
        elif type_filter < 5 :
            titre_label = ['Latitude', 'Longitude', 'Altitude']
        elif type_filter == 5:
            titre_label = ['tableau']
        else :
            titre_label = ['serie']

        if type_filter == 2 :
            liste_data = [f for f in liste_data_all if f.startswith("alt")]
        elif type_filter == 3 :
            liste_data = [f for f in liste_data_all if f.lower().startswith("pos_lon")]
        elif type_filter == 4 :
            liste_data = [f for f in liste_data_all if f.lower().startswith("pos_lat")]
        elif type_filter == 5 :
            liste_data = [f for f in liste_data_all if ( f.startswith("mic_conc_array") or (f.find("2D")>=0))]
        else :
            liste_data = liste_data_all

        liste_data.append("  ")
        liste_data_sort = sorted(liste_data, key = str.lower)

        # Create a new window
        window = Gtk.Window()
        self.win_choix_vecteur_serie = window
        window.set_title("Selection vecteurs 1D")
        window.set_size_request(600, 500)
        window.connect("delete-event", self.quitter_fenetre, window, 4)

        B_V_Gene = Gtk.VBox(homogeneous=False, spacing=0)
        B_H_Saisie = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Gene.pack_start(B_H_Saisie, True, True, 0)

        B_button = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Gene.pack_start(B_button, False, True, 0)
        B_Equation = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Gene.pack_start(B_Equation, False, True, 0)

        B_V_Saisie = Gtk.VBox(homogeneous=False, spacing=0)
        B_H_Saisie.pack_start(B_V_Saisie, True, True, 0)

        scrolledwindow = Gtk.ScrolledWindow()
        B_V_Saisie.pack_start(scrolledwindow, True, True, 0)

        B_H_Cherche = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Saisie.pack_start(B_H_Cherche, False, True, 0)

        L_Cherche = Gtk.Label()
        L_Cherche.set_markup("Filtre :")
        L_Cherche.set_size_request(50, 5)
        E_Cherche = Gtk.Entry()
        E_Cherche.set_size_request(60, 5)
        Bu_Cherche = Gtk.Button()
        image = Gtk.Image()
        AH = os.getenv('AIDA_HOME')
        basedir = os.path.join(AH, 'share/aidaplot/Bitmaps')
        image.set_from_file(basedir + "/Cherche.xpm")
        Bu_Cherche.add(image)

        B_H_Cherche.pack_start(L_Cherche, False, True, 0)
        B_H_Cherche.pack_start(E_Cherche, True, True, 0)
        B_H_Cherche.pack_start(Bu_Cherche, False, True, 0)

        cadre = Gtk.Frame()
        cadre.set_label("Choix courbe            Vecteur(s)")
        liste_label = []
        liste_button = []

        B_vbox_g = Gtk.VBox(homogeneous=False, spacing=0)
        cadre.add(B_vbox_g)
        B_hbox_1 = Gtk.HBox(homogeneous=False, spacing=0)
        B_vbox_g.pack_start(B_hbox_1, False, True, 0)
        B_TitreGraph = Gtk.RadioButton.new_with_label_from_widget(None, titre_label[0])
        liste_button.append(B_TitreGraph)
        E_Graph1 = Gtk.EventBox()
        vect = champsaisie[0].get_text()
        vect = vect.replace(' ', '\n')
        L_Graph1 = Gtk.Label()
        L_Graph1.set_markup(vect)
        liste_label.append(L_Graph1)
        B_hbox_1.pack_start(B_TitreGraph, False, True, 5)
        B_hbox_1.pack_start(E_Graph1, True, True, 0)
        E_Graph1.add(L_Graph1)
        separateur = Gtk.HSeparator()
        B_vbox_g.pack_start(separateur, False, True, 1)
        if flg_serie == 1 :
            E_Graph1.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            E_Graph1.connect('button_press_event', self.Config_vecteur_serie_1D, 1, L_Graph1)
            E_Graph1.connect('enter-notify-event', self.chg_cursor)
            E_Graph1.connect('leave-notify-event', self.chg1_cursor)


        if type_filter < 5 :
            B_hbox_2 = Gtk.HBox(homogeneous=False, spacing=0)
            B_vbox_g.pack_start(B_hbox_2, False, True, 0)
            B_TitreGraph2 = Gtk.RadioButton.new_from_widget(B_TitreGraph)
            B_TitreGraph2.set_label(titre_label[1])
            liste_button.append(B_TitreGraph2)
            E_Graph2 = Gtk.EventBox()
            vect = champsaisie[1].get_text()
            vect = vect.replace(' ', '\n')
            L_Graph2 = Gtk.Label()
            L_Graph2.set_markup(vect)
            liste_label.append(L_Graph2)
            B_hbox_2.pack_start(B_TitreGraph2, False, True, 5)
            B_hbox_2.pack_start(E_Graph2, True, True, 0)
            E_Graph2.add(L_Graph2)
            separateur = Gtk.HSeparator()
            B_vbox_g.pack_start(separateur, False, True, 1)
            if flg_serie == 1 :
                E_Graph2.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                E_Graph2.connect('button_press_event', self.Config_vecteur_serie_1D, 2, L_Graph2)
                E_Graph2.connect('enter-notify-event', self.chg_cursor)
                E_Graph2.connect('leave-notify-event', self.chg1_cursor)

            B_hbox_3 = Gtk.HBox(homogeneous=False, spacing=0)
            B_vbox_g.pack_start(B_hbox_3, False, True, 0)
            B_TitreGraph3 = Gtk.RadioButton.new_from_widget(B_TitreGraph)
            B_TitreGraph3.set_label(titre_label[2])
            liste_button.append(B_TitreGraph3)
            E_Graph3 = Gtk.EventBox()
            vect = champsaisie[2].get_text()
            vect = vect.replace(' ', '\n')
            L_Graph3 = Gtk.Label()
            L_Graph3.set_markup(vect)
            liste_label.append(L_Graph3)
            B_hbox_3.pack_start(B_TitreGraph3, False, True, 5)
            B_hbox_3.pack_start(E_Graph3, True, True, 5)
            E_Graph3.add(L_Graph3)
            separateur = Gtk.HSeparator()
            B_vbox_g.pack_start(separateur, False, True, 1)
            if flg_serie == 1 :
                E_Graph3.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                E_Graph3.connect('button_press_event', self.Config_vecteur_serie_1D, 3, L_Graph3)
                E_Graph3.connect('enter-notify-event', self.chg_cursor)
                E_Graph3.connect('leave-notify-event', self.chg1_cursor)

        if type_filter == 1 :
            B_hbox_4 = Gtk.HBox(homogeneous=False, spacing=0)
            B_vbox_g.pack_start(B_hbox_4, False, True, 0)
            B_TitreGraph4 = Gtk.RadioButton.new_from_widget(B_TitreGraph)
            B_TitreGraph4.set_label(titre_label[3])
            liste_button.append(B_TitreGraph4)
            E_Graph4 = Gtk.EventBox()
            vect = champsaisie[3].get_text()
            vect = vect.replace(' ', '\n')
            L_Graph4 = Gtk.Label()
            L_Graph4.set_markup(vect)
            liste_label.append(L_Graph4)
            B_hbox_4.pack_start(B_TitreGraph4, False, True, 5)
            B_hbox_4.pack_start(E_Graph4, True, True, 0)
            E_Graph4.add(L_Graph4)
            separateur = Gtk.HSeparator()
            B_vbox_g.pack_start(separateur, False, True, 1)
            E_Graph4.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            E_Graph4.connect('button_press_event', self.Config_vecteur_serie_1D, 4, L_Graph4)
            E_Graph4.connect('enter-notify-event', self.chg_cursor)
            E_Graph4.connect('leave-notify-event', self.chg1_cursor)

            B_hbox_5 = Gtk.HBox(homogeneous=False, spacing=0)
            B_vbox_g.pack_start(B_hbox_5, False, True, 0)
            B_TitreGraph5 = Gtk.RadioButton.new_from_widget(B_TitreGraph)
            B_TitreGraph5.set_label(titre_label[4])
            liste_button.append(B_TitreGraph5)
            E_Graph5 = Gtk.EventBox()
            vect = champsaisie[4].get_text()
            vect = vect.replace(' ', '\n')
            L_Graph5 = Gtk.Label()
            L_Graph5.set_markup(vect)
            liste_label.append(L_Graph5)
            B_hbox_5.pack_start(B_TitreGraph5, False, True, 5)
            B_hbox_5.pack_start(E_Graph5, True, True, 0)
            E_Graph5.add(L_Graph5)
            separateur = Gtk.HSeparator()
            B_vbox_g.pack_start(separateur, False, True, 1)
            E_Graph5.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            E_Graph5.connect('button_press_event', self.Config_vecteur_serie_1D, 5, L_Graph5)
            E_Graph5.connect('enter-notify-event', self.chg_cursor)
            E_Graph5.connect('leave-notify-event', self.chg1_cursor)

            B_hbox_6 = Gtk.HBox(homogeneous=False, spacing=0)
            B_vbox_g.pack_start(B_hbox_6, False, True, 0)
            B_TitreGraph6 = Gtk.RadioButton.new_from_widget(B_TitreGraph)
            B_TitreGraph6.set_label(titre_label[5])
            liste_button.append(B_TitreGraph6)
            E_Graph6 = Gtk.EventBox()
            vect = champsaisie[5].get_text()
            vect = vect.replace(' ', '\n')
            L_Graph6 = Gtk.Label()
            L_Graph6.set_markup(vect)
            liste_label.append(L_Graph6)
            E_Graph6.add(L_Graph6)
            B_hbox_6.pack_start(B_TitreGraph6, False, True, 5)
            B_hbox_6.pack_start(E_Graph6, True, True, 0)
            E_Graph6.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            E_Graph6.connect('button_press_event', self.Config_vecteur_serie_1D, 6, L_Graph6)
            E_Graph6.connect('enter-notify-event', self.chg_cursor)
            E_Graph6.connect('leave-notify-event', self.chg1_cursor)

        liste_button[ind].set_active(True)
        B_H_Saisie.pack_start(cadre, True, True, 0)

        B_quit = Gtk.Button()
        B_quit.set_label('Quitter')
        B_valid = Gtk.Button()
        B_valid.set_label('Valider')
        B_ok = Gtk.Button()
        B_ok.set_label('OK')
        b_equation = Gtk.Button()
        b_equation.set_label('Operation')
        b_equation_ok = Gtk.Button()
        b_equation_ok.set_label('OK')
        b_equation_clear = Gtk.Button()
        b_equation_clear.set_label('Efface')

        B_button.pack_end(B_valid, False, True, 0)
        B_button.pack_end(B_ok, False, True, 0)
        B_button.pack_end(B_quit, False, True, 0)
        B_button.pack_start(b_equation, False, True, 0)

        E_Equation = Gtk.Entry()
        E_Equation.set_tooltip_text("Equation de type A*B+C*D, avec A B C et D contantes ou vecteurs.\n * peut etre remplacé par /, + par -.\n Pas d'espace.")
        B_Equation.pack_start(E_Equation, True, True, 0)
        B_Equation.pack_end(b_equation_ok, False, True, 0)
        B_Equation.pack_end(b_equation_clear, False, True, 0)
        vect = champsaisie[ind].get_text()
        flg_equation = 0
        self.type_choix_serie = 'direct'
        if vect != "" :
            if vect.find('-') + vect.find('+') \
                     + vect.find('*') + vect.find('/')  >= 0 :
                oper = vect.split(" ")
                E_Equation.set_text(oper[0])
                flg_equation = 1
                self.type_choix_serie = 'operation'

        vect = []
        vect = champsaisie[ind].get_text().split(" ")

        # create a liststore with one string column to use as the model
        liststore = Gtk.ListStore(str)
        nbv = 0
        nbc = []
        Iter = liststore.append()
        liststore.set(Iter, 0, "")
        liste_data_virt = sorted(list(self.graph_gene.vecteurs_operations.keys()), key = str.lower)
        for fic in  liste_data_virt :
            Iter = liststore.append()
            liststore.set(Iter, 0, fic)
            if fic in vect :
                nbc.append(nbv)

        for fic in liste_data_sort :
            if len(fic) < 5 :
                continue
            Iter = liststore.append()
            if ((fic.endswith("vbn.gz"))) :
                liststore.set(Iter, 0, fic[0:len(fic)-7])
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                liststore.set(Iter, 0, fic[0:len(fic)-4])
                fic_sans_ext = fic[0:len(fic)-4]

            if fic_sans_ext in vect :
                nbc.append(nbv)
            nbv = nbv + 1

        # create the TreeView using liststore
        treeview = Gtk.TreeView(model=liststore)
        selection = treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.MULTIPLE)
        B_TitreGraph.connect('toggled', self.change_choix_courbes_1D, selection, liste_data_all, liststore, liste_label, 1)
        if type_filter < 5 :
            B_TitreGraph2.connect('toggled', self.change_choix_courbes_1D, selection, liste_data_all, liststore, liste_label, 2)
            B_TitreGraph3.connect('toggled', self.change_choix_courbes_1D, selection, liste_data_all, liststore, liste_label, 3)
        if type_filter == 1 :
            B_TitreGraph4.connect('toggled', self.change_choix_courbes_1D, selection, liste_data_all, liststore, liste_label, 4)
            B_TitreGraph5.connect('toggled', self.change_choix_courbes_1D, selection, liste_data_all, liststore, liste_label, 5)
            B_TitreGraph6.connect('toggled', self.change_choix_courbes_1D, selection, liste_data_all, liststore, liste_label, 6)

        Bu_Cherche.connect('clicked', self.filtre_vecteur, selection, liste_data_all, liststore, E_Cherche, type_filter, liste_button)
        for nbi in nbc :
            selection.select_path(nbi + 1)


        selection.connect("changed", self.maj_selection_cb, liste_label, liste_button, E_Equation)
        b_equation_ok.connect("clicked", self.valid_operation, liste_label, liste_button, E_Equation, liste_data_all, liststore)
        b_equation_clear.connect("clicked", self.efface_equation, E_Equation)
        # create a CellRenderer to render the data
        cell = Gtk.CellRendererText()

        # create the TreeViewColumns to display the data
        tvcolumn = Gtk.TreeViewColumn('Nom', cell, text= 0)

        # add columns to treeview
        treeview.append_column(tvcolumn)

        # Allow sorting on the column
        tvcolumn.set_sort_column_id(0)

        B_quit.connect("clicked", self.quitter_fenetre, None, window, 4)
        B_ok.connect_data('clicked', self.valid_selection_vecteurs_1D, champsaisie, liste_label, type_filter, window)
        B_valid.connect_data('clicked', self.valid_selection_vecteurs_1D, champsaisie, liste_label, type_filter, None)
        b_equation.connect_data('clicked', self.bascule_equation_direct, B_Equation, self)

#        self.selection_cb(selection, champsaisie, ind, combo, None, None)
        # make treeview searchable
        treeview.set_search_column(0)

        scrolledwindow.add(treeview)
        window.add(B_V_Gene)
        window.show_all()
        if flg_equation == 0 :
            B_Equation.hide()

    def bascule_equation_direct(widget,self, B_Equa, ihm) :
        if ihm.type_choix_serie == 'direct' :
            B_Equa.show()
            ihm.type_choix_serie = 'calcul'
        else :
            B_Equa.hide()
            ihm.type_choix_serie = 'direct'

    def chg_cursor(self, win, widget):
#        widget.set_sensitive(False)
        cursor = Gdk.Cursor(Gdk.CursorType.EXCHANGE)
        widget.window.set_cursor(cursor)

    def chg1_cursor(self, win, widget):
#        widget.set_sensitive(False)
        cursor = Gdk.Cursor(Gdk.CursorType.LEFT_PTR)
        widget.window.set_cursor(cursor)

    def Config_vecteur_serie_1D(self, arg1, arg2, ng, champsaisie):

        if champsaisie.get_text() == "" :
            print ("Pas de vecteur selectionne!")
            return

        vect = []
        coul = []
        trait = []
        epais = []
        mark = []
        axe = []

        vect = champsaisie.get_text().split("\n")

        try :
            vect_enr = self.graph_gene.graphes[ng-1].vecteur_Y.split(" ")
            coul_enr = self.graph_gene.graphes[ng-1].couleur.split(" ")
            trait_enr = self.graph_gene.graphes[ng-1].type_trait.split(" ")
            epais_str = str(self.graph_gene.graphes[ng-1].epais_trait)
            epais_enr = epais_str.split(" ")
            mark_enr = self.graph_gene.graphes[ng-1].type_mark.split(" ")
            axe_enr = self.graph_gene.graphes[ng-1].axe.split(" ")
        except :
            vect_enr = vect

        self.graph_gene.graphes[ng-1].epais_trait = ""
        self.graph_gene.graphes[ng-1].type_mark = ""
        self.graph_gene.graphes[ng-1].type_trait = ""
        self.graph_gene.graphes[ng-1].couleur = ""
        self.graph_gene.graphes[ng-1].axe = ""
        for nv in npy.arange(len(vect)) :
            trouve = 0
            for nvr in npy.arange(len(vect_enr)) :
                if vect[nv] == vect_enr[nvr] :
                    try :
                        coul.append(coul_enr[nvr])
                    except :
                        coul.append(adpt.Config_Couleur[nv])
                    self.graph_gene.graphes[ng-1].couleur = self.graph_gene.graphes[ng-1].couleur + coul[nvr] + " "

                    try :
                        epais.append(epais_enr[nvr])
                    except :
                        epais.append("1")
                    self.graph_gene.graphes[ng-1].epais_trait = self.graph_gene.graphes[ng-1].epais_trait  + epais[nvr] + " "

                    try :
                        trait.append(trait_enr[nvr])
                    except :
                        trait.append("Continu")
                    self.graph_gene.graphes[ng-1].type_trait = self.graph_gene.graphes[ng-1].type_trait + trait[nv] + " "

                    try :
                        mark.append(mark_enr[nvr])
                    except :
                        mark.append("Aucun")
                    self.graph_gene.graphes[ng-1].type_mark = self.graph_gene.graphes[ng-1].type_mark + mark[nv] + " "
                    trouve = 1

                    try :
                        axe.append(axe_enr[nvr])
                    except :
                        axe.append("Auro")
                    self.graph_gene.graphes[ng-1].axe = self.graph_gene.graphes[ng-1].axe + axe[nv] + " "
                    trouve = 1

            if trouve == 0 :
                coul.append(adpt.Config_Couleur[nv])
                epais.append("1")
                trait.append("Continu")
                mark.append("Aucun")
                axe.append("Auto")

# Create a new window
        window = Gtk.Window()
        window.set_title("Configuration Tracer 1D")
        window.set_size_request(600, 350)

        B_V_Gene = Gtk.VBox(homogeneous=False, spacing=0)
        B_H_Saisie = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Gene.pack_start(B_H_Saisie, True, True, 0)

        B_button = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Gene.pack_start(B_button, False, True, 0)

        B_V_Saisie = Gtk.VBox(homogeneous=False, spacing=0)
        B_H_Saisie.pack_start(B_V_Saisie, True, True, 0)

        scrolledwindow = Gtk.ScrolledWindow()
        B_V_Saisie.pack_start(scrolledwindow, True, True, 0)

        B_H_Cherche = Gtk.HBox(homogeneous=False, spacing=0)
        B_V_Saisie.pack_start(B_H_Cherche, False, True, 0)

        cadre = Gtk.Frame()
        cadre.set_label("Config courbe")

        B_hbox_g = Gtk.HBox(homogeneous=False, spacing=0)
        B_vbox_g = Gtk.VButtonBox()
        B_vbox_g2 = Gtk.VButtonBox()
        cadre.add(B_hbox_g)

        B_hbox_g.pack_start(B_vbox_g, True, True, 0)
        B_hbox_g.pack_start(B_vbox_g2, True, True, 0)
        B_H_Saisie.pack_start(cadre, True, True, 0)

# create a liststore with one string column to use as the model
        liststore = Gtk.ListStore(str)
        for fic in vect :
            Iter = liststore.append()
            liststore.set(Iter, 0, fic[0:len(fic)])

# create the TreeView using liststore
        treeview = Gtk.TreeView(model=liststore)
        treeview.set_headers_visible(False)
        selection = treeview.get_selection()
        cell = Gtk.CellRendererText()
        tvcolumn = Gtk.TreeViewColumn('Nom', cell, text=0)
        treeview.append_column(tvcolumn)
        tvcolumn.set_sort_column_id(0)


# Combo box choix type trait
        combolabel_type_trait = Gtk.Label()
        combolabel_type_trait.set_markup("Choix trait :")
        combo_type_trait = Gtk.ComboBoxText()
        npo = 1
        for np in list(Config_TypeTrait.keys()) :
            combo_type_trait.append_text(Config_TypeTrait[np])
            if Config_TypeTrait[np] == trait[0] :
                npo = np
        combo_type_trait.connect('changed', self.maj_config_courbe, selection, vect, trait, "Type", ng)
        combo_type_trait.set_active(npo)

# Combo box choix epaisseur trait
        combolabel_epais_trait = Gtk.Label()
        combolabel_epais_trait.set_markup("Epaisseur trait :")
        combo_epais_trait = Gtk.ComboBoxText()
        for np in npy.arange(1, 5) :
            combo_epais_trait.append_text(str(np))
        combo_epais_trait.connect('changed', self.maj_config_courbe, selection, vect, epais, "Epais", ng)
        try :
            np = epais[0]-1
        except :
            np = '1'

        try :
            combo_epais_trait.set_active(int(np))
        except :
            combo_epais_trait.set_active(0)

# Combo box choix marqueur
        combolabel_marqueur = Gtk.Label()
        combolabel_marqueur.set_markup("Marqueur :")
        combo_marqueur = Gtk.ComboBoxText()
        npo = 0
        for np in list(Config_Marqueur.keys()) :
            combo_marqueur.append_text(Config_Marqueur[np])
            if Config_Marqueur[np] == mark[0] :
                npo = np
        combo_marqueur.connect('changed', self.maj_config_courbe, selection, vect, mark, "Mark", ng)
        combo_marqueur.set_active(npo)

# Combo box choix axe
        combolabel_axe = Gtk.Label()
        combolabel_axe.set_markup("Axe :")
        combo_axe = Gtk.ComboBoxText()
        npo = 0
        for np in list(Config_Axe.keys()) :
            combo_axe.append_text(Config_Axe[np])
            if Config_Axe[np] == axe[0] :
                npo = np
        combo_axe.connect('changed', self.maj_config_courbe, selection, vect, axe, "Axe", ng)
        combo_axe.set_active(npo)

# Combo box choix couleur
        combolabel_couleur = Gtk.Label()
        combolabel_couleur.set_markup("Couleur trait :")
        b_couleur = Gtk.Button()
        if coul[0] == 'None' :
            coul[0] = 'black'
        color_rgba=matplotlib.colors.to_rgba(coul[0])
        clr = Gdk.RGBA()
        clr.red = color_rgba[0]
        clr.green = color_rgba[1]
        clr.blue = color_rgba[2]
        clr.alpha = color_rgba[3]

        b_couleur = Gtk.ColorButton()
        b_couleur.set_rgba(clr)
        b_couleur.set_title('Select a Color')
        b_couleur.connect('color-set', self.color_set_cb, selection, vect, coul, ng)

        B_vbox_g.pack_start(combolabel_type_trait, True, True, 0)
        B_vbox_g.pack_start(combo_type_trait, True, True, 0)
        B_vbox_g.pack_start(combolabel_epais_trait, True, True, 0)
        B_vbox_g.pack_start(combo_epais_trait, True, True, 0)
        B_vbox_g.pack_start(combolabel_marqueur, True, True, 0)
        B_vbox_g.pack_start(combo_marqueur, True, True, 0)
        B_vbox_g.pack_start(combolabel_axe, True, True, 0)
        B_vbox_g.pack_start(combo_axe, True, True, 0)
        B_vbox_g.pack_start(combolabel_couleur, True, True, 0)
        B_vbox_g.pack_start(b_couleur, True, True, 0)

        CB_semilog = Gtk.CheckButton()
        CB_semilog.set_label("Graphe semi_log")
        if self.graph_gene.graphes[ng-1].type_echelle =='log':
            CB_semilog.set_active(True)
        CB_semilog.connect('toggled', self.change_etat_btn, "type_echelle", ng, "log", "lineaire")
        B_vbox_g.pack_start(CB_semilog, True, True, 0)

        B_quit = Gtk.Button()
        B_quit.set_label('Quitter')
        B_efface = Gtk.Button()
        B_efface.set_label('Efface')

        B_button.pack_end(B_efface, False, True, 0)
        B_button.pack_end(B_quit, False, True, 0)

        B_efface.connect('clicked', self.clear_selected, selection, vect, trait, epais, mark, axe, coul, ng)
        B_quit.connect_object('clicked', self.quite_config_vecteurs_1D, arg1, selection, champsaisie, window)

#        self.selection_cb(selection, champsaisie, ind, combo, None, None)
        # make treeview searchable
        treeview.set_search_column(0)
#        treeview.set_reorderable(True)
        selection.connect("changed", self.clicked_vecteur, selection, vect, combo_type_trait, combo_epais_trait, combo_marqueur, b_couleur, trait, epais, mark, coul )

        scrolledwindow.add(treeview)
        window.add(B_V_Gene)
        window.show_all()

    def color_set_cb(self, colorbutton, selection, vect, param, ng):
        model, iter = selection.get_selected()
        if iter:
            vect_choisi = model.get_value(iter, 0)

        for nv in npy.arange(len(vect)) :
            if vect[nv] == vect_choisi :
                nvc = nv
                break

        color = colorbutton.get_color()
#        param[nvc] = "#{:02X}{:02X}{:02X}".format(int(color.red/256), int(color.green/256), int(color.blue/256))
        param[nvc] = "#"+bytearray([int(color.red/256), int(color.green/256), int(color.blue/256)]).hex()

        self.graph_gene.graphes[ng-1].couleur = param[0]
        for nv in npy.arange(1, len(vect)) :
            self.graph_gene.graphes[ng-1].couleur = self.graph_gene.graphes[ng-1].couleur + " " + param[nv]

        return

    def clicked_vecteur(self, par1, selection, vect, cb_tt, cb_et, cb_m, b_c, trait, epais, mark, coul) :
        model, iter = selection.get_selected()
        if iter:
            vect_choisi = model.get_value(iter, 0)
        else :
            return

        for nv in npy.arange(len(vect)) :
            if vect[nv] == vect_choisi :
                nvc = nv
                break


        npo = 0
        for np in list(Config_TypeTrait.keys()) :
            if Config_TypeTrait[np] == trait[nvc] :
                npo = np
                break
        cb_tt.set_active(npo)

        npo = 0
        for np in list(Config_Marqueur.keys()) :
            if  Config_Marqueur[np] == mark[nvc] :
                npo = np
                break
        cb_m.set_active(npo)

        for np in npy.arange(5) :
            if  str(np) == epais[nvc] :
                npo = np
                break
        cb_et.set_active(npo-1)

        color_rgba=matplotlib.colors.to_rgba(coul[nvc])
        clr = Gdk.RGBA()
        clr.red = color_rgba[0]
        clr.green = color_rgba[1]
        clr.blue = color_rgba[2]
        clr.alpha = color_rgba[3]

        b_c.set_rgba(clr)


    def maj_config_courbe(self, combo, selection, vect, param, str_param, ng):
        model, iter = selection.get_selected()
        if iter:
            vect_choisi = model.get_value(iter, 0)
        else :
            return

        for nv in npy.arange(len(vect)) :
            if vect[nv] == vect_choisi :
                nvc = nv
                break

        model = combo.get_model()
        index = combo.get_active()
        param[nvc] = model[index][0]

        if str_param == "Epais" :
            self.graph_gene.graphes[ng-1].epais_trait = param[0]
            for nv in npy.arange(1, len(vect)) :
                self.graph_gene.graphes[ng-1].epais_trait = self.graph_gene.graphes[ng-1].epais_trait + " " + param[nv]

        if str_param == "Mark" :
            self.graph_gene.graphes[ng-1].type_mark = param[0]
            for nv in npy.arange(1, len(vect)) :
                self.graph_gene.graphes[ng-1].type_mark = self.graph_gene.graphes[ng-1].type_mark + " " + param[nv]

        if str_param == "Type" :
            self.graph_gene.graphes[ng-1].type_trait = param[0]
            for nv in npy.arange(1, len(vect)) :
                self.graph_gene.graphes[ng-1].type_trait = self.graph_gene.graphes[ng-1].type_trait + " " + param[nv]

        if str_param == "Axe" :
            self.graph_gene.graphes[ng-1].axe = param[0]
            for nv in npy.arange(1, len(vect)) :
                self.graph_gene.graphes[ng-1].axe = self.graph_gene.graphes[ng-1].axe + " " + param[nv]
        return


    def clear_selected(self, button, selection, vect, trait, epais, mark, axe, coul , ng):
#    selection = self.treeview.get_selection()
        model, iter = selection.get_selected()
        if iter:
            vect_choisi = model.get_value(iter, 0)
            model.remove(iter)
        else :
            return

        for nv in npy.arange(len(vect)) :
            if vect[nv] == vect_choisi :
                nvc = nv
                break

        del vect[nvc]
        del trait[nvc]
        del epais[nvc]
        del mark[nvc]
        del axe[nvc]
        del coul[nvc]

        self.graph_gene.graphes[ng-1].epais_trait = epais[0]
        self.graph_gene.graphes[ng-1].type_mark = mark[0]
        self.graph_gene.graphes[ng-1].type_trait = trait[0]
        self.graph_gene.graphes[ng-1].axe = axe[0]
        self.graph_gene.graphes[ng-1].couleur = coul[0]
        for nv in npy.arange(1, len(vect)) :
            self.graph_gene.graphes[ng-1].epais_trait = self.graph_gene.graphes[ng-1].epais_trait + " " + epais[nv]
            self.graph_gene.graphes[ng-1].type_mark = self.graph_gene.graphes[ng-1].type_mark + " " + mark[nv]
            self.graph_gene.graphes[ng-1].axe = self.graph_gene.graphes[ng-1].axe + " " + axe[nv]
            self.graph_gene.graphes[ng-1].type_trait = self.graph_gene.graphes[ng-1].type_trait + " " + trait[nv]
            self.graph_gene.graphes[ng-1].couleur = self.graph_gene.graphes[ng-1].couleur + " " + coul[nv]


    def lance_Choix_vecteurs_XY(self, widget, champsaisie, ind, E_acqid):

        acqid = E_acqid.get_text()
        if acqid == '' :
            message = "Attention Choix acquisition non rempli"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        if self.ihm_choix_vecteurs != None :
            return
        else :
            win = Gtk.Window()
            self.ihm_choix_vecteurs = win
            win.set_title("Elaboration liste des vecteurs")
#            win.set_position(gtk.WIN_POS_CENTER)
            win.set_default_size(300, 50)

            #Table d'organisation des widgets
            table = Gtk.Table(2, 2, True) 

            #Barre de chargement
            progressbar = Gtk.ProgressBar()
            progressbar.set_text("En attente...")
            table.attach(progressbar, 0, 2, 0, 2)

            win.add(table)
            win.show_all()

            self.scroll = False
            #Lancement du thread
#            t2 = _thread.start_new_thread(self.Choix_vecteurs_XY,(widget, champsaisie, ind, acqid,progressbar, win))
            self.Choix_vecteurs_XY2(widget, champsaisie, ind, acqid,progressbar, win)
        return

    def Choix_vecteurs_XY2(self, widget, champsaisie, ind, acqid, canvas):

        MonIhm=self
        # Creation d'une nouvelle fenetre
        canvas.get_property("window").set_cursor(Gdk.Cursor(Gdk.CursorType.WATCH))
        window = Gtk.Window()
        window.connect("delete-event", self.quitter_fenetre, window, 4)
        window.set_title("Selection vecteurs Plot XY")
        window.set_size_request(600, 500)

        vbox = Gtk.VBox(homogeneous=False, spacing=0)
        pgbbox =  Gtk.HBox(homogeneous=False, spacing=0)
        hbox = Gtk.HBox(homogeneous=False, spacing=0)
        hbutton = Gtk.HBox(homogeneous=False, spacing=0)
        vbutton = Gtk.VButtonBox()
        B_Equation = Gtk.HBox(homogeneous=False, spacing=0)

        progressbar = Gtk.ProgressBar()
        progressbar.set_text("En attente...")
        pgbbox.pack_start (progressbar, False, False,0)
        progressbar.set_show_text(True)

#        vbox.pack_start(pgbbox, True, False,0)
        vbox.pack_start(progressbar, False, False,0)
        vbox.pack_start(hbox, True, True,0)
        vbox.pack_start(hbutton, False, True,0)
        vbox.pack_start(B_Equation, False, True,0)
        vbox.pack_start(progressbar, False, True,0)

# Combo box choix courbe
        combolabel = Gtk.Label()
        combolabel.set_markup("Choix courbe :")
        combo = Gtk.ComboBoxText()
        combo.append_text('1')
        combo.append_text('2')
        combo.append_text('3')
        combo.append_text('4')
        combo.append_text('5')
        combo.append_text('6')
        combo.set_active(ind)

        b_equation = Gtk.Button()
        b_equation.set_label('Operation')
        b_equation_ok = Gtk.Button()
        b_equation_ok.set_label('OK')
        b_equation_clear = Gtk.Button()
        b_equation_clear.set_label("Efface")

        E_Equation = Gtk.Entry()
        E_Equation.set_tooltip_text("Equation de type A*B+C*D, avec A B C et D contantes ou vecteurs.\n * peut etre remplacé par /, + par -.\n Pas d'espace.")
        B_Equation.pack_start(E_Equation, True, False, 0)
        B_Equation.pack_end(b_equation_ok, False, False,0)
        B_Equation.pack_end(b_equation_clear, False, False,0)
        flg_equation = 0
        self.type_choix_serie = 'direct'

# Combo box choix type trait
        combolabel_type_trait = Gtk.Label()
        combolabel_type_trait.set_markup("Choix trait :")
        combo_type_trait = Gtk.ComboBoxText()
        npo = 0
        for np in list(Config_TypeTrait.keys()) :
            combo_type_trait.append_text(Config_TypeTrait[np])
            if Config_TypeTrait[np] == self.graph_gene.graphes[ind].type_trait :
                npo = np
        combo_type_trait.connect('changed', self.changed_indice, combo, "Type")
        combo_type_trait.set_active(npo)

# Combo box choix epaisseur trait
        combolabel_epais_trait = Gtk.Label()
        combolabel_epais_trait.set_markup("Epaisseur trait :")
        combo_epais_trait = Gtk.ComboBoxText()
        for np in npy.arange(5) :
            combo_epais_trait.append_text(str(np+1))
        combo_epais_trait.connect('changed', self.changed_indice, combo, "Epais")
        try :
            np = self.graph_gene.graphes[ind].epais_trait
        except :
            np = '0'

        try :
            combo_epais_trait.set_active(int(np)-1)
        except :
            combo_epais_trait.set_active(0)

# Combo box choix marqueur
        combolabel_marqueur = Gtk.Label()
        combolabel_marqueur.set_markup("Marqueur :")
        combo_marqueur = Gtk.ComboBoxText()
        npo = 0
        for np in list(Config_Marqueur.keys()) :
            combo_marqueur.append_text(Config_Marqueur[np])
            if Config_Marqueur[np] == self.graph_gene.graphes[ind].type_mark :
                npo = np
        combo_marqueur.connect('changed', self.changed_indice, combo, "Mark")
        combo_marqueur.set_active(npo)

# Combo box choix couleur
        combolabel_couleur = Gtk.Label()
        combolabel_couleur.set_markup("Couleur trait :")
        combo_couleur = Gtk.ComboBoxText()
        npo = 0
        for np in list(adpt.Config_Couleur.keys()) :
            combo_couleur.append_text(adpt.Config_Couleur[np])
            if adpt.Config_Couleur[np] == self.graph_gene.graphes[ind].couleur :
                npo = np
        combo_couleur.connect('changed', self.changed_indice, combo, "Coul")
        combo_couleur.set_active(npo)

# Combo box choix Fonction
        combolabel_fonction = Gtk.Label()
        combolabel_fonction.set_markup("Fonction :")
        combo_fonction = Gtk.ComboBoxText()
        npo = 0
        for np in Config_Fonction.keys() :
            combo_fonction.append_text(Config_Fonction[np])
            if Config_Fonction[np] == self.graph_gene.graphes[ind].fonction :
                npo = np
        combo_fonction.connect('changed', self.changed_indice, combo, "Fonct")
        combo_fonction.set_active(npo)

# Hbox choix vecteur en X
        scrolledwindow_X = Gtk.ScrolledWindow()
        scrolledwindow_Y = Gtk.ScrolledWindow()
        separateur = Gtk.VSeparator()
        hbox.pack_start(scrolledwindow_X, True, True, 0)
#        hbox.pack_start(separateur, True, False, 1)
        hbox.pack_start(scrolledwindow_Y, True, True, 0)


# création de la boite
        vbutton.pack_start(combolabel_type_trait, True, False,0)
        vbutton.pack_start(combo_type_trait, True, False,0)
        vbutton.pack_start(combolabel_epais_trait, True, False,0)
        vbutton.pack_start(combo_epais_trait, True, False,0)
        vbutton.pack_start(combolabel_marqueur, True, False,0)
        vbutton.pack_start(combo_marqueur, True, False,0)
        vbutton.pack_start(combolabel_couleur, True, False,0)
        vbutton.pack_start(combo_couleur, True, False,0)
        vbutton.pack_start(combolabel_fonction, True, False,0)
        vbutton.pack_start(combo_fonction, True, False,0)
        hbox.pack_start(vbutton, True, True,0)

        b0 = Gtk.Button()
        b0.set_label('Toutes frequences')
        B_ok = Gtk.Button()
        B_ok.set_label('OK')
        hbutton.pack_start(combolabel, False, False, 0)
        hbutton.pack_start(combo, False, False, 0)
        hbutton.pack_end(b_equation, False, False,0)
        hbutton.pack_end(B_ok, False, False,0)
        hbutton.pack_start(b0, False,False,0)
        B_ok.connect_object('clicked', lambda w: w.destroy(), window)

# Hbox choix vecteur en X

        # create a liststore with one string column to use as the model
        list_reftime = []
        liststore_X = Gtk.ListStore(str, str)
        filtremodele_X = liststore_X.filter_new()
        iter_X = liststore_X.append()
        liststore_X.set(iter_X, 0, ' ' , 1, ' ')
        self.dict_link_time = {'time':'lien'}

        ihm_choix_vecteurs = None
        montre_reftime_X = list_reftime[:]

        # create the TreeView using liststore
        treeview_X = Gtk.TreeView(model=liststore_X)
        selection_X = treeview_X.get_selection()
        treeview_X.set_model(filtremodele_X)

        b0.connect("clicked", self.reset_cb, champsaisie, 2*ind+11, combo, filtremodele_X, montre_reftime_X)
        b_equation.connect_object('clicked', self.bascule_equation_direct, B_Equation, self)
        b_equation_clear.connect("clicked", self.efface_equation, E_Equation)
#        b_equation_ok.connect("clicked", self.valid_operation_XY, E_Equation, self.liste_data_sort, self.liststore_X, self.liststore_Y)
        # create a CellRenderer to render the data
        cell_X = Gtk.CellRendererText()
        cell_X1 = Gtk.CellRendererText()

        # create the TreeViewColumns to display the data
        tvcolumn_X = Gtk.TreeViewColumn('Nom vecteur en X', cell_X, text=0)
        tvcolumn_X1 = Gtk.TreeViewColumn('ref_time', cell_X1, text=1)

        # add columns to treeview
        treeview_X.append_column(tvcolumn_X)
        treeview_X.append_column(tvcolumn_X1)

        # Allow sorting on the column
        tvcolumn_X.set_sort_column_id(0)
        tvcolumn_X1.set_sort_column_id(1)

        treeview_X.set_search_column(0)
        treeview_X.set_search_column(1)

        scrolledwindow_X.add(treeview_X)

# Hbox choix vecteur en Y

        # create a liststore with one string column to use as the model
        liststore_Y = Gtk.ListStore(str,str)
        filtremodele_Y = liststore_Y.filter_new()
        Iter_Y = liststore_Y.append()
        liststore_Y.set(Iter_Y, 0, ' ' , 1, ' ')

        montre_reftime_Y = list_reftime[:]
        filtremodele_Y.set_visible_func(self.visible_cb, montre_reftime_Y)

        # create the TreeView using liststore
        treeview_Y = Gtk.TreeView(model=liststore_Y)
        selection_Y = treeview_Y.get_selection()
        treeview_Y.set_model(filtremodele_Y)

        b0.connect("clicked", self.reset_cb, champsaisie, 2*ind+10, combo, filtremodele_Y, montre_reftime_Y)
        selection_Y.connect("changed", self.selection_cb, champsaisie, 2*ind+11, combo, None, None, None)
        selection_X.connect("changed", self.selection_cb, champsaisie, 2*ind+10, combo, filtremodele_Y, montre_reftime_Y, E_Equation)
        #combo.connect('changed', self.changed_choix_courbes, selection_X, selection_Y, self.liste_data_sort, filtremodele_Y, montre_reftime_Y, list_reftime)

        # create a CellRenderer to render the data
        cell_Y = Gtk.CellRendererText()

        # create the TreeViewColumns to display the data
        tvcolumn_Y = Gtk.TreeViewColumn('Nom vecteur en Y', cell_Y, text=0)

        # add columns to treeview
        treeview_Y.append_column(tvcolumn_Y)

        # Allow sorting on the column
        tvcolumn_Y.set_sort_column_id(0)

        # make treeview searchable
        treeview_Y.set_search_column(0)

        scrolledwindow_Y.add(treeview_Y)

        self.scroll = True

        window.add(vbox)
        window.show_all()
 #       progressbar.hide()
        if flg_equation == 0 :
            B_Equation.hide()
        thread1 = myThread(MonIhm, widget, champsaisie, ind, acqid,progressbar, liststore_X, filtremodele_X, montre_reftime_X, liststore_Y, filtremodele_Y, montre_reftime_Y, list_reftime, canvas)
        thread1.start()
        thread1.join()

    def Choix_vecteurs_sondage(self, widget, type_filter, champsaisie, ind, E_acqid):

        acqid = E_acqid.get_text()
        self.type_choix_serie = 'direct'
        if acqid == '' :
            message = "Attention Choix acquisition non rempli"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        try :
            rep_data = AIDA.ID_to_datapath(acqid)
        except AIDA.AidaError :
            message = "Attention Acqid non valid !"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        liste_data = recup_liste_vecteur(rep_data)
        if ( len(liste_data) == 0 ) :
            message = u"Pas de fichier pour l'acquisition " + acqid + " dans " + rep_data + "!"
            raise Abandon(message, Gtk.MessageType.ERROR)
            return

        liste_data.append("")
        liste_data_sort = sorted(liste_data, key = str.lower)

        # Creation d'une nouvelle fenetre
        window = Gtk.Window()
        window.set_title("Selection vecteurs")
        window.set_size_request(300, 800)

        vbox = Gtk.VBox(homogeneous=False, spacing=0)
        v2box = Gtk.VBox(homogeneous=False, spacing=0)
        eb = Gtk.EventBox()
        eb.add(v2box)
        eb.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(red = 00000, green = 60000, blue = 65535))

        boite_v_gene = Gtk.VBox(homogeneous=False, spacing=0)
        hbutton = Gtk.HBox(homogeneous=False, spacing=0)
        vbox.pack_start(eb, True, True, 2)
        vbox.pack_start(hbutton, False, True, 0)

# Hbox choix vecteur en Pression
        scrolledwindow_P = Gtk.ScrolledWindow()
        scrolledwindow_P.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        v2box.pack_start(scrolledwindow_P, True, True, 3)

        # create a liststore with one string column to use as the model
        self.list_reftime = []
        liststore_P = Gtk.ListStore(str, str)
        filtremodele_P = liststore_P.filter_new()
        nbv = 0
        nbc = 0
        self.dict_link_time = {'time':'lien'}
        Iter_P = liststore_P.append()
        liststore_P.set(Iter_P, 0, "")
        for fic in [f for f in liste_data_sort if f.startswith("pre")] :
            if ((fic.endswith("vbn.gz"))) :
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                fic_sans_ext = fic[0:len(fic)-4]
            try :
                info_vect = adpt.read_vect(acqid, fic_sans_ext, attributes_only = True )
                vector_time_P = info_vect.attributes["ref_time"]
                src = os.path.join(rep_data, vector_time_P)+'.vbn'
                try :
                    link_time = os.readlink(src)
                    if (vector_time_P in self.dict_link_time) == False :
                        self.dict_link_time[vector_time_P] = link_time[0:len(link_time)-4]
                        self.dict_link_time[link_time[0:len(link_time)-4]] = vector_time_P
                except OSError :
                    pass
            except :
                vector_time_P = " "

            iter_P = liststore_P.append()
            liststore_P.set(iter_P, 0, fic_sans_ext, 1, vector_time_P)
            if fic_sans_ext == self.graph_gene.graphes[ind].vecteur_Y  :
                nbc = nbv

            nbv = nbv + 1
            if not vector_time_P in self.list_reftime :
                self.list_reftime.append(vector_time_P)

        montre_reftime_P = self.list_reftime[:]
        filtremodele_P.set_visible_func(self.visible_cb, montre_reftime_P)

        # create the TreeView using liststore
        treeview_P = Gtk.TreeView(model=liststore_P)
        selection_P = treeview_P.get_selection()
        treeview_P.set_model(filtremodele_P)

        selection_P.select_path(nbc)

        # create a CellRenderer to render the data
        cell_P = Gtk.CellRendererText()
#        cell_P.set_property('font-desc', Pango.FontDescription("sans 8") )
        cell_P1 = Gtk.CellRendererText()
#        cell_P1.set_property('font-desc', Pango.FontDescription("sans 8") )

        # create the TreeViewColumns to display the data
        tvcolumn_P = Gtk.TreeViewColumn('Pression', cell_P, text=0)
        tvcolumn_P1 = Gtk.TreeViewColumn('ref_time', cell_P1, text=1)

        # add columns to treeview
        treeview_P.append_column(tvcolumn_P)

        # Allow sorting on the column
        tvcolumn_P.set_sort_column_id(0)

        treeview_P.set_search_column(0)

        scrolledwindow_P.add(treeview_P)

        separateur = Gtk.HSeparator()
        v2box.pack_start(separateur, False, True, 1)

# Hbox choix vecteur en Temperature
        scrolledwindow_T = Gtk.ScrolledWindow()
        scrolledwindow_T.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        v2box.pack_start(scrolledwindow_T, True, True, 3)

        # create a liststore with one string column to use as the model
        liststore_T = Gtk.ListStore(str, str)
        filtremodele_T = liststore_T.filter_new()
        nbv = 0
        nbc = 0
        iter_T = liststore_T.append()
        liststore_T.set(iter_T, 0, "")
        for fic in [f for f in liste_data_sort if f.startswith("tpr")] :
            if ((fic.endswith("vbn.gz"))) :
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                fic_sans_ext = fic[0:len(fic)-4]
            try :
                info_vect = adpt.read_vect(acqid, fic_sans_ext, attributes_only = True )
                vector_time_T = info_vect.attributes["ref_time"]
                src = os.path.join(rep_data, vector_time_T)+'.vbn'
                try :
                    link_time = os.readlink(src)
                    if (vector_time_T in self.dict_link_time) == False :
                        self.dict_link_time[vector_time_T] = link_time[0:len(link_time)-4]
                        self.dict_link_time[link_time[0:len(link_time)-4]] = vector_time_T
                except OSError :
                    pass
            except :
                vector_time_T = " "

            iter_T = liststore_T.append()
            liststore_T.set(iter_T, 0, fic_sans_ext, 1, vector_time_T)
            if fic_sans_ext == self.graph_gene.graphes[ind].vecteur_Y  :
                nbc = nbv
            nbv = nbv + 1

        montre_reftime_T = self.list_reftime[:]
        filtremodele_T.set_visible_func(self.visible_cb, montre_reftime_T)

        # create the TreeView using liststore
        treeview_T = Gtk.TreeView(model=liststore_T)
        selection_T = treeview_T.get_selection()
        treeview_T.set_model(filtremodele_T)
        selection_T.select_path(nbc)
        selection_T.connect("changed", self.selection_cb, champsaisie, 31, None, filtremodele_P, montre_reftime_P, None)
        selection_P.connect("changed", self.selection_cb, champsaisie, 30, None, filtremodele_T, montre_reftime_T, None)

        # create a CellRenderer to render the data
        cell_T = Gtk.CellRendererText()
        cell_T.set_property('font-desc', Pango.FontDescription("sans 8") )

        # create the TreeViewColumns to display the data
        tvcolumn_T = Gtk.TreeViewColumn('Temperature', cell_T, text=0)

        # add columns to treeview
        treeview_T.append_column(tvcolumn_T)

        # Allow sorting on the column
        tvcolumn_T.set_sort_column_id(0)

        # make treeview searchable
        treeview_T.set_search_column(0)

        scrolledwindow_T.add(treeview_T)

        separateur = Gtk.HSeparator()
        v2box.pack_start(separateur, False, True, 1)

# Hbox choix vecteur en T prime
        scrolledwindow_TP = Gtk.ScrolledWindow()
        scrolledwindow_TP.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        v2box.pack_start(scrolledwindow_TP, True, True, 3)

        # create a liststore with one string column to use as the model
        liststore_TP = Gtk.ListStore(str, str)
        filtremodele_TP = liststore_TP.filter_new()
        nbv = 0
        nbc = 0
#        for fic in liste_data_sort :
        iter_TP = liststore_TP.append()
        liststore_TP.set(iter_TP, 0, "")
        for fic in [f for f in liste_data_sort if f.startswith("tpr")] :
            if ((fic.endswith("vbn.gz"))) :
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                fic_sans_ext = fic[0:len(fic)-4]
            try :
                info_vect = adpt.read_vect(acqid, fic_sans_ext, attributes_only = True )
                vector_time_TP = info_vect.attributes["ref_time"]
                src = os.path.join(rep_data, vector_time_TP)+'.vbn'
                try :
                    link_time = os.readlink(src)
                    if (vector_time_TP in self.dict_link_time) == False :
                        self.dict_link_time[vector_time_TP] = link_time[0:len(link_time)-4]
                        self.dict_link_time[link_time[0:len(link_time)-4]] = vector_time_TP
                except OSError :
                    pass
            except :
                vector_time_TP = " "

            iter_TP = liststore_TP.append()
            liststore_TP.set(iter_TP, 0, fic_sans_ext, 1, vector_time_TP)
            if fic_sans_ext == self.graph_gene.graphes[ind].vecteur_Y  :
                nbc = nbv
            nbv = nbv + 1

        montre_reftime_TP = self.list_reftime[:]
        filtremodele_TP.set_visible_func(self.visible_cb, montre_reftime_TP)

        # create the TreeView using liststore
        treeview_TP = Gtk.TreeView(model=liststore_TP)
        selection_TP = treeview_TP.get_selection()
        treeview_TP.set_model(filtremodele_TP)
        selection_TP.select_path(nbc)
        selection_TP.connect("changed", self.selection_cb, champsaisie, 32, None, filtremodele_P, montre_reftime_P, None)
        selection_P.connect("changed", self.selection_cb, champsaisie, 30, None, filtremodele_TP, montre_reftime_TP, None)

        # create a CellRenderer to render the data
        cell_TP = Gtk.CellRendererText()
        cell_TP.set_property('font-desc', Pango.FontDescription("sans 8") )

        # create the TreeViewColumns to display the data
        tvcolumn_TP = Gtk.TreeViewColumn('T prim', cell_TP, text=0)

        # add columns to treeview
        treeview_TP.append_column(tvcolumn_TP)

        # Allow sorting on the column
        tvcolumn_TP.set_sort_column_id(0)

        # make treeview searchable
        treeview_TP.set_search_column(0)

        scrolledwindow_TP.add(treeview_TP)

        separateur = Gtk.HSeparator()
        v2box.pack_start(separateur, False, True, 1)

# Hbox choix vecteur en T rosee
        scrolledwindow_TR = Gtk.ScrolledWindow()
        scrolledwindow_TR.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        v2box.pack_start(scrolledwindow_TR, True, True, 3)

        # create a liststore with one string column to use as the model
        liststore_TR = Gtk.ListStore(str, str)
        filtremodele_TR = liststore_TR.filter_new()
        nbv = 0
        nbc = 0
#        for fic in liste_data_sort :
        iter_TR = liststore_TR.append()
        liststore_TR.set(iter_TR, 0, "")
        for fic in [f for f in liste_data_sort if f.startswith("hum")] :
            if ((fic.endswith("vbn.gz"))) :
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                fic_sans_ext = fic[0:len(fic)-4]
            try :
                info_vect = adpt.read_vect(acqid, fic_sans_ext, attributes_only = True )
                vector_time_TR = info_vect.attributes["ref_time"]
                src = os.path.join(rep_data, vector_time_TR)+'.vbn'
                try :
                    link_time = os.readlink(src)
                    if (vector_time_TR in self.dict_link_time) == False :
                        self.dict_link_time[vector_time_TR] = link_time[0:len(link_time)-4]
                        self.dict_link_time[link_time[0:len(link_time)-4]] = vector_time_TR
                except OSError :
                    pass
            except :
                vector_time_TR = " "

            iter_TR = liststore_TR.append()
            liststore_TR.set(iter_TR, 0, fic_sans_ext, 1, vector_time_TR)
            if fic_sans_ext == self.graph_gene.graphes[ind].vecteur_Y  :
                nbc = nbv
            nbv = nbv + 1

        montre_reftime_TR = self.list_reftime[:]
        filtremodele_TR.set_visible_func(self.visible_cb, montre_reftime_TR)

        # create the TreeView using liststore
        treeview_TR = Gtk.TreeView(model=liststore_TR)
        selection_TR = treeview_TR.get_selection()
        treeview_TR.set_model(filtremodele_TR)
        selection_TR.select_path(nbc)
        selection_TR.connect("changed", self.selection_cb, champsaisie, 33, None, filtremodele_P, montre_reftime_P, None)
        selection_P.connect("changed", self.selection_cb, champsaisie, 30, None, filtremodele_TR, montre_reftime_TR, None)

        # create a CellRenderer to render the data
        cell_TR = Gtk.CellRendererText()
#        cell_TR.set_property('font-desc', Pango.FontDescription("sans 8") )

        # create the TreeViewColumns to display the data
        tvcolumn_TR = Gtk.TreeViewColumn('Temperature du point de rosee', cell_TR, text=0)

        # add columns to treeview
        treeview_TR.append_column(tvcolumn_TR)

        # Allow sorting on the column
        tvcolumn_TR.set_sort_column_id(0)

        # make treeview searchable
        treeview_TR.set_search_column(0)

        scrolledwindow_TR.add(treeview_TR)

# Hbox choix vecteur V1
        scrolledwindow_V1 = Gtk.ScrolledWindow()
        scrolledwindow_V1.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        v2box.pack_start(scrolledwindow_V1, True, True, 3)

        # create a liststore with one string column to use as the model
        liststore_V1 = Gtk.ListStore(str, str)
        filtremodele_V1 = liststore_V1.filter_new()
        nbv = 0
        nbc = 0
        iter_V1 = liststore_V1.append()
        liststore_V1.set(iter_V1, 0, "")
        for fic in [f for f in liste_data_sort if (f.lower().startswith("ven_dd") or f.startswith("ven_e")) ] :
            if ((fic.endswith("vbn.gz"))) :
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                fic_sans_ext = fic[0:len(fic)-4]
            try :
                info_vect = adpt.read_vect(acqid, fic_sans_ext, attributes_only = True )
                vector_time_V1 = info_vect.attributes["ref_time"]
                src = os.path.join(rep_data, vector_time_V1)+'.vbn'
                try :
                    link_time = os.readlink(src)
                    if (vector_time_V1 in self.dict_link_time) == False :
                        self.dict_link_time[vector_time_V1] = link_time[0:len(link_time)-4]
                        self.dict_link_time[link_time[0:len(link_time)-4]] = vector_time_V1
                except OSError :
                    pass
            except :
                vector_time_V1 = " "

            iter_V1 = liststore_V1.append()
            liststore_V1.set(iter_V1, 0, fic_sans_ext, 1, vector_time_V1)
            if fic_sans_ext == self.graph_gene.graphes[ind].vecteur_Y  :
                nbc = nbv
            nbv = nbv + 1

        montre_reftime_V1 = self.list_reftime[:]
        filtremodele_V1.set_visible_func(self.visible_cb, montre_reftime_V1)

        # create the TreeView using liststore
        treeview_V1 = Gtk.TreeView(model=liststore_V1)
        selection_V1 = treeview_V1.get_selection()
        treeview_V1.set_model(filtremodele_V1)
        selection_V1.select_path(nbc)
        selection_V1.connect("changed", self.selection_cb, champsaisie, 34, None, filtremodele_P, montre_reftime_P, None)
        selection_P.connect("changed", self.selection_cb, champsaisie, 30, None, filtremodele_V1, montre_reftime_V1, None)

        # create a CellRenderer to render the data
        cell_V1 = Gtk.CellRendererText()
        cell_V1.set_property('font-desc', Pango.FontDescription("sans 8") )

        # create the TreeViewColumns to display the data
        tvcolumn_V1 = Gtk.TreeViewColumn('Vent DD ou n', cell_V1, text=0)

        # add columns to treeview
        treeview_V1.append_column(tvcolumn_V1)

        # Allow sorting on the column
        tvcolumn_V1.set_sort_column_id(0)

        # make treeview searchable
        treeview_V1.set_search_column(0)

        scrolledwindow_V1.add(treeview_V1)

# Hbox choix vecteur V2
        scrolledwindow_V2 = Gtk.ScrolledWindow()
        scrolledwindow_V2.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        v2box.pack_start(scrolledwindow_V2, True, True, 3)

        # create a liststore with one string column to use as the model
        liststore_V2 = Gtk.ListStore(str, str)
        filtremodele_V2 = liststore_V2.filter_new()
        nbv = 0
        nbc = 0
#        for fic in liste_data_sort :
        iter_V2 = liststore_V2.append()
        liststore_V2.set(iter_V2, 0, "")
        for fic in [f for f in liste_data_sort if (f.lower().startswith("ven_ff") or f.startswith("ven_n"))] :
            if ((fic.endswith("vbn.gz"))) :
                fic_sans_ext = fic[0:len(fic)-7]
            else :
                fic_sans_ext = fic[0:len(fic)-4]
            try :
                info_vect = adpt.read_vect(acqid, fic_sans_ext, attributes_only = True )
                vector_time_V2 = info_vect.attributes["ref_time"]
                src = os.path.join(rep_data, vector_time_V2)+'.vbn'
                try :
                    link_time = os.readlink(src)
                    if (vector_time_V2 in self.dict_link_time) == False :
                        self.dict_link_time[vector_time_V2] = link_time[0:len(link_time)-4]
                        self.dict_link_time[link_time[0:len(link_time)-4]] = vector_time_V2
                except OSError :
                    pass
            except :
                vector_time_V2 = " "

            iter_V2 = liststore_V2.append()
            liststore_V2.set(iter_V2, 0, fic_sans_ext, 1, vector_time_V2)
            if fic_sans_ext == self.graph_gene.graphes[ind].vecteur_Y  :
                nbc = nbv
            nbv = nbv + 1

        montre_reftime_V2 = self.list_reftime[:]
        filtremodele_V2.set_visible_func(self.visible_cb, montre_reftime_V2)

        # create the TreeView using liststore
        treeview_V2 = Gtk.TreeView(model=liststore_V2)
        selection_V2 = treeview_V2.get_selection()
        treeview_V2.set_model(filtremodele_V2)
        selection_V2.select_path(nbc)
        selection_V2.connect("changed", self.selection_cb, champsaisie, 35, None, filtremodele_P, montre_reftime_P, None)
        selection_P.connect("changed", self.selection_cb, champsaisie, 30, None, filtremodele_V2, montre_reftime_V2, None)

        # create a CellRenderer to render the data
        cell_V2 = Gtk.CellRendererText()
#        cell_V2.set_property('font-desc', Pango.FontDescription("sans 8") )

        # create the TreeViewColumns to display the data
        tvcolumn_V2 = Gtk.TreeViewColumn('Vent FF ou n', cell_V2, text=0)

        # add columns to treeview
        treeview_V2.append_column(tvcolumn_V2)

        # Allow sorting on the column
        tvcolumn_V2.set_sort_column_id(0)

        # make treeview searchable
        treeview_V2.set_search_column(0)

        scrolledwindow_V2.add(treeview_V2)

        b0 = Gtk.Button()
        b0.set_label('Toutes frequences')
        B_ok = Gtk.Button()
        B_ok.set_label('OK')
        hbutton.pack_end(B_ok, False, True, 0)
        hbutton.pack_start(b0, False, True, 0)
        B_ok.connect_object('clicked', lambda w: w.destroy(), window)
        window.add(vbox)
        window.show_all()

    def visible_cb(self, modele, Iter, donnees):
#        print(self, modele, Iter, donnees)
        return modele.get_value(Iter, 1) in donnees


def main(argv = None):


    # Récupération des arguments

    fmt_help = IndentedHelpFormatter(indent_increment=4,max_help_position=40, width=80, short_first=False)
    usage = "usage: %prog \n ou \n%prog acq_id paramêtre \n"
    parser = OptionParser(usage=usage, add_help_option=True, formatter=fmt_help)

    (options, args) = parser.parse_args()

    if len(args) < 2 :
        arg_acqid   = None
        arg_vecteur = None
    else :
        arg_acqid   = args[0]
        arg_vecteur = args[1]

    Create_IHM(arg_acqid, arg_vecteur)
    return 0

if __name__ == "__main__":

    main()
    Gtk.main()
