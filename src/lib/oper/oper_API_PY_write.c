/*
 * Pour ADC :
 * Écriture d'un fichier .py contenant le dictionnaire de description de
 * l'interface d'appel (API) des opérateurs, à partir des
 * fonctions d'auto-description (les ID_xxx).
 */
#define _POSIX_SOURCE 1

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/stat.h>
#ifndef PATH_MAX
#define PATH_MAX 1023
#endif

#include "gene.h"
#include "rapt.h"
#include "oper.h"

#include "load_oper.h"

int OPERATEUR_BUGGE = 0 ;

char * CatCode (const CATEGORIE categorie)
{
	switch (categorie) {
		case VECTOR		: return "VECTOR";
		case COEFFICIENT: return "COEFFICIENT";
		default			: fprintf(stderr, "+++ 'categorie' : ni VECTOR ni COEFFICIENT\n");
						  OPERATEUR_BUGGE++;
						  return "CAT_UNKNOWN";
	}
}

char * DirCode (const sens direction)
{
	switch (direction) {
		case DIR_IN		: return "DIR_IN";
		case DIR_OUT	: return "DIR_OUT";
		default			: fprintf(stderr, "+++ 'direction' : ni DIR_IN ni DIR_OUT\n");
						  OPERATEUR_BUGGE++;
						  return "DIR_NONE";
	}
}

char * CleanStr (const char *str_in)
/* Retourne la chaine d'entrée suffisamment nettoyée pour être acceptable par
 * python.
 */
{
static char	cleaned[1024]	; // ça doit être bien assez grand...
int			i				;

	if (str_in         == NULL ||
		strlen(str_in) == 0    ) {
		return "";
	}

	// il y a souvent un premier espace qui ne sert à rien...
	if (*str_in == ' ') {
		str_in ++ ;
	}
	i = 0 ;
	for ( ; *str_in != '\0'; str_in++) {
		if (*str_in == '\'') {
			cleaned[i] = '\\' ;
			i ++ ;
		}
		cleaned[i] = *str_in;
		i ++ ;
	}
	cleaned[i] = '\0' ;
	
	// supprimer les ' ' à la fin
	for (i=strlen(cleaned)-1; i>=0 && cleaned[i] == ' '; i--) {
		cleaned[i] = '\0' ;
	}

	// DBG : printf(">%s< \n", cleaned) ;
	return cleaned ;
}

void InitDesc (FILE *DescFile)
/* Ecrit l'entête du fichier de description.
 */
{
	fprintf (DescFile, "# %s\n", "GÉNÉRÉ AUTOMATIQUEMENT: ne pas éditer") ;
	fprintf (DescFile, "# %s\n", "re-génération avec : oper_API_PY_write") ;

	/***
	fprintf (DescFile, "\n") ;
	fprintf (DescFile, "from enum import Enum\n\n") ;
	fprintf (DescFile, "class Categorie(Enum):\n") ;
	fprintf (DescFile, "\tCAT_UNKNOWN = %d \n", CAT_UNKNOWN) ;
	fprintf (DescFile, "\tVECTOR      = %d \n", VECTOR) ;
	fprintf (DescFile, "\tCOEFFICIENT = %d \n", COEFFICIENT) ;
	fprintf (DescFile, "\n") ;
	fprintf (DescFile, "class Direction(Enum):\n") ;
	fprintf (DescFile, "\tDIR_NONE    = %d \n", DIR_NONE) ;
	fprintf (DescFile, "\tDIR_IN      = %d \n", DIR_IN) ;
	fprintf (DescFile, "\tDIR_OUT     = %d \n", DIR_OUT) ;
	***/

	fprintf (DescFile, "\n") ;
	fprintf (DescFile, "oper_API_PY_desc = {\n") ;
}

