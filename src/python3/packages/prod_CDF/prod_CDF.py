#!/usr/bin/env python3

"""
Production de fichier NetCDF à partir de fichiers-vecteurs
==========================================================

  usage :
    %s [-h] [-o out_dir] [-S select] -c config -v version  prod_deb prod_fin

  avec :
    [-h]         : affichage de l'aide.
    [-o out_dir] : nom du répertoire de sortie.
    [-S select]  : nom du fichier de sélection (vecteurs des paramètres).

    -c config    : nom du fichier de configuration.
    -v version   : numéro de version des fichiers à produire.
                   (défaut : 1)
    prod_deb     : date de début (JJMMAAAA) ou acqid de début.
    prod_fin     : date de fin   (JJMMAAAA) ou acqid de fin.

  NOTE : la  version historique 'prod_CDF_histo.py' est lancée si
         le fichier de configuration ne contient pas de section '[DIRECTIVES]'
"""

import sys
import os
import argparse
import logging
import configparser
import re
import datetime as dt
import subprocess as sub
import numpy as np
import netCDF4 as nc

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y, 'prod_CDF'))

import AIDA
import AIDA_logger
import Units
import Ref_time
import prod_CDF_defaults
import prod_CDF_config
import prod_CDF_selector
import prod_CDF_params
import prod_CDF_datation
from   AcqId import *

logger = AIDA_logger.configure_AIDA_logging('prod_CDF')

__version__ = '2.0.1'

version_histo = 'prod_CDF_histo.py'

# parfois il faut préciser la longueur des chaines
string_length = 100


def stop_error(msg, more=None):
    """ Logge le message 'msg' et l'éventuel complément 'more' puis arrête le
    programme.
    """
    if more:
        logger.error(f"{msg} :\n    {more}")
    else:
        logger.error(msg)
    sys.exit(1)


def run_histo(runstring):
    """ éxécution de la version historique.

        :param str() runstring: arguments de lancement.
    """
    logger.info(f"Lancement de la version historique : {version_histo} {runstring}")

    exit_code = os.system(f"{version_histo} {runstring}")
    sys.exit(exit_code)


def check_ancillaries(params):
    """ Vérifie que les paramètres qui apparaissent en 'ancillary_variables'
        sont bien définis par ailleurs.

        :param dict() params: dictionnaires des objects Param
    """
    logger.log(logging.RUN, f"check_ancillaries")

    def replace_plus(in_str, with_str):
        """ Remplace le caractère '+' de 'in_str' par 'with_str' et
            retourne le résultat.
        """
        return in_str.replace('+', f" {with_str} ").strip(' ')

    for param_name, param in params.items():
        ancillaries = param.get_ancillary()
        if not ancillaries:
            continue

        for ancillary_name in re.split(r'[ \t]+', ancillaries):
            # cas où il y a plusieurs espaces entre les noms
            if len(ancillary_name) == 0:
                continue

            if not ancillary_name in params_infos.keys():
                stop_error(f"{param_name:15} : pas de section '{ancillary_name}' " +\
                           f"('ancillary_variables = {ancillaries}')")
            else:
                # remplacement syntaxique des '+' pour les champs des 'ancillary_variables'
                ancil = params_infos[ancillary_name] # objet Param

                # long_name
                src_long_name             = param.config['long_name']
                ancil_long_name           = ancil.config['long_name']
                ancil.config['long_name'] = replace_plus(ancil_long_name, src_long_name)

                # standard_name
                src_standard_name             = param.config['standard_name']
                ancil_standard_name           = ancil.config['standard_name']
                if src_standard_name == None:
                    repl_by = ' '
                else:
                    repl_by = src_standard_name

                if ancil_standard_name:
                    word = replace_plus(ancil_standard_name, repl_by)
                    ancil.config['standard_name'] = word

    return


def check_coordinates(config, params):
    """ Vérifie que les paramètres qui apparaissent en 'coordinates'
        sont bien définis par ailleurs.

        :param Config() config: objet Config
        :param dict()   params: dictionnaires des objects Param
    """
    logger.log(logging.RUN, f"check_coordinates")

    if not 'coordinates' in config.general.keys():
        return

    coordinates = config.general['coordinates']
    for i, param_name in enumerate(re.split(r'[ \t]+', coordinates)):
        if i == 0:
            if param_name != 'time':
                stop_error(f"'coordinates = {coordinates}' : " +\
                           f"le premier paramètre doit être 'time'")
            else:
                continue

        if not param_name in params_infos.keys():
            stop_error(f"'coordinates = {coordinates}' : " +\
                       f"le paramètre '{param_name}' n'existe pas")

    return


def get_deb_fin():
    """ Retourne les dates et les acqids de début et de fin pour le traitement,
        en fonction des arguments de la ligne de commande et de l'abréviation
        du nom de la plateforme trouvée dans le fichier de configuration.
        Les varaibles 'prod_deb', 'prod_fin', 'cfg_abrev_plt' ont été
        positionnées sous "if __name__ == '__main__':".

        Arrête le programme en cas de problème.

        - 'prod_deb' reçu dans la ligne de commande.
        - 'prod_fin' reçu dans la ligne de commande.
        - 'cfg_abrev_plt' abréviation de la plateforme à traitée

        :return: dt_deb    , dt_fin    , acqid_deb, acqid_fin
        :rtype : datetime(), datetime(), AcqId()  , AcqId()
    """
    # pour rappel : les variables crées sous : "if __name__ == '__main__':"
    # sont globales
    logger.log(logging.RUN, f"get_deb_fin({args}, {cfg_abrev_plt})")

    # arguments de début et fin de traitement
    try:
        # par date
        dt_deb = dt.datetime.strptime(prod_deb, "%d%m%Y")
        dt_fin = dt.datetime.strptime(prod_fin, "%d%m%Y")

        acqid_deb = AcqId(plateforme=cfg_abrev_plt, date=dt_deb)
        acqid_fin = AcqId(plateforme=cfg_abrev_plt, date=dt_fin)
    except ValueError as e:
        # par acqid
        try:
            AIDA.check_acq_id(prod_deb)
            AIDA.check_acq_id(prod_fin)
        except AIDA.AidaError as e:
            stop_error(f"acqid incorrect : "               +
                       f"début = '{prod_deb}' et/ou " +
                       f"fin = '{prod_fin}'")

        try:
            acqid_deb = AcqId(prod_deb)
            acqid_fin = AcqId(prod_fin)

            dt_deb = acqid_deb.acqid_to_date()
            dt_fin = acqid_fin.acqid_to_date()
        except (ValueError, KeyError) as e:
            stop_error(f"arguments incohérents : "         +
                       f"début = '{prod_deb}' et/ou " +
                       f"fin = '{prod_fin}'")

    return dt_deb, dt_fin, acqid_deb, acqid_fin


