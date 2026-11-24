/*************************************************
* OPERATOR 	Extr_tabflt2flt.c 	FUNCTION ANSI-C
*
* PURPOSE	Extrait N colonnes consécutives d'un vecteur-tableau.
*               et les range dans un nouveau vecteur-tableau.
*
* ARGUMENTS 	IN 	float[]	tabin 	       Vecteur-tableau d'entree
* 		IN 	int	Nb_Col_Tab_in  taille du vecteur d'entree
* 		IN 	int	Nb_Col_Tab_out taille du vecteur d'entree
*  		IN 	int	PremCol        première colonne selectionnée 
*                                                 (convention "C", début à zéro)
*
*		OUT	float[]	tabout		Vecteur-tableau produit
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	NONE
*
* COPYRIGHT	Meteo-France
*		Centre National de Recherches Meteorologiques
*		GMEI/MMA
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include <math.h>
#include "struct_oper.h"

long
Extr_tabflt2flt (unsigned long ndata,
	  const float *tabin,	/* tabin est en fait un tableau 2D */
	  const int Nb_Col_Tab_in,
	  const int Nb_Col_Tab_out,
	  const int premcol,
	  float *tabout)	/* tabout est en fait un tableau 2D */

{
  long i, jj, j_in, j_out;

  if (Nb_Col_Tab_out > Nb_Col_Tab_in)
    return -1;

  if (Nb_Col_Tab_out + premcol > Nb_Col_Tab_in)
    return -2;

  for (i = 0; i < ndata; i++)
    {
      j_in = i * Nb_Col_Tab_in + premcol;
      j_out = i * Nb_Col_Tab_out;
      for (jj = 0; jj < Nb_Col_Tab_out; jj++)
	tabout[j_out++] = tabin[j_in++];
    }
  return i;
}

/* fonction d'enrobage */

int
OP_Extr_tabflt2flt (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;

  CodRet = Extr_tabflt2flt (Nbval,
		     (float *) ArgList[0],
		     *((int *) ArgList[1]),
		     *((int *) ArgList[2]),
		     *((int *) ArgList[3]),
		     (float *) ArgList[4]);

  if (CodRet > 0)
    {
      sprintf (DiagExec, "OK, %ld instants traités", CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case 0:
      strcpy (DiagExec, "WARN : 0 instants traités !!!");
      return OP_OK;
    case -1:
      strcpy (DiagExec, "Vecteur de sortie plus grand que celui d'entree !!!!");
      return OP_FAIL;
    case -2:
      strcpy (DiagExec, "Colonne de fin APRES derniere colonne du vect. d'entree !!!!");
      return OP_FAIL;
    default:
      strcpy (DiagExec, "Unexpected error !!");
      return OP_FAIL;
    }
}

void
ID_Extr_tabflt2flt (oper * optr)
{
  strcpy (optr->Nom, "Extr_tabflt2flt");
  optr->Version = "1.0";
  optr->Date = "10/15/96";
  optr->fctptr = OP_Extr_tabflt2flt;
  optr->NbArg = 5;

  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* Le nombre de colonnes du vecteur d'entrée */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* Le nombre de colonnes du vecteur de sortie */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* La première colonne selectionnee dans le vecteur d'entree */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = COEFFICIENT;
  optr->Arg_Car[3].typ = ATYC_I32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].unite = "";

  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "$Arg3";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  /* TODO : propager bornes_unit et modifier bornes. */
}
