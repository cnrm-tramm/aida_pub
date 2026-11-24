#!/usr/bin/env python3

import os
import sys
import numpy as np

aida_home = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(aida_home, 'lib', PYTHON_X_Y))
import AIDA


#################################
# FONCTION de CALCUL
####################

def ProfilMobile2geo_1D(bornes, vert_direction, roulis, tangage, altitude):
    """
        Convertit les coordonnées (altitude) d'un profil exprimées dans un
        repère mobile en coordonnées géographiques.

        Input :
            bornes         : tableau des bornes du vecteur d'entrée X.
            vert_direction : 1 si mesure vers le haut, -1 si mesure vers le bas.
            roulis         : donnée de roulis.
            tangage        : données de tangage.
            altitude       : données d'altitude.

        Output :
            altitude_x     : Altitude des mesures X.

        Auteur : @Météo-France CNRM/GMEI/TRAMM
    """
    # le tableau de bornes est un tableau de dimension [nb_z, 2]
    # on fait la moyenne des bornes
    bornes_moy = np.nanmean(bornes, axis=1)
    nb_z = len(bornes_moy)
    nb_val = len(roulis)

    # on convertit
    altitude_x = np.ones(nb_val*nb_z)*np.nan
    for i in range(nb_val):
        coro = np.cos(np.radians(roulis[i]))
        cota = np.cos(np.radians(tangage[i]))
        for k in range(nb_z):
            altitude_x[ i*nb_z + k] = \
                    altitude[i] + vert_direction * cota*coro * bornes_moy[k]

    return altitude_x


###################
# MAIN : test sur fs200013
# doit être dans "if __name__ == '__main__': ", sinon est excécuté lors du
# chargement dans ADC.
######
if __name__ == '__main__': 

    print("ProfilMobile2geo_1D.py :")
    
    # lecture des données d'entrée
    acqid = "fs200013"
    
    # les paramètres en entrée de l'opérateur
    p_x        = "opt_dclid1_raw_%60"
    p_roulis   = "att_rollaipov_Met_%60"
    p_tangage  = "att_pitchaipov_Met_%60"
    p_altitude = "alt_altaipov_Met_%60"
    
    # lecture des vecteurs
    data_x, time_x, header_x                      = AIDA.read_datas(acqid, p_x)
    data_roulis, time_roulis, header_roulis       = AIDA.read_datas(acqid, p_roulis)
    data_tangage, time_tangage, header_tangage    = AIDA.read_datas(acqid, p_tangage)
    data_altitude, time_altitude, header_altitude = AIDA.read_datas(acqid, p_altitude)
    
    # on récupère les bornes de p_x (qui n'est d'ailleurs utilisé que pour ça)
    str_bornes = header_x['bornes']
    bornes     = AIDA.strBornes_to_array(str_bornes, acqid)
    
    # on appelle la fonction de calcul
    vert_direction = 1
    data_out = ProfilMobile2geo_1D(bornes[0],
                                   vert_direction,
                                   data_roulis,
                                   data_tangage,
                                   data_altitude)
    
    # on écrit le vecteur résultat : on utilise le header du vecteur
    # produit actuellement par fvb
    data_alt_gate, time_alt_gate, header_alt_gate = AIDA.read_datas(acqid, "alt_gate_lid_%60")
    
    vect_out = AIDA.Vector(acqid, "alt_gate_lid_new_%60", attributes=header_alt_gate, data=data_out)
    vect_out.write(backup=False, force=True)
    
    print(f"--> écriture de {vect_out.attributes['#hdr_name']}")
    print(f"    dans {vect_out.storage_path}")

