#!/usr/bin/env python3

"""
AITO
    Gestion de l'appel effectif des opétateurs.

    Cette classe fait le même travail que ADC en ligne de commande sauf que
    le résultat des opérateurs n'est pas écrit sur le disque mais retourné
    à l'appelant.
    De ce fait, cette classe import à peu près tout le code de ADC.
"""

import sys
import os
import logging
import ctypes as ct
import copy


AH = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
AL = os.path.join(os.getenv('AIDA_HOME'), 'lib')
sys.path.append(os.path.join(AL, PYTHON_X_Y))
sys.path.append(os.path.join(AL, PYTHON_X_Y, 'AIDAcalc'))

path_lib_oper = os.path.join(AL, 'liboper.so')

import AIDA
import AIDA_logger
from Fil_analyze import parse_instruction

from AITO_operators import operators

###logger = AIDA_logger.configure_AIDA_logging('aito')
logger = logging.getLogger('aito')

# gestion des opérateurs
# ----------------------
from OperTypes import OperTypes, get_OperType

# - 1) opérateurs connus de AITO
aito_operators = operators.keys()


# - 2) opérateurs Python
import oper
import AIDAcalc.Oper_PY

# descriptions de tous opérateurs Python (raccourcis)
desc_opers_PY = oper.__desc_opers

# descriptions des opérateurs Python utilisé dans AITO
aito_desc_opers_PY = dict()

# dictionnaire des operateurs Python
opers_PY = dict()

# noms des opérateurs Python
opers_PY_names = list()


# - 3) opérateurs C
import oper_API_PY_desc
import AIDAcalc.Oper_C

# description de tous les opérateurs C (raccourcis)
desc_opers_C = oper_API_PY_desc.oper_API_PY_desc

# descriptions des opérateurs C utilisé dans AITO
aito_desc_opers_C = dict()

# dictionnaire des operateurs C
opers_C = dict()

# noms des opérateurs C
opers_C_names = list()


# - 4) lib oper et pointeurs sur foncion C
# liboper (utile pour récupérer les pointeurs sur fonctions)
lib_oper = ct.CDLL(path_lib_oper)

# pointeurs sur fonction des opérateur C
OP_fcts = dict()


# initialisations
# ---------------
# ne récupérer que les informations concernant les opérateurs de AITO
for oper_name in aito_operators:
    # DBG print(f"  - oper_name = {oper_name}")
    if oper_name in desc_opers_PY.keys():
        # DBG print(f"     - in PYTHON")
        aito_desc_opers_PY[oper_name] = desc_opers_PY[oper_name]

    elif oper_name in desc_opers_C.keys():
        # DBG print(f"     - in C")
        aito_desc_opers_C[oper_name] = desc_opers_C[oper_name]

        # récupérer le pointeur sur fonction
        OP_name = f'lib_oper.OP_{oper_name}'
        try:
            instruction = compile(f'OP_xxx = {OP_name}', '<string>', 'exec')
            env_fvb = {}
            eval(instruction, globals(), env_fvb)
        except Exception as e:
            raise Exception(f"Call_Oper.py : unknown operator : '{oper_name}'")

        # mémoriser le pointeur sur fonction de l'opérateur
        OP_fcts[oper_name] = env_fvb['OP_xxx']


# créer les objets Oper_PY pour les opérateurs Python de AITO
opers_PY = { oper.Nom: oper
                for oper in AIDAcalc.Oper_PY.init_opers_PY(aito_desc_opers_PY) }


# créer les objets Oper_C pour les opérateurs C de AITO
opers_C = { oper.Nom: oper
              for oper in AIDAcalc.Oper_C.init_opers_C(aito_desc_opers_C,
                                              exclude=oper.__all_names)
          }

#  ajouter les pointeurs sur fonction aux opérateurs C.
for oper_name, oper in opers_C.items():
    oper.OP_fct = OP_fcts[oper_name]

# mémoriser les listes de nom d'opérateur connus de AITO
opers_PY_names = desc_opers_PY.keys()
opers_C_names  = desc_opers_C.keys()



