#!/usr/bin/env python3

"""
Created on 10 mai 2019

@author: CNRM/GMEI/TRAMM

Gere :
    - la fonction de recherche
    - le treeView d'aide
    - la creation des nouvelles fenetres
    et une grande partie de fonctions utilisé par edifil_main.py
"""

import os
import sys
import logging
import re
import gi
import codecs
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, Gdk, GtkSource, GObject

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

from Fil_analyze import parse_instruction


more_error_msg = "\n  - les strings doivent être encloses dans des doubles quotes" +\
                 "\n  - les numériques ne doivent pas être enclos dans des quotes" +\
                 "\n  - le séparateur décimal pour les floats est le caractère point" +\
                 "\n  - le nom d'un vecteur doit commencer par les 3 lettres d'une famille suivi d'un caractère _"

class IHMbuider(object):
    recherche_nb_element = 0
    recherche_element_actuel = 0
    ERR_MARK_1 = "Marque1"
    derniere_recherche_est_suivant = True
    # Nome de l'opérateur dont la description est affiché
    nom_oper_affiche = None

    # Liste de String donnant tout les nom des onglets du menus d'aide
    menu_liste= []

    def __init__(self, view_Gtk, builder, model):
        self.view_Gtk = view_Gtk
        self.builder  = builder
        self.model    = model
        self.buffer   = self.view_Gtk.get_buffer()
        self.builder.get_object('gtkMenuRecherche').connect('delete-event', self.fermer_menu_recherche)

        # Boutons du menu de recherche
        self.builder.get_object('btn_trouver').connect('clicked', self.recherche_btn_trouver)
        self.builder.get_object('btn_remplacer').connect('clicked', self.recherche_btn_remplacer)
        self.builder.get_object('btn_remplacer_trouver').connect('clicked', self.recherche_btn_trouver_remplacer)
        self.builder.get_object('btn_remplacer_tout').connect('clicked', self.recherche_btn_remplacer_tout)

        # Le menu de recherche ne peut pas être caché par la page principale
        self.builder.get_object('gtkMenuRecherche').set_transient_for(self.builder.get_object('gtkWindow'))

        # si du texte est collé
        self.buffer.connect('paste-done', self.verif_tout)

        # Resultat de recherche de la fonction find (vide a l'ini)
        self.result = ""
        # Derniere string recherché (pour comparaison avec le nouveau)
        # (En cas de changement la recherche et remise à zero)
        self.search_text = ""

        self.cursor_mark = ""

    def ouvrir_menu_recherche(self):
        """
        Ouvre le menu de recherche
        """
        #logging.debug(f":::: {'ouvrir_menu_recherche':25s} : DEBUT")
        # Affichage du menu de recherche
        self.builder.get_object('gtkMenuRecherche').set_position(Gtk.WindowPosition.CENTER)
        self.builder.get_object('gtkMenuRecherche').set_visible(True)

    def fermer_menu_recherche(self, widget, arg):
        """
        ferme le menu de recherche
        """
        self.builder.get_object('gtkMenuRecherche').set_visible(False)
        self.search_text = ""
        self.result = ""
        return True

    def recherche_btn_trouver(self, widget):
        """
        bouton trouver le menu de recherche
        """
        # Si le text recherché a changé (on recommence)
        if self.builder.get_object('txtbox_chercher').get_text() != self.search_text:
            self.search_text = self.builder.get_object('txtbox_chercher').get_text()
            self.result = ""

            # Nombre d'éléments correspondant

            text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
            self.recherche_nb_element = text.count(self.search_text)
            self.recherche_element_actuel = 0

        else:
            self.result = self.view_Gtk.get_buffer().get_iter_at_mark(self.cursor_mark)
            text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)
            self.recherche_nb_element = text.count(self.search_text)
        # Si il n'y a aucun résultat on éfface l'indicateur de position
        if self.recherche_nb_element == 0:
            self.builder.get_object('lbl_nb_elements').set_text("")

        # si on cherche le suivant
        if self.builder.get_object('radbtn_suivant').get_active() == True:

            match_start = self.result if self.result else self.buffer.get_start_iter()
            result = match_start.forward_search(self.search_text, 0, None)
            if result:
                match_start, match_end = result
                self.buffer.select_range(match_start, match_end)

                #Déplacement de la camera sur le curseur
                self.cursor_mark = self.buffer.create_mark("cursor_mark", match_start)
                self.view_Gtk.scroll_mark_onscreen(self.cursor_mark)

                # sauvegarde de la position de la recherche
                #(si on save le textIter directement, crash si modif du text)
                self.cursor_mark = match_end.get_marks()[0]

                self.result = result

                # l'affichage bug si ont chage de sens car le premier clic ne marche pas
                if not self.derniere_recherche_est_suivant:
                    self.recherche_element_actuel -= 1
                    self.derniere_recherche_est_suivant = True
                else:
                    self.derniere_recherche_est_suivant = True

                #affichage element actuel
                if self.recherche_element_actuel < self.recherche_nb_element :
                    self.recherche_element_actuel += 1
                self.builder.get_object('lbl_nb_elements').set_text(str(self.recherche_element_actuel)+
                                                                   "/"+str(self.recherche_nb_element))

        else : # Si on cherche le precedent
            match_start = self.result if self.result else self.buffer.get_end_iter()
            result = match_start.backward_search(self.search_text, 0, None)
            if result:
                match_start, match_end = result
                self.buffer.select_range(match_start, match_end)

                #Déplacement de la camera sur le curseur
                self.cursor_mark = self.buffer.create_mark("cursor_mark", match_end)
                self.view_Gtk.scroll_mark_onscreen(self.cursor_mark)

                # sauvegarde de la position de la recherche
                #(si on save le textIter directement, crash si modif du text)
                self.cursor_mark = match_start.get_marks()[0]

                self.result = result

                # l'affichage bug si ont chage de sens car le premier clic ne marche pas
                if self.derniere_recherche_est_suivant:
                    self.recherche_element_actuel += 1
                    self.derniere_recherche_est_suivant = False
                else:
                    self.derniere_recherche_est_suivant = False

                #affichage element actuel
                if self.recherche_element_actuel > 1 :
                    self.recherche_element_actuel -= 1
                self.builder.get_object('lbl_nb_elements').set_text(str(self.recherche_element_actuel)+
                                                                   "/"+str(self.recherche_nb_element))

    def recherche_btn_remplacer(self, widget):
        """
        Ouvre le menu de recherche
        """
        # si il y a une selection, on remplace
        selection = self.buffer.get_selection_bounds()
        if selection != () and selection[0] != selection[1]:
            text = self.builder.get_object('txtbox_remplacer').get_text()

            self.buffer.delete_selection(True,True)
            self.ajouter_text(text)

    def recherche_btn_trouver_remplacer(self, widget):
        """
        bouton trouver/remplacer le menu de recherche
        """
        # Si il n'y a pas de selection, on fait juste une recherche
        selection =  self.buffer.get_selection_bounds()
        if selection == () or selection[0] == selection[1]:
            self.recherche_btn_trouver(None)
        else:
            if self.builder.get_object('radbtn_suivant').get_active() == True:
                self.recherche_element_actuel -= 1
            self.recherche_btn_remplacer(None)
            self.recherche_btn_trouver(None)

    def recherche_btn_remplacer_tout(self, widget):
        """
        bouton remplacer_tout le menu de recherche
        """
        # search_text est mis a null, on ne prend pas en compte la position
        # du curseur mais on remplace dans toute la page
        self.search_text = ""
        # Recherche du premier element
        self.recherche_btn_trouver(None)
        #Tant qu'il y a des éléments à remplacer, on continue
        selection = self.buffer.get_selection_bounds()
        while selection != () and selection[0] != selection[1]:
            self.recherche_btn_trouver_remplacer(None)
            selection = self.buffer.get_selection_bounds()


    def aide_buider(self,search_txt = ""):
        """
        Crée le treeView du menu aide (à gauche de l'écrant)
        Le parametre search_txt permet de filtrer les éléments à afficher
            Si une ligne ne contient pas le txt, elle n'est pas affichée
            Si search_txt = "" tout est affiché
        return : le treeView complet
        """

        # Creation d'un TreeStore avec une colonne de type chaine, pour servir de modele
        self.treestore = Gtk.TreeStore(str)
        # Ajoutons des donnees

        # Ajout des Constantes
        self.const_iter = self.treestore.append(None, ["Constantes"])
        # Save du nom du chapitre
        self.menu_liste += ["Constantes"]
        for const in sorted(self.model.gest_arg_spe.constantes.arg_list, key=str.lower):
            if search_txt == "" :
                self.treestore.append(self.const_iter, [const])
            elif search_txt.lower() in const.lower(): # Si il y a un filtre
                self.treestore.append(self.const_iter, [const])


        # Ajout des argChrono
        self.chrono_iter = self.treestore.append(None, ["$Chrono"])
        # Save du nom du chapitre
        self.menu_liste += ["$Chrono"]
        for chrono in sorted(self.model.gest_arg_spe.argChrono.arg_list, key=str.lower):
            if search_txt == "" :
                self.treestore.append(self.chrono_iter, [chrono])
            elif search_txt.lower() in chrono.lower(): # Si il y a un filtre
                self.treestore.append(self.chrono_iter, [chrono])

        # Ajout des $Arg par n° (de 1 à 9, ça devrait suffire)
        # TODO : limiter la liste à la valeur 'nb_vectors_in' de chaque
        #      : 'opération' (operator)
        #      : peut-être en jouant avec une colonne "visible" (https://stackoverflow.com/questions/32072487/pygtk-set-checkbox-in-the-treeview-of-a-specific-row-invisible)
        self.const_arg = self.treestore.append(None, ["$Arg"])
        self.menu_liste += ["$Arg"]
        for i in range(1, 10):
            # Save du nom du chapitre
            self.menu_liste += [f'{i}']
            # ajout de l'onglet du n°
            arg_number = self.treestore.append(self.const_arg, [f'{i}'])
            # ajout des champs
            for arg in sorted(self.model.gest_arg_spe.arguments.arg_list, key=str.lower):
                if search_txt == "" :
                    self.treestore.append(arg_number, [f'$Arg{i}.{arg}'])
                elif search_txt.lower() in arg.lower(): # Si il y a un filtre
                    self.treestore.append(arg_number, [f'$Arg{i}.{arg}'])

        # Ajout des vecteur
        self.const_vect = self.treestore.append(None, ["Vecteurs"])
        # Save du nom du chapitre
        self.menu_liste += ["Vecteurs"]
        for vecteur in self.model.gest_vecteur.vect_list:
            if search_txt == "" :
                self.treestore.append(self.const_vect, [vecteur])
            elif search_txt.lower() in vecteur.lower(): # Si il y a un filtre
                self.treestore.append(self.const_vect, [vecteur])

        # Ajout des operateur par chapitre
        self.const_oper = self.treestore.append(None, ["Operateurs"])
        self.menu_liste += ["Operateurs"]
        for chapitre in self.model.gest_oper.oper_list_par_chap:
            # Save du nom du chapitre
            self.menu_liste += [chapitre[0]]
            # ajout de l'onglet du chapitre
            chap = self.treestore.append(self.const_oper, [chapitre[0]])
            # ajout des opérateurs
            for operateur in sorted([operateur.nom for operateur in chapitre[1]], key=str.lower):
                if search_txt == "" :
                    self.treestore.append(chap, [operateur])
                elif search_txt.lower() in operateur.lower(): # Si il y a un filtre
                    self.treestore.append(chap, [operateur])

        # Ajout de lignes inutile pour pouvoir lire la description des derniers
        # operateurs sinon (hors écran)
        for x in range (10):
            self.treestore.append(self.const_oper, [""])

        # creation du TreeView en utilisant notre TreeStore
        self.treeview = Gtk.TreeView(self.treestore)

        # creation du TreeViewColumn pour afficher les donnees
        self.tvcolumn = Gtk.TreeViewColumn('Documentation')

        # on place tvcolumn dans notre TreeView
        self.treeview.append_column(self.tvcolumn)

        # creation d'un CellRendererText pour afficher les donnees
        self.cell = Gtk.CellRendererText()
        # on place cell dans le TreeViewColumn et on lui permet de s'etirer
        self.tvcolumn.pack_start(self.cell, True)

        # reglage de l'attribut "text" de cell sur la colonne 0 - recupere le
        # texte dans cette colonne du TreeStore
        self.tvcolumn.add_attribute(self.cell, 'text', 0)

        # Gestion des infobulles
        self.treeview.set_property("has-tooltip", True)
        self.treeview.connect('query-tooltip', self.on_treeServers_tooltip)

        # Reception du double-clic sur le menu
        self.treeview.connect('row_activated', self.menu_aide_double_click)

        self.builder.get_object('view_aide').add(self.treeview)
        self.treeview.set_enable_search(False)
        return self.treeview

    def menu_aide_double_click(self, tree_view, path, column):
        """
        Si un utilisateur double clic sur une ligne du menu aide,
        le text correspondant est ajouté sur la page
        """

        treestore, selected_treepaths = tree_view.get_selection().get_selected_rows()
        selected_treepath             = selected_treepaths[0] # only one row can be selected
        selected_row                  = treestore[selected_treepath]
        texte                         = selected_row[0] # index 0 because this is a TreeStore with only one item of type str
        ### print(f"==== texte       = {texte}")

        selection = self.buffer.get_selection_bounds()
        if texte not in self.menu_liste:
            # Si c'est un opérateur
            oper = self.model.gest_oper.get(texte)
            #logging.debug(f":::: {'menu_aide_double_click':25s} : texte = {texte}, oper = {oper}")

            if oper is not None:
                # texte comportant le nom et les arguments de l'opérateur
                oper_texte = oper.nom + "("+oper.args[0][0]
                for args in oper.args[1:]:
                    oper_texte += ", "+args[0]
                oper_texte += ")\n"

                if selection != () and selection[0] != selection[1]:
                    self.buffer.delete_selection(True,True)
                    self.ajouter_text(oper_texte)
                else:
                    self.ajouter_text(oper_texte)
            else:
                # si c'est un $chrono, ajout du $CHRONO avant
                if self.model.gest_arg_spe.argChrono.exist(texte):
                    texte = '$Chrono.'+texte


                self.buffer.delete_selection(True,True)
                self.ajouter_text(texte)

            # -- Affichage description de la ligne --
            try :
                self.update_info_oper(oper.nom)
            except:
                pass


    def update_info_oper(self, nom_oper):
        """
        Affiche la description de l'operateur en argument dans le champ info_oper (en bas de l'interface)
        Verifie si c'est nécessaire en comparant le nom de l'opérateur affiché avec le nouveau
        """
        try :
            if nom_oper != self.nom_oper_affiche:
                txt = nom_oper+"\n----------------------------------\n"
                self.nom_oper_affiche = nom_oper

                # récupération de la description
                txt += self.model.gest_oper.get(nom_oper).description

                # mise a jour de l'affichage
                self.builder.get_object('txt_info_oper').get_buffer().set_text(txt)
            return True
        except:
            return False

    def aide_charger_chrono(self, acqid, search_txt=""):
        """
        Charge les chronos d'un acqid et actualise l'onglet d'aide
        param : acqid (String) acqid dont ont veut les chronos
        """

        # On vide l'onglet
        self.treestore.remove(self.chrono_iter)

        #on recrée l'onglet
        self.chrono_iter = self.treestore.insert(None, 1, ["$Chrono ("+acqid+")"])

        # Sauvegarde du nouveau nom du chapitre
        self.menu_liste[1] = "$Chrono ("+acqid+")"

        # on charge chrono avec l'acqid
        self.model.gest_arg_spe.argChrono.load(acqid)
        for chrono in sorted(self.model.gest_arg_spe.argChrono.arg_list, key=str.lower):
            if search_txt == "" :
                self.treestore.append(self.chrono_iter, [chrono])
            elif search_txt.lower() in chrono.lower(): # Si il y a un filtre
                self.treestore.append(self.chrono_iter, [chrono])

    def aide_charger_vecteur (self, acqid,search_txt = ""):
        """
        Charge les vecteurs d'un acqid et actualise l'onglet d'aide
        param : acqid (String) acqid dont ont veut les vecteurs
        """
        # On vide l'onglet
        self.treestore.remove(self.const_vect)

        #on recrée l'onglet
        self.const_vect = self.treestore.insert(None, 3, ["Vecteurs ("+acqid+")"])

        # Sauvegarde du nouveau nom du chapitre
        self.menu_liste[3] = "Vecteurs ("+acqid+")"
        # on charge chrono avec l'acqid
        self.model.gest_vecteur.load(acqid)
        for vecteur in sorted(self.model.gest_vecteur.vect_list, key=str.lower):
            if search_txt == "" :
                self.treestore.append(self.const_vect, [vecteur])
            elif search_txt.lower() in vecteur.lower(): # Si il y a un filtre
                self.treestore.append(self.const_vect, [vecteur])

    def on_treeServers_tooltip(self, widget, x, y, keyboard, tooltip):
        """
        Gère les info-bules du treeView
        """
        x,y = widget.convert_widget_to_bin_window_coords(x, y)
        pos = widget.get_path_at_pos(x, y)
        if pos:
            model = widget.get_model()
            tree_iter = model.get_iter(pos[0])
            # Nom de la ligne
            value = model.get_value(tree_iter,0)

            # Description
            if self.model.gest_oper.exist(value):
                # c'est un operateur, on affiche la description
                description = self.model.find_description(value)
                tooltip.set_markup(description[0])
            elif self.model.gest_arg_spe.exist_constante(value):
                # c'est une constante, on affiche la description
                description = self.model.gest_arg_spe.get_constante_tooltip(value)
                tooltip.set_markup(description)
            else:
                tooltip.set_markup(value)

            widget.set_tooltip_row(tooltip,pos[0])
        return True

    def menu_charger (self):
        """
        Affiche la fenetre de selection de fichier et retourne
        le chemin du fichier choisit
        """
        dialog = Gtk.FileChooserDialog("OUVRIR : Veuillez choisir un fichier",
            self.builder.get_object('gtkWindow'),
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_py = Gtk.FileFilter()
        filter_py.set_name(".fil")
        filter_py.add_pattern("*.fil")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

        response = dialog.run()
        if response == Gtk.ResponseType.OK and dialog.get_filename().endswith(".fil"):
            # nouvelle plateforme, elle est définit
            file = dialog.get_filename()

            dialog.destroy()
            return file

        dialog.destroy()
        return None


    def menu_save_as(self):
        """
        Affiche la fenetre de selection de fichier et retourne
        le chemin du fichier choisit
        """
        dialog = Gtk.FileChooserDialog("AJOUTER : Veuillez choisir un fichier", self.builder.get_object('gtkWindow'),
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        while True:
            response = dialog.run()
            # Si la page n'a pas été fermé
            if response != Gtk.ResponseType.CANCEL and response != Gtk.ResponseType.DELETE_EVENT :
                fileName = dialog.get_filename()
                # Si l'extension .txt n'est pas présente a la fin, elle et ajouté
                if fileName[-4:]!=".fil":
                    fileName+=".fil"

                # si le fichier existe deja, on demande confirmation
                if not os.path.exists(fileName) or os.path.exists(fileName) and\
                    self.demande_validation("    Le fichier existe déjà :\nVoulez vous le remplacer ?"):

                    dialog.destroy()
                    return fileName

            else:
                dialog.destroy()
                return None


    def save(self,path):
        """
        sauvegarde le code de la page dans le fichier path au format ISO-8859-15
        """
        #file = open(path,"w+")
        #
        #file.write(self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True))
        #file.close()
        file = codecs.open(path, "w", "ISO-8859-15")
        file.write(self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True))
        file.close()


    def reset_source_view(self, lang_manager_paths, scheme):
        """
        Actualise le champ de texte principal lors du changement d'acqid
        """
        logging.debug(f"==== {'reset_source_view':15s} : DEBUT")
        nom_fic = self.creer_lang_file()
        logging.debug(f"==== {'reset_source_view':15s} : APRES creer_lang_file")

        # On sauvegarde le text
        code_text = self.buffer.get_text(self.buffer.get_start_iter(), self.buffer.get_end_iter(), True)

        # Suppression du GtkSource.View
        self.view_Gtk.destroy()

        # Ajout d'un nouveau GtkSource.View
        self.view_Gtk = GtkSource.View()
        self.view_Gtk.props.auto_indent = True
        self.view_Gtk.set_show_line_numbers(True)
        self.view_Gtk.set_show_line_marks(True)

        self.buffer = self.view_Gtk.get_buffer()

        # Ajout de l'auto-completion
        self.set_auto_completion()

        # Definition du language
        lang_manager = GtkSource.LanguageManager()
        lang_manager.set_search_path(lang_manager_paths)
        
        Gtk.Buildable.set_name(self.view_Gtk,"text_view")
        self.builder.get_object('Window_zone_texte').add(self.view_Gtk)
        self.buffer.set_language(lang_manager.get_language('fil'))
        # ... et le scheme manager 
        self.view_Gtk.get_buffer().set_style_scheme(scheme)
        logging.debug(f"==== {'reset_source_view':15s} : APRES scheme")

        # Chargement du fichier .lang
        self.view_Gtk.get_buffer().set_language(lang_manager.get_language('fil'))
        logging.debug(f"==== {'reset_source_view':15s} : get_language('fil')")

        self.builder.get_object('gtkWindow').show_all()

        # Ajout du texte
        self.buffer.set_text(code_text)

        # suppression du fichier .lang
        os.remove(nom_fic)

        return self.view_Gtk


    def creer_lang_file (self):
        """
        Creer un fichier .lang pour la coloration syntaxique
        return : le nom du fichier crée

        NOTE :
        - on trouve des définitions de langage dans :
            /usr/share/gtksourceview-3.0/language-specs
        - on trouve des définitions de style dans :
            /usr/share/gtksourceview-3.0/styles/

        NOTE :
        j'ai voulu créer des styles 'opertaeur', 'vecteur' et 'string', mais
        je n'ai pas bien réussi...
        => pour le moment :
          - les opérateurs sont colorisés par def:statement
          - les vecteurs   sont colorisés par def:type
          - les chaînes    sont colorisés par def:doc-comment-element
        """
        logging.debug(f"==== {'creer_lang_file':15s} : DEBUT")

        text = """<?xml version="1.0" encoding="UTF-8"?>
<language id="fil" name="fil" version="2.0" _section="Source">

  <styles>
    <style id="comment"     name="Comment"     map-to="def:comment"/>
    <style id="operateur"   name="Operateur"   map-to="def:statement"/>
    <style id="vecteur"     name="Vecteur"     map-to="def:type"/>
    <style id="arguments"   name="Arguments"   map-to="def:constant"/>
    <style id="DollarArg"   name="DollarArg"   map-to="def:constant"/>
    <style id="String"      name="String"      map-to="def:doc-comment-element"/>
    <style id="float_perso" name="float_perso" map-to="def:constant"/>
  </styles>

  <definitions>
    <context id="fil">
      <include>
        <context id="DollarArg" style-ref="DollarArg">
            <start>\\$</start>
            <end>\\.</end>
        </context>

        <context id="String" style-ref="String">
            <start>\\"</start>
            <end>\\"</end>
        </context>

        <context id="comment" style-ref="comment">
          <start>#</start>
          <end>$</end>
        </context>

        <context id="float_perso" style-ref="float_perso">
          <match extended="true">
            ([+-]?(\s)*(\d+)?\.\d*)([eE]?[+-]?\d*)
          </match>
        </context>

        <context ref="def:decimal"/>
        """

        text +="""
        <context id="operateur" style-ref="def:statement">"""
        # ajout des vecteurs
        for oper in self.model.gest_oper.oper_list:
            text += "\n\t\t  <keyword>"+oper.nom+"</keyword>"
        text += "\n\t\t</context>\n"

        # ajout des Constantes
        text += """\n\t\t<context id="arguments" style-ref="arguments">"""
        for const in self.model.gest_arg_spe.constantes.arg_list:
            text += "\n\t\t  <keyword>"+const+"</keyword>"

        # ajout des $argChrono
        for chrono in self.model.gest_arg_spe.argChrono.arg_list:
            text += "\n\t\t  <keyword>"+chrono+"</keyword>"

        # ajout des $Arg
        for arg in self.model.gest_arg_spe.arguments.arg_list:
            text += "\n\t\t  <keyword>"+arg+"</keyword>"

        text +="""
        </context>

        """

        text +="""
        <context id="vecteur" style-ref="def:type">
          <start>("""
        # si il n'y a pas de famille en mémoire
        if len(self.model.gest_vecteur.vect_list_famille) < 1:
            text += "ezgoqpfzfazfazf" # ça ne devrait pas match par erreur
        # ajout des familles pour définir les vecteurs 
        else:
            text += self.model.gest_vecteur.vect_list_famille[0]
            for famille in self.model.gest_vecteur.vect_list_famille[1:-1]:
                text += "|"+famille
              
        text+=""")[^,)\s]+</start>
          <end></end>
        </context>
        """

        text +="""
      </include>
    </context>
  </definitions>
</language>"""


        # enregistrement du fichier
        pid = os.getpid()
        the_path = os.path.join(os.sep, 'tmp', 'fil' + str(pid) + '.lang')
        file = open(the_path, 'w+')

        file.write(text)
        file.close()

        logging.debug(f"==== {'creer_lang_file':15s} : FIN")
        return the_path


    def set_auto_completion(self):
        """
        Créé l'auto-completion dans le GtkSource.view
        """
        logging.debug(f"==== {'set_auto_completion':15s} : DEBUT")

        # This gets the GtkSourceView completion that's already tied to the GtkSourceView
        # We need it to attached our providers to it
        self.view_completion = self.view_Gtk.get_completion()

        # Propose les dernier éléments choisis
        #self.view_autocomplete = GtkSource.CompletionWords.new('main')
        #self.view_autocomplete.register(self.buffer)
        #self.view_completion.add_provider(self.view_autocomplete)

        # 2) Make a new buffer, add a str to it, make a provider, add it to the view_autocomplete
        self.keybuff = GtkSource.Buffer()
        self.keybuff.begin_not_undoable_action()
        #self.keybuff.set_text(self.keywords)
        self.keybuff.end_not_undoable_action()
        ##self.view_keyword_complete = GtkSource.CompletionWords.new('keyword')
        self.view_keyword_complete = GtkSource.CompletionWords.new('vecteur')
        self.view_keyword_complete.register(self.keybuff)
        self.view_completion.add_provider(self.view_keyword_complete)

        # 3) Set up our custom provider for syntax completion.
        custom_completion_provider = CustomCompletionProvider()
        custom_completion_provider.nb_vectors_in = 0 ## utiliser pour choisir le n° des '$Arg'
        custom_completion_provider.set_model(self.model)
        self.view_completion.add_provider(custom_completion_provider)
        self.view_completion.props.remember_info_visibility = True
        self.custom_completion_provider = custom_completion_provider

        self.buffer = self.view_Gtk.get_buffer()

        # definition des marks
        self.def_mark()

        logging.debug(f"==== {'set_auto_completion':15s} : FIN")
        return True


    # SB : widget et args, jamais fournis, jamais utilisés ?!!
    def verif_tout(self, widget=None,args=None):
        """
        Verifie toute les lignes du texte
        """
        nb = self.buffer.get_line_count()
        for num_line in range(nb):
            self.verif_line(num_line)


    def verif_line(self, num_line):
        """
        verifie si la ligne en parametre est valide et place une mark pour
        signaler l'erreur si besoin
        param:
        num_line = numéro de la ligne a vérifier (int)
        """
        #logging.debug(f":::: {'verif_line':25s} : DEBUT : num_line = {num_line}")
        start_line = self.buffer.get_iter_at_line(num_line)
        end_line = start_line.copy()
        end_line.forward_to_line_end();

        texte = self.buffer.get_text(start_line, end_line, False)
        #logging.debug("@@@@  verif_line AVANT VERIF_TEXT")
        erreur_texte = self.verif_text(texte)

        # si il y a deja une mark, on l'enleve
        self.buffer.remove_source_marks(start_line, end_line)

        # si il y a une erreur, le texte est != None
        if not erreur_texte is None:
            #logging.debug(f"!!!!!!!! {'verif_line':25s} : erreur_texte = {erreur_texte}")

            # ajout d'une mark
            self.place_mark(self.ERR_MARK_1, num_line, erreur_texte + more_error_msg)

            return True

        return False


    def place_mark(self, mark_type, line, err_str):
        """
        Place une mark à la ligne line et lui adjoint le texte de l'erreur.

        *** ATTENTION ***
        L'info-bulle d'erreur est mal gérée : la méthode 'mark_tooltip_func'
        est apellée à haute cadence tant que la souris est positionnée sur
        la marque...
        L'adjonction de l'attribut 'the_place_mark' par la méthode 'place_mark'
        permet juste de ne pas rappeller (en plus) la méthode 'verif_text' à
        chaque appel de mark_tooltip_func.

        :param str() mark_type : string identifiant la mark
        :param int() line      : numéro de la ligne à marquer.
        """
        mark_iter = self.buffer.get_iter_at_line (line)
        mark = self.buffer.create_source_mark(None, mark_type, mark_iter)
        ## SB --- DEBUT
        setattr(mark, 'the_place_mark', err_str)
        ## SB --- FIN



    def verif_text(self, texte):
        """
        Vérifie la syntaxe du texte.

        :return: une string d'erreur ou None
        :rtype : str() ou None
        """
        #logging.debug(f"\n:::: {'verif_text':25s} : DEBUT : texte = {texte}, len = {len(texte)}")

        # si le text commence par \n ou #(commentaire) pas d'erreur
        if len(texte) == 0 or texte[0:1] == "\n" or texte[0:1] == "#":
            return None

        # verification des parenthèses
        nb_open  = texte.count('(')
        nb_close = texte.count(')')
        if nb_open != nb_close:
            return "Erreur de parenthèses"

        # vérifier s'il y a des paramètres vides (AST génèrerait une erreur de
        # syntaxe)
        pattern      = re.compile('\s')
        compact_text = pattern.sub('', texte)
        if ',,' in compact_text:
            # rechercher le numéro d'argument
            fields = compact_text.split(',')
            for i, field in enumerate(fields):
                if not field:
                    return f"Erreur : l'argument {i+1} est vide."

        # si ça ressemble à une instruction complète, faire analyser le texte
        # par AST
        if nb_open > 0 and nb_open == nb_close:
            #logging.debug(f":::: analyse par ast de : >{texte}<")

            try:
                oper_name, args_brut, args_opt, args_HDR = parse_instruction(texte, "edifil")
            except Exception as e:
                return f"Erreur : syntaxe inattendue : '{e}'."

            #logging.debug(f"  - oper_name = {oper_name}")
            #logging.debug(f"  - args_brut = {args_brut}")
            #logging.debug(f"  - args_opt  = {args_opt}")
            #logging.debug(f"  - args_HDR  = {args_HDR}")

            operation = self.model.gest_oper.get(oper_name)

            # si c'est un opérateur,
            if operation:
                #logging.debug(f"  - l'opérateur existe : oper_name = {oper_name} <-> operation.nom = {operation.nom}")

                # arguments obligatoires
                # ----------------------
                # vérification du nombre d'arguments obligatoires
                nb_oper_args = len(operation.args)
                #logging.debug(f"  - nb_oper_args = {nb_oper_args}, reçu = {len(args_brut)}")

                if nb_oper_args != len(args_brut):
                    return f"Erreur : {nb_oper_args} arguments attendus, {len(args_brut)} fournis."

                for i, arg in enumerate(args_brut):
                    arg_type = operation.args[i][1]
                    types_valide = arg_type.replace(' ', '').lower().split(',')
                    resultat = self.verif_arg(arg, types_valide, i)
                    if not resultat is None:
                        return resultat

                # arguments optionnels
                # --------------------
                # vérification du nombre d'arguments optionnels
                nb_oper_args_opt = len(operation.args_opt)
                if args_opt:
                    if len(args_opt) > nb_oper_args_opt:
                        return f"Erreur : {nb_oper_args_opt} arguments optionnels possibles, {len(args_opt)} fournis."

                    for arg_name, arg_val in args_opt.items():
                        #logging.debug(f"::::   args_opt = {args_opt}, len(args_opt) = {len(args_opt)}, nb_oper_args_opt = {nb_oper_args_opt:}")
                        if arg_name in operation.args_opt.keys():
                            oper_arg_type = operation.args_opt[arg_name]
                            if not self.verif_python_instance(arg_val, oper_arg_type):
                                return f"Erreur : argument optionnel '{arg_name}' : {oper_arg_type} attendus."

                        else:
                            return f"Erreur : argument optionnel '{arg_name}' inattendu."
            else:
                    return f"Erreur : '{oper_name}' n'est pas un opérateur."

        return None


    def verif_python_instance (self, val, expected_type):
        """
        Vérifie si type(val) est du type python 'expected_type'.

        :param any   val           : valeur à tester.
        :param str() expected_type : chaine du type attendu (ex: list(), bool())

        :return: True / False
        """
        #logging.debug(f":::: {'verif_python_instance':25s} : DEBUT : val = {val}, type(val) = {type(val)}, expected_type = {expected_type}")

        # il y a sans doute moyen de faire plus propre...
        if expected_type == 'bool()':
            if not isinstance(val, bool):
                return False
        elif expected_type == 'NUM':
            if not isinstance(val, int) and not isinstance(val, float):
                return False
        elif expected_type == 'int()':
            if not isinstance(val, int):
                return False
        elif expected_type == 'float()':
            if not isinstance(val, float):
                return False
        elif expected_type == 'str()':
            if not isinstance(val, str):
                return False
        elif expected_type == 'list()':
            if not isinstance(val, list):
                return False
        elif expected_type == 'dict()':
            if not isinstance(val, dict):
                return False
        elif expected_type == 'set()':
            if not isinstance(val, set):
                return False

        return True


    def verif_arg (self, arg, types_valide, num_arg):
        """
        Vérifie l'argument 'arg'...

        :param str() arg          : argument à tester.
        :param str() types_valide : type attendu (exemple : coeff, int).
        :param int(à num_arg      : position de l'argument parmis les
                                    paramètres de l'opérateur.

        :return: une chaîne d'erreur ou None
        """
        #logging.debug(f":::: {'verif_arg':25s} : DEBUT : arg = {arg}, types_valide = {types_valide}, num_arg = {num_arg}")

        # si vide
        if arg == "":
            return "Erreur argument {num_arg+1} vide : {types_valide} attendu"

        # si c'est un string
        if arg[0] == '"' and arg[-1] == '"':
            arg_parts = [arg]
        else:
            arg_parts = re.compile("[+\-*/]").split(arg)

        for arg_part in arg_parts:
            arg_part = arg_part.replace(' ','').replace('(','').replace(')','')
            resultat = self.test_arg(arg_part, types_valide, num_arg)
            if resultat is not None:
                return resultat

        return None


    def test_arg (self, arg, types_valide, num_arg):
        """
        verifie si "arg" est du type voulu.

        :param str() arg i        : argument à tester.
        :param str() types_valide : type attendu (exemple : coeff, int).
        :param int(à num_arg      : position de l'argument parmis les
                                    paramètres de l'opérateur.
        """
        #logging.debug(f":::: {'test_arg':25s} : DEBUT : arg = {arg}, types_valide = {types_valide}, num_arg = {num_arg}")
        # cas de arg vide traité avant appel de test_arg
        if arg == "":
            return None

        # si on veux un tab, on le remplace par "tab" pour plus de simplicité
        if len(types_valide) > 1:
            if "[" in types_valide[1] and "]" in types_valide[1]:
                types_valide[1] = "tab"
            if types_valide[1]== "double":
                types_valide[1] = "float"
        else:
            # pour les opérateur Python, le type n'est pas fournit dans la doc
            types_valide.append("any")

        # Type de l'argument
        ## SB : pas sûre qu'un `try` soit necessaire...
        try :
            # $Arg
            if "." in arg and self.model.gest_arg_spe.arguments.exist(arg.split('.')[1]):
                type = "arg"
            # $Chrono
            elif "." in arg and self.model.gest_arg_spe.argChrono.exist(arg.split('.')[1]):
                type = "chrono"
            # $Acq ### TODO : faire pour les autres champs speciaux ?
            elif arg.startswith('$Acq'):
                if arg == '$Acq.$date.DOY':
                    type = "acq"
                else:
                    type = "non_definit"
            # Constante
            elif self.model.gest_arg_spe.constantes.exist(arg):
                type = "const"
            # vecteur
            elif self.model.gest_vecteur.is_vect(arg) or re.match("^[A-Z][^a-z]{1,}$", arg):
                type = "vecteur"
            # tableau
            elif arg[0] == "[" and arg[-1] == "]":
                type = "tab"
            # String
            elif arg[0] == "\"" and arg[-1] == "\"":
                type = "string"
            # float
            elif re.match("-?\d+?\.\d*", arg) is not None:
                type = "float"
            # int
            elif arg.replace("-","").isdigit():
                type = "int"
            else:
                type = "non_definit"
        except:
            type = "non_definit"

        # vérification validité
        if type == "non_definit":
            return f"Erreur : argument {num_arg+1} non_definit ('{arg}') : {types_valide} attendu."

        err_str = f"Erreur : argument {num_arg+1} ('{arg}') : {types_valide} attendu."

        # VECTEUR
        if types_valide[0] == "vecteur" and type != "vecteur":
            # erreur si on veux un vecteur mais que ce n'en est pas un.
            return err_str

        # COEFF
        if types_valide[0] == "coeff":
            if types_valide[1] == "tab" and \
                    type != "tab" and type != "const" and type != "chrono":
                # erreur si on veux du tab, on doit avoir du : tab, const ou chrono
                return err_str

            elif types_valide[1] == "int" and type != "int" and \
                    type != "chrono" and type != "arg" and type != "acq":
                # erreur si on veux du int, on doit avoir du : int, chrono, arg, acq
                return err_str

            elif types_valide[1] == "float" and type != "float" and \
                    type != "arg" and type != "chrono" and type != "const" and type != "int":
                # erreur si on veux du float, on doit avoir du : float, arg, chrono, const ou int
                return err_str

            elif types_valide[1] == "string" and type != "string" and \
                    type != "chrono" and type != "arg":
                # erreur si on veux du string, on doit avoir du : string, chrono ou arg
                return err_str

        return None


    def def_mark (self):
        """
        Definit les marks pour l'affichage des erreurs.

        *** ATTENTION ***
        L'info-bulle d'erreur est mal gérée : la méthode 'mark_tooltip_func'
        est apellée à haute cadence tant que la souris est positionnée sur
        la marque...
        L'adjonction de l'attribut 'the_place_mark' par la méthode 'place_mark'
        permet juste de ne pas rappeller (en plus) la méthode 'verif_text' à
        chaque appel de mark_tooltip_func.
        """
        mark_attributes1 = GtkSource.MarkAttributes()
        mark_attributes1.set_stock_id(Gtk.STOCK_NO)
        mark_attributes1.connect('query_tooltip_text', self.mark_tooltip_func)
        self.view_Gtk.set_mark_attributes(self.ERR_MARK_1, mark_attributes1, 0)


    def mark_tooltip_func(self, attrs, mark):
        """
        Retourne le texte pour l'info-bulle d'une mark.

        *** ATTENTION ***
        L'info-bulle d'erreur est mal gérée : la méthode 'mark_tooltip_func'
        est apellée à haute cadence tant que la souris est positionnée sur
        la marque...
        L'adjonction de l'attribut 'the_place_mark' par la méthode 'place_mark'
        permet juste de ne pas rappeller (en plus) la méthode 'verif_text' à
        chaque appel de mark_tooltip_func.
        """
        #logging.debug(f":::: {'mark_tooltip_func':25s} : DEBUT")
        err_str = getattr(mark, 'the_place_mark')

        return err_str


    def ajouter_text (self, text):
        """
        ajoute un texte a la position du curseur
        """
        #logging.debug(f":::: {'ajouter_text':25s} : DEBUT : text = >{text}<")
        self.buffer.insert_at_cursor(text.strip())


    def demande_user_opts (self, option_defaut):
        """
        Ouvre une demande de sélection des options de lancement de
        l'interpréteur de commandes (VALIDER, ANNULER).

        :param int() option_defaut : numéro du bouton sélectionné à
                                     l'ouverture de la fenêtre.

        :return: si VALIDER : la chaine de toutes les options positionnées
                 si ANNULER : None
        """
        self.rad_bouton_option = ""
        dialog = Dialog_user_opts(self.builder.get_object('gtkWindow'))
        dialog.set_dialog(self)
        dialog.set_position(option_defaut)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            #logging.debug(f":::: demande_user_opts : return : >{self.rad_bouton_option}<")
            return self.rad_bouton_option
        else:
            return None

    def demande_validation (self, message = "Etes vous sûr ?"):
        """
        Ouvre une demande de confirmation (VALIDER, ANNULER)
        param : message -- Question à afficher : "Etes vous sûr ?" par default
        return : true si VALIDER, False si ANNULER
        """
        # Demande de confirmation
        dialog = DialogValidation(self.builder.get_object('gtkWindow'), message)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return True
        else:
            return False


class DialogValidation(Gtk.Dialog):
    """
    Definit une fenetre pour demander validation à l'utilisateur.
    """

    def __init__(self, parent,message='Etes vous sûr ?'):
        Gtk.Dialog.__init__(self, "Confirmation", parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 70)

        label = Gtk.Label(message)

        box = self.get_content_area()
        box.add(label)
        self.show_all()


class Dialog_user_opts(Gtk.Dialog):
    """
    Définit une fenêtre pour demander à l'utilisateur les options de lancement
    pour l'interpréteur de commandes.
    """

    ihm_builder = ""

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, 'Options de lancement', parent, 0,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(150, 140)

        vbox = Gtk.VBox(spacing=6)

        label = Gtk.Label.new_with_mnemonic('Selectionez les options')
        vbox.pack_start(label, False, False, 0)


        label_exclusives     = Gtk.Label("Options exclusives :", xalign=0)
        label_non_exclusives = Gtk.Label("Options non-exclusives :", xalign=0)

        # les options exclusives
        self.button1 = Gtk.RadioButton.new_with_label_from_widget(None, "sans option")
        self.button1.opt_val = ''
        self.button1.connect("toggled", self.on_button_toggled)

        self.button2 = Gtk.RadioButton.new_from_widget(self.button1)
        self.button2.opt_val = '-F'
        self.button2.set_label("option : -F")
        self.button2.connect("toggled", self.on_button_toggled)

        self.button3 = Gtk.RadioButton.new_from_widget(self.button1)
        self.button3.opt_val = '-f'
        self.button3.set_label("option : -f")
        self.button3.connect("toggled", self.on_button_toggled)

        # les options non-exclusives
        self.check_button1 = Gtk.CheckButton("option : -S")
        self.check_button1.opt_val = '-S'
        self.check_button1.connect("toggled", self.on_button_toggled)

        self.check_button2 = Gtk.CheckButton("option : -C")
        self.check_button2.opt_val = '-C'
        self.check_button2.connect("toggled", self.on_button_toggled)

        # liste de tous les boutons (utilisée par self.on_button_toggled)
        self.opt_buttons = [self.button1, self.button2, self.button3,
                            self.check_button1, self.check_button2]

        vbox.pack_start(label_exclusives    , False, False, 0)
        vbox.pack_start(self.button1        , False, False, 0)
        vbox.pack_start(self.button2        , False, False, 0)
        vbox.pack_start(self.button3        , False, False, 0)
        vbox.pack_start(label_non_exclusives, False, False, 0)
        vbox.pack_start(self.check_button1  , False, False, 0)
        vbox.pack_start(self.check_button2  , False, False, 0)

        box = self.get_content_area()
        box.add(vbox)
        self.show_all()


    def set_dialog(self, ihm_builder):
        self.ihm_builder = ihm_builder


    def set_position(self, option_defaut):
        """
        change le bouton selectionné
        """
        if option_defaut == 1:
            self.button1.set_active(True)
        elif option_defaut == 2:
            self.button2.set_active(True)
        elif option_defaut == 3:
            self.button3.set_active(True)


    def on_button_toggled(self, button):
        """ Retourne la chaine de toutes les options sélectionnées.
            (Il y a sans doute une façon plus élégante de construire la
            chaine de retour...)
        """
        #logging.debug(":::: on_button_toggled")
        opt = ''
        for i, button in enumerate(self.opt_buttons):
            if button.get_active():
                opt = f"{opt} {button.opt_val}"
        self.ihm_builder.rad_bouton_option = opt


class Dialog_quiter_save(Gtk.Dialog):
    """
    Dialogue demandant si l'utilisateur veux quitter, sauvegarder ou annuler
    """

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "Enregistrer le document ?", parent, 0,
            (Gtk.STOCK_QUIT, Gtk.ResponseType.CLOSE,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_SAVE, Gtk.ResponseType.YES))

        self.set_default_size(150, 70)

        label = Gtk.Label("Voulez-vous sauvegarder vos modifications ?")

        box = self.get_content_area()
        box.add(label)
        self.show_all()


