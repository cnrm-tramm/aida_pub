#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    ADC : Opérateur Rotat_2D_rep_vent_moy_paliers
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
def Rotat_2D_rep_vent_moy_paliers(u, v, w, time_paliers):
    """
    Calcul des 3 composantes du vecteur vent dans un repère porté par le vent moyen,
    qui vérifie (si U est le module du vent) :
        umoy=U
        vmoy=0
        wmoy=0
    Ce calcul est effectué sur et entre chaque palier défini par l'attribut 
    time_bnds du vecteur time_paliers.


    Input :
        u               any     première composante horizontale du vent
        v               idem u  seconde composante horizontale du vent
        u               idem u  composante verticale du vent
        time_paliers    second  base de temps qui définit les paliers

    Output :
        u_rot           any     première composante horizontale du vent selon U moyen
        v_rot           idem u  seconde composante horizontale du vent dans le repère UVW moyen
        w_rot           idem u  composante verticale du vent dans le repère UVW moyen

    Auteur : @Météo-France CNRM/GMEI/TRAMM - Nov 2023
    """
    logger.debug("Rotat_2D_rep_vent_moy_paliers : debut")

    # récupération des arguments
    u_header     = u.attributes
    u_data       = u.data.data
    
    v_header     = v.attributes
    v_data       = v.data.data
    
    w_header     = w.attributes
    w_data       = w.data.data
    
    time_paliers_header = time_paliers.attributes
    time_paliers_data   = time_paliers.data.data
    
    #
    # préparation des arguments pour la fonction de calcul
    #
    # - récupération des time_bnds (bornes_temps) pour le vecteur time_paliers
    acqid     = time_paliers.acq_id
    bnds      = AIDA.time_to_data_bnds(acqid, time_paliers.name)
    if bnds is None:
        raise Exception ("opérateur Rotat_2D_rep_vent_moy_paliers : problème de lecture " +
                         f"des bornes du vecteur '{time_paliers.name}'")
                         
    # - récupération des données du vecteur temps de u
    time_u_data   = u.timedata()
    
    #
    # appel de la fonction de calcul
    #
    u_out_data, v_out_data, w_out_data, codret = \
        calcul.Rotat_2D_rep_vent_moy_paliers.Rotat_2D_rep_vent_moy_paliers(u_data, v_data, w_data, time_u_data, bnds)

    # préparation du retour
    # ATTENTION : les champs 'name et 'english_name' ne sont pas obligatoires
    # => passer par la méthode 'get_names' des vecteurs
    u_fr_name, u_en_name = u.get_names()
    u_out_header = default_out_header.copy()
    u_out_header['name']         = f"{u_fr_name} après double rotation"
    u_out_header['english_name'] = f"{u_en_name} after double rotation"
    u_out_header['unit']         = f"{u_header['unit']}"
    u_out_header['freq_ech']     = f"{u_header['freq_ech']}"
    u_out_header['ref_time']     = f"{u_header['ref_time']}"
    u_out_header['misval']       = f"{u_header['misval']}"
    u_out_header['dim_array']    = f"{u_header['dim_array']}"
    if u_data.ndim > 1 :
        u_out_header['bornes']    = f"{u_header['bornes']}"
        u_out_header['unit_bornes']    = f"{u_header['unit_bornes']}"
    
    v_fr_name, v_en_name = v.get_names()
    v_out_header = default_out_header.copy()
    v_out_header['name']         = f"{v_fr_name} après double rotation"
    v_out_header['english_name'] = f"{v_en_name} after double rotation"
    v_out_header['unit']         = f"{v_header['unit']}"
    v_out_header['freq_ech']     = f"{v_header['freq_ech']}"
    v_out_header['ref_time']     = f"{v_header['ref_time']}"
    v_out_header['misval']       = f"{v_header['misval']}"
    v_out_header['dim_array']    = f"{v_header['dim_array']}"
    if v_data.ndim > 1 :
        v_out_header['bornes']    = f"{v_header['bornes']}"
        v_out_header['unit_bornes']    = f"{v_header['unit_bornes']}"
    
    w_fr_name, w_en_name = w.get_names()
    w_out_header = default_out_header.copy()
    w_out_header['name']         = f"{w_fr_name} après double rotation"
    w_out_header['english_name'] = f"{w_en_name} after double rotation"
    w_out_header['unit']         = f"{w_header['unit']}"
    w_out_header['freq_ech']     = f"{w_header['freq_ech']}"
    w_out_header['ref_time']     = f"{w_header['ref_time']}"
    w_out_header['misval']       = f"{w_header['misval']}"
    w_out_header['dim_array']    = f"{w_header['dim_array']}"  
    if w_data.ndim > 1 :
        w_out_header['bornes']    = f"{w_header['bornes']}"
        w_out_header['unit_bornes']    = f"{w_header['unit_bornes']}"      

    if codret == 0 :
        str_diagexec = "OK"
    else :
        str_diagexec = " ERREUR : erreur non identifiée dans la fonction de calcul."
    diag = {'CodeRet' : codret,
            'DiagExec': f"Rotat_2D_rep_vent_moy_paliers : (u:{u_data.shape} ech., v:{v_data.shape} ech., w:{w_data.shape} ech.) : {str_diagexec}"
           }
    
    return [u_out_header, v_out_header, w_out_header], \
           [u_out_data, v_out_data, w_out_data], \
           diag
    
