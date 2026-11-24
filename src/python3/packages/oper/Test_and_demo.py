#!/usr/bin/env python3

"""
    ADC : Opérateur Test_and_demo
"""

import sys
import os
import logging
import numpy as np

logger = logging.getLogger('adc')

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

from oper.default_out_header import default_out_header
import calcul

#==============================================================================
# Fonction Opérateur
#
# Les arguments sont ceux de la ligne d'instruction ADC lue dans le .fil
# ***SANS*** les noms des VECTOR/DIR_OUT
#
# Les arguments de type VECTOR/DIR_IN reçus sont des AIDA.VectorMask.
#
# L'opérateur :
#   - prépare les arguments pour appeller la fonction de calcul
#   - appelle la fonction de calcul
#   - prépare le(s) header(s) du/des vecteurs de retour.
#   - retourne : [headers], [data], {'CodeRet' : int()>= 0, 'DiagExec': str()}
#
# NOTE : AIDAcalc et AIDA.Vector mettront à jour les attributs :
#           #hdr_name, date_creation, fct_origine et vol...
#        des headers avant d'écrire les vecteurs.
#==============================================================================
def Test_and_demo(T, unit=None, OPT_val=None, OPT_list=None, OPT_dict=None, OPT_bool=None, OPT_str=None):
    """
    Cet opérateur sert à faire des tests de ADC.
    IL NE DOIT PAS ÊTRE UTILISÉ POUR FAIRE DE LA PRODUCTION DE DONNÉES.

    Input :
        T        : température
        unit     : une unité.s
                   Un opérateur ne devrait jamais attendre un argument
                   optionnel de positionnement id'une variable du header. Pour
                   modifier une variable du header, l'utilisateur devrait
                   utiliser HDR_unit=['...', '...', ]
        OPT_val  : une valeur
        OPT_list : une liste
        OPT_dict : un dictionnaire
        OPT_bool : un booléen
        OPT_str  : une chaîne

    Output :
        P  : valeurs de retour

    Auteur : @Météo-France CNRM/GMEI/TRAMM - September 2022
    """
    logger.debug("Test_and_demo : debut")

    coef = 0
    print(f":::: opérateur Test_and_demo : coef init = {coef}")

    msg = f"OPT_val={OPT_val}, OPT_list={OPT_list}, OPT_dict={OPT_dict}, OPT_bool={OPT_bool}, OPT_str={OPT_str}"

    print(f":::: opérateur Test_and_demo : OPT_val  : value = {OPT_val}, type = {type(OPT_val)}")
    print(f":::: opérateur Test_and_demo : OPT_list : value = {OPT_list}, type = {type(OPT_list)}")
    print(f":::: opérateur Test_and_demo : OPT_dict : value = {OPT_dict}, type = {type(OPT_dict)}")
    print(f":::: opérateur Test_and_demo : OPT_bool : value = {OPT_bool}, type = {type(OPT_bool)}")
    print(f":::: opérateur Test_and_demo : OPT_str  : value = {OPT_str}, type = {type(OPT_str)}")
    if OPT_val:
        coef = coef + int(OPT_val)
        print(f":::: opérateur Test_and_demo : coef val  = {coef}")

    if OPT_list:
        for item in OPT_list:
            coef = coef + int(item)
        print(f":::: opérateur Test_and_demo : coef list = {coef}")

    if OPT_dict:
        for key, val in OPT_dict.items():
            coef = coef + int(val)
        print(f":::: opérateur Test_and_demo : coef dict = {coef}")

    # récupération des arguments
    T_header = T.attributes
    T_data   = T.data.data

    if not unit:
        unit = f"{T_header['unit']}"
    print(f":::: opérateur Test_and_demo : unit      = {unit}")

    # préparation des arguments pour la fonction de calcul
    CtoK  = calcul.unit.auto_tempe_unit(T_data.data)
    if CtoK == 0:
        unit_msg = "Unite reconnue : Kelvin"
    else:
        unit_msg = "Unite reconnue : Degres Celsius"
    print(f":::: opérateur Test_and_demo : ctok      = {CtoK}")
    print(f":::: opérateur Test_and_demo : ctok +coef= {CtoK + coef}")

    # appel de la fonction de calcul
    # sans OPT : P_data = calcul.Test_and_demo.Test_and_demo(T_data, CtoK + coef)
    P_data = calcul.Test_and_demo.Test_and_demo(T_data, CtoK + coef, OPT=coef)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    T_fr_name, T_en_name = T.get_names()

    P_header                 = default_out_header.copy() 
    P_header['name']         = f"Pression calculee a partir de '{T_fr_name}'"
    P_header['english_name'] = f"Pressure computed with '{T_en_name}'"
    P_header['unit']         = f"{unit}"
    P_header['freq_ech']     = f"{T_header['freq_ech']}"
    P_header['ref_time']     = f"{T_header['ref_time']}"
    P_header['misval']       = f"{T_header['misval']}"
    P_header['information']  =  "Pressure computed with pressure at others altitudes"
    print(f":::: opérateur Test_and_demo : on pourrait peut-être utiliser le champ 'information' pour donner des 'name' plus courts")

    diag = {'CodeRet' : 0,
            'DiagExec': f"Test_and_demo : ({len(T_data)} ech.), " +
                        f"CtoK = {CtoK}, coef = {coef}, msg = '{msg}', " +
                        f"{unit_msg}"
           }

    return [P_header], [P_data], diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Test_and_demo': {
        'Args': [
            {'Id': 'T'   , 'categorie': 'VECTOR_IN'  , 'unit': 'hPa' },
            {'Id': 'P'   , 'categorie': 'VECTOR_OUT'                 },
        ],
        'repl_oper' : 'new_oper',
        'repl_cause': 'Test_and_demo ne permet pas de faire xxx',
    },
}