def check_acqids_consistency(acqid_deb, acqid_fin, cfg_plateforme):
    """ Vérifie la cohérence de 'acqid_deb' et 'acqid_fin' puis la cohérence
        entre la plateforme du fichier de configuration 'cfg_plateforme' et
        celle des acqids.
        Arrête le programme en cas de problème.
    """
    logger.log(logging.RUN, f"check_acqids_consistency({acqid_deb}, " +\
                            f"{acqid_fin}, {cfg_plateforme})")

    # vérification des acqids
    if (str(acqid_deb)[0:2] != str(acqid_fin)[0:2]):
        stop_error(f"acqid_deb ('{acqid_deb}') et " +
                   f"acqid_fin ('{acqid_fin}') "    +
                    "ne sont pas de la même plateforme")

    if (acqid_deb > acqid_fin):
        stop_error(f"acqid_deb ('{acqid_deb}') doit précéder " +
                   f"acqid_fin ('{acqid_fin}')")

    plateforme, annee, num = AIDA.ID_to_full(str(acqid_deb))

    if plateforme != cfg_plateforme:
        stop_error("incohérence entre la plateforme des acqid et " +
                   "la plateforme du fichier de configuration : "  +
                  f"{cfg_plateforme}")


def get_treatable_acqids(mode, acqid_deb, acqid_fin, reftime):
    """ Pour tous les acqids entre 'acqid_deb' et 'acqid_fin', vérifie :
        - l'existence du .INF
        - l'existance des données
        - l'existence du vecteur 'reftime'
        Arrête le programme en cas de problème.

        :param str()   mode        : 'periode', 'jour', 'mobile'.
        :param AcqId() acqid_deb   : premier acqid
        :param AcqId() acqid_fin   : dernier acqid
        :param str()   reftime     : basename du fichier refime (sans extension)
    """
    logger.log(logging.RUN, f"get_treatable_acqids({acqid_deb}, {acqid_fin}, " +\
                            f"{reftime})")

    acqids = list()
    acqid = acqid_deb
    while acqid <= acqid_fin:
        msg = list()
        # ajout systématiquement de l'acqid à la liste (il sera supprimé si
        # il n'est pas traitable).
        acqids.append(acqid)

        s_acqid = str(acqid)

        if mode == 'mobile':
            inf_file = AIDA.ID_to_inf_path(s_acqid)
            if not os.path.isfile(inf_file):
                logger.warning(f"{s_acqid} : pas de fichier .INF")

        data_dir = AIDA.ID_to_datapath(s_acqid)
        if not os.path.isdir(data_dir):
            msg.append("pas de donnée")

        if not os.path.isfile(os.path.join(data_dir, reftime + '.vbn')):
            msg.append(f"pas de vecteur '{reftime}'")

        # supprimer l'acqid de la liste s'il n'est pas traitable
        if msg:
            acqids.pop()
            logger.warning(f"'{acqid}' ignoré : {', '.join(msg)}")

        try:
            acqid = acqid + 1
        except Exception as e:
            stop_error("problème sur les acqids", more=e)

    logger.debug(f"get_treatable_acqids : nb acqids = {len(acqids)}")

    return acqids


def get_times(acqid, reftime):
    """ Retourne les datations de début et fin et le vecteur temps pour
        l'acqid fourni.

        début = JOUR de l'acquisition (seulement) + première datation
        fin   = JOUR de l'acquisition (seulement) + dernière datation

        :param AcqId() acqid   : acquisition à traiter
        :param str()   reftime : nom du vecteur de datation à traiter (c'est
                                 une globale...)

        :return: date de début, date de fin, vecteur de datation, acq_day
        :rtype : datetime()   , datetime() , Vector()           , str()
    """
    dt_acq    = acqid.acqid_to_date()
    dt_day    = dt.datetime(dt_acq.year, dt_acq.month, dt_acq.day, 0,0,0)

    s_acqid   = str(acqid)
    vect_time = AIDA.Vector(s_acqid, reftime)

    dt_start = dt_day + dt.timedelta(seconds=vect_time.data[0])
    dt_end   = dt_day + dt.timedelta(seconds=vect_time.data[-1])

    return dt_start, dt_end, vect_time


def get_vector_from_other_acqid(origin, acqids):
    """ Recherche le vecteur dans une autre acquisition de la plage.

        :param str()  origin : nom du vecteur.
        :param list() acqids : liste des acquisitions à traiter.
    """
    logger.log(logging.RUN, f"get_vector_from_other_acqid : {origin}")

    vect = None
    for acqid in acqids:
        try:
            vect = AIDA.Vector(acqid._valeur, origin)
        except Exception as e:
            continue

    logger.debug(f"get_vector_from_other_acqid : return : {vect}")

    return vect


