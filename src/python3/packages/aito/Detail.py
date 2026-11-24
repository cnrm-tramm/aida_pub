#!/usr/bin/env python3

"""
AITO
   Gestion de la partie Détail.
"""

import sys
import os
import logging
from   enum import Enum

from PyQt5.QtWidgets import (QWidget,
                             QTabWidget,
                             QPushButton,
                             QHBoxLayout, QVBoxLayout,
                             QSplitter,
                             QMessageBox,
                            )
from PyQt5.QtCore    import (Qt,
                             QSettings,
                            )


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from   Selection        import Selection
from   Tab_Donnees      import Tab_Donnees
from   Tab_Informations import Tab_Informations
from   Tab_Traitements  import Tab_Traitements
from   Vector           import Vector
import AITO_lib
###from Splitter_handler import Splitter_handler

logger = logging.getLogger('aito')


class Detail(QWidget):
    """ Gestion de la page Detail
    """

    # page <-> index du QTabWidget
    class page_index (Enum):
        DONNEES      = 0
        INFORMATIONS = 1
        TRAITEMENTS  = 2


    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Detail::__init__")

        self.parent = kwargs.get('parent', None)
        self.app    = kwargs.get('app'   , None)


        # récupérer les objets de l'application (models, gest_XXX...)
        self.models     = self.parent.models
        self.gest_acqid = self.parent.gest_acqid

        self.vector = None

        # préférences utilisateur
        self.settings      = QSettings()
        self.settings.name = 'Detail'

        # mise en place de l'IHM
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Detail::setup_ihm")

        # les widgets graphiques
        # - la Selection
        self.selection = Selection(parent=self)

        # - les objets du tabwidget
        #   (toutes les pages ont une méthode : update(self, **kwargs)
        tab_donnees      = Tab_Donnees     (parent=self)
        tab_informations = Tab_Informations(parent=self)
        tab_traitements  = Tab_Traitements (parent=self, app=self.app)

        # - le tabwidget des détails
        self.detail_tabs = QTabWidget()
        self.detail_tabs.addTab(tab_donnees     , 'Données')
        self.detail_tabs.addTab(tab_informations, 'Informations')
        self.detail_tabs.addTab(tab_traitements , 'Traitements')

        # désactiver les pages DONNEES et TRAITEMENT
        self.enable_vector_tabs(False)

        # positionner sur la page INFORMATION
        self.detail_tabs.setCurrentIndex(self.page_index.INFORMATIONS.value)

        # un splitter pour ranger tout ça
        ###splitter = Splitter_handler(Qt.Horizontal)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.selection)
        self.splitter.addWidget(self.detail_tabs)

        # - taille : user préférences ou par default
        try:
            key = f'{self.settings.name}/splitter_sizes'
            self.splitter.restoreState( self.settings.value(key) )
        except Exception as e:
            self.splitter.setSizes([263, 263])


        # rangement de tout ça dans le layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.splitter)

        # positionnement du layout
        self.setLayout(layout)

        # connexions
        self.detail_tabs.currentChanged.connect(self.detail_tab_changed)

        # une fenêtre pour afficher des messages
        self.message = QMessageBox(self)

        return


    def view_selected_index(self, index):
        """ Positionne la vue sur l'index reçu.
        """
        logger.log(logging.RUN, f"Detail::view_selected_index : " +\
                                f"index.data() = {index.data()}")

        self.selection.left_selector.highlight_index(index)

        return


    def enable_vector_tabs(self, enable=False):
        """ Active/Désactive les pages DONNEES et TRAITEMENTS (elles ne sont
            active que lorsqu'un vecteur est sélectionné.
        """
        logger.log(logging.RUN, f"Detail::enable_vector_tabs : " +\
                                f"enable = {enable}")

        if not enable:
            self.vector = None
            self.acqid  = None

        self.detail_tabs.setTabEnabled(self.page_index.DONNEES.value    , enable)
        self.detail_tabs.setTabEnabled(self.page_index.TRAITEMENTS.value, enable)

        # cas spécifique au format string32 : pas de traitement
        if enable and self.vector.header['format'] == 'string32':
            self.detail_tabs.setTabEnabled(self.page_index.TRAITEMENTS.value, False)

        return


    def notify(self, model=None, index=None):
        """ Selection prévient que quelque chose a changé...
        """
        logger.log(logging.RUN, f"Detail::notify : " +\
                                f"model = {model}")
        if index:
            logger.debug(f"index.data() = {index.data()}")

        if index:
            filiation = AITO_lib.get_index_filiation(index)
        else:
            filiation = None

        self.detail_tabs.setCurrentIndex(self.page_index.INFORMATIONS.value)
        self.detail_tabs.currentWidget().update(model=model, filiation=filiation)

        self.enable_vector_tabs(False)

        return


    def detail_tab_changed(self, index):
        """ L'onglet index a été sélectioné.
        """
        logger.log(logging.RUN,f"Detail::detail_tab_changed : index = {index}")
        logger.debug("il reste peut-être des choses à faire...")

        #### vider les variables qui ne sont plus d'actualité
        ###if index == self.page_index.INFORMATIONS.value:
        ###    self.vector = None
        ###    self.acqid  = None

        # mise à jour de la page
        # (toutes les pages ont une méthode : update(self, **kwargs)
        self.detail_tabs.currentWidget().update(vector=self.vector)

        return


    def read_vector(self, acqid, vector_name):
        """ Lire le vecteur demandé.
        """
        logger.log(logging.RUN, f"Detail::read_vector : " +\
                                f"acqid = {acqid}, vector_name = {vector_name}")

        self.acqid = acqid

        # création de l'objet Vector pour le vecteur sélectionné
        self.vector = None
        try:
            self.vector = Vector(acqid=acqid, name=vector_name)
        except Exception as e:
            self.message.setText(f"Problème de lecture du vecteur " +\
                                 f"'{vector_name}' :\n" +\
                                 f"{e}")
            self.message.exec()

            return False

        return True


    def vector_selected(self, acqid, vector_name):
        """ Traiter le vecteur sélectionné.

            Cette méthode est appelée par Selection.
        """
        logger.log(logging.RUN, f"Detail::vector_selected : " +\
                                f"acqid = {acqid}, vector_name = {vector_name}")

        # lire le vecteur
        if not self.read_vector(acqid, vector_name):
            ###self.message.setText(f"Problème de lecture du vecteur " +\
            ###                     f"'{vector_name}'")
            ###self.message.exec()

            return

        # activer les pages DONNEES et TRAITEMENTS
        self.enable_vector_tabs(True)

        # sélection et mise à jour de la page DONNEES
        # ATTENTION : si on est déjà sur la page Donnees alors
        # la méthode self.detail_tab_changed n'est pas appelée...
        self.detail_tabs.setCurrentIndex(self.page_index.DONNEES.value)
        self.detail_tabs.currentWidget().clean_up()
        self.detail_tabs.currentWidget().vector_selected(self.vector)

        return


    def acqid_changed(self, acqid):
        """ La Selection avertie qu'un acqid a été sélectionné.
        """
        logger.log(logging.RUN, f"Detail::acqid_changed")
        logger.debug(f"rien à faire")


    def write_settings(self):
        """ Enregistrement des préférences utilisateur.
        """
        logger.log(logging.RUN, f"Detail::write_settings")

        # settings des "widgets QT"
        current_index      = self.detail_tabs.currentIndex()
        page               = list(self.page_index)[current_index].name

        donnees_index      = self.page_index.DONNEES.value
        enable_vector_tabs = self.detail_tabs.isTabEnabled(donnees_index)

        vector_name = ''
        acqid       = ''
        if self.vector:
            vector_name = self.vector.name
            acqid       = self.acqid


        # enregirster le groupe de settings
        self.settings.beginGroup('Detail')

        self.settings.setValue('page'              , page)
        self.settings.setValue('enable_vector_tabs', int(enable_vector_tabs))
        self.settings.setValue('vector_name'       , vector_name)
        self.settings.setValue('acqid'             , acqid)
        self.settings.setValue('splitter_sizes'    , self.splitter.saveState())

        # les settings des "sous-widgets"
        self.selection.write_settings()

        self.settings.endGroup();

        return


    def restore_context(self):
        """ Restauration du contexte de la dernière session de l'utilisateur.
        """
        logger.log(logging.RUN, f"Detail::restore_context")

        key = f'{self.settings.name}/filiation'
        filiation = self.settings.value(key)

        if not filiation:
            return

        self.selection.restore_context(filiation)

        # si un vecteur était en visualisation...
        key = f'{self.settings.name}/vector_name'
        vector_name = self.settings.value(key, None)

        key = f'{self.settings.name}/acqid'
        acqid = self.settings.value(key, None)

        if vector_name and acqid:
            self.vector_selected(acqid, vector_name)
            ### TODO sélectionner (highlight) le vecteur dans le right_selector

        return
