#!/usr/bin/env bash

#==============================================================================
#
# Tente de vérifier si les paquets standards python3 utilisés dans AIDA
# sont installés.
#
# - Pour ce faire, ce script :
#   - crée un fichier contenant tous les 'import' trouvés  dans les scripts
#     python AIDA.
#   - lance le script de vérification `check_imports.py` avec ce fichier en
#     argument.
#     - `check_imports.py` génère 2 fichiers :
#       - un fichier contenant la liste des modules absents
#       - un fichier contenant la liste des modules NON-AIDA nécessaires
#   - analyse la sortie de `check_imports.py`.
#
# NOTES :
# - La version python2 étant encore présente dans AIDA, seuls quelques
#   répertoires de AIDA sont explorés (cf. variable 'scan_dir').
# - Un fichier de configuration (cf. variable 'cfg') permet éventuellement :
#   * d'exclure des sous-répertoires de la recheche des fichiers à étudier (cf.
#     option -C).
#   * d'exclure des modules python de la vérification
#
# Ce script à pour vocation d'être lancé :
# - à la fin de la compilation générale de AIDA.
# - par l'installateur afin de vérifier que tous les modules nécessaires à AIDA
#   sont présents.
#
# Exemple de fichier configuration :
# -----8<-------------------------
#   Monitor vista
#   lecture/safire_dad/tools
#
#   ignore_paquets cfunits
# -----8<-------------------------
#
# NOTE
# Lorsque ce script est lancé sans DISPLAY (par cron par exemple), les import
# qui ont besoin d'un DISPLAY génèrent des erreurs ("Failed to connect to Mir",
# "...GDK_IS_DISPLAY...".
# Plusieurs tentatives infructueuses ont été faites pour remédier à ce
# problème.
# Une solution plus radicale est d'exclure systématiquement le modules
# 'matplotlib.backends'... (et peut-être d'autres à venir)
# Ces modules systématiquement ignorés doivent alors faire partie des prérequis
# de l'installation de AIDA.
# => voir la variable : always_ignored
#==============================================================================

