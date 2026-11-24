Jeu de données brutes METEOPOLE-FLUX
------------------------------------

Le répertoire 2021_08_01 contient les fichiers 30min de la station d'acquisition
campbel2 de la plateforme toulouse-flux.
Le fichier de config METEOPOLE_FLUX.toulouse-flux.campbel2.V2.config permet de créer
des vecteurs à partir de ces fichiers avec mtv.py :

mtv.py -t csv_like -p test-AIDA -f METEOPOLE_FLUX.toulouse-flux.campbel2.V2.config 2021_08_01


Le fichier CNRM_MTO_L2A-30min-Mean_2021-06-18.nc contient les données METEOPOLE_FLUX du 18/06/2021 au format netcdf.
La vectorisation se fait en lançant :

mtv.py -F -t netcdf -p test-AIDA CNRM_MTO_L2A-30min-Mean_2021-06-18.nc
ou (pour configurer les variables)
mtv.py -F -t netcdf -p test-AIDA -f netcdf.config CNRM_MTO_L2A-30min-Mean_2021-06-18.nc
