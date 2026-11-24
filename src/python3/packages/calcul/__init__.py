#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Import des modules calcul pour ADC
"""

from glob import glob
from keyword import iskeyword
from os.path import dirname, join, split, splitext
 
basedir = dirname(__file__) 
__all__ = []
for name in glob(join(basedir, '*.py')):
    module_name = splitext(split(name)[-1])[0]
    if not module_name.startswith('_') and not iskeyword(module_name):
        try:
            module = __import__(__name__+'.'+module_name, fromlist=[module_name])
        except Exception as e :
            print(("{} \nException ignorée lors de l'import du calcul {}.".format(e,module_name)))
        else:
            __all__.append(module_name)
            