def replace_missing(param, acqids, data_len):
    """ Initialise les données à np.nan.
        Si le paramètre n'a pas encore été lu (param.attrs['dim_array'] n'existe pas)
            - recherche de ce paramètre parmi les acquisitions à traiter
              si le paramètre est trouvé :
                - initialisation de param.attrs
                - initialisation de param.data
              sinon
                - initialisation de param.attrs par défaut (dim_array=1, type=float...)
                - initialisation de param.data
        Sinon (param.attrs['dim_array'] existe)
            - initialisation de param.data

        :param dict() param   : objet Param pour le paramètre.
        :param list() acqids  : liste des acquisitions à traiter.
        :param int()  data_len: longueur du vecteur temps.
    """
    logger.log(logging.RUN, f"replace_missing(param, acqids, {data_len})")

    logger.info(f"{param.name:15s} : remplacement de valeurs manquantes")

    origin = param.config['origin']

    # si besoin, tenter d'initialiser param.attrs
    if not 'dim_array' in param.attrs.keys():
        vect = get_vector_from_other_acqid(origin, acqids)
        if vect is None:
            param.attrs['dim_array'] = 1
            param.attrs['format']    = 'Ieeefloat_32'
            param.attrs['misval']    = np.nan
            logger.error(f"{param.name:15s} : vecteur absent sur toute " +\
                         f"la plage {origin}")

        else:
            # initialisation de param.attrs
            param.set_attrs_from_header(vect.attributes)

    # ici 'dim_array' est postionné soit par le header d'un vecteur soit par
    # défaut.
    # initialisation de param.data (peut-être un peu sommaire si le format
    # n'est pas float ou double...)
    ##dtype = AIDA.aida_format(param.attrs['format'])
    dtype  = AIDA.np_string(param.attrs['format'])
    dim    = int(param.attrs['dim_array'])
    misval = param.attrs['misval']
    if dim > 1:
        nan_data = np.full((data_len, dim),
                           misval,
                           dtype=dtype)
    else:
        nan_data = np.full((data_len, ),
                           misval,
                           dtype=dtype)

    logger.debug(f"replace_missing : {origin} : " +\
                 f"shape = {nan_data.shape}")
    param.append_data(nan_data)

    return


def get_source(origin, str_acqid):
    """ Récupère la liste des capteurs utilisés pour créer le vecteur
        considéré.
        Pour cela :
        - on interroge gengraphvect.py pour récupérer la liste des vecteurs
          cal qui ont servi à fabriquer le vecteur (ancêtres).
        - puis on recherche, dans le header des ancêtres, la liste des
          variables qui pourraient indiquer la source.

        :return: chaine des capteurs séparé par '; '
        :rtype : str()
    """
    logger.log(logging.RUN, f"get_source({origin}, {str_acqid})")

    source_instru = set()

    # interrogation de gengraphvect.py
    base_output = 'GenGraphVect.' + os.getenv('USER') 
    cmd  = f"gengraphvect.py -a {str_acqid} -n 4 -o png -s asc -f {base_output} {origin}"
    prog = os.path.join(AH, 'bin', cmd)
    s    = sub.run(prog, shell=True, capture_output=True, encoding='iso-8859-15')
    if s.stderr.startswith('ERREUR'):
        logger.debug(f"gengraphvect.py : erreur pour {str_acqid}::{origin}")
        return None

    # analyse du retour de gengraphvect.py
    ancetres = s.stdout.lstrip().split('\n')
    for ancetre in ancetres:
        source = None
        ancetre = ancetre.strip()
        fields = ancetre.split(':')
        # fields[0] est le 'type' de la ligne. Seuls les champs de 1 à 3 (max)
        # seront à retourner
        if len(fields) > 4:
            del fields[4:]

        # on prend les sensor et à défaut, les transducer ou les instrument
        if fields[0] == 'sensor':
            source = ' : '.join(fields[1:])
        elif source is None:
            if fields[0] in ['transducer', 'instrument']:
                source = ' : '.join(fields[1:])
        if source:
            source_instru.add(source)

    return '; '.join(sorted(list(source_instru)))


def reset_data(params):
    """ Vide les données des paramètres contenus dans 'params'.

        :param dict() params  : dictionnaire contenant toutes les informations
                                nécessaire pour la génération du fichier NetCDF.
    """
    logger.log(logging.RUN, f"reset_data")

    for param_name, param in params.items():
        param.data = None

    return


def get_trajectory_geospatial(trajectory_params, params):
    """ Retourne un dictionnaire contenant les valeurs :
        - 'geospatial_lat_min'
        - 'geospatial_lat_max'
        - 'geospatial_lat_units'
        - 'geospatial_lon_min'
        - 'geospatial_lon_max'
        - 'geospatial_lon_units'
        - 'geospatial_vertical_min'
        - 'geospatial_vertical_max'
        - 'geospatial_vertical_units'
        - 'geospatial_vertical_positive'
        pour les paramètres de trajectory_params.
    """
    alt_done = False
    d = dict()

    for param_name in trajectory_params:
        param = params[param_name]
        if param.config['standard_name'] == 'latitude':
            obs_min, obs_max = param.get_min_max()
            d['geospatial_lat_min']   = float(obs_min)
            d['geospatial_lat_max']   = float(obs_max)
            d['geospatial_lat_units'] = param.attrs['unit']
        elif param.config['standard_name'] == 'longitude':
            obs_min, obs_max = param.get_min_max()
            d['geospatial_lon_min']   = float(obs_min)
            d['geospatial_lon_max']   = float(obs_max)
            d['geospatial_lon_units'] = param.attrs['unit']
        elif param.config['standard_name'] == 'altitude':
            obs_min, obs_max = param.get_min_max()
            d['geospatial_vertical_min']      = float(obs_min)
            d['geospatial_vertical_max']      = float(obs_max)
            d['geospatial_vertical_units']    = param.attrs['unit']
            d['geospatial_vertical_positive'] = 'up'
            alt_done = True

    if not alt_done:
        logger.error("pas de 'standard_name' pour le paramètre d'altitude " +\
                     "=> pas de geospatialisation pour l'altitude")

    return d


def get_param_value(param, choix, s_acqid):
    """ Enrobage de param.get_from_selector.

        TODO
    """
    try:
        value = param.get_from_selector(choix, s_acqid)
    except Exception as e:
        logger.error(f"{config_file} : {param.name} : {e}")
        sys.exit(1)

    return value


def get_id_value():
    """ Retourne la valeur du champ 'id' à inscrire dans le fichier NetCDF.

        :return: valeur du champ 'id'
        :rtypr : str()
    """
    logger.log(logging.RUN, f"get_id_value")

    # raccourcis d'accès aux variables...
    prefix           = config.directives['prefix']
    processing_level = config.general['processing_level']

    # construction du nom (prefix et processing_level sont toujours positionnés)
    return f"{prefix}_{processing_level}"


