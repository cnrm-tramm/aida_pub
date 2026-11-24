#!/usr/bin/env bash

#==============================================================================
# Gestionnaire de AIDA
#	Ce script permet d'éffectuer les opération suivantes :
#	- primo installation de AIDA
#==============================================================================

# Initialisations
# ---------------
# éviter de semer des fichiers un peu partout...
LOG_DIR="$HOME/.config/aida/log"
mkdir -p $LOG_DIR

LOG_DIR_INSTALL=$LOG_DIR/install
mkdir -p $LOG_DIR_INSTALL

FIC_LOG=$LOG_DIR_INSTALL/INSTALL_AIDA.log
FIC_ERR=$LOG_DIR_INSTALL/INSTALL_AIDA.err

# positionnement des localisations
aida_home=$(realpath $(dirname $0))
scripts_dir=$(dirname $(realpath $0))
echo "aida_home   = $aida_home"
echo "scripts_dir = $scripts_dir"

# positionnement des variables d'environnement
export AIDA_HOME="$aida_home"
export AIDA_PROFIL="PUBLIC"
export AIDA_DATA="$aida_home/data"
export AIDA_META="$aida_home/meta"

echo "AIDA_PROFIL = $AIDA_PROFIL"
echo "AIDA_HOME   = $AIDA_HOME"

# test la présence de zenity
graphic_tool="zenity"
graphic_mode=$(which $graphic_tool 2>/dev/null)

#------------------------------------------------------------------------------
test_reponse ()
{
	if [ $1 -eq 0 ] ; then
		echo " OK"
	else
		echo " KO"
		exit -1
	fi
}

