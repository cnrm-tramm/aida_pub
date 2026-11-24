#!/usr/bin/env python3

"""
AITO
    Traitement des plateformes

    Organise les informations des plateformes
    sous la forme d'un gros dictionnaire de dictionnaires :
        plateforme -> année -> num

    Ex :
    'toulouse-flux': {
                      'years': {
                                '2020': {
                                         '0001': {'acqid'      : acqid ,
                                                  'data_exists': True  ,
                                                  'data_pah'   : 'path',
                                                  ...
                                         },
                                         '0002': {'acqid'      : acqid ,
                                                  'data_exists': False ,
                                                  'data_pah'   : Nonne ,
                                                  ...
                                         },
                                }
                      }
    }

    Note : pour le niveau 'num' :
           'data_exists' et 'data_pah' sont légèrement redondant, mais
           dans certains cas l'utilisation de l'un ou de l'autre est
           plus explicite.
"""

import sys
import os
import logging


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

logger = logging.getLogger('aito')


class Gest_plateforme():
    """ Gestion des plateformes.
    """

    def __init__(self, *args, **kwargs):
        logger.log(logging.RUN, "Gest_plateforme::__init__")

        self.gest_acqid = kwargs.get('gest_acqid', None)
        if not self.gest_acqid:
            raise Exception("Gest_plateforme::__init : no gest_acqid given")

        self.pltfs = dict()
        self.populate_names()

        return


    def populate_names(self):
        """ Crée le premier niveau de l'arborescence avec le nom de toutes
            les plateformes.
        """
        logger.log(logging.RUN, "Gest_plateforme::populate_names")

        # AIDA.plt_by_name retourne aussi les alias =>
        # utiliser AIDA.plt_by_abrev pour récupérer seulement les noms des
        # plateformes
        # récupérer les infos utiles pour la description
        pltfs = list()
        for abrev, infos in AIDA.plt_by_abrev.items():
            # position
            try:
                pos = infos.position.replace('+', '').replace(' ', '').split('/')
                position = [float(pos[0]),float(pos[1])]
            except Exception as e:
                if pos[0].lower() == 'mobile':
                    position = pos[0].lower()
                else:
                    position = None

            # altitude
            if len(pos) == 3:
                altitude = pos[2]
            else:
                altitude = None

            pltfs.append( (infos.nom, abrev, position, altitude) )

        # créer le premier niveau
        for pltf, abrev, pos, alt in sorted(pltfs, key=lambda x: x[0].lower()):
            self.pltfs[pltf] = dict()
            self.pltfs[pltf]['abrev']    = abrev
            self.pltfs[pltf]['position'] = pos
            self.pltfs[pltf]['altitude'] = alt

        return


    def populate_years(self, pltf):
        """ Crée le niveau 'years' pour la plateforme 'pltf'.
        """
        logger.log(logging.RUN, "Gest_plateforme::populate_years")

        # la plateforme n'existe pas
        if not pltf in self.pltfs.keys():
            raise Exception(f"Gest_plateforme::populate_years : " +\
                            f"la plateforme '{pltf}' n'existe pas.")

        # le niveau 'years' de l'arborescence de la plateforme est déjà
        # renseigné
        if 'years' in self.pltfs[pltf].keys():
            print(f"!!! Gest_plateforme::populate_years : DEJA FAIT :-)")
            return

        # créer le niveau 'year' de l'arborescence de la plateforme
        self.pltfs[pltf]['years'] = dict()

        # récupérer le noms des .inf (= acqid) existants pour la plateforme
        years = list()
        for acqid in sorted(AIDA.existing_inf_files([pltf],
                                                    names_only=True,
                                                    very_verbose=False)):
            # récupérer l'année de l'acqid
            long_name, year, num = AIDA.ID_to_full(acqid)

            # liste non triée des année
            if not year in years:
                years.append(year)

        # ajouter les années triées
        for year in sorted(years):
            self.pltfs[pltf]['years'][year] = dict()

        return


    def populate_nums(self, pltf, year):
        """ Crée le niveau 'num' pour la plateforme 'pltf' et son année 'year'.
        """
        logger.log(logging.RUN, "Gest_plateforme::populate_nums")

        # la plateforme n'existe pas
        if not pltf in self.pltfs.keys():
            raise Exception(f"Gest_plateforme::populate_nums : " +\
                            f"la plateforme '{pltf}' n'existe pas.")

        # si le niveau 'years' de l'arborescence de la plateforme n'existe pas,
        # le créer
        if not 'years' in self.pltfs[pltf].keys():
            self.populate_years(pltf)

        # l'année n'existe pas
        if not year in self.pltfs[pltf]['years'].keys():
            raise Exception(f"Gest_plateforme::populate_nums : " +\
                            f"pour la plateforme '{pltf}', " +\
                            f"l'année '{year}'  n'existe pas.")

        # créer le niveau 'num' pour la plateforme et l'année
        for acqid in sorted(AIDA.existing_inf_files([pltf],
                                                    liste_annees=[year],
                                                    names_only=True,
                                                    very_verbose=False)):

            # récupérer les informations de l'acqid
            infos       = self.gest_acqid.get_infos(acqid)
            if not infos:
                # DBG print(f"!!! Gest_plateforme::populate_nums : infos : {infos} PB POUR {acqid}")
                continue

            num         = infos['num']
            date        = infos['date']
            data_exists = infos['data_exists']

            # enregistrer les informations de l'acqid
            self.pltfs[pltf]['years'][year][num] = dict()
            self.pltfs[pltf]['years'][year][num]['acqid']       = acqid
            self.pltfs[pltf]['years'][year][num]['date']        = date
            self.pltfs[pltf]['years'][year][num]['data_exists'] = data_exists

        return


    def get_names(self):
        """ Retourne la liste des plateformes
            (premier niveau de l'arborescence).
        """
        return self.pltfs.keys()


    def get_years(self, pltf):
        """ Retourne la liste des années de l'arborescence de la plateforme
            'pltf'.
            (deuxième niveau de l'arborescence).
        """
        # si besoin, remplir le niveau 'years' de l'arborescence pour pltf
        self.populate_years(pltf)

        return self.pltfs[pltf]['years'].keys()


    def get_nums(self, pltf, year):
        """ Retourne le dictionnaire des acquisitions de l'arborescence de la
            plateforme 'pltf' pour l'année 'year'.
            (troisième niveau de l'arborescence).
        """
        # si besoin, remplir le niveau 'nums' de l'arborescence pour pltf
        self.populate_nums(pltf, year)

        return self.pltfs[pltf]['years'][year]


    def get_description(self, pltf, force=False):
        """ Retourne la description de la plateforme

                { 'nom balise'   : [description,
                                    [coordonnée,coordonnée]]}

            :param bool() force : False, retourne None si la position est
                                  indéfinie
                                  (voir Stack_Informations_campagne.py)
                                : True , retourne ila description même si la
                                  position est indéfinie
                                  (voir Stack_Informations_plateforme.py)
        """
        # DBG print(f"=== Gest_plateforme::get_description : pltf = {pltf}, force = {force}")

        if not pltf in self.pltfs.keys():
            raise Exception(f"Gest_plateforme::get_description : " +\
                            f"la plateforme '{pltf}' n'existe pas.")

        # si force=False, retourner None si la position est indéfinie
        if force == False:
            position = self.pltfs[pltf]['position']
            if isinstance(position, str): # ce doit être mobile
                return None

        # créer la description de la plateforme
        description = [ f"<b>nom</b>      : {pltf}<br/>" +\
                        f"<b>abrev</b>    : {self.pltfs[pltf]['abrev']}<br/>" +\
                        f"<b>position</b> : {self.pltfs[pltf]['position']}<br/>" +\
                        f"<b>altitude</b> : {self.pltfs[pltf]['altitude']}<br/>",
                        self.pltfs[pltf]['position']
                      ]

        return description


    def get_full_description(self, pltf):
        """ Retourne le contenu complet de la rubrique pltf du fichier de
            description des plateformes
        """
        # logger.log(logging.RUN, "Gest_plateforme::get_full_description")

        if not pltf in self.pltfs.keys():
            raise Exception(f"Gest_plateforme::get_description : " +\
                            f"la plateforme '{pltf}' n'existe pas.")

        return AIDA.plt_by_name[pltf].__dict__


    def get_position(self, pltf):
        """ Retourne seulement l'information de postion de la plateforme
        """
        # logger.log(logging.RUN, "Gest_plateforme::get_position")

        if not pltf in self.pltfs.keys():
            raise Exception(f"Gest_plateforme::get_position : " +\
                            f"la plateforme '{pltf}' n'existe pas.")

        return self.pltfs[pltf]['position']


