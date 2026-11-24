#!/usr/bin/env python3

"""
    ADC : dictionnaire contenant les valeurs par défaut pour les headers de
          sortie des opérateurs.

    USAGE :
    =====
        VO_header = default_out_header.copy()
        VO_header['name']         = ...
        VO_header['english_name'] = ...
        VO_header['unit']         = ...
        VO_header['freq_ech']     = ...
        VO_header['ref_time']     = ...
        VO_header['misval']       = ...

    CONSTRUCTION DES HEADERS :
    ========================
| nom           | nature      |positionné     | valeur 
| du champ      | du champ    |par            | par déeaut
+---------------+-------------+---------------+--------------------------------
| format        | obligatoire | opérateur     | Ieeefloat_32
| dim_array     | obligatoire | opérateur     | 1
| famille       | obligatoire | opérateur     | auto
| name          | souhaitable | opérateur     |
| english_name  | souhaitable | opérateur     |
| unit          | obligatoire | opérateur     |
| freq_ech      | obligatoire | opérateur     |
| ref_time      | obligatoire | opérateur     |
| bornes        | si besoin   | opérateur     | 
| unit_bornes   | si besoin   | opérateur     |
| time_bnds     | si besoin   | opérateur     |
| misval        | RECOMMANDÉ  | opérateur/ADC | 
| fct_comment   |             | opérateur     | retour de la fonction de calcul
| vol           |             | ADC           |
| origine       |             | ADC           | 
| misval        |             | ADC           | si non fourni par opérateur
| fct_origine   |             | ADC           |
| date_creation |             | ADC           |
| endianness    |             | ADC           |
| dimension     |             | ADC           |

"""

default_out_header = {
        'name'        : '',
        'english_name': '',
        'format'      : 'Ieeefloat_32',
        'dim_array'   : '1',
        'famille'     : 'auto',
        }


#==============================================================================
# Test
#==============================================================================
if __name__ == '__main__':


    VO_header = default_out_header.copy()
    name = 'test'
    VO_header['name'] = f"param '{name}"

    # résultat
    print("Contenu du VO_header")
    for key, value in VO_header.items():
        print(f"  - {key:15s} = {value}")