# script name
ME=${0##*/}
ME_NAME=${ME%%.*}
ME_DIR=$(dirname $(realpath $0))

VERSION="2.0.0"

# fichier de configuration des répertoires à exclures
cfg="$AIDA_HOME/config/${ME_NAME}.cfg"

# éviter de semer des fichiers un peu partout...
LOG_DIR="$HOME/log"
mkdir -p $LOG_DIR

# fichier temporaire
tmpfile="$LOG_DIR/all_imports.txt"
rm -f $tmpfile

# script python de vérification
# il faut excécuter le check_imports.py qui est dans le même répertoire
# que ce script (surtout pour l'installateur)
# script="$AIDA_HOME/src/script/installateur/check_imports.py"
script="$ME_DIR/check_imports.py"

# le fichier de sortie et d'erreur de $script
missings="$LOG_DIR/imports_manquants"
script_err="$LOG_DIR/check_imports.py.ERR"
rm -f $missings
rm -f $script_err

# fichier des modules requis
# ATTENTION : la localisation dépend du "mode" ('prerequis' ou 'usuel')
# ATTENTION : ces déclarations sont également faites dans git_auto_build.sh
req_file="aida_modules_python_requis"
requirements=$AIDA_HOME/log/$req_file
requirements_prerequis="$AIDA_HOME/src/script/installateur/$req_file"
rm -f $requirements

# pattern python attendu
py_pattern="python3"

# répertoires à scanner (merci de respecter la présentation de 'scan_dir' en
# cas de modification : ça fait plus propre dans le help)
scan_dir="
   $AIDA_HOME/src/$py_pattern
   $AIDA_HOME/src/lib/oper
   $AIDA_HOME/src/script
"

# Tentative pour ne pas avoir des : "Failed to connect to Mir" ou
# "..GDK_IS_DISPLAY...".
# *** les modules matplotlib.backends sont dans les prérequis AIDA
# *** les modules installables seulement pas `pip` sont ignorés
# *** les modules issus de Météo-France sont ignorés
from_prerequis="matplotlib.backends.backend_gtk3 matplotlib.backends.backend_gtk3agg"
# cfunits est devenu obligatoire et sa présence est testée àl'installation.
from_pip="keycloak pandas_profiling cfunits folium IMCtermite"
from_MF="bronx epygram"
not_required="sklearn matplotlib.gridspec rttovgb_pywrapper"
always_ignored="$from_prerequis $from_pip $from_MF $not_required"

#------------------------------------------------------------------------------
# fonctions
#------------------------------------------------------------------------------
function usage
# no parameters
{
	cat <<-EOF

	  Tente de vérfier que les paquets standards '$py_pattern' sont installés.
	  Version : $VERSION

	  ----------------------
	  Usage  : $ME [-C]
	     ou  : $ME [-P]            # usage réservé à TRAMM
	     ou  : $ME [-v] [-w]
	    avec :
	      -C : création du fichier de configuration.
	      -P : génération du fichier "aida_modules_python_requis"
	      -v : mode verbeux
	      -w : affiche un warning si le shebang ne contient pas '$py_pattern'.
	  ----------------------

	  exemple : $ME

	  Les répertoires explorés sont : $scan_dir
	  Le fichier '$cfg' permet d'exclure
	  des sous-répertoires ou des paquets de la recheche.
	  Les fichiers ne contenant pas le shebang '$py_pattern' sont ignorés.

	EOF
	exit 1
}

#------------------------------------------------------------------------------
function create_cfg
# no parameters
{
typeset -a cfg_list
typeset -l rep

	[[ -s "$cfg" ]] && cfg_list=( $(cat $cfg | grep -v "^#") )
	if [[ "${cfg_list}" ]] ; then
		clear
		printf "\n\033[31mLe fichier $cfg existe\033[0;39m\n"
		printf "Il contient :\n"
		printf "  - %s\n" ${cfg_list[*]}
		echo "Voulez-vous le modifier ? [o/N] "
		read rep
		[[ "$rep" != "o" ]] && echo "... bye" && exit 1
		cp $cfg ${cfg}.back
	fi
	
	cat <<-EOF >$cfg
		#
		# Liste des sous-répertoires et modules à exclure de la recherche pour
		# src/script/check_AIDA_PY_dependencies.sh
		#
		# Syntaxe :
		#  - les lignes vides ou commençant par '#' sont ignorées
		#  - les noms sont des noms courts sur une ou plusieurs lignes.
		#  - les noms peuvent contenir des '/'.
		#  - si une ligne commence par 'ignore_paquets'
		#    - elle contient la liste des modules python a ignorer (ex cfunits
		#      que l'on peut trouver sous 'pip' mais généralement pas dans les
		#      paquets standards de la distribution Linux).
		#
		# Exemple :
		# --8<----------------
		# Monitor vista
		# lecture/safire_dad/tools
		# ignore_paquets bronx epygram keycloak pandas_profiling cfunits
		# --8<----------------
		#
	EOF
	vi $cfg
	exit 1
}

#------------------------------------------------------------------------------
function build_requirements
{
	# initialisations
	# ---------------
	# à exclure à partir du fichier $cfg, construire :
	# - exclude        : tableau des répertoires à exclure
	# - ignore_paquets : tableau des paquets à ignorer
	##[[ $verbose ]] && printf "\nConfiguration : $cfg \n"
	printf "Configuration   : $cfg \n"
	if [[ -s "$cfg" ]] ; then
		exclude=( $(cat $cfg | grep -v "^#" | grep -v "^$" | grep -v "ignore_paquets") )
		ignore_paquets=$(cat $cfg | grep -v "^#" | grep -v "^$" | grep "ignore_paquets" | cut --delimiter=' ' -f2- )
	fi

	# ajouter à 'ignore_paquets', les paquets systématiquement ignorés
	ignore_paquets="$ignore_paquets $always_ignored"

	# supprimer d'éventuels espaces sur-numéraires de 'ignore_paquets'
	ignore_paquets=$(echo $ignore_paquets)
	##[[ $verbose ]] && printf "\nPaquets ignorés : $ignore_paquets \n"
	printf "Paquets ignorés : $ignore_paquets \n"
	
	# à partir du tableau des répertoires à exclure, construire l'option
	# d'exclusion pour la commande 'find'
	if [[ "${exclude}" ]] ; then
		exclude_opt='-not \( \( '
		last=$((${#exclude[*]}-1))
		for (( i=0 ; i < $last ; i++ )) ; do
			exclude_opt="$exclude_opt -path '*/${exclude[$i]}' -or"
		done
		# ajouter le dernier élément de $exclude
		exclude_opt="$exclude_opt -path '*/${exclude[$i]}' \) -prune \)"
	fi
	

	# traitement
	# ----------
	# récupéper toutes les lignes "import " et "from " des sources :
	# - les lignes de la forme "from ." indiquent des imports locaux et ne
	#   sont pas prises.
	# - parfois les lignes d'import sont terminée par des espaces => supprimer
	#   les espaces sur-numéraires (sinon elles peuvent doublonner avec des
	#   lignes identiques aux espaces surnuméraires près).
	
	[[ $verbose ]] && printf "Traitement des fichiers :\n"
	scan_dir=$(echo $scan_dir)
	
	# ATTENTION : chez TRAMM -name "*.py" (avec double quote) ne fonctionne pas.
	for f in $(eval "find $scan_dir "$exclude_opt" -type f -size +0 -name '*.py'") ; do
		# ne pas traiter les fichiers dont le shebang n'est pas 'py_pattern'
		head -1 $f | grep -q "$py_pattern" ; ret=$?
		if [[ $ret != 0 ]] ; then
			[[ $warn ]] && \
				ignore_files+="    - $f\n"
				#echo "    --> $f : le shebang n'est pas '$py_pattern'"
			continue
		fi
	
		# étudier le fichier
		here_dir=$(basename $(dirname $f) )
		process_files+="$f "
		[[ $verbose ]] && echo "  - $f"
		grep -E "^([[:space:]])*(import|from)([[:space:]])+" $f | \
			grep -v 'from \.' | \
		 	grep -v 'from '$here_dir'' | \
		 	sed 's/#.*$//' | \
		 	sed 's/[[:space:]]*$//' | \
		 	sed 's/ as .*$//' | \
		 	sed 's/^[[:space:]]*//' | \
		 	sed 's/[[:space:]]*$//' | \
			tr -s ' ' >>$tmpfile
	done

	if [[ $warn ]] ; then
		printf "\n  Fichiers ignorés (le shebang n'est pas '$py_pattern') :\n"
		printf "$ignore_files"
	fi

	# remplacer les lignes "import x,y" par 2 lignes d'import : cela permettra
	# de supprimer quelques doublons d'import comme :
	#   "import os, sys" <-> "import sys, os"
	## sed T : si la substitution précédente n'a pas été fructueuse, branche à
	## la fin du script sed <=> si pas de substitution, imprimer la ligne)
	cat $tmpfile | sed '/^import / { s/,[[:space:]]*/\nimport /g ; T ; p } ' >$tmpfile.2
	mv $tmpfile.2 $tmpfile

	# supprimer des import trouvés tout ce qui est dans 'ignore_paquets'
	if [[ -n "$ignore_paquets" ]] ; then
		sort -ru $tmpfile | \
			egrep -v "${ignore_paquets// /|}" >$tmpfile.2
			mv $tmpfile.2 $tmpfile
	fi


	mv $tmpfile $requirements
}

#------------------------------------------------------------------------------
function get_requirements
{
	# récupérer le fichier $requirements_prerequis
	cp $requirements_prerequis $requirements
	return
}

#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
mode='usuel'
# check des options
while getopts "CPvwh" opt; do
	case $opt in
		C)	create_cfg
			;;
		P)	mode='prerequis'
			requirements=$LOG_DIR/$req_file
			requirements_prerequis="$ME_DIR/$req_file"
			;;
		v)	verbose=true
			;;
		w)	warn=true
			;;
		h|*) usage
			;;
	esac
