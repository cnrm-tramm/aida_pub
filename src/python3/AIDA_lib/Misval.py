#!/usr/bin/env python3

"""
Gestion des valeurs de misval par défaut de AIDA.

    lancer avec l'option -l permet de lister les constantes normalisées AIDA.
"""

import sys
import os


# default misvals : il serait sans doute meilleur de passer par :
#   char_format = AIDA.np_string(VO_header['format'])[0]
#   puis selon char_format : np.finfo(char_format).max
#                       ou : np.iinfo(char_format).max
# conversion de type AIDA ->  misval
AIDA_type_misval = { 'Ieeefloat_32'  : '3.40282347e+38'         ,
                     'Ieeefloat_64'  : '1.7976931348623157e+308',
                     'Int_16'        : '32767'                  ,
                     'Int_32'        : '2147483647'             ,
                     'U_Int_8'       : '-9999'                  ,
                     'U_Int_16'      : '65535'                  ,
                     'U_Int_32'      : '-9999'                  ,
                     'U_Int_64'      : '-9999'                  ,
                     'String'        : '-9999'                  ,
                     'Hpfloat_32'    : '-9999'                  ,
                   }


if __name__ == '__main__':

    if len(sys.argv) > 1:
        # liste des constantes AIDA
        if sys.argv[1] == '-l':
            print("\nValeurs de misval par défaut de AIDA:")
            for name, value in AIDA_type_misval.items():
                print(f"- {name:12s} : {value}")

            sys.exit(1)

