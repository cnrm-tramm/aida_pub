#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Gestion des opérateurs Python pour ADC.
"""

import sys
import os
import logging
import numpy  as np
import ctypes as ct
import re
import copy


logger = logging.getLogger('adc')


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA

import ADC_error
from   Oper    import Oper, Arg
from   Diag    import Diag
from   FVB2ADC import fvb2adc

# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


class Oper_arg(Arg):
    """ Gestion des arguments d'un opérateurs.
    """

    def __init__(self, **kwargs):
        """
            :param dict kwargs: dictionnaire de la description de
                                l'argument de l'opérateur.

            kwargs *doit* contenir :
                - une description de l'argument de l'opérateur (ex : issue de
                  oper.__init__::__desc_wrappers).
        """
        if not 'Id' in kwargs:
            ADC_error.critical("DEV : Oper_arg:__init__ : argument sans 'Id' ",
                               stop=True)

        self.Id        = kwargs.get('Id')
        self.direction = kwargs.get('direction')
        self.categorie = kwargs.get('categorie')

        del kwargs['Id']
        del kwargs['direction']
        del kwargs['categorie']

        if 'unit' in kwargs:
            self.unit = kwargs.get('unit')
            del kwargs['unit']

        if 'famille' in kwargs:
            self.famille = kwargs.get('famille')
            del kwargs['famille']


        if len(kwargs):
            ADC_error.critical( "DEV : Oper_arg:__init__ : il reste des " +\
                               f"choses dans kwargs : {kwargs}",
                               stop=True)


class Oper_PY(Oper):
    """ Classe de gestion des opérateurs Python.
    """
    def __init__(self, **kwargs):
        """
            :param dict   kwargs: dictionnaire de la description de l'opérateur.

            kwargs *doit* contenir :
                - une clé 'Nom' : nom de l'opérateur.
                - une description de l'opérateur (ex : issue de
                  oper.__init__::__desc_wrappers).
        """
        super().__init__()

        self.Nom             = kwargs.get('Nom')
        self.oper_ptr        = kwargs.get('oper_ptr')
        self.control_reftime = kwargs.get('control_reftime')
        self.misval_auto     = True if (kwargs.get('misval_auto', 1)) == 1 else False
        del kwargs['Nom']
        del kwargs['oper_ptr']
        del kwargs['control_reftime']

        # clés facultatives
        for key in ['repl_oper', 'repl_cause']:
            if key in kwargs:
                setattr(self, key, kwargs.get(key))
                del kwargs[key]

        self.Oper_args = {}
        for arg in kwargs.get('Args'):
            Id = arg['Id']
            self.Oper_args[Id] = Oper_arg(**arg)
        del kwargs['Args']

        if len(kwargs):
            ADC_error.critical( "DEV : Oper_PY:__init__ : il reste des " +\
                               f"choses dans kwargs : {kwargs}",
                               stop=True)


    def show_me(self, msg=None):
        """ Debug...
        """
        if msg:
            print(f'Oper_PY::show_me : {msg}')

        max_len = max( (len(key) for key in self.__dict__.keys()) )
        for key, value in self.__dict__.items():
            if key == "Nom":
                print(f'- opérateur : {self.Nom}')
            elif key != "Oper_args":
                print(f'  - {key:{max_len}s} = {value}')
            else:
                for i, (arg_name, arg_value) in enumerate(self.Oper_args.items()):
                    print(f'  - Oper_args[{i}] :')
                    arg_value.show_me()


    def cleanup(self):
        """ Nettoye l'opérateur de tous les attributs qui ont été ajoutés
            pour une exécution (en particulier les attribut header, arg_brut,
            data qui ont été ajoutés aux arguments de l'opérateur).
        """
        logger.log(logging.RUN, f"cleanup")

        for i, arg_car in enumerate(self.Arg_Cars):
            for attr in ['header', 'arg_brut', 'data']:
                if hasattr(arg_car, attr):
                    delattr(arg_car, attr)

        return


    def get_all_DIR_IN(self):
        """ Yield les Oper_args dont la direction est DIR_IN.
        """
        for arg in self.Oper_args.values():
            if arg.direction == 'DIR_IN':
                yield arg


    def get_all_DIR_OUT(self):
        """ Yield les Oper_args dont la direction est DIR_OUT.
        """
        for arg in self.Oper_args.values():
            if arg.direction == 'DIR_OUT':
                yield arg


    def get_categorie_direction(self, categorie, direction):
        """ Yield les Oper_args dont la catégorie est 'categorie' et la
            direction 'direction' ainsi que leur indice dans la description
            des arguments (self.Oper_args).

            :param str() categorie: categorie à chercher
                                    ['VECTOR', 'COEFFICIENT']
            :param str() direction: direction à chercher
                                    ['DIR_IN', 'DIR_OUT']

            :return: generator
            :rtype : yield
        """
        for i, arg in enumerate(self.Oper_args.values()):
            if arg.categorie == categorie  and \
               arg.direction == direction      :
                yield i, arg


    def get_VECTOR_DIR_IN(self):
        """ Yield les Oper_args dont la catégorie est VECTOR et la direction
            est DIR_IN ainsi que leur indice dans la description des arguments
            (self.Oper_args).
        """
        return self.get_categorie_direction('VECTOR', 'DIR_IN')


    def get_VECTOR_DIR_OUT(self):
        """ Yield les Oper_args dont la catégorie est VECTOR et la direction
            est DIR_OUT ainsi que leur indice dans la description des arguments
            (self.Oper_args).
        """
        return self.get_categorie_direction('VECTOR', 'DIR_OUT')


    def get_COEFFICIENT_DIR_IN(self):
        """ Yield les Oper_args dont la catégorie est COEFFICIENT et la direction
            est DIR_IN ainsi que leur indice dans la description des arguments
            (self.Oper_args).
        """
        return self.get_categorie_direction('COEFFICIENT', 'DIR_IN')


    def get_COEFFICIENT_DIR_OUT(self):
        """ Yield les Oper_args dont la catégorie est COEFFICIENT et la direction
            est DIR_OUT ainsi que leur indice dans la description des arguments
            (self.Oper_args).

            NOTE : à ce jour, ce type de coef n'est pas utilisé...
        """
        return self.get_categorie_direction('COEFFICIENT', 'DIR_OUT')


    def compute_dollar_Acq(self, in_str):
        """ Retourne la valeur correspondante à 'in_str' après
            remplacement de *$Acq.$date.DOY* (in_str pourrait contenir :
            $Acq.$date.DOY*500)

            :param str() in_str: chaine débuttant par '$Acq_" à _remplacer_

            :return: si tout va bien, l'évaluation de la valeur trouvée
                     sinon in_str
        """
        if not isinstance(in_str, str):
            return in_str

        if not '$Acq.$date.DOY' in in_str:
            return in_str

        logger.log(logging.RUN, f"compute_dollar_Acq : in_str = '{in_str}'")

        in_str = in_str.replace('"', '')

        doy = self.replace_dollar_Acq('$Acq.$date.DOY')
        in_str = in_str.replace('$Acq.$date.DOY', str(doy))
        val = eval(in_str)

        logger.debug(f"compute_dollar_Acq : return val = {val}")

        return val


    def compute_dollar_Chrono(self, in_str):
        """ Retourne la valeur correspondante à 'in_str' après
            remplacement de *$Chrono* (in_str pourrait contenir :
            $Chrono*500)

            :param str() in_str: chaine débuttant par '$Chrono" à _remplacer_

            :return: si tout va bien, l'évaluation de la valeur trouvée
                     sinon in_str
        """
        logger.log(logging.RUN, f"compute_dollar_Chrono : in_str = '{in_str}'")

        if not isinstance(in_str, str):
            return in_str

        if not '$Chrono' in in_str:
            return in_str

        in_str = in_str.replace('"', '')

        # récupérer seulement la partie $Chrono.xxx dans in_str
        chrono_parts = self.get_dollar_parts(in_str)
        if len(chrono_parts) > 1:
            raise Exception(f"compute_dollar_Chrono : ne sait pas traiter : " +\
                            f"'{in_str}' : ")
        chrono_part = list(chrono_parts)[0]

        chrono = self.replace_dollar_Chrono(chrono_part)
        in_str = in_str.replace(chrono_part, str(chrono))
        val = eval(in_str)

        logger.debug(f"compute_dollar_Chrono : return val = {val}")

        return val


    def replace_dollar_Arg(self, in_arg):
        """ Retourne la valeur correspondante à 'in_arg' après remplacement de
            la variable de type '$Arg'.
            ('in_arg' est une chaine qui ne contient *que* la variable $Argxxx)

            :param str() in_arg: chaine débuttant par '$Arg_" à _remplacer_

            :return: si tout va bien, la valeur trouvée...

            NOTE : il n'était pas prévu que l'on puisse trouver des $Arg dans
                   les appels d'opérateurs python.
                   => le codage du remplacement de $Arg risque de ne pas être
                      très robuste...
        """
        logger.log(logging.RUN, f"replace_dollar_Arg : in_arg = {in_arg}")

        pattern = r'\$Arg(?P<number>\d+)(\.(?P<attribut>[a-zA-Z_]+))?'
        match = re.search(pattern, in_arg)
        if not match:
            raise Exception (f"replace_dollar_Arg : erreur de syntaxe : '{in_arg}'")

        number   = int(match.group('number')) - 1
        attribut = match.group('attribut')

        if number < 0:
            raise Exception (f"Oper_PY::replace_dollar_Arg : erreur de numérotation : '{in_arg}'")

        # il faut pouvoir accéder au Oper_args par numéro
        list_Oper_args = list(self.Oper_args.items()) # tuple('key', 'value')
        the_oper_arg   = list_Oper_args[number]

        if not hasattr(the_oper_arg[1], 'header'): # # la partie 'value' du tuple
            raise Exception (f"Oper_PY::replace_dollar_Arg : erreur de numérotation : '{in_arg.split('.')[0]}' utilisé trop tôt ou n'est pas un vecteur")

        the_header     = the_oper_arg[1].header # la partie 'value' du tuple
        the_name       = the_header['#hdr_name']

        if not attribut:
            return the_name
        elif attribut in the_header.keys():
            value = the_header[attribut]

            if value == '' and attribut == 'name':
                return 'la variable ' + the_name
            elif value == '' and attribut == 'english_name':
                return 'the variable named ' + the_name

            return the_header[attribut]

        # traitement spéciaux pour certaines valeurs de attribut si attribut
        # n'est pas dans le header du paramètre.
        elif attribut == 'name':
            return 'la variable ' + the_name
        elif attribut == 'english_name':
            return 'the variable named ' + the_name
        # rien compris à type_sample et type_ech, mais de toutes les façons :
        # - type_sample n'appartient pas au header
        # - type_ech appartient au header :
        #   -- n'est obligatoire que pour les vecteurs temps
        #   -- n'est pas géré selon la norme refman.pdf par FVB
        # => ce champ n'est pas géré par ADC
        elif attribut == 'type_sample':
            attribut = 'type_ech'
            if attribut in the_header.keys():
                return the_header[attribut]
            else:
                logger.debug(f"Oper_PY:replace_dollar_Arg : '{in_arg}' : " +\
                              "ne trouve ni 'type_sample' ni 'type_ech' -> ''")
                return ''
        elif attribut == 'sample':
            attribut = 'freq_ech'
            if attribut in the_header.keys():
                return the_header[attribut]
            else:
                logger.warning("ne trouve ni 'sample' ni 'freq_ech' : que faut-il retourner ?")
        elif attribut == 'nom':
            return the_name

        elif attribut == 'array_dim':
            attribut = 'dim_array'
            if attribut in the_.header:
                return the_header[attribut]
            else:
                logger.debug(f"Oper_PY:replace_dollar_Arg : '{in_arg}' : " +\
                              "ne trouve ni 'array_dim' ni 'dim_array' -> '1'")
                return '1'


        logger.warning(f"Oper_PY::replace_dollar_Arg : non trouvé : {in_arg}")
        return ''


    def replace_dollar(self, in_arg):
        """ Retourne la valeur d'une variable de type $xxx.
        """
        if not isinstance(in_arg, str):
            return in_arg

        if not '$' in in_arg:
            return in_arg

        logger.log(logging.RUN, f"replace_dollar : in_arg = {in_arg}")
        if '$Arg' in in_arg:
            return self.replace_dollar_Arg(in_arg)
        elif '$Acq' in in_arg:
            return self.compute_dollar_Acq(in_arg)
        elif '$Chrono' in in_arg:
            return self.compute_dollar_Chrono(in_arg)
        else:
            raise Exception (f"paramètre inattendu : '{in_arg}'")


    def replace_multi_dollar(self, in_str):
        """ Retourne la chaine correspondante à 'in_str' après remplacement de
            *toutes* les variables de type '$Arg'.

            :return: str()
        """
        if not isinstance(in_str, str):
            return str(in_str)

        dollar_parts = self.get_dollar_parts(in_str)
        for dollar_part in dollar_parts:
            # si $ArgX.sample : chercher d'abord $ArgX.freq_ech et seulement
            # à défaut, chercher ArgX.sample.
            if dollar_part.endswith('.sample'):
                dollar_freq_ech = dollar_part.replace('.sample', '.freq_ech')
                real_value = self.replace_dollar(dollar_freq_ech)
                if real_value == '':
                    real_value = self.replace_dollar(dollar_part)
            else:
                real_value = self.replace_dollar(dollar_part)

            # peut-ête un peu brutal... (il faudrait regarder le type)
            if isinstance(real_value, str) and real_value.lower() == 'nan':
                real_value = 'np.nan'

            # remplacement dans la string d'entrée
            in_str = in_str.replace(dollar_part, str(real_value))

        # TODO : il faudrait peut-être ajouter dans le dictionnaire 'desc_oper'
        #      : pour un argument de type COEFFICIENT, une clé facultatitive
        #      : 'type' précisant le type attendu de l'argument. Par défaut, le
        #      : type attendu serait 'float'. Si la fonction d'interface attend
        #      : une chaine, la descption du COEFFICIENT serait :'type': str
        # on ne connait pas le type de retour attendu
        # => si on ne peut pas évaluer l'argument, on retourne une sting...
        try:
            ret = eval(in_str)
        except Exception as e:
            ret = in_str
        return ret



    def get_call_args(self, acqid, args_brut):
        """ Prépare les arguments pour l'appel de wrap_xxx.

            ATTENTION : self va être modifié => self doit être une *deepcopy*
                        de la description de l'opérateur.

            :param str()   acqid    : acqid pour lequel appliquer l'instruction.
            :param list()  args_brut: arguments                de l'instruction.

            :return: P_in, P_out, reftimes
            - P_in     : liste des data des VECTOR/DIR_IN
            - P_out    : liste des dictionnaires (Id et header) pour
                         les VECTOR/DIR_OUT
            - reftimes : liste des champ 'ref_time' des VECTOR/DIR_IN
                         (utilisé pour le controle de vecteur temps)
        """
        logger.log(logging.RUN, "get_call_args")

        P_in     = list()
        P_out    = list()
        reftimes = list()

        # lecture des VECTOR / DIR_IN
        for arg_nb, arg in self.get_VECTOR_DIR_IN():
            # certains tests n'ont pas à être fait sur les vecteurs temps
            time_vector = False

            # cas où le paramètre fournit n'est pas une string...
            if not isinstance(args_brut[arg_nb], str):
                raise Exception(f"'{args_brut[arg_nb]}' : " +\
                                 "n'est pas un nom de vecteur")

            # cas où le paramètre fournit commence par $Chrono
            # - problème de "
            if args_brut[arg_nb].startswith('"$Chrono'):
                args_brut[arg_nb] = args_brut[arg_nb].strip('"')

            # - récupérer la valeur du Chrono
            if args_brut[arg_nb].startswith('$Chrono'):
                args_brut[arg_nb] = self.replace_dollar_Chrono(args_brut[arg_nb])

            # versionning
            ni_name = self.get_ni_name(args_brut[arg_nb])
            try:
                VI = AIDA.VectorMask(acqid, ni_name)
                VI.header_utf_8()
            except Exception as e:
                raise Exception(f"'{args_brut[arg_nb]}' : " +\
                                 "problème à la lecture du vecteur")

            # peut-être un peu succinct
            if ni_name.startswith('rft_') or ni_name.startswith('time'):
                time_vector = True

            # les fonctions d'interfaces font :
            #    - X_out['misval'] = f"{X_in_header['misval']}
            # => ajouter un misval cohérent si le champ est absent ou vide
            #    (surtout  pour les très anciens vecteurs)
            if not time_vector:
                if not 'misval' in VI.attributes.keys():
                    misval = self.get_default_misval(VI.attributes)
                    logger.warning(f"Oper_PY::get_call_args: " +\
                                   f"vecteur sans misval ({ni_name}) " +\
                                   f"=> forcé à {misval}")
                    VI.attributes['misval'] = misval
                elif not VI.attributes.get('misval', None):
                    misval = self.get_default_misval(VI.attributes)
                    logger.warning(f"Oper_PY::get_call_args: " +\
                                   f"vecteur avec misval vide ({ni_name}) " +\
                                   f"=> forcé à {misval}")
                    VI.attributes['misval'] = misval

            # pour le controle de la compatibilité des reftimes
            if self.control_reftime:
                rft = self.get_ref_time(VI.attributes)
                if rft:
                    reftimes.append(rft)

            # control de la famille
            if not time_vector:
                self.do_control_famille(args_brut[arg_nb], arg, VI.attributes)

            # conversion automatique d'unité
            # l'unité des vecteurs temps est souvent omise
            # => forcer à 's' si besoin
            if (not 'unit' in VI.attributes.keys()) and \
               (args_brut[arg_nb].startswith('rft')):
                VI.attributes['unit'] = 's'
            if hasattr(arg, 'unit') and VI.attributes['unit'] != arg.unit:
                Oper.convert_to_unit(args_brut[arg_nb], VI.data.data,
                                     VI.attributes['unit'], arg.unit)

            P_in.insert(arg_nb, VI)

            # ATTENTION : ajout à la description de cet argument son arg_brut
            # (le nom reçu dans la commande .fil), de son header, ses data...
            arg.arg_brut = args_brut[arg_nb]
            arg.header   = VI.attributes
            arg.data     = VI.data

        # traitement des COEFFICIENT / DIR_IN
        for arg_nb, arg in self.get_COEFFICIENT_DIR_IN():
            # supprimer les " dans les coef string (ici ils valent '"xxx"')
            if isinstance(args_brut[arg_nb], str) and \
               args_brut[arg_nb][0] == '"' and args_brut[arg_nb][-1] == '"':
                args_brut[arg_nb] = args_brut[arg_nb][1:-1]


            # cas où le paramètre fournit commence par $Acq
            args_brut[arg_nb] = self.compute_dollar_Acq(args_brut[arg_nb])

            # cas où le paramètre fournit commence par $Chrono
            if isinstance(args_brut[arg_nb], str) and \
               args_brut[arg_nb].startswith('$Chrono'):
                args_brut[arg_nb] = self.compute_dollar_Chrono(args_brut[arg_nb])

            # cas où le paramètre fournit contient $Arg
            if isinstance(args_brut[arg_nb], str) and \
               '$Arg' in args_brut[arg_nb]:
                args_brut[arg_nb] = self.replace_multi_dollar(args_brut[arg_nb])

            P_in.insert(arg_nb, args_brut[arg_nb])

        # noms de vecteurs de sortie VECTOR / DIR_OUT
        for i, (arg_nb, arg) in enumerate(self.get_VECTOR_DIR_OUT()):
            P_out.insert(i, {'Id':args_brut[arg_nb]})

            # ATTENTION : ajout à la description de cet argument son arg_brut
            arg.arg_brut = args_brut[arg_nb]

        return P_in, P_out, reftimes


    def exec_line(self, acqid, args_brut, args_opt):
        """ Excécute la ligne d'instruction ADC reçue :
            - prépare les arguments pour l'appel de l'opérateur
            - appelle l'opérateur OP_xxx
            - écrit les vecteurs de sortie

            :param str()   acqid    : acqid pour lequel appliquer l'instruction.
            :param list()  args_brut: arguments             de l'instruction.
            :param dict()  args_opt : arguments optionnels  de l'instruction.
        """
        logger.log(logging.RUN, "exec_line")

        logger.debug(f"{self.Nom} : opérateur PY : " +
                     f"control_reftime = {self.control_reftime}")

        if len(args_brut) > len(self.Oper_args):
            logger.debug(f"{self.Nom} : " +\
                          "trop de paramètres => tentative appel FVB -> appel ADC")
            # tenter une transformation des apppels FVB en appels ADC
            if self.Nom in fvb2adc:
                for arg_nb in reversed(fvb2adc[self.Nom]):
                    del args_brut[arg_nb]

                # cas des opérateurs mixtes : il peut rester des $Arg dans les
                # paramètres d'entrée. Ex :
                #   MoyEch_tps_bnds(..., 0.5*$Arg1.sample,...)
                ## NOTE : le 26 sept 2023 : les opérateurs Python peuvent à
                ## présent recevoir des COEFFICIENT sous la forme $Arg.
                ## => suppression du test suivant
                ##for arg in args_brut:
                ##    if isinstance(arg, str) and '$Arg' in arg:
                ##        raise Exception(f"'{arg}' : instruction incompatible avec ADC")

        if len(self.Oper_args) != len(args_brut):
            raise Exception ( "nombre de paramètre incorrect : attendu = " +\
                             f"{len(self.Oper_args)} <-> reçu = {len(args_brut)}")


        # enregistrement d'information dans l'opérateur
        self.acqid    = acqid
        self.path     = AIDA.ID_to_datapath(self.acqid)
        self.pltf     = AIDA.AIDA_abrev_to_plt(acqid[0:2])

        # traitement des arguments et ajout d'attribut aux Oper_args
        P_in, P_out, reftimes = self.get_call_args(acqid, args_brut)
        output_names = [ out['Id'] for out in P_out ]

        # controles avant le lancement de l'opérateur
        if not self.check_before_call(reftimes, output_names):
            return


        # excécution de l'opérateur
        # =========================
        logger.log(logging.RUN, "appel de l'opérateur")
        try:
            if args_opt:
                r_headers, r_data, diag_out = self.oper_ptr(*tuple(P_in), **args_opt)
            else:
                r_headers, r_data, diag_out = self.oper_ptr(*tuple(P_in))
        except Exception as e:
            raise Exception(e)

        # gestion du diagnostique
        diag = Diag(**diag_out)

        # vérification du code de retour
        if hasattr(diag, 'CodeRet'):
            if diag.CodeRet != 0:
                ADC_error.critical(f"{self.Nom} : CodeRet != 0 " +\
                                    "=> les vecteurs de sortie ne sont pas écrits",
                                   stop=True)
                return
        else:
            ADC_error.critical(f"{self.Nom} : ne retourne pas de CodeRet !!!" +\
                                    "=> les vecteurs de sortie de sont pas écrits",
                                   stop=True)
            return

        # finalisation des headers
        for i, (arg_nb, arg) in enumerate(self.get_VECTOR_DIR_OUT()):
            r_headers[i]['fct_origine'] = self.line_cmd
            r_headers[i]['fct_comment'] = diag.DiagExec

        # écriture des output
        for i, (arg_nb, arg) in enumerate(self.get_VECTOR_DIR_OUT()):
            VO_name   = arg.arg_brut
            VO_header = r_headers[i]
            VO_data   = r_data[i]
            super().write_vect(acqid, i, VO_name, VO_header, VO_data)

        return


    def exec_line_no_write(self, acqid, args_brut, args_opt):
        """ Excécute la ligne d'instruction ADC reçue SANS écriture sur disque.
            Cette méthode est une simplifiaction de la méthode 'exec_line'
            appelable par AITO par exemple.

            Retourne :
            - un code de retour : 1 en  cas d'erreur ou le code de retoure
              de l'opérateur (0 = ok).
            - un message de diagnostique ou le message de diagnostique de
              l'opérateur
            - None ou les données calculées par l'opérateur
        """
        logger.log(logging.RUN, "exec_line_no_write")

        logger.debug(f"{self.Nom} : opérateur PY : " +
                     f"control_reftime = {self.control_reftime}")

        if len(args_brut) > len(self.Oper_args):
            logger.debug(f"{self.Nom} : " +\
                          "trop de paramètres => tentative appel FVB -> appel ADC")
            # tenter une transformation des apppels FVB en appels ADC
            if self.Nom in fvb2adc:
                for arg_nb in reversed(fvb2adc[self.Nom]):
                    del args_brut[arg_nb]

                # cas des opérateurs mixtes : il peut rester des $Arg dans les
                # paramètres d'entrée. Ex :
                #   MoyEch_tps_bnds(..., 0.5*$Arg1.sample,...)
                ## NOTE : le 26 sept 2023 : les opérateurs Python peuvent à
                ## présent recevoir des COEFFICIENT sous la forme $Arg.
                ## => suppression du test suivant
                ##for arg in args_brut:
                ##    if isinstance(arg, str) and '$Arg' in arg:
                ##        raise Exception(f"'{arg}' : instruction incompatible avec ADC")

        if len(self.Oper_args) != len(args_brut):
            raise Exception ( "nombre de paramètre incorrect : attendu = " +\
                             f"{len(self.Oper_args)} <-> reçu = {len(args_brut)}")


        # enregistrement d'information dans l'opérateur
        self.acqid    = acqid
        self.path     = AIDA.ID_to_datapath(self.acqid)
        self.pltf     = AIDA.AIDA_abrev_to_plt(acqid[0:2])

        # traitement des arguments et ajout d'attribut aux Oper_args
        P_in, P_out, reftimes = self.get_call_args(acqid, args_brut)
        output_names = [ out['Id'] for out in P_out ]

        # controles avant le lancement de l'opérateur
        # (les dorits d'écriture sont vérifiés...)
        if not self.check_before_call(reftimes, output_names):
            msg = "'rft_time' incompatibles ou problèmes de droits"
            return 1, msg, None


        # excécution de l'opérateur
        # =========================
        logger.log(logging.RUN, "appel de l'opérateur")
        try:
            if args_opt:
                r_headers, r_data, diag_out = self.oper_ptr(*tuple(P_in), **args_opt)
            else:
                r_headers, r_data, diag_out = self.oper_ptr(*tuple(P_in))
        except Exception as e:
            raise Exception(e)

        # gestion du diagnostique
        diag = Diag(**diag_out)

        return diag.CodeRet, diag.DiagExec, r_data


def init_opers_PY(desc):
    """ Yield tous les Oper_PY décris dans le dictionnaire de description
        passé en argument. Typiquement, le dictionnaire de description est :
            `oper.__init__::__desc_wrappers'.

        :param dict() desc: dictionnaire de description des opérateurs Python.
    """
    logger.log(logging.RUN, "init_opers_PY")

    for oper_name, oper_desc in desc.items():

        for arg in oper_desc['Args']:
            if arg['categorie'] == 'VECTOR_IN':
                arg['categorie'] = 'VECTOR'
                arg['direction'] = 'DIR_IN'

            elif arg['categorie'] == 'VECTOR_OUT':
                arg['categorie'] = 'VECTOR'
                arg['direction'] = 'DIR_OUT'

            elif arg['categorie'] == 'COEFFICIENT':
                arg['categorie'] = 'COEFFICIENT'
                arg['direction'] = 'DIR_IN'

        yield Oper_PY(Nom=oper_name, **oper_desc)


if __name__ == '__main__':
    os.system('clear')

    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

    # création des niveaux de log 'AIDA', 'ADC'...
    logging.RUN  = 15   # DEBUG = 10
    logging.AIDA = 25   # INFO  = 20


    import oper
    from fct_messages import wait_user
    import pprint



    # description de tous les opérateurs Python
    print("\n* Récupération de la description des opérateurs PYTHON")
    desc_opers_PY = oper.__desc_opers
    wait_user()


    oper_name = 'PressAltiVect'
    print(f"\n* Récupération de la description de l'opérateur : {oper_name}")
    desc_mon_oper_PY = desc_opers_PY[oper_name]
    #print(f"  - desc_mon_oper_PY = {desc_mon_oper_PY}")
    print(f"  - desc_mon_oper_PY :")
    pprint.pprint(desc_mon_oper_PY)
    wait_user()

    print("\n================================================")
    print(f"* Création de tous les Oper_PY")
    opers_PY = { oper.Nom: oper for oper in init_opers_PY(desc_opers_PY) }
    print("** opers_PY :")
    nb = len(opers_PY)
    for i, (oper_py_name, oper_py_desc) in enumerate(opers_PY.items(), start=1):
        print(f"\n* 'oper {i}/{nb}: {oper_py_name} :")
        oper_py_desc.show_me()
        wait_user()


    print("\n================================================")
    oper_name = 'PressAltiVect'
    print(f"\n* Visualisation de l'opérateur '{oper_name}'")
    mon_oper_PY = opers_PY[oper_name]
    mon_oper_PY.show_me()
    wait_user()

    print(f"\n* Récupération des Oper_args de type DIR_IN")
    for i, arg in enumerate(mon_oper_PY.get_all_DIR_IN()):
        print(f"  - Oper_args[{i}]")
        arg.show_me()
        print()
    wait_user()

    print(f"\n* Récupération des Oper_args de type DIR_OUT")
    for i, arg in enumerate(mon_oper_PY.get_all_DIR_OUT()):
        print(f"  - Oper_args[{i}]")
        arg.show_me()
        print()
    wait_user()


    print(f"\n* Récupération des Oper_args de type VECTOR / DIR_IN")
    for arg_nb, arg in mon_oper_PY.get_VECTOR_DIR_IN():
        print(f"  - Oper_args[{arg_nb}]")
        arg.show_me()
        print()
    wait_user()

    print(f"\n* Récupération des Oper_args de type VECTOR / DIR_OUT")
    for arg_nb, arg in mon_oper_PY.get_VECTOR_DIR_OUT():
        print(f"  - Oper_args[{arg_nb}]")
        arg.show_me()
        print()
    wait_user()

    print(f"\n* Récupération des Oper_args de type COEFFIECIENT / DIR_IN")
    for arg_nb, arg in mon_oper_PY.get_COEFFICIENT_DIR_IN():
        print(f"  - Oper_args[{arg_nb}]")
        arg.show_me()
        print()
    wait_user()

    print(f"\n* Récupération des Oper_args de type COEFFIECIENT / DIR_OUT")
    for arg_nb, arg in mon_oper_PY.get_COEFFICIENT_DIR_OUT():
        print(f"  - Oper_args[{arg_nb}]")
        arg.show_me()
        print()
    wait_user()

