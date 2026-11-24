#!/usr/bin/env python3

"""
Gestion des constantes AIDA.

    Pour plus de détail, se reporter à src/C/AIDAcalc/symtab.c.

    lancer avec l'option -l permet de lister les constantes normalisées AIDA.

NOTE :
    Au sein d'un programme, pour avoir accés directement aux constantes
    (ex : pi), sans passer par : Constantes.AIDA_Csts['pi'] faire :
        import Constantes
        locals().update(Constantes.AIDA_Csts)
    (voir AIDAcalc.py)
"""

import sys
import os

AIDA_Csts = {
'ieeefloat64_max'         : 1.7976931348623157e+308       ,
'ieeefloat32_max'         : 3.40282347e+38                ,
'int32_max'               : 2147483647                    ,
'int16_max'               : 32767                         ,
'pi'                      : 3.14159265358979323846        ,
'DegRad'                  : 3.14159265358979323846 / 180.0,
'RadDeg'                  : 180.0 / 3.14159265358979323846,
'KtMs'                    : 1852.0 / 3600.0               ,
'FtmMs'                   : 0.3048 / 60.0                 ,
'FtM'                     : 0.3048                        ,
'g'                       : 9.806650                      ,
'T0'                      : 273.15                        ,
'sigma'                   : 5.67051e-8                    ,
'sigma_LOA'               : 5.6698e-8                     ,
'R'                       : 8.314510                      ,
'Ra'                      : 8.314510 / 0.028964           ,
'Rv'                      : 461.51                        ,
'cpa'                     : 1004.685                      ,
'cva'                     : 717.64                        ,
'SA_PMS_OAP230Y'          : [871.215, 1525.400, 1472.800, 1420.200, 1367.600,
                             1315.000, 1262.400, 1209.800, 1157.200, 1104.600,
                             1052.000, 999.400, 946.800, 894.200, 841.600,
                             789.000, 736.400, 683.800, 631.200, 578.600,
                             526.000, 473.400, 420.800, 368.200, 315.600,
                             263.000, 210.400, 157.800, 105.200, 52.600],
'SA_PMS_OAP200X_INSU'     : [0.17, 1.26, 3.61, 6.62, 9.60, 12.86, 16.27, 18.30,
                             17.08, 15.86, 14.64, 13.42, 12.20, 10.98, 9.76],
'SA_PMS_OAP200X_LaMP'     : [0.11, 1.04, 3.20, 6.08, 9.00, 12.24, 15.68, 18.30,
                             17.08, 15.86, 14.64, 13.42, 12.20, 10.98, 9.76],
'FSSP300_std_mid_diam'    : [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7625,
                             1.15, 1.9, 2.8, 3.7, 4.6, 5.5, 6.4, 7.3, 8.2, 9.1,
                             10.025, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
'SPP200_std_mid_diam'     : [0.095, 0.105, 0.115, 0.125, 0.135, 0.145, 0.155,
                             0.165, 0.175, 0.19, 0.21, 0.23, 0.25, 0.27, 0.29,
                             0.35, 0.45, 0.55, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7,
                             1.9, 2.1, 2.3, 2.5, 2.7, 2.9],
'PCASP_std_mid_diam'      : [0.11, 0.13, 0.155, 0.185, 0.225, 0.275, 0.350,
                             0.450, 0.6, 0.8, 1.05, 1.35, 1.75, 2.25, 2.75],
'GRIMM1_109_std_mid_diam' : [0.265, 0.29, 0.325, 0.375, 0.425, 0.475, 0.54,
                             0.615, 0.675, 0.75, 0.9, 1.15, 1.45, 1.8, 2.25,
                             2.75, 3.25, 3.75, 4.5, 5.775, 7.025, 8, 9.25,
                             11.25, 13.75, 16.25, 18.75, 22.5, 27.5, 31, 33.],
}

# descritpion des constantes AIDA
AIDA_Csts_desc = {
'ieeefloat64_max'         : "maximum pour une valeur de type : float64",
'ieeefloat32_max'         : "maximum pour une valeur de type : float32",
'int32_max'               : "maximum pour une valeur de type : int32"  ,
'int16_max'               : "maximum pour une valeur de type : int16"  ,
'pi'                      : "rapport constant de la circonférence d’un cercle à son diamètre dans un plan euclidien",
'DegRad'                  : "coéfficient de conversion : degrees -> radians",
'RadDeg'                  : "coéfficient de conversion : radians -> degrees",
'KtMs'                    : "coéfficient de conversion : kt -> m/s",
'FtmMs'                   : "coéfficient de conversion : foot/minute -> meter/second",
'FtM'                     : "coéfficient de conversion : foot -> meter",
'g'                       : "accélération de la pesanteur",
'T0'                      : "zéro absolu (limite basse de l'échelle de température thermodynamique)",
'sigma'                   : "constante Stefan-Boltzmann en W/(m2*K4)",
'sigma_LOA'               : "constante Stefan-Boltzmann  en W/(m2*K4) (utilisée au LOA)",
'R'                       : "constante molaire des gaz parfaits en J/(K*mol)",
'Ra'                      : "constante spécifique de l'air sec, en J/(K*kg) (= R/Ma)",
'Rv'                      : "constante spécifique de la vapeur d'eau, en J/(K*kg) (= R/Mv)",
'cpa'                     : "chaleur massique à P constante de l'air SEC en J/(K*kg)",
'cva'                     : "chaleur massique à V constante de l'air SEC en J/(K*kg)",
'SA_PMS_OAP230Y'          : "Sampling Area en mm2 (calcul de F. Burnet -novembre 2007- selon la documentation constructeur)",
'SA_PMS_OAP200X_INSU'     : "SA_PMS_OAP200X_INSU",
'SA_PMS_OAP200X_LaMP'     : "Sampling Section en mm2",
'FSSP300_std_mid_diam'    : "MidPoint_diameter_std_FSSP300 en µm",
'SPP200_std_mid_diam'     : "MidPoint_diameter_std_SPP200 (PCASP moderne) en µm",
'PCASP_std_mid_diam'      : "MidPoint_diameter_std_PCASP en µm",
'GRIMM1_109_std_mid_diam' : "MidPoint_diameter_std_GRIMM_1.109 en µm",
}


if __name__ == '__main__':

    if len(sys.argv) > 1:
        # liste des constantes AIDA
        if sys.argv[1] == '-l':
            print("\nConstantes AIDA :")
            for name, value in AIDA_Csts.items():
                print(f"- {name:s} :")
                print(f"    {value}")
                print(f"    {AIDA_Csts_desc[name]}\n")

            sys.exit(1)

