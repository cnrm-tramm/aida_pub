#!/usr/bin/env bash

#==============================================================================
#
# Tests des pre-requis pour AIDA et pour la génération du fichier de
# configuration pour make (local_cfg.mk)
#
# Note :
#	Si `bash` n'est pas installé, le lancement de ce script affichera quelque
#	chose comme :
#		... /bin/bash : mauvais interpréteur ...
#	La présence de bash n'est donc pas testée.
#
#==============================================================================

# initialisations
# ===============
# éviter de semer des fichiers un peu partout...
LOG_DIR="$HOME/log"
mkdir -p $LOG_DIR

LOG_FILE=$LOG_DIR/PREREQUIS_AIDA.log
>$LOG_FILE

# listes de ce qui doit être présent
### ATENTION à la ")" fermante !!!
tools_config_needed=(	"which"
)

tools_config=(			"find"
						"arch"
						"realpath"
						"uname"
						"lsb_release"
)

tools_AIDA=(			"readlink"
						"xterm"
						"git"
						"gcc"
						"gfortran"
						"makedepend"
						"make"
						"install"
						"tar"
						"rsync"
						"python3"
						"udunits2"
						"nc-config"
						"ncview"
						"dot"
						"doxygen"
						"latex"
						"pdflatex"
						"dvips"
						"bibtex"
						"htlatex"
						"makeindex"
)

facultatifs=(			"zenity"
)

# fiona est utilisé par cartopy mais n'est pas explicitement importé dans les
# code AIDA (=> il n'apparait pas dans check_AIDA_PY_dependencies.sh)
facultatifs_python=(	"fiona"
	                    "sklearn"
	                    "matplotlib*gridspec"
)


includes_AIDA=(			"asm/errno.h"
						"udunits2.h"
						"netcdf.h"
						"zlib.h"
						"gsl/gsl_sort.h"
)

includes_python=(		"Python.h"
)

# chercher des trucs qui ne sont pas toujours sous les mêmes répertoires
declare -A special_AIDA
special_AIDA['webkit2-4.0']='find /usr/{lib,lib64} -type f -name "WebKit2-4.0.typelib"'
special_AIDA['lmodern']='find /usr/share -type f -name "lmodern.sty"'
special_AIDA['tocbibind']='find /usr/share -type f -name "tocbibind.sty"'
special_AIDA['gitinfo2']='find /usr/share -type f -name "gitinfo2.sty"'
special_AIDA['sphinx-build']='realpath $(find /usr/bin -name "sphinx-build*") | sort -V | tail -1'
special_AIDA['stemmer']='find /usr/{lib,lib64} -type f -name "*stemmer*.so*"'
special_AIDA['pyqtgraph']='find /usr/li* $HOME -type d -name "pyqtgraph"'


# pour la lib python, ce n'est pas si simple => voir les prérequis python
libs_AIDA=(				"libc.so"
						"libgfortran.so"
						"libnetcdf.so"
						"libz.so"
						"libgsl.so"
						"libgslcblas.so"
						"libsqlite3.so"
)

declare -A versions_req
declare -A versions_min
declare -A versions_cur
versions_req['python3']=3.10
versions_min['python3']=3.10
versions_cur['python3']=$(python3 -c 'import sys ; print("%d.%d" % (sys.version_info[0], sys.version_info[1]))')
lib_python3="libpython${versions_cur['python3']}.so"

# cfunits est devenu obligatoire
by_pip=( "cfunits"
)

# defaults
default_arch="x86_64"

#------------------------------------------------------------------------------
function log
{
	printf " $*\n" >>$LOG_FILE
}

#------------------------------------------------------------------------------
function well
# si $1 = -n : pas de retour à la ligne
{
	newline="\n"
	if [[ "$1" == "-n" ]] ; then
		newline=""
		shift 1
	fi
	printf " $*$newline"
	log "$*"
}

#------------------------------------------------------------------------------
function ok_msg
{
	if (( $1 == 0 )) ; then
		msg="     ...ok"
		printf "\033[1m$msg\033[0;39m\n"
		log "$msg"
	fi
}

#------------------------------------------------------------------------------
function warn
{
	#printf "\033[1m     $*\033[0;39m\n"
	printf "\033[1;${red}m     ${*}\033[0;39m\n" "$*"
	log "$*"
}