#==============================================================================
# Description des arguments attendus par l'opérateur.
#==============================================================================
desc_oper = {
    'Rotat_2D_rep_vent_moy_paliers': {
        'Args': [
           {'Id': 'u'           , 'categorie': 'VECTOR_IN'   },
           {'Id': 'v'           , 'categorie': 'VECTOR_IN'   },
           {'Id': 'w'           , 'categorie': 'VECTOR_IN'   },
           {'Id': 'time_paliers', 'categorie': 'VECTOR_IN'   },
           {'Id': 'u_out'       , 'categorie': 'VECTOR_OUT'  },
           {'Id': 'v_out'       , 'categorie': 'VECTOR_OUT'  },
           {'Id': 'w_out'       , 'categorie': 'VECTOR_OUT'  }
        ]
    }
}


#==============================================================================
# Test de l'opérateur
#==============================================================================
if __name__ == '__main__':

    # ici, on est en direct, et non pas importé par adc
    # => le logger 'adc' n'existe pas
    # => on définit un logger basic
    if len(logger.handlers) == 0:
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)s : %(message)s')
        logging.basicConfig(level=logging.INFO, format='%(levelname)s : %(message)s')


    #acqid = 'ls230229'
    #logger.info(f'=== {acqid}')
    #u = AIDA.VectorMask(acqid, 'ven_e_20')
    #v = AIDA.VectorMask(acqid, 'ven_n_20')
    #w = AIDA.VectorMask(acqid, 'ven_u_20')
    #time_paliers = AIDA.VectorMask(acqid, 'rft_time_seq_0')
    
    acqid = 'Ce210183'
    logger.info(f'=== {acqid}')
    u = AIDA.VectorMask(acqid, 'ven_u_gillv3_50m_Dec_20')
    v = AIDA.VectorMask(acqid, 'ven_v_gillv3_50m_Dec_20')
    w = AIDA.VectorMask(acqid, 'ven_w_gillv3_50m_Dec_20')
    time_paliers = AIDA.VectorMask(acqid, 'rft_time_REG_%1800')

    acqid = 'Ce210183'
    logger.info(f'=== {acqid}')
    u = AIDA.VectorMask(acqid, 'ven_u_windcube_WFR_%4')
    v = AIDA.VectorMask(acqid, 'ven_v_windcube_WFR_%4')
    w = AIDA.VectorMask(acqid, 'ven_w_windcubeV_Eti_%4')
    time_paliers = AIDA.VectorMask(acqid, 'rft_time_REG_%1800')

    # appel de l'opérateur
    logger.info('*** appel de Rotat_2D_rep_vent_moy_paliers')
    headers, datas, diag = Rotat_2D_rep_vent_moy_paliers (u, v, w, time_paliers)

    # résultat
    logger.info("*** les champs #hdr_name, date_creation, fct_origine, vol seront mise à jour par ADC et AIDA.py *** \n")
    for header, data in zip(headers, datas):
        logger.info("header : ")
        for key, value in header.items():
            logger.info(f"  - {key:15s} = {value}")
        logger.info(f"data[0:500] = {data[0:500]}")
        input("...[ENTER] pour continuer ")

    logger.info("Diagnostique :")
    for key, value in diag.items():
        logger.info(f"  - {key} = {value}")
