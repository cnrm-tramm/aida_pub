#!/usr/bin/env python3

"""
AITO
    Création de QIcon à partir des icônes AIDA.
"""

import sys
import os
import glob

from PyQt5.QtGui  import QIcon
from PyQt5.QtCore import QSize

PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))


icons          = dict()
aida_dir_icons = None

def build_QIcons():
    """ Remplit le dictionnaire icons avec les icônes de AIDA
        Ceci ne peut être fait qu'une fois Qt initialisé.
    """

    global aida_dir_icons
    aida_dir_icons = os.path.join(os.getenv('AIDA_HOME'), 'share', 'icons')

    for f in glob.glob('*.png', root_dir=aida_dir_icons):
        name, ext = os.path.splitext(os.path.basename(f))
        icons[name] = QIcon(os.path.join(aida_dir_icons, f))

    for f in glob.glob('*.svg', root_dir=aida_dir_icons):
        name, ext = os.path.splitext(os.path.basename(f))
        icons[name] = QIcon(os.path.join(aida_dir_icons, f))

    return


def get_default_size():
    """ Retourne la taille par défaut des icônes
    """

    return QSize(20, 20)