class CustomCompletionProvider(GObject.GObject, GtkSource.CompletionProvider):
    """
    Gère l'auto completion de la page
    """

    def set_model(self, model):
        self.model = model

    # apparently interface methods MUST be prefixed with do_
    def do_get_name(self):
        return ''

    def do_match(self, context):
        # this should evaluate the context to determine if this completion
        # provider is applicable, for debugging always return True
        return True

    def do_populate(self, context):
        """ Met à jour les propositions de completion du popup.
        
            La complétion des $Arg dans les lignes qui ne sont pas des commande
            n'est pas présentée...
        """
        logging.debug(f":::: {'Model/IHMbuilder.py::do_populate':25s} : DEBUT ")

        # liste des éléments proposés dans le popup de la completion
        proposals = []

        # récupérer la ligne courante du texte
        #   il semble qu'il n'existe pas de méthode simple qui permette de ne
        #   retrouver que le texte de la ligne courrante (le texte récupéré
        #   peut contenir un '\n'
        _, end_iter = context.get_iter()
        if not end_iter:
            context.add_proposals(self, proposals, True)
            return

        buf = end_iter.get_buffer()
        start_iter = buf.get_start_iter()
        left_text = buf.get_text(start_iter, end_iter, True)
        ### print(f"=== left_text = {left_text}")

        # la méthode utilisée peut remonter plusieurs lignes
        # => splitter sur \n et ne garder que la dernière ligne...
        if '\n' in left_text:
            left_text = left_text.split('\n')[-1]
        logging.debug(f":::: {'Model/IHMbuilder.py::do_populate':25s} : left_text = >{left_text}< ")

        # si on est dans une chaine (entre "  "), on ne fait pas une completion
        if left_text.count("\"")%2 != 0 : # nombre impaire de "
            context.add_proposals(self, proposals, True)
            return

        # est-on *dans* la ligne commande d'un opérateur existant ?
        if left_text and '(' in left_text:
            an_oper_name = left_text.split('(')[0]
            an_oper_name = an_oper_name.strip()
            operation = self.model.gest_oper.get(an_oper_name)
            if operation:
                # que demande l'utilisateur ?
                #  on recupère ce qu'il y a après une '(' ou une ',' qui n'est pas :
                #  ,)"'= ou space et qui se trouve en fin de ligne...
                pattern = r'[(,]\s*([^,)\"\'\s=]+)$'
                texte_user = re.findall(pattern, left_text)
                logging.debug(f":::: left_text = {left_text}, texte user = {texte_user}")
                ### print(f":::: left_text  = {left_text}")
                ### print(f":::: texte user = {texte_user}")

                # si le texte_user ne contient rien, on ne fait pas de proposition
                if len(texte_user) == 0:
                    context.add_proposals(self, proposals, True)
                    return

                # si le texte_user commence par un digit, on va supposer que
                # l'utilisateur saisie une valeur => pas de porposition
                if texte_user[0][0].isdigit():
                    context.add_proposals(self, proposals, True)
                    return

                # si le texte_user ne contient que '$Arg', proposer un n°
                if texte_user[0] == '$Arg':
                    print(f":::: proposer un n°")
                    for i in range(1, 10):
                        proposals.append(
                            GtkSource.CompletionItem(label=f'$Arg{i}', text=f'Arg{i}')
                        )
                    context.add_proposals(self, proposals, True)
                    return

                # si le texte_user ne contient que '$Arg{d}.', proposer un nom
                # de champ
                if re.match(r'\$Arg\d{1,2}\.$', texte_user[0]):
                    print(f":::: proposer un champ")
                    for field in sorted(self.model.gest_arg_spe.arguments.arg_list, key=str.lower):
                        proposals.append(
                            GtkSource.CompletionItem(label=field, text=field)
                        )
                    context.add_proposals(self, proposals, True)

                    return

                # on est dans une commande pour un opérateur qui existe

                # => présenter les vecteurs, les $Args, les constantes et les
                #    arguments optionnels
                # TODO : si tous les arguments obligeatoires ont été donnés
                #      : n'ajouter que les paramètres optionnels dans les
                #      : propositions.

                # ajout des vecteurs
                for element in self.model.gest_vecteur.find(texte_user[0]):
                    #logging.debug(f":::: {'do_populate':25s} : VECTEUR element = {element} ")
                    proposals.append(
                        GtkSource.CompletionItem(label=element, text=element)
                    )

                # ajout des $Args (j'ai l'impression que jamais rien ne remonte ici)
                for element in self.model.gest_arg_spe.find(texte_user[0]):
                    logging.debug(f":::: {'do_populate':25s} : ARGSPE element = {element} ")
                    proposals.append(
                        GtkSource.CompletionItem(label=element, text=element)
                    )

                # ajout des arguments optionnels s'il en existe qui commencent
                # par le texte_user
                for key, val in operation.args_opt.items():
                    if key.startswith(texte_user[0]):
                        element = f"{key}={val}"
                        logging.debug(f":::: {'do_populate':25s} : ARGOPT element = {element} ")
                        proposals.append(
                            GtkSource.CompletionItem(label=element, text=element)
                        )
                context.add_proposals(self, proposals, True)
                return

        else: # pas dans une ligne d'opérateur
            logging.debug(f":::: {'Model/IHMbuilder.py::do_populate':25s} : ANCIEN CODE ============ ")
            # on n'est ni *dans* une chaine, ni dans une ligne de commande
            # Texte a completer
            texte = re.findall(r'.*\W(.+?)?$', left_text,re.DOTALL)
            #logging.debug(f":::: {'Model/IHMbuilder.py::do_populate':25s} : texte = {texte} ")

            # Si c'est le premier mot de la page
            if texte == []:
                texte = [left_text]

            # si il y a un mot, on propose une completion
            if texte != ['']:
                # Ajout des opérateurs
                for oper in self.model.gest_oper.find(texte[0]):
                    # texte comportant le nom et les arguments de l'opérateur
                    oper_texte = oper.nom + "("+oper.args[0][0]
                    for args in oper.args[1:]:
                        oper_texte += ", "+args[0]
                    oper_texte += ")"
                    #logging.debug(f":::: {'Model/IHMbuilder.py::do_populate':25s} : oper_texte = {oper_texte} ")

                    proposals.append(
                        GtkSource.CompletionItem(label=oper.nom, text=oper_texte,
                                                  icon=None, info=oper.description)
                    )

                # ajout des $Args et des vecteurs
                for element in self.model.gest_arg_spe.find(texte[0]) + self.model.gest_vecteur.find(texte[0]):
                    #logging.debug(f":::: {'Model/IHMbuilder.py::do_populate':25s} : element = {element} ")
                    proposals.append(
                        GtkSource.CompletionItem(label=element, text=element)
                    )

        context.add_proposals(self, proposals, True)
        return