#------------------------------------------------------------------------------
build_profile_aida ()
{
	echo "Génération de $HOME/.profile.aida"

	# création du fichier .profile.aida pour déclaration des variables
	# d'environnement de AIDA et la mise à jour de la variable $PATH.
	cat >$HOME/.profile.aida <<-EOF
		#
		# Initialisation de l'environnement de AIDA.
		# Pour passer en environnement AIDA, taper la commande :
		# . $HOME/.profile.aida
		# Cette commande peut être ajoutée dans le fichier $HOME/.bashrc
		#

		export AIDA_PROFIL=$AIDA_PROFIL
		export AIDA_HOME=$AIDA_HOME

		export AIDA_META=$AIDA_META
		export AIDA_DATA=$AIDA_DATA


		export PATH=\$PATH:\$AIDA_HOME/bin
		export PYQTGRAPH_QT_LIB=PyQt5

		# Utilisation de webkit dans vista et edifil
		export WEBKIT_DISABLE_COMPOSITING_MODE=1
		###export LIBGL_DRI2_DISABLE=true
		###export LIBGL_DRI3_DISABLE=true

		# sauvegarder le PS1 original (voir $HOME/.config/AIDA_env/AIDA_env.ini)
		export PS1_ORIG=\$PS1


		function acd {
		    data_path=\$(id2datapath \$1) ; ret=\$?
		    if [[ \$ret == 0 ]] ; then
		        if [[ -d "\$data_path" ]] ; then
		            echo \$data_path
		            cd \$data_path
		        else
		            echo "Attention : le repertoire \$data_path n'existe pas"
		        fi
		    fi
		}
		EOF

	# message à l'utilisateur et insertion éventuelle de la commande dans
	# le .bashrc
	msg=$(cat <<-EOF

	Afin d'initialiser les variables d'environnement nécessaires à AIDA,
	le fichier $HOME/.profile.aida a été écrit.

	Ce fichier devra être éxécuté avant toute utilisation d'AIDA en lançant :

	  . $HOME/.profile.aida

	(attention : cette commande commence par le caractère '.' suivi d'un espace)
	Cette commande peut-être ajoutée dans le fichier $HOME/.bashrc afin d'être
	éxécutée automatiquement.

	EOF
	)

	# voir s'il faut faire l'insertion dans le .bashrc
	in_place=$(grep ".profile.aida" $HOME/.bashrc | \
				cut --delimiter='#' -f1 | tr -d ' ')

	# pas de .profile.aida dans $HOME/.bashrc
	do_insert="non"
	if [[ "$in_place"  == "" ]] ; then
		question="Voulez-vous que cette commande soit ajoutée à votre fichier $HOME/.bashrc ? "
		if [[ ! "$graphic_mode" ]] ; then
			echo "$msg"
			echo ""
			read -p "$question [o/n] " ret
			if [[ "${ret^o}" == "O" ]] ; then
				do_insert="oui"
			fi
		else
			$graphic_tool --question --no-wrap --text="$msg  \n\n$question"
			ret=$?
			echo "ret = $ret"
			if [[ $ret == 0 ]] ; then
				do_insert="oui"
			fi
		fi
	fi

	if [[ "$do_insert" == "oui" ]] ; then
		echo "Modification de $HOME/.bashrc"
		echo ""                     >>$HOME/.bashrc
		echo "# environnement AIDA" >>$HOME/.bashrc
		echo ". ~/.profile.aida"    >>$HOME/.bashrc
	else
		echo "Pas de modification de $HOME/.bashrc"
	fi
}

#------------------------------------------------------------------------------
build_config_AIDA_env ()
{
	echo "Génération de $HOME/.config/AIDA_env/AIDA_env.ini"

	# le fichier existe => le sauvegarder
	if [ -f "$HOME/.config/AIDA_env/AIDA_env.ini" ] ; then
		now=$(date +%Y%m%d%H%M%S)
		mv $HOME/.config/AIDA_env/AIDA_env.ini \
		   $HOME/.config/AIDA_env/AIDA_env.ini.$now
	fi

	# créer le fichier
	mkdir -p $HOME/.config/AIDA_env/
	cat >$HOME/.config/AIDA_env/AIDA_env.ini <<-EOF
		# Configuration d'environnement de travail sous AIDA
		#
		# Ce fichier ne se substitue pas au fichier ~/.profil.aida
		#
		# NOTE : pour que PS1 puisse être modifier, il faut l'avoir exporté
		#        (par exemple dans .profile.aida)
		#        ou l'écrire en entier...

		[default]
		env_name = $AIDA_PROFIL

		[PUBLIC]
		AIDA_META   = $AIDA_META
		AIDA_DATA   = $AIDA_DATA
		AIDA_PROFIL = $AIDA_PROFIL
		PS1         = \$PS1_ORIG

		[EXEMPLES]
		AIDA_META   = $AIDA_HOME/profils/EXEMPLES/meta
		AIDA_DATA   = $AIDA_HOME/profils/EXEMPLES/data
		AIDA_PROFIL = EXEMPLES
		PS1         = (EXEMPLES) \$PS1_ORIG

		EOF
}

#------------------------------------------------------------------------------
compile_aida ()
{
	cd $AIDA_HOME/src

	echo -e "Lancement de make clean   :\c"
	make clean   >> $FIC_LOG 2>> $FIC_ERR
	test_reponse $?

	echo -e "Lancement de make depend  :\c"
	make depend  >> $FIC_LOG 2>> $FIC_ERR
	test_reponse $?

	echo -e "Lancement de make install :\c"
	make install >> $FIC_LOG 2>> $FIC_ERR
	test_reponse $?
}

#------------------------------------------------------------------------------
premiere_mise_en_place ()
{
	>$FIC_LOG
	>$FIC_ERR

	# Création des répertoires utiles
	cd $AIDA_HOME
	mkdir include bin lib log profils data meta meta/campagnes meta/INF
	mkdir -p share/common/logos

	# liens des profils_default/* dans profils
	echo "Installation des profils"
	cd profils
	for profil in ../profils_default/* ; do
		ln -s $profil
	done
	cd ..

	# copie des logos
	echo "Installation des logos"
	cp $AIDA_HOME/logos_default/* $AIDA_HOME/share/common/logos/

	# Compilation des utilitaires externes
	cd extern/src/
	echo -e "Détarage du source externe cextract_aida_gcc :\c"
	tar xvfz cextract_aida_gcc.tgz >> $FIC_LOG 2>> $FIC_ERR
	test_reponse $?
	cd cextract_aida_gcc
	echo -e "Compilation du source externe cextract_aida_gcc :\c"
	make install >> $FIC_LOG 2>> $FIC_ERR
	test_reponse $?

	# Pour que la compilation générale fonctionne
	# (./check_AIDA_PY_dependencies.py)
	export PYQTGRAPH_QT_LIB=PyQt5

	# décompression de share/common/Cartes/shapefiles/natural_earth/raster
	echo "Décompression de HYP_50M_SR.zip"
	cd $AIDA_HOME/share/common/Cartes/shapefiles/natural_earth/raster
	unzip HYP_50M_SR.zip

}

#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
if [[ $# -eq 1 ]] ; then
	if [[ "$1" == "-c" ]] ; then
		echo "$0 lancé en mode console"	
		graphic_mode=""
	else
		echo "option non valide (option valide = [-c])"
		echo "...bye"
		exit 1
	fi
fi

# Pré-requis
cd $scripts_dir

echo "Vérification des prérequis :"
./check_prerequis.sh || { echo "...bye" ; exit 1 ; }

echo "Vérification des modules python requis :"
./check_AIDA_PY_dependencies.sh -P || { echo "...bye" ; exit 1 ; }

# Installation
echo "Mise en place de $AIDA_HOME"
premiere_mise_en_place
compile_aida

# construction du fichier ~/.profile.aida
build_profile_aida

# construction d'un premier fichier ~/.config/AIDA_env/AIDA_env.ini
build_config_AIDA_env

echo "INSTALLATION TERMINÉE"
echo ""

echo "Vous pouvez fermer ce terminal."
echo "Pour travailler avec AIDA, pensez à exécuter la commande :"
echo "  . $HOME/.profile.aida"
echo "si elle n'a pas été ajoutée au votre fichier $HOME/.bashrc"
