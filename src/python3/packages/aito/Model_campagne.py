#!/usr/bin/env python3

"""
AITO
    Gestions du model campagne :
        arborescence : campagne -> plateforme -> year -> num
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

from AITO_icons      import icons
from Gest_acqid      import Gest_acqid
from Gest_campagne   import Gest_campagne

logger = logging.getLogger('aito')


class StandardItem_camp(QStandardItem):
    def __init__(self, txt='', role='', is_leaf=False, acqid=None, data_exists=True):
        """ Gestion des StandardItem pour le model campagne.

            :param str()  txt         : texte affiché
            :param str()  role        : rôle de l'item
                                        correspond au niveau de l'arborescence
                                        ('plateforme' ou 'year' ou 'num')
            :param bool() is_leaf     : gestion des icones :
                                        leaf = True  => icon file
                                        leaf = False => icon folder
            :param str()  acqid       : acqid de l'item de niveau 'num'
            :param bool() data_exists : True si les données sont présentes,
                                        False, sinon
        """
        super().__init__()
        # logger.log(logging.RUN, f"StandardItem_camp::__init__ : txt = {txt}")

        self.setEditable(False)
        self.setText(txt)
        self.setEnabled(data_exists)


        if is_leaf:
            self.setIcon(icons['icon_file'])
        else:
            self.setIcon(icons['folder_2'])

        # enregistrer le rôle
        self.setData(role, Qt.UserRole)

        # premier niveau en bold
        if role == 'campagne':
            font = self.font()
            font.setBold(True)
            self.setFont(font)

        # normalement, il n'y a que les leaf qui portent un acqid
        # ajouter le rôle
        if acqid:
            self.setData(acqid, Qt.UserRole + 1)

        return


class Model_campagne(QStandardItemModel):
    """ Gestion du model campagne.
        Arborescence : campagne -> plateforme -> year -> num
    """

    # signal de mise à jour de l'indicateur de progression
    in_progress_signal = pyqtSignal(int)


    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Model_campagne::__init__")

        self.parent     = kwargs.get('parent'    , None)
        self.name       = kwargs.get('name'      , None)
        self.gest_acqid = kwargs.get('gest_acqid', None)

        if not self.gest_acqid:
            raise Exception("Model_campagne::__init : no gest_acqid given")

        self.headers   = ['Nom', 'Date', 'Taille']

        self.gest_camp = Gest_campagne(gest_acqid=self.gest_acqid)

        self.populate_level_1()

        return


    def populate_level_1(self):
        """ Peuplement du premier niveau du model :
            nom des campagnes
        """
        logger.log(logging.RUN, "Model_campagne::populate_level_1")

        self.in_progress_signal.emit(0)

        # les entêtes de colonne
        self.setHorizontalHeaderLabels( [ self.headers[0] ] )

        # racine de l'arborescence
        root_node = self.invisibleRootItem()

        # récupérer la liste des noms des plateformes
        names = self.gest_camp.get_names()

        # ajouter chaque nom à l'arborescence
        for name in names:
            pltf_item  = StandardItem_camp(txt=name, role='campagne')

            root_node.appendRow(pltf_item)

        self.in_progress_signal.emit(100)

        return


    def populate_level_2(self, index):
        """ Peuplement du deuxième niveau du model :
            nom des plateformes de la campagne
            index est un nom de campagne.
        """
        logger.log(logging.RUN, "Model_campagne::populate_level_2")

        self.in_progress_signal.emit(0)

        # les entêtes de colonne
        self.setHorizontalHeaderLabels( [ self.headers[0] ] )

        # récupérer le StandardItem_camp lié à l'index reçu
        item = self.itemFromIndex(index)

        # le niveau est déjà rempli
        if item.hasChildren():
            self.in_progress_signal.emit(100)
            return


        # nom de la campagne à traiter
        camp = index.data()

        # récupérer la liste des plateformes de la campagne à traiter
        pltfs = self.gest_camp.get_pltfs(camp)

        # ajouter chaque plateforme à l'arborescence de la campagne
        for a_pltf in pltfs:
            pltf_item  = StandardItem_camp(txt=a_pltf, role='plateforme')

            item.appendRow(pltf_item)

        self.in_progress_signal.emit(100)

        return


    def populate_level_3(self, index):
        """ Peuplement du troisième niveau du model :
            années pour la plateforme de la campagne
            index est une plateforme.
        """
        logger.log(logging.RUN, f"Model_campagne::populate_level_3 : "
                                f"pltf = index.data() = {index.data()}")

        self.in_progress_signal.emit(0)

        # les entêtes de colonne
        self.setHorizontalHeaderLabels( [ self.headers[0] ] )

        # récupérer le StandardItem_camp lié à l'index reçu
        item = self.itemFromIndex(index)

        # le niveau est déjà rempli
        if item.hasChildren():
            self.in_progress_signal.emit(100)
            return


        # plateforme de la campagne à traiter
        pltf = index.data()

        # récupérer la campagne concernée (parent de l'index reçu)
        parent = index.parent()
        camp   = parent.data()

        # récupérer la liste des années de la plateforme pour la campagne
        years = self.gest_camp.get_years(camp, pltf)

        # ajouter chaque année à l'arborescence de la plateforme
        for a_year in years:
            year_item  = StandardItem_camp(txt=a_year, role='year')
            item.appendRow(year_item)

        self.in_progress_signal.emit(100)

        return


    def populate_level_4(self, index):
        """ Peuplement du quatrième niveau du model :
            num pour l'années de la plateforme de la campagne
            index est une année.
        """
        logger.log(logging.RUN, f"Model_campagne::populate_level_4 : "
                                f"year = index.data() = {index.data()}")

        self.in_progress_signal.emit(0)

        # les entêtes de colonne
        self.setHorizontalHeaderLabels(self.headers[0:2] )

        # récupérer le StandardItem_camp lié à l'index reçu
        item = self.itemFromIndex(index)

        # le niveau est déjà rempli
        if item.hasChildren():
            self.in_progress_signal.emit(100)
            return


        # année de la plateforme de la campagne à traiter
        year = index.data()

        # récupérer la plateforme concernée (parent de l'index reçu)
        parent1 = index.parent()
        pltf    = parent1.data()

        # récupérer la campagne concernée (parent de la plateforme)
        parent2 = parent1.parent()
        camp    = parent2.data()

        # récupérer la liste des numéros d'acquisition de camp/pltf/year
        num_infos = self.gest_camp.get_nums(camp, pltf, year)

        # ajouter chaque num d'acquisition à l'année de la plateforme concernée
        for num, infos in num_infos:
            num_item  = StandardItem_camp(txt         = num,
                                          role        = 'num',
                                          is_leaf     = False,
                                          acqid       = infos['acqid'],
                                          data_exists = infos['data_exists'])
            date      = QStandardItem(infos['date'])

            # rendre les informations supplémentaires non-clickable
            date.setEnabled(False)

            item.appendRow([num_item, date])

        self.in_progress_signal.emit(100)

        return

