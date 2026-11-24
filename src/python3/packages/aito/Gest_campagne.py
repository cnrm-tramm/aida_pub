#!/usr/bin/env python3

"""
AITO
    Traitement des campagnes

    Organise les informations des campagnes
    sous la forme d'un gros dictionnaire de dictionnaires :
        campagne -> plateforme -> année -> num

    Ex :
    'AIRGRAVI': {
        'infos': { header du fichier .camp
        },
        'pltfs': {
            'atr': {
               'years': {
                    '2018': {
                             '0001': {'acqid'      : acqid ,
                                      'data_exists': True  ,
                                      'data_pah'   : 'path',
                                      ...
                                     },
                            },
                    '2019': {
                             '0001': {'acqid'      : acqid ,
                                      'data_exists': True  ,
                                      'data_pah'   : 'path',
                                      ...
                                     },
                            },
               }
            },
            'toulouse-flux': {
               'years': { ...
               },
            },
        },
    },

"""

import sys
import os
import logging
from textwrap import wrap


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
import Camp

logger = logging.getLogger('aito')


class Gest_campagne():
    """ Gestion des campagnes.
    """

    def __init__(self, *args, **kwargs):
        logger.log(logging.RUN, "Gest_campagne::__init__")

        self.gest_acqid = kwargs.get('gest_acqid', None)
        if not self.gest_acqid:
            raise Exception("Gest_campagne::__init : no gest_acqid given")

        self.camps = dict()

        # autres type d'accès aux campagnes
        # - chaque clé est une plateforme, chaque value est la liste des
        #   campagnes dans lesquelles la plateforme a été engagée.
        self.camps_by_pltf = dict()

        self.populate_names()

        return


    def populate_names(self):
        """ Crée le premier niveau de l'arborescence avec le nom de toutes
            les campagnes.
        """
        logger.log(logging.RUN, "Gest_campagne::populate_names")

        # récupérer la liste des noms de campagne
        camps = Camp.existing_camp_files(name_only=True)

        # (tri case-insensitive des noms des campagnes)
        try:
            for camp in sorted(camps, key=str.lower):
                self.camps[camp] = dict()
        except Exception as e:
            logger.debug(f"EXCEPTION = {e}")
            print(f"\nEXCEPTION = {e}")
            return

        return

    def populate_pltfs(self, camp):
        """ Crée le niveau 'pltfs' pour la campagne 'camp'.
        """
        logger.log(logging.RUN, "Gest_campagne::populate_pltfs")

        # la campagne n'existe pas
        if not camp in self.camps.keys():
            raise Exception(f"Gest_campagne::populate_pltfs : " +\
                            f"la campagne '{camp}' n'existe pas.")

        # le niveau 'pltfs' de l'arborescence de la campagne est déjà
        # renseigné
        if 'pltfs' in self.camps[camp].keys():
            return

        # créer le niveau 'pltfs' de l'arborescence de la campagne
        self.camps[camp]['pltfs'] = dict()

        # récupérer les infos de la campagne
        infos = Camp.Campagne.info_from_file(camp)

        for pltf in sorted(infos['pltfs'].keys()):
            self.camps[camp]['pltfs'][pltf]  = dict()
            self.camps[camp]['pltfs'][pltf]['infos'] = infos['pltfs'][pltf]

        return


    def populate_years_and_num(self, camp, pltf):
        """ Crée le niveau 'years' pour la plateforme 'pltf' de la campagne
            'camp'.
            Crée également pour chaque année la liste des acqid
        """
        logger.log(logging.RUN, "Gest_campagne::populate_years_and_num")

        # la campagne n'existe pas
        if not camp in self.camps.keys():
            raise Exception(f"Gest_campagne::populate_years_and_num : " +\
                            f"la campagne '{camp}' n'existe pas.")

        # le niveau 'pltfs' n'existe pas
        if not 'pltfs' in self.camps[camp].keys():
            # créer le niveau 'pltfs' de l'arborescence de la campagne
            self.populate_pltfs(camp)

        # la plateforme n'existe pas pour la campagne
        if not pltf in self.camps[camp]['pltfs'].keys():
            raise Exception(f"Gest_campagne::populate_years_and_num : " +\
                            f"la plateforme '{pltf}' n'existe pas " +\
                            f"pour la campagne '{camp}'.")


        # le niveau 'years' de l'arborescence de la campagne/plateforme est
        # déjà renseigné
        if 'years' in self.camps[camp]['pltfs'][pltf].keys():
            return

        # créer le niveau 'years' de l'arborescence de la campagne/plateforme
        self.camps[camp]['pltfs'][pltf]['years'] = dict()

        # récupérer les infos de la campagne
        infos = Camp.Campagne.info_from_file(camp)

        # récupérer la liste compacte des acqid de la campagne/plateforme
        compact_acqids = infos['pltfs'][pltf]['liste_acqid']

        # l'opération 'expand_acqids_pltf' est couteuse
        # => pour ne pas avoir à la refaire, on construit aussi le niveau
        #    suivant ('num') de l'arborescence
        for acqid in Camp.expand_acqids_pltf(compact_acqids):
            # récupérer les informations de l'acqid
            infos       = self.gest_acqid.get_infos(acqid)
            num         = infos['num']
            date        = infos['date']
            year        = infos['year']
            data_exists = infos['data_exists']

            if not year in self.camps[camp]['pltfs'][pltf]['years'].keys():
                self.camps[camp]['pltfs'][pltf]['years'][year] = dict()

            self.camps[camp]['pltfs'][pltf]['years'][year][num] = dict()
            self.camps[camp]['pltfs'][pltf]['years'][year][num]['acqid']       = acqid
            self.camps[camp]['pltfs'][pltf]['years'][year][num]['date']        = date
            self.camps[camp]['pltfs'][pltf]['years'][year][num]['data_exists'] = data_exists

        return


    def get_names(self):
        """ Retourne la liste des campagnes
            (premier niveau de l'arborescence).
        """
        return self.camps.keys()


    def get_pltfs(self, camp):
        """ Retourne la liste des plateformes de la campagne
            (deuxième niveau de l'arborescence).
        """
        # si besoin, remplir le niveau 'pltfs' de l'arborescence pour camp
        self.populate_pltfs(camp)

        return self.camps[camp]['pltfs'].keys()


    def get_years(self, camp, pltf):
        """ Retourne la liste des années pour campagne/plateformes
            (troisième niveau de l'arborescence).
        """
        # si besoin, remplir le niveau 'years' de l'arborescence pour camp/pltf
        self.populate_years_and_num(camp, pltf)

        return self.camps[camp]['pltfs'][pltf]['years'].keys()


    def get_nums(self, camp, pltf, year):
        """ Retourne le dictionnaire des acquisition de l'arborescence
            campagne/plateformes/year
            (quatrièle niveau de l'arborescence).
        """
        # si besoin, remplir le niveau 'years' de l'arborescence pour camp/pltf
        self.populate_years_and_num(camp, pltf)

        return self.camps[camp]['pltfs'][pltf]['years'][year].items()


    def get_header_infos(self, camp):
        """ Retourne la partie header du fichier de .camp
        """
        # la campagne n'existe pas
        if not camp in self.camps.keys():
            raise Exception(f"Gest_campagne::get_header_infos : " +\
                            f"la campagne '{camp}' n'existe pas.")

        # récupérer header_info de la campagne, si besoin
        if not 'infos' in self.camps[camp].keys():
            infos = Camp.Campagne.info_from_file(camp)
            self.camps[camp]['infos'] = infos['header']

        return self.camps[camp]['infos']


    def get_pltf_header_infos(self, camp, pltf):
        """ Retourne la partie pltf du fichier de .camp
        """
        # la campagne n'existe pas
        if not camp in self.camps.keys():
            raise Exception(f"Gest_campagne::get_pltf_header_infos : " +\
                            f"la campagne '{camp}' n'existe pas.")

        # la plateforme n'existe pas
        if not pltf in self.camps[camp]['pltfs'].keys():
            raise Exception(f"Gest_campagne::get_pltf_header_infos : " +\
                            f"la plateforme '{pltf}' nexite pas " +\
                            f"pour la campagne '{camp}'.")

        #### récupérer header_info de la campagne, si besoin
        ###if not 'infos' in self.camps[camp].keys():
        ###    infos = Camp.Campagne.info_from_file(camp)
        ###    self.camps[camp]['infos'] = infos['header']

        return self.camps[camp]['pltfs'][pltf]['infos']


    def get_bounding_box(self, header):
        """ Retourne la bounding_box avec les informations du header.
        """
        lat_min = header.get('geospatial_lat_min', None)
        lon_min = header.get('geospatial_lon_min', None)
        lat_max = header.get('geospatial_lat_max', None)
        lon_max = header.get('geospatial_lon_max', None)
        if lat_min and lon_min and lat_max and lon_max:
            bounds = [ [ float(lat_min), float(lon_min) ],
                       [ float(lat_max), float(lon_max) ]
                     ]
        else:
            bounds = None

        return bounds


    def get_description(self, camp):
        """ Retourne la description de la campagne
            (utilisée pour la map)

                [description,
                  [[coordonnée Xmax,coordonnée Ymax],
                   [coordonnée Xmin,coordonnée Ymin]]
                ]
        """
        # la campagne n'existe pas
        if not camp in self.camps.keys():
            raise Exception(f"Gest_campagne::get_description : " +\
                            f"la campagne '{camp}' n'existe pas.")

        # récupérer header_info de la campagne, si besoin
        if not 'infos' in self.camps[camp].keys():
            infos = Camp.Campagne.info_from_file(camp)
            self.camps[camp]['infos'] = infos['header']

        # enregistrer les bounds, si besoin
        if not 'bounds' in self.camps[camp].keys():
            header = self.camps[camp]['infos']
            self.camps[camp]['bounds'] = self.get_bounding_box(header)

        desc   = self.camps[camp]['infos']['description']
        # formater les 'desc'
        desc = '<br/>'.join(wrap(desc, width=40))

        bounds = self.camps[camp]['bounds']

        description = [ f"<b>campagne</b>    : {camp}<br/>" +\
                        f"<b>description</b> : {desc}<br/>",
                        bounds
                      ]

        return description


    def get_campagnes_for_pltf(self, pltf):
        """ Retourne la liste des campagnes dans lesquelles la pateforme 'pltf'
            a été engagée.
        """
        if not pltf in self.camps_by_pltf.keys():
            self.camps_by_pltf[pltf] = Camp.get_campagnes_for_pltf(pltf)

        return self.camps_by_pltf[pltf]


