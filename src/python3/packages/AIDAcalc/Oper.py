#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Gestion des opérateurs pour ADC.
"""

import sys
import os
import logging
import re
import numpy as np
import cfunits as cf
import copy


logger = logging.getLogger('adc')


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import ADC_error
import AIDA
import Units
import Chrono
import Constantes
import Ref_time
from Misval      import AIDA_type_misval as AIDA_type_misval
from ADC_rapport import ADC_Rapport      as Rapport


# champ 'origine' des vecteurs
origine = os.path.split(sys.argv[0])[1]

abrev_to_families = { k: str(v)  for k, v in AIDA.get_all_abrev_to_family() }
families_to_abrev = { v: str(k)  for k, v in AIDA.get_all_abrev_to_family() }


class Arg():
    """ Gestion des argument des opérateurs pour ADC.
    """
    def __init__(self, **kwargs):
        return


    def show_me(self):
        """ Debug...
        """
        max_len = max( (len(key) for key in self.__dict__.keys()) )

        for key, value in self.__dict__.items():
            print(f'    - {key:{max_len}s}   = {value}')


class Oper():
    """ Gestion des opérateurs pour ADC.
    """
    def __init__(self, **kwargs):
        self.acqid    = kwargs.get('acqid'   , None)
        self.name     = kwargs.get('name'    , None)
        self.adc_opts = kwargs.get('adc_opts', None)
        return


    # méthodes de classe
    @classmethod
    def check_convertibility_to_unit(self, name, data, unit_from, unit_to):
        """ Test et log un message de compatibilté des 2 unités 'unit_from'
            et 'unit_to' sont compatibles...

            NOTE : utilisé par les opérateurs C (FVB teste la compatibilité
                   mais ne fait pas les convertions)

            :param str()       name      : nom du vecteur.
            :param np.array()  data      : data du vecteur.
            :param str()       unit_from : unité de départ des données.
            :param str()       unit_to   : unité d'arrivée des données.

            :return: 0 = les unités sont égales
                     1 = les unités sont équivalentes
                     2 = les unités ne sont pas compatibles
        """
        logger.log(logging.RUN, "check_convertibility_to_unit")

        # test de convertibilité
        cfunit_from = cf.Units(unit_from)
        cfunit_to   = cf.Units(unit_to)

        if cfunit_from.equals(cfunit_to):
            logger.debug(f"'{name}' (check) conversion : unité " +\
                         f"reçue = {cfunit_from} -> " +\
                         f"attendue = {cfunit_to} : " +\
                          "égales")
            ret = 0
        elif cfunit_from.equivalent(cfunit_to):
            logger.info(f"'{name}' (check) conversion : unité " +\
                        f"reçue = {cfunit_from} -> " +\
                        f"attendue = {cfunit_to} : " +\
                         "différentes mais convertibles : ON CONTINUE...")
            ret = 1
        else:
            logger.warning(f"'{name}' (check) conversion : unité " +\
                           f"reçue = {cfunit_from} -> " +\
                           f"attendue = {cfunit_to} : " +\
                            "incompatibles : ON CONTINUE QUAND MÊME")
            ret = 2

        return ret


    @classmethod
    def convert_to_unit(self, name, data, unit_from, unit_to):
        """ Convertie IN_PLACE par cfunits, les données reçues de l'unité
            unit_from en unit_to.

            NOTE : utilisé par les opérateurs Python.

            :param str()       name      : nom du vecteur.
            :param np.array()  data      : data du vecteur.
            :param str()       unit_from : unité de départ des données.
            :param str()       unit_to   : unité d'arrivée des données.
        """
        logger.log(logging.RUN, "convert_to_unit")

        # conversion automatique d'unité
        cfunit_from = cf.Units(unit_from)
        cfunit_to   = cf.Units(unit_to)

        # inutile de transformer par exemple des 's' en 'second'
        # TODO : ce test pourrait peut-être être supprimé si on est sûr d'avoir
        #        des unités normalisée ici...
        if cfunit_from.formatted(definition=True) != cfunit_to.formatted(definition=True):
            try:
                cf.Units.conform(data, cfunit_from, cfunit_to, inplace=True)
                logger.debug(f"'{name}' (effectif) conversion : unité " +\
                             f"reçue = {cfunit_from} -> " +\
                             f"attendue = {cfunit_to} : " +\
                              "ok")
            except ValueError as e:
                logger.warn(f"'{name}' (effectif) conversion: " +\
                            f"reçue = {cfunit_from} -> " +\
                            f"attendue = {cfunit_to} : " +\
                            "incompatibles : ON CONTINUE QUAND MÊME")
        else:
            logger.debug(f"'{name}' (effectif) conversion : unité " +\
                         f"reçue = {cfunit_from} -> " +\
                         f"attendue = {cfunit_to} : " +\
                          "rien à faire")

        return


    @classmethod
    def normalize_unit(cls, VO_name, VO_header, stop):
        """ Normalise, si possible, VO_header['unit'] et
            VO_header['unit_bornes'].

            :param str()  VO_name   : nom du vecteur.
            :param dict() VO_header : header du vecteur.
            :param bool() stop      : flag 'stop_on_error'
        """
        logger.log(logging.RUN, "normalize_unit")

        # 'unit'
        field = 'unit'
        if not field in VO_header.keys():
            unit = 'unitless'
            aida_unit = Units.get_AIDA_unit(unit)
            VO_header[field] = aida_unit
            logger.debug(f"'{VO_name}' : pas d'unité fournie pour {field} " +\
                         f"=> unité positionnée à {VO_header[field]}")
        else:
            unit = VO_header[field]

            try:
                aida_unit = Units.get_AIDA_unit(unit)

                # précision pour les latitude / longitude
                is_lat = cf.Units(aida_unit).islatitude
                is_lon = cf.Units(aida_unit).islongitude
                if is_lat and VO_name.startswith('pos_lat'):
                    aida_unit = 'degree_north'
                elif is_lon and VO_name.startswith('pos_lon'):
                    aida_unit = 'degree_east'

                if unit != aida_unit:
                    VO_header[field] = aida_unit
                    logger.debug(f"'{VO_name}' : normalisation de l'unité : " +\
                                 f"pour le champ '{field}' : " +\
                                 f"{unit} -> {aida_unit}")
            except Exception as e:
                logger.warning(f"Oper::normalize_unit : {e}")


        # 'unit_bornes'
        field = 'unit_bornes'
        if field in VO_header.keys():
            units = AIDA.get_unit_bornes(VO_header[field])
            print(f":::: units = {units}")
            for unit in units:
                try:
                    aida_unit = Units.get_AIDA_unit(unit)

                    # précision pour les latitude / longitude
                    is_lat = cf.Units(aida_unit).islatitude
                    is_lon = cf.Units(aida_unit).islongitude
                    if is_lat and VO_name.startswith('pos_lat'):
                        aida_unit = 'degree_north'
                    elif is_lon and VO_name.startswith('pos_lon'):
                        aida_unit = 'degree_east'

                    if unit != aida_unit:
                        VO_header[field] = aida_unit
                        logger.debug(f"'{VO_name}' : normalisation de l'unité : " +\
                                     f"pour le champ '{field}' : " +\
                                     f"{unit} -> {aida_unit}")
                except Exception as e:
                    logger.warning(f"Oper::normalize_unit : {e}")

        return


    @classmethod
    def get_default_misval(cls, attributes):
        """ Retourne autant que faire se peut le misval par dééfaut
            correspondant au type du vecteur.

            :param dict() attributes : attributs d'un vecteur.

            :return: la valeur par défault du misval
            :rtype:  str()
        """
        logger.log(logging.RUN, "get_default_misval")


        # default misval
        typ = attributes['format']
        if not typ in AIDA_type_misval.keys():
            ADC_error.critical( "DEV : Oper:get_default_misval : traiter " +\
                               f"typ = '{typ}'",
                               stop=True)
        else:
            return AIDA_type_misval[typ]


    @classmethod
    def get_ref_time(cls, attributes):
        """ Retourne autant que faire se peut le nom du ref_time trouvé dans
            le dictionnaires des attributs passé en argument.
            Si les attributs correspondent à ce qui semble être un ref_time,
            retourne None

            ATTENTION :
            il existe des vecteurs temps sans champ famille ou avec
            le champ famille=unknow...
            => on estime que l'on a à faire à un vecteur temps si le nom du
            paramètre commence par 'time' ou 'rft_' (oui, c'est un peu moyen)

            :param dict() attributes : attributs d'un vecteur.

            :return: le nom du ref_time si possible
                     False sinon.
            :rtype:  str()
        """
        logger.log(logging.RUN, "get_ref_time")

        name = attributes['#hdr_name']
        if name.startswith('time') or name.startswith('rft_'):
            return None

        if not 'ref_time' in attributes.keys():
            logger.warning(f"'{name}' : pas de 'ref_time'")
            return None
        else:
            return attributes['ref_time']


    def user_update_header(self, index, header):
        """ Traitement des arguments optionnels de type HDR_xxx reçus.
            Ces arguments permettent de forcer des valeurs dans le header des
            vecteurs de sortie.
            Ils ont été enregistrés dans l'objet 'opérateur' au parsing de la
            ligne de commande.
            Modifie le header reçu.

            :param int                     index  : index du vecteur de sortie
                                                    ([0, ...])
            :param AIDA.Vector['attribut'] header : header du vecteur.

            :return: 'header' mis à jour.
            :rtype:  AIDA.Vector['attribut']
        """
        logger.log(logging.RUN, "user_update_header")

        if not self.args_HDR:
            return

        for key, val in self.args_HDR.items():
            if val[index]:
                h_key = key[4:] # troncature de 'HDR_'
                header[h_key] = val[index]
            else:
                logger.info(f"'{key}:{val[index]} pour le vecteur de sortie {index}  => pas de modification")

        return


    def do_control_famille(self, arg_brut, arg, VI_attributes):
        """ Pour un vecteur d'entrée, vérifie si sa famille correspond à la

            famille demandée dans le descritpeur (C ou Python) de l'opérateur.
            Les espaces dans la famille sont systématiquement remplacés
            par '_'.

            Retourne sans rien faire si :
            - control_famille = False
            - il n'y a pas de famille requise dans la descrption de l'opérateur
            - la famille requise dans l'opérateur est '' ou 'any'.

            :param str()                   arg_brut      : nom du vecteur.
            :param Oper.Arg()              arg           : header du vecteur.
            :param AIDA.Vector['attribut'] VI_attributes : header du vecteur.
        """
        logger.log(logging.RUN, "do_control_famille")

        stop            = self.adc_opts['stop_on_error']
        control_famille = self.adc_opts['control_famille']

        famille_input = VI_attributes['famille']

        # famille reçue dans le header du vecteur
        # (remplacement des ' ' dans, par exemple, 'eau vapeur')
        if ' ' in famille_input:
            famille_input = famille_input.replace(' ', '_')
            logger.warning(f"'{arg_brut}' : remplacement des espaces " +\
                           f"dans la famille reçue : '{famille_input}'")

        if not control_famille:
            return

        if not hasattr(arg, 'famille'):
            return

        if isinstance(arg.famille, str):
            if arg.famille in ['', 'any']:
                return

        # famille(s) requise(s) dans la descrption de l'opérateur
        if isinstance(arg.famille, str):
                familles_required = [ arg.famille ]
        elif isinstance(arg.famille, list):
            familles_required = arg.famille


        # contrôle de la famille
        # (remplacement *silencieux* des ' ' dans, par exemple, 'eau vapeur')
        if not famille_input in [ value.replace(' ', '_') for value in familles_required ]:
            msg = f"'{arg_brut}' : erreur de famille : " +\
                  f"attendue(s) = '{familles_required}' <-> " +\
                  f"reçue = '{famille_input}'"
            if control_famille or stop:
                raise Exception(msg)
            else:
                logger.warning(msg)

        return


    def normalize_famille(self, VO_name, VO_header):
        """ Normalisation de la famille...
            - si le champ famille est absent du header, le positionner à 'auto'
            - si le champ famille est positionné à 'auto', détermine la
              famille à partir des 3 premières lettres du nom de vecteur
            - s'il y a des espaces dans la valeur de la famille, remplacer les
              espaces par des '_' (ex 'eau vapeur')

            Vérification de la cohérence entre la famille du header et la
            famille déterminée par CFunits (à partir de l'unité).
            NOTE : voir à l'usage si cette vérification est pertinante.

            :param str()  VO_name   : nom du vecteur.
            :param dict() VO_header : header du vecteur.
        """
        logger.log(logging.RUN, "normalize_famille")

        stop            = self.adc_opts['stop_on_error']
        control_famille = self.adc_opts['control_famille']

        stop_msg = "option -S => arrêt immédiat"

        # si le champ famille est absent du header, le positionner à 'auto'
        if not 'famille' in VO_header.keys():
            VO_header['famille'] = 'auto'
            logger.debug(f"'{VO_name}' : " +\
                          "pas de famille fournie " +\
                         f"=> forcée à {VO_header['famille']}")

        # si le champ famille est positionné à 'auto', déterminer la
        # famille à partir des 3 premières lettres du nom de vecteur
        if VO_header['famille'] == 'auto':
            acronyme = VO_name[0:3]
            if not acronyme in abrev_to_families.keys():
                msg = f"'{VO_name}' : " +\
                      f"'{acronyme}' ne correspond à aucune famille"

                acronyme = 'xxx'

                if control_famille:
                    logger.warning(msg)
                    if stop:
                        raise Exception(stop_msg)

            VO_header['famille'] = abrev_to_families[acronyme]
            logger.debug(f"'{VO_name}' : " +\
                         f"famille positionnée à : '{VO_header['famille']}'")
        else:
            # s'il y a des espaces dans la valeur de la famille, remplacer les
            # espaces par des '_' (ex 'eau vapeur')
            if ' ' in VO_header['famille']:
                VO_header['famille'] = VO_header['famille'].replace(' ', '_')
                logger.warning(f"'{VO_name}' : remplacement des ' ' par '_' : " +\
                               f"=> {VO_header['famille']}")

            # vérifier que la famille reçue existe
            if not VO_header['famille'] in abrev_to_families.values():
                msg = f"'{VO_name}' : " +\
                      f"famille inexistante : '{VO_header['famille']}'"

                if control_famille:
                    logger.warning(msg)
                    if stop:
                        raise Exception(stop_msg)

            acronyme = VO_name[0:3]

            # cas où le VO_name est 'LLATIME', par exemple
            if len(VO_name) < 4:
                msg = f"'{VO_name}' : " +\
                      f"nom trop court pour contenir une famille " +\
                      f"=> pas de normalisation de la famille"

                if control_famille:
                    logger.warning(msg)
                    if stop:
                        raise Exception(stop_msg)
                return

            if acronyme.isupper() or VO_name[3] != '_':
                logger.debug(f"'{VO_name}' : pas d'acronyme "
                              "=> pas de normalisation de la famille")
                return

            # cas où le VO_name est 'flg_', par exemple
            if acronyme == 'flg':
                if VO_header['famille'] != 'controle':
                    logger.warning(f"'{VO_name}' : la famille devrait être 'controle' " +\
                                   f"et non pas {VO_header['famille']}")
                return

            # vérifier que les 3 premières lettres correspondent à la famille reçue
            famille = VO_header['famille']
            if acronyme != families_to_abrev[famille]:
                msg = f"'{VO_name}' : " +\
                      f"'{acronyme}' ne correspond pas à la famille " +\
                      f"'{families_to_abrev[famille]}'"

                if control_famille:
                    logger.warning(msg)
                    if stop:
                        raise Exception(stop_msg)

        if not control_famille:
            return


        # cohérence entre la famille et la famille selon CF
        ### TODO : voir à l'usage si cette vérification est pertinante...
        if not 'unit' in VO_header.keys():
            logger.warning(f"'{VO_name}' : unité non fournie " +\
                            "=> pas de vérification de compatibilité avec " +\
                            "les familles CFunits")
            return

        ###        janvier 2023 : le code qui suit (contrôle de la cohérence
        ###        entre la famille et la famille selon CF_units) semble ne pas
        ###        amener grand-chose => non exécuté
        return

        ### TODO : voir à l'usage...
        cf_family = Units.get_CF_family(VO_header['unit'])
        if not cf_family:
            return

        famille   = VO_header['famille']
        if cf_family != famille:
            logger.warning(f"'{VO_name}' : " +\
                            "incompatibilité famille <-> CF famille : " +\
                           f"{famille} <-> {cf_family}")
        else:
            logger.debug(f"'{VO_name}' : " +\
                         f"famille '{VO_header['famille']}' cohérente avec " +\
                         f"'{cf_family}'")

        return


    def check_write_ability(self, output_names):
        """ Vérifie que tous les vecteurs de sortie dont les noms sont dans la
            liste reçue pourront être écrits/écrassés par l'opérateur.
            (il est inutile de lancer un opérateur qui ne pourra pas écrire
            ses outputs).

            :param list() output_names : nom des vecteurs de sortie.

            :return: True si tous les vecteurs de sortie pourront être écrits.
                     False sinon.
            :rtype:  boolean()
        """
        logger.log(logging.RUN, "check_write_ability")

        ok = True

        if not self.adc_opts['backup'] and not self.adc_opts['force']:
            for name in output_names:
                ni_name = self.get_ni_name(name, mode_IN=False)
                path = os.path.join (self.path, ni_name + '.vbn')
                if os.path.isfile(path):
                    ok = False
                    break

        # inscription dans le rapport
        if not ok:
            logger.warning("vecteurs existants non recréés => opérateur non exécuté")
            Rapport.add('vecteurs existants non recréés',
                        f"{self.Nom} : ligne {self.line_nb}")
        return ok


    def check_before_call(self, reftimes, output_names):
        """ Effectue toutes les vérifications fonctionnelles qui doivent être
            faites avant d'appeler un opérateur.

            :param list() reftimes     : nom des vecteurs temps.
            :param list() output_names : nom des vecteurs de sortie.

            :return: True si toutes les vérifications sont ok, False sinon.
            :rtype:  boolean()
        """
        logger.log(logging.RUN, f"check_before_call : {reftimes}, {output_names}")

        ok = True

        # vérification des vecteurs temps
        if self.control_reftime and len(reftimes) > 1:
            ok = Ref_time.check_reftimes(self.acqid, reftimes, logger=logger)

        # vérification des droits d'écriture/écrasement
        if ok:
            ok = self.check_write_ability(output_names)

        return ok


    def warn_if_obsolet(self):
        """ Afiche un warning si l'opérateur est obsolet.
        """
        logger.log(logging.RUN, "warn_if_obsolet")

        # opérateur obsolète ?
        if self.repl_oper:
            logger.warning(f"L'operateur {self.Nom} est obsolete : " +\
                           f"remplacez-le par {self.repl_oper}")
            if self.repl_cause:
                logger.warning(f"cause : {self.repl_cause}")


    def get_ni_name(self, name, mode_IN=True):
        """ Retourne le nom du vecteur à utiliser en fonction de l'option
            'dev_nb'.

            :param str()  name    : nom de base du vecteur
            :param bool() mode_IN : True : name est le nom d'un vecteur d'entrée
                                    => retourne le nom du vecteur à utiliser
                                       (<=> avec ou sans l'extension .ni)
                                    False : name est le nom d'un vecteur de sortie
                                    => retourne le nom que DOIT avoir le vecteur.


            :return: nom du vecteur fonction de l'option 'dev_nb'.
            :rtype:  str()
        """
        logger.log(logging.RUN, f"get_ni_name : name = {name}, mode_IN = {mode_IN}")

        if not self.adc_opts['dev_nb']:
            return name

        ni_name = name + f".n{self.adc_opts['dev_nb']}"

        if mode_IN:
            filename = os.path.join (AIDA.ID_to_datapath(self.acqid),
                                     ni_name + '.vbn')
            if not os.path.isfile(filename)        and \
               not os.path.isfile(filename + '.gz'):
               ni_name = name

        return ni_name


    def get_dollar_parts(self, in_str):
        """ Retourne un set de toutes les variables de type $xxx
        """
        pattern = r'(?P<field>\$[a-zA-Z0-9_.$]+)'

        return set(re.findall(pattern, in_str))


    def replace_dollar_Chrono(self, in_arg):
        """ Retourne la valeur correspondante à 'in_arg' après remplacement de
            la variable de type '$Chrono'.
            ('in_arg' est une chaine qui ne contient *que* la variable
             $Chronoxxx)
        """
        logger.log(logging.RUN, f"replace_dollar_Chrono : in_arg = '{in_arg}'")

        # vérifier que l'acqid est enregistré
        acqid = getattr(self, 'acqid', None)
        if not acqid:
            raise Exception ( "Oper::replace_dollar_Chrono : " +\
                             f"{self.Nom} : pas d'acqid...")


        # parser in_arg en ses différentes parties
        pattern = r'^\$Chrono\.(?P<field>[a-zA-Z_0-9]+)$'
        match = re.match(pattern, in_arg)
        if not match:
            raise Exception ( "Oper::replace_dollar_Chrono : " +\
                             f"erreur de syntaxe : '{in_arg}'")

        field   = match.group('field')

        # si besoin, lire le .chrono
        chrono = getattr(self, 'chrono', None)
        if not chrono:
            try:
                self.chrono = Chrono.Chrono(acqid)
            except Exception as e:
                ###ADC_error.critical(f"{e}", stop=True)
                raise Exception (f"Oper::replace_dollar_Chrono : {e}")

        # récupérer la valeur du champ demandé
        try:
            value = self.chrono.get_value(field)
        except Exception as e :
            ###ADC_error.critical(f"{e}", stop=True)
            raise Exception (f"Oper::replace_dollar_Chrono : {e}")

        logger.debug(f"replace_dollar_Chrono : return value = '{value}'")

        return value


    def replace_dollar_Acq(self, in_arg):
        """ Retourne la valeur correspondante à 'in_arg' après remplacement de
            la variable de type '$Acq'.
            ('in_arg' est une chaine qui ne contient *que* la variable $Acqxxx)
        """
        logger.log(logging.RUN, f"replace_dollar_Acq : in_arg = '{in_arg}'")

        # vérifier que l'acqid est enregistré
        acqid = getattr(self, 'acqid', None)
        if not acqid:
            raise Exception ( "Oper::replace_dollar_Acq : " +\
                             f"{self.Nom} : pas d'acqid...")

        # parser in_arg en ses différentes parties
        pattern = r'^\$Acq\.\$(?P<field>[a-zA-Z_]+)\.(?P<attribut>[a-zA-Z_]+)$'
        match = re.match(pattern, in_arg)
        if not match:
            raise Exception ( "Oper::replace_dollar_Acq : " +\
                             f"erreur de syntaxe : '{in_arg}'")

        field    = match.group('field')
        attribut = match.group('attribut')

        # si besoin, lire le .inf
        inf = getattr(self, 'inf', None)
        if not inf:
            self.inf = AIDA.Inf(acq_id=acqid)

        # récupérer la valeur du champ demandé
        if field == 'date' and attribut == 'DOY':
            try:
                inf_date = self.inf.get_date_acq()
                doy = int(inf_date.strftime("%j"))
            except Exception as e :
                ###ADC_error.critical( "Oper::replace_dollar_Acq : " +\
                ###                   f"Exception de Inf.get_date_acq : {e}",
                ###                   stop=True)
                raise Exception ("Oper::replace_dollar_Acq : {e}")
        else:
            raise Exception ( "Oper::replace_dollar_Acq : " +\
                             f"ne sait pas traiter : {in_arg}...")

        logger.debug(f"replace_dollar_Acq : return doy = '{doy}'")
        return doy


    def write_vect(self, acqid, VO_index, VO_name, VO_header, VO_data):
        """ Enrobage d'écriture d'un vecteur.

            :param int  VO_index  : VO_index du vecteur de sortie ([0, ...])
        """
        logger.log(logging.RUN, f"write_vect : {VO_name}")

        backup          = self.adc_opts['backup']
        force           = self.adc_opts['force']
        dev_nb          = self.adc_opts['dev_nb']
        stop            = self.adc_opts['stop_on_error']
        control_famille = self.adc_opts['control_famille']
        test_and_valid  = self.adc_opts['test_and_valid']

        # clés du header à supprimer
        # (elles sont gérées automatiquement par AIDA.Vector.write() ou
        #  n'appartiennent pas au header)
        delete_keys = ['obs_min',
                       'obs_max',
                       'endianness',
                       'date_creation',
                       'NbVal',
                      ]

        # traitement des arguments optionnels de type HDR
        self.user_update_header(VO_index, VO_header)

        # normalisation des l'unités
        Oper.normalize_unit(VO_name, VO_header, stop)

        # famille
        self.normalize_famille(VO_name, VO_header)

        # clés du header à supprimer si elles ont été données sans raison dans
        # les fonctions ID_xxx (opérateur C)
        # - type_ech seulement pour les vecteurs temps
        # - type_ech != de régulier ou irregulier
        if 'type_ech' in VO_header.keys():
            if VO_header['famille'] != 'temps':
                del VO_header['type_ech']
            else:
                if not VO_header['type_ech'] in ['regulier', 'irregulier']:
                    logger.debug(f"'{self.Nom}' : " +\
                                    "champ type_ech en sortie supprimé : " +\
                                   f"{VO_header['type_ech']}")
                del VO_header['type_ech']

        # "normalisation" des freq_ech...
        # il arrive que freq_ech soit en float alors que FVB l'a noté en int
        # (en particulier si freq_ech a été posiotnné par "$Arg1.sample")
        # tenter de se rapprocher de FVB
        if not 'freq_ech' in VO_header.keys():
            #raise Exception(f"'{VO_name}' : header sans 'freq_ech'")
            logger.info(f"'{VO_name}' : header sans 'freq_ech'")
        freq_ech = VO_header['freq_ech']
        if freq_ech.endswith('.') or freq_ech.endswith('.0'):
            VO_header['freq_ech'] = str(int(float(freq_ech)))
            logger.debug(f"freq_ech = {freq_ech} -> {str(int(float(freq_ech)))}")
        elif freq_ech.replace('"', '') == '':
            del VO_header['freq_ech']
            logger.info(f"'{VO_name}' : header avec 'freq_ech' vide")
        else:
            # pour les freq_ech non-entières, limiter le nombre de décimales
            freq_ech = float(VO_header['freq_ech'])
            VO_header['freq_ech'] = f"{freq_ech:.12g}"


        # finaliser le header
        VO_header['vol']       = acqid
        VO_header['origine']   = f"traitement {origine}"
        VO_header['#hdr_name'] = VO_name
        for key in delete_keys:
            if key in VO_header:
                del VO_header[key]

        # récupérer la lettre numpy du format
        char_format = AIDA.np_string(VO_header['format'])[0]

        misval = None
        if not 'misval' in VO_header.keys():
            VO_header['misval'] = 'nan'
            logger.info(f"Oper::write_vect : {VO_name} : " +\
                        f"misval positionné à : '{VO_header['misval']}'")
        else:
            # à force de transformation il arrive que misval pour Int_32 = xxx.yyy
            if char_format != 'f' and char_format != 'd' and char_format != 'U':
                try:
                    VO_header['misval'] = str(int(VO_header['misval']))
                except Exception as e:
                    VO_header['misval'] = '-2147483648'
                    logger.debug(f"forçage de misval à {VO_header['misval']}")


        # misval : doit être enregistré au format du vecteur (par ex.
        # misval = $Arg1.misval avec Arg1 vecteur de type float64 alors
        # que VO est de type float32)
        if not char_format == 'U':
            if not VO_header['misval'].lower() == 'nan':
                misval = eval(VO_header['misval'])
                if char_format == 'f':
                    VO_header['misval'] = f"{np.array([misval], char_format)[0]:.9g}"
                else:
                    VO_header['misval'] = str (np.array([misval], char_format)[0] )
            else:
                misval = np.nan


        # pour les types float/double, remplacement des nan, inf, -inf
        # par misval
        if char_format == 'f' or char_format == 'd':
            VO_data = np.nan_to_num(VO_data, nan=misval, posinf=misval, neginf=misval)

        # pour le type 'U', faire comme dans Vector:_write(), sinon, lorsqu'on
        # appel ADC avec l'option '-f' :
        # - les données en cours sont byte    : array(...b'Profil11'], dtype='|S32')
        # - les données disque sont en string : array(... 'Profil11'], dtype='<U32')
        if char_format == 'U':
            logger.debug(f"{VO_name} : type 'U' -> 'S', " +\
                         f"comme AIDA.Vector:_write()")
            VO_data = VO_data.astype(AIDA.np_string(VO_header['format']))

        # création du vecteur
        ni_name = self.get_ni_name(VO_name, mode_IN=False)
        try:
            # création du vecteur
            vect_out = AIDA.Vector(acqid, ni_name, attributes=VO_header, data=VO_data)
        except (AIDA.AidaError, IOError, Exception) as e :
            msg = f"'{VO_name}' : échec à la création du vecteur"
            logger.error(msg)
            # si besoin, ajouter un préfixe au message AIDA
            prefix = ''
            if not e.args[0][0] in ['-', '+']:
                prefix = '+++ '
            logger.log(logging.AIDA, f"{prefix}{e}")
            Rapport.add(msg)
            raise Exception (msg)


        # MODE 'test_and_valid'
        if test_and_valid:
            try:
                path         = vect_out.storage_path
                prev_version = AIDA.Vector(acqid, ni_name)
                fvb_file     = (prev_version.attributes['origine'] == 'traitement fvb')
                fvb_path     = path.replace('.vbn', '.FVB.vbn')
                if os.path.isfile(path) and fvb_file and not os.path.isfile(fvb_path):
                    os.rename(path, fvb_path)
            except Exception:
                pass


        # écriture du vecteur
        ret_msg = ''
        try :
            ret_msg = vect_out.write(force=force, backup=backup)
            if len(ret_msg) > 0:
                logger.log(logging.AIDA, ret_msg)

        except (AIDA.AidaError, IOError, Exception) as e :
            logger.log(logging.AIDA, e)

            msg = f"{acqid} : échec à l'écriture du vecteur '{VO_name}'"
            ADC_error.critical(msg, stop=stop)

        else:
            if ret_msg == '' or ret_msg.startswith('---'):
                logger.info(f"{acqid} : écriture du vecteur '{VO_name}' OK")
            else:
                logger.warning(f"{acqid} : problème à l'écriture " +\
                               f"du vecteur '{VO_name}'")


if __name__ == '__main__':
    os.system('clear')

    import AIDA_logger
    logger = AIDA_logger.configure_AIDA_logging('adc')

    adc_opts  = dict()
    adc_opts['dev_nb'] = None

    acqid   = 'Tf230001'
    name    = 'tpr_sol90cm_f2_tn1_cal_%900'
    oper    = Oper(acqid=acqid, name=name, adc_opts=adc_opts)
    ni_name = oper.get_ni_name(name)
    print(f"ni_name = {ni_name}")

    acqid     = 'Tf210001'
    name      = 'flx_co2rm_mg_licor_Chb_%1800'

    for opt in [None, 1, 2]:
        adc_opts['dev_nb'] = opt
        oper = Oper(acqid=acqid, name=name, adc_opts=adc_opts)
        ni_name = oper.get_ni_name(name)
        print(f"adc_opts['dev_nb'] = {adc_opts['dev_nb']} => ni_name = {ni_name}")
