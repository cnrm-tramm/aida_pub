#!/usr/bin/env python3

"""
AITO
    Gestions du model by-date :
        arborescence : year -> month -> day -> acqid
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

from AITO_icons   import icons
from Gest_acqid   import Gest_acqid
from Gest_by_date import Gest_by_date

logger = logging.getLogger('aito')


class StandardItem_by_date(QStandardItem):
    def __init__(self, txt='', role='', is_leaf=False, acqid=None, data_exists=True):
        """ Gestion des StandardItem pour le model plateforme.

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
        # logger.log(logging.RUN, f"StandardItem_by_date::__init__ : " +\
        #                         f"txt = {txt}, role = {role}")

        self.setEditable(False)
        if isinstance(txt, int):
            if txt < 10:
                txt = f"{txt:02d}"
            else:
                txt = f"{txt}"
        self.setText(txt)
        self.setEnabled(data_exists)


        if is_leaf:
            self.setIcon(icons['icon_file'])
        else:
            self.setIcon(icons['folder_2'])

        # enregistrer le rôle
        self.setData(role, Qt.UserRole)

        # premier niveau en bold
        if role == 'year':
            font = self.font()
            font.setBold(True)
            self.setFont(font)

        # normalement, il n'y a que les leaf qui portent un acqid
        # ajouter le rôle
        if acqid:
            self.setData(acqid, Qt.UserRole + 1)

        return


