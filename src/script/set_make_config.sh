#!/usr/bin/env bash

#==============================================================================
#
# Création du fichier de configuration pour make pour AIDA.
#
# Ce script a été fortement repris
# pour différencier les .mk d'avant et ceux générés maintenant, le nom du
# fichier se termine à présent : .auto.mk
#==============================================================================

ecrit_squelette ()
{
	file_mk="$1"
	echo "création du fichier : $file_mk"
	local_PYTHON_3_Y=$(python3 -c 'import sys; print ("python%d.%d" % (sys.version_info[0], sys.version_info[1]))')


	cat >$file_mk <<-EOF
		# Génération automatique
		# Ne pas modifer manuellement
		#
		
		
		.SECONDEXPANSION:
		
		ifndef AIDA_LIB
		AIDA_LIB = \$(AIDA_HOME)/lib
		endif
		
		# La variable doit exister
		# Elle ne sera utilisée que si nautilus existe sur la machine
		export NAUTILUS_SCRIPTS_DIR=\$(HOME)/.local/share/nautilus/scripts
		
		# -------------------------------------
		# Variables de compilations spécifiques
		# -------------------------------------
		# "WITHOUT_LAPACK" par défaut, car plus passe-partout.
		# WITHOUT_LAPACK=FALSE
		WITHOUT_LAPACK=TRUE
		
		# -------------------------------------
		# Variables de compilations générales
		# -------------------------------------
		# Environnement d'exécution de l'appli AIDA
		export LD_RUN_PATH=\$(AIDA_LIB)
		
		C_ANSI                   = gcc -ansi
		C_99                     = gcc -std=c99
		CC                       = \$(C_ANSI)
		C_STRICT_FLAGS           = -pedantic-errors -Wall
		C_OPT_FLAGS              = -O
		C_PROF_INFO_FLAGS        = -p
		C_COV_INFO_FLAGS         = -fprofile-arcs -ftest-coverage
		C_DEBUG_INFO_FLAGS       = -g
		C_VERBOSE_FLAGS          = -Q
		C_DEBUG_FLAGS            = \$(C_DEBUG_INFO_FLAGS)
		C_PIC_FLAGS              = -fpic
		PICFLAGS                 = \$(C_PIC_FLAGS)
		
		LD                       = gcc
		LD_RUNPATH_FLAGS         =  -L
		LD_SHLIB_FLAGS           = -shared
		DYN_LOADER_LIB           = -ldl
		
		
		F77                      = gfortran
		LIB_PATH_FORTRAN         = $(dirname $(realpath $(gcc -print-file-name=libgfortran.so)))
		C_FORTRAN_MIXING_LIB     = $(realpath $(gcc -print-file-name=libgfortran.so))
		F77_UNDERSCORE_FLAGS     = -funderscoring
		F77_NO_UNDERSCORE_FLAGS  = -fno-underscoring
		OPTS_FORTRAN_LAPACK      = -O \$(F77_UNDERSCORE_FLAGS) \$(PICFLAGS)
		
		SPHINXBUILD              = $(realpath $(find /usr/bin -name "sphinx-build*")				| sort -V | tail -1)
		
		UDUNITS2_INC_PATH        = $(dirname  $(find /usr/include -type f -iname "udunits2.h"		| sort -V | tail -1))
		PYTHON_INC_PATH          = $(dirname  $(find /usr/include -type f -iname "Python.h"			| sort -V | tail -1))
		LIB_PATH_PYTHON          = $(dirname  $(find /usr/lib* -name "lib${local_PYTHON_3_Y}.so"	| sort -V | tail -1))
		PYTHON_3_Y               = \$(shell python3 -c 'import sys; print ("python%d.%d" % (sys.version_info[0], sys.version_info[1]))')
		PY3_LIB_DIR              = \$(AIDA_HOME)/lib/\$(PYTHON_3_Y)
		
		# Sous linux, il faut créer des liens so -> so.1; s0.1 -> sl
		EXTRA_CMD_SL             = (cd  \$(AIDA_HOME)/lib; \\
		                           ln -sf ./lib\$(STD_LIBRARY_NAME).sl lib\$(STD_LIBRARY_NAME).so.1; \\
		                           ln -sf ./lib\$(STD_LIBRARY_NAME).so.1 lib\$(STD_LIBRARY_NAME).so )
		# La même règle que ci-dessus, écrite pour fonctionner sur le prérequis de la cible courante.
		EXTRA_CMD_SL_PREREQ      = (cd  \$(AIDA_HOME)/lib; \\
		                           ln -sf ./\$< \$(<:.sl=.so.1); \\
		                           ln -sf ./\$(<:.sl=.so.1) \$(<:.sl=.so) )
		
		
		#  QUEL INTERET DE PRECISER LE PATH /usr/bin ? ----
		DEPEND                   = makedepend
		MAKE                     = make
		INSTALL                  = install
		TAR                      = tar
		MKDIRHIER                = mkdir -p
		CEXTRACT                 = \$(AIDA_HOME)/bin/cextract
		
		LATEX                    = latex
		PDFLATEX                 = pdflatex
		DVIPS                    = dvips
		BIBTEX                   = bibtex
		HTLATEX                  = htlatex
		MAKEINDEX                = makeindex
		
		# A SUPPRIMER ?
		# Certains programmes ne sont pas portables (compilables seulement sur
		# certains systemes).
		# On définit donc ici des "EXTRA_LIST", dont le contenu dépend du système.
		# Chaque de ces liste sera ajoutée à la liste programmes portables dans
		# les makefiles correspondant (EXTRA_SUBDIRS_C_LECTURE sera utilisée
		# dans le makefile de src/C/lecture).
		   EXTRA_SUBDIRS_C_ECRITURE =  #vec2cdf
		    EXTRA_SUBDIRS_C_LECTURE =
		      EXTRA_SUBDIRS_ASC2VEC =
		
		
	EOF

	echo "--> Il faudra enregistrer le fichier '$file_mk' dans le repository."
}


