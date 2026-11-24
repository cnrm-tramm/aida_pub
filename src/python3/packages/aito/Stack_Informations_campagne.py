#!/usr/bin/env python3

"""
AITO
    Gestion de la partie textuelle de la page Information pour les campagnes
    > campagne
    > plateformes
    > .inf
"""

import sys
import os
import logging

from PyQt5.QtWidgets import (QWidget,
                             QPushButton, QLabel,
                             QLayout,
                             QHBoxLayout, QVBoxLayout, QGridLayout,
                             QSizePolicy,
                            )
from PyQt5.QtGui     import (QFont,
                            )

PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from AITO_icons import icons

logger = logging.getLogger('aito')


class Stack_Informations_campagne(QWidget):
    """ Gestion de la partie textuelle de la page Information
        pour les campagnes
    """

    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Stack_Informations_campagne::__init__")

        self.parent    = kwargs.get('parent', None)

        # récupérer les objets de l'application (models, gest_XXX...)
        self.models     = self.parent.models
        self.gest_camp  = self.models['campagne'].gest_camp
        self.gest_pltf  = self.models['plateforme'].gest_pltf
        self.gest_acqid = self.models['acqid'].gest_acqid

        self.camp_name = None
        self.acqid     = None

        # mise en place de l'IHM
        self.button_size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Stack_Informations_campagne::_setup_ihm")

        # les widgets graphiques
        self.button_metadata        = QPushButton(icons['right_arrow'], None)
        label_campagne              = QLabel("<b>Métadonnées de la campagne</b>")
        self.label_metadata_content = QLabel("")

        label_plateforms            = QLabel("<b>Plateformes :</b>")
        self.grid_details           = QGridLayout()

        self.button_acqid           = QPushButton(icons['right_arrow'], None)
        label_acqid                 = QLabel("<b>Métadonnées de l'acquisition</b>")
        self.label_acqid_content    = QLabel("")


        # affinage
        self.button_metadata.opened  = False
        self.button_metadata.setSizePolicy(self.button_size_policy)
        self.label_metadata_content.setFont(QFont('Courier', 12))
        self.label_metadata_content.setWordWrap(True)

        self.button_acqid.opened  = False
        self.button_acqid.setSizePolicy(self.button_size_policy)
        self.label_acqid_content.setFont(QFont('Courier', 12))
        self.label_acqid_content.setWordWrap(True)

        # rangement des métadonnées
        layout_meta = QHBoxLayout()
        layout_meta.addWidget(self.button_metadata)
        layout_meta.addWidget(label_campagne)

        # rangement des métadonnées de l'acqid
        layout_acqid = QHBoxLayout()
        layout_acqid.addWidget(self.button_acqid)
        layout_acqid.addWidget(label_acqid)

        # rangement de tout ça dans le layout principal
        layout = QVBoxLayout()
        layout.addLayout(layout_meta)
        layout.addWidget(self.label_metadata_content)
        layout.addWidget(label_plateforms)
        layout.addLayout(self.grid_details)
        layout.addLayout(layout_acqid)
        layout.addWidget(self.label_acqid_content)

        layout.setSizeConstraint(QLayout.SetMinimumSize)

        # positionnement du layout
        self.setLayout(layout)

        # connexions
        self.button_metadata.clicked.connect(self.show_metadata)
        self.button_acqid.clicked.connect(self.show_acqid_header)

        return


    def init_page(self, camp_name=None):
        """ Initialise la page pour la campagne camp_name.
        """
        logger.log(logging.RUN, f"Stack_Informations_campagne::init_page : " +\
                                f"camp_name = {camp_name}")

        self.camp_name = camp_name
        self.acqid     = None

        self.button_metadata.opened = False
        self.button_metadata.setIcon(icons['right_arrow'])
        self.label_metadata_content.setText('')
        self.label_metadata_content.setHidden(True)

        self.button_acqid.opened = False
        self.button_acqid.setIcon(icons['right_arrow'])
        self.label_acqid_content.setText('')
        self.label_acqid_content.setHidden(True)

        # vider le grid
        grid = self.grid_details
        for i in reversed(range(grid.count())):
            try:
                if i%2 == 0:
                    layout = grid.itemAt(i).layout()
                    if layout:
                        for j in reversed(range(layout.count() - 1)):
                            w = layout.itemAt(j).widget()
                            if w:
                                w.deleteLater()
                        layout.deleteLater()
                else:
                    w = grid.itemAt(i).widget().deleteLater()
                    if w:
                        w.deleteLater()
            except Exception as e:
                pass

        if not camp_name:
            return

        # remplir le grid avec les plateformes de la campagne
        pltfs = self.gest_camp.get_pltfs(camp_name)
        if not pltfs:
            print(f"!!! Stack_Informations_campagne::init_page : PAS DE PLATEFORMES POUR camp_name = {camp_name}")
            return

        for nb, pltf in enumerate(pltfs):
            pos = self.gest_pltf.get_position(pltf)
            self.add_main_line_to_details(self.grid_details, pltf, pos, nb)

        return


    def add_main_line_to_details(self, widget_details, name, position, nb):
        """ Ajout une ligne : "'bouton' 'name' (position)" dans le widget
            widget_details.
            Prépare le label des details
        """
        logger.log(logging.RUN, f"Stack_Informations_campagne::" +\
                                f"add_main_line_to_details : " +\
                                f"name = {name}, nb = {nb}")

        # les widgets graphiques
        button_show   = QPushButton(icons['right_arrow'], None)
        label_name    = QLabel(f"<b>{name}</b> ({position})")
        label_content = QLabel("")

        # son affinage
        button_show.name          = name
        button_show.opened        = False
        button_show.label_content = label_content
        button_show.setSizePolicy(self.button_size_policy)
        label_content.setHidden(True)
        label_content.setWordWrap(True)
        label_content.setFont(QFont ('Courier', 12))

        # rangement du bouton et label dans un layout (sinon, le label est
        # décalé lorsqu'on affiche le content)
        layout = QHBoxLayout()
        layout.addWidget(button_show)
        layout.addWidget(label_name)
        layout.addStretch()

        # chaque information occupe 2 lignes
        widget_details.addLayout(layout, nb*2  , 0)
        widget_details.addWidget(label_content, nb*2+1, 0)

        # connexions
        button_show.clicked.connect(self.show_detail)

        return


    def init_acqid(self, acqid=None):
        """ Initialise les métadonnées de la page pour l'acqid
        """
        logger.log(logging.RUN, f"Stack_Informations_campagne::init_acqid : " +\
                                f"acqid = {acqid}")

        self.acqid = acqid

        self.button_acqid.opened = False
        self.button_acqid.setIcon(icons['right_arrow'])
        self.label_acqid_content.setText('')
        self.label_acqid_content.setHidden(True)

        return


    def show_metadata(self):
        """ Affiche/Masque les metadata de la campagne (issues du header du
            fichier de sdescritpion de la campagne)
        """
        if not self.camp_name:
            return

        sender = self.sender()

        # récupérer le header de la campagne
        if self.label_metadata_content.text() == '':
            infos = self.gest_camp.get_header_infos(self.camp_name)
            content = '\n'.join( [ f"{k:22s} : {v}"
                                        for k, v in infos.items() ] )
            self.label_metadata_content.setText(content)

        if sender.opened:
            sender.opened = False
            sender.setIcon(icons['right_arrow'])
            self.label_metadata_content.setHidden(True)
        else:
            sender.opened = True
            sender.setIcon(icons['down_arrow'])
            self.label_metadata_content.setHidden(False)

        return


    def show_detail(self):
        """ Affiche/Masque le detail demandé par le bouton sender
        """
        sender        = self.sender()
        pltf          = sender.name
        label_content = sender.label_content

        # récupérer le header de la plateforme
        if label_content.text() == '':
            infos = self.gest_camp.get_pltf_header_infos(self.camp_name, pltf)
            content = '\n'.join( [ f"{k:22s} : {v}"
                                        for k, v in infos.items() ] )
            label_content.setText(content)

        if sender.opened:
            sender.opened = False
            sender.setIcon(icons['right_arrow'])
            label_content.setHidden(True)
        else:
            sender.opened = True
            sender.setIcon(icons['down_arrow'])
            label_content.setHidden(False)

        return


    def show_acqid_header(self):
        """ Affiche/Masque le header de l'acquisition
        """
        logger.log(logging.RUN, f"Stack_Informations_campagne::show_acqid_header")

        if not self.camp_name or not self.acqid:
            return

        sender = self.sender()

        # récupérer le header du .Inf
        if self.label_acqid_content.text() == '':
            infos = self.gest_acqid.get_header_inf(self.acqid)
            content = '\n'.join( [ f"{k:22s} : {v}"
                                        for k, v in infos.items() ] )
            self.label_acqid_content.setText(content)

        if sender.opened:
            sender.opened = False
            sender.setIcon(icons['right_arrow'])
            self.label_acqid_content.setHidden(True)
        else:
            sender.opened = True
            sender.setIcon(icons['down_arrow'])
            self.label_acqid_content.setHidden(False)

        return