#==============================================================================
# Test de l'opérateur
#==============================================================================
if __name__ == '__main__':

    import AIDA
    from   Misval import AIDA_type_misval as AIDA_type_misval


    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')


    # création de Vector en mémoire
    acqid = 'ch229999'
    logger.info(f'=== {acqid}')
    header = dict()
    header['name']         = 'pseudo variable francais'
    header['english_name'] = 'pseudo variable english'
    header['format']       = 'Ieeefloat_32'
    header['dimension']    = '4'
    header['dim_array']    = '1'
    header['ref_time']     = 'rft_TIME_20'
    header['misval']       = AIDA_type_misval[ header['format'] ]
    header['freq_ech']     = 20
    header['unit']         = 'K'
    header['famille']      = 'temperature'
    header['origine']      = 'test ADC'

    print(f":::: header['misval'] = {header['misval']}")
    print(f":::: type header['misval'] = {type(header['misval'])}")
    input("... [ENTER] pour continuer")


    T = AIDA.VectorMask(acqid, 'T', attributes=header, data=np.array([np.nan,  2.,  3.,  4.]))

    # appel de l'opérateur
    logger.info("== Appel de Test_and_demo sans arguments optionnels")
    headers, datas, diag = Test_and_demo(T)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in { k:header[k] for k in sorted(header) }.items():
            logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data   = {data}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
    input("... [ENTER] pour continuer")
    print("\n\n")



    # appel de l'opérateur
    OPT_val = 12
    logger.info(f"== Appel de Test_and_demo avec OPT_val={OPT_val}")
    headers, datas, diag = Test_and_demo(T, OPT_val=OPT_val)

    # résultat
    for header, data in zip(headers, datas):
        logger.info(f"data   = {data}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
    input("... [ENTER] pour continuer")
    print("\n\n")



    # appel de l'opérateur
    OPT_list = [1, 2]
    logger.info(f"== Appel de Test_and_demo avec OPT_list={OPT_list}")
    headers, datas, diag = Test_and_demo(T, OPT_list=OPT_list)

    # résultat
    for header, data in zip(headers, datas):
        logger.info(f"data   = {data}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
    input("... [ENTER] pour continuer")
    print("\n\n")



    # appel de l'opérateur
    OPT_dict = {'a': 10, 'b': 11}
    logger.info(f"== Appel de Test_and_demo avec OPT_dict={OPT_dict}")
    headers, datas, diag = Test_and_demo(T, OPT_dict=OPT_dict)

    # résultat
    for header, data in zip(headers, datas):
        logger.info(f"data   = {data}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
    input("... [ENTER] pour continuer")
    print("\n\n")



    # appel de l'opérateur
    logger.info(f"== Appel de Test_and_demo avec OPT_val={OPT_val}, OPT_list={OPT_list}, OPT_dict={OPT_dict}")
    headers, datas, diag = Test_and_demo(T, OPT_dict=OPT_dict, OPT_val=OPT_val, OPT_list=OPT_list)

    # résultat
    for header, data in zip(headers, datas):
        logger.info(f"data   = {data}")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
