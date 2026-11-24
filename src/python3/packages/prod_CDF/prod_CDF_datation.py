#!/usr/bin/env python3

"""
Production de fichier NetCDF à partir de fichiers-vecteurs
==========================================================

  Gestion des datations à inscrire dans le fichier NetCDF.
"""

import sys
import os
import numpy as np
import datetime as dt

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
import logging

logger = logging.getLogger('prod_CDF')


class Datation:
    """ Gestion des datations à inscrire dans le fichier NetCDF.
    """

    def __init__(self, convention_datation, reftime):
        """
            :param str() convention_datation: convention de datation.
                                              ['debut', 'milieu', 'fin']
            :param str() reftime            : nom du vecteur de datation.
        """
        logger.log(logging.RUN, "Datation::__init__")
        self.convention_datation = convention_datation
        self.reftime             = reftime
        self.dt_time             = list()
        self.time_bounds         = np.empty((0,2))


    def show_me(self):
        """ Debug
        """
        print( "--- datation")
        print(f" - convention_datation = {self.convention_datationval}")
        print(f" - reftime             = {self.reftime}")


    def get_time_conv(self, time_bounds):
        """ Retourne un numpy.ndarray à partir des time_bounds et de la
            convention de datation.

            :param numpy.ndarray() time_bounds: bornes de temps.
        """
        logger.log(logging.RUN, "Datation::get_time_conv")

        d = {'debut' : [1. , 0. ],
             'milieu': [0.5, 0.5],
             'fin'   : [0. , 1. ]}

        conv = self.convention_datation

        return d[conv][0] * time_bounds[:,0]  +  d[conv][1] * time_bounds[:,1]


    def time_append(self, s_acqid, acq_day):
        """ Ajoute à la liste 'self.dt_time' les datations du l'acqid 's_acqid'.
            Retoune les time_bnds de l'acqid.

            :param str()      s_acqid: nom de l'acqid à traiter
            :param datetime() acq_day: jour de l'acqid.


            :return: time_bounds de l'acqid
            :rtype : np.array()
        """
        logger.log(logging.RUN, "Datation::time_append")

        acq_time_bounds = AIDA.time_to_data_bnds(s_acqid, self.reftime, show_msg=False)
        if acq_time_bounds is None:
            logger.error(f"problème sur : " +\
                         f"AIDA.time_to_data_bnds({s_acqid}, {self.reftime})")
            sys.exit(1)

        time_conv = self.get_time_conv(acq_time_bounds)

        self.dt_time.extend([ acq_day + dt.timedelta(seconds=t) for t in time_conv ])

        return acq_time_bounds


    def bnds_append(self, time_bnds, nb_days):
        """ Ajoute au np.array 'self.time_bounds' les time_bnds reçus.

            :param np.array() time_bnds: bornes de temps
                                         (voir AIDA.time_to_data_bnds)
            :param int()      nb_days  : nombre de jours depuis le début du
                                         traitement (0 si pour les traitements
                                         par journée)

            NOTE :
            les bornes ne sont pas datées (elles sont en nombre de secondes
            depuis 00h)
            => en mode periode, il faut ajouter 86400*nbjour aux bornes
               temporelles correspondant à chaque jour
        """
        logger.log(logging.RUN, "Datation::bnds_append")

        self.time_bounds = np.append(self.time_bounds,
                                     time_bnds + (nb_days*86400), axis=0)

        return
