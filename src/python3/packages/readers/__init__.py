#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Import des modules readers

    ATTENTION : l'import du reader 'imc' est ignoré *silencieusement* (cas où
                le package 'IMCtermite' est absent).
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
            if module_name != 'imc':
                print("{} : Exception ignorée lors de l'import du reader {}.".format(e, module_name))
        else:
            __all__.append(module)
            
#__all__.sort()

# on contrôle que l'on n'a pas plusieurs modules traitant le même type
type_list = []
module_list = []
for module in __all__ :
    try :
        type_list.append(module.Reader.reader_type)
        module_list.append(module)
    except :
        pass
doublons = set([t for t in type_list if type_list.count(t)>1])
msg = ""
if len(doublons) > 0 :
    for m in module_list :
        if m.Reader.reader_type in doublons :
            msg += "le module {} traite le type {}\n".format(m, m.Reader.reader_type)
    raise ImportError("Plusieurs modules traitent le même type de données :\n"+msg)

def get_module(reader_type) :
    """
        Retourne le module reader correspondant au type.
        Si aucun reader n'est trouvé, onquitte le programme.
    """
    module_reader = None
    for module in __all__ :
        try :
            if module.Reader.reader_type == reader_type :
                module_reader = module
        except AttributeError:
            pass    
    if module_reader is None :
        print(("Aucun module reader trouvé pour le type {}".format(reader_type)))
        exit(1)
    else :
        return module_reader
    
def get_reader(reader_type, source, config, logger=None, start=None, end=None, keep_normal=True, no_checksum=False):
    """
        Retourne un objet reader correspondant au type.
    """
    reader_module = get_module(reader_type)
    reader = reader_module.Reader(source, config, logger, start, end, keep_normal, no_checksum)
    return reader
    
