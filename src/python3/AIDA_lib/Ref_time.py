#!/usr/bin/env python3

"""
Concernant les ref_time...
"""

import os
import sys
import logging


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA


def check_reftimes(acqid, reftimes, logger=None):
    """ Vérifie que tous les vecteurs temps dont les noms sont dans la
        liste reçue sont "compatibles".

        Peut lever des Exceptions.

        :param str()      acqid    : acqid
        :param list()     reftimes : nom des vecteurs temps.
        :param AID_logger logger   : un logger AIDA (contenant le niveau RUN)

        :return: True si tous les vecteurs temps sont compatibles
                 False sinon.
        :rtype:  boolean()
    """
    if logger and hasattr(logging, 'RUN'):
        logger.log(logging.RUN, "check_reftimes")

    ok = True
    first = reftimes[0]
    # inutile de tester plusieurs fois le même vecteur => utiliser un set()
    others = set(reftimes[1:])

    path_first = None
    vect_first = None
    for other in others:
        if other != first:
            # vérifier si other n'est pas un lien symbolique sur first
            if not path_first:
                path_first = os.path.realpath(
                                os.path.join(
                                    AIDA.ID_to_datapath(acqid),
                                                        first + '.vbn'))
            path_other = os.path.realpath(
                            os.path.join(
                                AIDA.ID_to_datapath(acqid),
                                                    other + '.vbn'))

            if path_first == path_other:
                if logger:
                    logger.debug(f"'{first}' et '{other}' : " +\
                                  "référencent le même vecteur")
                continue

            # vérifier que le contenu des 2 vecteurs sont compatibles
            if not vect_first:
                vect_first = AIDA.Vector(acqid, first)
            ret, msg = vect_first.compare_vect_data(other)
            if ret == True:
                if logger:
                    logger.debug(f"'{first}' et '{other}' : " +\
                                  "sont compatibles")
            else:
                raise Exception(f"'{first}' et '{other}' : " +\
                                 "vecteurs temps incompatibles")

    return ok


if __name__ == '__main__':
    acqid = 'Tf210001'
    v1 = AIDA.Vector(acqid, 'flx_phi0_moy_c2_%60_Met_%1800')
    v2 = AIDA.Vector(acqid, 'prp_rr_min_c2_%60_Som_%1800')

    ref_time_1 = v1.attributes['ref_time']
    ref_time_2 = v2.attributes['ref_time']
    list_ref_times = [ ref_time_1, ref_time_2 ]

    print(f"\nSANS LOGGER")
    ok = check_reftimes(acqid, list_ref_times)
    print(f"  -->  pour {ref_time_1} et {ref_time_2} : ret = {ok}")

    print(f"\nAVEC AIDA BASIQUE")
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    ok = check_reftimes(acqid, list_ref_times, logger=logger)
    print(f"  -->  pour {ref_time_1} et {ref_time_2} : ret = {ok}")


    # avec un logger AIDA
    import AIDA_logger
    # le fichier de log sera /tmp/<USER>.test.log
    logger = AIDA_logger.configure_AIDA_logging('test')

    print(f"\nAVEC AIDA LOGGER")
    ok = check_reftimes(acqid, list_ref_times, logger=logger)
    print(f"  --> pour {ref_time_1} et {ref_time_2} : ret = {ok}")
    
    # avec un vecteur incompatible
    v3 = AIDA.Vector(acqid, 'flx_phi0_moy_c2_%60')
    ref_time_3 = v3.attributes['ref_time']
    list_ref_times.append(ref_time_3)

    try:
        ok = check_reftimes(acqid, list_ref_times, logger=logger)
    except Exception as e:
        print(f"  --> EXCEPTION : {e}")
    print(f"\n--> voir : {logger.handlers[1].baseFilename}")