class Model_by_date(QStandardItemModel):
    """ Gestion du model plateforme.
        Arborescence : year -> month -> day -> acqid
    """

    # signal de mise à jour de l'indicateur de progression
    in_progress_signal = pyqtSignal(int)


    def __init__(self, *args, **kwargs):
        super().__init__()
        logger.log(logging.RUN, "Model_by_date::__init__")

        self.parent     = kwargs.get('parent'    , None)
        self.name       = kwargs.get('name'      , None)
        self.gest_acqid = kwargs.get('gest_acqid', None)

        if not self.gest_acqid:
            raise Exception("Model_by_date::__init : no gest_acqid given")

        self.gest_by_date = Gest_by_date(gest_acqid=self.gest_acqid)

        return


    def populate_levels(self, year, month, day):
        """ Peuplement du premier niveau du model
            puis si besoin de chaque sous-niveau
        """
        logger.log(logging.RUN, "Model_by_date::populate_levels")

        self.in_progress_signal.emit(0)

        # récupérer la liste l'année
        a_year = self.gest_by_date.get_year(year)

        # l'année n'existe pas
        if not a_year:
            self.in_progress_signal.emit(100)
            return

        # l'année est déjà renseignée
        still_exists = self.findItems(f"{year}")
        if len(still_exists) > 0:
            self.in_progress_signal.emit(100)
            return

        # racine de l'arborescence
        root_node = self.invisibleRootItem()

        # ajouter l'année à l'arborescence
        year_item = StandardItem_by_date(txt         = f"{year}",
                                         role        = 'year',
                                         data_exists = not a_year is None)
        root_node.appendRow(year_item)

        if not a_year:
            self.in_progress_signal.emit(100)
            return

        # peupler les mois de l'année
        self.populate_level_2(year, month, day, year_item)

        self.in_progress_signal.emit(100)

        return


    def populate_level_2(self, year, month, day, year_item):
        """ Peuplement du deuxième niveau du model : mois
            puis si besoin de chaque sous-niveau
        """
        # logger.log(logging.RUN, f"Model_by_date::populate_level_2 : " +\
        #                         f"pour year_item = {year_item.text()}")

        # récupérer la liste des mois de l'année pour lesquels il existe des
        # acquisitions (=> data_exists = True)
        months = self.gest_by_date.get_months_of_year(year)

        for a_month in months:
            month_item = StandardItem_by_date(txt         = a_month,
                                              role        = 'month',
                                              data_exists = True)

            year_item.appendRow(month_item)

            # peupler les jour du mois de l'année
            self.populate_level_3(year, a_month, day, month_item)

        self.in_progress_signal.emit(100)

        return


    def populate_level_3(self, year, month, day, month_item):
        """ Peuplement du troisième niveau du model : jours
            puis si besoin de chaque sous-niveau
        """
        # logger.log(logging.RUN, f"Model_by_date::populate_level_3 : " +\
        #                         f" pour month_item = {month_item.text()}")

        self.in_progress_signal.emit(0)

        # récupérer la liste des jours du mois de l'année pour lesquels il
        # existe des acquisitions (=> data_exists = True)
        days = self.gest_by_date.get_days_of_year_month(year, month)

        for a_day in days:

            day_item = StandardItem_by_date(txt         = a_day,
                                            role        = 'day',
                                            data_exists = True)

            month_item.appendRow(day_item)

            # peupler les acquisitions du jour du mois de l'année
            self.populate_level_4(year, month, a_day, day_item)

        self.in_progress_signal.emit(100)

        return


    def populate_level_4(self, year, month, day, day_item):
        """ Peuplement du quatrième niveau du model : acqid
        """
        # logger.log(logging.RUN, f"Model_by_date::populate_level_4 : " +\
        #                         f"pour day_item = {day_item.text()}")

        self.in_progress_signal.emit(0)

        # récupérer les dictionnaires des acquitions du jours du mois de
        # l'année pour lesquels il existe des acquisitions.
        acqids = self.gest_by_date.get_acqids_of_date(year, month, day)

        for a_acqid, infos in acqids.items():
            acqid_item  = StandardItem_by_date(txt         = a_acqid,
                                               role        = 'acqid',
                                               is_leaf     = False,
                                               acqid       = a_acqid,
                                               data_exists = infos['data_exists'])

            day_item.appendRow(acqid_item)
        self.in_progress_signal.emit(100)

        return


    def get_item_date(self, year, month, day):
        """ Return la liste des index (pas des items) permettant d'accéder à
            la date reçue.
            (typiquement pour expander la date)

            TODO : ça fonctionne mais ça me semble trop complexe. Doit y'avoir
                   mieux à faire...
        """
        logger.log(logging.RUN, f"Model_by_date::get_item_date : " +\
                                 f"{year}/{month}/{day}")

        self.in_progress_signal.emit(0)

        ret_list = list()

        # chercher l'année
        # ----------------
        s_year = f"{year}"
        year_items = self.findItems(s_year)

        if len(year_items) == 0:
            # année non trouvée => retourner une liste vide
            self.in_progress_signal.emit(100)
            return ret_list

        year_item = year_items[0]

        # ajouter l'index de l'année à la liste de retour
        ret_list.append(self.indexFromItem(year_item))

        if not year_items[0].hasChildren():
            # année sans enfant => retourner une liste vide
            self.in_progress_signal.emit(100)
            return ret_list


        # chercher le mois
        # ----------------
        month_item = None
        s_month = f"{month:02d}"
        for row in range(year_item.rowCount()):
            if year_item.child(row).text() == s_month:
                month_item = year_item.child(row)
                break

        if not month_item or not month_item.hasChildren():
            # mois non trouvé ou sans d'enfant => retourner l'index de l'année
            self.in_progress_signal.emit(100)
            return ret_list

        # ajouter l'index du mois à la liste de retour
        ret_list.append(self.indexFromItem(month_item))


        # chercher le jour
        # ----------------
        day_item = None
        s_day = f"{day:02d}"
        for row in range(month_item.rowCount()):
            if month_item.child(row).text() == s_day:
                day_item = month_item.child(row)
                break

        if not day_item:
            # jour non trouvé => retourner l'index de l'année et du mois
            self.in_progress_signal.emit(100)
            return ret_list

        # ajouter l'index du jour à la liste de retour
        ret_list.append(self.indexFromItem(day_item))

        self.in_progress_signal.emit(100)

        return ret_list

