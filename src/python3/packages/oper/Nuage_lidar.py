#!/usr/bin/env python3

"""
    ADC : Opérateur Nuage_lidar
"""

import sys
import os
import logging
import numpy as np

logger = logging.getLogger('adc')

PYTHON_X_Y = 'python%d.%d' % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(os.getenv('AIDA_HOME'), 'lib', PYTHON_X_Y))

import AIDA
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
def Nuage_lidar(Pr, Thr1, Thr2, Gates, zmin):
    """
    Trouve les bases, peaks et top d'un profil lidar PrF
    basé sur Pal, 1992 - Adapté par Mortier A.

    Input :
        Pr    : signal lidar (matrice)
        Thr1  : seuil de détection (coefficient)
        Thr2  : seuil de détection (coefficient)
        Gates : altitudes réelles des portes du lidar (m).
        zmin  : altitude en dessous de laquelle on ne détecte pas de nuage (m).

    Output :
        base : altitude des bases des nuages (m).
        peak : altitude des maximums de rétro-diffusion (m).
        top  : altitude des sommets des nuages (m).
        flag : nombre de couches détectées (m).

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Febr 2018

    sources :
    script scilab ecrit par le LOA.
    """
    logger.debug("Nuage_lidar : debut")

    # récupération des arguments
    Pr_header     = Pr.attributes
    Pr_data       = Pr.data.data

    Gates_header  = Gates.attributes
    Gates_data    = Gates.data.data


    # préparation des arguments pour la fonction de calcul

    # appel de la fonction de calcul
    base_data, peak_data, top_data, flag_data = \
        calcul.Nuage_lidar.Nuage_lidar(Pr_data, Thr1, Thr2, Gates_data, zmin)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs

    base_header = default_out_header.copy()
    base_header['name']         = 'Altitude des bases des nuages'
    base_header['english_name'] = 'Base cloud layer altitude'
    base_header['unit']         = 'm'
    base_header['freq_ech']     = f"{Pr_header['freq_ech']}"
    base_header['ref_time']     = f"{Pr_header['ref_time']}"
    base_header['misval']       = f"{Pr_header['misval']}"
    base_header['famille']      = 'altitude'
    base_header['dim_array']    = 6

    peak_header = default_out_header.copy()
    peak_header['name']         = 'Altitude des nuages'
    peak_header['english_name'] = 'Cloud altitude'
    peak_header['unit']         = 'm'
    peak_header['freq_ech']     = f"{Pr_header['freq_ech']}"
    peak_header['ref_time']     = f"{Pr_header['ref_time']}"
    peak_header['misval']       = f"{Pr_header['misval']}"
    peak_header['famille']      = 'altitude'
    peak_header['dim_array']    = 6

    top_header = default_out_header.copy()
    top_header['name']         = 'Altitude des sommets des nuages'
    top_header['english_name'] = 'Top cloud layer altitude'
    top_header['unit']         = 'm'
    top_header['freq_ech']     = f"{Pr_header['freq_ech']}"
    top_header['ref_time']     = f"{Pr_header['ref_time']}"
    top_header['misval']       = f"{Pr_header['misval']}"
    top_header['famille']      = 'altitude'
    top_header['dim_array']    = 6

    flag_header = default_out_header.copy()
    flag_header['name']         = 'Flag presence couche nuageuse'
    flag_header['english_name'] = 'Cloud indicator flag'
    flag_header['freq_ech']     = f"{Pr_header['freq_ech']}"
    flag_header['ref_time']     = f"{Pr_header['ref_time']}"
    flag_header['misval']       = f"{Pr_header['misval']}"
    flag_header['unit']         = 'unitless'
    flag_header['famille']      = 'controle'
    flag_header['dim_array']    = 1


    diag = {'CodeRet' : 0,
            'DiagExec': f"Nuage_lidar : ({len(Pr_data)} ech.)"
           }

    return [base_header, peak_header, top_header, flag_header], \
           [base_data  , peak_data  , top_data  , flag_data  ], \
           diag


#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Nuage_lidar': {
        'Args': [
           {'Id': 'Pr'        , 'categorie': 'VECTOR_IN'   },
           {'Id': 'Thr1'      , 'categorie': 'COEFFICIENT' },
           {'Id': 'Thr2'      , 'categorie': 'COEFFICIENT' },
           {'Id': 'Gates'     , 'categorie': 'VECTOR_IN'   },
           {'Id': 'zmin'      , 'categorie': 'COEFFICIENT' },
           {'Id': 'base'      , 'categorie': 'VECTOR_OUT'  },
           {'Id': 'peak'      , 'categorie': 'VECTOR_OUT'  },
           {'Id': 'top'       , 'categorie': 'VECTOR_OUT'  },
           {'Id': 'flag'      , 'categorie': 'VECTOR_OUT'  },
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

    # Nuage_lidar (
    #   opt_pr2_lid_filtre_%60,
    #   $Arg1.array_dim,
    #   10,
    #   4,
    #   alt_gate_lid_%60,
    #   300,
    #   alt_nuagelidar_base_%60,
    #   alt_nuagelidar_peak_%60,
    #   alt_nuagelidar_top_%60,
    #   ctl_flg_nuagelidar_%60
    #)

    # sur de vrais vecteurs
    acqid = 'fs200013'
    logger.info(f'=== {acqid}')
    Pr         = AIDA.VectorMask(acqid, 'opt_pr2_lid_filtre_%60')
    Thr1       = 10
    Thr2       = 4
    Gates      = AIDA.VectorMask(acqid, 'alt_gate_lid_%60')
    zmin       = 300

    # appel de l'opérateur
    logger.info('*** appel de Nuage_lidar')
    headers, datas, diag = Nuage_lidar (Pr, Thr1, Thr2, Gates, zmin)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in header.items():
            if key == 'bornes' and len(value) > 60:
                logger.info(f"  - {key:15s} = {value[:60]}...")
            else:
                logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data[0:5] = {data[0:5]}")
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
