#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    Lecture d'un vecteur sur une période
"""
import os
import sys
import matplotlib.pyplot as plt

# Ajout de AIDA au path et import
aida_home = os.getenv('AIDA_HOME')
PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
sys.path.append(os.path.join(aida_home, 'lib', PYTHON_X_Y))
import AIDA

# Période et paramètre à lire
acqid_debut = "ts210213"
acqid_fin = "ts210213"
parametre = "pre_air_c1_cal_%60"

# Lecture des données
data, time, header = AIDA.read_datas(acqid_debut, parametre, acqid_fin) 

# Tracé
plt.plot(time,data)
plt.show()

