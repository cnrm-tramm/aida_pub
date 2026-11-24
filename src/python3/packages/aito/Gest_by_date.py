#!/usr/bin/env python3

"""
AITO
    Traitement des acqids par date

    Afin de limiter la lourdeur des traitements, on ne traite que les années
    demandées par l'utilisateur.

    Organise les informations des plateformes
    sous la forme d'un gros dictionnaire de dictionnaires :
    year -> month -> day -> acqids

    Ex :
    'years': {
              '2020': {
                       '01': {
                              '01': {
                                      'acqid': { 'data_exists': True,
                                                 ...
                                               }
                              }
                              '31': {
                                      'acqid': { 'data_exists': False,
                                                 ...
                                               }
                              }
                       },
                       '12': {
                              '04': {
                                      'acqid': { 'data_exists': True,
                                                 ...
                                               }
                              }
                              '12': {
                                      'acqid': { 'data_exists': False,
                                                 ...
                                               }
                              }
                       },
              }
    }
"""

import sys
import os
import logging
import glob
import time


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

logger = logging.getLogger('aito')


class Gest_by_date():
    """ Gestion des acqids par date
    """

    def __init__(self, *args, **kwargs):
        logger.log(logging.RUN, "Gest_by_date::__init__")

        self.gest_acqid = kwargs.get('gest_acqid', None)
        if not self.gest_acqid:
            raise Exception("Gest_by_date::__init : no gest_acqid given")

        # TODO : initialiser first_year et last_year *avec* les infos tirées
        #        des .inf...
        # self.first_year = 1992
        # self.last_year  = 2023

        self.dates          = dict()
        self.dates['years'] = dict()

        # récupérer la liste des plateformes
        # AIDA.plt_by_name retourne aussi les alias =>
        # utiliser AIDA.plt_by_abrev pour récupérer seulement les noms des
        # plateformes
        pltfs = list()
        for abrev, info in AIDA.plt_by_abrev.items():
            pltfs.append(info.nom)

        self.pltfs = sorted(pltfs)

        return


    def populate_year(self, year):
        """ Crée tous les niveau de l'arborescence pour l'année demandée.
            year -> month -> day -> acqids
        """
        # logger.log(logging.RUN, f"Gest_by_date::populate_year " +\
        #                         f"{year}, TYPE = {type(year)}"))

        # le niveau 'years' pour l'année year est déjà renseigné
        if year in self.dates['years']:
            # DBG print(f"!!! Gest_by_date::populate_year : {year} :  : DEJA FAIT :-)")
            return

        # pour tous les acqids de l'année, créer tous les niveaux de
        # l'arborescence pour l'année
        for acqid in sorted(AIDA.existing_inf_files(self.pltfs,
                                                    liste_annees=[year],
                                                    names_only=True,
                                                    very_verbose=False)):
            # crée l'année
            if not year in self.dates['years'].keys():
                self.dates['years'][year] = dict()

            # nom de la plateforme
            # TODO : j'ai oublié le niveau name MAIS je ne suis pas
            #        convaincue de son utilité...
            abrev = acqid[0:2]
            name = AIDA.plt_by_abrev[abrev].nom

            # récupérer les informations de l'acqid
            infos       = self.gest_acqid.get_infos(acqid)
            if not infos:
                # DBG print(f"!!! Gest_by_date::populate_year : infos : {infos} PB POUR {acqid}")
                continue

            data_exists = infos['data_exists']
            month       = infos['month']
            day         = infos['day']

            # créer le mois, si besoin
            if not month in self.dates['years'][year].keys():
                self.dates['years'][year][month] = dict()

            # créer le jour, si besoin
            if not day in self.dates['years'][year][month].keys():
                self.dates['years'][year][month][day] = dict()

            # enregistrer les informations de l'acqid
            self.dates['years'][year][month][day][acqid] = dict()
            self.dates['years'][year][month][day][acqid]['data_exists'] = data_exists

        return


    def get_year(self, year):
        """ Retourne year, s'il existe des acquisition pour year
            sinon None.
        """
        # si besoin, remplir le niveau 'year' de l'arborescence pour l'année
        self.populate_year(year)

        if year in self.dates['years'].keys():
            return year
        else:
            return None


    def get_months_of_year(self, year):
        """ Retourne la liste des mois de l'année year pour lesquels il existe
            des acquisitions.
        """
        # logger.log(logging.RUN, f"Gest_by_date::get_months_of_year " +\
        #                         f"{year}, TYPE = {type(year)}"))

        # si besoin, remplir le niveau 'year' de l'arborescence pour l'année
        self.populate_year(year)

        try:
            return sorted(self.dates['years'][year].keys())
        except Exception as e:
            # DBG print(f"!!! EXCEPTION : {e}")
            return list()


    def get_days_of_year_month(self, year, month):
        """ Retourne la liste des jours de l'année year iet du mois month pour
            lesquels il existe des acquisitions.
        """
        # si besoin, remplir le niveau 'year' de l'arborescence pour l'année
        self.populate_year(year)

        try:
            return sorted(self.dates['years'][year][month].keys())
        except Exception as e:
            return list()


    def get_acqids_of_date(self, year, month, day):
        """ Retourne les dictionnaires des acqids pour la date fournie.
        """
        # si besoin, remplir le niveau 'year' de l'arborescence pour l'année
        self.populate_year(year)

        try:
            return self.dates['years'][year][month][day]
        except Exception as e:
            return dict()



