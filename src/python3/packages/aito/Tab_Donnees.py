#!/usr/bin/env python3

"""
AITO
    Gestion de la page Données.
"""

import sys
import os
import logging
import subprocess

from PyQt5.QtWidgets import (QWidget,
                             QPushButton,
                             QLabel,
                             QHBoxLayout, QVBoxLayout,
                             QScrollArea,
                             QSizePolicy,
                             QMessageBox,
                            )
from PyQt5.QtGui     import (QFont,
                            )
from PyQt5.QtCore    import (Qt,
                             pyqtSignal,
                            )


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from AITO_icons    import icons
from Plot_overview import Plot_overview

logger = logging.getLogger('aito')


class Tab_Donnees(QWidget):
    """ Gestion de la page Données.
    """

    # signal de mise à jour de l'indicateur de progression
    in_progress_signal = pyqtSignal(int)


    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Tab_Donnees::__init__")

        self.parent = kwargs.get('parent', None)

        self.vector = None

        # mise en place de l'IHM
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Tab_Donnees::setup_ihm")

        # les widgets graphiques
        self.plot_overview           = Plot_overview()

        button_arbre_genealogique    = QPushButton("arbre généalogique")
        button_vivect                = QPushButton("vivect")

        # affinage des premiers boutons
        button_arbre_genealogique.setToolTip("Affichage graphique de l'arbre " +\
                                             "généalogique du vecteur sélectionné.")
        button_vivect.setToolTip("Affichage ASCII du contenu " +\
                                 "du vecteur sélectionné.")

        # pilotage des Métadonnées
        button_vect_metadata         = QPushButton(icons['right_arrow'], None)
        label_vect_metadata          = QLabel("Métadonnées du vecteur")
        self.content_vect_metadata   = QLabel()
        self.content_vect_metadata.setFont (QFont ('Courier', 12))
        # - enrichissement du bouton
        button_vect_metadata.name    = 'metadata'
        button_vect_metadata.opened  = False
        button_vect_metadata.update  = self.show_metadata

        # pilotage des Ascendants
        button_vect_ancestors        = QPushButton(icons['right_arrow'], None)
        label_vect_ancestors         = QLabel("Ascendants du vecteur")
        self.content_vect_ancestors  = QLabel()
        self.content_vect_ancestors.setFont (QFont ('Courier', 12))
        # - enrichissement du bouton
        button_vect_ancestors.name   = 'ancestors'
        button_vect_ancestors.opened = False
        button_vect_ancestors.update = self.show_ancestors

        # pilotage des Versions
        button_vect_versions         = QPushButton(icons['right_arrow'], None)
        label_vect_versions          = QLabel("Versions du vecteur")
        self.content_vect_versions   = QLabel()
        self.content_vect_versions.setFont (QFont ('Courier', 12))
        # - enrichissement du bouton
        button_vect_versions.name    = 'versions'
        button_vect_versions.opened  = False
        button_vect_versions.update  = self.show_versions


        # une scrollarea pour ranger les infos du vecteur
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scroll_area_widget_content = QWidget()
        scroll_area_widget_content_layout = QVBoxLayout()
        scroll_area_widget_content.setLayout(scroll_area_widget_content_layout)

        # - métadonnées
        layout = QHBoxLayout()
        layout.addWidget(button_vect_metadata)
        layout.addWidget(label_vect_metadata)
        layout.addStretch()

        scroll_area_widget_content_layout.addLayout(layout)
        scroll_area_widget_content_layout.addWidget(self.content_vect_metadata)

        # - ancêtres
        layout = QHBoxLayout()
        layout.addWidget(button_vect_ancestors)
        layout.addWidget(label_vect_ancestors)
        layout.addStretch()

        scroll_area_widget_content_layout.addLayout(layout)
        scroll_area_widget_content_layout.addWidget(self.content_vect_ancestors)

        # - versions
        layout = QHBoxLayout()
        layout.addWidget(button_vect_versions)
        layout.addWidget(label_vect_versions)
        layout.addStretch()

        scroll_area_widget_content_layout.addLayout(layout)
        scroll_area_widget_content_layout.addWidget(self.content_vect_versions)

        scroll_area_widget_content_layout.addStretch()

        # ranger le scroll_area_widget_content dans la scroll_area
        scroll_area.setWidget(scroll_area_widget_content)

        # rangement des boutons dans leur layout
        layout_tools = QHBoxLayout()
        layout_tools.addWidget(button_arbre_genealogique)
        layout_tools.addWidget(button_vivect)
        layout_tools.addStretch()

        # rangement de tout ça dans le layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.plot_overview)
        layout.addLayout(layout_tools)
        layout.addWidget(scroll_area)

        # positionnement du layout
        self.setLayout(layout)

        # connexions
        button_vect_metadata.clicked.connect(self.show_infos)
        button_vect_ancestors.clicked.connect(self.show_infos)
        button_vect_versions.clicked.connect(self.show_infos)
        button_arbre_genealogique.clicked.connect(self.show_ancestry)
        button_vivect.clicked.connect(self.run_vivect)

        # une fenêtre pour afficher des messages
        self.message = QMessageBox(self)

        # mémoriser la liste des buttons d'information pour pouvoir les reseter
        self.buttons = [ button_vect_metadata,
                         button_vect_ancestors,
                         button_vect_versions,
                       ]
        return


    def show_metadata(self, show=True):
        """ Affiche/masque les métadonnées du vecteur.
        """
        logger.log(logging.RUN, f"Tab_Donnees::show_metadata : " +\
                                f"show = {show}")

        if self.content_vect_metadata.text() == '':
            header = self.parent.vector.header
            metadata = '\n'.join( [ f"{k:20s} = {v}"
                                        for k, v in header.items() ] )

            self.content_vect_metadata.setText(metadata)

        self.content_vect_metadata.setVisible(show)

        return


    def show_ancestors(self, show=True):
        """ Affiche/masque les ancêtres du vecteur.
        """
        logger.log(logging.RUN, f"Tab_Donnees::show_ancestors : " +\
                                f"show = {show}")

        if self.content_vect_ancestors.text() == '':
            self.vector.get_ancestors()
            ancestors = '\n'.join( [ f"{x}" for x in self.vector.ancestors ] )

            self.content_vect_ancestors.setText(ancestors)

        self.content_vect_ancestors.setVisible(show)

        return


    def show_versions(self, show=True):
        """ Affiche/masque les versions du vecteur.
        """
        logger.log(logging.RUN, f"Tab_Donnees::show_versions : " +\
                                f"show = {show}")

        if self.content_vect_versions.text() == '':
            self.vector.get_versions()
            versions = '\n'.join( [ f"{x}" for x in self.vector.versions ] )

            self.content_vect_versions.setText(versions)

        self.content_vect_versions.setVisible(show)

        return


    def show_infos(self):
        """ Affiche/masque l'info gérée par le bouton cliqué (sender).
        """
        logger.log(logging.RUN, f"Tab_Donnees::show_infos : " +\
                                f"sender = {self.sender().name}")

        self.in_progress_signal.emit(0)

        # traiter la demande
        sender = self.sender()

        if sender.opened:
            sender.opened = False
            sender.setIcon(icons['right_arrow'])
            sender.update(show=False)
        else:
            sender.opened = True
            sender.setIcon(icons['down_arrow'])
            sender.update(show=True)

        self.in_progress_signal.emit(100)

        return


    def show_ancestry(self):
        """ Fait générer par gengraphvect.py l'arbre généalogique du vecteur
            et affiche le résultat.
        """
        logger.log(logging.RUN, f"Tab_Donnees::show_infos : ")

        self.in_progress_signal.emit(0)

        name  = self.vector.name
        acqid = self.vector.acqid

        base_output = name + '.' + os.getenv('USER')
        result = subprocess.run(
                    [ 'gengraphvect.py', '-a', acqid,
                      '-n', '3', '-o', 'png', name , '-f', base_output],
                    capture_output=True,
                    text=True).stderr
        result = result.strip()

        if "OK" in result[-2:]:
            file_name = os.path.join('/tmp', base_output + '.png')
            subprocess.Popen( [ "xdg-open", file_name ] )
        else :
            msg = "<b>L'execution de gengraphvect.py a échoué :</b> <br/><br/>" +\
                  result

            self.message.setText(msg)
            self.message.exec()

        self.in_progress_signal.emit(100)

        return


    def run_vivect(self):
        """ Lance vivect.sh sur le vecteur.
        """
        logger.log(logging.RUN, f"Tab_Donnees::run_vivect")

        subprocess.Popen( [ 'simple_vivect.py',
                            self.vector.acqid, self.vector.name ] )

        return


    def clean_up(self):
        """ Remet la page dans son état initial.
        """
        logger.log(logging.RUN, f"Tab_Donnees::clean_up")

        for button in self.buttons:
            button.opened = False
            button.setIcon(icons['right_arrow'])

        self.content_vect_metadata.setText('')
        self.content_vect_ancestors.setText('')
        self.content_vect_versions.setText('')

        self.plot_overview.clear()
        self.vector = None

        return


    def vector_selected(self, vector):
        """ Mise à jour de la page avec les informations du vecteur.
        """
        logger.log(logging.RUN, f"Tab_Donnees::vector_selected : " +\
                                f"vector = {vector} : acqid = {vector.acqid}, " +\
                                f"vector = {vector.name}")

        self.in_progress_signal.emit(0)

        self.vector = vector
        self.plot_overview.update(vector)

        self.in_progress_signal.emit(100)

        return


    def update(self, **kwargs):
        """ Mise à jour de la page.

            Cette méthode *doit* exister
        """
        logger.log(logging.RUN, f"Tab_Donnees::update")

        logger.debug(f"rien à faire : kwargs.items() = {kwargs.items()}")

        return