if __name__ == '__main__':
    print(f"=== MAIN")

    import AIDA_logger
    logger = AIDA_logger.configure_AIDA_logging('test')

    from Gest_acqid import Gest_acqid


    gest_acqid = Gest_acqid()
    gest_pltf  = Gest_plateforme(gest_acqid=gest_acqid)

    print(f"=== Liste des plateformes (niveau 1 : get_names)")
    for pltf_name in gest_pltf.get_names():
        print(f"  - {pltf_name}")
    input('...')


    # interrogation d'une plateforme
    pltf = 'toulouse-flux'
    print(f"=== Années de la plateforme : {pltf} (niveau 2 : get_years)")
    for year in gest_pltf.get_years(pltf):
        print(f"  - {year}")
    input('...')


    # interrogation d'une plateforme/année
    year = '2023'
    print(f"=== Acquisition de : {pltf}/{year} (niveau 3 : get_nums)")
    for num, infos in gest_pltf.get_nums(pltf, year).items():
        print(f"  - {num} :")
        for key, val in infos.items():
            print(f"    - {key:12s} : {val}")

    #### position des plateformes fixes
    ###print(f"=== POSITION DES PLATEFORMES FIXES")
    ###d = gest_pltf.get_fixe_pltfs_position()
    ###for name, pos in d.items():
    ###    print(f"  - {name} : {pos}")
