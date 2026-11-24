#!/usr/bin/env python3

"""
AIDAcalc (ou adc)
=================
    Transformation des appels FVB en ADC pour les anciens opérateurs mixtes.

    Les appels pour FVB nécessitent plus d'arguments que les appels pour ADC.
    => il faut supprimer un certains nombre d'arguments.
    La 'transformation' est un dictionnaire dont les clés sont le nom des
    opérateurs et les valeurs une liste de numéro d'argument à supprimer (la
    numérotation commence à 0).
    On ne supprime pas les arguments de type VECTOR / DIR_OUT.
    Ex :
                      arg[0]    [1]      [2]            [3]       [4]        [5]       [6]
    FVB : MoyEch_tps_bnds(X_in, time_in, tolerance_mnq, time_out, time_bnds, size_out, X_out)
    ADC : MoyEch_tps_bnds(X_in,          tolerance_mnq, time_out,                      X_out)
    => 'MoyEch_tps_bnds': [1, 4, 5]
"""



fvb2adc = {
        'MoyEch_tps_bnds'          : [1, 4, 5],
        'Filtre_RC_sdph'           : [1],
        'SomEch_tps_bnds'          : [1, 4, 5],
        'MinEch_tps_bnds'          : [1, 4, 5],
        'MaxEch_tps_bnds'          : [1, 4, 5],
        'StdEch_tps_bnds'          : [1, 4, 5],
        'MoyHarmEch_tps_bnds'      : [1, 4, 5],
        'MoyHarmInvEch_tps_bnds'   : [1, 4, 5],
        'PourcentSeuilEch_tps_bnds': [1, 4, 5],
        'PercentileEch_tps_bnds'   : [1, 4, 5],
        'PercentileInvEch_tps_bnds': [1, 4, 5],
        'QuantileEch_tps_bnds'     : [1, 4, 5],
        'MoyInvEch_tps_bnds'       : [1, 4, 5],
        'StdInvEch_tps_bnds'       : [1, 4, 5],
        'PresenceNuageEch_tps_bnds': [3, 6, 7],
        'HbnMoyInvEch_tps_bnds'    : [3, 6, 7],
        'Covar_XY_max'             : [2],
        'CovarXYmax_tps_bnds'      : [2, 5, 6],
        'CorFlux_spectral'         : [1, 2],
        'Flag_to_percent'          : [4],
        'Filtre_spectral_1D'       : [1, 3],
        'Nuage_lidar'              : [1],
        'Lidar_Zref_ecart'         : [2],
        'Lidar_Zref'               : [2],
        'Qualite_profil_lidar'     : [2],
        'Synchro_spline'           : [1, 5],
        'Inv_Klett_sa'             : [1, 2],
        'Inv_Klett_aod'            : [1, 2],
        'Profil_Diff_Mol'          : [1, 3],
        'Profil_Diff_Mol_reel'     : [1, 3, 7],
        'ProfilMobile2geo_1D'      : [1, 2],
        'Filtre_RC_sdph_paliers'   : [1, 2, 6, 7],
        'Ech_tps_impos'            : [1, 4],
        'TKE'                      : [3],
        'VarEch_tps_bnds'          : [1, 4, 5],
}
