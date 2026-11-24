#!/usr/bin/env python3

"""
AITO
    Gestions du model acqid (de selection des vecteurs) :
        pas d'arborescence : liste "name | date | size" en liste ou en icone
"""

import sys
import os
import logging

from PyQt5.Qt        import (QStandardItemModel,
                             QStandardItem,
                            )
from PyQt5.QtCore    import (Qt,
                             pyqtSignal,
                            )


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

from AITO_icons import icons

logger = logging.getLogger('aito')


class StandardItem_acqid(QStandardItem):
    def __init__(self, txt='', role='', is_leaf=False, acqid=None, data_exists=True):
        """ Gestion des StandardItem pour le model acqid.

            :param str()  txt         : texte affiché
            :param str()  role        : rôle de l'item
                                        ('vector')
            :param bool() is_leaf     : gestion des icones :
                                        leaf = True  => icon file
                                        leaf = False => icon folder
                                        permet de gérer les icones
            :param str()  acqid       : acqid de l'item de niveau 'num'
            :param bool() data_exists : True si les données sont présentes,
                                        False, sinon
        """
        super().__init__()
        #logger.log(logging.RUN, f"StandardItem_acqid::__init__ : txt = {txt}")

        self.setEditable(False)
        self.setText(txt)
        self.setEnabled(data_exists)


        if is_leaf:
            self.setIcon(icons['icon_file'])
        else:
            self.setIcon(icons['folder_2'])

        # enregistrer le rôle
        self.setData(role, Qt.UserRole)

        # normalement, il n'y a que les leaf qui portent un acqid
        # ajouter le rôle
        if acqid:
            self.setData(acqid, Qt.UserRole + 1)

        return


class StandardItem_infos(QStandardItem):
    def __init__(self, txt='', role='', acqid=None, data_exists=True):
        """ Gestion des StandardItem pour le model acqid (info date et size).

            :param str()  txt         : texte affiché
            :param str()  role        : rôle de l'item
                                        ('vector')
            :param str()  acqid       : acqid de l'item de niveau 'num'
            :param bool() data_exists : True si les données sont présentes,
                                        False, sinon
        """
        super().__init__()
        # logger.log(logging.RUN, f"StandardItem_infos::__init__ : txt = {txt}")

        self.setEditable(False)
        self.setText(txt)
        self.setEnabled(data_exists)

        # enregistrer le rôle
        self.setData(role, Qt.UserRole)
        self.setData(acqid, Qt.UserRole + 1)

        return


class Model_acqid(QStandardItemModel):
    """ Gestion du model acqid.
        pas d'arborescence : liste "name | date | size" en liste ou en icone
    """

    # signal de mise à jour de l'indicateur de progression
    in_progress_signal = pyqtSignal(int)


    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Model_acqid::__init__")

        self.parent     = kwargs.get('parent'    , None)
        self.name       = kwargs.get('name'      , None)
        self.gest_acqid = kwargs.get('gest_acqid', None)

        if not self.gest_acqid:
            raise Exception("Model_acqid::__init : no gest_acqid given")

        self.setHorizontalHeaderLabels(['Nom', 'Date', 'Taille'])

        return


    def populate_acqid(self, acqid):
        """ Peuplement du seul niveau du model.
        """
        logger.log(logging.RUN, "Model_acqid::populate_acqid")

        self.in_progress_signal.emit(0)

        # vider l'existant
        self.removeRows(0, self.rowCount())

        # racine de l'arborescence
        root_node = self.invisibleRootItem()
        root_node.setData('acqid', Qt.UserRole)

        # récupérer la liste des vecteurs
        vectors = self.gest_acqid.get_vectors(acqid)

        # ajouter chaque vecteur à la vue
        for vector in vectors:
            name = vector['name']
            date = vector['date']
            size = vector['size']

            # basename du nom du vecteur seulement
            name, ext = os.path.splitext(os.path.basename(name))

            vector_item = StandardItem_acqid(txt     = name,
                                             role    = 'vector',
                                             is_leaf = True,
                                             acqid   = acqid)
            date        = StandardItem_infos(txt     = date,
                                             role    = 'vector',
                                             acqid   = acqid)
            size        = StandardItem_infos(txt     = size,
                                             role    = 'vector',
                                             acqid   = acqid)

            root_node.appendRow([vector_item, date, size])

        self.in_progress_signal.emit(100)

        return

