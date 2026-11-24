#!/usr/bin/env python3

"""
AITO
    Traitement des acqids

    Organise les informations des acqids
    'acqid': {'num'        : numero_acquisition,
              'date'       : str,
              'year'       : int,
              'month'      : int,
              'day'        : int,
              'data_exists': boolean,
              'data_pah'   : path ,
              'vectors'    : [ {'name': nom, 'size': taille, 'date': date} ],
             }

    Notes :
        - la date et chaque partie de la date sont mémorisées pour "alléger"
          le code des méthodes qui récupèrent les informations de cette
          classe...
        - 'data_exists' et 'data_pah' sont légèrement redondant, mais
          dans certains cas l'utilisation de l'un ou de l'autre est
          plus explicite.
"""

import sys
import os
import logging
import glob
import time


PYTHON_X_Y    = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
import AcqId

logger = logging.getLogger('aito')


class Gest_acqid():
    """ Gestion des acqids.
    """

    def __init__(self, *args, **kwargs):
        logger.log(logging.RUN, "Gest_acqid::__init__")

        self.acqids      = dict()
        self.inf_headers = dict()

        return


    def populate(self, acqid):
        """ Enregistre les informations de l'acqid
        """
        # logger.log(logging.RUN, f"Gest_acqid::populate : acqid = {acqid}")

        try:
            long_name, year, num = AIDA.ID_to_full(acqid)
            data_path            = AIDA.ID_to_datapath(acqid)
            data_exists          = os.path.isdir(data_path)
        except Exception as e:
            raise Exception(f"Gest_acqid::populate : " +\
                            f"erreur AIDA pour l'acqid '{acqid}' " +\
                            f"{e}")


        # récupérer le datetime de l'acqid (class AIDA.AcqId)
        try:
            dt_date = AcqId.AcqId(acqid).acqid_to_date()
            date    = dt_date.strftime('%Y-%m-%d')
            month   = dt_date.month
            day     = dt_date.day
        except Exception as e:
            logger.debug(f"acqid invalide : '{acqid}', dt_date = {dt_date}")
            date    = ''
            month   = ''
            day     = ''


        self.acqids[acqid] = dict()
        self.acqids[acqid]['num']         = num
        self.acqids[acqid]['date']        = date
        self.acqids[acqid]['year']        = year
        self.acqids[acqid]['month']       = month
        self.acqids[acqid]['day']         = day
        self.acqids[acqid]['data_exists'] = data_exists
        self.acqids[acqid]['data_path']   = data_path if data_exists else None

        return


    def get_size_date(self, file_path):
        """ Retourne la taille 'human readable' et la date de dernière
            modification de file_path.
        """
        # la taille
        size  = os.path.getsize(file_path)
        power = 2**10
        n = 0
        power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB', 5: 'PB'}
        while size > power:
            size /= power
            n = n + 1

        # la date
        mtime = os.path.getmtime(file_path)
        mdate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))

        return f"{round(size)} {power_labels[n]}", mdate


    def populate_vectors(self, acqid):
        """ Enregistre les informations des vecteurs de l'acqid
        """
        logger.log(logging.RUN, f"Gest_acqid::populate_vectors : acqid = {acqid}")

        # l'acqid n'est pas encore enregistré
        if not acqid in self.acqids.keys():
            self.populate(acqid)

        # la liste a déjà été faite
        if 'vectors' in self.acqids[acqid].keys():
            return

        self.acqids[acqid]['vectors'] = list()

        # les données n'existe pas
        if not self.acqids[acqid]['data_exists']:
            return

        # récupération des noms des vecteurs
        # (utilisation d'une liste temporaire qui sera triée à la fin)
        l = list()
        path = self.acqids[acqid]['data_path']
        for base_name in glob.glob('*.vbn', root_dir=path):
            name = os.path.join(path, base_name)
            size, mdate = self.get_size_date(name)

            d = {'name': name, 'size': size, 'date': mdate}
            l.append(d)

        # trier la liste sur les name des dictionnaires
        self.acqids[acqid]['vectors'] = sorted(l, key=lambda d: d['name'].lower())

        return


    def get_path_infos(self, acqid):
        """ Retourne les informations plateforme, année, num, data_exists
            pour l'acqid reçu.

            (cette me"thode est prévue pour la recherche directe par acqid.)
        """
        # logger.log(logging.RUN, f"Gest_acqid::get_path_infos : acqid = {acqid}")

        ret_dict = dict()
        try:
            long_name, year, num = AIDA.ID_to_full(acqid)
            data_path            = AIDA.ID_to_datapath(acqid)
            data_exists          = os.path.isdir(data_path)
            ret_dict['plateforme']  = long_name
            ret_dict['year']        = year
            ret_dict['num']         = num
            ret_dict['data_exists'] = data_exists
        except Exception as e:
           ret_dict = None

        return ret_dict


    def get_infos(self, acqid):
        """ Retourne les informations concernant l'acqid reçu.
        """
        # logger.log(logging.RUN, f"Gest_acqid::get_infos : acqid = {acqid}")

        if not acqid in self.acqids.keys():
            try:
                self.populate(acqid)
            except Exception as e:
                return None

        return self.acqids[acqid]


    def get_vectors(self, acqid):
        """ Retourne la liste des informations de tous les vecteurs concernant
            l'acqid reçu.
        """
        # logger.log(logging.RUN, f"Gest_acqid::get_vectors : acqid = {acqid}")

        self.populate_vectors(acqid)

        return self.acqids[acqid]['vectors']


    def get_vectors_mask(self, acqid, mask):
        """ Retourne la liste des informations des vecteurs de l'acqid dont
            le nom contient le mask reçu.
        """
        # logger.log(logging.RUN, f"Gest_acqid::get_vectors_mask : " +\
        #                         f"acqid = {acqid}, mask = {mask}")

        self.populate_vectors(acqid)

        ret_list = list()
        for vector in self.acqids[acqid]['vectors']:
            if mask in vector['name']:
                ret_list.append(vector)

        return ret_list


    def get_header_inf(self, acqid):
        """ Retourne la partie [IDENTIFICATION] du .inf de l'acqid reçu.
        """
        # logger.log(logging.RUN, f"Gest_acqid::get_header_inf : acqid = {acqid}")

        if not acqid in self.inf_headers.keys():
            infos = AIDA.Inf(acqid)._sections['IDENTIFICATION']
            # supprimer la clé '__name__'
            del infos['__name__']
            self.inf_headers[acqid] = infos

        return self.inf_headers[acqid]


