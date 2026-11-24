#!/usr/bin/env bash

#==============================================================================
# 
# Construction d'un fichier PDF dans ./resources/ de la documentation d'un
# opérateur à partir de ses 2 fichiers TEX 'main' et 'arguments'.
# (dans AITO, la formule n'est pas indispensable.)
# 
#==============================================================================

ME=${0##*/}

function usage
{
	echo " "
	echo " usage :"
	echo "  $ME -h"
	echo "  $ME nom_d_opérateurs"
	echo " "
	echo " exemple :"
	echo "  $ME Filtre_RC_sdph Correc_pics_mnq"
	echo " "
	exit 1
}

#-----------------------------------------------------------------------------
# main
#-----------------------------------------------------------------------------
# arguments
if [[ $# -eq 0 ]] ; then
	usage
fi
if [[ $# -eq 1 && "$1" =~ -h ]] ; then
	usage
fi

# boucle de traitement
for oper in $* ; do
	oper="$oper"
	out_file="./resources/$oper.html"
	echo "oper=$oper, out_file=$out_file"

	input_main="$AIDA_HOME/src/doc/oper/$oper.tex"
	input_args="$AIDA_HOME/src/doc/oper/arguments/$oper.args.tex"
	
	if [[ ! -f $input_main ]] ; then
		echo "  --> le fichier '$input_main' n'existe pas"
		#usage
		exit 1
	fi
	
	if [[ ! -f $input_args ]] ; then
		echo "  --> le fichier '$input_args' n'existe pas"
		#usage
		exit 1
	fi
	
	# construction d'un seul fichier TEX à partir des 2 fichiers de l'opérateur
	# ----------------------------------
	# notes : pandoc n'aime pas le latin-1 => convertir en utf8
	#         `read -r` : préverse les \ du fichier d'entrée
	
	# - le fichier des arguments
	#   le titre des tables (entrées/sorties), tel qu'il est défini dans les doc,
	#   n'est pas bien géré par pandoc => passer par une bidouille
	tmp_args=/tmp/$USER.$oper.args.tex
	rm -f $tmp_args
	
	iconv -f ISO-8859-1 -t utf-8 $input_args | \
		while read -r line ; do
			if [[ "$line" =~ \multicolumn* ]] ; then
				echo "\multicolumn{3}{l}" >>$tmp_args
	
				if [[ "$line" =~ Entr* ]] ; then 
					##echo "{\titretab {Entrée}}\\\\" >>$tmp_args
					echo "\\bf{Entrée}\\\\" >>$tmp_args
					continue
				elif [[ "$line" =~ Sort* ]] ; then
					###echo "{\titretab {Sorties}}\\\\" >>$tmp_args
					echo "\\bf{Sorties}}\\\\" >>$tmp_args
					continue
				fi
			else
				echo "$line" >>$tmp_args
			fi
		done
	
	# - le fichier main
	tmp_main=/tmp/$USER.$oper.tex
	rm -f $tmp_main
	echo "\newenvironment{tabarg}{\begin{tabular}{p{3cm}p{5cm}p{7cm}}}{\end{tabular}}" >>$tmp_main
	echo "\newcommand{\itemstyle}[1]{\bigskip $\bullet$ {\bf #1}}" >>$tmp_main
	echo "\newcommand\operfmt{\textsf}" >>$tmp_main
	
	iconv -f ISO-8859-1 -t utf-8 $input_main | \
		while read -r line ; do
			if [[ "$line" =~ input\{arguments* ]] ; then
				cat $tmp_args >>$tmp_main
			elif [[ "$line" =~ input\{formules* ]] ; then
				continue
			elif [[ "$line" =~ \section* ]] ; then
				# il arrive que la ligne section contiennent un \n => trouver la
				# '}' de fermeture
				search_end=1
				if [[ "$line" =~ } ]] ; then
					search_end=0
				fi
				continue
			else
				if [[ $search_end == 1 ]] ; then
					if [[ "$line" =~ } ]] ; then
						search_end=0
					fi
					continue
				fi
				echo "$line" >>$tmp_main
			fi
		done
	
	# lancer `pandoc` sur le fichier obtenu
	### en PDF, les descriptions des arguments sont toncqués
	### pandoc --from=latex --to=pdf $tmp_main
	
	
	# en HTML
	pandoc --shift-heading-level-by=3 --from=latex --to=html $tmp_main |
		sed '/<table>/ c\
	<table style=width:100%>\
	  <colgroup>\
	    <col style=width:20%;>\
	    <col style=width:30%;>\
	    <col style=width:50%;>\
	  </colgroup>' >>$out_file
	
	# fin
	rm -f $tmp_args
	rm -f $tmp_main
done
exit 0