class Call_Oper():

    def __init__(self):
        # DBG print(f"=== Call_Oper::__init__")

        # initialiser le dictionnaire d'option :
        # - force = True : faire le traitement même si le vecteur de sortie
        #                  existe (un vecteur du même nom peut avoir été crée
        #                  manuellement à partir de la commande copiée dans le
        #                  presse-papier...
        opts = dict()
        opts['backup']          = False
        opts['force']           = True
        opts['dev_nb']          = False
        opts['control_famille'] = False
        opts['stop_on_error']   = False
        opts['mails']           = False
        opts['test_and_valid']  = False

        self.opts = opts


    def exec(self, acqid, cmd):
        """ Exécute la commande 'cmd' sur l'acqid 'acqid'.
            Retourne : le code de retour de l'opéateur (0 = ok)
                       la chaine de diagnotique retournée par l'opérateur
                       les données calculée par l'opérateur.
        """
        # DBG print(f"=== Call_Oper::exec({acqid}, {cmd}")

        logger.log(logging.AIDA, '')    # saut de ligne...
        logger.debug(f"Call_Oper::exec({acqid}, {cmd}")

        # parser l'instruction et récupérer le type (C ou python) de
        # l'opérateur
        try:
            oper_name, args_brut, args_opt, args_HDR = parse_instruction(cmd)
            oper_type = get_OperType(oper_name, opers_C_names, opers_PY_names)
        except Exception as e:
            diag = f"erreur de commande : {e}"
            return 1, diag, None

        if args_HDR:
            diag = f"arguments de type 'args_HDR' inattendus : '{ args_HDR}'"
            return 1, diag, None


        # initialisation de la variable 'oper' en fonction du type
        # d'opérateur
        if oper_type == OperTypes.C:
            oper = opers_C[oper_name]
            if args_opt:
                diag = f"l'opérateur '{oper_name}' ne prend " +\
                       f"pas d'argument optionnel ('{args_opt}')"
                return 1, diag, None
        else:
            # ATTENTION : faire une copie profonde pour pouvoir
            # ajouter des atributs de l'instruction à la
            # description de l'opérateur
            oper = copy.deepcopy(opers_PY[oper_name])

        oper.line_nb  = 1
        oper.line_cmd = cmd
        oper.adc_opts = self.opts
        oper.args_HDR = args_HDR

        # exécution
        if oper_type == OperTypes.C:
            try:
                ret, diag, data = oper.exec_line_no_write(acqid, args_brut)
            except Exception as e:
                diag = f"erreur d'exécution : {e}"
                return 1, diag, None
        else:
            try:
                ret, diag, data = oper.exec_line_no_write(acqid, args_brut, args_opt)
            except Exception as e:
                diag = f"erreur d'exécution : {e}"
                return 1, diag, None

        return ret, diag, data


#if __name__ == '__main__':
#
#    import AIDA_logger
#    logger = AIDA_logger.configure_AIDA_logging('test')
#
#
#    call_oper = Call_Oper()
#
#    print("\n=== Opérateur Python")
#    acqid = 'Tf230001'
#    cmd   = "Log_flt (chm_conco2_umolmol_licor_%1800, 1.0, 1.0, 0.0, 0.0, ' ', ' ', ' ', " +\
#                             "chm_conco2_umolmol_licor_aitodata_%1800)"
#    ret, diag, data = call_oper.exec(acqid, cmd)
#    print(f"Exec :")
#    print(f"  - acqid = {acqid}")
#    print(f"  - cmd   = {cmd}")
#    print(f"RET  :")
#    print(f"  - ret  = {ret}")
#    print(f"  - diag = {diag}")
#    print(f"  - data = {data}")
#    print(f"  - data[0][0:5] = {data[0][0:5]}")
#    input('...')
#
#    print("\n=== Opérateur Python")
#    acqid = 'Tf230001'
#    cmd   = 'Filtre_RC_sdph (chm_conco2_d_li7500_Eti_20, 0.0, 0, ' +\
#                             'chm_conco2_d_li7500_Eti_aitodata_20)'
#    ret, diag, data = call_oper.exec(acqid, cmd)
#    print(f"Exec :")
#    print(f"  - acqid = {acqid}")
#    print(f"  - cmd   = {cmd}")
#    print(f"RET  :")
#    print(f"  - ret  = {ret}")
#    print(f"  - diag = {diag}")
#    print(f"  - data = {data}")
#    print(f"  - data[0][0:5] = {data[0][0:5]}")
#    input('...')
#
#
#    print("\n=== Opérateur Mixte")
#    acqid = 'Tf230001'
#    cmd   = 'Comble_spline (chm_conco2_d_li7500_Eti_20, 5, ' +\
#            'chm_conco2_d_li7500_Eti_aitodata_20, ' +\
#            'chm_conco2_d_li7500_Eti_aitoctl_20)'
#    ret, diag, data = call_oper.exec(acqid, cmd)
#    print(f"Exec :")
#    print(f"  - acqid = {acqid}")
#    print(f"  - cmd   = {cmd}")
#    print(f"RET  :")
#    print(f"  - ret  = {ret}")
#    print(f"  - diag = {diag}")
#    print(f"  - data = {data}")
#    input('...')
#
#
#    print("\n=== Opérateur C")
#    acqid = 'Tf230001'
#    cmd   = 'Decale (chm_conco2_d_li7500_Eti_20, 20.0, 0.0, ' +\
#            'chm_conco2_d_li7500_Eti_aitodata_20)'
#    ret, diag, data = call_oper.exec(acqid, cmd)
#    print(f"Exec :")
#    print(f"  - acqid = {acqid}")
#    print(f"  - cmd   = {cmd}")
#    print(f"RET  :")
#    print(f"  - ret  = {ret}")
#    print(f"  - diag = {diag}")
#    print(f"  - data = {data}")
#    input('...')