#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------
if [[ -z "$AIDA_HOME" ]] ; then
	echo "*** AIDA_HOME n'est pas défini ! ***"
	exit -1
fi
AIDA_CONFIG="${AIDA_CONFIG:-${AIDA_HOME}/config}"

if [[ ! -d "${AIDA_CONFIG}" ]] ; then
	mkdir -p ${AIDA_CONFIG}
	chmod a+rx ${AIDA_CONFIG}
fi

cd ${AIDA_CONFIG}
if [[ $? -ne 0 ]] ; then
	echo "*** cd vers ${AIDA_CONFIG} : impossible ***"
	exit -1
fi

if [[ ! -d "make" ]] ; then
	mkdir make
	chmod a+rx make
fi


# nom du fichier à générer
DISTRIB="$(lsb_release -is)"
DISTRIB_RELEASE="$(lsb_release -rs)"
ARCH="$(arch)"
filename_mk="make/Linux_${DISTRIB}_${DISTRIB_RELEASE}_${ARCH}.auto.mk"

if [[ -f "$filename_mk" ]] ; then
	echo "fichier existant : $filename_mk"
	# vérifier si ecrit_squelette donne la même chose que la fois d'avant...
	tmp_mk="${filename_mk/make/\/tmp}"
	ecrit_squelette $tmp_mk
	diff -q $tmp_mk $filename_mk >/dev/null
	ret=$?
	if [[ $ret -ne 0 ]] ; then
		mv $tmp_mk $filename_mk
	fi
else
	ecrit_squelette $filename_mk
	which nautilus >/dev/null && mkdir -p $HOME/.local/share/nautilus/scripts
fi

# si le lien n'existe pas ou si le lien en mort,(re)créer le lien
if [[ ! -L "local_cfg.mk"  ||  ! -f "$(readlink ./local_cfg.mk)" ]] ; then
	echo "création du lien local_cfg.mk sur $filename_mk"
	ln -sf $filename_mk local_cfg.mk
else
	local_link="$(readlink ./local_cfg.mk)"

	echo "$local_link" | grep "$DISTRIB" >/dev/null
	meme_distrib=$?

	echo "$local_link" | grep "$DISTRIB_RELEASE" >/dev/null
	meme_distrib_release=$?

	echo "$local_link" | grep "$ARCH"    >/dev/null 
	meme_arch=$?

	echo "$local_link" | grep ".auto.mk" >/dev/null 
	gen_auto=$?

	if [[ $meme_distrib -ne 0 || $meme_distrib_release -ne 0 || \
		  $meme_arch -ne 0 || $gen_auto  -ne 0 ]] ; then
		echo "local_cfg_mk pointe vers un fichier trop différent"
		echo "=> creation d'un local_cfg.mk pointant vers $filename_mk"
		ln -sf $filename_mk local_cfg.mk
	else
		echo "local_cfg_mk pointe sur $local_link"
	fi
fi

echo "...fini"
exit 0