def get_geos():
    """ Retourne les information de  geospatialisation sous forme de
		dictionnaire.
        sera inscrit directement dans le fichier NetCDF).
    """
    logger.log(logging.RUN, f"get_geos")

    # raccourcis d'accès aux variables...
    coordinates   = config.general.get('coordinates', None)

    if coordinates:
        # récupérer les min/max de spacialisation pour les paramètres de
        # 'coordinates' (sauf le premier qui est le temps)
        trajectory_params = coordinates.split()[1:]
        geos = get_trajectory_geospatial(trajectory_params, params_infos)
    else:
        lat, lon, alt = AIDA.decode_position_plf(cfg_abrev_plt)
        geos = dict()
        geos['geospatial_lat_min']      = lat
        geos['geospatial_lat_max']      = lat
        geos['geospatial_lon_min']      = lon
        geos['geospatial_lon_max']      = lon
        geos['geospatial_vertical_min'] = alt
        geos['geospatial_vertical_max'] = alt

    # écraser les valeurs trouvées avec celles éventuellement fournies dans
    # le fichier de configuration
    for key, val in config.geos.items():
        geos[key] = val

    return geos


def add_infos_to_config(mode, periode_infos, s_acqid, acq_infos, today):
    """ Ajoute les informations utiles à 'config.general' ('config.general'
        sera inscrit directement dans le fichier NetCDF).

        :param str()      mode         : 'mobile', 'jour', 'periode'
        :param dict()     periode_infos: dictionnaire qui contient les clés :
                                         'acqid_start', 'date_start', 'time_start',
                                         'acqid_end'  , 'date_end'  , 'time_end'
        :param str()      s_acqid      : nom de l'acquisition courrante
        :param AIDA.Inf() acq_infos    : .inf de l'acquisition.
        :param datetime() today        : datetime du moment.
    """
    logger.log(logging.RUN, f"add_infos_to_config")

    # raccourcis d'accès aux variables...
    coordinates   = config.general.get('coordinates', None)

    today_ISO     = today.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    acqid_start   = periode_infos['acqid_start']
    acqid_end     = periode_infos['acqid_end']


    # valeur du champ 'id'
    config.general['id'] = get_id_value()

    # product_version
    config.general['product_version'] = np.int32(version)

    # source_config
    config.general['source_config'] = os.path.basename(config_file)

    # valeur du champ 'acqid' ou 'flight_id'
    if mode == 'mobile':
        config.general['flight_id'] = s_acqid
    else:
        if acqid_start == acqid_end:
            config.general['acqid'] = acqid_start
        else:
            config.general['acqid'] = f"{acqid_start}-{acqid_end}"

    # valeur des champs specifiques aux vols (issues du .INF)
    if mode == 'mobile':
        try:
            date_vol = acq_infos.get_date_acq()
            config.general['flight_date'] = date_vol.strftime('%Y-%m-%d')
        except Exception as e:
            logger.error(f"problème 'Inf::date_vol' ({e})")

        try:
            date_dec = acq_infos.get_horaire('decollage')
            config.general['time_take_off'] = date_dec.strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception as e:
            logger.error(f"problème 'Inf::decollage' ({e})")

        try:
            date_att = acq_infos.get_horaire('atterrissage')
            config.general['time_landing'] = date_att.strftime('%Y-%m-%dT%H:%M:%SZ')
        except Exception as e:
            logger.error(f"problème 'Inf::atterrissage' ({e})")

    # valeur des champs 'date_created' et 'date_modified'
    config.general['date_created']  = today_ISO
    config.general['date_modified'] = today_ISO

    return


#==============================================================================
# fonctions de génération du fichier Net_CDF
def NetCDF_get_filename(periode_infos):
    """ Retourne le nom du fichier NetCDF à écrire en fonction des informations
        de 'periode_infos' et de 'date_format' (issu du fichier de
        configuration).

        :param dict() periode_infos: dictionnaire qui contient les clés :
                                     'acqid_start', 'date_start', 'time_start',
                                     'acqid_end'  , 'date_end'  , 'time_end'

        :return: nom du fichier NetCDF à écrire.
        :rtypr : str()
    """
    logger.log(logging.RUN, f"NetCDF_get_filename")

    # raccourcis d'accès aux variables...
    mode             = config.directives['mode']
    prefix           = config.directives['prefix']
    date_format      = config.directives['date_format']
    processing_level = config.general['processing_level']

    # construction du nom
    if mode != 'periode':
        s_acqid      = periode_infos['acqid_start']
        dt_acq       = periode_infos['time_start']
        s_acqid_date = dt_acq.strftime(date_format)

        if mode == 'mobile':
            if processing_level is None:
                filename = f"{prefix}_{s_acqid_date}_{s_acqid}_V{version}"
            else:
                filename = f"{prefix}_{s_acqid_date}_{s_acqid}_{processing_level}_V{version}"
        else:   # == 'jour'
            if processing_level is None:
                filename = f"{prefix}_{s_acqid_date}_V{version}"
            else :
                ## JCE filename = f"{prefix}_{processing_level}_{s_acqid_date}_V{version}"
                filename = f"{prefix}_{s_acqid_date}_{processing_level}_V{version}"

    else : # mode == 'periode':
        date_start = periode_infos['date_start']
        date_end   = periode_infos['date_end']

        filename = f"{prefix}_{date_start}_{date_end}"

        if processing_level is None:
            filename = f"{filename}_V{version}"
        else:
            filename = f"{filename}_{processing_level}_V{version}"

    logger.debug(f"NetCDF_get_filename : return : {os.path.join(out_dir, filename + '.nc')}")
    return os.path.join(out_dir, filename + '.nc')


def NetCDF_set_dimensions(root_cdf, dimensions, nb_time_values, coordinates):
    """ Enregistre dans l'objet root_cdf, les informations 'dimensions'.

        :param  nc.Dataset() root_cdf      : le dataset en cours de construction
        :param  str()        dimensions    : ['Limited', 'Unlimited']
        :param  str()        nb_time_values: longueur du vecteur temps
        :param  str()        coordinates   : chaine de configuration ou None
    """
    logger.log(logging.RUN, f"NetCDF_set_dimensions")

    # dimensions
    if dimensions == "Limited":
        root_cdf.createDimension('time', nb_time_values)
    else:
        root_cdf.createDimension('time', None)

    root_cdf.createDimension('level', 2)

    return


