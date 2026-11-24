#!/usr/bin/env python3

"""
    ADC : Opérateur ITC_model_Foken_zvar
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
def ITC_model_Foken_zvar(Ustar, LMO, Z, Hc, Lat):
    """
    Calcule la caracteristique integrale de la turbulence
    (Integral Turbulent Characteristis en anglais) à partir 
    des modèles fournis par Foken, avec une hauteur de mesure variable.

    Input :
        Ustar  : Vitesse de frottement (m/s)
        LMO    : Longueur de Monin-Obukhov (m)
        Z      : Hauteur de mesure (m)
        Hc     : Hauteur de la canopée (m)
        Lat    : Latitude (degres decimal)

    Output :
        ITCm_U : Caracteristique integrale de la turbulence selon U 
        ITCm_W : Caracteristique integrale de la turbulence selon W 
        ITCm_T : Caracteristique integrale de la turbulence selon T

    Auteur : @Météo-France CNRM/GMEI/TRAMM - avril 2023
    """
    logger.debug("ITC_model_Foken_zvar : debut")

    # récupération des arguments
    Ustar_header = Ustar.attributes
    Ustar_data   = Ustar.data

    LMO_header = LMO.attributes
    LMO_data   = LMO.data

    Z_header = Z.attributes
    Z_data   = Z.data

    # préparation des arguments pour la fonction de calcul

    # appel de la fonction de calcul
    ITCm_U, ITCm_W, ITCm_T = calcul.ITC_model_Foken_zvar.ITC_model_Foken_zvar(Ustar_data, LMO_data, Z_data, Hc, Lat)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    ITCm_U_header                 = default_out_header.copy() 
    ITCm_U_header['name']         = f"Caracteristique integrale turbulente de U calculee par le modele Foken"
    ITCm_U_header['english_name'] = f"Integral turbulence characteristics of U calculated with Foken model"
    ITCm_U_header['unit']         = f"unitless"
    ITCm_U_header['freq_ech']     = f"{Ustar_header['freq_ech']}"
    ITCm_U_header['ref_time']     = f"{Ustar_header['ref_time']}"
    ITCm_U_header['misval']       = f"{Ustar_header['misval']}"
    ITCm_U_header['famille']      = f"turbulence"
    
    ITCm_W_header                 = default_out_header.copy() 
    ITCm_W_header['name']         = f"Caracteristique integrale turbulente de W calculee par le modele Foken"
    ITCm_W_header['english_name'] = f"Integral turbulence characteristics of W calculated with Foken model"
    ITCm_W_header['unit']         = f"unitless"
    ITCm_W_header['freq_ech']     = f"{Ustar_header['freq_ech']}"
    ITCm_W_header['ref_time']     = f"{Ustar_header['ref_time']}"
    ITCm_W_header['misval']       = f"{Ustar_header['misval']}"
    ITCm_W_header['famille']      = f"turbulence"
    
    ITCm_T_header                 = default_out_header.copy() 
    ITCm_T_header['name']         = f"Caracteristique integrale turbulente de T calculee par le modele Foken"
    ITCm_T_header['english_name'] = f"Integral turbulence characteristics of T calculated with Foken model"
    ITCm_T_header['unit']         = f"unitless"
    ITCm_T_header['freq_ech']     = f"{Ustar_header['freq_ech']}"
    ITCm_T_header['ref_time']     = f"{Ustar_header['ref_time']}"
    ITCm_T_header['misval']       = f"{Ustar_header['misval']}"
    ITCm_T_header['famille']      = f"turbulence"


    diag = {'CodeRet' : 0,
            'DiagExec': f"ITC_model_Foken_zvar : ({len(Ustar_data)} ech.), " +
                        f"Hc = {Hc}, Lat = {Lat}"
           }

    return [ITCm_U_header, ITCm_W_header, ITCm_T_header], \
           [ITCm_U.data.astype(np.float32), ITCm_W.data.astype(np.float32), ITCm_T.data.astype(np.float32)], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'ITC_model_Foken_zvar': {
        'Args': [
            {'Id': 'Ustar'   , 'categorie': 'VECTOR_IN'   , 'unit': 'm/s'},
            {'Id': 'LMO'     , 'categorie': 'VECTOR_IN'   , 'unit': 'm'  },
            {'Id': 'Z'       , 'categorie': 'VECTOR_IN'   , 'unit': 'm'  },
            {'Id': 'Hc'      , 'categorie': 'COEFFICIENT' , 'unit': 'm'  },
            {'Id': 'Lat'     , 'categorie': 'COEFFICIENT'                },
            {'Id': 'ITCm_U'  , 'categorie': 'VECTOR_OUT'                 },
            {'Id': 'ITCm_W'  , 'categorie': 'VECTOR_OUT'                 },
            {'Id': 'ITCm_T'  , 'categorie': 'VECTOR_OUT'                 },
        ],
    },
}


#==============================================================================
# Test de l'opérateur
#==============================================================================
if __name__ == '__main__':

    import AIDA


    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')

    # création de Vector en mémoire
    acqid = 'Pl210226'
    logger.info(f'=== {acqid}')
    
    Ustar = AIDA.VectorMask(acqid, 'flx_ustar_Chb_%1800')
    LMO   = AIDA.VectorMask(acqid, 'trb_lmon_tson_gillh_Moa_%1800')
    Z     = AIDA.VectorMask(acqid, 'alt_haut_6m_%1800')
    Hc    = 27
    Lat   = 43.5975


    # appel de l'opérateur
    headers, datas, diag = ITC_model_Foken_zvar(Ustar, LMO, Z, Hc, Lat)

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
