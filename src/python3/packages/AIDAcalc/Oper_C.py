#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Gestion des opérateurs C pour ADC.
"""

import sys
import os
import logging
import numpy  as np
import ctypes as ct
from   ctypes import util
import re
import copy


logger = logging.getLogger('adc')


PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
import Units
from   Misval import AIDA_type_misval as AIDA_type_misval

import ADC_error
from   ADC_rapport import ADC_Rapport as Rapport
from   Oper import Oper, Arg


# des types pour simplfier les expressions
c_float_p  = ct.POINTER(ct.c_float)

# libc (pour pouvoir flusher stdin et stdout après l'appel d'un opérateur C)
libc_file = ct.util.find_library('c')
libc = ct.CDLL(libc_file)


# Meta_Out variable globale de liboper.so)
import Meta_Out
meta_out = Meta_Out.Meta_Out()

# liste des opérateurs pur-C qui utilisent la variable Meta_Out
use_Meta_Out = ['Cre_time_bnds_reg']

# opérateur pour lesquels il faut positionner 'control_reftime' à off
# (cf. document de référence de William...)
control_reftimes = ['async_to_regul'        ,
                    'Ech_tps_impos'         ,
                    'Ech_tps_impos_tab'     ,
                    'Interpol_irreg'        ,
                    'Interpol_irreg_mnq'    ,
                    'MaxEch_tps_impos'      ,
                    'MedEch_tps_impos'      ,
                    'MinEch_tps_impos'      ,
                    'MoyEch_tps_impos'      ,
                    'MoyEch_tps_impos_dbl'  ,
                    'MoyHarmEch_tps_impos'  ,
                   ]


# concernant ce programme
__version__ = "1.0.0"
me = os.path.split(sys.argv[0])[1]


def sample_to_str(sample):
    """ Retourne sample sous la forme qui va bien :
        - '%1/sample' : pour sample < 0
        - 'sample'    : pour sample > 0

        :param str() sample: valeur de sample

        :return: '%1/sample' ou 'sample'
        :rtype : str()
    """
    try:
        x    = float(eval(sample))
        if x > 0.0 and x < 0.75:
            freq = int( np.floor( (1.0 / x) + 0.5) )
            return f"%{freq}"
        else:
            return f"{int(x)}"
    except Exception as e:
        ADC_error.critical(f"sample_to_str : {e}", stop=True)


class Arg_Car(Arg):
    """ Gestion des Arg_Car d'un opérateur.
        (<=> Arg_Car de FVB).
    """

    # méthodes de classe
    @classmethod
    def get_ptr_VI(cls, x):
        """ Retourne un ctypes pointer sur x pour un VECTOR / DIR_IN.

            :param numpy.array    x      : data pour le VECTOR/DIR_IN
        """
        return ct.c_char_p(x.data.tobytes())


    @classmethod
    def get_ptr_VO(cls, x, ct_type):
        """ Retourne un ctypes pointer sur x pour un VECTOR / DIR_OUT.

            :param numpy.array    x      : data pour le VECTOR/DIR_OUT
            :param ctypes.POINTER ct_type: ex : ct.POINTER(ct.c_float)
        """
        return x.ctypes.data_as(ct_type)


    @classmethod
    def get_ptr_CI_array(cls, x, numpy_format):
        """ Retourne un ctypes pointer sur x pour un COEFFICIENT / DIR_IN de
            type list().
            (on fait comme pour get_ptr_VI())

            :param x            : coefficient de type liste
                                : numpy format de la liste des coefficients
            :param numpy_format : coefficient de type liste
        """
        # passer la liste des coef en numpy array
        n = np.array(x, dtype=numpy_format)
        return ct.c_char_p(n.data.tobytes())


    @classmethod
    def get_ptr_CI(cls, x, aida_type):
        """ Retourne un ctypes pointer sur x pour un COEFFICIENT / DIR_IN.

            :param           x         : valeur du coefficient.
            :param AIDA_type aida_type : une clé de Misval.AIDA_type_misval.
        """
        if not aida_type in AIDA_type_misval.keys():
            ADC_error.critical( "DEV : Arg_Car:get_ptr_CI : traiter " +\
                               f"aida_type = '{aida_type}'", stop=True)

        if aida_type == 'Ieeefloat_32'  or aida_type == 'Hpfloat_32':
            return ct.pointer(ct.c_float (float(x)))
        if aida_type == 'Ieeefloat_64':
            return ct.pointer(ct.c_double (float(x)))
        if aida_type == 'Int_16':
            return ct.pointer(ct.c_short (int(x)))
        if aida_type == 'Int_32':
            return ct.pointer(ct.c_int ( int(float(x)) ))
        if aida_type == 'U_Int_8':
            return ct.pointer(ct.c_ubyte (int(x)))
        if aida_type == 'U_Int_16':
            return ct.pointer(ct.c_ushort (int(x)))
        if aida_type == 'U_Int_32':
            return ct.pointer(ct.c_uint (int(x)))
        if aida_type == 'U_Int_64':
            return ct.pointer(ct.c_long ( int(x) ))
        if aida_type == 'String':
            return ct.c_char_p (bytes(str(x), encoding='iso8859-15'))

        ADC_error.critical( "DEV : Arg_Car:get_ptr_CI : traiter " +\
                           f"aida_type = '{aida_type}'", stop=True)


    def __init__(self, **kwargs):
        """
            :param dict kwargs: dictionnaire de la description de
                                l'argument de l'opérateur.


            kwargs *doit* contenir :
                -  une description de l'argument de l'opérateur (ex : issue de
                   oper_API_PY_desc.oper_API_PY_desc).
        """
        self.direction   = kwargs.get('direction'                  )
        self.categorie   = kwargs.get('categorie'                  )
        self.typ         = kwargs.get('typ'                        )
        self.array_dim   = kwargs.get('array_dim'  , '1'           )
        self.array_shape = kwargs.get('array_shape', self.array_dim)
        self.bornes      = kwargs.get('bornes'                     )
        self.unit_bornes = kwargs.get('unit_bornes'                )
        self.unite       = kwargs.get('unite'                      )
        self.name        = kwargs.get('name'                       )
        self.en_name     = kwargs.get('en_name'                    )
        self.type_sample = kwargs.get('type_sample'                )
        self.sample      = kwargs.get('sample'                     )
        self.ref_time    = kwargs.get('ref_time'                   )
        self.time_bnds   = kwargs.get('time_bnds'                  )
        self.famille     = kwargs.get('famille'                    )
        self.misval      = kwargs.get('misval'                     )
        self.NbVal       = kwargs.get('NbVal'                      )

        # valider l'unité passée
        if self.categorie == 'VECTOR':
            if len(self.unite) == 0 or self.unite == 'any':
                logger.debug(f"  - {self.direction}  : suppression de " +\
                             f"l'unité reçue : '{self.unite}'...")
                del self.unite
            elif self.unite == 'unknown':
                if self.direction == 'DIR_IN':
                    logger.debug(f"  - {self.direction}  : suppression de " +\
                                 f"l'unité reçue : '{self.unite}'...")
                    del self.unite
                else:   # DIR_OUT
                    logger.debug(f"  - {self.direction} : " +\
                                 f"self.unite = {self.unite} : " +\
                                  "ne devrait pas exister")

            else:
                try:
                    s = Units.get_AIDA_unit(self.unite)
                except Exception as e:
                    ADC_error.critical(f"Oper_C::Arg_Car::__init__ : {e}",
                                       stop=True)

                if s == '':
                    logger.debug(f"  - {self.direction}  : suppression de " +\
                                 f"l'unité reçue : '{self.unite}'...")
                    del self.unite
                # pas la peine de mémoriser l'unité normalisée
                #else:
                #    self.unite = s


            # misval
            # NOTE : certains vecteurs n'ont pas de champ 'misval' mais
            # certains opérateurs sont appelés avec l'argument $ArgX.misval
            # => ajouté systématiquement un 'misval' aux vecteurs lus.
            if self.misval == None:
                if not self.typ in AIDA_type_misval.keys():
                    ADC_error.critical( "DEV : Arg_Car:__init__ : traiter " +\
                                       f"self.typ = '{typ}'", stop=True)
                else:
                    self.misval = 'nan'
                    logger.debug( "  - Arg_Car::__init__ : " +\
                                 f"positionnement de misval = {self.misval}")

        # nettoyer la famille des '"' surnuméraires...
        if self.famille:
            self.famille = self.famille.strip('"')

        # ajout des formats binding, numpy...
        Format_bind,  \
        Format_numpy, \
        Numpy_itemsize = self.get_formats(self.typ, self.categorie, self.direction)

        self.Format_bind    = Format_bind
        self.Format_numpy   = Format_numpy
        self.Numpy_itemsize = Numpy_itemsize


    def get_formats(self, typ, categorie, direction):
        """ Retourne 3 valeurs :
                Format_bind, Format_numpy, Numpy.itemsize
            correspondant à typ, categorie et direction.
        """
        Format_bind    = None
        Format_numpy   = None
        Numpy_itemsize = None

        # récupérer la conversion en format numpy selon AIDA
        if typ == "String":
            Format_numpy   = AIDA.np_string(typ, dimension=4)
        else:
            Format_numpy   = AIDA.np_string(typ)

        Numpy_itemsize = np.dtype(Format_numpy).itemsize

        # ajouter la méthode de conversion des arguments pour ctypes
        if not typ in AIDA_type_misval.keys():
            ADC_error.critical( "DEV : Arg_Car:get_formats : traiter " +\
                               f"typ = '{typ}'", stop=True)

        if (categorie == 'VECTOR' and direction == 'DIR_IN'):
            Format_bind = Arg_Car.get_ptr_VI

        elif (categorie == 'VECTOR' and direction == 'DIR_OUT'):
            Format_bind = Arg_Car.get_ptr_VO

        elif (categorie == 'COEFFICIENT' and direction == 'DIR_IN'):
            if self.array_dim == '1':
                Format_bind = Arg_Car.get_ptr_CI
            else:
                Format_bind = Arg_Car.get_ptr_CI_array

        else:
            Format_bind = 'UNEXPECTED'

        return Format_bind, Format_numpy, Numpy_itemsize


class Oper_C(Oper):
    """ Classe de gestion des opérateurs C.
    """
    def __init__(self, **kwargs):
        """
            :param dict   kwargs: dictionnaire de la description de l'opérateur.

            kwargs *doit* contenir :
                - une clé 'Nom' : nom de l'opérateur.
                - une description issue de oper_API_PY_desc.oper_API_PY_desc.
        """
        super().__init__()

        self.Nom             = kwargs.get('Nom')
        self.type            = kwargs.get('type')
        self.control_reftime = kwargs.get('control_reftime')
        self.repl_oper       = kwargs.get('repl_oper')
        self.repl_cause      = kwargs.get('repl_cause')
        self.misval_auto     = True if (kwargs.get('misval_auto', 1)) == 1 else False
        self.NbArg           = kwargs.get('NbArg')

        self.Arg_Cars    = []
        for i, arg_car in enumerate(kwargs.get('Arg_Cars')):
            self.Arg_Cars.append(Arg_Car(**arg_car))

        self.OP_fct_name = f'OP_{self.Nom}'


    def show_me(self, msg=None):
        """ Debug...
        """
        if msg:
            print(f'Oper_C::show_me : {msg}')

        max_len = max( (len(key) for key in self.__dict__.keys()) )
        for key, value in self.__dict__.items():
            if key == "Nom":
                print(f'- opérateur : {self.Nom}')
            elif key != "Arg_Cars":
                print(f'  - {key:{max_len}s} = {value}')
            else:
                for i, arg_car in enumerate(self.Arg_Cars):
                    print(f'  - Arg_Cars[{i}] :')
                    arg_car.show_me()


    def cleanup(self):
        """ Nettoye l'opérateur de tous les attributs qui ont été ajoutés
            pour une exécution (en particulier les attribut header et arg_brut
            qui ont été ajoutés aux arguments de l'opérateur).
        """
        logger.log(logging.RUN, f"cleanup")

        for i, arg_car in enumerate(self.Arg_Cars):
            for attr in ['header', 'arg_brut']:
                if hasattr(arg_car, attr):
                    delattr(arg_car, attr)

        return


    def get_all_DIR_IN(self):
        """ Yield les Arg_Cars dont la direction est DIR_IN.
        """
        for arg_car in self.Arg_Cars:
            if arg_car.direction == 'DIR_IN':
                yield arg_car


    def get_all_DIR_OUT(self):
        """ Yield les Arg_Cars dont la direction est DIR_OUT.
        """
        for arg_car in self.Arg_Cars:
            if arg_car.direction == 'DIR_OUT':
                yield arg_car


    def get_VECTOR_DIR_OUT(self):
        """ Yield les Arg_Cars dont la catégorie est VECTOR et la direction
            est DIR_OUT ainsi que leur indice.
        """
        for i, arg_car in enumerate(self.Arg_Cars):
            if arg_car.categorie == 'VECTOR'  and \
               arg_car.direction == 'DIR_OUT'     :
                yield i, arg_car


    def get_nb_of_VECTOR_DIR_IN(self):
        """ Retourne le nombre de Arg_Cars dont la catégorie est VECTOR et l
            direction est DIR_IN.
        """
        nb_of = 0
        for arg_car in self.Arg_Cars:
            if arg_car.categorie == 'VECTOR'  and \
               arg_car.direction == 'DIR_IN'      :
                nb_of = nb_of + 1
        return nb_of


    def replace_dollar_Arg(self, in_arg):
        """ Retourne la valeur correspondante à 'in_arg' après remplacement de
            la variable de type '$Arg'.
            ('in_arg' est une chaine qui ne contient *que* la variable $Argxxx)

            :param str() in_arg: chaine débuttant par '$Arg_" à _remplacer_

            :return: si tout va bien, la valeur trouvée...
        """
        logger.log(logging.RUN, f"replace_dollar_Arg : in_arg = {in_arg}")

        pattern = r'\$Arg(?P<number>\d+)(\.(?P<attribut>[a-zA-Z_]+))?'
        match = re.search(pattern, in_arg)
        if not match:
            raise Exception (f"replace_dollar_Arg : erreur de syntaxe : '{in_arg}'")

        number   = int(match.group('number')) - 1
        attribut = match.group('attribut')

        if number < 0:
            raise Exception (f"Oper_C::replace_dollar_Arg : erreur de numérotation : '{in_arg}'")

        if not attribut:
            return self.Arg_Cars[number].arg_brut

        if not hasattr(self.Arg_Cars[number], 'header'):
            raise Exception (f"Oper_C::replace_dollar_Arg : erreur de numérotation : '{in_arg.split('.')[0]}' utilisé trop tôt !")

        if attribut in self.Arg_Cars[number].header:
            value = self.Arg_Cars[number].header[attribut]
            # DBG if attribut == 'unit':
            # DBG     logger.info(f"replace_dollar_Arg : UNIT = {value}")

            if value == '' and attribut == 'name':
                return 'la variable ' + self.Arg_Cars[number].header['#hdr_name']
            elif value == '' and attribut == 'english_name':
                return 'the variable named ' + self.Arg_Cars[number].header['#hdr_name']

            return self.Arg_Cars[number].header[attribut]

        # traitement spéciaux pour certaines valeurs de attribut si attribut
        # n'est pas dans self.Arg_Cars[number].header
        elif attribut == 'name':
            return 'la variable ' + self.Arg_Cars[number].header['#hdr_name']
        elif attribut == 'english_name':
            return 'the variable named ' + self.Arg_Cars[number].header['#hdr_name']
        # rien compris à type_sample et type_ech, mais de toutes les façons :
        # - type_sample n'appartient pas au header
        # - type_ech appartient au header :
        #   -- n'est obligatoire que pour les vecteurs temps
        #   -- n'est pas géré selon la norme refman.pdf par FVB
        # => ce champ n'est pas géré par ADC
        elif attribut == 'type_sample':
            attribut = 'type_ech'
            if attribut in self.Arg_Cars[number].header:
                return self.Arg_Cars[number].header[attribut]
            else:
                logger.debug(f"Oper_C:replace_dollar_Arg : '{in_arg}' : " +\
                              "ne trouve ni 'type_sample' ni 'type_ech' -> ''")
                return ''
        elif attribut == 'sample':
            attribut = 'freq_ech'
            if attribut in self.Arg_Cars[number].header:
                return self.Arg_Cars[number].header[attribut]
            else:
                logger.warning("ne trouve ni 'sample' ni 'freq_ech' : que faut-il retourner ?")
        elif attribut == 'nom':
            return self.Arg_Cars[number].arg_brut

        elif attribut == 'array_dim':
            attribut = 'dim_array'
            if attribut in self.Arg_Cars[number].header:
                return self.Arg_Cars[number].header[attribut]
            else:
                logger.debug(f"Oper_C:replace_dollar_Arg : '{in_arg}' : " +\
                              "ne trouve ni 'array_dim' ni 'dim_array' -> '1'")
                return '1'


        logger.warning(f"Oper_C::replace_dollar_Arg : non trouvé : {in_arg}")
        return ''


    def replace_dollar(self, in_arg):
        """ Retourne la valeur d'une variable de type $xxx.
        """
        if not isinstance(in_arg, str):
            return in_arg

        if not '$' in in_arg:
            return in_arg

        if '$Arg' in in_arg:
            return self.replace_dollar_Arg(in_arg)
        elif '$Acq' in in_arg:
            return self.replace_dollar_Acq(in_arg)
        elif '$Chrono' in in_arg:
            return self.replace_dollar_Chrono(in_arg)
        else:
            raise Exception (f"paramètre inattendu : '{in_arg}'")


    def replace_multi_dollar(self, in_str, np_format, ref_time_field=False):
        """ Retourne la chaine correspondante à 'in_str' après remplacement de
            *toutes* les variables de type '$xxx'.

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

            if not real_value == '""':
                if '.sample' in dollar_part and ref_time_field:
                    real_value = sample_to_str(real_value)

                in_str = in_str.replace(dollar_part, '"' + str(real_value) + '"')
            else:
                in_str = in_str.replace(dollar_part, '')

        if in_str == '""' or len(in_str) == 0:
            return in_str

        if np_format.startswith('S'):
            # champ de type chaine...
            if re.search(r'"\s*\+\s*"', in_str):
                # champ de type sous-chaines à concaténer ou '%'
                in_str = in_str.replace('""', '"') #### parfois j'ai 2 "...
                ret = eval(in_str)
            else:
                # champ de type chaine
                ret = in_str.replace('"', '')
        else:
            # champ de type numérique
            ret = eval(in_str.replace('"', ''))


        return str(ret)


    def get_call_args(self, acqid, args_brut):
        """ Prépare les arguments pour l'appel de OP_xxx.

            :param str()   acqid    : acqid pour lequel appliquer l'instruction.
            :param list()  args_brut: arguments                de l'instruction.

            :return: P_in, P_out, reftimes
            - oper_arg_NbVal : premier paramètre d'appel des opérateurs
                      NOTE : par convention, c'est le nombre de valeurs du
                      *premier* VECTOR/DIR_IN lu. Lorsque l'opérateur n'attend
                      aucun VECTOR/DIR_IN (ex : Cre_time_reg), alors
                      oper_arg_NbVal = valeur du *premier* COEFFICIENT fourni.

            - P_in  : liste des arguments pour appeler l'opérateur.
                      Contient l'espace necessaire pour les données de retour
                      (VO_data).
                      ex : list( np.array(VI_1), np_array((VI_2), nb_array(VO_data) )

            - P_out : dictionnaire pour les données de retour.
                      Chaque clé est le nom d'un vecteur VECTOR/DIR_OUT
                      chaque value est "les data ce vecteur VECTOR/DIR_OUT".

            - reftimes : liste des champ 'ref_time' des VECTOR/DIR_IN
                      (utilisé pour le controle de vecteur temps)

            Raise Exception en cas de problème.
        """
        logger.log(logging.RUN, "get_call_args")

        oper_arg_NbVal = -1
        P_in           = list()
        P_out          = dict()
        reftimes       = list()

        nb_of_VECTOR_DIR_IN = self.get_nb_of_VECTOR_DIR_IN()
        for i, (arg_cars, arg_brut) in enumerate(zip(self.Arg_Cars, args_brut)):
            if arg_cars.direction == "DIR_IN":
                if arg_cars.categorie  == "VECTOR":
                    # cas où le paramètre fournit n'est pas une string...
                    if not isinstance(arg_brut, str):
                        raise Exception(f"'{arg_brut}' : " +\
                                         "n'est pas un nom de vecteur")
                    # cas où le paramètre fournit commence par $Chrono
                    # - problème de "
                    if arg_brut.startswith('"$Chrono'):
                        args_brut = args_brut.strip('"')

                    # - récupérer la valeur du Chrono
                    if arg_brut.startswith('$Chrono'):
                        arg_brut = self.replace_dollar_Chrono(arg_brut)

                    # versionning
                    ni_name = self.get_ni_name(arg_brut)
                    try:
                        VI = AIDA.Vector(acqid, ni_name,
                                         misval_auto=self.misval_auto)
                        VI.header_utf_8()
                        P_in.insert(i, VI.data)
                    except Exception as e:
                        raise Exception(f"'{arg_brut}' : " +\
                                         "problème à la lecture du vecteur")


                    # quelques vérifications...
                    if arg_cars.typ.lower() != VI.attributes['format'].lower():
                        raise Exception(f"'{arg_brut}' (type = {VI.attributes['format']}) " +\
                                        f"n'est pas du type attendu ({arg_cars.typ})")

                    # pour le controle de la compatibilité des reftimes
                    if self.control_reftime:
                        rft = self.get_ref_time(VI.attributes)
                        if rft:
                            reftimes.append(rft)

                    # l'unité des vecteurs temps est souvent omise
                    # => forcer à 's' si besoin
                    if (not 'unit' in VI.attributes.keys()) and \
                       (arg_brut.startswith('rft')):
                        VI.attributes['unit'] = 's'

                    # pour les cas où famille="eau vapeur" (sans '_')
                    self.normalize_famille(arg_brut, VI.attributes)

                    # control de la famille si spécifié dans ID_xxx
                    self.do_control_famille(arg_brut, arg_cars, VI.attributes)

                    # ATTENTION : FVB teste les unités MAIS ne fait pas les
                    # conversions !
                    if (hasattr(arg_cars, 'unite')) and \
                       ('unit' in VI.attributes.keys()) and \
                       (arg_cars.unite not in ['', 'any', '*']):
                        unit_to = arg_cars.unite
                        if unit_to[0] == '$':
                            unit_to = self.replace_multi_dollar(unit_to, 'S')

                        if VI.attributes['unit'] != unit_to:
                            #Oper.convert_to_unit(arg_brut, VI.data,
                            #                     VI.attributes['unit'], unit_to)
                            Oper.check_convertibility_to_unit(arg_brut, VI.data,
                                                 VI.attributes['unit'], unit_to)

                    # ajout à la description de cet argument de son header
                    # et de la longeur de ses data...
                    arg_cars.header          = VI.attributes
                    arg_cars.header['NbVal'] = len(VI.data)

                    # le premier paramètre des opérateurs (NbVal) est toujours
                    # la longueur du premier VECTOR/DIR_IN (sauf lorsqu'aucun
                    # VECTOR/DIR_IN n'est fourni)
                    if oper_arg_NbVal == -1:
                        oper_arg_NbVal = len(VI.data)

                else: # "COEFFICIENT"
                    np_format = arg_cars.Format_numpy

                    # cas particulier pour misval qui peut valoir : nan
                    if isinstance(arg_brut, str) and 'misval' in arg_brut:
                        np_format = 'S'

                    if isinstance(arg_brut, str):
                        # commencer par supprimer les  ""+  et les  +""
                        pattern = r'\s*\+\s*""|""\s*\+\s*'
                        arg_brut = re.sub(pattern, '', arg_brut)

                    # traitement particulier des Constantes de type list (ex
                    # FSSP300_std_mid_diam)
                    if isinstance(arg_brut, list):
                        array_dim = self.replace_multi_dollar(arg_cars.array_dim, 'i')
                        array_dim = eval(array_dim)
                        if len(arg_brut) != array_dim:
                            raise Exception(f"'{arg_brut}' : " +\
                                            f"longueur ({len(arg_brut)}) " +\
                                            f"différente de {array_dim}")
                        # la préparation de l'argument pour le passage en C
                        # sera fait par la méthode call_op()
                        P_in.insert(i, arg_brut)
                    else:
                        arg_brut = self.replace_multi_dollar(arg_brut, np_format)
                        if arg_cars.Format_numpy in [ 'i', 'I', 'q', 'Q' ]:
                            x = round(float(arg_brut))
                            P_in.insert(i, str(x))
                        elif arg_cars.Format_numpy in [ 'f', 'd' ]:
                            x = float(arg_brut)
                            P_in.insert(i, str(x))
                        elif arg_cars.Format_numpy.startswith('S'):
                            x = arg_brut
                            P_in.insert(i, x)
                        else:
                            ADC_error.critical( "DEV : Oper_C:get_call_args : traiter " +\
                                               f"np_format = '{np_format}'",
                                               stop=True)


                    # cas particulier des opérateur qui n'attendent aucun
                    # VECTOR / DIR_IN (ex : Cre_time_reg). Dans ce cas,
                    # oper_arg_NbVal = la valeur du *premier* COEFFICIENT
                    if i == 0               and \
                       oper_arg_NbVal == -1 and \
                       nb_of_VECTOR_DIR_IN == 0 :
                        oper_arg_NbVal = int(float(arg_brut))

            else: # "DIR_OUT"
                # vérification de la description
                if not hasattr(arg_cars, 'NbVal'):
                    raise Exception (f"{arg_cars.name} : clé 'NbVal' absente " +\
                                      "=> ne peut pas calculer la taille")

                if not hasattr(arg_cars, 'Format_numpy'):
                    raise Exception(f"{arg_cars.name} : clé 'Format_numpy' absente " +\
                                     "=> ne peut pas calculer la taille")

                # calculer la taille du VO
                arg_NbVal  = getattr(arg_cars, 'NbVal')
                data_dtype = getattr(arg_cars, 'Format_numpy')

                s_NbVal  = self.replace_multi_dollar(arg_NbVal, arg_cars.Format_numpy)
                ### ATTENTION : FVB arrondi à l'entier supérieur !!!
                VO_NbVal = int(np.ceil(eval(s_NbVal)))

                arg_array_dim = getattr(arg_cars, 'array_dim')
                s_array_dim   = self.replace_multi_dollar(arg_array_dim, 'i')
                VO_array_dim  = int(eval(s_array_dim))

                # réserver de la place pour les data du VO et l'initialiser à :
                # - nan pour les vecteurs de type float32 et float64 (à
                #   l'écriture, les nan seront positionné au misval du vecteur
                #   de sortie.
                # - 0   pour tous les autres
                # ATTENTION : il ne faut pas spécifier VO_array_dim si
                #           : VO_array_dim = 1 (sinon le shape est (x,1) au
                #           : lieu de (x)
                if data_dtype == 'f' or data_dtype == 'd':
                    if VO_array_dim == 1:
                        VO_data = np.full( VO_NbVal               , np.nan, dtype=data_dtype)
                    else:
                        VO_data = np.full((VO_NbVal, VO_array_dim), np.nan, dtype=data_dtype)
                else:
                    if VO_array_dim == 1:
                        VO_data = np.full( VO_NbVal               , 0, dtype=data_dtype)
                    else:
                        VO_data = np.full((VO_NbVal, VO_array_dim), 0, dtype=data_dtype)


                # mémoriser tout ça
                P_in.insert(i, VO_data)
                P_out[arg_brut] = VO_data

            # ajout, à la description de cet argument, de son arg_brut
            # (le nom reçu dans la commande .fil)
            arg_cars.arg_brut = arg_brut

        return oper_arg_NbVal, P_in, P_out, reftimes


    def call_op(self, NbVal, args_list):
        """ Appelle l'OP_xxx.

            :param int()   NbVal    : nombre de valeur (voir OP_XXX)
            :param list()  args_list: arguments de l'opérateur
        """
        logger.log(logging.RUN, "call_op")

        # création du type 'tableau de {NbArg} void *'
        ArgList_type = ct.c_void_p * self.NbArg

        ArgList = ArgList_type()

        # initialisation de ce tableau (ArgList)
        for i, (arg_car, arg) in enumerate(zip(self.Arg_Cars, args_list)):

            if arg_car.Format_bind == Arg_Car.get_ptr_VI:
                ArgList[i] = ct.cast( arg_car.Format_bind(arg)             , ct.c_void_p)

            elif arg_car.Format_bind == Arg_Car.get_ptr_VO:
                ArgList[i] = ct.cast( arg_car.Format_bind(arg, c_float_p)  , ct.c_void_p)

            elif arg_car.Format_bind == Arg_Car.get_ptr_CI:
                ArgList[i] = ct.cast( arg_car.Format_bind(arg, arg_car.typ), ct.c_void_p)

            elif arg_car.Format_bind == Arg_Car.get_ptr_CI_array:
                # traitement particulier des Constantes de type list (ex
                # FSSP300_std_mid_diam)
                ArgList[i] = ct.cast( arg_car.Format_bind(arg, arg_car.Format_numpy), ct.c_void_p)

        # allocation d'espace mémoire pour le DiagExec
        DiagExec = ct.create_string_buffer(512)
        if NbVal <= 0:
            logger.warning(f"NbVal = {NbVal} => ça va surement planter grave !!!")

        # appel de l'opérateur
        logger.log(logging.RUN, "appel de l'opérateur")
        ret = self.OP_fct(NbVal, ArgList, DiagExec)

        return ret, DiagExec


    def build_headers(self, acqid, diag):
        """ Construit le header de tous les vecteurs de sortie de l'opérateur.

            :param str() acqid: acqid pour lequel est fait le traitement.
            :param str() diag : chaine à inscrire dans le champ 'fct_comment'

            :return: liste des headers de sortie
            :rtype : list()
        """
        logger.log(logging.RUN, "build_headers")

        VO_headers = []

        # correspondances entre les clés des descritpeurs des opérateurs (que
        # l'on peut trouver dans une instruction ADC) et les clés des headers
        # des vecteurs (validé par William et Jacques).
        fil_keys = {'typ'         : {'name': 'format'       , 'np_format': 'S'},
                    'array_dim'   : {'name': 'dim_array'    , 'np_format': 'i'},
                    'bornes'      : {'name': 'bornes'       , 'np_format': 'S'},
                    'unit_bornes' : {'name': 'unit_bornes'  , 'np_format': 'S'},
                    'unite'       : {'name': 'unit'         , 'np_format': 'S'},
                    'name'        : {'name': 'name'         , 'np_format': 'S'},
                    'en_name'     : {'name': 'english_name' , 'np_format': 'S'},
                    'type_sample' : {'name': 'type_ech'     , 'np_format': 'S'},
                    'sample'      : {'name': 'freq_ech'     , 'np_format': 'f'},
                    'ref_time'    : {'name': 'ref_time'     , 'np_format': 'S'},
                    'time_bnds'   : {'name': 'time_bnds'    , 'np_format': 'S'},
                    'famille'     : {'name': 'famille'      , 'np_format': 'S'},
                    # misval peut être 'nan'
                    'misval'      : {'name': 'misval'       , 'np_format': 'S'},
        }

        # pour tous les VECTOR / DIR_OUT de l'opérateur
        for i, (arg_nb, arg_cars) in enumerate(self.get_VECTOR_DIR_OUT()):
            logger.debug(f"build_headers : {arg_cars.arg_brut}")
            VO_header = dict()
            setattr(arg_cars, 'header', VO_header)

            # traiter 'sample' avant tout : on peut retrouver par la suite dans
            # la description, par ex :
            # name = $Arg1.name + " moyenne a " + $Arg4.sample + "Hz"
            if 'sample' in arg_cars.__dict__.keys():
                key = 'sample'
                value = getattr(arg_cars, key)
                if isinstance(value, str)  and  '$' in value:
                    fil_key   = fil_keys[key]['name']
                    np_format = fil_keys[key]['np_format']
                    real_value = self.replace_multi_dollar(value, np_format,
                                              ref_time_field=(key=='ref_time'))
                else:
                    real_value = value
                arg_cars.header[fil_key] = real_value


            for key, value in arg_cars.__dict__.items():
                if key == 'sample': # clé traitée ci-dessus
                    continue

                # clef qui ne font pas partie du header
                if not key in fil_keys.keys():
                    continue

                fil_key   = fil_keys[key]['name']
                np_format = fil_keys[key]['np_format']
                if isinstance(value, str)  and  '$' in value:
                    real_value = self.replace_multi_dollar(value, np_format,
                                              ref_time_field=(key=='ref_time'))
                    if np_format == 'i':
                        real_value = str(int(float(real_value)))
                else:
                    real_value = value

                # les valeurs non-positionnées ne sont pas enregistrées
                real_value = real_value.strip('"')
                if len(real_value) > 0:
                    VO_header[fil_key] = real_value

            # récupération des variables passées dans Meta_Out
            if self.Nom in use_Meta_Out:
                vals_for_header = meta_out.restricted_get_variables(arg_nb)
                for key, value in vals_for_header.items():
                    VO_header[key] = value
                    logger.debug( "build_headers : Meta_Out : " +\
                                 f"VO_header['{key}'] = {VO_header[key]}")

            # default misval
            if not 'misval' in VO_header.keys():
                typ = VO_header['format']
                if not typ in AIDA_type_misval.keys():
                    ADC_error.critical( "DEV : Oper_C:build_headers : traiter " +\
                                       f"typ = '{typ}'",
                                       stop=True)
                else:
                    VO_header['misval'] = AIDA_type_misval[typ]
                    logger.debug( "build_headers : misval : " +\
                                 f"VO_header['misval'] = {VO_header['misval']}")

            # finaliser le header
            if not 'unit' in VO_header.keys():
                VO_header['unit'] = 'unitless'
            VO_header['fct_origine'] = self.line_cmd
            VO_header['fct_comment'] = diag

            VO_headers.insert(i, copy.deepcopy(VO_header))

        return VO_headers


    def exec_line(self, acqid, args_brut):
        """ Excécute la ligne d'instruction ADC reçue :
            - prépare les arguments pour l'appel de l'opérateur
            - appelle l'opérateur OP_xxx
            - écrit les vecteurs de sortie

            :param str()   acqid    : acqid pour lequel appliquer l'instruction.
            :param list()  args_brut: arguments             de l'instruction.
        """
        logger.log(logging.RUN, "exec_line")

        logger.debug(f"{self.Nom} : opérateur C : " +
                     f"control_reftime = {self.control_reftime}")

        self.cleanup()

        # controle du nombre de paramètres
        if self.NbArg != len(args_brut):
            raise Exception ( "nombre de paramètre incorrect : attendu = " +\
                             f"{self.NbArg} <-> reçu = {len(args_brut)}")

        # enregistrement d'information dans l'opérateur
        self.acqid    = acqid
        self.path     = AIDA.ID_to_datapath(self.acqid)
        self.pltf     = AIDA.AIDA_abrev_to_plt(acqid[0:2])

        # traitement des arguments
        try:
            NbVal, P_in, P_out, reftimes = self.get_call_args(acqid, args_brut)
            output_names = P_out.keys()
        except Exception as e:
            raise Exception (e)


        # controles avant le lancement de l'opérateur
        if not self.check_before_call(reftimes, output_names):
            return

        # excécution de l'opérateur
        # =========================
        logger.log(logging.RUN, "appel de l'opérateur")
        DiagExec = 1
        ret, DiagExec = self.call_op(NbVal, P_in)

        # certains opérateurs font des printf sans \n => flusher...
        libc.fflush(None) # flush all C streams

        # gestion du diagnostique
        try:
            diag = DiagExec.value.decode()
        except UnicodeDecodeError as e:
            diag = DiagExec.value.decode('iso8859-15')

        # vérification du code de retour
        if ret != 0:
            ADC_error.critical(f"{self.Nom} : CodeRet != 0 " +\
                                "=> les vecteurs de sortie ne sont pas écrits",
                               stop=True)
            return

        # il arrive que le DiagExec contienne des morceaux de string sous la
        # forme : b\'xxx\' => nettoyer
        pattern = r"b'([^']*)'"
        diag = re.sub(pattern, r"'\1'", diag)

        # il arrive que diag contient des chaines vides sur-côtées...
        # ex : Poly_1_flt (flx_phi0_1p2p3p4_c2_%60,0,1/4.,"Watt/m2","","",...)
        # retourne : ... calcul de '""' ("'""'") par ...
        diag = diag.replace('\'""\'', '""')
        diag = diag.replace('""""', '""')


        # construction du header des vecteurs de sortie
        VO_headers = self.build_headers(acqid, diag)

        # écriture des output
        i = 0
        for (VO_name, VO_data), VO_header in zip(P_out.items(), VO_headers):
            super().write_vect(acqid, i, VO_name, VO_header, VO_data)
            i = i + 1


    def exec_line_no_write(self, acqid, args_brut):
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

        logger.debug(f"{self.Nom} : opérateur C : " +
                     f"control_reftime = {self.control_reftime}")

        self.cleanup()

        # controle du nombre de paramètres
        if self.NbArg != len(args_brut):
            raise Exception ( "nombre de paramètre incorrect : attendu = " +\
                             f"{self.NbArg} <-> reçu = {len(args_brut)}")

        # enregistrement d'information dans l'opérateur
        self.acqid    = acqid
        self.path     = AIDA.ID_to_datapath(self.acqid)
        self.pltf     = AIDA.AIDA_abrev_to_plt(acqid[0:2])

        # traitement des arguments
        try:
            NbVal, P_in, P_out, reftimes = self.get_call_args(acqid, args_brut)
            output_names = P_out.keys()
        except Exception as e:
            raise Exception (e)

        # controles avant le lancement de l'opérateur
        if not self.check_before_call(reftimes, output_names):
            msg = "'rft_time' incompatibles ou problèmes de droits"
            return 1, msg, None

        # excécution de l'opérateur
        # =========================
        logger.log(logging.RUN, "appel de l'opérateur")
        DiagExec = 1
        ret, DiagExec = self.call_op(NbVal, P_in)

        # certains opérateurs font des printf sans \n => flusher...
        libc.fflush(None) # flush all C streams

        # gestion du diagnostique
        try:
            diag = DiagExec.value.decode()
        except UnicodeDecodeError as e:
            diag = DiagExec.value.decode('iso8859-15')

        # il arrive que le DiagExec contienne des morceaux de string sous la
        # forme : b\'xxx\' => nettoyer
        pattern = r"b'([^']*)'"
        diag = re.sub(pattern, r"'\1'", diag)

        # il arrive que diag contient des chaines vides sur-côtées...
        # ex : Poly_1_flt (flx_phi0_1p2p3p4_c2_%60,0,1/4.,"Watt/m2","","",...)
        # retourne : ... calcul de '""' ("'""'") par ...
        diag = diag.replace('\'""\'', '""')
        diag = diag.replace('""""', '""')

        return ret, diag, [ val for val in P_out.values() ]


def init_opers_C(desc, exclude=None):
    """ Yield tous les Oper_C décrits dans le fichier de description passé en
        argument. Typiquement, le fichiers de description est :
            `oper_API_PY_desc.py`
        Exclue les opérateurs dont le nom appartient à 'exclude' (ceux qui
        ont été ré-écrit en python)

        :param str() desc     : fichier de description des opérateurs C.

        Si l'un des Arg_Cars n'est pas DIR_IN/DIR_OUT ou VECTOR/COEFFICIENT
        l'opérateur n'est pas renvoyé.
    """
    logger.log(logging.RUN, "init_opers_C")

    for oper_name, oper_desc in desc.items():
        if exclude and oper_name in exclude:
            logger.debug(f"opérateur C -> Python : {oper_name}")
            continue

        logger.debug(f"- {oper_name}")

        if oper_name in control_reftimes:
            oper_desc['control_reftime'] = False
        else:
            oper_desc['control_reftime'] = True


        oper_ok = True
        for i, arg_car in enumerate(oper_desc['Arg_Cars']):
            if arg_car['direction'] != 'DIR_IN'  and \
               arg_car['direction'] != 'DIR_OUT'     :
                msg = f"init_opers_C : {oper_name} : Arg_Cars[{i}] : " +\
                       "ni DIR_IN ni DIR_OUT => ignoré"
                logger.error(msg)
                Rapport.add( "problème d'initialisation d'opérateur C", msg, cat='dev')

                oper_ok = False
                break

            if arg_car['categorie'] != 'VECTOR'  and \
               arg_car['categorie'] != 'COEFFICIENT' :
                msg = f"init_opers_C : {oper_name} : Arg_Cars[{i}] : " +\
                       "ni VECTOR ni COEFFICIENT => ignoré"
                logger.error(msg)
                Rapport.add( "problème d'initialisation d'opérateur C", msg)

                oper_ok = False
                break

        if oper_ok:
            try:
                yield Oper_C(Nom=oper_name, **oper_desc)
            except Exception as e:
                ADC_error.critical(e, stop=True)


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


    # dans $AIDA_HOME/lib/pythonx.y
    import oper_API_PY_desc
    from fct_messages import warning, stop_error, wait_user

    # description de tous les opérateurs C
    desc_opers_C = oper_API_PY_desc.oper_API_PY_desc

    oper_name = 'Poly_1_flt'
    print(f"\n* Récupération de la description de l'opérateur : {oper_name}")
    wait_user()
    desc_mon_oper_C = desc_opers_C[oper_name]


    print(f"\n* Création de l'opérateur '{oper_name}' à partir de sa description")
    wait_user()
    try:
        mon_oper_C = Oper_C(Nom=oper_name, **desc_mon_oper_C)
    except Exception as e:
        logger.error(e)

    print(f"\n* Visualisation de l'opérateur '{oper_name}'")
    wait_user()
    mon_oper_C.show_me()

    print(f"\n* Récupération des Arg_Cars de type DIR_IN")
    wait_user()
    for i, arg_cars in enumerate(mon_oper_C.get_all_DIR_IN()):
        print(f"  - Arg_Cars[{i}]")
        arg_cars.show_me()
        print()

    print(f"\n* Récupération des Arg_Cars de type DIR_OUT")
    wait_user()
    for i, arg_cars in enumerate(mon_oper_C.get_all_DIR_OUT()):
        print(f"  - Arg_Cars[{i}]")
        arg_cars.show_me()
        print()

    print(f"\n* Récupération des Arg_Cars de type VECTOR / DIR_OUT")
    wait_user()
    for arg_nb, arg_cars in mon_oper_C.get_VECTOR_DIR_OUT():
        print(f"  - Arg_Cars[{arg_nb}]")
        arg_cars.show_me()
        print()


    print(f"\n* Création de tous les Oper_C")
    wait_user()
    opers_C = { oper.Nom: oper for oper in init_opers_C(desc_opers_C) }
    # vérifier que dens_cdp n'est pas remonté
    if 'dens_cdp' in opers_C:
        print(f"  ** !!! 'dens_cdp' ne devrait pas être là !!!")
        print(f"  ** 'dens_cdp': {opers_C['dens_cdp'].show_me()}")
    else:
        print(f"  ** 'dens_cdp' n'est pas dans les opérateurs : c'est ok !!!")


    oper_name = 'Plus'
    print(f"\n* Visualisation de l'opérateur '{oper_name}'")
    wait_user()
    opers_C['Plus'].show_me()