def NetCDF_trajectory(root_cdf, s_acqid):
    """ Enregistre dans l'objet root_cdf, les informations utiles pour la
        production d'un fichier NetCDF de type 'Trajectory'.

        TODO
    """
    logger.log(logging.RUN, f"NetCDF_trajectory")

    # raccourcis d'accès aux variables...
    coordinates   = config.general.get('coordinates', None)

    root_cdf.coordinates = coordinates
    root_cdf.featureType = "Trajectory"

    root_cdf.createDimension('string_length', string_length)

    # pour coller au format 'Single trajectory', il faut ajouter la variable
    # 'trajectory' qui contient : 'acqid=<acqid>'
    var = root_cdf.createVariable('trajectory', 'S1', ('string_length'))
    var.cf_role = 'trajectory_id'
    var[:] = nc.stringtochar(np.array(['acqid=' + s_acqid], f'S{string_length}'))

    return


def NetCDF_set_times(root_cdf, periode_infos, s_freq_ech, datation):
    """ Enregistre dans l'objet root_cdf, l'information datations.

        TODO
        :param  dict() period_infos: informations de début/fin de datation
        :param  str()  s_freq_ech  : freq_ech du vecteur temps (format str())
        :param Datation() datation: information de datation de la période.
    """
    logger.log(logging.RUN, f"NetCDF_set_times")

    beg = periode_infos['time_start'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    end = periode_infos['time_end'].strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    root_cdf.time_coverage_start = beg
    root_cdf.time_coverage_end   = end

    # time_resolution
    freq_ech = float(s_freq_ech)
    if freq_ech != 0.:
        time_ech = 1./freq_ech
        root_cdf.time_coverage_resolution = f"PT{time_ech:f}S"

    # écriture du temps
    dt  = datation.dt_time[0]
    dt0 = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    var               = root_cdf.createVariable ('time', 'f8', ('time',))
    var.units         = f'seconds since {dt0.strftime("%Y-%m-%d")} 00:00 UTC'
    var.standard_name = 'time'
    var.long_name     = 'time UTC'
    var.calendar      = 'standard'
    var[:]            = [ (t - dt0).total_seconds()  for t in datation.dt_time ]
    logger.debug("écriture du temps")

    # écriture des bornes temporelles
    time_bounds = datation.time_bounds
    if len(time_bounds) != 0:
        var.bounds = 'time_bnds'
        var        = root_cdf.createVariable ('time_bnds', 'f8', ('time','level'))
        var[:] = time_bounds[:,:]
    logger.debug("écriture des bornes temporelles")

    return


def NetCDF_add_meta(var, param, s_acqid):
    """ Enregistre dans la variable 'var' de l'objet root_cdf, les métadonnées
        du paramètres.

        TODO
    """
    logger.log(logging.RUN, f"NetCDF_add_meta pour : {param.name}")

    treated = list()

    # NOTE : get_param_value est un enrobage de : param.get_from_selector.
    # ----

    # les informations obligatoires (param_val peut contenir des '${}')
    # long_nale
    param_val     = param.config.get('long_name')
    var.long_name = get_param_value(param, param_val, s_acqid)
    treated.append('long_name')

    # origin
    param_val  = param.config['origin']
    var.origin = get_param_value(param, param_val, s_acqid)
    treated.append('origin')

    # standard_name
    param_val = param.config.get('standard_name')
    if param_val:
        standard_name = get_param_value(param, param_val, s_acqid)
        if standard_name:
            var.standard_name = get_param_value(param, param_val, s_acqid)
    treated.append('standard_name')

    # pour les altitudes seulement
    if param_val == 'altitude':
        var.positive = 'up'

    # unit
    param_val = param.config.get('units', param.attrs.get('unit', None))
    if not param_val:
        param_val = '1'
    else:
        if param_val in ['unknown', 'without', 'unitless']:
            param_val = '1'

    var.units = get_param_value(param, param_val, s_acqid)
    treated.append('units')

    # source
    param_val = param.config.get('source', param.source)
    if param_val:
        var.source = get_param_value(param, param_val, s_acqid)
    treated.append('source')

    # les autres informations venant du fichier de configuration
    for name, value in param.config.items():
        try:
            name, fmt = name.split(':')
        except Exception as e:
            fmt = None

        # déjà traité
        if name in treated:
            continue

        # récupérer la valeur fournie par le selector
        if isinstance(value, str):
            selected_value = get_param_value(param, value, s_acqid)
        else:
            selected_value = value

        # traitement des indications de format dans le nom de l'option
        if fmt:
            if fmt == 'NUM':
                # récupérer le format des données
                dtype = param.data.dtype
                val   = np.fromstring(selected_value, dtype=dtype, sep=',')

                # inscrire l'option sous le format désiré dans la variable NetCDF
                try:
                    setattr(var, name, val)
                except Exception as e:
                    stop_error(f"paramètre {name} : '{fmt}' : erreur netCDF4",
                               more=e)

            else:
                # fmt est un numpy dtype : int8, int16, int32, int64
                #                          float32, float64
                dtype = fmt
                try:
                    val = np.fromstring(selected_value, dtype=dtype, sep=',')
                except Exception as e:
                    stop_error(f"paramètre {name} : '{fmt}' : erreur de conversion",
                               more=e)
                # inscrire l'option sous le format désiré dans la variable NetCDF
                try:
                    setattr(var, name, val)
                except Exception as e:
                    stop_error(f"paramètre {name} : '{fmt}' : erreur netCDF4",
                               more=e)

        else: # pas de fmt
            # inscrire l'option sous le format désiré dans la variable NetCDF
            # NOTE : var.setncattr(name, selected_value) enregistre
            #        selected_value au format string
            # NOTE : ça ne "marche" pas pour des flag_values de type
            #        char/string : netCDF4 les enregistre en string et non pas
            #        en np.array de dtype='<U1' => le checker
            #        https://compliance.ioos.us/index.html râle...
            try:
                setattr(var, name, selected_value)
            except Exception as e:
                stop_error(f"paramètre {name} : '{selected_value}' : erreur netCDF4",
                           more=e)

    return


def NetCDF_init(periode_infos):
    """ Crée l'objet NetCDF et initialise les informations globales.

        TODO
    """
    logger.log(logging.RUN, f"NetCDF_init")

    # construction du nom du fichier à créer
    file_name = NetCDF_get_filename(periode_infos)

    # initialisation d'un objet NetCDF4.Dataset
    root_cdf = nc.Dataset(file_name , 'w', format='NETCDF4')

    return root_cdf, file_name


def NetCDF_create_variable(root_cdf, param):
    """ Crée une variable pour le paramètre param.name

        TODO
    """
    logger.log(logging.RUN, f"NetCDF_create_variable")

    # récupération de dim_array (en string depuis AIDA.get_unit_bornes)
    str_dim_array = str(param.attrs.get('dim_array', '1'))
    dim_array = AIDA.get_dim_array(str_dim_array)

    # récupération de unit_bornes ('unit_bornes' devrait être obligatoire...)
    str_unit_bornes = param.attrs.get('unit_bornes', 'unitless')
    unit_bornes = AIDA.get_unit_bornes(str_unit_bornes)

    dtype = param.data.dtype
    if str(dtype)[0] in ['f', 'd']:
        misval = np.nan
    else:
        # peut-être un peu sommaire...
        try:
            misval = int(param.attrs['misval'])
        except Exception as e:
            misval = None

    # TODO : on doit pouvoir regrouper les cas :
    #        si len(dim_array) == 1 && dim_array[0] == 1
    #           => création d'une variable simple
    #        sinon:
    #           pour chaque dimension de dim_array:
    #               créer une _class et une _bnds
    if len(dim_array) == 1:
        if dim_array[0] == 1:
            # vecteur 1D
            var = root_cdf.createVariable(param.name,
                                          dtype,
                                          ('time',),
                                          fill_value=misval)
        else:
            # vecteur 2D : creation d'une dimension et d'une
            # donnée pour les bornes
            dim_name = param.name + '_class'
            root_cdf.createDimension(dim_name, dim_array[0])

            var = root_cdf.createVariable(dim_name, 'f4', (dim_name,))

            # 'unit_bornes'
            var.units  = unit_bornes[0]
            var.bounds = dim_name + '_bnds'
            try :
                var.long_name = param.config['bornes_name']
            except :
                var.long_name = f"Classes of {param.config['long_name']}"

            liste_bornes   = AIDA.strBornes_to_array (param.attrs['bornes'])
            tab_bornes_sup = np.array( [ x[1] for x in liste_bornes[0] ] )
            var[:]         = tab_bornes_sup

            # creation de bounds pour les bornes du tableau
            var = root_cdf.createVariable(dim_name + '_bnds',
                                          'f4',
                                          (dim_name, 'level'))
            var[:] = np.array(liste_bornes[0])

            var = root_cdf.createVariable(param.name,
                                          'f4',
                                          ('time', dim_name),
                                          fill_value=np.nan)
    else: # dim_array contient plusieurs valeurs
        liste_bornes   = AIDA.strBornes_to_array (param.attrs['bornes'])
        tab_bornes_sup = np.array( [ x[1] for x in liste_bornes[0] ] )

        # pour le slicing de liste_bornes[0]
        start = 0

        dim_names = list()
        dim_names.append('time')

        for n, (dim, unit) in enumerate(zip(dim_array, unit_bornes)):
            dim_name = f'{param.name}_dim{n}_class'
            dim_names.append(dim_name)
            
            root_cdf.createDimension(dim_name, dim)

            var = root_cdf.createVariable(dim_name, 'f4', (dim_name,))

            # 'unit_bornes'
            var.units  = unit
            var.bounds = dim_name + '_bnds'
            try :
                var.long_name = param.config['bornes_name']
            except :
                var.long_name = f"Classes of {param.config['long_name']}"

            stop = start + dim
            var[:] = tab_bornes_sup[start:stop]

            # creation de bounds pour les bornes du tableau
            var = root_cdf.createVariable(dim_name + '_bnds',
                                          'f4',
                                          (dim_name, 'level'))
            var[:] = np.array(liste_bornes[0][start:stop])

            # incrémenter le slicing de liste_bornes[0]
            start = stop

        var = root_cdf.createVariable(param.name,
                                      'f4',
                                      tuple(dim_names),
                                      fill_value=np.nan)

    return var


def NetCDF_write(mode, periode_infos, vect_time, datation, params,
                 s_acqid=None, acq_infos=None):
    """ Génére le fichier NetCDF à partir des informations transmises.

        :params .... TODO :
        :param str()      mode    : 'mobile', 'jour', 'periode'
        :param Datation() datation: information de datation de la période.
        :param dict() params  : dictionnaire contenant toutes les informations
                                nécessaire pour la génération du fichier NetCDF.
        :param str()  s_acqid : nom de l'acquisition courrante (utilisé pour
                                faire le remplacement via le fichier de
                                sélection)
    """
    logger.log(logging.RUN, f"NetCDF_write")

    # date du moment
    today         = dt.datetime.today()
    today_history = today.strftime('%a %b %d %Y, %H:%M:%S')

    # raccourcis d'accès aux variables...
    creator_name  = config.general['creator_name']
    history       = config.general.get('history', None)

    # ajouter les informations utiles à config.general (config.general sera
    # inscrit directement dans le fichier NetCDF)
    add_infos_to_config(mode, periode_infos, s_acqid, acq_infos, today)

    # récupérer les inforamtion de geospatialisation
    geos = get_geos()

    # génération
    # ----------
    # raccourcis d'accès aux variables...
    dimensions  = config.directives['dimensions']
    coordinates = config.general.get('coordinates', None)

    # initialisation
    root_cdf, file_name = NetCDF_init(periode_infos)

    # dimensions
    NetCDF_set_dimensions(root_cdf, dimensions, len(vect_time.data), coordinates)

    # généralités (inscription directe de tout le dictionnaire `config.general`,
    # mis à jour par `add_infos_to_config`)
    root_cdf.setncatts(config.general)

    # geospatialisation (inscription directe de tout le dictionnaire 'geos')
    root_cdf.setncatts(geos)

    # history
    day_history = f"{today_history}, {creator_name}, {' '.join(sys.argv)} (V{__version__})"
    if history is None:
        history = f"{day_history}"
    else:
        history = f"{history.strip()}\n {day_history}"
    root_cdf.history = history

    # trajectory
    if coordinates:
        # en mode 'coordinates', pour les paramètres qui ne sont pas dans la
        # liste de 'coordinates' ajouter 'var.coordinates'
        # => mémoriser la liste des paramètres utilisés pour 'coordinates' sauf
        #    le 1ier paramètre qui est le temps
        trajectory_params = coordinates.split()[1:]

        NetCDF_trajectory(root_cdf, s_acqid)

    # datation
    s_freq_ech = vect_time.attributes['freq_ech']
    NetCDF_set_times(root_cdf, periode_infos, s_freq_ech, datation)

    # paramètres
    for param_name, param in params_infos.items():
        # creation de la variable (et des bornes si besoin)
        var = NetCDF_create_variable(root_cdf, param)

        if coordinates and param_name not in trajectory_params:
            var.coordinates = coordinates

        # ajout des données
        var[:] = param.data

        # ajout des méta-data
        NetCDF_add_meta(var, param, s_acqid)

    root_cdf.close
    print()
    logger.info(f"data_policy         : {config.general['data_policy']}")
    print()
    logger.info(f"écriture du fichier : {file_name}")

    return


#==============================================================================
def main():
    # pour rappel : les variables crées sous : "if __name__ == '__main__':"
    # sont globales

    # arguments de début et fin de traitement
    # ---------------------------------------
    dt_deb, dt_fin, acqid_deb, acqid_fin = get_deb_fin()

    # cohérence des paramètres début et fin
    check_acqids_consistency(acqid_deb, acqid_fin, cfg_plateforme)


    # raccourcis d'accès aux variables...
    reftime                = config.directives['reftime']
    datation_convention    = config.directives['datation_convention']
    date_format            = config.directives['date_format']
    mode                   = config.directives['mode']
    replace_missing_vector = config.directives['replace_missing_vector']
    if replace_missing_vector.lower() == 'true':
        replace_missing_vector = True
    else:
        replace_missing_vector = False


    # récupérer la liste des acqids traitables dans la liste des acqids
    # correspondants aux arguments debut et fin
    treatable_acqids = get_treatable_acqids(mode, acqid_deb, acqid_fin, reftime)
    if len(treatable_acqids) == 0:
        stop_error("...aucune acquisition traitables :-/")


    # mise à jour de l'option 'project' si absente
    config.check_project(str(treatable_acqids[0]))


    # recherche de la source
    # ----------------------
    # on estime qu'un vecteur de nom XXX a toujours la même source
    # => la source n'est cherchée qu'une fois
    # Cependant, si 'origin' est un nom de vecteur à chercher dans le
    # fichier de selection (il contient : ${...}), on ne connait le
    # nom du vecteur que lorsque'on traite l'acqid
    # => il faudrait faire une recherche à chaque acqid.
    # => pour éviter les multiples recherche (qui sont longues à faire)
    #    les sources trouvée sont mémorisées dans found_sources
    found_sources = dict()


    # boucle sur les acqid
    # --------------------
    datation         = None
    time_ref_checked = dict()
    periode_infos = dict()
    for acqid in treatable_acqids:
        print()
        logger.info(f"traitement de : {acqid}")
        s_acqid = str(acqid)

        if datation is None:
            datation = prod_CDF_datation.Datation(datation_convention, reftime)

        # gestion du temps
        # ----------------
        dt_start, dt_end, vect_time = get_times(acqid, reftime)
        dt_current_day = dt.datetime(dt_start.year, dt_start.month, dt_start.day, 0,0,0)
        nb_days = 0

        if not 'acqid_start' in periode_infos.keys():
            periode_infos['acqid_start'] = s_acqid
            periode_infos['time_start']  = dt_start
            periode_infos['date_start']  = dt_start.strftime(date_format)

        periode_infos['acqid_end'] = s_acqid
        periode_infos['time_end']  = dt_end
        # ATTENTION : ici il faut bien la date dt_start. (dt_end est 1 jour
        # trop loin pour les acquisitions de type 'jour').
        periode_infos['date_end']  = dt_start.strftime(date_format)

        # en mode 'periode' : mémoriser les informations du 1ier acqid.
        # en mode 'jour', 'mobile' : mémoriser les informations du .INF.
        if mode == 'periode':
            if s_acqid == str(treatable_acqids[0]):
                first_acqid = s_acqid
                first_time  = dt_start
                first_day   = dt_current_day
            else:
                nb_days = (dt_current_day - first_day).days
        else:
            try:
                acq_infos = AIDA.Inf(s_acqid)
            except Exception as e:
                logger.error(f"problème de lecture du .INF ({e})")


        # datation
        acq_time_bounds = datation.time_append(s_acqid, dt_current_day)

        # bornes
        datation.bnds_append(acq_time_bounds, nb_days)

        # si les vecteurs sont à rechercher dans le fichier de selection et
        # qu'il faut générer 1 fichier NetCDF par acqid, il faut mettre à jour
        # le standard_name et la source pour chaque acqid
        update_infos = mode in ['mobile', 'jour']


        # lecture des paramètres
        # ----------------------
        for param_name, param in params_infos.items():
            logger.debug(f"traitement de : [{param_name}]")

            cfg_origin = param.config['origin']

            try:
                origin = param.get_from_selector(cfg_origin, s_acqid,
                                                 update_infos=update_infos)
                # si update_infos = True, param.source est remis à None
            except Exception as e:
                stop_error(f"{config_file} : {param.name}", more=e)

            # lecture du vecteur
            try:
                vect = AIDA.Vector(s_acqid, origin)

                # vérification de la cohérence des ref_time
                if not origin in time_ref_checked.keys():
                    if vect.attributes['ref_time'] != reftime:
                        try:
                            l = [ reftime, vect.attributes['ref_time'] ]
                            Ref_time.check_reftimes(s_acqid, l, logger=logger)
                        except Exception as e:
                            stop_error(f"{param.name:15s} : " +\
                                       f"problème de datation :", more=e)
                        finally:
                            time_ref_checked[origin] = True

            except Exception as e:
                if replace_missing_vector:
                    replace_missing(param, treatable_acqids, len(vect_time.data))
                else:
                    logger.error(f"{param.name:15s} : " +\
                                 f"vecteur absent. Pas de remplacement demandé " +\
                                 f"'{origin}'")
                    sys.exit(1)
                continue
            else:
                param.set_attrs_from_header(vect.attributes)
                param.append_data(vect.data)


            # recherche de la source
            # ----------------------
            # - à l'initialisation param.source vaut None
            # - après la recherche, param.source contient une string qui peut
            #   être vide
            # - si update_infos = True, param.source est remis à None
            if param.source is None:
                if origin in found_sources.keys():
                    param.source = found_sources[origin]
                else:
                    logger.info(f"{param.name:15s} : recherche de source pour {origin}")
                    param.source = get_source(origin, s_acqid)
                    found_sources[origin] = param.source


        if mode in ['mobile', 'jour']:
            NetCDF_write(mode, periode_infos, vect_time, datation, params_infos,
                         s_acqid=s_acqid, acq_infos=acq_infos)
            reset_data(params_infos)
            datation      = None
            periode_infos = dict()


    if mode == 'periode':
        NetCDF_write(mode, periode_infos, vect_time, datation, params_infos,
                     s_acqid=None, acq_infos=None)

    return


if __name__ == '__main__':
    # pour rappel : les variables crées sous : "if __name__ == '__main__':"
    # sont globales


    # parsing de la ligne de commande
    description = 'Production de fichier NetCDF à partir de fichiers-vecteurs'
    epilog      = "Si le fichier de configurtation ne convient pas de " +\
                  "section [DIRECTIVES], la version historique est de " +\
                  "prod_CDF est lancée."

    parser = argparse.ArgumentParser(description=description, epilog=epilog)

    parser.add_argument('-r','--rep_out', '-o', '--out_dir',
                        dest='out_dir',
                        default='./',
                        metavar='dir', type=str,
                        help='nom du repertoire de sortie (défaut: %(default)s)')

    parser.add_argument('-S','--select',  required = False,
                        dest='select_file',
                        metavar='select_file', type=str,
                        help='chemin du fichier de sélection des vecteurs ' +\
                             'pour les paramètres.')
    parser.add_argument('-v','--version', required = False,
                        dest='version',
                        default=1,
                        metavar='version', type=int,
                        help='numéro de version des fichiers à produire ' +\
                             '(défaut: %(default)s)')

    parser.add_argument('-c', '--config', required = True,
                        dest='config_file',
                        metavar='config_file', type=str,
                        help='chemin du fichier de configuration.')

    parser.add_argument('prod_deb',
                        help='date de début (JJMMAAAA) ou acqid de début.')
    parser.add_argument('prod_fin',
                        help='date de fin   (JJMMAAAA) ou acqid de fin.')


    args = parser.parse_args()

    # récupération des arguments
    out_dir     = args.out_dir
    config_file = args.config_file
    select_file = args.select_file
    version     = args.version
    prod_deb    = args.prod_deb
    prod_fin    = args.prod_fin

    ### si l'option '-r' ou '--rep_out' a été passée, lancer la version historique
    ##if '-r' in sys.argv or '--rep_out' in sys.argv:
    ##    do_run_histo = True


    # lecture du fichier de config
    # ----------------------------
    if not os.path.isfile(config_file):
        stop_error(f"le fichier de configuration '{config_file}' n'existe pas")

    config_parser = configparser.ConfigParser(delimiters='=', interpolation=None)
    # obliger configparser a ne pas modifier la case des options
    config_parser.optionxform = str
    try:
        config_parser.read(config_file)
    except Exception as e:
        stop_error(f"Problème à la lecture du fichier '{config_file}'", more=e)

    # mémoriser le nom du fichier (il est utilisé dans prod_CDF_config.py)
    config_parser.filename = config_file

    # vérifier si la section [DIRECTIVES] est présente
    if not config_parser.has_section('DIRECTIVES'):
        logger.warning("pas de section 'DIRECTIVES' dans le fichier de configuration")

        # lancement de la version historique
        runstring = f"-c {config_file} -r {out_dir}"
        if version:
            runstring = f"{runstring} -v {version}"
        runstring = f"{runstring} {prod_deb} {prod_fin}"
        run_histo(runstring)


    # Nouvelle version
    # ================
    logger.info(f"{parser.prog}                         : version {__version__}")

    # répertoire de sortie
    if not os.path.isdir(out_dir):
        stop_error(f"le répertoire de sortie '{out_dir}' n'existe pas")
    logger.info(f"Répertoire de sortie                : {out_dir}")

    # version
    logger.info(f"Version                             : {version}")

    # fichier de configuration par défaut
    try:
        defaults = prod_CDF_defaults.Defaults()
    except Exception as e:
        stop_error("erreur à la lecture du fichier de configuration par défaut",
                   more=e)
    logger.info(f"Fichier de configuartion par défaut : {defaults.filename}")

    # fichier de configuration
    logger.info(f"Fichier de configuration            : {config_file}")
    try:
        config = prod_CDF_config.Config(config_parser, defaults.general)
    except Exception as e:
        stop_error("erreur à la lecture du fichier de configuration",
                   more=e)

    # fichier de sélection de vecteur pour les paramètres
    selector = None
    if select_file:
        try:
            selector = prod_CDF_selector.Selector(select_file)
        except Exception as e:
            stop_error(f"ERREUR", more=e)

        logger.info(f"Fichier de sélection                : {select_file}")
    else:
        logger.info(f"Fichier de sélection                : aucun")


    # analyse du fichier de configuration
    logger.info(f"Vérification du contenu du fichier  : {config_file}")
    try:
        config.check_directives()
    except Exception as e:
        stop_error("erreur dans le contenu du fichier de configuration",
                   more=e)

    config.check_general()

    params_infos = prod_CDF_params.get_params_from_config(config_parser, selector)
    check_ancillaries(params_infos)
    check_coordinates(config, params_infos)

    # vérifications de compatibilité...
    if (config.mode == 'periode') and select_file:
        stop_error(f"l'option '-S {select_file}' et la configuration " +\
                   f"'mode = {config.mode}' sont incompatibles.")

    if config.trajectory and config.mode == 'periode':
        stop_error(f"l'option 'coordinates' et la configuration " +\
                   f"'mode = {config.mode}' sont incompatibles.")

    # check de la plateforme fournie dans le fichier de configuration
    try:
        cfg_plateforme = config.directives['plateforme']
        cfg_abrev_plt = AIDA.AIDA_nom_long_to_abrev(cfg_plateforme)
    except Exception as e:
        stop_error(f"plateforme inconnue : '{cfg_plateforme}'")


    # ouf ! on y va !
    main()

    # fin
    sys.exit(0)