int EcritDescOperAPI (FILE *DescFile, const oper *Oper)
/* Ecrit la description de l'opérateur dans le fichier de description.
 */
{
int					j		;
const Arg_profil	*Arg_Car;

	fprintf (DescFile, "\t'%s': { \n", Oper->Nom) ;
	/*** contiennent souvent des cochonneries SVN plutôt que des valeurs
	fprintf (DescFile, "\t\t'Version'    : '%s',\n", Oper->Version    );
	fprintf (DescFile, "\t\t'Date'       : '%s',\n", Oper->Date       );
	***/
	fprintf (DescFile, "\t\t'type'       : %d,\n", Oper->type       );
	fprintf (DescFile, "\t\t'repl_oper'  : '%s',\n", CleanStr(Oper->repl_oper  ));
	fprintf (DescFile, "\t\t'repl_cause' : '%s',\n", CleanStr(Oper->repl_cause ));
	/*** il faudra récupérer le pointer du module bind_oper ***
	fprintf (DescFile, "\t\t'fctptr'     : 0x%lx,\n", Oper->fctptr               );
	printf ("================ %s : fctptr = 0x%lx\n", Oper->Nom, Oper->fctptr);
	if (strcmp(Oper->Nom, "Poly_1_flt") == 0) {
		getchar() ;
	}
	***/

	fprintf (DescFile, "\t\t'misval_auto': %d,\n", Oper->misval_auto);
	fprintf (DescFile, "\t\t'NbArg'      : %d,\n", Oper->NbArg      );
	fprintf (DescFile, "\t\t'Arg_Cars'   : [\n");
	
	for (j = 0; j < Oper->NbArg; j++) {
		Arg_Car = &(Oper->Arg_Car[j]);
		fprintf (DescFile, "\t\t\t{ # %2d\n", j);
		fprintf (DescFile, "\t\t\t 'direction'  : '%s',\n",   DirCode   (Arg_Car->direction ));
		fprintf (DescFile, "\t\t\t 'categorie'  : '%s',\n",   CatCode   (Arg_Car->categorie ));
		fprintf (DescFile, "\t\t\t 'typ'        : '%s',\n",   AidaTypNom(Arg_Car->typ       )); /*** TODO ***/
		fprintf (DescFile, "\t\t\t 'array_shape': '%s',\n",     CleanStr(Arg_Car->array_shape));	/*** permet de positionner dim_array à array_shape dans certains cas.... voir Jacques ? ***/
		fprintf (DescFile, "\t\t\t 'array_dim'  : '%s',\n",     CleanStr(Arg_Car->array_dim  ));
		fprintf (DescFile, "\t\t\t 'bornes'     : '%s',\n",     CleanStr(Arg_Car->bornes     ));
		fprintf (DescFile, "\t\t\t 'unit_bornes': '%s',\n",     CleanStr(Arg_Car->unit_bornes));
		fprintf (DescFile, "\t\t\t 'unite'      : '%s',\n",     CleanStr(Arg_Car->unite      ));

		if (Arg_Car->categorie == VECTOR) {
			fprintf (DescFile, "\t\t\t 'name'       : '%s',\n", CleanStr(Arg_Car->name       ));
			fprintf (DescFile, "\t\t\t 'en_name'    : '%s',\n", CleanStr(Arg_Car->en_name    ));
			fprintf (DescFile, "\t\t\t 'type_sample': '%s',\n", CleanStr(Arg_Car->type_sample));
			fprintf (DescFile, "\t\t\t 'sample'     : '%s',\n", CleanStr(Arg_Car->sample     ));
			fprintf (DescFile, "\t\t\t 'ref_time'   : '%s',\n", CleanStr(Arg_Car->ref_time   ));
			fprintf (DescFile, "\t\t\t 'time_bnds'  : '%s',\n", CleanStr(Arg_Car->time_bnds  ));
			fprintf (DescFile, "\t\t\t 'famille'    : '%s',\n", CleanStr(Arg_Car->famille    ));
			fprintf (DescFile, "\t\t\t 'misval'     : '%s',\n", CleanStr(Arg_Car->misval     ));
			fprintf (DescFile, "\t\t\t 'NbVal'      : '%s',\n", CleanStr(Arg_Car->NbVal      ));
		}
		fprintf (DescFile, "\t\t\t},\n");

	}
	fprintf (DescFile, "\t\t]\n");
	fprintf (DescFile, "\t},\n");

	return 1 ;
}

void FinitDesc (FILE * DescFile)
/* Ecrit la fin du fichier de description.
 */
{
	fprintf (DescFile, "}\n") ;
}

int main (int argc, char *argv[])
{
oper		*Liste_oper								;
int			i, NbOper, NbEcrit						;
FILE		*DescFile								;
const char	*OperLibPath	= "./liboper.sl"		;
const char	*DescFileName	= "oper_API_PY_desc.py"	;

	NbOper = Init_Liste_Oper_dyn (OperLibPath, &Liste_oper);
	if (NbOper < 0) {
		fprintf (stderr,
				 "%s: Impossible de charger la bibliotheque d'operateurs %s \n",
				 argv[0], OperLibPath);
		fprintf (stderr, "---%s---\n", OPLD_erreur (NbOper));
		exit (4);
	}
	else {
		fprintf (stdout, "--- %s : %d opérateurs chargés depuis %s\n",
				 argv[0], NbOper, OperLibPath);
	}

	/* ouverture du fichier de description */
	DescFile = fopen (DescFileName, "w");
	if (DescFile == NULL) {
		fprintf(stderr, "+++ '%s' : problème d'ouveture \n", DescFileName) ;
		return EXIT_FAILURE;
	}

	/* traitement */
	InitDesc (DescFile);
	NbEcrit = 0;
	for (i = 0; i < NbOper; i++) {
		fprintf (stdout, "--- opérateur %3d : %s \n", i+1, Liste_oper[i].Nom) ;
		NbEcrit += EcritDescOperAPI (DescFile, &(Liste_oper[i]));
	}
	FinitDesc (DescFile);

	/* fin */
	fclose (DescFile);

	fprintf (stdout, "--- %s : %d opérateurs décrits dans %s\n",
			 argv[0], NbEcrit, DescFileName);
	if (OPERATEUR_BUGGE > 0) {
		fprintf (stdout, "\n-+- %s : %d opérateur(s) buggé(s) dans %s\n\n",
						argv[0], OPERATEUR_BUGGE, DescFileName);
	}
	Free_Liste_Oper (&Liste_oper);

	return EXIT_SUCCESS;
}