if __name__ == '__main__':
    print(f"=== MAIN")

    import AIDA_logger
    logger = AIDA_logger.configure_AIDA_logging('test')

    from Gest_acqid import Gest_acqid


    gest_acqid = Gest_acqid()
    gest_camp  = Gest_campagne(gest_acqid=gest_acqid)

    print(f"=== Liste des campagnes (niveau 1)")
    for camp_name in gest_camp.get_names():
        print(f"  - {camp_name}")
    input('...')


    # interrogation d'une campagne
    camp = 'HISA-3'
    print(f"=== Liste des plateformes de la campagne : {camp}")
    for pltf in gest_camp.get_pltfs(camp):
        print(f"  - {pltf}")
    input('...')

    # interrogation d'une campagne/plateforme
    pltf = 'atr'
    print(f"=== Années de la plateforme : {pltf} pour la campagne {camp}")
    for year in gest_camp.get_years(camp, pltf):
        print(f"  - {year}")
    input('...')


    # interrogation d'une campagne/plateforme/year
    year = '2019'
    print(f"=== Acquisition de la plateforme : {pltf} pour l'année {year} pour la campagne {camp}")
    for year, infos in gest_camp.get_nums(camp, pltf, year):
        print(f"  - {year} : {infos}")
    input('...')


    # interrogation d'une campagne/plateforme/year
    year = '2020'
    print(f"=== Acquisition de la plateforme : {pltf} pour l'année {year} pour la campagne {camp}")
    for year, infos in gest_camp.get_nums(camp, pltf, year):
        print(f"  - {year} : {infos}")
    input('...')


    # listes des campagnes d'une plateforme
    pltf = 'atr'
    campagnes = gest_camp.get_campagnes_for_pltf(pltf)
    print(f"=== listes des campagnes pour : {pltf}")
    for campagne in campagnes:
        print(f"  - {campagne}")
    input('...')


    # interrogation d'une campagne
    camp = 'EXPRESSO'
    print(f"=== Liste des plateformes de la campagne : {camp}")
    for pltf in gest_camp.get_pltfs(camp):
        print(f"  - {pltf}")
    input('...')
