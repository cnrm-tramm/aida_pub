#!/usr/bin/env bash
# Copyright 2011 Brent Longborough
# Please read gitinfo.pdf for licencing and other details
# -----------------------------------------------------
#
# Script de génération du gitHeadLocal.gin dans les direcrtory
# de la doc pour que Latex puisse récupérer la date de version de la doc
#
# usage :
#   make_gitinfo.sh <dirdoc> 
#    
# W Maurel le 20/05/2021

dirdoc=$1

echo "--- génération de gitHeadLocal.gin dans ${AIDA_HOME}/src/doc/${dirdoc}"

# la documentation n'existe pas encore sous git
in_git=$(git ls-tree -d --name-only master $(realpath ../$dirdoc))
if [[ -z "$in_git" ]] ; then
	echo "-+- pas encore sous git : $dirdoc"
	today=$(date +"%Y-%m-%d")
	today_hour=$(date +"%Y-%m-%d %H:%M:%S %z")
	cat >$AIDA_HOME/src/doc/${dirdoc}/gitHeadLocal.gin <<-EOF
		\usepackage[%
			authsdate={$today},
			authidate={$today_hour},
			commsdate={$today},
			commidate={$today_hour},
			]{gitsetinfo}
	EOF
	exit 0
fi

# récupération des information git
git log -1 --date=short \
        --pretty=format:"\usepackage[%
	shash={%h},
	lhash={%H},
    authemail={%ae},
	authsdate={%ad},
	authidate={%ai},
	authudate={%at},
	commemail={%ae},
	commsdate={%ad},
	commidate={%ai},
	commudate={%at},
	refnames={%d}
	]{gitsetinfo}" HEAD -- ${AIDA_HOME}/src/doc/${dirdoc} > ${AIDA_HOME}/src/doc/${dirdoc}/gitHeadLocal.gin

