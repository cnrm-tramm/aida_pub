#!/usr/bin/env python3

"""
Created on 10 mai 2019

@author: CNRM/GMEI/TRAMM
"""

import os
import sys
import logging
import re
import glob
import shutil
import subprocess
import codecs
import argparse
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gdk, GtkSource
from gi.repository import GObject
from gi.repository import WebKit2 as webkit


AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))
AL = os.path.join(AH, 'lib', PYTHON_X_Y)

import AIDA
from edifil.Model.IHMbuilder import IHMbuider, Dialog_quiter_save
from edifil.Model.Model import model


__version__ = '2.0.0'

# TODO : j'ai ajouté un SchemeManger...
#      : peut-il éviter d'utiliser palette_XXX et d'avoir le
#      : warning : "DeprecationWarning: Gtk.Widget.override_color is deprecated" ?
palette_green = Gdk.RGBA( 46/255, 139/255,  87/255, 255/255)
palette_black = Gdk.RGBA(0  /255,   0/255,   0/255, 255/255)
palette_white = Gdk.RGBA(255/255, 255/255, 255/255, 255/255)
palette_red   = Gdk.RGBA(255/255,   0/255,   0/255, 255/255)

class IHM:
    # True si la save correspond au text actuel (pour la demande de save à la fermeture) 
    save_a_jour = True

    # adresse du fichier de sauvegarde
    save_path = None

    # utilisation des touches CTRL pour la selection multiple (1 si enfoncée, 0 sinon)
    touche_ctrl_etat = 0

    # si la touche entree est enfoncée
    entree_press = False
    windowContenu = None


    def __init__(self, args):
        self.builder = Gtk.Builder()
        the_path = os.path.join(AL, 'edifil', 'IHM.glade')
        self.builder.add_from_file(the_path)

        self.main_window = self.builder.get_object('gtkWindow')
        self.main_window.set_title(f"EdiFil-{__version__}")

        # La fenêtre sera fermée proprement
        self.main_window.connect('delete-event', self.ihm_quit)

        # Détection permettant de savoir CTRL est utilisée
        self.main_window.connect("key-press-event", self.on_key_press)
        self.main_window.connect("key-release-event", self.on_key_release) 
        # pareil pour le menu de recherche
        windowjournal = self.builder.get_object('gtkMenuRecherche')
        windowjournal.connect("key-press-event", self.on_key_press)

        # Clics sur les menus
        self.builder.get_object('btnMenu_new').connect('activate', self.menu_new, None)
        self.builder.get_object('btnMenu_open').connect('activate', self.menu_open)
        self.builder.get_object('btnMenu_save').connect('activate', self.menu_save)
        self.builder.get_object('btnMenu_save_as').connect('activate', self.menu_save_as)
        self.builder.get_object('btnMenu_quit').connect('activate', self.ihm_quit, '')
        self.builder.get_object('btnMenu_aide').connect('activate', self.onAideManuelActivate, '')

        self.builder.get_object('btn_launch').connect('clicked', self.btn_launch_press)
        self.builder.get_object('btn_doc').connect('clicked', self.btn_doc_press)
        self.builder.get_object('btn_search').connect('clicked', self.btn_search_press)
        self.builder.get_object('gtkMenuRecherche').connect('notify::visible', self.recherche_visi_change)
        self.builder.get_object('btn_redo').connect('clicked', self.btn_redo_press)
        self.builder.get_object('btn_undo').connect('clicked', self.btn_undo_press)
        self.builder.get_object('btn_test').connect('clicked', self.btn_test_press)
        self.builder.get_object('btn_save').connect('clicked', self.menu_save)
        self.builder.get_object('txt_recherche_doc').connect('changed', self.recherche_aide)

        # si l'acqid est modifié et si le texte est un acqid valide : $Chrono est chargé
        self.builder.get_object('txt_acqid').connect('changed', self.acqid_edit)

        # bien que marqué "non visible" dans le fichier glade, il semble que
        # set_visible() soit inopérant :
        # => modifier le contenu du label...
        self.INF_msg = self.builder.get_object('INF_msg')
        self.INF_msg.set_text('')

        # utilisation d'une font fixe pour ile panneau de description de
        # opérateur
        ## ajouté dans le fichier glade : self.builder.get_object('txt_info_oper').set_monospace('monospace 18')

        self.view_Gtk = GtkSource.View()
        self.view_Gtk.props.auto_indent = True
        self.view_Gtk.set_show_line_numbers(True)
        self.view_Gtk.set_show_line_marks(True)
        self.view_Gtk.set_monospace('monospace 18')

        Gtk.Buildable.set_name(self.view_Gtk,"text_view")
        self.builder.get_object('Window_zone_texte').add(self.view_Gtk)
        # nouveau model
        self.model = model()      
        self.ihm_builder = IHMbuider(self.view_Gtk, self.builder, self.model)
        # ajout du menu d'aide
        self.treeview = self.ihm_builder.aide_buider()

        self.builder.get_object('paned_doc').max_position = 300
        # Si le text est modifié
        self.view_Gtk.get_buffer().connect('changed', self.text_change)
        self.view_Gtk.connect("button-release-event", self.on_click) 
        self.view_Gtk.connect('undo', self.ihm_builder.verif_tout)
        self.view_Gtk.connect('redo', self.ihm_builder.verif_tout)

        # Creation du fichier .lang pour coloration syntaxique
        #logging.debug(f"==== {'IHM::__init__':15s} : AVANT creer_lang_file")
        nom_fic = self.ihm_builder.creer_lang_file()
        #logging.debug(f"==== {'IHM::__init__':15s} : APRES creer_lang_file : nom_fic = {nom_fic}")

        # Definition du scheme manager
        manager = GtkSource.StyleSchemeManager()
        paths = manager.get_search_path()
        the_path = os.path.join(AL, 'edifil')
        paths.append(the_path)
        manager.set_search_path(paths)
        self.scheme  = manager.get_scheme('edifil')

        # Definition du language
        lang_manager = GtkSource.LanguageManager()
        paths = lang_manager.get_search_path()
        the_path = os.path.join(os.sep, 'tmp')
        paths.append(the_path)
        lang_manager.set_search_path(paths)
        self.lang_manager_paths = lang_manager.get_search_path()

        # Chargement du fichier .lang
        self.view_Gtk.get_buffer().set_style_scheme(self.scheme)

        self.view_Gtk.get_buffer().set_language(lang_manager.get_language('fil'))
        logging.debug(f"==== {'IHM::__init__':15s} : APRES buffer set_language")

        # suppression du fichier .lang
        os.remove(nom_fic)

        # Ajout de l'auto-completion
        self.ihm_builder.set_auto_completion()

        # changement de la taille de l'ecran
        self.main_window.resize(1400, 800)

        self.main_window.show_all()

        # si un fichier est en paramètre, on l'ouvre
        for path in args.file :
            try :
                self.menu_open(None, path)
            except:
                raise

    def recherche_aide (self, widget):
        # suppression de l'ancienne version
        self.treeview.destroy()
        # texte recherché
        txt_recherche = self.builder.get_object('txt_recherche_doc').get_text()
        self.treeview = self.ihm_builder.aide_buider(txt_recherche)
        # si une recherche est en cour, on ouvre tout les onglets
        if txt_recherche != "":
            self.treeview.expand_all()
        self.main_window.show_all()


    def text_change (self, widget):
        """
        En cas de changement du text, on enregistre que la save n'est plus a
        jour et on vérifie si la ligne est valide.
        """
        #logging.debug(f"==== {'text_change':15s} : DEBUT : self.entree_press = {self.entree_press}")

        # SB le control de la ligne étant fait au fur et à mesure de la saisie
        # par l'utilisateur, il n'y a rien à faire lorsque la touche [ENTREE] a
        # été tapée...
        if self.entree_press:
            self.entree_press = False
            return

        self.save_a_jour = False
        # le changement du titre permet d'informer que le text n'est pas sauvegardé
        if self.save_path is None:
            self.main_window.set_title(f"EdiFil-{__version__}*")
        else:
            self.main_window.set_title(f"EdiFil-{__version__} : {self.save_path}*")
        # Récupération du texte
        buffer = self.view_Gtk.get_buffer()
        # numéro de la ligne
        ligne = buffer.get_iter_at_mark(buffer.get_insert()).get_line()

        ## SB --- DEBUT
        ## j'ai l'impression qu'en forçant ligne à ligne-1, on génère des
        ## problèmes pour les récupératio de start_iter/ebd_iter...
        ## SB# si on vient de faire un "à la ligne"
        ## SBif self.entree_press :
        ## SB    ligne -= 1
        ## SB --- FIN

        self.ihm_builder.verif_line(ligne)


    def btn_launch_press (self, widget):
        """
        Lance le code de la page (attention les fichiers sont réellement créés).
        """
        # demande des options de lancement
        user_opts = self.ihm_builder.demande_user_opts(1)
        path = self.save_path
        if user_opts is not None:
            # sauvegarde du texte
            if path is None:
                path = os.path.join(os.sep, 'tmp', 'edifil_save_tmp')
                self.ihm_builder.save(path)
            else :
                self.menu_save(None)

            # text entier du .fil
            buffer = self.view_Gtk.get_buffer()
            texte = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(),True)
            self.search_vecteur_list(texte)

            acqid = self.builder.get_object('txt_acqid').get_text()
            datapath = AIDA.ID_to_datapath(acqid)
            #logging.debug(f":::: datapath = {datapath}")

            # lance la commande
            ## TODO : si un xterm de RUN tourne déjà, le terminer et en relancer un nouveau
            title  = "'Edifil'" 
            PS1    = "'edifil-\w : '"
            msg    = "Lancer adp pour visualiser les vecteurs" 
            cmd = f"xterm -bg black -fg white -title {title} -e bash -c \"export PS1={PS1} ; adc {user_opts} {acqid} {path} ; cd {datapath} ; echo ; tput rev ; echo {msg} ; tput sgr0 ; echo && bash --noprofile --norc\""
            subprocess.Popen(cmd, shell=True)


    def search_vecteur_list (self, texte):
        """
        Donne une liste de tous les vecteurs de 'texte'.
        On utilise les familles pour les reconnaitre.
        """
        # construction du regex
        regex_txt = r'(\W('+ self.model.gest_vecteur.vect_list_famille[0]
        for famille in self.model.gest_vecteur.vect_list_famille[1:-1]:
            regex_txt += "|"+famille
        regex_txt += ')_[^ |\)|,|\n]*)'

        return [vecteur[0][1:] for vecteur in re.findall(regex_txt, texte,re.DOTALL)]

    def btn_doc_press (self, widget):
        """
        Ouvre la doc CATALOG_OPER.pdf de aida
        """        
        opener = "xdg-open"
        the_path = os.path.join(AH, 'doc', 'CATALOG_OPER.pdf')
        subprocess.Popen([opener, the_path])
        pass


    def btn_search_press (self, widget):
        """
        Ouvre la fenetre de recherche (CTRL F) 
        """
        self.ihm_builder.ouvrir_menu_recherche()


    def btn_redo_press (self, widget):
        """
        Annule le dernier redo (CTRL Y)
        """
        # La ligne en double c'est normal
        self.view_Gtk.do_redo(self.view_Gtk)
        self.view_Gtk.do_redo(self.view_Gtk)

        self.on_click()

    def btn_undo_press (self, widget):
        """
        Annule la dernière action (CTRL Z)
        """
        # La ligne en double c'est normal
        self.view_Gtk.do_undo(self.view_Gtk)
        self.view_Gtk.do_undo(self.view_Gtk)

        self.on_click()

    def btn_test_press (self, widget):
        """
        Test le code de la page (travaille dans le répertoire temporaire).
        """
        # demande confirmation
        reponse = self.ihm_builder.demande_validation()
        path = self.save_path
        if reponse:
            # sauvegarde du texte
            if path is None:
                path = os.path.join(os.sep, 'tmp', 'edifil_save_tmp')
                self.ihm_builder.save(path)
            else :
                self.menu_save(None)
                path = path.replace(" ","\\ ")

            # text entier du .fil
            buffer = self.view_Gtk.get_buffer()
            texte = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(),True)
            # on enleve les commentaires
            texte = re.sub(r"#.*", "", texte)

            vecteur_list = set(self.search_vecteur_list(texte))

            # copie des vecteurs dans le répertoirer temporaire
            acqid = self.builder.get_object('txt_acqid').get_text()
            datapath = AIDA.ID_to_datapath(acqid)   
            nom_plateforme, annee, num = AIDA.ID_to_full(acqid)
            new_datapath = os.path.join(os.sep, 'tmp', 'editest', nom_plateforme, annee, num)


            # Nouveau fichier (ou on le vide)
            try:
                os.system("rm -rf "+new_datapath)
            except:
                pass
            os.makedirs(new_datapath, exist_ok=True)

            for vecteur in vecteur_list:
                try:
                    shutil.copy2(os.path.join(datapath, vecteur+'.vbn'), new_datapath)
                except Exception as e :
                    pass

            # Copie des vecteurs temps
            for vecteur_temps in glob.glob(os.path.join(datapath, '*time*.vbn')) + glob.glob(os.path.join(datapath, '*TIME*.vbn')):
                try:
                    # préserver les liens
                    shutil.copy2(vecteur_temps, new_datapath, follow_symlinks=False)
                except Exception as e:
                    #print(e)
                    #logging.debug(f":::: Echec copie de : {vecteur_temps} vers {new_datapath}")
                    pass

            # lance la commande
            ## TODO : si un xterm de TEST tourne déjà, le terminer et en relancer un nouveau
            title  = f"'Edifil : test {path}'" 
            aidata = os.path.join(os.sep, 'tmp', 'editest')
            PS1    = "'edifil-\w : '"
            msg    = "Lancer adp pour visualiser les vecteurs" 
            cmd = f"xterm -bg white -fg black -title {title} -e bash -c \"export AIDA_DATA={aidata} ; export PS1={PS1} ; adc -F {acqid} {path} ; cd {new_datapath} ; echo ; tput rev ; echo {msg} ; tput sgr0 ; echo && bash --noprofile --norc\""
            subprocess.Popen(cmd, shell=True)

    def menu_new (self, widget, path):
        """
        Créé une nouvelle page.
        Si path = None , on ouvre une page vide.
        """
        if path is None:
            the_path = os.path.join(AH, 'bin', 'edifil')
            subprocess.Popen(the_path)
        else:
            the_path = os.path.join(AH, 'bin', 'edifil')
            subprocess.Popen([the_path, path])


    def menu_open (self, widget, path=None):
        """
        Ouvre une nouvelle page.
        Si la page actuelle est vide, la page est remplacée, sinon une seconde
        page est ouverte.

        :param str() path : Fichier a ouvrir, si None le menu pour choisir un
                            fichier est lancé
        """
        # text présent dans la page active
        debut = self.view_Gtk.get_buffer().get_start_iter()
        fin = self.view_Gtk.get_buffer().get_end_iter()
        text = self.view_Gtk.get_buffer().get_text(debut,fin,False)

        if path is None:
            path = self.ihm_builder.menu_charger()

        if path is None:        # si le path est None, on ne fait rien
            return False
        elif text == "":        # si le texte est vide on charge le fichier
            self.charger(path)
            self.save_a_jour = True
        else :                  # sinon, ouvrir une nouvelle page avec le contenu du fichier
            self.menu_new(None, path)


    def charger (self, file_path):
        """
        Gère le chargement et l'affichage du nouveau text
        param: 
            - file_path : String, addresse du fichier à charger
        """ 

        # Si l'adresse est None
        if file_path is not None:
            #Lecture du fichier
            print("charge de "+file_path)
            try : # ouvertur en UTF-8
                fichier = open(file_path, "r")
                self.save_path = file_path
                self.view_Gtk.get_buffer().set_text(fichier.read())
            except: # sinon ouverture en ISO-8859-15
                fichier = codecs.open(file_path, 'r', encoding='ISO-8859-15')
                self.save_path = file_path
                self.view_Gtk.get_buffer().set_text(fichier.read())

            self.main_window.set_title(f"EdiFil-{__version__} : {file_path}")
            self.ihm_builder.verif_tout(None,None)

    def menu_save (self, widget):
        """
        Sauvegarde la page (si aucun fichier de sauvegarde n'est defini, il est demandé)
        """
        # Si il n'y a pas de fichier de save, on ouvre save_as
        if self.save_path is None:
            return self.menu_save_as(None)
        else:
            self.ihm_builder.save(self.save_path)
            self.save_a_jour = True

            self.main_window.set_title(f"EdiFil-{__version__} : {self.save_path}")
            return True

    def menu_save_as (self, widget):
        """
        Sauvegarde la page en demandant le dossier de destination
        """
        path = self.ihm_builder.menu_save_as()

        if path is not None:
            self.save_a_jour = True
            self.save_path = path
            self.ihm_builder.save(self.save_path)
            self.main_window.set_title(f"EdiFil-{__version__} : {self.save_path}")
            return True
        return False

    def ihm_quit(self, widget, args):
        """
        Ferme proprement l'IHM
        """
	# Enregistrement du fichier

        if not self.save_a_jour:
            dialog = Dialog_quiter_save(self.builder.get_object('gtkWindow'))
            response = dialog.run()

            # Si on save
            if response == Gtk.ResponseType.YES:
                if self.menu_save(None):
                    Gtk.main_quit()
                else:
                    dialog.destroy()

            # Si on quite sans save
            elif response == Gtk.ResponseType.CLOSE:
                Gtk.main_quit()

            # Si on annule la fermeture de la page                
            dialog.destroy()    
            return True 

        else :
            Gtk.main_quit()

    def getChildByName(self, parent, name):
        """
        Cherche dans l'arboresscence un widget correspondant au nom à partir de parent.
        Ca fait la même chose que self.wTree.get_object de libglade si ce n'est 
        qu'on n'est pas obligé de rechercher depuis le sommet de l'arbre.
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


    def acqid_edit(self, widget):
        """
        si l'acqid est modifié et si il est valide, les données de $chrono liées sont chargés
        """
        logging.debug(f"\n==== {'acqid_edite':15s} : DEBUT")

        msg = { False: '.INF absent', True: '' }

        # texte du champ de recherche
        txt_recherche = self.builder.get_object('txt_recherche_doc').get_text()
        #logging.debug(f":::: txt_recherche = {txt_recherche}")
        #logging.debug(f":::: widget.get_text() = {widget.get_text()}")

        # validation de l'acqid
        self.acqid  = None
        inf_present = False
        acqid = widget.get_text()
        try:
            acqid_datapath = AIDA.ID_to_datapath(acqid)
            if os.path.isdir(acqid_datapath):
                self.acqid = acqid
            # présence du .INF
            inf_present = os.path.isfile(AIDA.ID_to_inf_path(self.acqid))
        except Exception as e:
            #logging.debug(f"==== EXCEPT : acqid = {acqid}, {e}")
            pass

        # mettre à jour les différents widget de l'IHM (les vider si l'acqid
        # n'est pas valide)
        if self.acqid: 
            #logging.debug(f"==== acqid_edite : self.acqid = {self.acqid}")
            ## deprecated widget.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("black"))
            widget.override_color(Gtk.StateFlags.NORMAL, palette_green)
            self.ihm_builder.aide_charger_chrono (self.acqid, txt_recherche)
            self.ihm_builder.aide_charger_vecteur(self.acqid, txt_recherche)

            # actualisation du language
            self.view_Gtk = self.ihm_builder.reset_source_view(self.lang_manager_paths, self.scheme)
            self.view_Gtk.get_buffer().connect('changed', self.text_change)
            self.view_Gtk.connect("button-release-event", self.on_click) 
            self.view_Gtk.connect('undo', self.ihm_builder.verif_tout)
            self.view_Gtk.connect('redo', self.ihm_builder.verif_tout)
            #logging.debug(f"==== acqid_edite : AVANT OK verif_tout('','')")
            self.ihm_builder.verif_tout("","")

            # on peut utiliser les boutons lancer et tester
            self.builder.get_object('btn_test').set_sensitive(True)
            self.builder.get_object('btn_launch').set_sensitive(True)

            # présence du .INF
            self.INF_msg.set_text(msg[inf_present])
        else:
            ## deprecated widget.modify_fg(Gtk.StateFlags.NORMAL, Gdk.color_parse("red"))
            widget.override_color(Gtk.StateFlags.NORMAL, palette_red)
            self.ihm_builder.aide_charger_chrono("")
            self.ihm_builder.aide_charger_vecteur("")

            # actualisation du language
            self.view_Gtk = self.ihm_builder.reset_source_view(self.lang_manager_paths, self.scheme)
            self.view_Gtk.get_buffer().connect('changed', self.text_change)
            self.view_Gtk.connect("button-release-event", self.on_click) 
            self.view_Gtk.connect('undo', self.ihm_builder.verif_tout)
            self.view_Gtk.connect('redo', self.ihm_builder.verif_tout)

            # on ne peut pas utiliser les boutons lancer et tester
            self.builder.get_object('btn_test').set_sensitive(False)
            self.builder.get_object('btn_launch').set_sensitive(False)


    def on_key_press(self, widget, ev, data=None):
        ''' Si une touche est enfoncée'''
        # Si entree est utilisé
        if ev.keyval == 65421 or ev.keyval == 65293:
            self.entree_press = True

        if ev.keyval == Gdk.KEY_Control_L or ev.keyval == Gdk.KEY_Control_R :
            self.touche_ctrl_etat = 1

        # si on appuie sur echap et que les menu du journal des actions est ouvert
        if (ev.keyval == Gdk.KEY_Escape and self.builder.get_object('gtkMenuRecherche').is_visible()):
            self.ihm_builder.fermer_menu_recherche(None,None)

        # Si ctrl-F : on ouvre le menu de recherche
        if ev.keyval == 102 and self.touche_ctrl_etat == 1:
            self.ihm_builder.ouvrir_menu_recherche()

        # Si ctrl-S : on sauvegarde
        if ev.keyval == 115 and self.touche_ctrl_etat == 1:
            self.menu_save(None)

    def on_key_release(self, widget, ev, data=None):
        ''' Si une touche est relachée'''

        # -- Affichage description de la ligne --
        buffer = self.view_Gtk.get_buffer()
        ligne = buffer.get_iter_at_mark(buffer.get_insert()).get_line()

        if self.entree_press :
            ligne -= 1
        # texte de la ligne
        start_line = buffer.get_iter_at_line(ligne)
        end_line = start_line.copy()
        end_line.forward_to_line_end();

        texte = buffer.get_text(start_line, end_line, False)
        oper = re.findall(r'^[ (]*([^ (]*)', texte,re.DOTALL)[0]
        self.ihm_builder.update_info_oper(oper)

        # Si entree et utilisé
        if ev.keyval == 65421 or ev.keyval == 65293:
            self.entree_press = False

        if ev.keyval == Gdk.KEY_Control_L or ev.keyval == Gdk.KEY_Control_R :
            self.touche_ctrl_etat = 0


    def recherche_visi_change(self, widget,event):
        """
        Detect quand la propriété visibility change de la fenetre recherche change d'état
        """
        self.touche_ctrl_etat = 0

    def on_click(self,widget = None, event = None):
        """
        Si un clic est réalisé sur la TextView
        Mise ajour de la description de l'opérateur
        """ 
        # -- Affichage description de la ligne --
        buffer = self.view_Gtk.get_buffer()
        ligne = buffer.get_iter_at_mark(buffer.get_insert()).get_line()

        if self.entree_press :
            ligne -= 1
        # texte de la ligne
        start_line = buffer.get_iter_at_line(ligne)
        end_line = start_line.copy()
        end_line.forward_to_line_end();

        texte = buffer.get_text(start_line, end_line, False)
        oper = re.findall(r'^[ (]*([^ (]*)', texte,re.DOTALL)[0]
        self.ihm_builder.update_info_oper(oper)
    
    
    def onAideManuelActivate(self,widget = None, envent = None):
        """
        Crée la fenêtre d'aide (contenu) qui affiche les pages html.
        """         
        def destroyContenu(w):
            self.windowContenu = None
                
        if self.windowContenu is None :
            self.windowContenu = Gtk.Window()
            self.windowContenu.connect("destroy", destroyContenu)
            self.windowContenu.set_title("Aide - Edifil")       
            web = webkit.WebView()
            web.set_size_request(903,607)
            web.load_uri("file://"+AL+"/edifil/doc/index.html")       
            self.windowContenu.add(web)
            self.windowContenu.show_all()
            self.windowContenu.set_resizable(False)
        else :
            self.windowContenu.present()

if __name__ == '__main__':
    
    ## SB --- DEBUT
    ## TODO : supprimer ma bidouille
    if '-v' in sys.argv:
        from gi.repository import Gtk
        print(f"gi  version = {gi.version_info}")
        print(f"Gkt version = {Gtk.MAJOR_VERSION}.{Gtk.MINOR_VERSION}.{Gtk.MICRO_VERSION}")
        sys.exit(0)

    if '-V' in sys.argv:
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)
        i = sys.argv.index('-V')
        del sys.argv[i]
    else:
        logging.basicConfig(format='%(message)s')
    ## SB --- FIN

    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="*", help="un ou plusieurs fichiers de commandes (.fil).")

    args = parser.parse_args()
    #logging.debug(f"==== MAIN ----------- args = {args} ")
    IHM(args)
    
    Gtk.main()
    pass


