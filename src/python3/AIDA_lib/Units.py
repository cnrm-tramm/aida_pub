#!/usr/bin/env python3

"""
Normalisation des unités AIDA.

Il n'existe pas de liste exhaustive des unités normalisées AIDA.
AIDA accepte les unités conformes au module python 'cfunits' en notation courte
(plus quelques autres comme 'unitless').

Pour connaitre la notation AIDA d'une unité, taper la commande :
    Units.py <votre unité sans accent>

Exemples :
    * unités valides :
        Units.py metre
            metre -> m
    
        Units.py metre second
            metre second -> m.s

        Units.py m second
            m second -> m.s

        Units.py 1e-06 m-2.s-1.mol
            1e-06 m-2.s-1.mol -> umol.m-2.s-1

    * unités NON valides :
        Units.py mètre
            Units::get_AIDA_unit : unité non-valide : 'mètre'

        Units.py metre seconde
            Units::get_AIDA_unit : unité non-valide : 'metre seconde'
"""

import sys
import re
import cfunits as cf

# Normalisation manuelle des unités :
# clés    = unités non-AIDA
# valeurs = unités normalisées AIDA
AIDA_Units = {
    'K @ 273.15'                 : 'Celsius',

    'bits'                       : 'bit',
    'count'                      : 'count',
    'count / cm3'                : 'count.cm-3',
    'count second-1'             : 'count.s-1',
    'second/second'              : 's.s-1',
    'm3/m3'                      : 'm3.m-3',
    'gram/kg'                    : 'g.kg-1',
    'g/kg'                       : 'g.kg-1',
    '%'                          : 'percent',
    'ppm'                        : 'ppm',
    'ppb'                        : 'ppb',
    'ppmv'                       : 'ppmv',
    'ppbv'                       : 'ppbv',

    '86400 s'                    : 'day',
    '60 s'                       : 'min',
    'seconde'                    : 's',

    '1.66666666666667e-05 m.s-1' : 'mm/min',
    '2.77777777777778e-07 m.s-1' : 'mm/h',

    'degre'                      : 'degree',
    'degres'                     : 'degree',
    'degree_north'               : 'degree_north',
    'degree_east'                : 'degree_east',
    '0.0174532925199433 rad'     : 'degree',    # ne permet de différencier degree, degreen, degreee...

    's-1'                        : 'Hz',        # ne permet pas de différencier Hz et 1/s
    '1000000 s-1'                : 'MHz',
    '1000000000 s-1'             : 'GHz',

    'N/m2'                       : 'N.m-2',
    'm-1.kg.s-2'                 : 'Pa',
    '100 m-1.kg.s-2'             : 'hPa',

    '1000 m2.kg.s-3.A-2'         : 'kOhm',
    'm2.kg.s-3.A-2'              : 'Ohm',

    'm2.kg.s-3.A-1'              : 'V',
    '0.001 m2.kg.s-3.A-1'        : 'mV',

    'm2.kg.s-3'                  : 'W',
    'kg.s-3'                     : 'W.m-2',

    '0.3048 m'                   : 'ft',

    '0.514444444444444 m.s-1'    : 'kt',

    '1e-09 m'                    : 'nm',
    '1e-06 m'                    : 'um',
    '0.001 m'                    : 'mm',
    '1e-06 m2'                   : 'mm2',
    '0.01 m'                     : 'cm',
    '0.0001 m2'                  : 'cm2',
    '1e-06 m3'                   : 'cm3',
    '10000 m-2'                  : 'cm-2',
    '1000000 m-3'                : 'cm-3',
    '1000000000 m-4'             : 'l-1.um-1',
    '1000000000000 m-4'          : 'cm-3.um-1',

    '1000 m-3'                   : 'l-1',

    '1e-06 m-6.kg2'              : 'g2.m-6',
    '0.001 m-2.kg.s-1'           : 'g.m-2.s-1',
    '0.001 m-3.kg'               : 'g.m-3',
    '1000 m-3.kg'                : 'g.cm-3',
    '1e-09 m-3.kg'               : 'ug.m-3',

    'm2.s-2.K-1'                 : 'J.kg-1.K-1',

    '2.77777777777778e-07 m.s-1' : 'mm.h-1',

    '1e-06 m-2.s-1.mol'          : 'umol.m-2.s-1',

    '1e-06 m-2.kg.s-1'           : 'mg.m-2.s-1',

    'sccm'                       : 'sccm',      # Standard cubic centimetres per minute

    '1.602176487e-19 s.A'        : 'e',         # charge éléctrique (*)

    'unitless'                   : 'unitless',  # voir ticket AIDA n°2391
    'without'                    : 'unitless',

    # unités spécifiques des fonctions C ID_xxx
    '1'                          : 'unitless',
    ''                           : 'unitless',
    'nihil'                      : 'unitless',
    'none'                       : 'unitless',

    'unknown'                    : 'unknown',   # ou 'without' ? le 27 oct 2022 : on ne sait pas trop
    # 'any'                        : 'without', # doit être traiter spécifiquement par ADC
}

# (*) :
# cfunits, pour des unités "sans nom d'unité", retourne une définition
# d'unité de la forme '1', '1e-06 1'... Dans ce cas, on doit retourner l'unité
# reçue (ex 'ppm', 'm3.m-3').
# On estime que l'unité retournée par cfunits est une unité "sans nom d'unité"
# si la liste des lettres qu'elle contient est vide ou égale à 'e'.
# De ce fait, l'unité 'e' doit être définie ici pour que l'on ne retourne
# pas '1.602176487e-19 s.A' lorsque l'unité 'e' est présentée


