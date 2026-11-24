#!/usr/bin/env python3

"""
AITO
    Selecteur de gauche

    Il permet de naviguer dans les plateformes ou les campagnes selon le model
    positionné par les boutons 'plateforme' et 'campagne'.
    La sélection s'arrête au choix d'un acqid


    NOTE : la gestion des tête de colonne (header) est pourrie : le model ne
           devrait pas le positionner. Il devrait être positionner par
           Left_selector et Right_selector (Left_selector ne veut affichier
           que la colonne 0 et ne devrait pas faire des pieds et des mains
           pour masquer les autres)
"""

import sys
import os
import logging

from PyQt5.QtWidgets import (QWidget,
                             QTreeView,
                             QVBoxLayout,
                             QAbstractItemView,
                             QMessageBox,
                            )
from PyQt5.Qt        import (QHeaderView,
                            )
from PyQt5.QtCore    import (Qt,
                            )


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

import AITO_lib

logger = logging.getLogger('aito')


class Left_selector(QWidget):
    """ Gestion de la sélection dans la partie gauche.
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Left_selector::__init__")

        self.parent    = kwargs.get('parent'   , None)
        self.models    = kwargs.get('models'   , None)
        self.view_mode = kwargs.get('view_mode', 'plateforme')

        if not self.models:
            raise Exception("Left_selector::__init : no models given")

        # préférences utilisateur
        self.settings = self.parent.settings

        # mise en place de l'IHM
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Left_selector::setup_ihm")

        layout = QVBoxLayout()

        # les widgets graphiques
        # - le treeview
        self.treeview = QTreeView()
        self.treeview.setHeaderHidden(True)
        self.treeview.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # amélioration des performance d'affichage...
        self.treeview.setUniformRowHeights(True)

        # -- le model associé au treeview
        self.treeview.setModel(self.models[self.view_mode])


        # rangement de tout ça dans le layout principal
        layout.addWidget(self.treeview)

        self.setLayout(layout)

        # connexions
        self.treeview.clicked.connect(self.treeview_clicked)
        self.treeview.activated.connect(self.treeview_clicked)
        self.treeview.expanded.connect(self.treeview_expanded)

        # une fenêtre pour afficher des messages
        self.message = QMessageBox(self)

        return


    def use_view_mode(self, view_mode):
        """ Change le view_mode et le model utilisé par le treeview.
            ('plateforme', 'campagne', 'date')
        """
        logger.log(logging.RUN, f"Left_selector::use_view_mode : " +\
                                f"view_mode = {view_mode}")

        ### TODO ??? se passer de tous les self.view_mode ???
        self.view_mode = view_mode
        model          = self.models[self.view_mode]
        self.treeview.setModel(model)

        return


    def treeview_expanded(self, index):
        """ Gestion du dépliage d'une ligne du treeview.
            Prévenir le parent qui fera ce qu'il veut de l'information.
        """
        logger.log(logging.RUN, f"Left_selector::treeview_expanded : " +\
                                f"index.model().name = {index.model().name}, " +\
                                f"index.data() = {index.data()}")

        # role
        role = index.model().data(index, Qt.UserRole)

        # prévenir le parent
        self.parent.left_expanded(index, role)

        return


    def treeview_clicked(self, index, advise_parent=True):
        """ Gestion de la sélection d'une ligne du treeview.

            :param bool() advise_parent: prévenir le parent qu'un index a été
                                         sélectionné.
                                         Toujours True sauf pour les appels
                                         directs fait par le parent (cas de la
                                         navigation par les boutons prev et
                                         next)
            ### TODO ?
            ### les appels à populate devrait être fait par le main...
            ### et non pas dupliqué dans Left et Rigth
        """
        logger.log(logging.RUN, f"Left_selector::treeview_clicked : " +\
                                f"advise_parent = {advise_parent}")

        if index:
            logger.debug(f"index.model().name = {index.model().name}, " +\
                         f"index.data() = {index.data()}")

        # récupérer le model de l'index reçu
        used_model = index.model()

        # récupérer le StandardItem lié à l'index reçu
        item = used_model.itemFromIndex(index)

        # item sans données
        if not item.isEnabled():
            return

        # récupérer le role dans l'arborescence de la ligne sélectionnée
        role = used_model.data(index, Qt.UserRole)

        ### TODO : user préference...
        # taille des colonnes
        self.treeview.setColumnWidth(0, 400)
        self.treeview.setColumnWidth(1, 200)

        # "élargir" la première colonne à toute la longueur
        self.treeview.setFirstColumnSpanned(index.row(), index.parent(), True)

        if self.view_mode == 'plateforme':
            if role == 'plateforme':
                used_model.populate_level_2(index)

                # développer l'index cliqué
                self.treeview.setExpanded(index, False)
                self.treeview.expand(index)

            elif role == 'year':
                used_model.populate_level_3(index)

                # masquer les colonnes d'information (col 0 = num, col 1 = info)
                self.treeview.setColumnHidden(1, True)

                # développer l'index cliqué
                self.treeview.setExpanded(index, False)
                self.treeview.expand(index)

            elif role == 'num':
                # prévenir le parent qu'une acquisition a été cliquée
                acqid = used_model.data(index, Qt.UserRole + 1)
                if advise_parent:
                    self.parent.left_acqid_selected(acqid, index, role)

        elif self.view_mode == 'campagne':
            if role == 'campagne':
                used_model.populate_level_2(index)

                # développer l'index cliqué
                self.treeview.setExpanded(index, False)
                self.treeview.expand(index)

            elif role == 'plateforme':
                used_model.populate_level_3(index)

                # développer l'index cliqué
                self.treeview.setExpanded(index, False)
                self.treeview.expand(index)

            elif role =='year':
                used_model.populate_level_4(index)

                # masquer les colonnes d'information (col 0 = num, col 1 = info)
                self.treeview.setColumnHidden(1, True)

                # développer l'index cliqué
                self.treeview.setExpanded(index, False)
                self.treeview.expand(index)

            elif role == 'num':
                # prévenir le parent qu'une acquisition a été cliquée
                acqid = used_model.data(index, Qt.UserRole + 1)
                if advise_parent:
                    self.parent.left_acqid_selected(acqid, index, role)

        elif self.view_mode == 'by_date':
            # développer l'index cliqué
            if role == 'acqid':
                # prévenir le parent qu'une acquisition a été cliquée
                acqid = index.data()
                if advise_parent:
                    self.parent.left_acqid_selected(acqid, index, role)

            else:
                self.treeview.setExpanded(index, False)
                self.treeview.expand(index)

        else:
            raise Exception(f"Left_selector::treeview_clicked : " +\
                            f"ne sait pas gérer le mode '{self.view_mode}.")

        # prévenir le parent qu'un index a été sélectionné
        if advise_parent:
            self.parent.left_selected(index)

        return


    def expand(self, index):
        """ Déplier 'index'.
        """
        logger.log(logging.RUN, f"Left_selector::expand : " +\
                                f"index.model().name = {index.model().name}, " +\
                                f"index.data() = {index.data()}")

        self.treeview.expand(index)

        ### TODO : user préference...
        # taille des colonnes
        self.treeview.setColumnWidth(0, 400)
        self.treeview.setColumnWidth(1, 200)

        # masquer les colonnes d'information (col 0 = num, col 1 = info)
        self.treeview.setColumnHidden(1, True)

        return


    def date_changed(self, year, month, day):
        """ Afficher l'arborescence pour la date reçue.
        """
        logger.log(logging.RUN, f"Left_selector::date_changed : " +\
                                f"year = {year}, " +\
                                f"month = {month}, " +\
                                f"day = {day}")

        # récupérer le model
        used_model = self.treeview.model()

        # peupler le model pour l'année
        used_model.populate_levels(year, month, day)

        # expander au plus près de la date demandée
        index = None
        y_m_d_indexes = used_model.get_item_date(year, month, day)
        for index in y_m_d_indexes:
            self.treeview.expand(index)

        # message pour l'utilisateur si la date n'a pas été trouvée
        n = len(y_m_d_indexes)
        if n != 3:
            if n == 0:
                msg = f"Pas d'acquisition pour l'année {year}.\n" +\
                       "Choisir une autre année."
            elif n == 1:
                msg = f"Pas d'acquisition pour le mois {month:02d}/{year}.\n" +\
                       "Choisir un autre mois."
            elif n == 2:
                msg = f"Pas d'acquisition pour le jour {day:02d}/{month:02d}/{year}.\n" +\
                       "Choisir un autre jour."

            self.message.setText(msg)
            self.message.exec()

        # prévenir le parent qu'un index a été sélectionné
        if index:
            self.treeview.setCurrentIndex(index)
            # role
            role = index.model().data(index, Qt.UserRole)
            self.parent.left_expanded(index, role)

        return


    def highlight_index(self, index, expand=True):
        """ Position index dans la partie visible par l'utilisateur...

            Cette méthode est appelée par Selection après une sélection dans
            right_selector
        """
        logger.log(logging.RUN, f"Left_selector::highlight_index : " +\
                                f"index.data() = {index.data()}, " +\
                                f"expand = {expand}")

        # DBG print(f"=== Left_selector::highlight_index : index = {index.data()}")

        # repositionner left_selector sur l'index et faire "comme si"
        # l'utilisateur venait de sélectionner cet index.
        if expand:
            self.expand(index)
        self.treeview.scrollTo(index, hint=QAbstractItemView.PositionAtCenter)
        self.treeview.setCurrentIndex(index)
        self.treeview_clicked(index, advise_parent=False)

        return


    def highlight_current_index(self):
        """ Scroll le treeview sur son index courant.

            Cette méthode est appelée par main après la sélection d'un
            vecteur dans right_selector.
        """
        logger.log(logging.RUN, f"Left_selector::highlight_current_index")

        cur_index = self.treeview.currentIndex()
        self.treeview.scrollTo(cur_index, hint=QAbstractItemView.PositionAtCenter)

        return


    def write_settings(self):
        """ Enregistrement des préférences utilisateur.
        """
        logger.log(logging.RUN, f"Left_selector::write_settings")

        cur_index = self.treeview.currentIndex()
        filiation = AITO_lib.get_index_filiation(cur_index)
        if not filiation:
            filiation = ''

        self.settings.setValue('filiation', filiation)


        return


    def restore_context_plateforme(self, model, filiation):
        """ Restauration du contexte de la dernière session de l'utilisateur.
            Page plateforme

            TODO : ? factoriser la récupération des sous-items ?
        """
        logger.log(logging.RUN, f"Left_selector::restore_context_plateforme : " +\
                                f"model.name = {model.name}, " +\
                                f"filiation = {filiation}")

        # restauration de la plateforme
        plateforme = filiation['plateforme']
        items = model.findItems(plateforme)
        if len(items) == 0:
            self.message.setText(f"La plateforme '{plateforme}' n'a pas été retrouvée")
            self.message.exec()

            return

        item = items[0]
        index = model.indexFromItem(item)
        self.treeview_clicked(index)
        self.expand(index)
        self.highlight_index(index, expand=False)

        # restauration de l'année
        if not 'year' in filiation.keys():
            return

        item_year = None
        year = filiation['year']
        if item.hasChildren():
            for row in range(item.rowCount()):
                if item.child(row).text() == year:
                    item_year = item.child(row)
                    break

        if not item_year:
            self.message.setText(f"L'année '{year}' n'a pas été retrouvée")
            self.message.exec()

            return

        index = model.indexFromItem(item_year)
        self.treeview_clicked(index)
        self.expand(index)
        self.highlight_index(index, expand=False)
        item = item_year

        # restauration du numéro d'acquisition (acqid)
        if not 'num' in filiation.keys():
            return

        item_num = None
        num = filiation['num']
        if item.hasChildren():
            for row in range(item.rowCount()):
                if item.child(row).text() == num:
                    item_num = item.child(row)
                    break

        if not item_num:
            self.message.setText(f"Le numéro d'acquisition '{num}' n'a pas été retrouvé")
            self.message.exec()

            return

        index = model.indexFromItem(item_num)
        self.treeview_clicked(index)
        self.highlight_index(index, expand=False)

        return


    def restore_context_campagne(self, model, filiation):
        """ Restauration du contexte de la dernière session de l'utilisateur.
            Page campagne

            TODO : ? factoriser la récupération des sous-items ?
        """
        logger.log(logging.RUN, f"Left_selector::restore_context_campagne : " +\
                                f"model.name = {model.name}, " +\
                                f"filiation = {filiation}")

        # restauration de la campagne
        campagne = filiation['campagne']
        items = model.findItems(campagne)
        if len(items) == 0:
            self.message.setText(f"La campagne '{campagne}' n'a pas été retrouvée")
            self.message.exec()

            return

        item = items[0]
        index = model.indexFromItem(item)
        self.treeview_clicked(index)
        self.expand(index)
        self.highlight_index(index, expand=False)

        # restauration de la plateforme
        if not 'plateforme' in filiation.keys():
            return

        item_pltf = None
        plateforme = filiation['plateforme']
        if item.hasChildren():
            for row in range(item.rowCount()):
                if item.child(row).text() == plateforme:
                    item_pltf = item.child(row)
                    break

        if not item_pltf:
            self.message.setText(f"La plateforme '{plateforme}' n'a pas été retrouvée")
            self.message.exec()

            return

        index = model.indexFromItem(item_pltf)
        self.treeview_clicked(index)
        self.expand(index)
        item = item_pltf
        self.highlight_index(index, expand=False)

        # restauration de l'année
        if not 'year' in filiation.keys():
            return

        item_year = None
        year = filiation['year']
        if item.hasChildren():
            for row in range(item.rowCount()):
                if item.child(row).text() == year:
                    item_year = item.child(row)
                    break

        if not item_year:
            self.message.setText(f"L'année '{year}' n'a pas été retrouvée")
            self.message.exec()

            return

        index = model.indexFromItem(item_year)
        self.treeview_clicked(index)
        self.expand(index)
        item = item_year
        self.highlight_index(index, expand=False)

        # restauration du numéro d'acquisition (acqid)
        if not 'num' in filiation.keys():
            return

        item_num = None
        num = filiation['num']
        if item.hasChildren():
            for row in range(item.rowCount()):
                if item.child(row).text() == num:
                    item_num = item.child(row)
                    break

        if not item_num:
            self.message.setText(f"Le numéro d'acquisition '{num}' n'a pas été retrouvé")
            self.message.exec()

            return

        index = model.indexFromItem(item_num)
        self.treeview_clicked(index)
        self.highlight_index(index, expand=False)

        return


    def restore_context_by_date(self, model, filiation):
        """ Restauration du contexte de la dernière session de l'utilisateur.
            Page Date

            TODO : ? factoriser la récupération des sous-items ?
        """
        logger.log(logging.RUN, f"Left_selector::restore_context_by_date : " +\
                                f"model.name = {model.name}, " +\
                                f"filiation = {filiation}")

        # restauration la date
        year  = int(filiation['year'])
        month = int(filiation['month'])
        day   = int(filiation['day'])
        self.date_changed(year, month, day)

        # restauration de l'acqid
        if not 'acqid' in filiation.keys():
            return

        item_acqid = None
        acqid = filiation['acqid']
        index = self.treeview.currentIndex()
        item  = model.itemFromIndex(index)
        if item.hasChildren():
            for row in range(item.rowCount()):
                if item.child(row).text() == acqid:
                    item_acqid = item.child(row)
                    break

        if not item_acqid:
            self.message.setText(f"L'acqid '{acqid}' n'a pas été retrouvé")
            self.message.exec()

            return

        index = model.indexFromItem(item_acqid)
        self.treeview_clicked(index)
        self.highlight_index(index, expand=False)

        return


    def restore_context(self, filiation):
        """ Restauration du contexte de la dernière session de l'utilisateur.
        """
        logger.log(logging.RUN, f"Left_selector::restore_context : " +\
                                f"filiation = {filiation}")

        if 'model' in filiation.keys():
            self.use_view_mode(filiation['model'])
            model = self.models[ filiation['model'] ]
        else:
            return

        if model.name == 'plateforme' and 'plateforme' in filiation.keys():
            self.restore_context_plateforme(model, filiation)

        elif model.name == 'campagne' and 'campagne' in filiation.keys():
            self.restore_context_campagne(model, filiation)

        elif model.name == 'by_date' and 'year' in filiation.keys():
            self.restore_context_by_date(model, filiation)

        else:
            self.message.setText(f"Le contexte ne peut pas être restauré :-/...")
            self.message.exec()

            return

        return

