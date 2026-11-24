/*************************************************
* OPERATOR 	 Remplace_col_tab_flt.c 	FUNCTION ANSI-C
*
* PURPOSE	Crée une copie d'un vecteur tableau, en remplaçant les
*               valeurs de la  i-eme colonne  par un vecteur "scalaire"
* 
* DESCRIPTION
*
* ARGUMENTS 	IN 	float[]	tabin 	        Vecteur-tableau d'entree
* 		IN 	int	Nb_Col_Tab_in   Taille du vecteur d'entree
*  		IN 	int	col_rempla      Numéro de la "Colonne" à remplacer
*                                                 (convention "C", début à zéro)
* 		IN 	float	val_rempla      Valeurs de remplacement.
*
*		OUT	float[]	tabout		Vecteur-tableau produit
*		
* ENTRY		NONE
*
* SUBPROGRAMS 	NONE
*
* REFERENCE	NONE
*
* AUTHOR 	Bruno Piguet
*
* COPYRIGHT	CNRM-GAME,
*               URA Meteo-France & CNRS
*		Centre National de Recherches Meteorologiques
*		GMEI/TRAMM
*		42, av G. Coriolis 
*		31057	TOULOUSE cedex
*
*****************************************************************/

#define _POSIX_SOURCE 1
#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <string.h>
#include "struct_oper.h"

long
Remplace_col_tab_flt (unsigned long ndata,
                      const float *tabin,	/* tabin est en fait un tableau 2D */
		      int Nb_Col_Tab_in,
                      int col_rempla,
                      const float *val_rempla,
                      float *tabout)	/* tabout est en fait un tableau 2D */
{
  unsigned long i, k;
  int j;

  if (col_rempla < 0)
    return -1;

  if (col_rempla > Nb_Col_Tab_in)
    return -2;

  /* Première boucle de copie systématique. */
  for (i = 0; i < ndata; i++)
    {
      k = i * Nb_Col_Tab_in;
      for (j = 0; j < Nb_Col_Tab_in; j++)
	{
	  tabout[k] = tabin[k];
	  k++;
	}
    }

  /* Seconde boucle de remplacement */
  for (i = 0; i < ndata; i++)
    {
      k = i * Nb_Col_Tab_in + col_rempla;
      tabout[k] = val_rempla[i];
    }

  return i;
}

/* fonction d'enrobage */

int 
OP_Remplace_col_tab_flt (unsigned long Nbval, void *ArgList[], char *DiagExec)
{
  long CodRet;

  CodRet = Remplace_col_tab_flt (Nbval,
				 (float *) ArgList[0],
				 *((int *) ArgList[1]),
				 *((int *) ArgList[2]),
				 (float *) ArgList[3], (float *) ArgList[4]);

  if (CodRet > 0)
    {
      sprintf (DiagExec, "OK, %ld instants traités", CodRet);
      return OP_OK;
    }
  switch (CodRet)
    {
    case 0:
      strcpy (DiagExec, "WARN : 0 instants traités !");
      return OP_OK;
    case -1:
      strcpy (DiagExec,
	      "Valeur négative de l'indice de colonne à remplacer !");
      return OP_FAIL;
    case -2:
      strcpy (DiagExec,
	      "Indice de colonne à remplacer plus grand que taille du tableau d'entree !");
      return OP_FAIL;
    default:
      strcpy (DiagExec, "Unexpected error !!");
      return OP_FAIL;
    }
}

void
ID_Remplace_col_tab_flt (oper * optr)
{
  strcpy (optr->Nom, "Remplace_col_tab_flt");
  optr->Version = "$Revision$";
  optr->Date = "$Date$";
  optr->fctptr = OP_Remplace_col_tab_flt;
  optr->NbArg = 5;

  /* tabin */
  optr->Arg_Car[0].direction = DIR_IN;
  optr->Arg_Car[0].categorie = VECTOR;
  optr->Arg_Car[0].typ = ATYC_IF32;
  optr->Arg_Car[0].array_dim = "any";
  optr->Arg_Car[0].type_sample = "any";
  optr->Arg_Car[0].sample = "any";
  optr->Arg_Car[0].unite = "";

  /* Nb_Col_Tab_in  */
  optr->Arg_Car[1].direction = DIR_IN;
  optr->Arg_Car[1].categorie = COEFFICIENT;
  optr->Arg_Car[1].typ = ATYC_I32;
  optr->Arg_Car[1].array_dim = "1";
  optr->Arg_Car[1].unite = "";

  /* col_rempla  */
  optr->Arg_Car[2].direction = DIR_IN;
  optr->Arg_Car[2].categorie = COEFFICIENT;
  optr->Arg_Car[2].typ = ATYC_I32;
  optr->Arg_Car[2].array_dim = "1";
  optr->Arg_Car[2].unite = "";

  /* val_rempla  */
  optr->Arg_Car[3].direction = DIR_IN;
  optr->Arg_Car[3].categorie = VECTOR;
  optr->Arg_Car[3].typ = ATYC_IF32;
  optr->Arg_Car[3].array_dim = "1";
  optr->Arg_Car[3].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[3].unite = "$Arg1.unit";

  /* tabout */
  optr->Arg_Car[4].direction = DIR_OUT;
  optr->Arg_Car[4].categorie = VECTOR;
  optr->Arg_Car[4].typ = ATYC_IF32;
  optr->Arg_Car[4].array_dim = "$Arg1.array_dim";
  optr->Arg_Car[4].NbVal = "$Arg1.NbVal";
  optr->Arg_Car[4].ref_time = "$Arg1.ref_time";
  optr->Arg_Car[4].type_sample = "$Arg1.type_sample";
  optr->Arg_Car[4].sample = "$Arg1.sample";
  optr->Arg_Car[4].unite = "$Arg1.unit";
  optr->Arg_Car[4].famille = "$Arg1.famille";
  optr->Arg_Car[4].misval = "$Arg1.misval";
  optr->Arg_Car[4].name = "$Arg1.name modifie par $Arg4.name";
  /* TODO : propager bornes_unit  */
}
