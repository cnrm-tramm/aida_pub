.. _modules_python 

Modules Python
==============

Pour utiliser les modules de AIDA 
quelques lignes à insérer en début de votre 
programme Python : ::

    import os
    import sys
    AH = os.getenv('AIDA_HOME')
    PYTHON_X_Y = "python%d.%d" % (sys.version_info[0], sys.version_info[1])
    sys.path.append(os.path.join(AH, 'lib', PYTHON_X_Y))


.. toctree::
   :maxdepth: 2

AIDA
-----
.. automodule:: AIDA
   :members:

AcqId
-----
.. automodule:: AcqId
   :members:

Camp
----
.. automodule:: Camp
   :members:

Chrono
------
.. automodule:: Chrono
   :members:

Constantes
----------
.. automodule:: Constantes
   :members:

Units
-----
.. automodule:: Units
   :members:

AIDA_mail
---------
.. automodule:: AIDA_mail
   :members:

AIDA_env
--------
.. automodule:: AIDA_env
   :members:


opla
----
.. automodule:: opla
   :members:

DataBase
--------
.. automodule:: DataBase
   :members:

VersionVect
-----------
.. automodule:: VersionVect
   :members:

readers
-------
:doc:`La doc du package readers <readers:index>`
