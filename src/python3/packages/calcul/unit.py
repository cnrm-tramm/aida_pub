#!/usr/bin/env python3

import numpy as np

def auto_tempe_unit(T):
    """ Retourne la constante de conversion à ajouter à T pour obtenir des
        Kelvins (0 ou 273.15)
    """
    if (np.nanmedian(T) > 100.)  or (np.isnan(T).all()) :
        CtoK = 0.
    else : 
        CtoK = 273.15

    return CtoK