#------------------------------------------------------------------------------
function error
{
red=31
	printf "\n\033[1;${red}m${*}\033[0;39m\n" "$*"
	log "$*"

	exit_if_nok 1
	exit 1
}

#------------------------------------------------------------------------------
function exit_if_nok
# si le paramètre reçu est > 0, écrit un message et sort
# $1 = nombre de nok
{
nok=$1
red=31
msg_1="Veuillez corriger le problème puis relancer ce script."
msg_N="Veuillez corriger les $nok problèmes puis relancer ce script."

	if [[ $nok -gt 0 ]] ; then
		msg=$msg_N
		[[ $nok -eq 1 ]] && msg=$msg_1

		printf "\n\033[1;${red}m--> $msg\033[0;39m\n(voir $LOG_FILE)\n"
		log "\n--> $msg\n(voir $LOG_FILE)\n"
		exit 1
	fi
}

#------------------------------------------------------------------------------
function version_ok
# retourne 0 si la version requise ($1) reçue est >= à la version currente ($2).
# $1 = version 1 ("requise")
# $2 = version 2 ("current")
{
requise=$1
current=$2

	# trier les 2 versions et récupérer celle qui sort en 1ier
	check=$(printf '%s\n' "$requise" "$current" | sort -V | head -n1)

	# si la version qui sort en premier est la verion requise alors la
	# current est supérieure ou égale à la requise
	if [ "$check"  == "$requise" ] ; then
		return 0 # ok
	else
		return 1 # NOK
	fi
}

#-------------------------------------------------------------------------------
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
clear

well "$0 $* : $(date)"

well "\n- pre-requis du configurateur (impératif)"
nok=0
for tool in ${tools_config_needed[*]} ; do
	#well "    $tool"
	ret=$(which $tool 2>/dev/null)
	if [[ "$?" != "0" ]] ; then
		warn "absent : $tool"
		nok=$((nok + 1))
	fi
done
exit_if_nok $nok && ok_msg $nok


well "\n- pre-requis du configurateur"
part_nok=0
for tool in ${tools_config[*]} ; do
	#well "    $tool"
	ret=$(which $tool 2>/dev/null)
	if [[ "$?" != "0" ]] ; then
		warn "absent : $tool"
		part_nok=$((part_nok + 1))
	fi
done
ok_msg $part_nok
nok=$((nok + part_nok))


# test préliminaire avant d'aller plus loin :
# - machine 64bits ?
well "\n- architecture : $default_arch ?"
if [[ "$(arch)" != "$default_arch" ]] ; then
	error "AIDA ne peut être installé que sur des architectures $default_arch"
fi
ok_msg 0

well "\n- pre-requis de AIDA (tools)"
part_nok=0
for tool in ${tools_AIDA[*]} ; do
	#well "    $tool"
	ret=$(which $tool 2>/dev/null)
	if [[ "$?" != "0" ]] ; then
		warn "absent : $tool"
		part_nok=$((part_nok + 1))
	fi
done
ok_msg $part_nok
nok=$((nok + part_nok))


well "\n- pre-requis de AIDA (include)"
part_nok=0
for include in ${includes_AIDA[*]} ; do
	#well "    $include"
	ret=$(find /usr/include -follow -path "/usr/include/*$include")
	if [[ -z "$ret" ]] ; then
		warn "absent : /usr/include/$include"
		part_nok=$((part_nok + 1))
	fi
done
ok_msg $part_nok
nok=$((nok + part_nok))


well "\n- pre-requis de AIDA (speciaux)"
part_nok=0
for key in ${!special_AIDA[*]} ; do
	#well "    $key"
	ret=$(eval "${special_AIDA[$key]}" 2>/dev/null)
	if [[ -z "$ret" ]] ; then
		warn "infructueux : ${special_AIDA[$key]}"
		part_nok=$((part_nok + 1))
	fi
done
ok_msg $part_nok
nok=$((nok + part_nok))


well "\n- pre-requis de AIDA (gcc libs)"
part_nok=0
for lib in ${libs_AIDA[*]} ; do
	#well "    $lib"
	gcc_libname=$(gcc -print-file-name=$lib 2>/dev/null)
	if [[ $? == 127 || $gcc_libname == "$lib" ]] ; then
		warn "absent : $lib"
		part_nok=$((part_nok + 1))
	#else
	#	well "    $(realpath $gcc_libname)"
	fi
