#!/usr/bin/env python3

"""
AIDA
    Gestion des vecteurs.

    Les vecteurs gérés par cette classe ne seront pas écrits sur disque. De ce
    fait, cette classe peut faire les manipulations qu'elle veut et en
    particulier, enrichir le header du champ NbVal (pour rester cohérent avec
    FVB/ADC) qui contient la longueur des données. Ce champ est ensuite utilisé
    par les methodes de mise à jour des Widgets de l'opérateur (en particulier
    pour initialiser le champ 'size out' de l'opérateur MoyEch_tps_impos)
"""

import sys
import os
import logging
import datetime
import numpy as np
import subprocess
import glob

AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))

import AIDA

logger = logging.getLogger('aito')


class Vector():

    def __init__(self, acqid, name, rft_time=False, get_histogram=True):
        """ option rft_time
            - False : le vecteur est un vecteur de données
            - True  : le vecteur est un vecteur de datation (rft_time)
                      (cas des opérateurs qui font des transformations
                      temporelles)
            option get_histogram
            - True  : les données pour l'histogramme sont calculées
            - False : les données pour l'histogramme ne sont calculées
                      (utilisé par les opérateurs qui attendent un
                      vecteur de type 'extra_rft_time')
        """

        logger.log(logging.RUN, f"Vector::__init__ : " +\
                                f"acqid = {acqid}, name = {name}")

        self.acqid     = acqid
        self.name      = name
        self.acqid_dir = AIDA.ID_to_datapath(acqid)
        self.ancestors = None
        self.versions  = None

        if not rft_time:
            self.data, self.time, self.header = self.get_data(acqid, name)
        else:
            self.data, self.time, self.header = self.get_rft_time_data(acqid, name)

        # bornage du nombre de colonnes pour l'histogramme
        self.NB_COLS_MIN = 3
        self.NB_COLS_MAX = 100

        # format 'string32'
        if 'format' in self.header.keys() and self.header['format'] == 'string32':
            #raise Exception("Ne sait pas encore traiter le format 'string32'")
            self.histo_X = np.full(len(self.data), 0)
            self.histo_Y = np.full(len(self.data), 0)

            return

        # valeurs pour l'histogramme
        if get_histogram:
            self.histo_X, self.histo_Y = self.get_histogram_values()

        return


    def get_data(self, acqid, name):
        """ Retourne les données du vecteur, le temps assoicé (sous le format
            datetime.timestamp()), et le header du vecteur.

            Pour les vecteurs temps _supplémentaires_ utiliser la méthode :
                get_rft_time_data
        """
        # DBG logger.log(logging.RUN, "Vector::get_data")
        data, time, header = AIDA.read_data(acqid, name, header_utf_8=True)

        # enrichissement du header
        header['NbVal'] = len(data)

        return data, [ x.timestamp() for x in time ], header


    def get_histogram_values(self):
        """ Retourne les valeurs (X, Y) d'histogramme des data.
        """
        logger.log(logging.RUN, "Vector::get_histogram_values")

        # pas d'histogramme si dim_array > 1
        if int(self.header['dim_array']) > 1:
            return None, None


        try :
            # nombre de colonnes de l'histogramme
            nb_cols = max(self.NB_COLS_MIN, int(len(self.data)/10))
            nb_cols = min(self.NB_COLS_MAX, nb_cols)

            Y, X = np.histogram(self.data.compressed(), bins=nb_cols)

        except Exception as e:
            print(f"!!! PROBLEME Vector.py::get_histogram_values() : EXCEPTION : {e}")
            return Y, X

        nb_data   = len(self.data)
        Y_percent = list()
        for i in range(len(Y)):
            Y_percent += [ float( Y[i] / nb_data*100) ]

        return X, Y_percent


    def get_rft_time_data(self, acqid, name):
        """ Comme `get_data` mais pour les vecteur rft_time spécifiquement.

            La fonction AIDA_lib::read_data ne retourne pas tout à fait ce qui
            est nécessaire pour AITO => réimplémentation locale de la fonction
            AIDA_lib::read_data.
        """
        logger.log(logging.RUN, f"Vector::get_rft_time_data : " +\
                                f"acqid = {acqid}, name = {name}")

        try:
            vect_time = AIDA.VectorMask(acqid, name, overwrite=True)
            date_acq  = AIDA.Inf(acqid).get_date_acq()
        except Exception as e:
            raise Exception(f"{acqid}::{name} : {e}")

        data_time = []
        datetime_acq = datetime.datetime(date_acq.year,
                                         date_acq.month,
                                         date_acq.day)
        # time au format datetime
        data_time_acq = np.full(len(vect_time.data), datetime_acq, dtype="datetime64[us]")
        time_delta    = (vect_time.data*1000000).astype("timedelta64[us]")
        data_time     = (data_time_acq + time_delta).astype(datetime.datetime)


        # enrichissement du header
        vect_time.attributes['NbVal'] = len(vect_time.data)

        return None, [ x.timestamp() for x in data_time ], vect_time.attributes


    def get_ancestors(self):
        """ Retourne la liste des noms des vecteurs ascendants du vecteur.
        """
        # logger.log(logging.RUN, "Vector::get_ancestors")

        base_output = self.name + '.' + os.getenv('USER')
        result = subprocess.run(
                    [ 'gengraphvect.py', '-a', self.acqid,
                      '-n', '9', '-s', 'asc', self.name, '-f', base_output ],
                    capture_output=True,
                    text=True).stdout
        result = result.strip()

        # la première ligne contient le nom du vecteur lui-même (qui n'est pas
        # son propre ascendant)
        # => [1:]
        self.ancestors = result.split('\n')[1:]

        return self.ancestors



    def get_versions(self):
        """ Retourne la listes des versions du vecteur (les .vx et les .nx).

            note : le path d'une version est de la forme XXX.vN.vbn.
        """
        # logger.log(logging.RUN, "Vector::get_versions")

        name = self.name
        # si besoin, supprimer la version du vecteur courant
        if (name.split(".")[-1].startswith("v") or len(name.split(".")) > 1):
            final_name = name.split(".")[0]
            for part in name.split(".")[1:-1]:
                final_name += part
            name = final_name

        name += '.[v|n]*.vbn'
        l = [ os.path.splitext(f)[0]
                for f in glob.glob(name, root_dir=self.acqid_dir) ]
        self.versions = l if len(l) >0 else ["pas d'autre version"]

        return self.versions


