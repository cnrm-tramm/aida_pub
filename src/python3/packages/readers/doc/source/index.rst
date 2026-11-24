.. Mouton2Vec documentation master file, created by
   sphinx-quickstart on Wed Oct 12 14:10:54 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Bienvenu sur la documentation du package **readers** !
======================================================

Index
=====

* :ref:`genindex`
* :ref:`Index des modules<modindex>`
* :ref:`search`

Interface
=========

Le package **readers** met à disposition des objets qui permettent de lire différents types de données :

- csv_like (fichiers texte colonnes avec 1 ou plusieurs séparateurs)

- eddypro

- pads

Ces objets sont accessibles via la fonction **readers.get_reader** (type, sources, config, logger=None, start=None, end=None, keep_normal=True) :

- type : type de donnée

- sources : fichier(s) ou répertoire(s) de données à lire

- config : fichier de configuration qui décrit les données

- logger : handler du module logging ou s'écriront les logs (par défaut /tmp/reader_<type>.log)

- start : date de début YYYYMMDD

- end : date de fin YYYYMMDD

- keep_normal : conserver les valeurs hors normes (True/False)

Exemple :   
            *my_reader = readers.get_reader("csv_like", ["/data/fic1.dat", "/data/fic2.dat"], "/config/config.txt")*

            *my_reader.read() # les données sont lues dans my_reader.datas*


Contenu
=======

.. toctree::
   :maxdepth: 2

.. automodule:: abstract_reader
        :members:
.. automodule:: csv_like
        :members:
.. automodule:: eddypro
        :members:
.. automodule:: pads
        :members:
.. automodule:: ce376
        :members:
.. automodule:: netcdf
        :members:
.. automodule:: licor_as2
        :members:
