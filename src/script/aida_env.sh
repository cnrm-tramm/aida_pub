#!/usr/bin/env bash

#==============================================================================
#
# Changement d'environnement de travail de AIDA.
#
# NOTE :
# ====
# Ce script est fait pour être sourcé (". aida_env.sh" ou "source aida_env.sh")
# => il ne doit pas faire 'exit' sinon le terminal est fermé.
#
#==============================================================================

# test la présence de zenity
graphic_tool="zenity"
graphic_mode=$(which $graphic_tool 2>/dev/null)


#------------------------------------------------------------------------------
function chooser
# $1   : titre
# $2-* : choix1...
{
	# affichage du menu
	printf "\n$1 ?\n"
	shift
	i=1
	while [ "$1" ] ; do
		printf "\t %2d - %s \n" $i "$1"
		i=$((i + 1))
		shift
	done
	i=$((i - 1))

	# boucle de lecture du choix
	rep=-1
	while [ $rep -lt 1 -o $rep -gt $i ] ; do
		printf "\t votre choix [1, %d] : " $i
		read x
		rep=${x:-$rep}
		# si la réponse n'est pas un int, la passer à -1
		[[ ! "$rep" =~ ^[0-9]+$ ]] && rep=-1
	done
	return $rep
}

#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
# ce script doit être sourcé (sur le serveur, le "lanceur" est alors `-bash`
# et non pas simplement `bash`.
if [[ "$0" != "bash" && "$0" != "-bash" ]] ; then
	echo "Ce script doit être 'sourcé' !"
	echo "=> lancer soit '. aida_env.sh', soit 'source aida_env.sh'"
	exit 1
fi

unset env
# récupération de la liste des environnements
envs=( $(aida_env.py -l) )

# argument
if [[ $# -eq 1 ]] ; then
	env=$1
	ok="non"
	for item in ${envs[@]} ; do
		if [[ "$env" == "$item" ]] ; then
			ok="oui"
		fi
	done
	
	if [[ "$ok" == "non" ]] ; then
		echo "'$env' n'existe pas (${envs[@]})"
		return
	fi
fi

# choix de l'environnement
if [[ ! "$env" ]] ; then
	# en mode console
	question="Quel environnement voulez-vous utiliser"
	if [[ ! "$graphic_mode" ]] ; then
		chooser "$question" "${envs[@]}"
		choix=$(($? - 1))
		env="${envs[$choix]}"
	# en mode graphique
	else
		#title="Mode d'installation"
		text="Sélectionner le mode d'installation de AIDA"
	
		rep=""
		while [[ "$rep" == "" ]] ; do
			rep=$($graphic_tool --list --title "Environnement de travail"  \
				                --column "" --hide-header \
								--text "$question" "${envs[@]}" 2>/dev/null)
			ret=$?
			# l'utilisateur a annulé
			### NE SURTOUT PAS FAIRE 'exit' ICI MAIS 'return' (voir l'entête
			### de ce script)
			[[ $ret -eq 1 ]] && echo "...bye" && return 0
		done
		env=$rep
	fi
fi
#echo "env = $env"

# récupération des variables à positionner
# la variable PS1 peut contenir des ' ' qui gènent à la construction du tableau
# 'vars' => remplacer les ' ' par des '§' (le caractère '§' a peu de chance
# d'être utilisé dans les variables d'environnement)
OIFS="$IFS"
IFS="," vars=( $(aida_env.py $env | tr ' ' '§') )
IFS="$OIFS"

for var in ${vars[*]} ; do
	v=$(echo $var | tr '§' ' ' | tr -d "'")
	# n'afficher que les variables qui commencent par AIDA
	# (l'affichage de PS1 est peu lisible)
	if [[ "${v:0:4}" == "AIDA" ]] ; then
		echo "  $v"
	fi
	export "$v"
done