if __name__ == '__main__':

    import AIDA_logger
    logger = AIDA_logger.configure_AIDA_logging('test')

    print("\ntest sur : 'Tf230001', 'chm_conco2_d_li7500_Eti_20'")
    vector = Vector(acqid='Tf230001', name='chm_conco2_d_li7500_Eti_20')
    print(f" - vector.header['NbVal'] = {vector.header['NbVal']}")
    if vector.time is not None:
        print(f" - vector.time[0:5] = {vector.time[0:5]}")
    else:
        print(f" - vector.time is None")
    input('...')


    print("\ntest sur : 'Tf230001', 'tpr_sol_profil100_%900'")
    vector = Vector(acqid='Tf230001', name='tpr_sol_profil100_%900')
    print(f" - vector.header['NbVal'] = {vector.header['NbVal']}")
    if vector.time is not None:
        print(f" - vector.time[0:5] = {vector.time[0:5]}")
    else:
        print(f" - vector.time is None")
    input('...')


    print("\ntest sur : 'Tf230001', 'time_%3600'")
    vector = Vector(acqid='Tf230001', name='time_%3600', rft_time=True)
    print(f" - vector.header['NbVal'] = {vector.header['NbVal']}")
    if vector.time is not None:
        print(f" - vector.time[0:5] = {vector.time[0:5]}")
    else:
        print(f" - vector.time is None")
    input('...')


    print("\ntest sur : 'Tf230001', 'rft_time_dso_precip_%60'")
    vector = Vector(acqid='Tf230001', name='time_%3600', rft_time=True)
    print(f" - vector.header['NbVal'] = {vector.header['NbVal']}")
    if vector.time is not None:
        print(f" - vector.time[0:5] = {vector.time[0:5]}")
    else:
        print(f" - vector.time is None")
    input('...')


    print("\ntest sur : 'Tf230001', 'rft_time_REG_4'")
    vector = Vector(acqid='Tf230001', name='time_%3600', rft_time=True)
    print(f" - vector.header['NbVal'] = {vector.header['NbVal']}")
    if vector.time is not None:
        print(f" - vector.time[0:5] = {vector.time[0:5]}")
    else:
        print(f" - vector.time is None")
    input('...')
