#!/usr/bin/env python3

"""
AITO
    Gestion de la sélection dans les arborescences plateforme et campagne.
"""

import sys
import os
import logging
import glob

from PyQt5.QtWidgets import (QWidget,
                             QLayout, QVBoxLayout, QHBoxLayout,
                             QSplitter,
                             QButtonGroup, QRadioButton, QPushButton,
                             QDateEdit, QLineEdit,
                             QMessageBox,
                             QAbstractItemView,
                             QSizePolicy,
                            )

from PyQt5.QtGui     import (QKeySequence,
                            )
from PyQt5.QtCore    import (Qt,
                             QDateTime,
                             QSettings,
                            )

PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

import AITO_icons
from AITO_icons       import icons
from Nav_tools        import Nav_tools
from Left_selector    import Left_selector
from Right_selector   import Right_selector
###from Splitter_handler import Splitter_handler

logger = logging.getLogger('aito')


class Selection(QWidget):
    """ Gestion de la sélection dans les arborescences plateforme et campagne
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Selection::__init__")

        self.parent      = kwargs.get('parent'       , None)
        self.select_mode = kwargs.get('select_mode'  ,'single')

        # récupérer les objets de l'application (models, gest_XXX...)
        self.models     = self.parent.models
        self.gest_acqid = self.parent.gest_acqid

        # le parent a peut-être une méthode `notify` qu'il faudra appeler
        # lorsque la vue change...
        # - la class Detail a une méthode `notify` qu'il faut appeler lorsque
        #   la view est sur autre chose que 'vector.
        # - les class Importation et Exportation n'ont pas de méthode 'notify')
        self.notify_parent = None
        if hasattr(self.parent, 'notify') and callable(self.parent.notify):
            self.notify_parent = self.parent.notify

        # préférences utilisateur
        self.settings = self.parent.settings

        # mise en place de l'IHM
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Selection::setup_ihm")

        # les widgets graphiques
        # - les boutons de sélection du type d'affichage
        #   regroupés dans un groupe
        self.button_group = QButtonGroup(self)

        self.button_plateforme = QRadioButton('plateforme', self)
        self.button_campagne   = QRadioButton('campagne'  , self)
        self.button_by_date    = QRadioButton('date'      , self)

        # ajouter chaque bouton au groupe
        self.button_group.addButton(self.button_plateforme)
        self.button_group.addButton(self.button_campagne)
        self.button_group.addButton(self.button_by_date)

        # enrichir chaque bouton du view_mode qu'il gère
        self.button_plateforme.view_mode = 'plateforme'
        self.button_campagne  .view_mode = 'campagne'
        self.button_by_date   .view_mode = 'by_date'

        # - sélecteur de date : user préférences ou par default
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setToolTip('Recherche par date')
        key = f'{self.settings.name}/date'
        try:
            date = QDateTime( self.settings.value(key) )
        except Exception as e:
            date = QDateTime.currentDateTime()
        self.date_edit.setDateTime(date)
        logger.debug(f"??? Selection::setup_ihm : comment limiter le calendar aux dates du [ 1ier acqid, last acqid] ?")

        # - sélecteur d'acqid : user préférences ou par default
        self.acqid_edit = QLineEdit()
        self.acqid_edit.setToolTip('accès direct par acqid')
        self.acqid_edit.setPlaceholderText('acqid')
        self.acqid_edit.setClearButtonEnabled(True)
        self.acqid_edit.setMaxLength(8)
        key = f'{self.settings.name}/acqid_edit'
        self.acqid_edit.setText( self.settings.value(key, '') )

        # view_mode : user préférences ou par default
        key = f'{self.settings.name}/mode'
        view_mode = self.settings.value(key, 'plateforme')
        for b in [self.button_plateforme, self.button_campagne, self.button_by_date]:
            if b.view_mode == view_mode:
                b.setChecked(True)
                break

        # - barre de navigation
        self.nav_tools = Nav_tools(parent=self)

        # - sélecteur de gauche
        self.left_selector = Left_selector(parent    = self,
                                           models    = self.models,
                                           view_mode = view_mode,
                                          )

        # - sélecteur de droite
        self.right_selector = Right_selector(parent      = self,
                                             models      = self.models,
                                             view_mode   = view_mode,
                                             select_mode = self.select_mode,
                                            )


        # rangements
        # - des boutons dans leur layout (en les tassant)
        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_plateforme)
        layout_buttons.addWidget(self.button_campagne  )
        layout_buttons.addWidget(self.button_by_date   )
        layout_buttons.addWidget(self.date_edit        )
        layout_buttons.addWidget(self.acqid_edit       )
        self.acqid_edit.setMinimumSize(100, 20)

        # - des selectors
        ###splitter = Splitter_handler(Qt.Horizontal)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_selector )
        self.splitter.addWidget(self.right_selector)
        self.splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # -- taille : user préférences ou par default
        try:
            key = f'{self.settings.name}/selection_splitter_sizes'
            self.splitter.restoreState( self.settings.value(key) )
        except Exception as e:
            self.splitter.setSizes([263, 263])

        # rangement de tout ça dans le layout principal
        layout = QVBoxLayout()
        layout.addLayout(layout_buttons)
        layout.addWidget(self.nav_tools, alignment=Qt.AlignTop)
        layout.addWidget(self.splitter)

        self.setLayout(layout)

        # une fenêtre pour afficher des messages
        self.message = QMessageBox(self)


        # connexions
        self.button_group.buttonClicked.connect(self.set_view_mode)
        self.date_edit.dateChanged.connect(self.date_changed)
        self.acqid_edit.returnPressed.connect(self.acqid_changed)

        return


    def set_view_mode(self):
        """ Gestion du mode courant d'affichage :
            ('plateforme', 'campagne', 'by_date')
        """
        logger.log(logging.RUN, "Selection::set_view_mode")

        button    = self.button_group.checkedButton()
        view_mode = button.view_mode
        logger.debug(f"view_mode = {view_mode}")

        # vider self.acqid_edit
        self.acqid_edit.setText('')

        # mode by_date mais aucune date n'a été peuplée
        if view_mode == 'by_date':
            if self.models[view_mode].rowCount() == 0:
                self.message.setText("Sélectionner une date grâce au calendier")
                self.message.exec()
                return

        # prévenir le parent
        if self.notify_parent:
            self.notify_parent(model=view_mode)


        self.left_selector.use_view_mode(view_mode)
        self.right_selector.use_view_mode(view_mode)

        return


    def date_changed(self, date):
        """ Gestion de la sélection d'une date.
        """
        logger.log(logging.RUN, "Selection::date_changed")

        year  = date.year()
        month = date.month()
        day   = date.day()

        # sélectionner le bouton by_date
        self.button_by_date.setChecked(True)
        # TODO : setChecked(True) ne déplenche pas set_view_mode
        view_mode = 'by_date'

        # passer les selecteurs en mode 'date'
        self.left_selector.use_view_mode(view_mode)
        self.right_selector.use_view_mode(view_mode)

        # peupler le selecteur de droite en mode date
        self.left_selector.date_changed(year, month, day)

        # TODO : voir si je peux me passer de tous les self.view_mode

        return


    def acqid_changed(self):
        """ Gestion de la sélection d'un acqid.
        """
        logger.log(logging.RUN, "Selection::acqid_changed")

        acqid = self.acqid_edit.text()
        logger.debug(f"acqid = {acqid}")

        infos = self.gest_acqid.get_path_infos(acqid)
        if not infos:
            self.message.setText(f"L'acqid '{acqid}' n'exite pas")
            self.message.exec()
            return

        if not infos['data_exists']:
            self.message.setText(f"Les données pour l'acqid '{acqid}' n'exitent pas")
            self.message.exec()
            return

        plateforme = infos['plateforme']
        year       = infos['year']
        num        = infos['num']

        self.button_plateforme.setChecked(True)
        self.set_view_mode()

        model = self.models['plateforme']

        # TODO : doit y avoir plus simple mais je sature grave....
        # traitement de la plateforme
        items = model.findItems(plateforme)
        item  = items[0]
        index = model.indexFromItem(item)
        self.left_selector.treeview_clicked(index)

        # traitement de l'année de la plateforme
        if item.hasChildren():
            for row in range(item.rowCount()):
                if item.child(row).text() == year:
                    item = item.child(row)
                    break

        index = model.indexFromItem(item)
        self.left_selector.treeview_clicked(index)

        # traitement du numéro de l'année de la plateforme
        if item.hasChildren():
            for row in range(item.rowCount()):
                if item.child(row).text() == num:
                    item = item.child(row)
                    break

        index = model.indexFromItem(item)
        self.left_selector.treeview_clicked(index)
        self.left_selector.treeview.scrollTo(index, hint=QAbstractItemView.PositionAtCenter)
        self.left_selector.treeview.setCurrentIndex(index)

        # prévenir le parent
        if self.notify_parent:
            self.notify_parent(model=model, index=index)
        return


    def vector_selected(self, acqid, vector_name):
        """ Repositionne le selecteur de gauche
            Transmet le nom du vecteur au parent.
        """
        logger.log(logging.RUN, f"Selection::vector_selected : " +\
                                f"acqid = {acqid}, vector_name = {vector_name}")

        # au cas où, repositionner le scroll du left_selector sur *son* index
        # courant
        self.left_selector.highlight_current_index()

        # prévenir le parent
        self.parent.vector_selected(acqid, vector_name)

        return


    def multi_vectors_selected(self, acqid, vector_names):
        """ Repositionne le selecteur de gauche
            Transmet la liste des noms du vecteur au parent.
        """
        logger.log(logging.RUN, f"Selection::multi_vectors_selected : " +\
                                f"acqid = {acqid}, vector_names = {vector_names}")


        # au cas où, repositionner le scroll du left_selector sur *son* index
        # courant
        self.left_selector.highlight_current_index()

        # prévenir le parent
        self.parent.multi_vectors_selected(acqid, vector_names)

        return


    def left_acqid_selected(self, acqid, index, role):
        """ Mise à jour du selecteur right :
            affichage des vecteurs de l'acqid sélectionné.

            Cette méthode est appelée par left_selector
        """
        logger.log(logging.RUN, f"Selection::left_acqid_selected : " +\
                                f"acqid = {acqid}, " +\
                                f"index.data() = {index.data()}, " +\
                                f"role = {role}")

        # vider self.acqid_edit
        self.acqid_edit.setText('')

        # prévenir le parent
        if self.notify_parent:
            self.notify_parent(model=index.model().name, index=index)

        # peupler le selector de droite
        self.right_selector.display_acqid(acqid)

        # mettre à jour l'acqid du parent
        self.parent.acqid_changed(acqid)

        return


    def left_expanded(self, index, role):
        """ left_selector a déplié 'index' => mettre à jour right_selector.

            Cette méthode est appelée par left_selector
        """
        logger.log(logging.RUN, f"Selection::left_expanded : " +\
                                f"index.data() = {index.data()}, " +\
                                f"index.model().name = {index.model().name}, " +\
                                f"role = {role}")

        # prévenir le parent
        if self.notify_parent:
            self.notify_parent(model=index.model().name, index=index)

        # le model de left_selector peut être acqid => le faire passer
        # sur le model de l'index reçu
        self.right_selector.change_root(index)

        return


    def left_selected(self, index):
        """ left_selector a affiché 'index'

            Cette méthode est appelée par left_selector
        """
        logger.log(logging.RUN, f"Selection::left_selected : " +\
                                f"index.data() = {index.data()}")
        logger.debug(f"rien à faire ? (suppression de l'historique)")

        return


    def get_model_and_index(self):
        """ retourne le model et l'index courant de left_selector.

            Cette méthode est appelée par Nav_tools.
        """
        logger.log(logging.RUN, "Selection::get_model_and_inde")

        model = self.left_selector.treeview.model().name
        index = self.left_selector.treeview.currentIndex()

        return model, index


    def right_acqid_selected(self, acqid, index):
        """ Afficher les vecteurs dans le selecteur de droite et
            mettre à jour du selecteur gauche.

            Cette méthode est appelée par right_selector
        """
        logger.log(logging.RUN, f"Selection::right_acqid_selected : " +\
                                f"acqid = {acqid}, " +\
                                f"index.data() = {index.data()}")

        # repositionner left_selector sur l'index et faire "comme si"
        # l'utilisateur venait de sélectionner cet index.
        self.left_selector.highlight_index(index)

        # peupler le selector de droite
        self.right_selector.display_acqid(acqid)

        # mettre à jour l'acqid du parent
        self.parent.acqid_changed(acqid)

        return


    def right_selected(self, index):
        """ rightleft_selector a affiché 'index' => mettre à jour right_selector.

            Cette méthode est appelée par right_selector
        """
        logger.log(logging.RUN, f"Selection::right_selected : " +\
                                f"index.model().name = {index.model().name}, " +\
                                f"index.data() = {index.data()}")

        # repositionner left_selector sur l'index et faire "comme si"
        # l'utilisateur venait de sélectionner cet index.
        self.left_selector.highlight_index(index)

        self.right_selector.change_root(index)

        return


    def write_settings(self):
        """ Enregistrement des préférences utilisateur.
        """
        logger.log(logging.RUN, "Selection::write_settings")

        button    = self.button_group.checkedButton()
        view_mode = button.view_mode
        if view_mode == 'by_date':
            date = self.date_edit.date()
        else:
            date = ''
        acqid_edit = self.acqid_edit.text()

        self.settings.setValue('mode'                    , view_mode)
        self.settings.setValue('date'                    , date)
        self.settings.setValue('acqid_edit'              , acqid_edit)
        self.settings.setValue('selection_splitter_sizes', self.splitter.saveState())

        self.left_selector.write_settings()
        self.right_selector.write_settings()

        return


    def restore_context(self, filiation):
        """ Restauration du contexte de la dernière session de l'utilisateur.
        """
        logger.log(logging.RUN, "Selection::restore_context")

        # view_mode : user préférences ou par default
        key = f'{self.settings.name}/mode'
        view_mode = self.settings.value(key, 'plateforme')
        for b in [self.button_plateforme, self.button_campagne, self.button_by_date]:
            if b.view_mode == view_mode:
                b.setChecked(True)
                break

        self.left_selector.restore_context(filiation)

        return

