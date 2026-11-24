Jeu de données brutes test-AIDA (construit à partir de données de METEOPOLE-FLUX)
---------------------------------------------------------------------------------

Fichiers PTUV_2021*.txt : illustration d'un fichier csv avec une seule trame
YYYY-MM-DD HH:MM:SS,pression,temperature,humidite,dd,ff

Fichiers RAY_RR_2021*.txt : illustration d'un fichier csv à plusieurs trames (1 rayonnement, 1 precipitations)
YYYY-MM-DD HH:MM:SS,RAY,ird,irm,rgd,rgm
YYYY-MM-DD HH:MM:SS,RR,rr1,rr2

Fichiers TSOL_2021*.txt : illustration d'un fichier csv 1 trame décrivant un profil
YYYY-MM-DD HH:MM:SS,t-5cm,t-10cm,t-20cm,t-30cm,t-50cm



Création des vecteurs à partir des données brutes
-------------------------------------------------
mtv.py -F -t csv_like -p test-AIDA -f ptuv.config `ls PTUV_2021*.txt`
mtv.py -F -t csv_like -p test-AIDA -f ray_rr.config `ls RAY_RR_2021*.txt`
mtv.py -F -t csv_like -p test-AIDA -f tsol.config `ls TSOL_2021*.txt`