def get_AIDA_unit(unit):
    """ retourne l'unité normalisée...
        Raise Exception s'il n'existe pas de normalisation pour l'unité
        d'entrée.

        :param str() unit: unité d'entrée

        :return: unité normalisée
        :rtype: str()
    """
    # cas particulier
    if not unit:
        return 'unitless'

    # cas à ne par traiter
    if '$' in unit:
        return unit

    # cas simple : l'unité est une valeur ou une clé de la norme
    if unit in AIDA_Units.values():
        return unit
    elif unit in AIDA_Units.keys():
        return AIDA_Units[unit]

    # que dit cfunits ?
    cf_unit = cf.Units(unit)
    if not cf_unit.isvalid:
        raise Exception(f"Units::get_AIDA_unit : unité non-valide : '{unit}'")

    # pour les unités "sans nom d'unité", retourner l'unité reçue
    # (ex : ppm -> 1e-06 1, count -> 1)
    pattern = r'[a-zA-Z]'
    all_letters = re.findall(pattern, cf_unit.formatted())
    if not all_letters or all_letters == ['e']:
        return unit

    # si la definition de cfunits est une clé de la norme, retourner la valeur
    cf_unit_def = cf_unit.formatted(definition=True)
    if cf_unit_def in AIDA_Units.keys():
        return AIDA_Units[cf_unit_def]

    # retourner la definition de cfunits
    # (si besoin, elle sera peut-être ajoutée manuellement à la norme...)
    return cf_unit_def


def get_CF_family(unit):
    """ Si unit est une unité CF valide et que cette unité appartient à une
        famille CF d'unité, retroune la famille CF.
        Sinon retourne None.

        :param str() unit: unité en entrée.

        :return: famille CF d'unité ou None
        :rtype : str()
    """
    u = cf.Units(unit)
    if u.isvalid:
        if u.islatitude:
            return 'latitude'
        if u.islongitude:
            return 'longitude'
        if u.ispressure:
            return 'pression'
        if u.isreftime:
            return 'temps'
        if u.istime:
            return 'temps'
        #if u.isdimensionless:
        #    return 'sans_dimension'
        else:
            return None
    return None


if __name__ == '__main__':

    if len(sys.argv) == 1:
        print(__doc__)
        sys.exit(1)

    if len(sys.argv) > 1:
        # test de l'unité passée en argument
        u = ' '.join(sys.argv[1:])
        #print(f"AIDA : test de l'unité passée en argument : '{u}'")
        try:
            print(f"{u} -> {get_AIDA_unit(u)}")
        except Exception as e:
            print(e)
        sys.exit(1)

    # code volontairement NON EXÉCUTÉ
    # ===============================
    # tests de différentes unités rencontrées pendant le développement d'ADC
    print("AIDA : tests sur les unités")
    test_units = [ 'ampere',
                   'bit',
                   'bits',
                   'celsius',
                   'Celsius',
                   'Celsius2',
                   'cm2',
                   'cm-3',
                   'count',
                   'count / cm3',
                   'count second-1',
                   'day',
                   'min',
                   's',
                   'sec',
                   'second',
                   'second-1',
                   's-1',
                   'second/second',
                   'degre',
                   'degree',
                   'degres',
                   'degree_north',
                   'degree_east',
                   'g2/m6',
                   'g/kg',
                   'g.m-2.s-1',
                   'g/m3',
                   'gram/m3',
                   'gram/cm3',
                   'gram/kg',
                   'g.s-1.m-2',
                   'hertz',
                   'Hz',
                   'hPa',
                   'J K-1 kg-1',
                   'J.kg-1.K-1',
                   'K',
                   'kelvin',
                   'Kelvin',
                   'kg m-3',
                   'kg.m-3',
                   'kg/m3',
                   'kohm',
                   'kt',
                   'l-1',
                   'liter-1',
                   'liter-1*micron-1',
                   'm',
                   'm-1',
                   'm2.s-2',
                   'm2/s2',
                   'm3/m3',
                   'meter',
                   'meters',
                   'meter/second',
                   'm/s*m/s',
                   'm/s m/s',
                   'micron',
                   'microns',
                   'microns-1.cm-3',
                   'm.K/s',
                   'm.K.s-1',
                   'cm',
                   'mm',
                   'millimeter',
                   'mm2',
                   'mm/h',
                   'm/s',
                   'msec',
                   'mvolt',
                   'micromoles/m2/s',
                   'milligram/m2/s',
                   'mVolt',
                   'volt',
                   'Volt',
                   'nm',
                   'N/m2',
                   '%',
                   'percent',
                   'radian',
                   'radians',
                   'rad/s',
                   'radian/s',
                   'ugram/m3',
                   'watt',
                   'Watt',
                   'W/m2',
                   'watt/m2',
                   'Watt/m2',
                   '1',
                   'without',
                   'unitless',
                   '',
                   'any',
                   'nihil',
                   'none',
                   'unknown',
                   'ppm',
                   'ppb',
                   'ppmv',
                   'ppbv',
                   'e',
                   'sccm',
                   '0.0174532925199433 rad',
                   '86400 s',
                   'umoles.mm-2',
                   'mmmol/mol',
                   'mmol/mol',
                 ]

    for unit in test_units:
        if unit == 'any':
            continue
        try:
            print(f"{unit:30s} -> {get_AIDA_unit(unit)}")
        except Exception as e:
            print(e)