if __name__ == '__main__':
    print(f"=== MAIN")

    import AIDA_logger
    logger = AIDA_logger.configure_AIDA_logging('test')


    gest_acqid = Gest_acqid()

    acqid = 'Tf230250'
    print(f"\n=== Information pour l'acqid {acqid} :")
    infos = gest_acqid.get_infos(acqid)
    for key, val in infos.items():
        print(f"  - {key:12s} : {val}")
    input('...')

    acqid = 'Tf230001'
    print(f"\n=== Information pour l'acqid {acqid} :")
    infos = gest_acqid.get_infos(acqid)
    for key, val in infos.items():
        print(f"  - {key:12s} : {val}")
    input('...')

    print(f"\n=== Vecteurs pour l'acqid {acqid} :")
    vectors = gest_acqid.get_vectors(acqid)
    for vector in vectors:
        print(f"  - {vector['name']:40s} : " +\
              f"size = {vector['size']}, date = {vector['date']}")
    input('...')

    acqid = 'Tf330001'
    print(f"\n=== Information pour l'acqid {acqid} :")
    infos = gest_acqid.get_infos(acqid)
    for key, val in infos.items():
        print(f"  - {key:12s} : {val}")
    input('...')

    acqid = 'Tf2300001'
    print(f"\n=== Information pour l'acqid {acqid} :")
    try:
        infos = gest_acqid.get_infos(acqid)
    except Exception as e:
        print(f"ERREUR : {e}")
    input('...')

    print(f"\n=== Vecteurs pour l'acqid {acqid} :")
    try:
        vectors = gest_acqid.get_vectors(acqid)
    except Exception as e:
        print(f"ERREUR : {e}")
    else:
        for vector in vectors:
            print(f"  - {vector['name']:40s} : " +\
                  f"size = {vector['size']}, date = {vector['date']}")


    mask = 'aip'
    acqid = 'as230031'
    print(f"\n=== Vecteurs qui matchent '{mask}' pour l'acqid {acqid} :")
    vectors = gest_acqid.get_vectors_mask(acqid, mask)
    for vector in vectors:
        print(f"  - {vector['name']:40s} : " +\
              f"size = {vector['size']}, date = {vector['date']}")
    input('...')

    acqid = 'fs170006'
    print(f"\n=== Header du .inf de : {acqid}")
    infos = gest_acqid.get_header_inf(acqid)
    for key, val in infos.items():
        print(f"  - {key:22s} : {val}")
    input('...')