if __name__ == '__main__':
    print(f"=== MAIN")

    import AIDA_logger
    logger = AIDA_logger.configure_AIDA_logging('test')

    from Gest_acqid import Gest_acqid


    gest_acqid   = Gest_acqid()
    gest_by_date = Gest_by_date(gest_acqid=gest_acqid)

    # Cas valides
    print(f"\nCAS VALIDES")
    year  = 2023
    month = 4
    day   = 18
    print(f"\n=== acqid pour l'année/mois/jour {year}/{month}/{day} :")
    input('...')
    acqids = gest_by_date.get_acqids_of_date(year, month, day)
    for acqid, infos in acqids.items():
        print(f"  - acqid = {acqid}, {infos}")
    input('...')


    print(f"\nDEMANDE IDENTIQUE => les interrogations ne sont pas refaites")
    input('...')
    print(f"=== acqid pour l'année/mois/jour {year}/{month}/{day} :")
    acqids = gest_by_date.get_acqids_of_date(year, month, day)
    for acqid, infos in acqids.items():
        print(f"  - acqid = {acqid}, {infos}")
    input('...')

    print(f"\n=== get_year({year}) :")
    a_year = gest_by_date.get_year(year)
    if a_year:
        print(f"  - year = {year}")
    input('...')


    print(f"\n=== get_months_of_year({year}) :")
    months = gest_by_date.get_months_of_year(year)
    for month in months:
        print(f"  - months = {month}")
    input('...')


    # erreurs
    year = 2024
    print(f"\nERREUR === année {year} :")
    a_year = gest_by_date.get_year(year)
    if a_year:
        print(f"  - year = {month}")
    input('...')


    print(f"\nERREUR === mois pour l'année {year} :")
    months = gest_by_date.get_months_of_year(year)
    for month in months:
        print(f"  - months = {month}")
    input('...')


    year  = 2022
    month = 18
    print(f"\nERREUR === jours pour l'année/mois {year}/{month} :")
    days = gest_by_date.get_days_of_year_month(year, month)
    for day in days:
        print(f"  - day = {day}")
    input('...')


    year  = 2022
    month = 18
    day   = 18
    print(f"\nERREUR === acqid pour l'année/mois/jour {year}/{month}/{day} :")
    acqids = gest_by_date.get_acqids_of_date(year, month, day)
    for acqid, infos in acqids.items():
        print(f"  - acqid = {acqid}, {infos}")
    input('...')


    year = 2023
    print(f"\n=== mois pour l'année {year} :")
    months = gest_by_date.get_months_of_year(year)
    for month in months:
         print(f"  - months = {month}")
    input('...')


    month = 1
    print(f"\n=== jours pour l'année/mois {year}/{month} :")
    days = gest_by_date.get_days_of_year_month(year, month)
    for day in days:
        print(f"  - day = {day}")
    input('...')


    day = 1
    print(f"\n=== acqid pour l'année/mois/jour {year}/{month}/{day} :")
    acqids = gest_by_date.get_acqids_of_date(year, month, day)
    for acqid, infos in acqids.items():
        print(f"  - acqid = {acqid}, {infos}")
    input('...')


    day = 31
    print(f"\n=== acqid pour l'année/mois/jour {year}/{month}/{day} :")
    acqids = gest_by_date.get_acqids_of_date(year, month, day)
    for acqid, infos in acqids.items():
        print(f"  - acqid = {acqid}, {infos}")
    input('...')


    day = 41
    print(f"\n=== acqid pour l'année/mois/jour {year}/{month}/{day} :")
    acqids = gest_by_date.get_acqids_of_date(year, month, day)
    for acqid, infos in acqids.items():
        print(f"  - acqid = {acqid}, {infos}")
    input('...')


    year  = 2022
    month = 1
    day   = 18
    print(f"\n=== acqid pour l'année/mois/jour {year}/{month}/{day} :")
    acqids = gest_by_date.get_acqids_of_date(year, month, day)
    for acqid, infos in acqids.items():
        print(f"  - acqid = {acqid}, {infos}")
    input('...')

