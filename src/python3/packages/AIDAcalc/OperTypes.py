#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Type des opérateurs : C ou Python
"""

from enum import Enum


# type d'opérateur
class OperTypes (Enum):
    C   = 0
    PY  = 1

def get_OperType(oper_name, oper_c_names, oper_py_names):
    """ Retourne le OperType pour oper_name.

        Raise une exception si l'opérateur n'est trouvé ni dans opers_PY_names,
        ni dans opers_C_names.

        :param str()     oper_name    : nom de l'opérateur
        :param list()    oper_c_names : liste des noms d'opérateur C.
        :param list()    oper_py_names: liste des noms d'opérateur Python.

        :return: le type de oper_name
        :rtype: OperTypes()
    """
    # chercher d'abord dans les opérateurs Python pour by-passer les
    # opérateurs mixtes
    if oper_name in oper_py_names:
        oper_type = OperTypes.PY
    elif oper_name in oper_c_names:
        oper_type = OperTypes.C
    else:
        raise Exception (f"opérateur '{oper_name}' inconnu !")

    return oper_type

