#!/usr/bin/env python3

"""
AITO
    Barre de navigation
"""

import sys
import os
import logging
import subprocess

from PyQt5.QtWidgets import (QWidget,
                             QPushButton,
                             QHBoxLayout,
                            )
from PyQt5.QtCore    import (pyqtSignal,
                            )

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from   AITO_icons import icons, get_default_size
import AITO_lib

logger = logging.getLogger('aito')


class Nav_tools(QWidget):
    """ Gestion des boutons de navigation
    """
    path_plateforme = os.getenv('AIDA_DATA')
    path_campagne   = os.path.join(os.getenv('AIDA_META'), 'campagnes')

    # signal de réouverture de la page initiale (bouton 'home')
    home_signal = pyqtSignal()


    def __init__(self, *args, **kwargs):
        super(QWidget, self).__init__()
        logger.log(logging.RUN, "Nav_tools::__init__")

        self.parent = kwargs.get('parent', None)

        # mise en place de l'IHM
        self.setup_ihm()

        return


    def setup_ihm(self):
        """ Mise en place des objets graphiques.
        """
        logger.log(logging.RUN, "Nav_tools::setup_ihm")

        layout = QHBoxLayout()

        # les widgets graphiques
        self.home     = QPushButton(icons['go_home' ], None)
        self.terminal = QPushButton(icons['terminal'], None)

        # affinage
        self.home.setIconSize(get_default_size())
        self.home.setToolTip("revenir à la première page ouverte")

        self.terminal.setToolTip("ouvrir un terminal")
        self.terminal.setIconSize(get_default_size())

        # ranger tout ça dans le layout
        layout.addWidget(self.home)
        layout.addWidget(self.terminal)
        layout.addStretch()

        self.setLayout(layout)

        # connexions
        self.home    .clicked.connect(self.goto_home)
        self.terminal.clicked.connect(self.run_terminal)

        return


    def run_terminal(self):
        """ lance un terminal là où le sélecteur de gauche est ouvert.
            Dans le pire des cas, ouvre un terminal dans self.path_plateforme
            (<=> $AIDA_DATA).
        """
        logger.log(logging.RUN, "Nav_tools::run_terminal")

        # dans le pire des cas, le terminal sera ouvert dans
        # self.path_plateforme
        path = self.path_plateforme

        # récupérer le model et l'index depuis le parent
        model, index = self.parent.get_model_and_index()
        logger.debug(f"model = {model}")
        logger.debug(f"index = {index}")

        if model == 'campagne':
            path =  self.path_campagne

        if not index:
            # pas d'index sélectionné
            # => on garde le path positionné
            pass
        else:
            # récupérer l'arborescence de l'ndex
            filiation = AITO_lib.get_index_filiation(index)
            logger.debug(f"filiation = {filiation}")

            if filiation:
                if model == 'by_date':
                    if not 'acqid' in filiation.keys():
                        # pas d'acqid => on garde le path par défaut
                        pass
                    else:
                        # posiotnner sur  le path de l'acqid
                        path = AIDA.ID_to_datapath(filiation['acqid'])
                else:
                    for key, val in filiation.items():
                        if key == 'model':
                            continue

                        if model == 'campagne':
                            if key == 'campagne':
                                if len(filiation) == 2:
                                    # on n'a que le nom d'une campagne
                                    # => on reste dans self.path_campagne (déjà
                                    # positionné)
                                    break
                                else:
                                    # on a au moins le nom d'une platefome
                                    # => on passe sur self.path_plateforme
                                    path = self.path_plateforme
                                    continue
                        else:
                            if key == 'model':
                                continue

                        path = os.path.join(path, val)

        PS1 = "'aito-\w : '"
        ###cmd = f"xterm  -e bash -c \"export PS1={PS1} ; cd {path}; echo && bash --noprofile --norc\""
        cmd = f"xterm  -e bash -c \"export PS1={PS1} ; cd {path}; " +\
              f"echo && bash --noprofile --norc\""
        subprocess.Popen(cmd, shell=True)

        return


    def goto_home(self):
        """ Réaffiche la page initiale de l'application (enregistrée dans les
            préféences utilisateur)
        """
        logger.log(logging.RUN, "Nav_tools::goto_home")

        self.home_signal.emit()

        return

