#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Gestion des données transférées par les opérateurs C dans la variables
    globale de la liboper : "Meta_Out"


  Utilisation de la globale C Meta_Out
  ------------------------------------
  A ce jour la variable Meta_Out n'est utilisée que dans :

  - Cospectre_Chaleur_Moncrieff97.c  : Meta_Out[5].bornes    = bornes ;
  - Cospectre_Mouvement_Moncrieff97.c: Meta_Out[5].bornes    = bornes ;
  - Cre_time_bnds_reg.c              : Meta_Out[4].time_bnds = (char *)ArgList[3] ;
  - FT_analytique_Moncrieff.c        : Meta_Out[11].bornes   = bornes ;


  La variable Meta_Out n'est lue que pour les opérateurs pur-C (les opérateurs
  mixtes C/Python sont réécrits en python pur et n'utilisent plus cette
  variable)
  - Cospectre_Chaleur_Moncrieff97.c  : opérateur mixte C/Python
  - Cospectre_Mouvement_Moncrieff97.c: opérateur mixte C/Python
  - Cre_time_bnds_reg.c              : opérateur mixte C
  - FT_analytique_Moncrieff.c        : opérateur mixte C/Python

  Définition de la globale variable C Meta_Out : lib/oper/struct_oper.h :
  --------------------------------------------

  #define FIL_MAX_ARG 60

  Arg_profil Meta_Out[FIL_MAX_ARG];

  typedef struct
    {
      sens direction;
      CATEGORIE categorie;
      AIDA_TYPE_CODE typ;
      char *array_shape;
      char *array_dim;
      char *bornes;
      char *unit_bornes;
      char *unite;
      char *name;        /* Seulement pour les VECTOR, nom_long dans l'en-tete;*/
      char *en_name;     /* version anglaise du champ précédent. */
      char *type_sample; /* Seulement pour les VECTOR */
      char *sample;      /* Seulement pour les VECTOR */
      char *ref_time;    /* Seulement pour les VECTOR */
      char *time_bnds;   /* Seulement pour les VECTOR */
      char *famille;     /* Seulement pour les VECTOR */
      char *misval;      /* Seulement pour les VECTOR */
      char *NbVal;       /* Seulement pour les VECTOR */
    } Arg_profil ;
"""

import sys
import os
import logging
import ctypes as ct


logger = logging.getLogger('adc')


# ATTENTION : la variable AL est utilisée plus loin pour la liboper
PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
AL         = os.path.join(os.getenv('AIDA_HOME'), 'lib')
sys.path.append(os.path.join(AL, PYTHON_X_Y))

from fct_messages import info, warning, stop_error, result, wait_user


# liboper
import ctypes as ct
path_lib_oper = os.path.join(AL, 'liboper.so')
lib_oper      = ct.CDLL(path_lib_oper)

# traduction de la structure C Arg_profil
class struct_Arg_profil(ct.Structure):
    _fields_ = [("direction"   , ct.c_int   ),   # enum -> int pour simplifier
                ("categorie"   , ct.c_int   ),   # enum -> int pour simplifier
                ("typ"         , ct.c_int   ),   # enum -> int pour simplifier
                ("array_shape" , ct.c_char_p),
                ("array_dim"   , ct.c_char_p),
                ("bornes"      , ct.c_char_p),
                ("unit_bornes" , ct.c_char_p),
                ("unite"       , ct.c_char_p),
                ("name"        , ct.c_char_p),
                ("en_name"     , ct.c_char_p),
                ("type_sample" , ct.c_char_p),
                ("sample"      , ct.c_char_p),
                ("ref_time"    , ct.c_char_p),
                ("time_bnds"   , ct.c_char_p),
                ("famille"     , ct.c_char_p),
                ("misval"      , ct.c_char_p),
                ("NbVal"       , ct.c_char_p),
               ]


class Meta_Out():
    """ Gestion des données transférées par les OP_xxx dans la variable globale
        de la liboper : "Meta_Out"
    """
    def __init__(self):
        """
            La définition de la variable globale C Meta_Out est :
              Arg_profil Meta_Out[FIL_MAX_ARG];
              avec #define FIL_MAX_ARG 60
            Je ne pense pas que l'on puisse récupérer simplement le FIL_MAX_ARG.
            Cependant, il y a peut de chance que ce '#define' soit modifié
            => je le définit en dur :

        """
        FIL_MAX_ARG = 60
        Meta_Out = struct_Arg_profil * FIL_MAX_ARG

        # récupération de la variable globale C Meta_Out
        self.meta_out = Meta_Out.in_dll(lib_oper, "Meta_Out")

        # pour faciliter le travail sur meta_out :
        self.attributs = [ f for f, v in struct_Arg_profil._fields_ \
                                if v == ct.c_char_p]


    def restricted_get_variables(self, index):
        """ Retourne un dictionnaire des valeurs de la globale C Meta_Out.
            Seules les valeurs de type "char *" positionnées sont retournées.

            Les clés du dictionnaire sont les noms dans la variable C Meta_Out.
        """
        ret = dict()
        for attribut in self.attributs:
            attr = getattr(self.meta_out[index], attribut)
            if attr:
                try:
                    ret[attribut] = attr.decode().replace('"', '')
                except UnicodeDecodeError as e:
                    ret[attribut] = attr.decode('iso8859-15').replace('"', '')

        return ret


if __name__ == '__main__':

    meta_out = Meta_Out()

    # les attribut de la classe
    print("Liste des attribut d'une structure struct_Arg_profil :")
    print(meta_out.attributs)

    vals_for_header = meta_out.restricted_get_variables(0)