done
shift $((OPTIND-1))

# check des arguments
[[ $# -gt 0 ]] && usage


if [[ "$mode" == 'usuel' ]] ; then
	build_requirements
else
	get_requirements
fi

# lancement du script de vérification des import sur le fichier contenant tous
# les imports ($requirements). Il créera le fichier des modules manquants
# ($missings) et un fichier _propre_ des modules nécessaires à AIDA
# ($requirements.clean)
if [[ "$DISPLAY" ]] ; then
	printf "\n\033[1mExécution de : $script\033[0;39m\n"
else
	printf "\nExécution de : $script\n"
fi
$script $requirements $missings $requirements.clean 2>$script_err ; ret=$?
if [[ "$mode" == 'usuel' ]] ; then
	mv $requirements.clean $requirements
fi

# ret est le retour du script de vérification :
# si != 0, ret = nombre de modules absents
if [[ $ret != 0  ]] ; then
	absents=( $(cat $missings | sort -u) )
	if [[ "$mode" = 'usuel' ]] ; then
		printf "\n--> ERREUR : '${absents[*]}' \n"
		for absent in ${absents[*]} ; do
			printf "    '$absent' depuis : \n"
			printf "     - %s \n" $(grep -l -E -w "(import|from)([[:space:]]+)($absent)" $process_files)
		done
		printf "\n--> Pour exclure des répertoires de la vérifications, lancer :"
		printf "\n    $ME -C \n"
	fi
else
	printf "\n--> modules python : pas de problèmes détectés.\n"
fi

printf "\n"

# fin
rm -f $tmpfile $missings

# ce script est lancé par la compilation générale en mode 'usuel'
# => pour que 'make' ne se termine pas en erreur, toujours finir par exit 0
# ce script est lancé par l'installateur qui attend un retour != 0 s'il a des
# problème
# => différencier le code d'exit
if [[ "$mode" == 'usuel' ]] ; then
	exit 0
else
	exit $ret
fi