done
ok_msg $part_nok
nok=$((nok + part_nok))


well "\n- pre-requis de AIDA (versions)"
part_nok=0
for tool in ${!versions_min[*]} ; do
	req="${versions_req[$tool]}"
	min="${versions_min[$tool]}"
	cur="${versions_cur[$tool]}"
	well "    $tool (version requise  : $req)"

	version_ok "$req" "$cur" ; ret=$?
	if [[ "$ret" != "0" ]] ; then
		# la version courante est < à la version requise
		# => tester si elle est _compatible_ avec la version mininale
		version_ok "$min" "$cur" ; ret=$?
		if [[ "$ret" != "0" ]] ; then
			warn "$tool : version courante = $cur, version minimale = $min"
			part_nok=$((part_nok + 1))
		else
			warn "$tool (version courante : $cur) : acceptable"
		fi
	#else
	#	well "    $tool (version courante : $cur) : ok"
	fi
done
ok_msg $part_nok
nok=$((nok + part_nok))


well "\n- pre-requis de AIDA (lib python3)"
well "    $lib_python3"
part_nok=0
ret=$(find /usr/lib* -name "$lib_python3" 2>/dev/null)
if [[ -z "$ret" ]] ; then
	warn "absent : $lib_python3"
	part_nok=$((part_nok + 1))
fi
ok_msg $part_nok
nok=$((nok + part_nok))


well "\n- pre-requis de AIDA (include python)"
part_nok=0
for include in ${includes_python[*]} ; do
	#well "    $include"
	ret=$(find /usr/include -name "$include")
	if [[ -z "$ret" ]] ; then
		warn "absent : /usr/include : $include"
		part_nok=$((part_nok + 1))
	fi
done
ok_msg $part_nok
nok=$((nok + part_nok))


part_nok=0
well "\n- pre-requis python facultatifs"
for package in ${facultatifs_python[*]} ; do
	#well "    $package"
	ret=$(find /usr/lib*/python3* $HOME -type d -path "*$package" 2>/dev/null)
	if [[ -z "$ret" ]] ; then
		warn "absent (facultatif): $package"
		part_nok=$((part_nok + 1))
	fi
done
ok_msg $part_nok

part_nok=0
well "\n- pre-requis facultatifs"
for tool in ${facultatifs[*]} ; do
	#well "    $tool"
	ret=$(which $tool 2>/dev/null)
	if [[ "$?" != "0" ]] ; then
		warn "absent (facultatif): $tool"
		part_nok=$((part_nok + 1))
	fi
done
ok_msg $part_nok

part_nok=0
well "\n- pre-requis installés par pip"
for tool in ${by_pip[*]} ; do
	python3 -c 'import '$tool';'  2>/dev/null
	if [[ "$?" != "0" ]] ; then
		warn "absent : $tool (cf. documentation d'installation)"
		part_nok=$((part_nok + 1))
	else
		well "    $tool"
	fi
done
exit_if_nok $part_nok && ok_msg $nok

#### prérequis dépendants du profil
###chooser "Pour quel profil installez-vous AIDA" ${profils[*]}
###choix=$(($? - 1))
###profil="${profils[$choix]}"
###well "\n\nprofil : $profil"
###
###tools=( ${profil_tools[$profil]} )
###part_nok=0
###if [[ ! -z "${tools[*]}" ]] ; then
###	for tool in ${tools[*]} ; do
###		#well "    $tool"
###		ret=$(which $tool 2>/dev/null)
###		if [[ "$?" != "0" ]] ; then
###			warn "absent : $tool"
###			part_nok=$((part_nok + 1))
###		fi
###	done
###fi
####[[ "$profil" == "autre" ]] && profil="EXEMPLES"
###ok_msg $part_nok
###nok=$((nok + part_nok))
###
#### enregistrer le profil choisi dans un fichier temporaire
###echo "$profil" >$LOG_DIR/INSTALL_AIDA_PROFIL


# fin
exit_if_nok $nok
well "\n$0 $* : terminé avec succès !"
well "(voir $LOG_FILE)"
echo ""
